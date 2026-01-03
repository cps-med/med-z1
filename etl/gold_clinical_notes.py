# ---------------------------------------------------------------------
# gold_clinical_notes.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver clinical notes data
#  - Read Silver: tiu_clinical_notes.parquet and tiu_document_definition_dim.parquet
#  - Add patient identity lookup (PatientSID → PatientICN → PatientKey)
#  - Enrich with facility/location information
#  - Add derived fields (DaysSinceNote, NoteAgeCategory)
#  - Create patient-centric denormalized view
#  - Save to med-z1/gold/clinical_notes as clinical_notes_final.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_clinical_notes
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def load_patient_icn_lookup():
    """
    Load PatientSID to PatientICN lookup from CDWWork.
    Returns a polars DataFrame with PatientSID to PatientICN mapping.
    """
    logger.info("Loading PatientSID to PatientICN lookup from CDWWork")

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    query = """
    SELECT
        PatientSID,
        PatientICN
    FROM SPatient.SPatient
    WHERE PatientICN IS NOT NULL
    """

    with engine.connect() as conn:
        patient_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(patient_df)} patient ICN mappings")
    return patient_df


def load_sta3n_lookup():
    """
    Load Sta3n lookup table from CDWWork.
    Returns a polars DataFrame with Sta3n code to name mapping.
    """
    logger.info("Loading Sta3n lookup table from CDWWork")

    # Create SQLAlchemy connection string
    conn_str = (
        f"mssql+pyodbc://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}?"
        f"driver={CDWWORK_DB_CONFIG['driver']}&"
        f"TrustServerCertificate=yes"
    )

    engine = create_engine(conn_str)

    query = """
    SELECT
        Sta3n,
        Sta3nName
    FROM Dim.Sta3n
    WHERE Active = 'Y'
    """

    with engine.connect() as conn:
        sta3n_df = pl.read_database(query, connection=conn)

    logger.info(f"Loaded {len(sta3n_df)} active stations for lookup")
    return sta3n_df


