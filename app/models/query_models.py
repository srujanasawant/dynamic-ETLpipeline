from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class QueryRequest(BaseModel):
    source: str
    fields: List[str]
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 100


class QueryResponse(BaseModel):
    count: int
    records: List[Dict[str, Any]]


class PaginatedQueryResponse(BaseModel):
    page: int
    page_size: int
    total_count: int
    results: List[Dict[str, Any]]


class QueryExecution(BaseModel):
    query: Dict[str, Any]
    executed_at: str
    duration_ms: float
    result_count: int


class QueryStatus(BaseModel):
    status: str              # e.g., "running", "completed", "failed"
    message: Optional[str] = None  # additional info or error message
    executed_at: Optional[str] = None
    duration_ms: Optional[float] = None