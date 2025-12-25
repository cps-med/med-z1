"""
silver_patient_allergies.py

Create Silver layer patient allergies from Bronze layer data.
- Read from med-z1/bronze/cdwwork/allergen
- Read from med-z1/bronze/cdwwork/reaction
- Read from med-z1/bronze/cdwwork/allergy_severity
- Read from med-z1/bronze/cdwwork/patient_allergy
- Read from med-z1/bronze/cdwwork/patient_allergy_reaction
- Join and transform data
- Aggregate reactions per allergy
- Save to med-z1/silver/patient_allergies as patient_allergies_cleaned.parquet

To run this script from the project root folder:
  $ cd med-z1
  $ python -m etl.silver_patient_allergies
"""

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logger = logging.getLogger(__name__)


def transform_patient_allergies_silver():
    """Transform Bronze patient allergy data to Silver layer in MinIO."""

    logger.info("Starting Silver patient allergies transformation")

    # Initialize MinIO client
    minio_client = MinIOClient()

    # =========================================================================
    # Read Bronze Parquet files from MinIO
    # =========================================================================

    # Read Allergen dimension
    allergen_path = build_bronze_path("cdwwork", "allergen", "allergen_raw.parquet")
    df_allergen = minio_client.read_parquet(allergen_path)
    logger.info(f"Bronze allergen data read: {len(df_allergen)} records")

    # Read Reaction dimension
    reaction_path = build_bronze_path("cdwwork", "reaction", "reaction_raw.parquet")
    df_reaction = minio_client.read_parquet(reaction_path)
    logger.info(f"Bronze reaction data read: {len(df_reaction)} records")

    # Read AllergySeverity dimension
    severity_path = build_bronze_path("cdwwork", "allergy_severity", "allergy_severity_raw.parquet")
    df_severity = minio_client.read_parquet(severity_path)
    logger.info(f"Bronze allergy severity data read: {len(df_severity)} records")

    # Read PatientAllergy fact table
    patient_allergy_path = build_bronze_path("cdwwork", "patient_allergy", "patient_allergy_raw.parquet")
    df_patient_allergy = minio_client.read_parquet(patient_allergy_path)
    logger.info(f"Bronze patient allergy data read: {len(df_patient_allergy)} records")

    # Read PatientAllergyReaction bridge table
    allergy_reaction_path = build_bronze_path("cdwwork", "patient_allergy_reaction", "patient_allergy_reaction_raw.parquet")
    df_allergy_reaction = minio_client.read_parquet(allergy_reaction_path)
    logger.info(f"Bronze patient allergy reaction data read: {len(df_allergy_reaction)} records")

    # =========================================================================
    # Transform and clean dimension data
    # =========================================================================

    # Clean allergen dimension
    df_allergen = df_allergen.select([
        pl.col("AllergenSID").alias("allergen_sid"),
        pl.col("AllergenName").str.strip_chars().str.to_uppercase().alias("allergen_name"),
        pl.col("AllergenType").str.strip_chars().str.to_uppercase().alias("allergen_type"),
    ])

    # Clean reaction dimension
    df_reaction = df_reaction.select([
        pl.col("ReactionSID").alias("reaction_sid"),
        pl.col("ReactionName").str.strip_chars().str.to_uppercase().alias("reaction_name"),
    ])

    # Clean severity dimension
    df_severity = df_severity.select([
        pl.col("AllergySeveritySID").alias("severity_sid"),
        pl.col("SeverityName").str.strip_chars().str.to_uppercase().alias("severity_name"),
        pl.col("SeverityRank").alias("severity_rank"),
    ])

    # =========================================================================
    # Aggregate reactions per allergy
    # =========================================================================

    # Join allergy reactions with reaction names
    df_reactions_joined = df_allergy_reaction.join(
        df_reaction,
        left_on="ReactionSID",
        right_on="reaction_sid",
        how="left"
    )

    # Aggregate reactions per allergy (comma-separated)
    df_reactions_agg = (
        df_reactions_joined
        .group_by("PatientAllergySID")
        .agg([
            pl.col("reaction_name").str.join(", ").alias("reactions"),
            pl.col("reaction_name").count().alias("reaction_count"),
        ])
        .select([
            pl.col("PatientAllergySID").alias("patient_allergy_sid_react"),
            pl.col("reactions"),
            pl.col("reaction_count"),
        ])
    )
    logger.info(f"Aggregated reactions for {len(df_reactions_agg)} allergies")

    # =========================================================================
    # Transform patient allergy data and join with dimensions
    # =========================================================================

    # Clean and standardize patient allergy fields
    df = df_patient_allergy.with_columns([
        pl.col("PatientAllergySID").alias("patient_allergy_sid"),
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("AllergenSID").alias("allergen_sid"),
        pl.col("AllergySeveritySID").alias("severity_sid"),
        pl.col("LocalAllergenName").str.strip_chars().alias("allergen_local"),
        pl.col("OriginationDateTime").alias("origination_datetime"),
        pl.col("ObservedDateTime").alias("observed_datetime"),
        pl.col("OriginatingSiteSta3n").cast(pl.Utf8).alias("originating_site_sta3n"),
        pl.col("Comment").str.strip_chars().alias("comment"),
        pl.col("HistoricalOrObserved").str.strip_chars().str.to_uppercase().alias("historical_or_observed"),
        pl.col("VerificationStatus").str.strip_chars().str.to_uppercase().alias("verification_status"),
        pl.col("SourceSystem").alias("source_system"),
    ])

    # Join with allergen dimension to get standardized allergen name and type
    df = df.join(
        df_allergen,
        on="allergen_sid",
        how="left"
    )
    logger.info("Joined allergen dimension to patient allergies")

    # Join with severity dimension to get severity name and rank
    df = df.join(
        df_severity,
        on="severity_sid",
        how="left"
    )
    logger.info("Joined severity dimension to patient allergies")

    # Join with aggregated reactions
    df = df.join(
        df_reactions_agg,
        left_on="patient_allergy_sid",
        right_on="patient_allergy_sid_react",
        how="left"
    )
    logger.info("Joined aggregated reactions to patient allergies")

    # =========================================================================
    # Add derived fields
    # =========================================================================

    df = df.with_columns([
        # is_drug_allergy flag (TRUE if allergen_type = 'DRUG')
        (pl.col("allergen_type") == "DRUG").alias("is_drug_allergy"),

        # last_updated timestamp
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # =========================================================================
    # Select final Silver schema columns
    # =========================================================================

    df_silver = df.select([
        "patient_allergy_sid",
        "patient_sid",
        "allergen_sid",
        "allergen_local",
        "allergen_name",
        "allergen_type",
        "severity_sid",
        "severity_name",
        "severity_rank",
        "reactions",
        "reaction_count",
        "origination_datetime",
        "observed_datetime",
        "historical_or_observed",
        "originating_site_sta3n",
        "comment",
        "verification_status",
        "is_drug_allergy",
        "source_system",
        "last_updated",
    ])

    logger.info(f"Silver transformation complete: {len(df_silver)} allergy records")

    # =========================================================================
    # Write to Silver layer in MinIO
    # =========================================================================

    silver_path = build_silver_path("patient_allergies", "patient_allergies_cleaned.parquet")
    minio_client.write_parquet(df_silver, silver_path)

    logger.info(
        f"Silver patient allergies written to s3://{minio_client.bucket_name}/{silver_path}"
    )
    logger.info(f"Total allergies: {len(df_silver)}")
    logger.info(f"Drug allergies: {df_silver.filter(pl.col('is_drug_allergy') == True).shape[0]}")
    logger.info(f"Food allergies: {df_silver.filter(pl.col('allergen_type') == 'FOOD').shape[0]}")
    logger.info(f"Environmental allergies: {df_silver.filter(pl.col('allergen_type') == 'ENVIRONMENTAL').shape[0]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Starting Silver ETL: Patient Allergies")
    transform_patient_allergies_silver()
    logger.info("Silver ETL: Patient Allergies complete")
