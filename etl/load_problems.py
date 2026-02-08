# ---------------------------------------------------------------------
# load_problems.py
# ---------------------------------------------------------------------
# Load Gold problems/diagnoses data into PostgreSQL serving database
#  - Read Gold: patient_problems.parquet
#  - Transform to match PostgreSQL schema
#  - Load into clinical.patient_problems table
#  - Truncate and reload (development pattern)
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.load_problems
# ---------------------------------------------------------------------

import polars as pl
import logging
from sqlalchemy import create_engine, text
from config import POSTGRES_CONFIG
from lake.minio_client import MinIOClient, build_gold_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_problems_to_postgresql():
    """Load Gold problems/diagnoses data into PostgreSQL serving database."""

    logger.info("=" * 70)
    logger.info("PostgreSQL Load: Problems/Diagnoses")
    logger.info("=" * 70)

    try:
        # Initialize MinIO client
        minio_client = MinIOClient()

        # ==================================================================
        # Step 1: Load Gold problems
        # ==================================================================
        logger.info("Step 1: Loading Gold problems...")

        gold_path = build_gold_path("problems", "patient_problems.parquet")
        df = minio_client.read_parquet(gold_path)
        logger.info(f"  - Loaded {len(df)} problem records from Gold layer")

        # ==================================================================
        # Step 2: Transform to match PostgreSQL schema
        # ==================================================================
        logger.info("Step 2: Transforming to match PostgreSQL schema...")

        # Select and rename columns to match patient_problems table schema
        # Note: PostgreSQL table has problem_id (auto) + all these columns
        df_pg = df.select([
            # Primary keys and identifiers
            pl.col("problem_id").alias("problem_sid"),  # Rename to match PostgreSQL schema
            pl.col("patient_sid"),
            pl.col("patient_icn"),
            pl.col("patient_icn").alias("patient_key"),  # Same as ICN

            # Problem identification
            pl.col("problem_number"),

            # Dual coding system
            pl.col("icd10_code"),
            pl.col("diagnosis_description").alias("icd10_description"),  # Use diagnosis_description as primary
            pl.col("icd10_category"),
            pl.col("snomed_code"),
            pl.col("snomed_description"),
            pl.col("diagnosis_description"),

            # Problem status and classification
            pl.col("problem_status"),
            pl.col("acute_condition"),
            pl.col("chronic_condition"),
            pl.col("service_connected"),

            # Temporal tracking
            pl.col("onset_date"),
            pl.col("recorded_date"),
            pl.col("last_modified_date"),
            pl.col("resolved_date"),
            pl.col("entered_datetime"),

            # Provider and location
            pl.col("provider_id"),
            pl.col("provider_name"),
            pl.col("clinic_location"),
            pl.col("facility_id"),

            # Entered by information
            pl.col("entered_by_name"),

            # Source system tracking
            pl.col("source_ehr"),
            pl.col("source_system"),

            # ICD-10 reference enrichment
            pl.col("icd10_chronic_flag"),
            pl.col("icd10_charlson_condition"),

            # Patient-level Charlson Index aggregations
            pl.col("charlson_index"),
            pl.col("charlson_condition_count"),

            # Patient-level problem count aggregations
            pl.col("total_problem_count"),
            pl.col("active_problem_count"),
            pl.col("inactive_problem_count"),
            pl.col("resolved_problem_count"),
            pl.col("chronic_problem_count"),
            pl.col("service_connected_count"),

            # Chronic condition flags (15 total)
            pl.col("has_chf"),
            pl.col("has_cad"),
            pl.col("has_afib"),
            pl.col("has_hypertension"),
            pl.col("has_copd"),
            pl.col("has_asthma"),
            pl.col("has_diabetes"),
            pl.col("has_hyperlipidemia"),
            pl.col("has_ckd"),
            pl.col("has_depression"),
            pl.col("has_ptsd"),
            pl.col("has_anxiety"),
            pl.col("has_cancer"),
            pl.col("has_osteoarthritis"),
            pl.col("has_back_pain"),

            # Metadata timestamps
            pl.col("silver_load_datetime"),
            pl.col("gold_load_datetime"),
        ])

        logger.info(f"  - Prepared {len(df_pg)} problem records for PostgreSQL")

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
        # Step 4: Truncate existing data (development pattern)
        # ==================================================================
        logger.info("Step 4: Truncating existing patient_problems table...")

        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE clinical.patient_problems;"))
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
            "patient_problems",
            engine,
            schema="clinical",
            if_exists="append",
            index=False,
            method="multi",  # Bulk insert for performance
            chunksize=1000
        )

        logger.info(f"  - Loaded {len(df_pandas)} problem records into patient_problems table")

        # ==================================================================
        # Step 6: Verify data
        # ==================================================================
        logger.info("Step 6: Verifying data...")

        with engine.connect() as conn:
            # Total count
            result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_problems;"))
            count = result.scalar()
            logger.info(f"  - Verified: {count} rows in patient_problems table")

            # Patient count
            result = conn.execute(text("SELECT COUNT(DISTINCT patient_key) FROM clinical.patient_problems;"))
            patient_count = result.scalar()
            logger.info(f"  - Patients: {patient_count}")

            # Problem status distribution
            result = conn.execute(text("""
                SELECT problem_status, COUNT(*) as count
                FROM clinical.patient_problems
                GROUP BY problem_status
                ORDER BY count DESC;
            """))
            logger.info("  - Problem status distribution:")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} problems")

            # Active problems by ICD-10 category
            result = conn.execute(text("""
                SELECT icd10_category, COUNT(*) as count
                FROM clinical.patient_problems
                WHERE problem_status = 'Active'
                  AND icd10_category IS NOT NULL
                GROUP BY icd10_category
                ORDER BY count DESC
                LIMIT 5;
            """))
            logger.info("  - Top 5 ICD-10 categories (active problems):")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} problems")

            # Charlson Index distribution
            result = conn.execute(text("""
                SELECT
                    MIN(charlson_index) as min_score,
                    MAX(charlson_index) as max_score,
                    AVG(charlson_index)::NUMERIC(5,2) as avg_score,
                    percentile_cont(0.5) WITHIN GROUP (ORDER BY charlson_index)::NUMERIC(5,2) as median_score
                FROM (
                    SELECT DISTINCT patient_key, charlson_index
                    FROM clinical.patient_problems
                ) AS unique_patients;
            """))
            row = result.fetchone()
            logger.info(f"  - Charlson Index distribution (unique patients):")
            logger.info(f"    Min: {row[0]}, Max: {row[1]}, Mean: {row[2]}, Median: {row[3]}")

            # Charlson Index ranges
            result = conn.execute(text("""
                SELECT
                    CASE
                        WHEN charlson_index = 0 THEN '0 (No comorbidities)'
                        WHEN charlson_index BETWEEN 1 AND 2 THEN '1-2 (Low)'
                        WHEN charlson_index BETWEEN 3 AND 4 THEN '3-4 (Moderate)'
                        WHEN charlson_index >= 5 THEN '5+ (High)'
                    END as charlson_range,
                    COUNT(*) as patient_count
                FROM (
                    SELECT DISTINCT patient_key, charlson_index
                    FROM clinical.patient_problems
                ) AS unique_patients
                GROUP BY
                    CASE
                        WHEN charlson_index = 0 THEN '0 (No comorbidities)'
                        WHEN charlson_index BETWEEN 1 AND 2 THEN '1-2 (Low)'
                        WHEN charlson_index BETWEEN 3 AND 4 THEN '3-4 (Moderate)'
                        WHEN charlson_index >= 5 THEN '5+ (High)'
                    END
                ORDER BY MIN(charlson_index);
            """))
            logger.info("  - Patients by Charlson Index range:")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} patients")

            # Chronic condition flags
            result = conn.execute(text("""
                SELECT
                    SUM(CASE WHEN has_chf = TRUE THEN 1 ELSE 0 END) as chf,
                    SUM(CASE WHEN has_diabetes = TRUE THEN 1 ELSE 0 END) as diabetes,
                    SUM(CASE WHEN has_copd = TRUE THEN 1 ELSE 0 END) as copd,
                    SUM(CASE WHEN has_ckd = TRUE THEN 1 ELSE 0 END) as ckd,
                    SUM(CASE WHEN has_hypertension = TRUE THEN 1 ELSE 0 END) as hypertension,
                    SUM(CASE WHEN has_depression = TRUE THEN 1 ELSE 0 END) as depression,
                    SUM(CASE WHEN has_ptsd = TRUE THEN 1 ELSE 0 END) as ptsd,
                    SUM(CASE WHEN has_cancer = TRUE THEN 1 ELSE 0 END) as cancer
                FROM (
                    SELECT DISTINCT patient_key, has_chf, has_diabetes, has_copd, has_ckd,
                                    has_hypertension, has_depression, has_ptsd, has_cancer
                    FROM clinical.patient_problems
                ) AS unique_patients;
            """))
            row = result.fetchone()
            logger.info(f"  - Patients with specific chronic conditions:")
            logger.info(f"    CHF: {row[0]}, Diabetes: {row[1]}, COPD: {row[2]}, CKD: {row[3]}")
            logger.info(f"    Hypertension: {row[4]}, Depression: {row[5]}, PTSD: {row[6]}, Cancer: {row[7]}")

            # Service-connected problems
            result = conn.execute(text("""
                SELECT COUNT(*) FROM clinical.patient_problems
                WHERE service_connected = TRUE AND problem_status = 'Active';
            """))
            service_connected_count = result.scalar()
            logger.info(f"  - Active service-connected problems: {service_connected_count}")

            # Source system distribution
            result = conn.execute(text("""
                SELECT source_ehr, COUNT(*) as count
                FROM clinical.patient_problems
                GROUP BY source_ehr
                ORDER BY count DESC;
            """))
            logger.info("  - Problems by source EHR:")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} problems")

            # Sample records
            result = conn.execute(text("""
                SELECT patient_key, icd10_code, icd10_description, problem_status, onset_date, source_ehr
                FROM clinical.patient_problems
                WHERE problem_status = 'Active'
                ORDER BY onset_date DESC
                LIMIT 5;
            """))
            logger.info("  - Sample active problems (most recent 5):")
            for row in result:
                logger.info(f"    {row[0]}: {row[1]} - {row[2][:50]}... ({row[3]}, {row[4]}, {row[5]})")

        logger.info("=" * 70)
        logger.info(f"✓ PostgreSQL load complete: {count} problem records loaded")
        logger.info("=" * 70)

        return count

    except Exception as e:
        logger.error(f"✗ PostgreSQL load failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    load_problems_to_postgresql()
