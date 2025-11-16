from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
import structlog

from app.models.source_models import SourceFile
from app.models.database import get_db
from app.core.etl.pipeline import ETLPipeline

import io
from pypdf import PdfReader

router = APIRouter()
logger = structlog.get_logger()


# ---------------------------------------------
# HEALTH ENDPOINT (GET)
# ---------------------------------------------
@router.get("/health")
async def upload_health():
    return {"status": "ok", "message": "Upload endpoint alive"}


# ---------------------------------------------
# FILE UPLOAD ENDPOINT (POST)
# ---------------------------------------------
@router.post("/", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    source_id: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    
    allowed_ext = [".txt", ".md", ".pdf"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_ext):
        raise HTTPException(status_code=400, detail="Only .txt, .md, .pdf supported")

    # -----------------------
    # 1. READ FILE CONTENT
    # -----------------------
    content = await file.read()

    # --------------------
    # PDF Upload Handling
    # --------------------
    if file.filename.lower().endswith(".pdf"):
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            extracted = []
            for page in pdf_reader.pages:
                extracted.append(page.extract_text() or "")
            text = "\n".join(extracted)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract PDF text: {e}"
            )

    # --------------------
    # Markdown or Text Handling
    # --------------------
    else:
        try:
            text = content.decode("utf-8", errors="ignore")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode file as UTF-8 text"
            )

    # -----------------------
    # 2. RUN ETL
    # -----------------------
    etl = ETLPipeline()

    try:
        await etl.process_text(
            source_id=source_id,
            text=text,
            filename=file.filename
        )
    except Exception as e:
        logger.error("ETL failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"ETL failed: {e}")

    # -----------------------
    # 3. INSERT METADATA INTO POSTGRES
    # -----------------------
    stmt = (
        insert(SourceFile)
        .values(
            source_id=source_id,
            filename=file.filename,
            file_type=file.content_type,
            storage_path=f"uploads/{file.filename}",
        )
        .returning(SourceFile.id, SourceFile.uploaded_at)
    )

    try:
        result = await db.execute(stmt)
        await db.commit()
    except Exception as e:
        logger.error("DB insert failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to store metadata")

    row = result.first()
    if not row:
        raise HTTPException(status_code=500, detail="Insert returned no data")

    file_id, uploaded_at = row

    # -----------------------
    # 4. RETURN RESPONSE
    # -----------------------
    return {
        "id": file_id,
        "source_id": source_id,
        "filename": file.filename,
        "file_type": file.content_type,
        "storage_path": f"uploads/{file.filename}",
        "uploaded_at": uploaded_at
    }
