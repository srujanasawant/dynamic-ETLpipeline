# app/api/routes/records.py

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional, Dict, Any, List
import csv
from io import StringIO
import structlog

from app.storage.mongodb import MongoDBStorage
from app.models.query_models import QueryResponse

router = APIRouter()
logger = structlog.get_logger()


# ---------------------------------------------------------
# GET /records — return parsed records from MongoDB
# ---------------------------------------------------------
@router.get("/", response_model=QueryResponse)
async def get_records(
    source_id: str = Query(..., description="Source identifier"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """
    Return parsed cleaned records from MongoDB for a given source_id.
    This returns the raw extracted & cleaned records stored by ETL.
    """
    try:
        mongo = MongoDBStorage()
        collection = f"{source_id}_records"

        cursor = mongo.db[collection].find({}).skip(offset).limit(limit)
        docs = await cursor.to_list(length=limit)

        if not docs:
            raise HTTPException(status_code=404, detail=f"No records found for source_id: {source_id}")

        # Extract only the record dict
        records = [d.get("record", {}) for d in docs]

        return QueryResponse(
            count=len(records),
            records=records
        )

    except Exception as e:
        logger.error("Failed to fetch records", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# GET /records/export — export cleaned records
# ---------------------------------------------------------
@router.get("/export")
async def export_records(
    source_id: str = Query(..., description="Source identifier"),
    format: str = Query("json", regex="^(json|csv)$"),
    limit: int = Query(1000, ge=1, le=5000)
):
    """
    Export raw cleaned records in JSON or CSV format.
    """
    try:
        mongo = MongoDBStorage()
        collection = f"{source_id}_records"

        docs = await mongo.db[collection].find({}).limit(limit).to_list(length=limit)
        records = [d.get("record", {}) for d in docs]

        if not records:
            raise HTTPException(status_code=404, detail="No data to export")

        # JSON export
        if format == "json":
            return JSONResponse(content={"data": records})

        # CSV export
        if format == "csv":
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
            output.seek(0)

            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={source_id}.csv"
                }
            )

    except Exception as e:
        logger.error("Export failed", exc_info=e)
        raise HTTPException(status_code=500, detail=str(e))
