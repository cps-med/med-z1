# ---------------------------------------------------------------------
# app/db/patient_problems.py
# ---------------------------------------------------------------------
# Patient Problems Database Query Layer
# Provides functions to query patient_problems table in PostgreSQL
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


def get_patient_problems(
    patient_icn: str,
    status: Optional[str] = None,
    category: Optional[str] = None,
    service_connected_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Get all problems for a patient by ICN with optional filtering.

    Returns problems sorted by:
    1. Status priority (Active > Inactive > Resolved)
    2. Most recent onset date first

    Args:
        patient_icn: Patient ICN (Integrated Care Number)
        status: Filter by status ('Active', 'Inactive', 'Resolved', or None for all)
        category: Filter by ICD-10 category (e.g., 'Cardiovascular', 'Respiratory', or None for all)
        service_connected_only: If True, only return service-connected problems

    Returns:
        List of problem dictionaries with all problem details
    """
    # Build query with dynamic WHERE clauses
    where_clauses = ["patient_key = :patient_icn"]
    params = {"patient_icn": patient_icn}

    if status:
        where_clauses.append("problem_status = :status")
        params["status"] = status

    if category:
        where_clauses.append("icd10_category = :category")
        params["category"] = category

    if service_connected_only:
        where_clauses.append("service_connected = true")

    where_sql = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            problem_id,
            patient_key,
            patient_icn,
            icd10_code,
            icd10_description,
            icd10_category,
            snomed_code,
            snomed_description,
            diagnosis_description,
            problem_status,
            onset_date,
            recorded_date,
            last_modified_date,
            resolved_date,
            service_connected,
            acute_condition,
            chronic_condition,
            provider_name,
            clinic_location,
            icd10_charlson_condition,
            source_ehr,
            source_system
        FROM clinical.patient_problems
        WHERE {where_sql}
        ORDER BY
            CASE problem_status
                WHEN 'Active' THEN 1
                WHEN 'Inactive' THEN 2
                WHEN 'Resolved' THEN 3
                ELSE 4
            END,
            onset_date DESC NULLS LAST
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()

            problems = []
            for row in rows:
                problems.append({
                    "problem_id": row[0],
                    "patient_key": row[1],
                    "patient_icn": row[2],
                    "icd10_code": row[3],
                    "icd10_description": row[4],
                    "icd10_category": row[5],
                    "snomed_code": row[6],
                    "snomed_description": row[7],
                    "problem_text": row[8],  # diagnosis_description
                    "problem_status": row[9],
                    "onset_date": row[10].isoformat() if row[10] else None,
                    "recorded_date": row[11].isoformat() if row[11] else None,
                    "modified_date": row[12].isoformat() if row[12] else None,
                    "resolved_date": row[13].isoformat() if row[13] else None,
                    "service_connected": row[14],
                    "is_acute": row[15],
                    "is_chronic": row[16],
                    "provider_name": row[17],
                    "clinic_location": row[18],
                    "charlson_condition": row[19],
                    "source_ehr": row[20],
                    "source_system": row[21],
                })

            logger.info(f"Retrieved {len(problems)} problems for patient {patient_icn} (status={status}, category={category}, sc_only={service_connected_only})")
            return problems

    except Exception as e:
        logger.error(f"Error fetching patient problems for ICN {patient_icn}: {e}")
        return []


def get_problems_summary(patient_icn: str, limit: int = 8) -> Dict[str, Any]:
    """
    Get problems summary for dashboard widget display.

    Returns top N active problems plus aggregate statistics.

    Args:
        patient_icn: Patient ICN
        limit: Maximum number of problems to return in list (default 8 for widget)

    Returns:
        Dictionary with:
        - problems: List of top N active problems
        - total_active: Total count of active problems
        - total_chronic: Count of chronic conditions
        - charlson_index: Charlson Comorbidity Index score
        - has_critical_conditions: Boolean flag for CHF/COPD/CKD/diabetes
    """
    # Get top N active problems
    problems_query = text("""
        SELECT
            problem_id,
            patient_key,
            icd10_code,
            icd10_description,
            icd10_category,
            diagnosis_description,
            problem_status,
            onset_date,
            service_connected,
            chronic_condition,
            icd10_charlson_condition
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
          AND problem_status = 'Active'
        ORDER BY
            icd10_charlson_condition DESC NULLS LAST,
            chronic_condition DESC NULLS LAST,
            onset_date DESC NULLS LAST
        LIMIT :limit
    """)

    # Get summary statistics
    stats_query = text("""
        SELECT
            COUNT(*) FILTER (WHERE problem_status = 'Active') as total_active,
            COUNT(*) FILTER (WHERE chronic_condition = true) as total_chronic,
            MAX(charlson_index) as charlson_index,
            BOOL_OR(has_chf) as has_chf,
            BOOL_OR(has_copd) as has_copd,
            BOOL_OR(has_ckd) as has_ckd,
            BOOL_OR(has_diabetes) as has_diabetes
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            # Get top problems
            result = conn.execute(problems_query, {"patient_icn": patient_icn, "limit": limit})
            rows = result.fetchall()

            problems = []
            for row in rows:
                problems.append({
                    "problem_id": row[0],
                    "patient_key": row[1],
                    "icd10_code": row[2],
                    "icd10_description": row[3],
                    "icd10_category": row[4],
                    "problem_text": row[5],
                    "problem_status": row[6],
                    "onset_date": row[7].isoformat() if row[7] else None,
                    "service_connected": row[8],
                    "is_chronic": row[9],
                    "charlson_condition": row[10],
                })

            # Get statistics
            result = conn.execute(stats_query, {"patient_icn": patient_icn})
            stats_row = result.fetchone()

            summary = {
                "problems": problems,
                "total_active": stats_row[0] or 0,
                "total_chronic": stats_row[1] or 0,
                "charlson_index": stats_row[2] or 0,
                "has_critical_conditions": any([stats_row[3], stats_row[4], stats_row[5], stats_row[6]]),
                "has_chf": stats_row[3] or False,
                "has_copd": stats_row[4] or False,
                "has_ckd": stats_row[5] or False,
                "has_diabetes": stats_row[6] or False,
            }

            logger.info(f"Retrieved problems summary for patient {patient_icn}: {summary['total_active']} active, Charlson={summary['charlson_index']}")
            return summary

    except Exception as e:
        logger.error(f"Error fetching problems summary for ICN {patient_icn}: {e}")
        return {
            "problems": [],
            "total_active": 0,
            "total_chronic": 0,
            "charlson_index": 0,
            "has_critical_conditions": False,
            "has_chf": False,
            "has_copd": False,
            "has_ckd": False,
            "has_diabetes": False,
        }


def get_problems_grouped_by_category(patient_icn: str, status: str = "Active") -> Dict[str, List[Dict[str, Any]]]:
    """
    Get problems grouped by ICD-10 category.

    Args:
        patient_icn: Patient ICN
        status: Problem status filter (default 'Active')

    Returns:
        Dictionary mapping category name to list of problems
        Example: {"Cardiovascular": [...], "Respiratory": [...], ...}
    """
    query = text("""
        SELECT
            problem_id,
            patient_key,
            icd10_code,
            icd10_description,
            icd10_category,
            diagnosis_description,
            problem_status,
            onset_date,
            service_connected,
            chronic_condition,
            icd10_charlson_condition
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
          AND problem_status = :status
        ORDER BY
            icd10_category NULLS LAST,
            onset_date DESC NULLS LAST
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn, "status": status})
            rows = result.fetchall()

            grouped = {}
            for row in rows:
                category = row[4] or "Other"

                problem = {
                    "problem_id": row[0],
                    "patient_key": row[1],
                    "icd10_code": row[2],
                    "icd10_description": row[3],
                    "icd10_category": row[4],
                    "problem_text": row[5],
                    "problem_status": row[6],
                    "onset_date": row[7].isoformat() if row[7] else None,
                    "service_connected": row[8],
                    "is_chronic": row[9],
                    "charlson_condition": row[10],
                }

                if category not in grouped:
                    grouped[category] = []

                grouped[category].append(problem)

            logger.info(f"Retrieved problems grouped by category for patient {patient_icn}: {len(grouped)} categories")
            return grouped

    except Exception as e:
        logger.error(f"Error fetching grouped problems for ICN {patient_icn}: {e}")
        return {}


def get_charlson_score(patient_icn: str) -> int:
    """
    Get Charlson Comorbidity Index score for a patient.

    Args:
        patient_icn: Patient ICN

    Returns:
        Integer Charlson score (0-37, typically 0-15)
    """
    query = text("""
        SELECT MAX(charlson_index) as charlson_score
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            score = row[0] if row and row[0] is not None else 0
            logger.info(f"Charlson score for patient {patient_icn}: {score}")
            return score

    except Exception as e:
        logger.error(f"Error fetching Charlson score for ICN {patient_icn}: {e}")
        return 0


def has_chronic_condition(patient_icn: str, condition: str) -> bool:
    """
    Check if patient has a specific chronic condition.

    Args:
        patient_icn: Patient ICN
        condition: Condition flag name (e.g., 'has_chf', 'has_diabetes', 'has_copd', 'has_ckd')

    Returns:
        Boolean indicating if patient has the condition
    """
    # Map condition names to column names
    condition_columns = {
        "chf": "has_chf",
        "cad": "has_cad",
        "afib": "has_afib",
        "hypertension": "has_hypertension",
        "copd": "has_copd",
        "asthma": "has_asthma",
        "diabetes": "has_diabetes",
        "hyperlipidemia": "has_hyperlipidemia",
        "ckd": "has_ckd",
        "depression": "has_depression",
        "ptsd": "has_ptsd",
        "anxiety": "has_anxiety",
        "cancer": "has_cancer",
        "osteoarthritis": "has_osteoarthritis",
        "back_pain": "has_back_pain",
    }

    column = condition_columns.get(condition.lower().replace("has_", ""))
    if not column:
        logger.warning(f"Unknown condition: {condition}")
        return False

    query = text(f"""
        SELECT BOOL_OR({column}) as has_condition
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            has_cond = row[0] if row and row[0] is not None else False
            logger.debug(f"Patient {patient_icn} has {condition}: {has_cond}")
            return has_cond

    except Exception as e:
        logger.error(f"Error checking condition {condition} for ICN {patient_icn}: {e}")
        return False


def get_chronic_conditions_summary(patient_icn: str) -> Dict[str, bool]:
    """
    Get summary of all chronic conditions for a patient.

    Args:
        patient_icn: Patient ICN

    Returns:
        Dictionary mapping condition name to boolean
    """
    query = text("""
        SELECT
            BOOL_OR(has_chf) as has_chf,
            BOOL_OR(has_cad) as has_cad,
            BOOL_OR(has_afib) as has_afib,
            BOOL_OR(has_hypertension) as has_hypertension,
            BOOL_OR(has_copd) as has_copd,
            BOOL_OR(has_asthma) as has_asthma,
            BOOL_OR(has_diabetes) as has_diabetes,
            BOOL_OR(has_hyperlipidemia) as has_hyperlipidemia,
            BOOL_OR(has_ckd) as has_ckd,
            BOOL_OR(has_depression) as has_depression,
            BOOL_OR(has_ptsd) as has_ptsd,
            BOOL_OR(has_anxiety) as has_anxiety,
            BOOL_OR(has_cancer) as has_cancer,
            BOOL_OR(has_osteoarthritis) as has_osteoarthritis,
            BOOL_OR(has_back_pain) as has_back_pain
        FROM clinical.patient_problems
        WHERE patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            if not row:
                return {}

            conditions = {
                "has_chf": row[0] or False,
                "has_cad": row[1] or False,
                "has_afib": row[2] or False,
                "has_hypertension": row[3] or False,
                "has_copd": row[4] or False,
                "has_asthma": row[5] or False,
                "has_diabetes": row[6] or False,
                "has_hyperlipidemia": row[7] or False,
                "has_ckd": row[8] or False,
                "has_depression": row[9] or False,
                "has_ptsd": row[10] or False,
                "has_anxiety": row[11] or False,
                "has_cancer": row[12] or False,
                "has_osteoarthritis": row[13] or False,
                "has_back_pain": row[14] or False,
            }

            logger.info(f"Retrieved chronic conditions summary for patient {patient_icn}")
            return conditions

    except Exception as e:
        logger.error(f"Error fetching chronic conditions for ICN {patient_icn}: {e}")
        return {}
