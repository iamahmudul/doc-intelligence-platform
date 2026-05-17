from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Document Intelligence Backend"
    admin_email: str
    items_per_user: int = 50

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # MinIO
    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_NAME: str

    # ChromaDB
    CHROMA_HOST: str
    CHROMA_PORT: int = 8000

    # HuggingFace
    HUGGINGFACE_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
