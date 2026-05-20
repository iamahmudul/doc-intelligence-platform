import boto3
from botocore.exceptions import NoCredentialsError
import os
from botocore.client import Config
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def get_minio_client():
    print("MinIO Config:")
    return boto3.client(
        's3',
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ROOT_USER,
        aws_secret_access_key=settings.MINIO_ROOT_PASSWORD,
        config=Config(signature_version='s3v4'),
        region_name="us-east-1"
    )

def ensure_bucket_exists():
    client = get_minio_client()
    try:
        client.head_bucket(Bucket=settings.MINIO_BUCKET_NAME)
        logger.info(f"Bucket '{settings.MINIO_BUCKET_NAME}' already exists.")
    except client.exceptions.NoSuchBucket:
        client.create_bucket(Bucket=settings.MINIO_BUCKET_NAME)
        logger.info(f"Bucket '{settings.MINIO_BUCKET_NAME}' created successfully.")
    except NoCredentialsError:
        logger.error("MinIO credentials not found. Please check your configuration.")

def upload_file(file_bytes: bytes, storage_key: str, content_type: str) -> str:
    client = get_minio_client()
    print("client===========", client)
    try:
        client.put_object(
            Bucket=settings.MINIO_BUCKET_NAME,
            Key=storage_key,
            Body=file_bytes,
            ContentType=content_type
        )
        logger.info(f"File uploaded successfully to '{storage_key}' in bucket '{settings.MINIO_BUCKET_NAME}'.")
        return storage_key
    except NoCredentialsError:
        logger.error("MinIO credentials not found. Please check your configuration.")
        raise Exception("MinIO credentials not found.")
    
def delete_file(storage_key: str) -> None:
    client = get_minio_client()
    try:
        client.delete_object(Bucket=settings.MINIO_BUCKET_NAME, Key=storage_key)
        logger.info(f"File '{storage_key}' deleted successfully from bucket '{settings.MINIO_BUCKET_NAME}'.")
    except NoCredentialsError:
        logger.error("MinIO credentials not found. Please check your configuration.")
        raise Exception("MinIO credentials not found.")
    
def get_presigned_url(storage_key: str, expires_in: int = 3600) -> str:
    client = get_minio_client()
    try:
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.MINIO_BUCKET_NAME, 'Key': storage_key},
            ExpiresIn=expires_in
        )
        logger.info(f"Presigned URL generated successfully for '{storage_key}'.")
        return url
    except NoCredentialsError:
        logger.error("MinIO credentials not found. Please check your configuration.")
        raise Exception("MinIO credentials not found.")
