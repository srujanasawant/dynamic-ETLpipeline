# app/utils/validators.py
from typing import List
import magic
from app.config import settings


class FileValidator:
    """Validate uploaded files"""
    
    @staticmethod
    def validate_extension(filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = f".{filename.split('.')[-1].lower()}"
        return ext in settings.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_size(size: int) -> bool:
        """Check if file size is within limit"""
        return size <= settings.MAX_UPLOAD_SIZE
    
    @staticmethod
    def validate_mime_type(content: bytes) -> str:
        """Detect and validate MIME type"""
        mime = magic.from_buffer(content, mime=True)
        
        allowed_mimes = {
            'application/pdf',
            'text/plain',
            'text/markdown',
            'application/octet-stream'  # Some text files
        }
        
        if mime not in allowed_mimes:
            raise ValueError(f"MIME type not allowed: {mime}")
        
        return mime