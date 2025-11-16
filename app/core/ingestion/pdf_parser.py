# app/core/ingestion/pdf_parser.py
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import io
import structlog
from typing import Dict, Any

logger = structlog.get_logger()


class PDFParser:
    """Parse PDF files with OCR support"""
    
    async def parse(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Extract text from PDF, with OCR fallback"""
        text_parts = []
        tables = []
        has_ocr = False
        
        try:
            # Try extracting text with PyPDF2
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
            
            # Extract tables with pdfplumber
            pdf_file.seek(0)
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    for table_idx, table in enumerate(page_tables):
                        tables.append({
                            "page": page_num + 1,
                            "table_index": table_idx,
                            "data": table
                        })
            
            # If no text extracted, try OCR
            if not text_parts or len("".join(text_parts).strip()) < 50:
                logger.info("Attempting OCR", filename=filename)
                text_parts = await self._ocr_pdf(content)
                has_ocr = True
            
            return {
                "text": "\n\n".join(text_parts),
                "tables": tables,
                "metadata": {
                    "pages": len(pdf_reader.pages),
                    "has_ocr": has_ocr,
                    "table_count": len(tables)
                }
            }
            
        except Exception as e:
            logger.error("PDF parsing failed", exc_info=e)
            raise
    
    async def _ocr_pdf(self, content: bytes) -> list:
        """Perform OCR on PDF pages"""
        # This is a simplified OCR implementation
        # In production, use AWS Textract or Google Vision API
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(content)
            
            text_parts = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image)
                if text.strip():
                    text_parts.append(f"[Page {i + 1} - OCR]\n{text}")
            
            return text_parts
        except Exception as e:
            logger.warning("OCR failed", exc_info=e)
            return ["[OCR extraction failed]"]