#!/usr/bin/env python3
"""
Diagnostic script to test medications database queries directly.
This replicates what the web application does to help identify platform-specific issues.

Usage:
    python scripts/test_medications_query.py [ICN]

Example:
    python scripts/test_medications_query.py ICN100001
"""

import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

# Add project root to path
sys.path.insert(0, '/Users/chuck/swdev/med/med-z1')

from config import DATABASE_URL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_outpatient_medications(icn: str):
    """Test outpatient medications query."""
    logger.info("=" * 70)
    logger.info(f"Testing OUTPATIENT medications query for ICN: {icn}")
    logger.info("=" * 70)

    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)

    query = text("""
        SELECT
            medication_outpatient_id,
            patient_icn,
            drug_name_local,
            drug_name_national,
            rx_status_computed,
            issue_date,
            is_active,
            is_controlled_substance
        FROM clinical.patient_medications_outpatient
        WHERE patient_icn = :icn
        ORDER BY issue_date DESC
        LIMIT 10
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            logger.info(f"Found {len(results)} outpatient medications")

            if results:
                logger.info("\nSample records:")
                for i, row in enumerate(results[:5], 1):
                    logger.info(f"\n  Record {i}:")
                    logger.info(f"    ID: {row[0]}")
                    logger.info(f"    Patient ICN: {row[1]}")
                    logger.info(f"    Drug (Local): {row[2]}")
                    logger.info(f"    Drug (National): {row[3]}")
                    logger.info(f"    Status: {row[4]}")
                    logger.info(f"    Issue Date: {row[5]}")
                    logger.info(f"    Active: {row[6]}")
                    logger.info(f"    Controlled: {row[7]}")
            else:
                logger.warning(f"No outpatient medications found for ICN: {icn}")

            return len(results)

    except Exception as e:
        logger.error(f"Error querying outpatient medications: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_inpatient_medications(icn: str):
    """Test inpatient medications query."""
    logger.info("\n" + "=" * 70)
    logger.info(f"Testing INPATIENT medications query for ICN: {icn}")
    logger.info("=" * 70)

    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)

    query = text("""
        SELECT
            medication_inpatient_id,
            patient_icn,
            drug_name_local,
            drug_name_national,
            action_type,
            action_status,
            action_datetime,
            is_controlled_substance
        FROM clinical.patient_medications_inpatient
        WHERE patient_icn = :icn
        ORDER BY action_datetime DESC
        LIMIT 10
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            logger.info(f"Found {len(results)} inpatient medications")

            if results:
                logger.info("\nSample records:")
                for i, row in enumerate(results[:5], 1):
                    logger.info(f"\n  Record {i}:")
                    logger.info(f"    ID: {row[0]}")
                    logger.info(f"    Patient ICN: {row[1]}")
                    logger.info(f"    Drug (Local): {row[2]}")
                    logger.info(f"    Drug (National): {row[3]}")
                    logger.info(f"    Action Type: {row[4]}")
                    logger.info(f"    Action Status: {row[5]}")
                    logger.info(f"    Action DateTime: {row[6]}")
                    logger.info(f"    Controlled: {row[7]}")
            else:
                logger.warning(f"No inpatient medications found for ICN: {icn}")

            return len(results)

    except Exception as e:
        logger.error(f"Error querying inpatient medications: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_medication_counts(icn: str):
    """Test medication counts query."""
    logger.info("\n" + "=" * 70)
    logger.info(f"Testing MEDICATION COUNTS query for ICN: {icn}")
    logger.info("=" * 70)

    engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)

    try:
        with engine.connect() as conn:
            # Outpatient counts
            outpatient_query = text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_active = TRUE) as active,
                    COUNT(*) FILTER (WHERE is_controlled_substance = TRUE) as controlled
                FROM clinical.patient_medications_outpatient
                WHERE patient_icn = :icn
            """)

            result = conn.execute(outpatient_query, {"icn": icn}).fetchone()
            logger.info(f"\nOutpatient medication counts:")
            logger.info(f"  Total: {result[0]}")
            logger.info(f"  Active: {result[1]}")
            logger.info(f"  Controlled: {result[2]}")

            # Inpatient counts
            inpatient_query = text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_controlled_substance = TRUE) as controlled
                FROM clinical.patient_medications_inpatient
                WHERE patient_icn = :icn
            """)

            result = conn.execute(inpatient_query, {"icn": icn}).fetchone()
            logger.info(f"\nInpatient medication counts:")
            logger.info(f"  Total: {result[0]}")
            logger.info(f"  Controlled: {result[1]}")

    except Exception as e:
        logger.error(f"Error querying medication counts: {e}")
        import traceback
        traceback.print_exc()


def test_database_connection():
    """Test basic database connection."""
    logger.info("=" * 70)
    logger.info("Testing database connection")
    logger.info("=" * 70)
    logger.info(f"Database URL: {DATABASE_URL}")

    try:
        engine = create_engine(DATABASE_URL, poolclass=NullPool, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"PostgreSQL version: {version}")

            # Check search path
            result = conn.execute(text("SHOW search_path;"))
            search_path = result.scalar()
            logger.info(f"Schema search path: {search_path}")

            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    # Default test ICN
    test_icn = "ICN100001"

    # Allow ICN to be specified via command line
    if len(sys.argv) > 1:
        test_icn = sys.argv[1]

    logger.info("=" * 70)
    logger.info("MEDICATIONS QUERY DIAGNOSTIC TEST")
    logger.info("=" * 70)
    logger.info(f"Test ICN: {test_icn}")
    logger.info("=" * 70)

    # Test 1: Database connection
    if not test_database_connection():
        logger.error("Database connection failed. Exiting.")
        sys.exit(1)

    # Test 2: Outpatient medications
    outpatient_count = test_outpatient_medications(test_icn)

    # Test 3: Inpatient medications
    inpatient_count = test_inpatient_medications(test_icn)

    # Test 4: Medication counts
    test_medication_counts(test_icn)

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"ICN Tested: {test_icn}")
    logger.info(f"Outpatient medications found: {outpatient_count}")
    logger.info(f"Inpatient medications found: {inpatient_count}")
    logger.info(f"Total medications: {outpatient_count + inpatient_count}")

    if outpatient_count == 0 and inpatient_count == 0:
        logger.warning(f"\n⚠️  NO MEDICATIONS FOUND for {test_icn}")
        logger.warning("This matches the symptoms reported on Linux.")
        logger.warning("\nPossible causes:")
        logger.warning("  1. Data not loaded into medications tables")
        logger.warning("  2. ICN mismatch between demographics and medications")
        logger.warning("  3. Schema search path issues")
        logger.warning("  4. ETL pipeline didn't run successfully")
        logger.warning("\nNext steps:")
        logger.warning("  1. Run: psql -U med -d medz1 -f scripts/diagnose_medications_linux.sql")
        logger.warning("  2. Check ETL logs for medications load")
        logger.warning("  3. Verify data exists in Gold layer Parquet files")
    else:
        logger.info("\n✅ Medications found successfully!")

    logger.info("=" * 70)


if __name__ == "__main__":
    main()
