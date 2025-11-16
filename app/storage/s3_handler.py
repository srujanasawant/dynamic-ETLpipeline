# app/storage/s3_handler.py
import structlog
from minio import Minio
from minio.error import S3Error
from app.config import settings
import io

logger = structlog.get_logger()


class S3Handler:
    """Handle file storage in MinIO/S3"""
    
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        """Ensure bucket exists"""
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
                logger.info(f"Created bucket: {settings.MINIO_BUCKET}")
        except S3Error as e:
            logger.error("Bucket creation failed", exc_info=e)
    
    async def upload_file(self, file_id: str, content: bytes, filename: str) -> str:
        """Upload file to S3/MinIO"""
        try:
            object_name = f"uploads/{file_id}/{filename}"
            
            self.client.put_object(
                settings.MINIO_BUCKET,
                object_name,
                io.BytesIO(content),
                length=len(content)
            )
            
            logger.info("File uploaded", object_name=object_name)
            return object_name
            
        except S3Error as e:
            logger.error("File upload failed", exc_info=e)
            raise
    
    async def download_file(self, storage_path: str) -> bytes:
        """Download file from S3/MinIO"""
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, storage_path)
            content = response.read()
            response.close()
            response.release_conn()
            return content
        except S3Error as e:
            logger.error("File download failed", exc_info=e)
            raise
