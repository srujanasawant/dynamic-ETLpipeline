# app/storage/postgres.py

from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy import (
    MetaData, Table, Column,
    Integer, String, Float, Boolean, JSON, text as sql_text
)
import structlog

logger = structlog.get_logger()


# ---------------------------------------------------------
# TYPE MAP — maps inferred schema types → SQLAlchemy column
# ---------------------------------------------------------
TYPE_MAP = {
    "string": String,
    "integer": Integer,
    "float": Float,
    "boolean": Boolean,
    "date": String,   # kept as TEXT/STRING for MVP
    "json": JSON,
    "null": String,
}


class PostgresStorage:
    """
    Handles dynamic table creation + record insertion for JSON-structured data.
    """

    def __init__(self, session: AsyncSession, engine: AsyncEngine):
        self.session = session
        self.engine = engine

    # ---------------------------------------------------------
    # CREATE DYNAMIC TABLE FROM SCHEMA
    # ---------------------------------------------------------
    async def create_table_for_schema(self, table_name: str, schema: Dict[str, Dict[str, Any]]):
        """
        Create a SQL table based on an inferred schema.
        schema example:
        {
            "age": {"type": "integer", "nullable": True},
            "email": {"type": "string", "nullable": False}
        }
        """
        metadata = MetaData()

        columns = [
            Column("id", Integer, primary_key=True, autoincrement=True)
        ]

        for field_name, meta in schema.items():
            col_name = field_name.strip().lower().replace(" ", "_")

            sa_type = TYPE_MAP.get(meta.get("type", "string"), String)
            nullable = meta.get("nullable", True)

            columns.append(Column(col_name, sa_type, nullable=True))

        table = Table(table_name, metadata, *columns)

        # IMPORTANT: async engine must be used like this
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        logger.info("Dynamic table created", table=table_name)

    # ---------------------------------------------------------
    # INSERT RECORD INTO DYNAMIC TABLE
    # ---------------------------------------------------------
    async def insert_record(self, table_name: str, record: Dict[str, Any]):
        """
        Insert a row into a dynamic table.
        Keys must match schema column names.
        """
        sanitized = {
            k.strip().lower().replace(" ", "_"): v
            for k, v in record.items()
        }

        cols = ", ".join(f'"{c}"' for c in sanitized.keys())
        vals = ", ".join(f":{c}" for c in sanitized.keys())

        stmt = sql_text(f'INSERT INTO "{table_name}" ({cols}) VALUES ({vals})')

        await self.session.execute(stmt, sanitized)
        await self.session.commit()

    # ---------------------------------------------------------
    # CHECK IF TABLE EXISTS
    # ---------------------------------------------------------
    async def ensure_table_exists(self, table_name: str) -> bool:
        stmt = sql_text("SELECT to_regclass(:tname)")
        result = await self.session.execute(stmt, {"tname": table_name})
        exists = result.scalar()
        return exists is not None
