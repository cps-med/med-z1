# ---------------------------------------------------------------------
# silver_family_history.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Silver version from Bronze Family History data.
#  - Harmonize CDWWork (VistA patient-centric) and CDWWork2 (Cerner encounter-centric)
#  - Resolve relationship/condition/status display values
#  - Standardize status/flags and source lineage
#  - Deduplicate by patient + relationship + condition + recorded date + source
#  - Save to silver/family_history/family_history_harmonized.parquet
# ---------------------------------------------------------------------

import logging
from datetime import datetime, timezone

import polars as pl

from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def _bool_from_yn(expr: pl.Expr) -> pl.Expr:
    return (
        pl.when(expr == "Y").then(pl.lit(True))
        .when(expr == "N").then(pl.lit(False))
        .otherwise(None)
    )


def transform_family_history_silver():
    logger.info("=" * 70)
    logger.info("Starting Silver Family History transformation")
    logger.info("=" * 70)

    minio_client = MinIOClient()

    # ------------------------------------------------------------------
    # Step 1: Load Bronze datasets
    # ------------------------------------------------------------------
    logger.info("Step 1: Loading Bronze datasets...")

    rel_path = build_bronze_path("cdwwork", "family_relationship_dim", "family_relationship_dim_raw.parquet")
    cond_path = build_bronze_path("cdwwork", "family_condition_dim", "family_condition_dim_raw.parquet")
    vista_path = build_bronze_path("cdwwork", "outpat_family_history", "outpat_family_history_raw.parquet")
    codevalue_path = build_bronze_path("cdwwork2", "family_history_codevalue", "family_history_codevalue_raw.parquet")
    cerner_path = build_bronze_path("cdwwork2", "encmill_family_history", "encmill_family_history_raw.parquet")

    df_rel = minio_client.read_parquet(rel_path)
    df_cond = minio_client.read_parquet(cond_path)
    df_vista = minio_client.read_parquet(vista_path)
    df_codevalue = minio_client.read_parquet(codevalue_path)
    df_cerner = minio_client.read_parquet(cerner_path)

    logger.info(f"  - relationship dim: {len(df_rel)}")
    logger.info(f"  - condition dim: {len(df_cond)}")
    logger.info(f"  - VistA facts: {len(df_vista)}")
    logger.info(f"  - Cerner code values: {len(df_codevalue)}")
    logger.info(f"  - Cerner facts: {len(df_cerner)}")

    # ------------------------------------------------------------------
    # Step 2: Harmonize VistA dataset
    # ------------------------------------------------------------------
    logger.info("Step 2: Harmonizing VistA family-history...")

    df_vista_harmonized = (
        df_vista
        .join(
            df_rel.select([
                "FamilyRelationshipSID",
                "RelationshipCode",
                "RelationshipName",
                "Degree",
            ]),
            on="FamilyRelationshipSID",
            how="left",
        )
        .join(
            df_cond.select([
                "FamilyConditionSID",
                "ConditionCode",
                "ConditionName",
                "SNOMEDCode",
                "ICD10Code",
                "ConditionCategory",
                "HereditaryRiskFlag",
            ]),
            on="FamilyConditionSID",
            how="left",
        )
        .select([
            pl.lit("CDWWork").alias("source_system"),
            pl.lit("VistA").alias("source_ehr"),
            pl.col("FamilyHistorySID").cast(pl.Utf8).alias("record_id"),
            pl.col("PatientSID").alias("patient_sid"),
            pl.col("PatientICN").alias("patient_icn"),
            pl.col("Sta3n").cast(pl.Utf8).alias("facility_id"),
            pl.lit(None).cast(pl.Int64).alias("encounter_sid"),
            pl.col("RelationshipCode").alias("relationship_code"),
            pl.col("RelationshipName").alias("relationship_name"),
            pl.col("Degree").alias("relationship_degree"),
            pl.col("ConditionCode").alias("condition_code"),
            pl.col("ConditionName").alias("condition_name"),
            pl.col("SNOMEDCode").alias("snomed_code"),
            pl.col("ICD10Code").alias("icd10_code"),
            pl.col("ConditionCategory").alias("condition_category"),
            _bool_from_yn(pl.col("HereditaryRiskFlag")).alias("hereditary_risk_flag"),
            pl.col("ClinicalStatus").str.to_uppercase().alias("clinical_status"),
            pl.col("FamilyMemberGender").alias("family_member_gender"),
            pl.lit(None).cast(pl.Int64).alias("family_member_age"),
            _bool_from_yn(pl.col("DeceasedFlag")).alias("family_member_deceased"),
            pl.col("OnsetAgeYears").alias("onset_age_years"),
            pl.col("RecordedDateTime").cast(pl.Datetime).alias("recorded_datetime"),
            pl.col("EnteredDateTime").cast(pl.Datetime).alias("entered_datetime"),
            pl.col("ProviderSID").alias("provider_id"),
            pl.lit(None).cast(pl.Utf8).alias("provider_name"),
            pl.col("LocationSID").alias("location_id"),
            pl.col("CommentText").alias("comment_text"),
            _bool_from_yn(pl.col("IsActive")).alias("is_active"),
        ])
    )

    # ------------------------------------------------------------------
    # Step 3: Harmonize Cerner dataset
    # ------------------------------------------------------------------
    logger.info("Step 3: Harmonizing Cerner family-history...")

    df_rel_code = (
        df_codevalue
        .filter(pl.col("CodeSet") == "FAMILY_RELATIONSHIP")
        .select([
            pl.col("CodeValueSID").alias("RelationshipCodeSID"),
            pl.col("Code").alias("relationship_code"),
            pl.col("DisplayText").alias("relationship_name"),
        ])
    )
    df_cond_code = (
        df_codevalue
        .filter(pl.col("CodeSet") == "FAMILY_HISTORY_CONDITION")
        .select([
            pl.col("CodeValueSID").alias("ConditionCodeSID"),
            pl.col("Code").alias("condition_code"),
            pl.col("DisplayText").alias("condition_name"),
        ])
    )
    df_status_code = (
        df_codevalue
        .filter(pl.col("CodeSet") == "FAMILY_HISTORY_STATUS")
        .select([
            pl.col("CodeValueSID").alias("StatusCodeSID"),
            pl.col("Code").alias("clinical_status"),
        ])
    )

    df_cerner_harmonized = (
        df_cerner
        .join(df_rel_code, on="RelationshipCodeSID", how="left")
        .join(df_cond_code, on="ConditionCodeSID", how="left")
        .join(df_status_code, on="StatusCodeSID", how="left")
        .select([
            pl.lit("CDWWork2").alias("source_system"),
            pl.lit("Cerner").alias("source_ehr"),
            pl.col("FamilyHistorySID").cast(pl.Utf8).alias("record_id"),
            pl.col("PersonSID").alias("patient_sid"),
            pl.col("PatientICN").alias("patient_icn"),
            pl.col("Sta3n").cast(pl.Utf8).alias("facility_id"),
            pl.col("EncounterSID").alias("encounter_sid"),
            pl.col("relationship_code"),
            pl.col("relationship_name"),
            pl.lit(None).cast(pl.Utf8).alias("relationship_degree"),
            pl.col("condition_code"),
            pl.col("condition_name"),
            pl.lit(None).cast(pl.Utf8).alias("snomed_code"),
            pl.lit(None).cast(pl.Utf8).alias("icd10_code"),
            pl.lit(None).cast(pl.Utf8).alias("condition_category"),
            pl.lit(None).cast(pl.Boolean).alias("hereditary_risk_flag"),
            pl.col("clinical_status").str.to_uppercase(),
            pl.lit(None).cast(pl.Utf8).alias("family_member_gender"),
            pl.col("FamilyMemberAge").alias("family_member_age"),
            pl.lit(None).cast(pl.Boolean).alias("family_member_deceased"),
            pl.col("OnsetAgeYears").alias("onset_age_years"),
            pl.col("NotedDateTime").cast(pl.Datetime).alias("recorded_datetime"),
            pl.col("CreatedDateTime").cast(pl.Datetime).alias("entered_datetime"),
            pl.lit(None).cast(pl.Int64).alias("provider_id"),
            pl.col("DocumentedBy").alias("provider_name"),
            pl.lit(None).cast(pl.Int64).alias("location_id"),
            pl.col("CommentText").alias("comment_text"),
            pl.col("IsActive").cast(pl.Boolean).alias("is_active"),
        ])
    )

    # ------------------------------------------------------------------
    # Step 4: Union and dedup
    # ------------------------------------------------------------------
    logger.info("Step 4: Combining and deduplicating...")

    df_combined = pl.concat([df_vista_harmonized, df_cerner_harmonized], how="vertical")

    # Dedup key anchored on patient + relationship + condition + recorded date + source.
    # Keeps both systems unless exact duplicate exists within same source.
    df_silver = (
        df_combined
        .with_columns([
            pl.col("recorded_datetime").cast(pl.Date).alias("recorded_date"),
            pl.col("clinical_status").fill_null("UNKNOWN"),
            pl.col("is_active").fill_null(True),
        ])
        .sort(["patient_icn", "recorded_datetime", "source_system"], descending=[False, True, False])
        .unique(
            subset=["patient_icn", "relationship_code", "condition_code", "recorded_date", "source_system"],
            keep="first",
            maintain_order=True,
        )
    )

    # ------------------------------------------------------------------
    # Step 5: Add metadata and write Silver output
    # ------------------------------------------------------------------
    logger.info("Step 5: Writing Silver output...")

    df_silver = df_silver.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("silver_load_datetime"),
        pl.lit("v1.0").alias("silver_schema_version"),
    ])

    silver_path = build_silver_path("family_history", "family_history_harmonized.parquet")
    minio_client.write_parquet(df_silver, silver_path)

    logger.info(
        f"Silver transformation complete: {len(df_silver)} records written to "
        f"s3://{minio_client.bucket_name}/{silver_path}"
    )

    by_source = df_silver.group_by("source_system").agg(pl.len().alias("count")).sort("source_system")
    for row in by_source.iter_rows(named=True):
        logger.info(f"  - {row['source_system']}: {row['count']} records")

    return df_silver


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    transform_family_history_silver()

