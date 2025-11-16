# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog

from app.utils.logging import setup_logging
from app.config import settings
from app.models.database import init_db

# Routers are imported later to avoid premature model loading
from app.api.routes import upload, schema, query, records


# ---------------------------------------------------------
# Init logging
# ---------------------------------------------------------
setup_logging()
logger = structlog.get_logger()


# ---------------------------------------------------------
# Lifespan Context Manager
# ---------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs once when FastAPI starts and once on shutdown.
    Safe place to initialize database and other dependencies.
    """
    logger.info("Starting Dynamic ETL Pipeline")

    # Initialize database tables
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error("Database initialization failed", exc_info=e)
        raise

    yield

    logger.info("Shutting down Dynamic ETL Pipeline")


# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------
app = FastAPI(
    title="Dynamic ETL Pipeline",
    description="Schema-evolving ETL for unstructured data",
    version="1.0.0",
    lifespan=lifespan
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ---------------------------------------------------------
# Routers
# ---------------------------------------------------------
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(schema.router, prefix="/schema", tags=["Schema"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(records.router, prefix="/records", tags=["Records"])

# ---------------------------------------------------------
# Endpoints
# ---------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Dynamic ETL Pipeline API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
