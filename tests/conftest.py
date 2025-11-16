# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from app.main import app
from app.models.database import Base
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://etl_user:etl_pass@localhost:5432/etl_test_db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine):
    """Create test database session"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# tests/test_ingestion.py
import pytest
from app.core.ingestion.file_handler import FileHandler
from app.core.ingestion.text_parser import TextParser


@pytest.mark.asyncio
async def test_text_parser():
    """Test text file parsing"""
    content = b"Hello World\nThis is a test\nkey: value"
    parser = TextParser()
    
    result = await parser.parse(content, "test.txt")
    
    assert "text" in result
    assert "Hello World" in result["text"]
    assert result["metadata"]["encoding"] == "utf-8"


@pytest.mark.asyncio
async def test_file_handler():
    """Test file handler orchestration"""
    content = b"Sample text content\nAnother line"
    handler = FileHandler()
    
    result = await handler.parse_file(content, "test.txt", ".txt")
    
    assert "text" in result
    assert len(result["text"]) > 0

