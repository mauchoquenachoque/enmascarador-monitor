import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Multi-DB Masking & Performance Overhead Monitor"
    APP_VERSION: str = "5.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production-use-openssl-rand-hex-32")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local_monitor.db")
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    PG_PORT: int = int(os.getenv("PG_PORT", "5432"))
    PG_USER: str = os.getenv("PG_USER", "postgres")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "postgres")
    PG_DB: str = os.getenv("PG_DB", "masking_monitor")

    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER: str = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DB: str = os.getenv("MYSQL_DB", "mysql")

    MSSQL_HOST: str = os.getenv("MSSQL_HOST", "localhost")
    MSSQL_PORT: int = int(os.getenv("MSSQL_PORT", "1433"))
    MSSQL_USER: str = os.getenv("MSSQL_USER", "sa")
    MSSQL_PASSWORD: str = os.getenv("MSSQL_PASSWORD", "StrongPassword123!")
    MSSQL_DB: str = os.getenv("MSSQL_DB", "master")

    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "local_monitor.db")

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB: str = os.getenv("MONGO_DB", "admin")

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")

    CORS_ORIGINS: list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 60

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"

    FERNET_KEY_PATH: str = os.getenv("FERNET_KEY_PATH", ".keyfile")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
