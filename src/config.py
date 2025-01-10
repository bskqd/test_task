import os
from pathlib import Path, PosixPath
from typing import Optional

from passlib.context import CryptContext
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    HOST_DOMAIN: str = os.getenv("HOST_DOMAIN", "http://127.0.0.1:8000")

    BASE_DIR: PosixPath = Path(__file__).resolve().parent

    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    JWT_TOKEN_TYPE_NAME: str = os.getenv("JWT_TOKEN_TYPE_NAME", "Bearer")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 1440))
    JWT_ACCESS_TOKEN_TYPE: str = os.getenv("JWT_ACCESS_TOKEN_TYPE", "access_token")
    JWT_REFRESH_TOKEN_TYPE: str = os.getenv("JWT_REFRESH_TOKEN_TYPE", "refresh_token")

    MINIO_URL: str = os.getenv("MINIO_URL", "minio:9000")
    MINIO_SECURE: bool = bool(os.getenv("MINIO_SECURE", ""))
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY")
    MINIO_PUBLIC_HOST: Optional[str] = os.getenv("MINIO_PUBLIC_HOST")

    TICKET_FILES_BUCKET_NAME: str = os.getenv("TICKET_FILES_BUCKET_NAME", "files")

    class Config:
        frozen = True
