"""
DDI Reference Data ETL Pipeline

Runs the complete medallion architecture pipeline for DDI reference data:
1. Bronze: Extract CSV from med-sandbox → Parquet
2. Silver: Clean and normalize
3. Gold: Create query-optimized reference

Usage:
    python scripts/load_ddi_reference.py

Prerequisites:
    - DDI CSV uploaded to MinIO: med-sandbox/kaggle-data/ddi/db_drug_interactions.csv
    - MinIO med-z1 bucket exists
    - Required dependencies installed (polars, boto3)
"""

import sys
import os
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from etl.bronze_ddi import extract_ddi_bronze
from etl.silver_ddi import clean_ddi_silver
from etl.gold_ddi import create_gold_ddi_reference

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_ddi_pipeline():
    """Run complete DDI reference data pipeline."""
    print("=" * 70)
    print("DDI Reference Data ETL Pipeline")
    print("=" * 70)
    print()

    try:
        # Step 1: Bronze extraction
        print("Step 1/3: Bronze Layer (CSV → Parquet)")
        print("-" * 70)
        df_bronze = extract_ddi_bronze()
        print(f"✅ Bronze complete: {len(df_bronze):,} rows")
        print()

        # Step 2: Silver cleaning
        print("Step 2/3: Silver Layer (Clean & Normalize)")
        print("-" * 70)
        df_silver = clean_ddi_silver()
        print(f"✅ Silver complete: {len(df_silver):,} rows")
        print()

        # Step 3: Gold optimization
        print("Step 3/3: Gold Layer (Query Optimization)")
        print("-" * 70)
        df_gold = create_gold_ddi_reference()
        print(f"✅ Gold complete: {len(df_gold):,} rows")
        print()

        # Summary
        print("=" * 70)
        print("Pipeline Summary")
        print("=" * 70)
        print(f"Bronze → Silver: {len(df_bronze):,} → {len(df_silver):,} rows ({len(df_bronze) - len(df_silver):,} removed)")
        print(f"Silver → Gold:   {len(df_silver):,} → {len(df_gold):,} rows ({len(df_silver) - len(df_gold):,} removed)")
        print(f"Overall:         {len(df_bronze):,} → {len(df_gold):,} rows ({100 * len(df_gold) / len(df_bronze):.1f}% retained)")
        print()
        print("✅ DDI reference data pipeline complete!")
        print()
        print("Output location:")
        print("  MinIO bucket: med-z1")
        print("  Path: gold/ddi/ddi_reference.parquet")
        print()
        print("Next steps:")
        print("  1. Test DDI analyzer with real data:")
        print("     python scripts/test_ddi_with_real_data.py")
        print("  2. Test DDI tool with LangGraph agent")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_ddi_pipeline()
