# app/api/routes/query.py

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text as sql_text
from typing import Any, Dict, List, Optional
import structlog

from app.models.database import get_db
from app.models.query_models import (
    QueryRequest,
    QueryResponse,
)
from app.storage.mongodb import MongoDBStorage

router = APIRouter()
logger = structlog.get_logger()


# ------------------------------------------------------------
# POST /query — Execute a query on MongoDB or Postgres
# ------------------------------------------------------------
@router.post("/", response_model=QueryResponse)
async def run_query(
    request: QueryRequest,
    use_mongo: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute a simple structured query on the parsed records.

    - If use_mongo=True → query MongoDB parsed documents
    - Else → query Postgres dynamic table for the source_id

    QueryRequest:
        source: str          → source_id
        fields: List[str]    → which fields to return
        filters: dict        → exact match filters
        limit: int           → result limit
    """

    source_id = request.source
    filters = request.filters or {}
    limit = request.limit or 100
    fields = request.fields or []

    # --------------------------------------------------------
    # MONGO MODE (simplest & recommended for your ETL)
    # --------------------------------------------------------
    if use_mongo:
        try:
            mongo = MongoDBStorage()
            collection = f"{source_id}_records"

            # Build Mongo filters
            mongo_filter = {f"record.{k}": v for k, v in filters.items()}

            docs = await mongo.db[collection].find(mongo_filter).limit(limit).to_list(length=limit)

            results = []
            for d in docs:
                rec = d.get("record", {})
                if fields:
                    rec = {k: rec.get(k) for k in fields}
                results.append(rec)

            return QueryResponse(count=len(results), records=results)

        except Exception as e:
            logger.error("Mongo query failed", exc_info=e)
            raise HTTPException(500, f"MongoDB query failed: {str(e)}")

    # --------------------------------------------------------
    # POSTGRES MODE (query dynamic tables)
    # --------------------------------------------------------
    table_name = f"data_{source_id}"

    try:
        # Build SELECT clause
        if fields:
            select_cols = ", ".join(f'"{f}"' for f in fields)
        else:
            select_cols = "*"

        # Build WHERE clause
        where_clauses = []
        params = {}

        for i, (key, val) in enumerate(filters.items()):
            param_name = f"p{i}"
            where_clauses.append(f'"{key}" = :{param_name}')
            params[param_name] = val

        where_sql = " AND ".join(where_clauses)
        if where_sql:
            where_sql = "WHERE " + where_sql

        query_sql = f"""
            SELECT {select_cols}
            FROM "{table_name}"
            {where_sql}
            LIMIT :limit
        """

        params["limit"] = limit

        result = await db.execute(sql_text(query_sql), params)
        rows = [dict(r) for r in result.mappings().all()]

        return QueryResponse(count=len(rows), records=rows)

    except Exception as e:
        logger.error("Postgres query failed", exc_info=e)
        raise HTTPException(500, f"PostgreSQL query failed: {str(e)}")
