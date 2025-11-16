from datetime import datetime
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from app.models.database import Base

# ---------- SQLAlchemy Model (stored in Postgres) ----------

class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


# ---------- Pydantic Models (returned in API responses) ----------

class UploadResponse(BaseModel):
    id: int
    source_id: str
    filename: str
    file_type: str
    storage_path: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
