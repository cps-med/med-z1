# ---------------------------------------------------------------------
# app/db/patient_family_history.py
# ---------------------------------------------------------------------
# Database query functions for patient family history
# ---------------------------------------------------------------------

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,
)


def get_patient_family_history(
    icn: str,
    days: Optional[int] = None,
    relationship: Optional[str] = None,
    category: Optional[str] = None,
    active_only: bool = False,
) -> List[Dict[str, Any]]:
    """
    Get family history rows for a patient with optional filtering.

    Args:
        icn: Integrated Care Number
        days: Optional lookback window in days
        relationship: Optional filter by relationship (name or code)
        category: Optional filter by condition category/risk group
        active_only: If True, only return active rows

    Returns:
        List of family-history dictionaries sorted by most recent recorded date.
    """

    where_clauses = ["patient_icn = :icn"]
    params: Dict[str, Any] = {"icn": icn}

    if days and days > 0:
        where_clauses.append("recorded_datetime >= :cutoff_datetime")
        params["cutoff_datetime"] = datetime.utcnow() - timedelta(days=days)

    if relationship:
        where_clauses.append("(relationship_name ILIKE :relationship OR relationship_code ILIKE :relationship)")
        params["relationship"] = f"%{relationship}%"

    if category:
        where_clauses.append(
            "(condition_category ILIKE :category OR risk_condition_group ILIKE :category)"
        )
        params["category"] = f"%{category}%"

    if active_only:
        where_clauses.append("is_active = TRUE")

    where_sql = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            family_history_id,
            patient_icn,
            patient_key,
            source_system,
            source_ehr,
            source_record_id,
            relationship_code,
            relationship_name,
            relationship_degree,
            condition_code,
            condition_name,
            snomed_code,
            icd10_code,
            condition_category,
            risk_condition_group,
            hereditary_risk_flag,
            first_degree_relative_flag,
            clinical_status,
            is_active,
            family_member_gender,
            family_member_age,
            family_member_deceased,
            onset_age_years,
            recorded_datetime,
            entered_datetime,
            encounter_sid,
            facility_id,
            provider_id,
            provider_name,
            location_id,
            comment_text,
            last_updated
        FROM clinical.patient_family_history
        WHERE {where_sql}
        ORDER BY recorded_datetime DESC NULLS LAST, family_history_id DESC
    """)

    try:
        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        history = []
        for row in rows:
            history.append({
                "family_history_id": row[0],
                "patient_icn": row[1],
                "patient_key": row[2],
                "source_system": row[3],
                "source_ehr": row[4],
                "source_record_id": row[5],
                "relationship_code": row[6],
                "relationship_name": row[7],
                "relationship_degree": row[8],
                "condition_code": row[9],
                "condition_name": row[10],
                "snomed_code": row[11],
                "icd10_code": row[12],
                "condition_category": row[13],
                "risk_condition_group": row[14],
                "hereditary_risk_flag": row[15],
                "first_degree_relative_flag": row[16],
                "clinical_status": row[17],
                "is_active": row[18],
                "family_member_gender": row[19],
                "family_member_age": row[20],
                "family_member_deceased": row[21],
                "onset_age_years": row[22],
                "recorded_datetime": row[23].isoformat() if row[23] else None,
                "entered_datetime": row[24].isoformat() if row[24] else None,
                "encounter_sid": row[25],
                "facility_id": row[26],
                "provider_id": row[27],
                "provider_name": row[28],
                "location_id": row[29],
                "comment_text": row[30],
                "last_updated": row[31].isoformat() if row[31] else None,
            })

        logger.info(
            "Retrieved %s family-history rows for patient %s (days=%s, relationship=%s, category=%s, active_only=%s)",
            len(history),
            icn,
            days,
            relationship,
            category,
            active_only,
        )
        return history

    except Exception as exc:
        logger.error("Error fetching family history for ICN %s: %s", icn, exc)
        return []


def get_recent_family_history(icn: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get the most recent family history rows for dashboard/widget usage.

    Args:
        icn: Integrated Care Number
        limit: Maximum rows to return

    Returns:
        List of family-history dictionaries, most recent first.
    """

    safe_limit = max(1, min(limit, 50))

    query = text("""
        SELECT
            family_history_id,
            patient_icn,
            source_system,
            relationship_name,
            relationship_degree,
            condition_name,
            condition_category,
            clinical_status,
            first_degree_relative_flag,
            hereditary_risk_flag,
            onset_age_years,
            recorded_datetime,
            comment_text
        FROM clinical.patient_family_history
        WHERE patient_icn = :icn
        ORDER BY recorded_datetime DESC NULLS LAST, family_history_id DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            rows = conn.execute(query, {"icn": icn, "limit": safe_limit}).fetchall()

        recent = []
        for row in rows:
            recent.append({
                "family_history_id": row[0],
                "patient_icn": row[1],
                "source_system": row[2],
                "relationship_name": row[3],
                "relationship_degree": row[4],
                "condition_name": row[5],
                "condition_category": row[6],
                "clinical_status": row[7],
                "first_degree_relative_flag": row[8],
                "hereditary_risk_flag": row[9],
                "onset_age_years": row[10],
                "recorded_datetime": row[11].isoformat() if row[11] else None,
                "comment_text": row[12],
            })

        logger.info("Retrieved %s recent family-history rows for patient %s", len(recent), icn)
        return recent

    except Exception as exc:
        logger.error("Error fetching recent family history for ICN %s: %s", icn, exc)
        return []


def get_family_history_counts(icn: str) -> Dict[str, Any]:
    """
    Get aggregate family-history counts for a patient.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with counts and recentness fields.
    """

    query = text("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN is_active = TRUE THEN 1 ELSE 0 END) AS active,
            SUM(CASE WHEN first_degree_relative_flag = TRUE THEN 1 ELSE 0 END) AS first_degree,
            SUM(CASE WHEN first_degree_relative_flag = TRUE
                      AND COALESCE(hereditary_risk_flag, FALSE) = TRUE
                     THEN 1 ELSE 0 END) AS first_degree_high_risk,
            COUNT(DISTINCT condition_name) AS distinct_conditions,
            SUM(CASE WHEN recorded_datetime >= NOW() - INTERVAL '2 years' THEN 1 ELSE 0 END) AS recent_2y,
            MAX(recorded_datetime) AS last_recorded_datetime
        FROM clinical.patient_family_history
        WHERE patient_icn = :icn
    """)

    try:
        with engine.connect() as conn:
            row = conn.execute(query, {"icn": icn}).fetchone()

        if not row:
            return {
                "total": 0,
                "active": 0,
                "first_degree": 0,
                "first_degree_high_risk": 0,
                "distinct_conditions": 0,
                "recent_2y": 0,
                "last_recorded_datetime": None,
            }

        return {
            "total": row[0] or 0,
            "active": row[1] or 0,
            "first_degree": row[2] or 0,
            "first_degree_high_risk": row[3] or 0,
            "distinct_conditions": row[4] or 0,
            "recent_2y": row[5] or 0,
            "last_recorded_datetime": row[6].isoformat() if row[6] else None,
        }

    except Exception as exc:
        logger.error("Error fetching family-history counts for ICN %s: %s", icn, exc)
        return {
            "total": 0,
            "active": 0,
            "first_degree": 0,
            "first_degree_high_risk": 0,
            "distinct_conditions": 0,
            "recent_2y": 0,
            "last_recorded_datetime": None,
        }
