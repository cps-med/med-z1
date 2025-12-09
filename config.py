"""
med-z1 Project Configuration
Centralized configuration and environment setup.

Usage:
    from config import (
        PROJECT_ROOT,
        CDWWORK_DB_CONFIG,
        EXTRACT_DB_CONFIG,
        MINIO_CONFIG,
        PATHS,
        USE_MINIO,
    )
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv

# -----------------------------------------------------------
# Paths & environment loading
# -----------------------------------------------------------

# Path to the med-z1 project root (where this file lives)
PROJECT_ROOT = Path(__file__).resolve().parent

# Path to .env in the project root
ENV_PATH = PROJECT_ROOT / ".env"

# Load environment variables from .env (if it exists)
load_dotenv(ENV_PATH)


# -----------------------------------------------------------
# Helper functions
# -----------------------------------------------------------

def _get_bool(name: str, default: bool = False) -> bool:
    """Read a boolean-like env var (true/false/yes/no/1/0)."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y"}


def _expand_path(name: str, default: str | None = None) -> Path:
    """
    Expand ~ in a path-like env var and return a Path.
    If the env var is missing and no default is provided,
    return the current working directory.
    """
    value = os.getenv(name, default) if default is not None else os.getenv(name)
    if not value:
        return Path(".").resolve()
    return Path(os.path.expanduser(value)).resolve()


# -----------------------------------------------------------
# CDWWork (source) database configuration
# -----------------------------------------------------------

CDWWORK_DB_ENGINE = os.getenv("CDWWORK_DB_ENGINE", "MS_SQL_SERVER_2019")
CDWWORK_DB_DRIVER = os.getenv("CDWWORK_DB_DRIVER", "ODBC Driver 18 for SQL Server")
CDWWORK_DB_SERVER = os.getenv("CDWWORK_DB_SERVER", "127.0.0.1,1433")
CDWWORK_DB_NAME = os.getenv("CDWWORK_DB_NAME", "CDWWork")
CDWWORK_DB_USER = os.getenv("CDWWORK_DB_USER", "sa")
CDWWORK_DB_PASSWORD = os.getenv("CDWWORK_DB_PASSWORD", "")
TRUST_CONNECTION = _get_bool("TRUST_CONNECTION", True)
TRUST_CERT = _get_bool("TRUST_CERT", True)

CDWWORK_DB_CONFIG = {
    "engine": CDWWORK_DB_ENGINE,
    "driver": CDWWORK_DB_DRIVER,
    "server": CDWWORK_DB_SERVER,
    "name": CDWWORK_DB_NAME,
    "user": CDWWORK_DB_USER,
    "password": CDWWORK_DB_PASSWORD,
    "trust_connection": TRUST_CONNECTION,
    "trust_cert": TRUST_CERT,
}


# -----------------------------------------------------------
# Extract (intermediate) database configuration
# -----------------------------------------------------------

EXTRACT_DB_ENGINE = os.getenv("EXTRACT_DB_ENGINE", "MS_SQL_SERVER_2019")
EXTRACT_DB_DRIVER = os.getenv("EXTRACT_DB_DRIVER", "ODBC Driver 18 for SQL Server")
EXTRACT_DB_SERVER = os.getenv("EXTRACT_DB_SERVER", "127.0.0.1,1433")
EXTRACT_DB_NAME = os.getenv("EXTRACT_DB_NAME", "Extract")
EXTRACT_DB_USER = os.getenv("EXTRACT_DB_USER", "sa")
EXTRACT_DB_PASSWORD = os.getenv("EXTRACT_DB_PASSWORD", "")

EXTRACT_DB_CONFIG = {
    "engine": EXTRACT_DB_ENGINE,
    "driver": EXTRACT_DB_DRIVER,
    "server": EXTRACT_DB_SERVER,
    "name": EXTRACT_DB_NAME,
    "user": EXTRACT_DB_USER,
    "password": EXTRACT_DB_PASSWORD,
    "trust_connection": TRUST_CONNECTION,
    "trust_cert": TRUST_CERT,
}


# -----------------------------------------------------------
# MinIO / S3-compatible storage configuration
# -----------------------------------------------------------

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "")
MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "med-sandbox")
MINIO_USE_SSL = _get_bool("MINIO_USE_SSL", False)

MINIO_SANDBOX_NAME = os.getenv("MINIO_SANDBOX_NAME", None)
MINIO_DATA_NAME = os.getenv("MINIO_DATA_NAME", None)

MINIO_CONFIG = {
    "endpoint": MINIO_ENDPOINT,
    "access_key": MINIO_ACCESS_KEY,
    "secret_key": MINIO_SECRET_KEY,
    "bucket_name": MINIO_BUCKET_NAME,
    "use_ssl": MINIO_USE_SSL,
    "sandbox_name": MINIO_SANDBOX_NAME,
    "data_name": MINIO_DATA_NAME,
}


# -----------------------------------------------------------
# Storage / path configuration
# -----------------------------------------------------------

USE_MINIO = _get_bool("USE_MINIO", True)

ASCII_EXTRACT_FOLDER = _expand_path("ASCII_EXTRACT_FOLDER")
LOG_DIRECTORY_PATH = _expand_path("LOG_DIRECTORY_PATH")

PATHS = {
    "ascii_extract_folder": ASCII_EXTRACT_FOLDER,
    "log_directory_path": LOG_DIRECTORY_PATH,
}


# -----------------------------------------------------------
# CCOW Context Vault configuration
# -----------------------------------------------------------

CCOW_ENABLED = _get_bool("CCOW_ENABLED", default=True)
CCOW_URL = os.getenv("CCOW_URL", "http://localhost:8001")
CCOW_VAULT_PORT = int(os.getenv("CCOW_VAULT_PORT", "8001"))

CCOW_CONFIG = {
    "enabled": CCOW_ENABLED,
    "url": CCOW_URL,
    "port": CCOW_VAULT_PORT,
}


# -----------------------------------------------------------
# PostgreSQL Serving Database configuration
# -----------------------------------------------------------

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "medz1")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# PostgreSQL connection URL (for SQLAlchemy)
DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

POSTGRES_CONFIG = {
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
    "database": POSTGRES_DB,
    "user": POSTGRES_USER,
    "password": POSTGRES_PASSWORD,
    "url": DATABASE_URL,
}


# -----------------------------------------------------------
# Optional logging of config (without secrets)
# -----------------------------------------------------------

if __name__ != "__main__":
    logger = logging.getLogger(__name__)
    logger.info(f"Loaded config from: {ENV_PATH}")
    logger.info(f"Project root: {PROJECT_ROOT}")
    logger.info(f"CDWWORK server: {CDWWORK_DB_SERVER} / DB: {CDWWORK_DB_NAME}")
    logger.info(f"EXTRACT server: {EXTRACT_DB_SERVER} / DB: {EXTRACT_DB_NAME}")
    logger.info(f"MinIO endpoint: {MINIO_ENDPOINT}, bucket: {MINIO_BUCKET_NAME}")
    logger.info(f"USE_MINIO: {USE_MINIO}")
    logger.info(f"PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT} / DB: {POSTGRES_DB}")
    logger.info(f"ASCII extract folder: {ASCII_EXTRACT_FOLDER}")
    logger.info(f"Log directory: {LOG_DIRECTORY_PATH}")
    logger.info(f"CCOW enabled: {CCOW_ENABLED}, URL: {CCOW_URL}")
