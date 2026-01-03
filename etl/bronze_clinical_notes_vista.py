# ---------------------------------------------------------------------
# bronze_clinical_notes_vista.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Clinical Notes from CDWWork (VistA).
#  - Extract 2 tables:
#    1. Dim.TIUDocumentDefinition → bronze/cdwwork/tiu_document_definition_dim
#    2. TIU.TIUDocument_8925 + TIU.TIUDocumentText → bronze/cdwwork/tiu_clinical_notes (with JOINs)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_clinical_notes_vista
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from sqlalchemy import create_engine
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_tiu_document_definition_dim():
    """Extract Dim.TIUDocumentDefinition to Bronze layer."""
    logger.info("Starting Bronze extraction: Dim.TIUDocumentDefinition")

    minio_client = MinIOClient()

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

    # Extract query
    query = """
    SELECT
        DocumentDefinitionSID,
        TIUDocumentTitle,
        DocumentClass,
        VHAEnterpriseStandardTitle,
        IsActive,
        Sta3n,
        TIUDocumentDefinitionIEN
    FROM Dim.TIUDocumentDefinition
    WHERE IsActive = 1
    ORDER BY DocumentClass, TIUDocumentTitle
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} TIU document type definitions from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="tiu_document_definition_dim",
        filename="tiu_document_definition_dim_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"Bronze layer written to MinIO: {object_key}")
    return len(df)


def extract_tiu_clinical_notes():
    """Extract TIU.TIUDocument_8925 with TIUDocumentText and JOINs to Bronze layer."""
    logger.info("Starting Bronze extraction: TIU.TIUDocument_8925 + TIU.TIUDocumentText")

    minio_client = MinIOClient()

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

    # Extract query with JOINs to get patient info, note definitions, authors, and text
    query = """
    SELECT
        doc.TIUDocumentSID,
        doc.PatientSID,
        doc.DocumentDefinitionSID,
        doc.ReferenceDateTime,
        doc.EntryDateTime,
        doc.Status,
        doc.AuthorSID,
        doc.CosignerSID,
        doc.VisitSID,
        doc.Sta3n,
        doc.TIUDocumentIEN,
        doc.CreatedDateTimeUTC,
        doc.UpdatedDateTimeUTC,
        -- Patient info
        p.PatientICN,
        p.PatientName,
        -- Document type info
        def.TIUDocumentTitle,
        def.DocumentClass,
        def.VHAEnterpriseStandardTitle,
        -- Author info
        author.StaffName AS AuthorName,
        -- Cosigner info (if exists)
        cosigner.StaffName AS CosignerName,
        -- Note text
        txt.DocumentText,
        txt.TextLength
    FROM TIU.TIUDocument_8925 doc
    LEFT JOIN SPatient.SPatient p ON doc.PatientSID = p.PatientSID
    LEFT JOIN Dim.TIUDocumentDefinition def ON doc.DocumentDefinitionSID = def.DocumentDefinitionSID
    LEFT JOIN SStaff.SStaff author ON doc.AuthorSID = author.StaffSID
    LEFT JOIN SStaff.SStaff cosigner ON doc.CosignerSID = cosigner.StaffSID
    LEFT JOIN TIU.TIUDocumentText txt ON doc.TIUDocumentSID = txt.TIUDocumentSID
    WHERE doc.Status = 'COMPLETED'
    ORDER BY doc.ReferenceDateTime DESC, doc.PatientSID, doc.TIUDocumentSID
    """

    # Read data using SQLAlchemy connection
    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    logger.info(f"Extracted {len(df)} clinical notes from CDWWork")

    # Add metadata columns
    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    # Build Bronze path
    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="tiu_clinical_notes",
        filename="tiu_clinical_notes_raw.parquet"
    )

    # Write to MinIO
    minio_client.write_parquet(df, object_key)

    logger.info(f"Bronze layer written to MinIO: {object_key}")
    return len(df)


def main():
    """Execute Bronze ETL for Clinical Notes (VistA)."""
    logger.info("=" * 70)
    logger.info("BRONZE ETL: Clinical Notes (VistA TIU)")
    logger.info("=" * 70)

    try:
        # Extract Dim.TIUDocumentDefinition
        def_count = extract_tiu_document_definition_dim()
        logger.info(f"✅ TIU Document Type Definitions extracted: {def_count}")

        # Extract TIU.TIUDocument_8925 + TIU.TIUDocumentText
        note_count = extract_tiu_clinical_notes()
        logger.info(f"✅ Clinical Notes extracted: {note_count}")

        logger.info("=" * 70)
        logger.info("BRONZE ETL COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Bronze ETL failed: {e}")
        raise


if __name__ == "__main__":
    main()
