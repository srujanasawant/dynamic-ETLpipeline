# app/core/ingestion/text_parser.py
import structlog
from typing import Dict, Any

logger = structlog.get_logger()


class TextParser:
    """Parse plain text files"""
    
    async def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text and detect encoding"""
        try:
            # Try UTF-8 first
            try:
                text = content.decode('utf-8')
                encoding = 'utf-8'
            except UnicodeDecodeError:
                # Fallback to latin-1
                text = content.decode('latin-1')
                encoding = 'latin-1'
            
            return {
                "text": text,
                "metadata": {
                    "encoding": encoding,
                    "size_bytes": len(content),
                    "line_count": text.count('\n') + 1
                }
            }
            
        except Exception as e:
            logger.error("Text parsing failed", exc_info=e)
            raise

