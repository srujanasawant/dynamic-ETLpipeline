# tests/test_schema.py
import pytest
from app.core.schema.generator import SchemaGenerator


@pytest.mark.asyncio
async def test_schema_generation(test_db):
    """Test schema generation"""
    fragments = {
        "json": [{
            "data": {"id": 1, "name": "Test", "email": "test@example.com"},
            "offset": 0,
            "confidence": 1.0
        }],
        "html_tables": [],
        "csv": [],
        "kv_pairs": [],
        "text": []
    }
    
    generator = SchemaGenerator()
    schema = await generator.generate_schema(
        source_id="test_source",
        fragments=fragments,
        db=test_db
    )
    
    assert schema.source_id == "test_source"
    assert schema.version == 1
    assert len(schema.fields) >= 3
    assert "postgresql" in schema.compatible_dbs


@pytest.mark.asyncio
async def test_schema_evolution(test_db):
    """Test schema evolution"""
    # First version
    fragments_v1 = {
        "json": [{
            "data": {"id": 1, "name": "Test"},
            "offset": 0,
            "confidence": 1.0
        }],
        "html_tables": [],
        "csv": [],
        "kv_pairs": [],
        "text": []
    }
    
    generator = SchemaGenerator()
    schema_v1 = await generator.generate_schema(
        source_id="test_source",
        fragments=fragments_v1,
        db=test_db
    )
    
    # Second version with new field
    fragments_v2 = {
        "json": [{
            "data": {"id": 1, "name": "Test", "email": "test@example.com"},
            "offset": 0,
            "confidence": 1.0
        }],
        "html_tables": [],
        "csv": [],
        "kv_pairs": [],
        "text": []
    }
    
    schema_v2 = await generator.generate_schema(
        source_id="test_source",
        fragments=fragments_v2,
        db=test_db
    )
    
    assert schema_v2.version == 2
    assert "Added fields: email" in schema_v2.migration_notes
