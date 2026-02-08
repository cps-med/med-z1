# ---------------------------------------------------------------------
# gold_problems.py
# ---------------------------------------------------------------------
# Create MinIO Parquet Gold version from Silver problems data
#  - Read Silver: problems_harmonized.parquet
#  - Calculate Charlson Comorbidity Index per patient
#  - Aggregate problem counts and chronic condition flags
#  - Create patient-level problem summary metrics
#  - Save to med-z1/gold/problems as:
#    - patient_problems.parquet (patient-level aggregations with Charlson Index)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.gold_problems
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path, build_gold_path

logger = logging.getLogger(__name__)


def calculate_charlson_index():
    """
    Calculate Charlson Comorbidity Index and patient-level problem aggregations.

    Charlson Index calculation:
    1. Join active problems with Charlson mappings
    2. Group by patient + condition (take max points if multiple ICD-10 codes map to same condition)
    3. Sum points across all conditions per patient

    Returns Gold DataFrame with patient-level aggregations.
    """

    logger.info("=" * 70)
    logger.info("Starting Gold Problems transformation (Charlson Index)")
    logger.info("=" * 70)

    # Initialize MinIO client
    minio_client = MinIOClient()

    # ==================================================================
    # Step 1: Load Silver Parquet file
    # ==================================================================
    logger.info("Step 1: Loading Silver Parquet file...")

    silver_path = build_silver_path("problems", "problems_harmonized.parquet")
    df_problems = minio_client.read_parquet(silver_path)
    logger.info(f"  - Loaded {len(df_problems)} problem records from Silver")

    # Load Bronze Charlson mapping for weight lookups
    charlson_path = build_bronze_path("cdwwork", "charlson_mapping", "charlson_mapping_raw.parquet")
    df_charlson_mapping = minio_client.read_parquet(charlson_path)
    logger.info(f"  - Loaded {len(df_charlson_mapping)} Charlson mappings from Bronze")

    # ==================================================================
    # Step 2: Calculate Charlson Index per patient
    # ==================================================================
    logger.info("Step 2: Calculating Charlson Comorbidity Index per patient...")

    # Filter to active problems only (Charlson Index only counts active diagnoses)
    df_active = df_problems.filter(pl.col("problem_status") == "Active")
    logger.info(f"  - Filtered to {len(df_active)} active problems")

    # Join active problems with Charlson mapping to get weights
    # Only join problems that have a Charlson condition mapping
    df_charlson_problems = df_active.filter(
        pl.col("icd10_charlson_condition").is_not_null()
    ).join(
        df_charlson_mapping.select([
            pl.col("ICD10Code").str.strip_chars().str.to_uppercase().alias("icd10_code"),
            pl.col("CharlsonCondition").alias("charlson_condition"),
            pl.col("CharlsonWeight").alias("charlson_weight")
        ]),
        on="icd10_code",
        how="inner"
    )
    logger.info(f"  - Found {len(df_charlson_problems)} active problems with Charlson mappings and weights")

    # Aggregate by patient + condition (max points if multiple ICD-10 codes map to same condition)
    # Example: E11.9 (uncomplicated diabetes) = 1 point, E11.22 (diabetes with CKD) = 2 points
    # If patient has both, we take the maximum (2 points) for "Diabetes" condition
    df_patient_conditions = (
        df_charlson_problems
        .group_by(["patient_icn", "charlson_condition"])
        .agg([
            pl.col("charlson_weight").max().alias("condition_points")
        ])
    )
    logger.info(f"  - Aggregated to {len(df_patient_conditions)} patient-condition pairs")

    # Sum points across all conditions per patient
    df_charlson_scores = (
        df_patient_conditions
        .group_by("patient_icn")
        .agg([
            pl.col("condition_points").sum().alias("charlson_index"),
            pl.col("charlson_condition").n_unique().alias("charlson_condition_count"),
        ])
    )
    logger.info(f"  - Calculated Charlson Index for {len(df_charlson_scores)} patients")

    # ==================================================================
    # Step 3: Calculate problem counts per patient
    # ==================================================================
    logger.info("Step 3: Calculating problem counts per patient...")

    df_problem_counts = (
        df_problems
        .group_by("patient_icn")
        .agg([
            pl.len().alias("total_problem_count"),
            pl.col("problem_status").filter(pl.col("problem_status") == "Active").count().alias("active_problem_count"),
            pl.col("problem_status").filter(pl.col("problem_status") == "Inactive").count().alias("inactive_problem_count"),
            pl.col("problem_status").filter(pl.col("problem_status") == "Resolved").count().alias("resolved_problem_count"),
            pl.col("chronic_condition").filter(pl.col("chronic_condition") == True).count().alias("chronic_problem_count"),
            pl.col("service_connected").filter(pl.col("service_connected") == True).count().alias("service_connected_count"),
        ])
    )
    logger.info(f"  - Calculated problem counts for {len(df_problem_counts)} patients")

    # ==================================================================
    # Step 4: Flag specific chronic conditions (for AI/ML and clinical decision support)
    # ==================================================================
    logger.info("Step 4: Flagging specific chronic conditions per patient...")

    df_chronic_flags = (
        df_active
        .group_by("patient_icn")
        .agg([
            # Cardiovascular
            pl.col("icd10_code").str.starts_with("I50").any().alias("has_chf"),  # Congestive Heart Failure
            pl.col("icd10_code").str.starts_with("I25").any().alias("has_cad"),  # Coronary Artery Disease
            pl.col("icd10_code").str.starts_with("I48").any().alias("has_afib"),  # Atrial Fibrillation
            pl.col("icd10_code").str.starts_with("I10").any().alias("has_hypertension"),  # Essential Hypertension

            # Respiratory
            pl.col("icd10_code").str.starts_with("J44").any().alias("has_copd"),  # COPD
            pl.col("icd10_code").str.starts_with("J45").any().alias("has_asthma"),  # Asthma

            # Endocrine/Metabolic
            pl.col("icd10_code").str.starts_with("E11").any().alias("has_diabetes"),  # Type 2 Diabetes
            pl.col("icd10_code").str.starts_with("E78").any().alias("has_hyperlipidemia"),  # Hyperlipidemia

            # Renal
            pl.col("icd10_code").str.starts_with("N18").any().alias("has_ckd"),  # Chronic Kidney Disease

            # Mental Health
            (pl.col("icd10_code").str.starts_with("F32") | pl.col("icd10_code").str.starts_with("F33")).any().alias("has_depression"),  # Depression
            pl.col("icd10_code").str.contains("F43\\.10").any().alias("has_ptsd"),  # PTSD
            pl.col("icd10_code").str.starts_with("F41").any().alias("has_anxiety"),  # Anxiety

            # Oncology
            (pl.col("icd10_code").str.starts_with("C") & ~pl.col("icd10_code").str.starts_with("C7")).any().alias("has_cancer"),  # Malignant neoplasms (exclude benign C7x)

            # Musculoskeletal
            pl.col("icd10_code").str.starts_with("M15").any().alias("has_osteoarthritis"),  # Osteoarthritis
            pl.col("icd10_code").str.starts_with("M54").any().alias("has_back_pain"),  # Back pain
        ])
    )
    logger.info(f"  - Created chronic condition flags for {len(df_chronic_flags)} patients")

    # ==================================================================
    # Step 5: Join all patient-level aggregations with original problems
    # ==================================================================
    logger.info("Step 5: Joining patient-level aggregations...")

    # Join Charlson scores
    df_gold = df_problems.join(
        df_charlson_scores,
        on="patient_icn",
        how="left"
    )

    # Join problem counts
    df_gold = df_gold.join(
        df_problem_counts,
        on="patient_icn",
        how="left"
    )

    # Join chronic flags
    df_gold = df_gold.join(
        df_chronic_flags,
        on="patient_icn",
        how="left"
    )

    # Fill nulls for patients without Charlson conditions or specific flags
    df_gold = df_gold.with_columns([
        pl.col("charlson_index").fill_null(0),
        pl.col("charlson_condition_count").fill_null(0),
        pl.col("total_problem_count").fill_null(0),
        pl.col("active_problem_count").fill_null(0),
        pl.col("inactive_problem_count").fill_null(0),
        pl.col("resolved_problem_count").fill_null(0),
        pl.col("chronic_problem_count").fill_null(0),
        pl.col("service_connected_count").fill_null(0),
        # Fill boolean flags with False
        pl.col("has_chf").fill_null(False),
        pl.col("has_cad").fill_null(False),
        pl.col("has_afib").fill_null(False),
        pl.col("has_hypertension").fill_null(False),
        pl.col("has_copd").fill_null(False),
        pl.col("has_asthma").fill_null(False),
        pl.col("has_diabetes").fill_null(False),
        pl.col("has_hyperlipidemia").fill_null(False),
        pl.col("has_ckd").fill_null(False),
        pl.col("has_depression").fill_null(False),
        pl.col("has_ptsd").fill_null(False),
        pl.col("has_anxiety").fill_null(False),
        pl.col("has_cancer").fill_null(False),
        pl.col("has_osteoarthritis").fill_null(False),
        pl.col("has_back_pain").fill_null(False),
    ])

    # ==================================================================
    # Step 6: Add Gold metadata
    # ==================================================================
    logger.info("Step 6: Adding Gold metadata...")

    df_gold = df_gold.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("gold_load_datetime"),
        pl.lit("v1.0").alias("gold_schema_version"),
    ])

    # ==================================================================
    # Step 7: Write to Gold layer
    # ==================================================================
    logger.info("Step 7: Writing to Gold layer...")

    gold_path = build_gold_path("problems", "patient_problems.parquet")
    minio_client.write_parquet(df_gold, gold_path)

    logger.info(
        f"Gold transformation complete: {len(df_gold)} problem records written to "
        f"s3://{minio_client.bucket_name}/{gold_path}"
    )

    # ==================================================================
    # Summary statistics
    # ==================================================================
    logger.info("=" * 70)
    logger.info("Gold Problems Transformation Summary")
    logger.info("=" * 70)

    # Charlson Index distribution
    logger.info("Charlson Index Distribution (unique patients):")
    unique_patients = df_gold.select([
        "patient_icn", "charlson_index", "has_chf", "has_diabetes", "has_copd",
        "has_ckd", "has_hypertension", "has_depression", "has_ptsd", "has_cancer"
    ]).unique()
    charlson_stats = unique_patients.select([
        pl.col("charlson_index").min().alias("min"),
        pl.col("charlson_index").max().alias("max"),
        pl.col("charlson_index").mean().alias("mean"),
        pl.col("charlson_index").median().alias("median"),
    ])
    for row in charlson_stats.iter_rows(named=True):
        logger.info(f"  - Min: {row['min']}, Max: {row['max']}, Mean: {row['mean']:.2f}, Median: {row['median']}")

    # Count patients by Charlson Index ranges
    charlson_ranges = unique_patients.with_columns([
        pl.when(pl.col("charlson_index") == 0).then(pl.lit("0 (No comorbidities)"))
          .when((pl.col("charlson_index") >= 1) & (pl.col("charlson_index") <= 2)).then(pl.lit("1-2 (Low)"))
          .when((pl.col("charlson_index") >= 3) & (pl.col("charlson_index") <= 4)).then(pl.lit("3-4 (Moderate)"))
          .when(pl.col("charlson_index") >= 5).then(pl.lit("5+ (High)"))
          .alias("charlson_range")
    ]).group_by("charlson_range").agg(
        pl.len().alias("patient_count")
    ).sort("charlson_range")

    logger.info("Patients by Charlson Index range:")
    for row in charlson_ranges.iter_rows(named=True):
        logger.info(f"  - {row['charlson_range']}: {row['patient_count']} patients")

    # Count patients with specific chronic conditions
    logger.info("Patients with specific chronic conditions:")
    condition_counts = unique_patients.select([
        pl.col("has_chf").sum().alias("CHF"),
        pl.col("has_diabetes").sum().alias("Diabetes"),
        pl.col("has_copd").sum().alias("COPD"),
        pl.col("has_ckd").sum().alias("CKD"),
        pl.col("has_hypertension").sum().alias("Hypertension"),
        pl.col("has_depression").sum().alias("Depression"),
        pl.col("has_ptsd").sum().alias("PTSD"),
        pl.col("has_cancer").sum().alias("Cancer"),
    ])
    for row in condition_counts.iter_rows(named=True):
        for condition, count in row.items():
            logger.info(f"  - {condition}: {count} patients")

    logger.info("=" * 70)

    return df_gold


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    calculate_charlson_index()
