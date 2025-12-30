"""
Bronze Layer: DDI Reference Data

Extracts drug-drug interaction data from Kaggle CSV and saves to Bronze layer.

Source: MinIO med-sandbox/kaggle-data/ddi/db_drug_interactions.csv
Target: MinIO med-z1/bronze/ddi/ddi_raw.parquet

Data Source: Kaggle DrugBank dataset
URL: https://www.kaggle.com/datasets/mghobashy/drug-drug-interactions/data
Schema: Drug 1, Drug 2, Interaction Description
"""

import logging
from pathlib import Path

import polars as pl
from lake.minio_client import MinIOClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_ddi_bronze():
    """Extract DDI data from CSV to Bronze Parquet."""
    logger.info("Starting Bronze DDI extraction")

    # Initialize MinIO client
    client = MinIOClient()

    # Read CSV from med-sandbox bucket
    csv_key = "kaggle-data/ddi/db_drug_interactions.csv"
    logger.info(f"Reading CSV from MinIO: {csv_key}")

    try:
        # Download CSV from MinIO
        response = client.s3_client.get_object(
            Bucket='med-sandbox',  # Raw data bucket
            Key=csv_key
        )
        csv_data = response['Body'].read()

        # Read CSV into Polars DataFrame
        df = pl.read_csv(csv_data)

        logger.info(f"Loaded {len(df):,} rows from CSV")
        logger.info(f"Columns: {df.columns}")
        logger.info(f"Schema: {df.schema}")

        # Write to Bronze layer (minimal transformation - just CSV → Parquet)
        bronze_key = "bronze/ddi/ddi_raw.parquet"
        logger.info(f"Writing Bronze Parquet: {bronze_key}")

        client.write_parquet(df, bronze_key)

        logger.info(
            f"✅ Bronze extraction complete: {len(df):,} rows written to {bronze_key}"
        )

        return df

    except Exception as e:
        logger.error(f"Failed to extract DDI Bronze data: {e}")
        raise


if __name__ == "__main__":
    extract_ddi_bronze()
