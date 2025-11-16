# app/api/routes/schema.py
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import structlog

from app.models.database import get_db
from app.models.schema_models import (
    SchemaVersionDB,
    SchemaResponse,
    SchemaHistoryResponse,
    SchemaDiff
)

router = APIRouter()
logger = structlog.get_logger()


# ---------------------------------------------------------
# GET latest schema or specific version
# ---------------------------------------------------------
@router.get("/", response_model=SchemaResponse)
async def get_schema(
    source_id: str = Query(...),
    version: int | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Return schema for a given source_id.
    If version is omitted → return latest schema.
    """
    try:
        query = select(SchemaVersionDB).where(
            SchemaVersionDB.source_id == source_id
        )

        if version:
            query = query.where(SchemaVersionDB.version == version)
        else:
            query = query.order_by(desc(SchemaVersionDB.version)).limit(1)

        result = await db.execute(query)
        row = result.scalars().first()

        if row is None:
            raise HTTPException(404, f"No schema found for source_id={source_id}")

        return SchemaResponse(
            source_id=row.source_id,
            current_version=row.version,
            schema=row.schema
        )

    except Exception as e:
        logger.error("Schema retrieval failed", exc_info=e)
        raise HTTPException(500, str(e))


# ---------------------------------------------------------
# GET full schema history
# ---------------------------------------------------------
@router.get("/history", response_model=SchemaHistoryResponse)
async def get_schema_history(
    source_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns ALL versions of schema for the source.
    """
    try:
        query = (
            select(SchemaVersionDB)
            .where(SchemaVersionDB.source_id == source_id)
            .order_by(SchemaVersionDB.version)
        )

        result = await db.execute(query)
        rows = result.scalars().all()

        if not rows:
            raise HTTPException(404, f"No schema history for source_id={source_id}")

        history_items = []
        for row in rows:
            history_items.append({
                "id": row.id,
                "version": row.version,
                "schema": row.schema,
                "created_at": row.created_at
            })

        return SchemaHistoryResponse(
            source_id=source_id,
            history=history_items
        )

    except Exception as e:
        logger.error("Schema history failed", exc_info=e)
        raise HTTPException(500, str(e))


# ---------------------------------------------------------
# GET last version diff vs previous version
# ---------------------------------------------------------
@router.get("/diff", response_model=SchemaDiff)
async def get_schema_diff(
    source_id: str = Query(...),
    version: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve schema diff between the given version and the previous version.
    """
    try:
        # Get current version
        query_current = select(SchemaVersionDB).where(
            SchemaVersionDB.source_id == source_id,
            SchemaVersionDB.version == version
        )

        res_current = await db.execute(query_current)
        current = res_current.scalars().first()

        if not current:
            raise HTTPException(404, "Schema version not found")

        # Get previous version
        query_prev = select(SchemaVersionDB).where(
            SchemaVersionDB.source_id == source_id,
            SchemaVersionDB.version == version - 1
        )

        res_prev = await db.execute(query_prev)
        prev = res_prev.scalars().first()

        if not prev:
            # No previous version → diff is 100% added
            return SchemaDiff(
                added=current.schema,
                removed={},
                changed={}
            )

        # Compute diff manually (same rules as SchemaGenerator)
        added = {k: v for k, v in current.schema.items() if k not in prev.schema}
        removed = {k: v for k, v in prev.schema.items() if k not in current.schema}

        changed = {}
        for k in current.schema:
            if k in prev.schema and current.schema[k] != prev.schema[k]:
                changed[k] = {
                    "old": prev.schema[k],
                    "new": current.schema[k]
                }

        return SchemaDiff(
            added=added,
            removed=removed,
            changed=changed
        )

    except Exception as e:
        logger.error("Schema diff failed", exc_info=e)
        raise HTTPException(500, str(e))
