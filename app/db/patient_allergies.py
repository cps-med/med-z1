# ---------------------------------------------------------------------
# app/db/patient_allergies.py
# ---------------------------------------------------------------------
# Patient Allergies Database Query Layer
# Provides functions to query patient_allergies and patient_allergy_reactions
# tables in PostgreSQL
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


def get_patient_allergies(patient_icn: str) -> List[Dict[str, Any]]:
    """
    Get all allergies for a patient by ICN.

    Returns allergies sorted by:
    1. Drug allergies first (is_drug_allergy DESC)
    2. Severity rank (SEVERE=3, MODERATE=2, MILD=1, NULL=0)
    3. Most recent origination date first

    Args:
        patient_icn: Patient ICN (Integrated Care Number)

    Returns:
        List of allergy dictionaries with all allergy details
    """
    query = text("""
        SELECT
            allergy_sid,
            patient_key,
            allergen_local,
            allergen_standardized,
            allergen_type,
            severity,
            severity_rank,
            reactions,
            reaction_count,
            origination_date,
            observed_date,
            historical_or_observed,
            originating_site,
            originating_site_name,
            comment,
            verification_status,
            is_drug_allergy,
            is_active,
            originating_staff,
            source_system,
            last_updated
        FROM clinical.patient_allergies
        WHERE patient_key = :patient_icn
          AND is_active = true
        ORDER BY
            is_drug_allergy DESC NULLS LAST,
            severity_rank DESC NULLS LAST,
            origination_date DESC NULLS LAST
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            rows = result.fetchall()

            allergies = []
            for row in rows:
                allergies.append({
                    "allergy_sid": row[0],
                    "patient_key": row[1],
                    "allergen_local": row[2],
                    "allergen_standardized": row[3],
                    "allergen_name": row[3],  # Alias for PatientContextBuilder compatibility
                    "allergen_type": row[4],
                    "severity": row[5],
                    "severity_rank": row[6],
                    "reactions": row[7],
                    "reaction_count": row[8],
                    "origination_date": row[9].isoformat() if row[9] else None,
                    "observed_date": row[10].isoformat() if row[10] else None,
                    "historical_or_observed": row[11],
                    "originating_site": row[12],
                    "originating_site_name": row[13],
                    "comment": row[14],
                    "verification_status": row[15],
                    "is_drug_allergy": row[16],
                    "is_active": row[17],
                    "originating_staff": row[18],
                    "source_system": row[19],
                    "last_updated": row[20].isoformat() if row[20] else None,
                })

            logger.info(f"Retrieved {len(allergies)} allergies for patient {patient_icn}")
            return allergies

    except Exception as e:
        logger.error(f"Error fetching patient allergies for ICN {patient_icn}: {e}")
        return []


def get_critical_allergies(patient_icn: str, limit: int = 6) -> List[Dict[str, Any]]:
    """
    Get critical allergies for dashboard widget display.

    Prioritizes:
    1. Drug allergies first
    2. Highest severity (SEVERE > MODERATE > MILD)
    3. Most recent

    Args:
        patient_icn: Patient ICN
        limit: Maximum number of allergies to return (default 6 for widget)

    Returns:
        List of critical allergy dictionaries (limited to top N)
    """
    query = text("""
        SELECT
            allergy_sid,
            patient_key,
            allergen_local,
            allergen_standardized,
            allergen_type,
            severity,
            severity_rank,
            reactions,
            reaction_count,
            origination_date,
            is_drug_allergy
        FROM clinical.patient_allergies
        WHERE patient_key = :patient_icn
          AND is_active = true
        ORDER BY
            is_drug_allergy DESC NULLS LAST,
            severity_rank DESC NULLS LAST,
            origination_date DESC NULLS LAST
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "patient_icn": patient_icn,
                "limit": limit
            })
            rows = result.fetchall()

            allergies = []
            for row in rows:
                allergies.append({
                    "allergy_sid": row[0],
                    "patient_key": row[1],
                    "allergen_local": row[2],
                    "allergen_standardized": row[3],
                    "allergen_name": row[3],  # Alias for PatientContextBuilder compatibility
                    "allergen_type": row[4],
                    "severity": row[5],
                    "severity_rank": row[6],
                    "reactions": row[7],
                    "reaction_count": row[8],
                    "origination_date": row[9].isoformat() if row[9] else None,
                    "is_drug_allergy": row[10],
                })

            logger.info(f"Retrieved {len(allergies)} critical allergies for patient {patient_icn}")
            return allergies

    except Exception as e:
        logger.error(f"Error fetching critical allergies for ICN {patient_icn}: {e}")
        return []


