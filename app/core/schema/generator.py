# app/core/schema/generator.py

import structlog
from typing import Dict, Any, Tuple, Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schema_models import (
    SchemaVersionDB,
    SchemaDiff
)
from app.models.database import AsyncSessionLocal

logger = structlog.get_logger()


# -------------------------------------------------------------
# Merge logic (safe + deterministic)
# -------------------------------------------------------------
def merge_field_definitions(
    existing: Dict[str, Dict[str, Any]],
    new: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    merged = {k: dict(v) for k, v in existing.items()}

    for name, meta in new.items():
        if name not in merged:
            merged[name] = dict(meta)
            continue

        current = merged[name]

        # Type harmonization
        if current.get("type") != meta.get("type"):
            # Fallback to string if incompatible
            if "string" in (current.get("type"), meta.get("type")):
                current["type"] = "string"

        # Nullable handling (nullable only if both say nullable)
        current["nullable"] = current.get("nullable", True) and meta.get("nullable", True)

        # Example propagation
        if current.get("example") is None and meta.get("example") is not None:
            current["example"] = meta["example"]

    return merged


# -------------------------------------------------------------
# Schema Generator
# -------------------------------------------------------------
class SchemaGenerator:
    """
    Handles schema evolution for each source_id.
    Creates versioned schemas stored in Postgres.
    """

    async def _get_latest_version(
        self, session: AsyncSession, source_id: str
    ) -> Optional[SchemaVersionDB]:

        stmt = (
            select(SchemaVersionDB)
            .where(SchemaVersionDB.source_id == source_id)
            .order_by(desc(SchemaVersionDB.version))
            .limit(1)
        )

        result = await session.execute(stmt)
        return result.scalars().first()

    # ---------------------------------------------------------
    async def get_current_schema(self, source_id: str) -> Optional[Dict[str, Any]]:
        async with AsyncSessionLocal() as session:
            latest = await self._get_latest_version(session, source_id)
            return latest.schema if latest else None

    # ---------------------------------------------------------
    async def register_schema(
        self,
        source_id: str,
        new_schema: Dict[str, Dict[str, Any]],
        comment: Optional[str] = None
    ) -> Tuple[int, SchemaDiff]:

        async with AsyncSessionLocal() as session:
            latest = await self._get_latest_version(session, source_id)

            # First-time schema
            if latest is None:
                version = 1
                merged = new_schema

                diff = SchemaDiff(
                    added=new_schema,
                    removed={},
                    changed={}
                )

            else:
                version = latest.version + 1
                old_schema = latest.schema or {}

                # Compute diff
                added = {k: v for k, v in new_schema.items() if k not in old_schema}
                removed = {k: v for k, v in old_schema.items() if k not in new_schema}

                changed = {}
                for k in new_schema:
                    if k in old_schema and new_schema[k] != old_schema[k]:
                        changed[k] = {
                            "old": old_schema[k],
                            "new": new_schema[k]
                        }

                diff = SchemaDiff(
                    added=added,
                    removed=removed,
                    changed=changed
                )

                # Merge schemas for storage
                merged = merge_field_definitions(old_schema, new_schema)

            # Store the schema version in Postgres
            row = SchemaVersionDB(
                source_id=source_id,
                version=version,
                schema=merged,
                comment=comment
            )

            session.add(row)
            await session.commit()
            await session.refresh(row)

            return version, diff
