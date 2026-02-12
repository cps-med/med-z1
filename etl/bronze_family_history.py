# ---------------------------------------------------------------------
# bronze_family_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Bronze version of Family History data from:
#  - CDWWork (VistA-style):
#    1. Dim.FamilyRelationship
#    2. Dim.FamilyCondition
#    3. Outpat.FamilyHistory
#  - CDWWork2 (Cerner-style):
#    4. NDimMill.CodeValue (family-history code sets only)
#    5. EncMill.FamilyHistory
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.bronze_family_history
# ---------------------------------------------------------------------

import logging
from datetime import datetime, timezone

import polars as pl
from sqlalchemy import create_engine

from config import CDWWORK_DB_CONFIG, CDWWORK2_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _build_engine(db_config: dict):
    conn_str = (
        f"mssql+pyodbc://{db_config['user']}:"
        f"{db_config['password']}@"
        f"{db_config['server']}/"
        f"{db_config['name']}?"
        f"driver={db_config['driver']}&"
        f"TrustServerCertificate=yes"
    )
    return create_engine(conn_str)


def extract_family_relationship_dim():
    """Extract CDWWork Dim.FamilyRelationship."""
    logger.info("Starting Bronze extraction: Dim.FamilyRelationship")
    minio_client = MinIOClient()
    engine = _build_engine(CDWWORK_DB_CONFIG)

    query = """
    SELECT
        FamilyRelationshipSID,
        RelationshipCode,
        RelationshipName,
        Degree,
        IsActive,
        CreatedDateTime
    FROM Dim.FamilyRelationship
    ORDER BY FamilyRelationshipSID
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="family_relationship_dim",
        filename="family_relationship_dim_raw.parquet",
    )
    minio_client.write_parquet(df, object_key)
    logger.info(f"Extracted {len(df)} relationship rows")
    return df


def extract_family_condition_dim():
    """Extract CDWWork Dim.FamilyCondition."""
    logger.info("Starting Bronze extraction: Dim.FamilyCondition")
    minio_client = MinIOClient()
    engine = _build_engine(CDWWORK_DB_CONFIG)

    query = """
    SELECT
        FamilyConditionSID,
        ConditionCode,
        ConditionName,
        SNOMEDCode,
        ICD10Code,
        ConditionCategory,
        HereditaryRiskFlag,
        IsActive,
        CreatedDateTime
    FROM Dim.FamilyCondition
    ORDER BY FamilyConditionSID
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="family_condition_dim",
        filename="family_condition_dim_raw.parquet",
    )
    minio_client.write_parquet(df, object_key)
    logger.info(f"Extracted {len(df)} condition rows")
    return df


def extract_outpat_family_history():
    """Extract CDWWork Outpat.FamilyHistory fact rows."""
    logger.info("Starting Bronze extraction: Outpat.FamilyHistory")
    minio_client = MinIOClient()
    engine = _build_engine(CDWWORK_DB_CONFIG)

    query = """
    SELECT
        FamilyHistorySID,
        PatientSID,
        PatientICN,
        Sta3n,
        FamilyRelationshipSID,
        FamilyConditionSID,
        FamilyMemberGender,
        OnsetAgeYears,
        DeceasedFlag,
        ClinicalStatus,
        RecordedDateTime,
        EnteredDateTime,
        ProviderSID,
        LocationSID,
        CommentText,
        IsActive,
        CreatedDateTime
    FROM Outpat.FamilyHistory
    ORDER BY FamilyHistorySID
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    df = df.with_columns([
        pl.lit("CDWWork").alias("SourceSystem"),
        pl.lit("VistA").alias("SourceEHR"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    object_key = build_bronze_path(
        source_system="cdwwork",
        domain="outpat_family_history",
        filename="outpat_family_history_raw.parquet",
    )
    minio_client.write_parquet(df, object_key)
    logger.info(f"Extracted {len(df)} VistA family-history rows")
    return df


def extract_family_codevalue():
    """Extract CDWWork2 NDimMill.CodeValue for family-history code sets."""
    logger.info("Starting Bronze extraction: NDimMill.CodeValue (family-history subsets)")
    minio_client = MinIOClient()
    engine = _build_engine(CDWWORK2_DB_CONFIG)

    query = """
    SELECT
        CodeValueSID,
        CodeSet,
        Code,
        DisplayText,
        Description,
        IsActive
    FROM NDimMill.CodeValue
    WHERE CodeSet IN ('FAMILY_RELATIONSHIP', 'FAMILY_HISTORY_CONDITION', 'FAMILY_HISTORY_STATUS')
    ORDER BY CodeSet, CodeValueSID
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="family_history_codevalue",
        filename="family_history_codevalue_raw.parquet",
    )
    minio_client.write_parquet(df, object_key)
    logger.info(f"Extracted {len(df)} Cerner code-value rows")
    return df


def extract_encmill_family_history():
    """Extract CDWWork2 EncMill.FamilyHistory fact rows."""
    logger.info("Starting Bronze extraction: EncMill.FamilyHistory")
    minio_client = MinIOClient()
    engine = _build_engine(CDWWORK2_DB_CONFIG)

    query = """
    SELECT
        FamilyHistorySID,
        EncounterSID,
        PersonSID,
        PatientICN,
        Sta3n,
        RelationshipCodeSID,
        ConditionCodeSID,
        StatusCodeSID,
        FamilyMemberName,
        FamilyMemberAge,
        OnsetAgeYears,
        NotedDateTime,
        DocumentedBy,
        CommentText,
        IsActive,
        CreatedDateTime
    FROM EncMill.FamilyHistory
    ORDER BY FamilyHistorySID
    """

    with engine.connect() as conn:
        df = pl.read_database(query, connection=conn)

    df = df.with_columns([
        pl.lit("CDWWork2").alias("SourceSystem"),
        pl.lit("Cerner").alias("SourceEHR"),
        pl.lit(datetime.now(timezone.utc)).alias("LoadDateTime"),
    ])

    object_key = build_bronze_path(
        source_system="cdwwork2",
        domain="encmill_family_history",
        filename="encmill_family_history_raw.parquet",
    )
    minio_client.write_parquet(df, object_key)
    logger.info(f"Extracted {len(df)} Cerner family-history rows")
    return df


def main():
    logger.info("=" * 70)
    logger.info("BRONZE ETL: Family History")
    logger.info("=" * 70)

    try:
        df_rel = extract_family_relationship_dim()
        df_cond = extract_family_condition_dim()
        df_vista = extract_outpat_family_history()
        df_code = extract_family_codevalue()
        df_cerner = extract_encmill_family_history()

        logger.info("=" * 70)
        logger.info("Bronze extraction complete: Family History")
        logger.info("=" * 70)
        logger.info(f"CDWWork relationship dim: {len(df_rel)}")
        logger.info(f"CDWWork condition dim: {len(df_cond)}")
        logger.info(f"CDWWork Outpat.FamilyHistory: {len(df_vista)}")
        logger.info(f"CDWWork2 family code values: {len(df_code)}")
        logger.info(f"CDWWork2 EncMill.FamilyHistory: {len(df_cerner)}")
    except Exception as exc:
        logger.error(f"Bronze Family History extraction failed: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

