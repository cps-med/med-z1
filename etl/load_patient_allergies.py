"""
load_patient_allergies.py

Load PostgreSQL DB with Gold layer patient allergies data.
- Read from med-z1/gold/patient_allergies
- Load to PostgreSQL patient_allergies table
- Optionally load patient_allergy_reactions table (normalized reactions)

To run this script from the project root folder:
  $ cd med-z1
  $ python -m etl.load_patient_allergies
"""

import polars as pl
import pandas as pd
from sqlalchemy import create_engine, text
import logging
from config import DATABASE_URL  # PostgreSQL connection string
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_patient_allergies_to_postgres():
    """Load Gold patient allergies from MinIO to PostgreSQL."""

    logger.info("Loading patient allergies to PostgreSQL...")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # =========================================================================
    # Read Gold Parquet from MinIO
    # =========================================================================

    gold_path = build_gold_path(
        "patient_allergies",
        "patient_allergies.parquet"
    )
    df = minio_client.read_parquet(gold_path)
    logger.info(f"Read {len(df)} allergy records from Gold layer")

    # =========================================================================
    # Prepare data for PostgreSQL
    # =========================================================================

    # Convert Polars to Pandas (for SQLAlchemy compatibility)
    df_pandas = df.to_pandas()

    # Rename columns to match PostgreSQL schema
    df_pandas = df_pandas.rename(columns={
        "patient_key": "patient_key",
        "patient_allergy_sid": "allergy_sid",
        "allergen_local": "allergen_local",
        "allergen_name": "allergen_standardized",
        "allergen_type": "allergen_type",
        "severity_name": "severity",
        "severity_rank": "severity_rank",
        "reactions": "reactions",
        "reaction_count": "reaction_count",
        "origination_datetime": "origination_date",
        "observed_datetime": "observed_date",
        "historical_or_observed": "historical_or_observed",
        "originating_site_sta3n": "originating_site",
        "originating_site_name": "originating_site_name",
        "comment": "comment",
        "verification_status": "verification_status",
        "is_drug_allergy": "is_drug_allergy",
        "source_system": "source_system",
        "last_updated": "last_updated",
    })

    # Add placeholder fields for future enhancements
    df_pandas["originating_staff"] = None  # Not yet populated in mock data
    df_pandas["is_active"] = True          # All allergies are active in this phase

    # =========================================================================
    # Load to PostgreSQL
    # =========================================================================

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    logger.info("Writing to patient_allergies table...")
    df_pandas.to_sql(
        "patient_allergies",
        engine,
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} allergies to PostgreSQL patient_allergies table")

    # =========================================================================
    # Verify data loaded correctly
    # =========================================================================

    with engine.connect() as conn:
        # Check row count
        result = conn.execute(text("SELECT COUNT(*) FROM patient_allergies")).fetchone()
        logger.info(f"Verification: {result[0]} rows in patient_allergies table")

        # Check allergy type distribution
        type_dist = conn.execute(text("""
            SELECT allergen_type, COUNT(*) as count
            FROM patient_allergies
            GROUP BY allergen_type
            ORDER BY count DESC
        """)).fetchall()

        logger.info("Allergy type distribution:")
        for row in type_dist:
            logger.info(f"  - {row[0]}: {row[1]}")

        # Check severity distribution
        severity_dist = conn.execute(text("""
            SELECT severity, COUNT(*) as count
            FROM patient_allergies
            WHERE severity IS NOT NULL
            GROUP BY severity
            ORDER BY count DESC
        """)).fetchall()

        logger.info("Severity distribution:")
        for row in severity_dist:
            logger.info(f"  - {row[0]}: {row[1]}")

    # =========================================================================
    # Optionally load patient_allergy_reactions table (normalized)
    # =========================================================================

    logger.info("Loading patient_allergy_reactions table (normalized reactions)...")

    # Extract individual reactions from the comma-separated string
    reactions_list = []
    for _, row in df_pandas.iterrows():
        if pd.notna(row['reactions']) and row['reactions']:
            reaction_names = row['reactions'].split(', ')
            for reaction_name in reaction_names:
                reactions_list.append({
                    'allergy_sid': row['allergy_sid'],
                    'patient_key': row['patient_key'],
                    'reaction_name': reaction_name.strip(),
                })

    if reactions_list:
        df_reactions = pd.DataFrame(reactions_list)

        df_reactions.to_sql(
            "patient_allergy_reactions",
            engine,
            if_exists="replace",
            index=False,
            method="multi",
        )

        logger.info(f"Loaded {len(df_reactions)} reaction records to patient_allergy_reactions table")

        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM patient_allergy_reactions")).fetchone()
            logger.info(f"Verification: {result[0]} rows in patient_allergy_reactions table")
    else:
        logger.warning("No reactions to load to patient_allergy_reactions table")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    load_patient_allergies_to_postgres()
