# tests/test_api.py
import pytest
from io import BytesIO


@pytest.mark.asyncio
async def test_upload_endpoint(client):
    """Test file upload endpoint"""
    content = b"Test content\nkey: value\nname: John"
    
    files = {"file": ("test.txt", BytesIO(content), "text/plain")}
    
    response = await client.post(
        "/upload/",
        files=files,
        data={"source_id": "test_source"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "source_id" in data
    assert "schema_id" in data


@pytest.mark.asyncio
async def test_schema_endpoint(client):
    """Test schema retrieval endpoint"""
    # First upload a file
    content = b"Test content\nid: 1\nname: John"
    files = {"file": ("test.txt", BytesIO(content), "text/plain")}
    
    upload_response = await client.post(
        "/upload/",
        files=files,
        data={"source_id": "test_source"}
    )
    
    source_id = upload_response.json()["source_id"]
    
    # Get schema
    response = await client.get(f"/schema/?source_id={source_id}")
    
    assert response.status_code == 200
    schema = response.json()
    assert "fields" in schema
    assert len(schema["fields"]) > 0