def transform_clinical_notes_gold():
    """Transform Silver clinical notes data to Gold layer in MinIO."""

    logger.info("=" * 70)
    logger.info("Starting Gold clinical notes transformation")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver Parquet files
    # ==================================================================
    logger.info("Step 1: Loading Silver Parquet files...")

    # Read clinical notes
    notes_path = build_silver_path("tiu_clinical_notes", "tiu_clinical_notes.parquet")
    df = minio_client.read_parquet(notes_path)
    logger.info(f"  - Loaded {len(df)} clinical notes from Silver layer")

    # Read document definitions (for reference, but already joined in Silver)
    doc_def_path = build_silver_path("tiu_document_definition_dim", "tiu_document_definition_dim.parquet")
    df_doc_def = minio_client.read_parquet(doc_def_path)
    logger.info(f"  - Loaded {len(df_doc_def)} document definitions from Silver layer")

    # ==================================================================
    # Step 2: Load patient identity lookup
    # ==================================================================
    logger.info("Step 2: Loading patient identity lookup...")

    patient_lookup = load_patient_icn_lookup()

    # Join to get PatientICN (should already be in Silver, but verify)
    if "PatientICN" not in df.columns or df.filter(pl.col("PatientICN").is_null()).height > 0:
        logger.warning("PatientICN missing or NULL for some records - adding from lookup")
        df = df.join(
            patient_lookup.select([
                pl.col("PatientSID"),
                pl.col("PatientICN").alias("PatientICN_lookup")
            ]),
            on="PatientSID",
            how="left"
        )

        # Use lookup value if original is NULL
        df = df.with_columns([
            pl.when(pl.col("PatientICN").is_null())
                .then(pl.col("PatientICN_lookup"))
                .otherwise(pl.col("PatientICN"))
                .alias("PatientICN")
        ]).drop("PatientICN_lookup")

    # Create PatientKey (same as ICN for Phase 1)
    df = df.with_columns([
        pl.col("PatientICN").alias("patient_key")
    ])

    logger.info(f"  - Patient identity resolution complete")

    # ==================================================================
    # Step 3: Load facility lookup
    # ==================================================================
    logger.info("Step 3: Loading facility lookup...")

    sta3n_lookup = load_sta3n_lookup()

    df = df.join(
        sta3n_lookup.select([
            pl.col("Sta3n").cast(pl.Int32),
            pl.col("Sta3nName").alias("facility_name")
        ]),
        on="Sta3n",
        how="left"
    )

    # ==================================================================
    # Step 4: Standardize column names and add derived fields
    # ==================================================================
    logger.info("Step 4: Standardizing column names and adding derived fields...")

    # Parse dates for calculation
    df = df.with_columns([
        pl.col("ReferenceDateTime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias("reference_datetime_parsed"),
    ])

    # Add derived fields
    # Use timezone-naive datetime for compatibility with parsed datetime columns
    now = datetime.now()
    df = df.with_columns([
        # Primary IDs
        pl.col("TIUDocumentSID").alias("tiu_document_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("patient_key").alias("patient_key"),
        pl.col("PatientICN").alias("patient_icn"),
        pl.col("PatientName").alias("patient_name"),

        # Document identifiers
        pl.col("DocumentDefinitionSID").alias("document_definition_sid"),
        pl.col("TIUDocumentTitle").alias("document_title"),
        pl.col("DocumentClass").alias("document_class"),
        pl.col("VHAEnterpriseStandardTitle").alias("vha_standard_title"),
        pl.col("Status").alias("status"),

        # Dates
        pl.col("reference_datetime_parsed").alias("reference_datetime"),
        pl.col("EntryDateTime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").alias("entry_datetime"),

        # Calculate days since note
        ((pl.lit(now) - pl.col("reference_datetime_parsed")).dt.total_days()).alias("days_since_note"),

        # Author information
        pl.col("AuthorSID").alias("author_sid"),
        pl.col("AuthorName").alias("author_name"),
        pl.col("CosignerSID").alias("cosigner_sid"),
        pl.col("CosignerName").alias("cosigner_name"),

        # Visit and location
        pl.col("VisitSID").alias("visit_sid"),
        pl.col("Sta3n").cast(pl.Utf8).alias("sta3n"),
        pl.col("facility_name").alias("facility_name"),

        # Note content
        pl.col("DocumentText").alias("document_text"),
        pl.col("TextLength").alias("text_length"),
        pl.col("TextPreview").alias("text_preview"),

        # Source identifiers
        pl.col("TIUDocumentIEN").alias("tiu_document_ien"),
        pl.lit("CDWWork").alias("source_system"),
        pl.lit(now).alias("last_updated"),
    ])

    # Add note age category
    df = df.with_columns([
        pl.when(pl.col("days_since_note") <= 30)
            .then(pl.lit("<30 days"))
            .when(pl.col("days_since_note") <= 90)
            .then(pl.lit("30-90 days"))
            .when(pl.col("days_since_note") <= 180)
            .then(pl.lit("90-180 days"))
            .otherwise(pl.lit(">180 days"))
            .alias("note_age_category")
    ])

    # ==================================================================
    # Step 5: Select final columns for Gold layer
    # ==================================================================
    logger.info("Step 5: Selecting final columns for Gold layer...")

    df = df.select([
        # Primary identifiers
        "tiu_document_sid",
        "patient_sid",
        "patient_icn",
        "patient_key",
        "patient_name",

        # Document identifiers
        "document_definition_sid",
        "document_title",
        "document_class",
        "vha_standard_title",
        "status",

        # Dates
        "reference_datetime",
        "entry_datetime",
        "days_since_note",
        "note_age_category",

        # Author information
        "author_sid",
        "author_name",
        "cosigner_sid",
        "cosigner_name",

        # Visit and location
        "visit_sid",
        "sta3n",
        "facility_name",

        # Note content
        "document_text",
        "text_length",
        "text_preview",

        # Source identifiers
        "tiu_document_ien",
        "source_system",
        "last_updated",
    ])

    # ==================================================================
    # Step 6: Write to Gold layer
    # ==================================================================
    logger.info("Step 6: Writing to Gold layer...")

    gold_path = build_gold_path("clinical_notes", "clinical_notes_final.parquet")
    minio_client.write_parquet(df, gold_path)

    logger.info(f"  - Written {len(df)} clinical notes to Gold layer")
    logger.info(f"  - Gold layer path: {gold_path}")

    # ==================================================================
    # Step 7: Summary statistics
    # ==================================================================
    logger.info("Step 7: Summary statistics...")

    # Document class distribution
    class_dist = df.group_by("document_class").agg(pl.len()).sort("document_class")
    logger.info(f"  - Document class distribution:")
    for row in class_dist.iter_rows():
        logger.info(f"    {row[0]}: {row[1]}")

    # Note age distribution
    age_dist = df.group_by("note_age_category").agg(pl.len()).sort("note_age_category")
    logger.info(f"  - Note age distribution:")
    for row in age_dist.iter_rows():
        logger.info(f"    {row[0]}: {row[1]}")

    logger.info("=" * 70)
    logger.info("Gold transformation complete")
    logger.info("=" * 70)

    return len(df)


def main():
    """Execute Gold ETL for Clinical Notes."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )

    try:
        record_count = transform_clinical_notes_gold()
        logger.info(f"✅ Gold ETL complete: {record_count} clinical notes")
    except Exception as e:
        logger.error(f"❌ Gold ETL failed: {e}")
        raise


if __name__ == "__main__":
    main()
