# app/models/schema_models.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlalchemy import (
    Column, Integer, String, DateTime, JSON, Text
)
from app.models.database import Base


# SQLAlchemy table for storing schema versions
class SchemaVersionDB(Base):
    __tablename__ = "schema_versions"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    schema = Column(JSON, nullable=False)  # { field_name: { type: "string", ... } }
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text, nullable=True)


# Pydantic models used by API and internal code
class FieldMetadata(BaseModel):
    name: str
    type: str
    example: Optional[Any] = None
    nullable: Optional[bool] = True

class FieldMetadataSchema(BaseModel):
    fields: List[FieldMetadata]

class SchemaVersion(BaseModel):
    id: int
    source_id: str
    version: int
    schema: Dict[str, Dict[str, Any]]
    created_at: datetime
    comment: Optional[str] = None

    class Config:
        orm_mode = True

class SchemaResponse(BaseModel):
    source_id: str
    current_version: int
    schema: Dict[str, Dict[str, Any]]

class SchemaHistoryItem(BaseModel):
    id: int
    version: int
    schema: Dict[str, Dict[str, Any]    ]
    created_at: datetime

class SchemaHistoryResponse(BaseModel):
    source_id: str
    history: List[SchemaHistoryItem]

class SchemaDiff(BaseModel):
    added: Dict[str, Dict[str, Any]]
    removed: Dict[str, Dict[str, Any]]
    changed: Dict[str, Dict[str, Any]]
