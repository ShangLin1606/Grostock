from minio import Minio
from minio.error import S3Error
from loguru import logger
import os
from dotenv import load_dotenv

load_dotenv()

class MinioClient:
    def __init__(self):
        endpoint = os.getenv("MINIO_ADDRESS", "minio:9000")  # 預設值
        access_key = os.getenv("MINIO_ROOT_USER", "minioadmin")
        secret_key = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")

        if not all([endpoint, access_key, secret_key]):
            raise ValueError("MinIO configuration is incomplete. Please set MINIO_ADDRESS, MINIO_ROOT_USER, and MINIO_ROOT_PASSWORD in .env")

        try:
            self.client = Minio(
                endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=False  # 本地測試使用 HTTP，AWS 部署改為 True
            )
            self.bucket_name = "grostock"

            # 確保 bucket 存在
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
            else:
                logger.info(f"MinIO bucket {self.bucket_name} already exists")
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

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