def get_allergy_details(allergy_sid: int, patient_icn: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for a specific allergy.

    Includes full details including comment field (may be large).

    Args:
        allergy_sid: Allergy SID (surrogate ID)
        patient_icn: Patient ICN (for security validation)

    Returns:
        Allergy dictionary with all details, or None if not found
    """
    query = text("""
        SELECT
            allergy_sid,
            patient_key,
            allergen_local,
            allergen_standardized,
            allergen_type,
            severity,
            severity_rank,
            reactions,
            reaction_count,
            origination_date,
            observed_date,
            historical_or_observed,
            originating_site,
            originating_site_name,
            comment,
            verification_status,
            is_drug_allergy,
            is_active,
            originating_staff,
            source_system,
            last_updated
        FROM clinical.patient_allergies
        WHERE allergy_sid = :allergy_sid
          AND patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "allergy_sid": allergy_sid,
                "patient_icn": patient_icn
            })
            row = result.fetchone()

            if not row:
                logger.warning(f"Allergy {allergy_sid} not found for patient {patient_icn}")
                return None

            allergy = {
                "allergy_sid": row[0],
                "patient_key": row[1],
                "allergen_local": row[2],
                "allergen_standardized": row[3],
                "allergen_name": row[3],  # Alias for PatientContextBuilder compatibility
                "allergen_type": row[4],
                "severity": row[5],
                "severity_rank": row[6],
                "reactions": row[7],
                "reaction_count": row[8],
                "origination_date": row[9].isoformat() if row[9] else None,
                "observed_date": row[10].isoformat() if row[10] else None,
                "historical_or_observed": row[11],
                "originating_site": row[12],
                "originating_site_name": row[13],
                "comment": row[14],
                "verification_status": row[15],
                "is_drug_allergy": row[16],
                "is_active": row[17],
                "originating_staff": row[18],
                "source_system": row[19],
                "last_updated": row[20].isoformat() if row[20] else None,
            }

            logger.info(f"Retrieved allergy details for {allergy_sid}")
            return allergy

    except Exception as e:
        logger.error(f"Error fetching allergy details for SID {allergy_sid}: {e}")
        return None


def get_allergy_count(patient_icn: str) -> Dict[str, int]:
    """
    Get allergy counts for badge display.

    Args:
        patient_icn: Patient ICN

    Returns:
        Dictionary with total, drug, food, environmental, and severe counts
    """
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN allergen_type = 'DRUG' THEN 1 ELSE 0 END) as drug,
            SUM(CASE WHEN allergen_type = 'FOOD' THEN 1 ELSE 0 END) as food,
            SUM(CASE WHEN allergen_type = 'ENVIRONMENTAL' THEN 1 ELSE 0 END) as environmental,
            SUM(CASE WHEN severity = 'SEVERE' THEN 1 ELSE 0 END) as severe
        FROM clinical.patient_allergies
        WHERE patient_key = :patient_icn
          AND is_active = true
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            counts = {
                "total": int(row[0]) if row[0] else 0,
                "drug": int(row[1]) if row[1] else 0,
                "food": int(row[2]) if row[2] else 0,
                "environmental": int(row[3]) if row[3] else 0,
                "severe": int(row[4]) if row[4] else 0,
            }

            logger.info(f"Allergy counts for {patient_icn}: {counts}")
            return counts

    except Exception as e:
        logger.error(f"Error getting allergy count for ICN {patient_icn}: {e}")
        return {"total": 0, "drug": 0, "food": 0, "environmental": 0, "severe": 0}


def get_allergy_reactions(allergy_sid: int) -> List[Dict[str, Any]]:
    """
    Get individual reactions for a specific allergy (from normalized table).

    Args:
        allergy_sid: Allergy SID

    Returns:
        List of reaction dictionaries
    """
    query = text("""
        SELECT
            allergy_sid,
            patient_key,
            reaction_name
        FROM patient_allergy_reactions
        WHERE allergy_sid = :allergy_sid
        ORDER BY reaction_name
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"allergy_sid": allergy_sid})
            rows = result.fetchall()

            reactions = []
            for row in rows:
                reactions.append({
                    "allergy_sid": row[0],
                    "patient_key": row[1],
                    "reaction_name": row[2],
                })

            logger.info(f"Retrieved {len(reactions)} reactions for allergy {allergy_sid}")
            return reactions

    except Exception as e:
        logger.error(f"Error fetching reactions for allergy {allergy_sid}: {e}")
        return []
