# app/core/etl/pipeline.py

import uuid
import structlog
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.parsing.fragment_detector import FragmentDetector
from app.core.parsing.field_extractor import FieldExtractor
from app.core.parsing.data_cleaner import DataCleaner
from app.core.schema.generator import SchemaGenerator

from app.storage.s3_handler import S3Handler
from app.storage.postgres import PostgresStorage
from app.storage.mongodb import MongoDBStorage

from app.models.database import AsyncSessionLocal, engine


logger = structlog.get_logger()


class ETLPipeline:
    """
    Full end-to-end ETL pipeline for text-based uploads.
    """

    def __init__(self):
        self.detector = FragmentDetector()
        self.extractor = FieldExtractor()
        self.cleaner = DataCleaner()
        self.schema_gen = SchemaGenerator()
        self.s3 = S3Handler()
        self.mongo = MongoDBStorage()

    # -------------------------------------------------------------
    # MAIN ENTRY: PROCESS A TEXT FILE
    # -------------------------------------------------------------
    async def process_text(self, source_id: str, text: str, filename: str = None):
        """
        Executes:
          1. detect fragments
          2. extract structured fields
          3. clean fields
          4. compute + register schema
          5. ensure Postgres dynamic table exists
          6. insert cleaned rows into Postgres
          7. insert cleaned rows into MongoDB
          8. store raw file in S3
        """

        # ----------------------------------
        # 1. Fragment detection
        # ----------------------------------
        fragments = self.detector.detect_fragments(text)

        # ----------------------------------
        # 2. Extract candidate field groups
        # ----------------------------------
        extracted_groups = self.extractor.extract_fields(fragments)

        cleaned_records: List[Dict[str, Any]] = []
        unified_schema: Dict[str, Dict[str, Any]] = {}

        # ----------------------------------
        # 3. Clean + assemble schema
        # ----------------------------------
        for group in extracted_groups:
            raw_fields = group.get("fields", {})

            # clean values → {field: cleaned_value}
            cleaned = self.cleaner.clean(raw_fields)
            cleaned_records.append(cleaned)

            # push schema metadata
            for k, meta in raw_fields.items():
                unified_schema[k] = {
                    "type": meta.get("type", "string"),
                    "nullable": (meta.get("value") is None),
                    "example": meta.get("value")
                }

        # ----------------------------------
        # 4. Register schema version
        # ----------------------------------
        version, diff = await self.schema_gen.register_schema(source_id, unified_schema)

        # ----------------------------------
        # 5. Store records (Postgres + Mongo)
        # ----------------------------------
        async with AsyncSessionLocal() as session:

            pg = PostgresStorage(session, engine)
            table_name = f"data_{source_id}"

            # ensure table exists with the schema of latest version
            await pg.create_table_for_schema(table_name, unified_schema)

            # INSERT rows into Postgres
            for rec in cleaned_records:
                await pg.insert_record(table_name, rec)

            # INSERT rows into Mongo
            for rec in cleaned_records:
                await self.mongo.insert_record(
                    collection=f"{source_id}_records",
                    document={
                        "source_id": source_id,
                        "schema_version": version,
                        "record": rec
                    }
                )

        # ----------------------------------
        # 6. Store raw file in S3
        # ----------------------------------
        if filename:
            file_id = str(uuid.uuid4())
            # S3 client is synchronous → DO NOT await the call
            await self._upload_async(file_id, text.encode("utf-8"), filename)

        return {
            "source_id": source_id,
            "schema_version": version,
            "diff": diff,
            "records_added": len(cleaned_records),
        }

    # -------------------------------------------------------------
    # Helper to wrap sync S3 upload inside async
    # -------------------------------------------------------------
    async def _upload_async(self, file_id: str, content: bytes, filename: str):
        """
        Run blocking MinIO upload in an async manner using a threadpool.
        """
        import asyncio
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3.upload_file(file_id, content, filename)
        )
