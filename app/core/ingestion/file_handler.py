# app/core/ingestion/file_handler.py
import structlog
from typing import Dict, Any
from app.core.ingestion.pdf_parser import PDFParser
from app.core.ingestion.text_parser import TextParser
from app.core.ingestion.markdown_parser import MarkdownParser

logger = structlog.get_logger()


class FileHandler:
    """Orchestrates file parsing based on file type"""
    
    def __init__(self):
        self.parsers = {
            '.pdf': PDFParser(),
            '.txt': TextParser(),
            '.md': MarkdownParser()
        }
    
    async def parse_file(self, content: bytes, filename: str, file_ext: str) -> Dict[str, Any]:
        """Parse file and return structured content"""
        try:
            parser = self.parsers.get(file_ext)
            if not parser:
                raise ValueError(f"No parser available for {file_ext}")
            
            result = await parser.parse(content, filename)
            
            logger.info(
                "File parsed successfully",
                filename=filename,
                file_type=file_ext,
                text_length=len(result.get("text", ""))
            )
            
            return result
            
        except Exception as e:
            logger.error("File parsing failed", exc_info=e, filename=filename)
            raise