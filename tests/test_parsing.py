# tests/test_parsing.py
import pytest
from app.core.parsing.fragment_detector import FragmentDetector
from app.core.parsing.type_inference import TypeInferencer


@pytest.mark.asyncio
async def test_json_detection():
    """Test JSON fragment detection"""
    text = """
    Some text here
    {"name": "John", "age": 30, "city": "New York"}
    More text
    """
    
    detector = FragmentDetector()
    fragments = detector.detect_all({"text": text})
    
    assert len(fragments["json"]) > 0
    assert fragments["json"][0]["data"]["name"] == "John"


@pytest.mark.asyncio
async def test_type_inference():
    """Test type inference"""
    inferencer = TypeInferencer()
    
    # Test integer
    result = inferencer.infer_type(42)
    assert result["type"] == "integer"
    
    # Test float
    result = inferencer.infer_type(3.14)
    assert result["type"] == "float"
    
    # Test date string
    result = inferencer.infer_type("2024-01-15", "created_date")
    assert result["type"] in ["date", "datetime"]


@pytest.mark.asyncio
async def test_kv_pair_detection():
    """Test key-value pair detection"""
    text = """
    Name: John Doe
    Email: john@example.com
    Age: 30
    Location: New York
    """
    
    detector = FragmentDetector()
    fragments = detector.detect_all({"text": text})
    
    assert len(fragments["kv_pairs"]) >= 3