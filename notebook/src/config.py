"""
med-ml Project Configuration
Centralized configuration and environment setup for DDI risk analysis.

Usage in notebooks:
    from config import *
"""

import os
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from root .env file
# Navigate up three levels: med-ml/src -> med-ml -> med-insight
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# MinIO Configuration (Local Development)
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# SQL Server Configuration (CDWWork database)
SQLSERVER_DRIVER = os.getenv("CDWWORK_DB_DRIVER", "ODBC Driver 18 for SQL Server")
SQLSERVER_SERVER = os.getenv("CDWWORK_DB_SERVER", "127.0.0.1,1433")
SQLSERVER_DATABASE = "CDWWork"
SQLSERVER_USER = os.getenv("CDWWORK_DB_USER", "sa")
SQLSERVER_PASSWORD = os.getenv("CDWWORK_DB_PASSWORD")
SQLSERVER_TRUST_CERT = "yes"

# Source and Destination Buckets
SOURCE_BUCKET = "med-sandbox"      # External/raw datasets
DEST_BUCKET = "med-data"           # Processed ML data

# Data Paths - DDI Dataset (Drug-Drug Interactions Reference Data)
SOURCE_DDI_PATH = "kaggle-data/ddi/"                    # Source CSV location
V1_RAW_DDI_PREFIX = "v1_raw/ddi/"                       # Unmodified parquet
V2_CLEAN_DDI_PREFIX = "v2_clean/ddi/"                   # Cleaned data
V3_FEATURES_DDI_PREFIX = "v3_features/ddi/"             # Feature-engineered
V4_MODELS_DDI_PREFIX = "v4_models/ddi/"                 # Model outputs

# Data Paths - Medications Dataset (Patient Medication Exposure Data)
V1_RAW_MEDICATIONS_PREFIX = "v1_raw/medications/"       # Unified medication data
V2_CLEAN_MEDICATIONS_PREFIX = "v2_clean/medications/"   # Cleaned medication data
V3_FEATURES_MEDICATIONS_PREFIX = "v3_features/medications/"  # Feature-engineered

# Data Paths - MIMIC-IV Community Care Integration (PhysioNet MIMIC-IV Demo)
SOURCE_MIMIC_PATH = "mimic-data/hosp/"                  # MIMIC CSV files in med-sandbox
V1_RAW_MIMIC_PREFIX = "v1_raw/mimic/"                   # MIMIC parquet files in med-data

# Community Care Configuration
COMMUNITY_CARE_STA3N = 999                              # Sta3n value for community care records
COMMUNITY_CARE_SOURCE = "MIMIC-Community"               # SourceSystem identifier

# Date Range Filtering (for medication data extraction)
# Extended to include community care period (2025 full year for concurrent care)
from datetime import date
DEFAULT_DATE_RANGE_DAYS = 365
DEFAULT_END_DATE = date(2025, 12, 31)                   # Extended through 2025 for concurrent care
DEFAULT_START_DATE = date(2025, 1, 1)                   # Start of concurrent care period

# BCMA Action Type Filtering
# Include only actual medication administrations (not held/refused)
BCMA_INCLUDE_ACTION_TYPES = ['GIVEN', 'NEW BAG']

# Processing Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "100000"))

# Pandas DataFrame Configuration
pd.set_option('display.max_colwidth', 120)

# Validation
assert MINIO_SECRET_KEY, "MINIO_SECRET_KEY must be set in .env"
assert SQLSERVER_PASSWORD, "CDWWORK_DB_PASSWORD must be set in .env"

# Log configuration (without exposing secrets)
if __name__ != "__main__":
    logger = logging.getLogger(__name__)
    logger.info(f"Configuration loaded from: {env_path}")
    logger.info(f"Project root: {project_root}")
    logger.info(f"MinIO endpoint: {MINIO_ENDPOINT}")
    logger.info(f"SQL Server: {SQLSERVER_SERVER}/{SQLSERVER_DATABASE}")
    logger.info(f"Source bucket: {SOURCE_BUCKET}")
    logger.info(f"Destination bucket: {DEST_BUCKET}")
    logger.info(f"DDI source path: {SOURCE_BUCKET}/{SOURCE_DDI_PATH}")
    logger.info(f"DDI v1_raw output: {DEST_BUCKET}/{V1_RAW_DDI_PREFIX}")
    logger.info(f"Medications v1_raw output: {DEST_BUCKET}/{V1_RAW_MEDICATIONS_PREFIX}")
    logger.info(f"Default date range: {DEFAULT_START_DATE} to {DEFAULT_END_DATE}")
