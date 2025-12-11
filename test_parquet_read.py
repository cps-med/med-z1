#!/usr/bin/env python3
# ---------------------------------------------------------------------
# test_parquet_read.py
# ---------------------------------------------------------------------
# Diagnostic script to test reading parquet files from MinIO
# ---------------------------------------------------------------------

import polars as pl
import logging
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_read_silver():
    """Test reading Silver patient parquet file."""
    logger.info("=" * 70)
    logger.info("Testing Silver Patient Parquet Read")
    logger.info("=" * 70)

    try:
        minio_client = MinIOClient()
        silver_path = build_silver_path("patient", "patient_cleaned.parquet")

        logger.info(f"Attempting to read: {silver_path}")
        df = minio_client.read_parquet(silver_path)

        logger.info(f"✅ SUCCESS: Read {len(df)} rows")
        logger.info(f"Schema: {df.schema}")
        logger.info(f"Columns: {df.columns}")
        logger.info(f"Shape: {df.shape}")

        # Show first few rows
        logger.info("\nFirst 3 rows:")
        print(df.head(3))

        # Check for NULL values in new columns
        logger.info("\nNULL counts in new columns:")
        print(df.select([
            pl.col("address_street1").is_null().sum().alias("address_street1_nulls"),
            pl.col("address_city").is_null().sum().alias("address_city_nulls"),
            pl.col("insurance_company_name").is_null().sum().alias("insurance_nulls"),
        ]))

        return True

    except Exception as e:
        logger.error(f"❌ FAILED to read Silver parquet: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_read_gold():
    """Test reading Gold patient demographics parquet file."""
    logger.info("\n" + "=" * 70)
    logger.info("Testing Gold Patient Demographics Parquet Read")
    logger.info("=" * 70)

    try:
        minio_client = MinIOClient()
        gold_path = build_gold_path("patient_demographics", "patient_demographics.parquet")

        logger.info(f"Attempting to read: {gold_path}")
        df = minio_client.read_parquet(gold_path)

        logger.info(f"✅ SUCCESS: Read {len(df)} rows")
        logger.info(f"Schema: {df.schema}")
        logger.info(f"Columns: {df.columns}")
        logger.info(f"Shape: {df.shape}")

        # Show first few rows
        logger.info("\nFirst 3 rows:")
        print(df.head(3))

        # Check for NULL values in new columns
        logger.info("\nNULL counts in new columns:")
        print(df.select([
            pl.col("address_street1").is_null().sum().alias("address_street1_nulls"),
            pl.col("address_city").is_null().sum().alias("address_city_nulls"),
            pl.col("insurance_company_name").is_null().sum().alias("insurance_nulls"),
        ]))

        return True

    except Exception as e:
        logger.error(f"❌ FAILED to read Gold parquet: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    silver_ok = test_read_silver()
    gold_ok = test_read_gold()

    logger.info("\n" + "=" * 70)
    logger.info("Test Summary")
    logger.info("=" * 70)
    logger.info(f"Silver parquet: {'✅ OK' if silver_ok else '❌ FAILED'}")
    logger.info(f"Gold parquet: {'✅ OK' if gold_ok else '❌ FAILED'}")
