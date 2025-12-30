"""
Gold Layer: DDI Reference Data

Creates query-optimized DDI reference data for the AI Clinical Insights feature.

Source: MinIO med-z1/silver/ddi/ddi_clean.parquet
Target: MinIO med-z1/gold/ddi/ddi_reference.parquet

Transformations:
- Optimized schema for fast lookups
- Add any computed fields for future enhancements
- Final quality checks
"""

import logging

import polars as pl
from lake.minio_client import MinIOClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_gold_ddi_reference():
    """Create Gold DDI reference optimized for AI Clinical Insights."""
    logger.info("Starting Gold DDI transformation")

    # Initialize MinIO client
    client = MinIOClient()

    # Read Silver Parquet
    silver_key = "silver/ddi/ddi_clean.parquet"
    logger.info(f"Reading from Silver: {silver_key}")

    df = client.read_parquet(silver_key)
    rows_input = len(df)

    logger.info(f"Silver data: {rows_input:,} rows")
    logger.info(f"Schema: {df.schema}")

    # Gold layer transformations
    # For Phase 1, Gold = Silver (minimal transformation)
    # Future enhancements could add:
    # - Severity classification (parsed from description or external source)
    # - Drug class categorization
    # - Mechanism-based features
    # - Risk scores

    # Verify required columns exist
    required_columns = ["drug_1", "drug_2", "interaction_description"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Final quality check: ensure no nulls in required fields
    null_counts = df.null_count()
    if null_counts.select(pl.col(required_columns).sum()).row(0)[0] > 0:
        logger.warning("Found nulls in required columns - removing...")
        df = df.drop_nulls(subset=required_columns)

    rows_output = len(df)

    logger.info(f"Gold transformation complete: {rows_output:,} rows")

    # Get some statistics
    unique_drugs = set(df["drug_1"].unique().to_list() + df["drug_2"].unique().to_list())
    logger.info(f"Unique drugs in reference: {len(unique_drugs):,}")

    # Write to Gold layer
    gold_key = "gold/ddi/ddi_reference.parquet"
    logger.info(f"Writing to Gold: {gold_key}")

    client.write_parquet(df, gold_key)

    logger.info(
        f"✅ Gold layer complete: {rows_output:,} rows written to {gold_key}"
    )
    logger.info(f"   Unique drugs: {len(unique_drugs):,}")
    logger.info(f"   Memory estimate: ~{df.estimated_size('mb'):.1f} MB")

    return df


if __name__ == "__main__":
    create_gold_ddi_reference()
