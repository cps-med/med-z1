# ---------------------------------------------------------------------
# app/db/patient_flags.py
# ---------------------------------------------------------------------
# Patient Flags Database Query Layer
# Provides functions to query patient_flags and patient_flag_history
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


def get_patient_flags(patient_icn: str) -> List[Dict[str, Any]]:
    """
    Get all flags for a patient by ICN.

    Args:
        patient_icn: Patient ICN (Integrated Care Number)

    Returns:
        List of flag dictionaries with all flag details
    """
    query = text("""
        SELECT
            flag_id,
            patient_key,
            assignment_id,
            flag_name,
            flag_category,
            flag_type,
            is_active,
            assignment_status,
            assignment_date,
            inactivation_date,
            owner_site,
            owner_site_name,
            review_frequency_days,
            next_review_date,
            review_status,
            last_action_date,
            last_action,
            last_action_by,
            last_updated
        FROM clinical.patient_flags
        WHERE patient_key = :patient_icn
        ORDER BY
            flag_category ASC,  -- National (I) first, then Local (II)
            is_active DESC,     -- Active flags first
            assignment_date DESC
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            rows = result.fetchall()

            flags = []
            for row in rows:
                flags.append({
                    "flag_id": row[0],
                    "patient_key": row[1],
                    "assignment_id": row[2],
                    "flag_name": row[3],
                    "flag_category": row[4],
                    "flag_type": row[5],
                    "is_active": row[6],
                    "assignment_status": row[7],
                    "assignment_date": row[8].isoformat() if row[8] else None,
                    "inactivation_date": row[9].isoformat() if row[9] else None,
                    "owner_site": row[10],
                    "owner_site_name": row[11],
                    "review_frequency_days": row[12],
                    "next_review_date": row[13].isoformat() if row[13] else None,
                    "review_status": row[14],
                    "last_action_date": row[15].isoformat() if row[15] else None,
                    "last_action": row[16],
                    "last_action_by": row[17],
                    "last_updated": row[18].isoformat() if row[18] else None,
                })

            logger.info(f"Retrieved {len(flags)} flags for patient {patient_icn}")
            return flags

    except Exception as e:
        logger.error(f"Error fetching patient flags for ICN {patient_icn}: {e}")
        return []


def get_flag_count(patient_icn: str) -> Dict[str, int]:
    """
    Get flag counts for badge display.

    Args:
        patient_icn: Patient ICN

    Returns:
        Dictionary with total, national, local, and overdue counts
    """
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN flag_category = 'I' THEN 1 ELSE 0 END) as national,
            SUM(CASE WHEN flag_category = 'II' THEN 1 ELSE 0 END) as local,
            SUM(CASE WHEN review_status = 'OVERDUE' THEN 1 ELSE 0 END) as overdue
        FROM clinical.patient_flags
        WHERE patient_key = :patient_icn
          AND is_active = true
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            counts = {
                "total": int(row[0]) if row[0] else 0,
                "national": int(row[1]) if row[1] else 0,
                "local": int(row[2]) if row[2] else 0,
                "overdue": int(row[3]) if row[3] else 0,
            }

            logger.info(f"Flag counts for {patient_icn}: {counts}")
            return counts

    except Exception as e:
        logger.error(f"Error getting flag count for ICN {patient_icn}: {e}")
        return {"total": 0, "national": 0, "local": 0, "overdue": 0}


def get_flag_history(assignment_id: int, patient_icn: str) -> List[Dict[str, Any]]:
    """
    Get complete history timeline for a specific flag assignment.

    IMPORTANT: Includes SENSITIVE narrative text with clinical details.

    Args:
        assignment_id: Flag assignment ID
        patient_icn: Patient ICN (for security validation)

    Returns:
        List of history records ordered by date (most recent first)
    """
    query = text("""
        SELECT
            history_id,
            assignment_id,
            patient_key,
            history_date,
            action_code,
            action_name,
            entered_by_duz,
            entered_by_name,
            approved_by_duz,
            approved_by_name,
            tiu_document_ien,
            history_comments,
            event_site,
            created_at
        FROM clinical.patient_flag_history
        WHERE assignment_id = :assignment_id
          AND patient_key = :patient_icn
        ORDER BY history_date DESC
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "assignment_id": assignment_id,
                "patient_icn": patient_icn
            })
            rows = result.fetchall()

            history = []
            for row in rows:
                history.append({
                    "history_id": row[0],
                    "assignment_id": row[1],
                    "patient_key": row[2],
                    "history_date": row[3].isoformat() if row[3] else None,
                    "action_code": row[4],
                    "action_name": row[5],
                    "entered_by_duz": row[6],
                    "entered_by_name": row[7],
                    "approved_by_duz": row[8],
                    "approved_by_name": row[9],
                    "tiu_document_ien": row[10],
                    "narrative": row[11],  # SENSITIVE - clinical narrative
                    "event_site": row[12],
                    "created_at": row[13].isoformat() if row[13] else None,
                })

            logger.info(f"Retrieved {len(history)} history records for assignment {assignment_id}")
            return history

    except Exception as e:
        logger.error(f"Error fetching flag history for assignment {assignment_id}: {e}")
        return []


def get_active_flags_count(patient_icn: str) -> int:
    """
    Get count of active flags for a patient (quick helper for badge).

    Args:
        patient_icn: Patient ICN

    Returns:
        Count of active flags
    """
    query = text("""
        SELECT COUNT(*)
        FROM clinical.patient_flags
        WHERE patient_key = :patient_icn
          AND is_active = true
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            count = result.scalar()
            return int(count) if count else 0

    except Exception as e:
        logger.error(f"Error getting active flag count for ICN {patient_icn}: {e}")
        return 0
