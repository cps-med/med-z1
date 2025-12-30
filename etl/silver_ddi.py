"""
Silver Layer: DDI Reference Data

Cleans and normalizes DDI data from Bronze layer.

Source: MinIO med-z1/bronze/ddi/ddi_raw.parquet
Target: MinIO med-z1/silver/ddi/ddi_clean.parquet

Transformations:
- Normalize column names (Drug 1 → drug_1, etc.)
- Remove duplicates
- Handle missing values
- Lowercase drug names for consistency
- Remove invalid records
"""

import logging

import polars as pl
from lake.minio_client import MinIOClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def clean_ddi_silver():
    """Clean and normalize DDI data from Bronze to Silver."""
    logger.info("Starting Silver DDI transformation")

    # Initialize MinIO client
    client = MinIOClient()

    # Read Bronze Parquet
    bronze_key = "bronze/ddi/ddi_raw.parquet"
    logger.info(f"Reading from Bronze: {bronze_key}")

    df = client.read_parquet(bronze_key)
    rows_input = len(df)

    logger.info(f"Bronze data: {rows_input:,} rows")
    logger.info(f"Columns: {df.columns}")

    # Normalize column names (Kaggle CSV uses "Drug 1", "Drug 2", "Interaction Description")
    # Rename to standardized snake_case names
    df = df.rename({
        "Drug 1": "drug_1",
        "Drug 2": "drug_2",
        "Interaction Description": "interaction_description"
    })

    # Remove rows with missing values
    df = df.drop_nulls()
    rows_after_nulls = len(df)
    logger.info(f"After removing nulls: {rows_after_nulls:,} rows ({rows_input - rows_after_nulls:,} removed)")

    # Remove duplicate interactions (same drug pair)
    df = df.unique(subset=["drug_1", "drug_2"])
    rows_after_dedup = len(df)
    logger.info(f"After deduplication: {rows_after_dedup:,} rows ({rows_after_nulls - rows_after_dedup:,} removed)")

    # Lowercase drug names for consistency
    df = df.with_columns([
        pl.col("drug_1").str.to_lowercase(),
        pl.col("drug_2").str.to_lowercase()
    ])

    # Remove any rows where drug names are empty after lowercasing
    df = df.filter(
        (pl.col("drug_1").str.len_chars() > 0) &
        (pl.col("drug_2").str.len_chars() > 0) &
        (pl.col("interaction_description").str.len_chars() > 0)
    )
    rows_output = len(df)

    # Calculate statistics
    rows_removed = rows_input - rows_output
    pct_removed = (rows_removed / rows_input * 100) if rows_input > 0 else 0

    logger.info(
        f"Cleaning complete: {rows_output:,} rows ({rows_removed:,} removed, {pct_removed:.1f}%)"
    )

    # Write to Silver layer
    silver_key = "silver/ddi/ddi_clean.parquet"
    logger.info(f"Writing to Silver: {silver_key}")

    client.write_parquet(df, silver_key)

    logger.info(f"✅ Silver transformation complete: {rows_output:,} rows written")

    return df


if __name__ == "__main__":
    clean_ddi_silver()
