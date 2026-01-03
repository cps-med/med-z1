# ---------------------------------------------------------------------
# load_clinical_notes.py
# ---------------------------------------------------------------------
# Load Gold clinical notes data into PostgreSQL serving database
#  - Read Gold: clinical_notes_final.parquet
#  - Transform to match PostgreSQL schema
#  - Load into patient_clinical_notes table
#  - Use truncate/load for now (upsert in future phases)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_clinical_notes
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

logger = logging.getLogger(__name__)


def load_clinical_notes_to_postgresql():
    """Load Gold clinical notes data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("Starting PostgreSQL load for clinical notes")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Gold clinical notes
    # ==================================================================
    logger.info("Step 1: Loading Gold clinical notes...")

    gold_path = build_gold_path("clinical_notes", "clinical_notes_final.parquet")
    df = minio_client.read_parquet(gold_path)
    logger.info(f"  - Loaded {len(df)} clinical notes from Gold layer")

    # ==================================================================
    # Step 2: Transform to match PostgreSQL schema
    # ==================================================================
    logger.info("Step 2: Transforming to match PostgreSQL schema...")

    # Select and rename columns to match patient_clinical_notes table schema
    # Note: patient_clinical_notes table has these columns:
    #   note_id (auto), patient_key, tiu_document_sid, document_definition_sid,
    #   document_title, document_class, vha_standard_title, status,
    #   reference_datetime, entry_datetime, days_since_note, note_age_category,
    #   author_sid, author_name, cosigner_sid, cosigner_name, visit_sid,
    #   sta3n, facility_name, document_text, text_length, text_preview,
    #   tiu_document_ien, source_system, last_updated
    df_pg = df.select([
        pl.col("patient_key"),
        pl.col("tiu_document_sid"),
        pl.col("document_definition_sid"),
        pl.col("document_title"),
        pl.col("document_class"),
        pl.col("vha_standard_title"),
        pl.col("status"),
        pl.col("reference_datetime"),
        pl.col("entry_datetime"),
        pl.col("days_since_note").cast(pl.Int32),
        pl.col("note_age_category"),
        pl.col("author_sid"),
        pl.col("author_name"),
        pl.col("cosigner_sid"),
        pl.col("cosigner_name"),
        pl.col("visit_sid"),
        pl.col("sta3n"),
        pl.col("facility_name"),
        pl.col("document_text"),
        pl.col("text_length").cast(pl.Int32),
        pl.col("text_preview"),
        pl.col("tiu_document_ien"),
        pl.col("source_system"),
    ])

    logger.info(f"  - Prepared {len(df_pg)} clinical notes for PostgreSQL")

    # ==================================================================
    # Step 3: Create PostgreSQL connection
    # ==================================================================
    logger.info("Step 3: Connecting to PostgreSQL...")

    # Create SQLAlchemy connection string
    conn_str = (
        f"postgresql://{POSTGRES_CONFIG['user']}:"
        f"{POSTGRES_CONFIG['password']}@"
        f"{POSTGRES_CONFIG['host']}:"
        f"{POSTGRES_CONFIG['port']}/"
        f"{POSTGRES_CONFIG['database']}"
    )

    engine = create_engine(conn_str)

    # ==================================================================
    # Step 4: Truncate existing data (for now)
    # ==================================================================
    logger.info("Step 4: Truncating existing patient_clinical_notes table...")

    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE clinical.patient_clinical_notes;"))
        conn.commit()

    logger.info("  - Table truncated")

    # ==================================================================
    # Step 5: Load data into PostgreSQL
    # ==================================================================
    logger.info("Step 5: Loading data into PostgreSQL...")

    # Convert Polars DataFrame to Pandas for SQLAlchemy compatibility
    df_pandas = df_pg.to_pandas()

    # Write to PostgreSQL
    df_pandas.to_sql(
        "patient_clinical_notes",
        engine,
        schema="clinical",
        if_exists="append",
        index=False,
        method="multi",  # Bulk insert for performance
        chunksize=1000
    )

    logger.info(f"  - Loaded {len(df_pandas)} clinical notes into patient_clinical_notes table")

    # ==================================================================
    # Step 6: Verify data
    # ==================================================================
    logger.info("Step 6: Verifying data...")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_clinical_notes;"))
        count = result.scalar()
        logger.info(f"  - Verified: {count} rows in patient_clinical_notes table")

        # Get sample data
        result = conn.execute(text("""
            SELECT patient_key, document_title, document_class, reference_datetime, text_length
            FROM clinical.patient_clinical_notes
            ORDER BY reference_datetime DESC
            LIMIT 5;
        """))
        logger.info(f"  - Sample data (most recent 5 notes):")
        for row in result:
            logger.info(f"    {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} chars")

        # Document class distribution
        result = conn.execute(text("""
            SELECT document_class, COUNT(*) as count
            FROM clinical.patient_clinical_notes
            GROUP BY document_class
            ORDER BY document_class;
        """))
        logger.info(f"  - Document class distribution:")
        for row in result:
            logger.info(f"    {row[0]}: {row[1]}")

        # Note age distribution
        result = conn.execute(text("""
            SELECT note_age_category, COUNT(*) as count
            FROM clinical.patient_clinical_notes
            GROUP BY note_age_category
            ORDER BY note_age_category;
        """))
        logger.info(f"  - Note age distribution:")
        for row in result:
            logger.info(f"    {row[0]}: {row[1]}")

    logger.info("=" * 70)
    logger.info("PostgreSQL load complete")
    logger.info("=" * 70)


def main():
    """Execute PostgreSQL load for Clinical Notes."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    try:
        load_clinical_notes_to_postgresql()
        logger.info("✅ PostgreSQL load complete")
    except Exception as e:
        logger.error(f"❌ PostgreSQL load failed: {e}")
        raise


if __name__ == "__main__":
    main()
