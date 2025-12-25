# ---------------------------------------------------------------------
# app/db/vitals.py
# ---------------------------------------------------------------------
# Vitals Database Query Layer
# Provides functions to query patient_vitals table in PostgreSQL
# This module encapsulates all SQL queries for vital signs data
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


def get_patient_vitals(
    icn: str,
    limit: Optional[int] = 100,
    vital_type: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all vitals for a patient by ICN.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of vitals to return (default 100)
        vital_type: Optional filter by vital type (e.g., "BLOOD PRESSURE", "TEMPERATURE")

    Returns:
        List of dictionaries with vital signs data
    """
    # Build query with optional vital_type filter
    where_clause = "WHERE patient_key = :icn"
    if vital_type:
        where_clause += " AND vital_type = :vital_type"

    query = text(f"""
        SELECT
            vital_id,
            patient_key,
            vital_sign_id,
            vital_type,
            vital_abbr,
            taken_datetime,
            entered_datetime,
            result_value,
            numeric_value,
            systolic,
            diastolic,
            metric_value,
            unit_of_measure,
            qualifiers,
            location_id,
            location_name,
            location_type,
            entered_by,
            abnormal_flag,
            bmi
        FROM clinical.patient_vitals
        {where_clause}
        ORDER BY taken_datetime DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            params = {"icn": icn, "limit": limit}
            if vital_type:
                params["vital_type"] = vital_type

            results = conn.execute(query, params).fetchall()

            vitals = []
            for row in results:
                vitals.append({
                    "vital_id": row[0],
                    "patient_key": row[1],
                    "vital_sign_id": row[2],
                    "vital_type": row[3],
                    "vital_abbr": row[4],
                    "taken_datetime": str(row[5]) if row[5] else None,
                    "entered_datetime": str(row[6]) if row[6] else None,
                    "result_value": row[7],
                    "numeric_value": float(row[8]) if row[8] is not None else None,
                    "systolic": row[9],
                    "diastolic": row[10],
                    "metric_value": float(row[11]) if row[11] is not None else None,
                    "unit_of_measure": row[12],
                    "qualifiers": row[13],  # Already JSONB
                    "location_id": row[14],
                    "location_name": row[15],
                    "location_type": row[16],
                    "entered_by": row[17],
                    "abnormal_flag": row[18],
                    "bmi": float(row[19]) if row[19] is not None else None,
                })

            return vitals

    except Exception as e:
        logger.error(f"Error fetching vitals for ICN {icn}: {e}")
        return []


def get_recent_vitals(icn: str) -> Dict[str, Any]:
    """
    Get the most recent vital sign measurement per vital type for a patient.
    Used for dashboard widget to show current status.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with vital_abbr as keys and vital data as values
    """
    query = text("""
        SELECT DISTINCT ON (vital_abbr)
            vital_id,
            patient_key,
            vital_sign_id,
            vital_type,
            vital_abbr,
            taken_datetime,
            entered_datetime,
            result_value,
            numeric_value,
            systolic,
            diastolic,
            metric_value,
            unit_of_measure,
            qualifiers,
            location_id,
            location_name,
            location_type,
            entered_by,
            abnormal_flag,
            bmi
        FROM clinical.patient_vitals
        WHERE patient_key = :icn
        ORDER BY vital_abbr, taken_datetime DESC
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            recent_vitals = {}
            for row in results:
                vital_abbr = row[4]
                recent_vitals[vital_abbr] = {
                    "vital_id": row[0],
                    "patient_key": row[1],
                    "vital_sign_id": row[2],
                    "vital_type": row[3],
                    "vital_abbr": vital_abbr,
                    "taken_datetime": str(row[5]) if row[5] else None,
                    "entered_datetime": str(row[6]) if row[6] else None,
                    "result_value": row[7],
                    "numeric_value": float(row[8]) if row[8] is not None else None,
                    "systolic": row[9],
                    "diastolic": row[10],
                    "metric_value": float(row[11]) if row[11] is not None else None,
                    "unit_of_measure": row[12],
                    "qualifiers": row[13],  # Already JSONB
                    "location_id": row[14],
                    "location_name": row[15],
                    "location_type": row[16],
                    "entered_by": row[17],
                    "abnormal_flag": row[18],
                    "bmi": float(row[19]) if row[19] is not None else None,
                }

            return recent_vitals

    except Exception as e:
        logger.error(f"Error fetching recent vitals for ICN {icn}: {e}")
        return {}


def get_vital_type_history(
    icn: str,
    vital_type: str,
    limit: Optional[int] = 50
) -> List[Dict[str, Any]]:
    """
    Get historical timeline for a specific vital type.
    Used for trending and graphing a single vital type over time.

    Args:
        icn: Integrated Care Number
        vital_type: Vital type (e.g., "BLOOD PRESSURE", "TEMPERATURE")
        limit: Maximum number of measurements to return (default 50)

    Returns:
        List of dictionaries with vital measurements sorted by date (oldest first)
    """
    query = text("""
        SELECT
            vital_id,
            patient_key,
            vital_sign_id,
            vital_type,
            vital_abbr,
            taken_datetime,
            entered_datetime,
            result_value,
            numeric_value,
            systolic,
            diastolic,
            metric_value,
            unit_of_measure,
            qualifiers,
            location_id,
            location_name,
            location_type,
            entered_by,
            abnormal_flag,
            bmi
        FROM clinical.patient_vitals
        WHERE patient_key = :icn
          AND vital_type = :vital_type
        ORDER BY taken_datetime ASC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(
                query,
                {"icn": icn, "vital_type": vital_type, "limit": limit}
            ).fetchall()

            history = []
            for row in results:
                history.append({
                    "vital_id": row[0],
                    "patient_key": row[1],
                    "vital_sign_id": row[2],
                    "vital_type": row[3],
                    "vital_abbr": row[4],
                    "taken_datetime": str(row[5]) if row[5] else None,
                    "entered_datetime": str(row[6]) if row[6] else None,
                    "result_value": row[7],
                    "numeric_value": float(row[8]) if row[8] is not None else None,
                    "systolic": row[9],
                    "diastolic": row[10],
                    "metric_value": float(row[11]) if row[11] is not None else None,
                    "unit_of_measure": row[12],
                    "qualifiers": row[13],  # Already JSONB
                    "location_id": row[14],
                    "location_name": row[15],
                    "location_type": row[16],
                    "entered_by": row[17],
                    "abnormal_flag": row[18],
                    "bmi": float(row[19]) if row[19] is not None else None,
                })

            return history

    except Exception as e:
        logger.error(f"Error fetching vital type history for ICN {icn}, type {vital_type}: {e}")
        return []


def get_vital_counts(icn: str) -> Dict[str, int]:
    """
    Get count of vitals per type for a patient.
    Useful for dashboard stats and navigation.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with vital_abbr as keys and counts as values
    """
    query = text("""
        SELECT
            vital_abbr,
            COUNT(*) as count
        FROM clinical.patient_vitals
        WHERE patient_key = :icn
        GROUP BY vital_abbr
        ORDER BY count DESC
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            counts = {}
            for row in results:
                counts[row[0]] = row[1]

            return counts

    except Exception as e:
        logger.error(f"Error fetching vital counts for ICN {icn}: {e}")
        return {}
