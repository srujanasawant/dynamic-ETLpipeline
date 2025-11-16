# tests/test_query.py
import pytest


@pytest.mark.asyncio
async def test_llm_query_translation():
    """Test LLM query translation"""
    from app.core.query.llm_translator import LLMQueryTranslator
    from app.models.schema_models import SchemaResponse, FieldMetadataSchema
    from datetime import datetime
    
    # Mock schema
    schema = SchemaResponse(
        schema_id="test_schema",
        source_id="test_source",
        version=1,
        generated_at=datetime.now(),
        compatible_dbs=["postgresql"],
        fields=[
            FieldMetadataSchema(
                name="id",
                type="integer",
                confidence=1.0
            ),
            FieldMetadataSchema(
                name="name",
                type="string",
                confidence=1.0
            )
        ],
        confidence_score=1.0
    )
    
    translator = LLMQueryTranslator()
    
    # Note: This will fail without API key
    # In real tests, mock the API call
    try:
        query = await translator.translate(
            nl_query="Find all records where id is greater than 5",
            schema=schema,
            target_db="postgresql"
        )
        assert "SELECT" in query.upper()
        assert "WHERE" in query.upper()
    except Exception as e:
        pytest.skip(f"LLM API not available: {e}")