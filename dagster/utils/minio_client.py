from minio import Minio
from minio.error import S3Error
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class MinioClient:
    def __init__(self):
        self.client = Minio(
            os.getenv("MINIO_ADDRESS"),
            access_key=os.getenv("MINIO_ROOT_USER"),
            secret_key=os.getenv("MINIO_ROOT_PASSWORD"),
            secure=False  # 本地測試使用 HTTP，AWS 部署改為 True
        )
        self.bucket_name = "grostock"

        # 確保 bucket 存在
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.info(f"Created MinIO bucket: {self.bucket_name}")

    def upload_file(self, file_path, object_name):
        try:
            self.client.fput_object(self.bucket_name, object_name, file_path)
            logger.info(f"Uploaded {file_path} to MinIO as {object_name}")
        except S3Error as e:
            logger.error(f"Failed to upload {file_path} to MinIO: {e}")

    def download_file(self, object_name, file_path):
        try:
            self.client.fget_object(self.bucket_name, object_name, file_path)
            logger.info(f"Downloaded {object_name} from MinIO to {file_path}")
        except S3Error as e:
            logger.error(f"Failed to download {object_name} from MinIO: {e}")

minio_client = MinioClient()