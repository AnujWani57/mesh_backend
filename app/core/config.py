import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")


class Settings:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "minemesh")
    DB_USERNAME = os.getenv("DB_USERNAME", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_PORT = os.getenv("DB_PORT", "5432")
    raw_database_url = os.getenv(
        "DATABASE_URL",
        f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )
    if raw_database_url.startswith("postgresql://") and "+psycopg" not in raw_database_url:
        DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    else:
        DATABASE_URL = raw_database_url
    if "+pg8000" in DATABASE_URL and "ssl=" not in DATABASE_URL and "sslmode=" not in DATABASE_URL:
        DATABASE_URL = raw_database_url.replace("postgresql://", "postgresql+pg8000://", 1)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    VITE_USE_DUMMY_API = os.getenv("VITE_USE_DUMMY_API", "false").lower() == "true"
    VITE_API_BASE_URL = os.getenv("VITE_API_BASE_URL", "http://127.0.0.1:8002")


settings = Settings()
