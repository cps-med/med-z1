# ---------------------------------------------------------------------
# app/db/encounters.py
# ---------------------------------------------------------------------
# Encounters Database Query Layer
# Provides functions to query patient_encounters table in PostgreSQL
# This module encapsulates all SQL queries for inpatient encounter data
# ---------------------------------------------------------------------

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,  # Set to True to see SQL queries in logs
)


def get_patient_encounters(
    icn: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    active_only: Optional[bool] = False,
    recent_only: Optional[bool] = False
) -> List[Dict[str, Any]]:
    """
    Get all encounters for a patient by ICN.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of encounters to return (default 100)
        offset: Number of encounters to skip (for pagination, default 0)
        active_only: If True, return only active admissions (default False)
        recent_only: If True, return only recent encounters (last 30 days, default False)

    Returns:
        List of dictionaries with encounter data
    """
    # Build query with optional filters
    where_clauses = ["patient_key = :icn"]
    if active_only:
        where_clauses.append("is_active = TRUE")
    if recent_only:
        where_clauses.append("is_recent = TRUE")

    where_clause = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            encounter_id,
            patient_key,
            inpatient_id,
            admit_datetime,
            admit_location_id,
            admit_diagnosis_code,
            admitting_provider_id,
            admitting_provider_name,
            discharge_datetime,
            discharge_date_id,
            discharge_location_id,
            discharge_diagnosis_code,
            discharge_diagnosis_text,
            discharge_disposition,
            length_of_stay,
            total_days,
            encounter_status,
            is_active,
            admission_category,
            is_recent,
            is_extended_stay,
            sta3n,
            facility_name,
            source_system,
            last_updated
        FROM patient_encounters
        WHERE {where_clause}
        ORDER BY admit_datetime DESC
        LIMIT :limit
        OFFSET :offset
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(
                query,
                {"icn": icn, "limit": limit, "offset": offset}
            ).fetchall()

            encounters = []
            for row in results:
                encounters.append({
                    "encounter_id": row[0],
                    "patient_key": row[1],
                    "inpatient_id": row[2],
                    "admit_datetime": str(row[3]) if row[3] else None,
                    "admit_location_id": row[4],
                    "admit_diagnosis_code": row[5],
                    "admitting_provider_id": row[6],
                    "admitting_provider_name": row[7],
                    "discharge_datetime": str(row[8]) if row[8] else None,
                    "discharge_date_id": row[9],
                    "discharge_location_id": row[10],
                    "discharge_diagnosis_code": row[11],
                    "discharge_diagnosis_text": row[12],
                    "discharge_disposition": row[13],
                    "length_of_stay": row[14],
                    "total_days": row[15],
                    "encounter_status": row[16],
                    "is_active": row[17],
                    "admission_category": row[18],
                    "is_recent": row[19],
                    "is_extended_stay": row[20],
                    "sta3n": row[21],
                    "facility_name": row[22],
                    "source_system": row[23],
                    "last_updated": str(row[24]) if row[24] else None,
                })

            return encounters

    except Exception as e:
        logger.error(f"Error fetching encounters for ICN {icn}: {e}")
        return []


def get_recent_encounters(icn: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most recent encounters for a patient (active and recently discharged).
    Used for dashboard widget to show current admission status.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of encounters to return (default 5)

    Returns:
        List of dictionaries with recent encounter data
    """
    query = text("""
        SELECT
            encounter_id,
            patient_key,
            inpatient_id,
            admit_datetime,
            admit_diagnosis_code,
            admitting_provider_name,
            discharge_datetime,
            discharge_diagnosis_text,
            discharge_disposition,
            length_of_stay,
            total_days,
            encounter_status,
            is_active,
            admission_category,
            is_extended_stay,
            sta3n,
            facility_name
        FROM patient_encounters
        WHERE patient_key = :icn
          AND is_recent = TRUE
        ORDER BY admit_datetime DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn, "limit": limit}).fetchall()

            encounters = []
            for row in results:
                encounters.append({
                    "encounter_id": row[0],
                    "patient_key": row[1],
                    "inpatient_id": row[2],
                    "admit_datetime": str(row[3]) if row[3] else None,
                    "admit_diagnosis_code": row[4],
                    "admitting_provider_name": row[5],
                    "discharge_datetime": str(row[6]) if row[6] else None,
                    "discharge_diagnosis_text": row[7],
                    "discharge_disposition": row[8],
                    "length_of_stay": row[9],
                    "total_days": row[10],
                    "encounter_status": row[11],
                    "is_active": row[12],
                    "admission_category": row[13],
                    "is_extended_stay": row[14],
                    "sta3n": row[15],
                    "facility_name": row[16],
                })

            return encounters

    except Exception as e:
        logger.error(f"Error fetching recent encounters for ICN {icn}: {e}")
        return []


def get_active_admissions(icn: str) -> List[Dict[str, Any]]:
    """
    Get currently active admissions for a patient.
    Used for alerts and current admission status.

    Args:
        icn: Integrated Care Number

    Returns:
        List of dictionaries with active admission data
    """
    query = text("""
        SELECT
            encounter_id,
            patient_key,
            inpatient_id,
            admit_datetime,
            admit_diagnosis_code,
            admitting_provider_name,
            length_of_stay,
            total_days,
            admission_category,
            is_extended_stay,
            sta3n,
            facility_name
        FROM patient_encounters
        WHERE patient_key = :icn
          AND is_active = TRUE
        ORDER BY admit_datetime DESC
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            admissions = []
            for row in results:
                admissions.append({
                    "encounter_id": row[0],
                    "patient_key": row[1],
                    "inpatient_id": row[2],
                    "admit_datetime": str(row[3]) if row[3] else None,
                    "admit_diagnosis_code": row[4],
                    "admitting_provider_name": row[5],
                    "length_of_stay": row[6],
                    "total_days": row[7],
                    "admission_category": row[8],
                    "is_extended_stay": row[9],
                    "sta3n": row[10],
                    "facility_name": row[11],
                })

            return admissions

    except Exception as e:
        logger.error(f"Error fetching active admissions for ICN {icn}: {e}")
        return []


def get_encounter_counts(icn: str) -> Dict[str, int]:
    """
    Get counts of encounters by category for a patient.
    Useful for dashboard stats and navigation.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with encounter statistics
    """
    query = text("""
        SELECT
            COUNT(*) as total_encounters,
            COUNT(*) FILTER (WHERE is_active = TRUE) as active_admissions,
            COUNT(*) FILTER (WHERE is_recent = TRUE) as recent_encounters,
            COUNT(*) FILTER (WHERE is_extended_stay = TRUE) as extended_stays,
            COUNT(DISTINCT sta3n) as facility_count
        FROM patient_encounters
        WHERE patient_key = :icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn}).fetchone()

            return {
                "total_encounters": result[0] if result else 0,
                "active_admissions": result[1] if result else 0,
                "recent_encounters": result[2] if result else 0,
                "extended_stays": result[3] if result else 0,
                "facility_count": result[4] if result else 0,
            }

    except Exception as e:
        logger.error(f"Error fetching encounter counts for ICN {icn}: {e}")
        return {
            "total_encounters": 0,
            "active_admissions": 0,
            "recent_encounters": 0,
            "extended_stays": 0,
            "facility_count": 0,
        }


def get_encounter_by_id(encounter_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single encounter by encounter_id.
    Used for detail views.

    Args:
        encounter_id: Encounter ID

    Returns:
        Dictionary with complete encounter data, or None if not found
    """
    query = text("""
        SELECT
            encounter_id,
            patient_key,
            inpatient_id,
            admit_datetime,
            admit_location_id,
            admit_diagnosis_code,
            admitting_provider_id,
            admitting_provider_name,
            discharge_datetime,
            discharge_date_id,
            discharge_location_id,
            discharge_diagnosis_code,
            discharge_diagnosis_text,
            discharge_disposition,
            length_of_stay,
            total_days,
            encounter_status,
            is_active,
            admission_category,
            is_recent,
            is_extended_stay,
            sta3n,
            facility_name,
            source_system,
            last_updated
        FROM patient_encounters
        WHERE encounter_id = :encounter_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"encounter_id": encounter_id}).fetchone()

            if not result:
                return None

            return {
                "encounter_id": result[0],
                "patient_key": result[1],
                "inpatient_id": result[2],
                "admit_datetime": str(result[3]) if result[3] else None,
                "admit_location_id": result[4],
                "admit_diagnosis_code": result[5],
                "admitting_provider_id": result[6],
                "admitting_provider_name": result[7],
                "discharge_datetime": str(result[8]) if result[8] else None,
                "discharge_date_id": result[9],
                "discharge_location_id": result[10],
                "discharge_diagnosis_code": result[11],
                "discharge_diagnosis_text": result[12],
                "discharge_disposition": result[13],
                "length_of_stay": result[14],
                "total_days": result[15],
                "encounter_status": result[16],
                "is_active": result[17],
                "admission_category": result[18],
                "is_recent": result[19],
                "is_extended_stay": result[20],
                "sta3n": result[21],
                "facility_name": result[22],
                "source_system": result[23],
                "last_updated": str(result[24]) if result[24] else None,
            }

    except Exception as e:
        logger.error(f"Error fetching encounter {encounter_id}: {e}")
        return None
