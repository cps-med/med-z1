# ---------------------------------------------------------------------
# app/db/labs.py
# ---------------------------------------------------------------------
# Laboratory Results Database Query Layer
# Provides functions to query patient_labs table in PostgreSQL
# This module encapsulates all SQL queries for lab results data
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


def get_recent_panels(
    icn: str,
    limit: Optional[int] = 3
) -> List[Dict[str, Any]]:
    """
    Get the most recent lab panels for a patient (for dashboard widget).
    Groups results by panel_name and accession_number, returns most recent panels.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of panels to return (default 3 for 3x1 widget layout)

    Returns:
        List of dictionaries with panel data including results
    """
    # First, get the most recent panels
    panel_query = text("""
        SELECT DISTINCT
            panel_name,
            accession_number,
            collection_datetime,
            location_id,
            collection_location,
            collection_location_type,
            sta3n
        FROM clinical.patient_labs
        WHERE patient_key = :icn
          AND panel_name IS NOT NULL
        ORDER BY collection_datetime DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            panel_results = conn.execute(
                panel_query,
                {"icn": icn, "limit": limit}
            ).fetchall()

            panels = []
            for panel_row in panel_results:
                panel_name = panel_row[0]
                accession_number = panel_row[1]

                # Get all results for this panel
                results_query = text("""
                    SELECT
                        lab_id,
                        lab_test_name,
                        result_value,
                        result_numeric,
                        result_unit,
                        abnormal_flag,
                        is_abnormal,
                        is_critical,
                        ref_range_text,
                        collection_datetime
                    FROM clinical.patient_labs
                    WHERE patient_key = :icn
                      AND accession_number = :accession_number
                    ORDER BY lab_test_name ASC
                """)

                results = conn.execute(
                    results_query,
                    {"icn": icn, "accession_number": accession_number}
                ).fetchall()

                panel_data = {
                    "panel_name": panel_name,
                    "accession_number": accession_number,
                    "collection_datetime": str(panel_row[2]) if panel_row[2] else None,
                    "location_id": panel_row[3],
                    "collection_location": panel_row[4],
                    "collection_location_type": panel_row[5],
                    "sta3n": panel_row[6],
                    "results": []
                }

                for result in results:
                    panel_data["results"].append({
                        "lab_id": result[0],
                        "lab_test_name": result[1],
                        "result_value": result[2],
                        "result_numeric": float(result[3]) if result[3] is not None else None,
                        "result_unit": result[4],
                        "abnormal_flag": result[5],
                        "is_abnormal": result[6],
                        "is_critical": result[7],
                        "ref_range_text": result[8],
                        "collection_datetime": str(result[9]) if result[9] else None,
                    })

                panels.append(panel_data)

            return panels

    except Exception as e:
        logger.error(f"Error fetching recent panels for ICN {icn}: {e}")
        return []


def get_trending_tests(
    icn: str,
    test_names: Optional[List[str]] = None,
    days: Optional[int] = 90
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get trending data for specific lab tests (for widget sparklines).
    Returns historical values for specified tests over time period.

    Args:
        icn: Integrated Care Number
        test_names: List of test names to trend (e.g., ["Glucose", "Creatinine"])
        days: Number of days to look back (default 90)

    Returns:
        Dictionary keyed by test name with list of {date, value} points
    """
    if test_names is None:
        test_names = ["Glucose", "Creatinine", "Hemoglobin", "Potassium"]

    query = text("""
        SELECT
            lab_test_name,
            collection_datetime,
            result_numeric,
            result_unit,
            abnormal_flag
        FROM clinical.patient_labs
        WHERE patient_key = :icn
          AND lab_test_name = ANY(:test_names)
          AND result_numeric IS NOT NULL
          AND collection_datetime >= CURRENT_DATE - INTERVAL ':days days'
        ORDER BY lab_test_name ASC, collection_datetime ASC
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(
                query,
                {"icn": icn, "test_names": test_names, "days": days}
            ).fetchall()

            trending_data = {}
            for row in results:
                test_name = row[0]
                if test_name not in trending_data:
                    trending_data[test_name] = []

                trending_data[test_name].append({
                    "collection_datetime": str(row[1]) if row[1] else None,
                    "result_numeric": float(row[2]) if row[2] is not None else None,
                    "result_unit": row[3],
                    "abnormal_flag": row[4],
                })

            return trending_data

    except Exception as e:
        logger.error(f"Error fetching trending tests for ICN {icn}: {e}")
        return {}


def get_all_lab_results(
    icn: str,
    limit: Optional[int] = 100,
    offset: Optional[int] = 0,
    panel_filter: Optional[str] = None,
    abnormal_only: Optional[bool] = False,
    days: Optional[int] = None,
    sort_by: Optional[str] = "collection_datetime",
    sort_order: Optional[str] = "desc"
) -> List[Dict[str, Any]]:
    """
    Get all lab results for a patient with optional filters and sorting.
    Used for full lab results page with filtering capabilities.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of results to return (default 100)
        offset: Number of results to skip (for pagination, default 0)
        panel_filter: Filter by panel name (e.g., "BMP", "CBC")
        abnormal_only: If True, return only abnormal results (default False)
        days: If specified, only return results from last N days
        sort_by: Column to sort by (default: collection_datetime)
        sort_order: Sort direction - asc or desc (default: desc)

    Returns:
        List of dictionaries with lab result data
    """
    # Build query with optional filters
    where_clauses = ["patient_key = :icn"]
    if panel_filter:
        # Handle "Individual Tests" filter (these have NULL panel_name)
        if panel_filter == "Individual Tests":
            where_clauses.append("panel_name IS NULL")
        else:
            where_clauses.append("panel_name = :panel_filter")
    if abnormal_only:
        where_clauses.append("is_abnormal = TRUE")
    if days:
        where_clauses.append("collection_datetime >= CURRENT_DATE - INTERVAL ':days days'")

    where_clause = " AND ".join(where_clauses)

    # Validate and build ORDER BY clause
    valid_sort_columns = {
        "collection_datetime": "collection_datetime",
        "lab_test_name": "lab_test_name",
        "abnormal_flag": "is_abnormal DESC, abnormal_flag"
    }

    order_column = valid_sort_columns.get(sort_by, "collection_datetime")
    order_direction = "ASC" if sort_order.lower() == "asc" else "DESC"
    order_clause = f"{order_column} {order_direction}"

    query = text(f"""
        SELECT
            lab_id,
            patient_key,
            lab_chem_sid,
            lab_test_sid,
            lab_test_name,
            lab_test_code,
            loinc_code,
            panel_name,
            accession_number,
            result_value,
            result_numeric,
            result_unit,
            abnormal_flag,
            is_abnormal,
            is_critical,
            ref_range_text,
            ref_range_low,
            ref_range_high,
            collection_datetime,
            result_datetime,
            location_id,
            collection_location,
            collection_location_type,
            specimen_type,
            sta3n,
            vista_package,
            last_updated
        FROM clinical.patient_labs
        WHERE {where_clause}
        ORDER BY {order_clause}
        LIMIT :limit
        OFFSET :offset
    """)

    try:
        with engine.connect() as conn:
            params = {"icn": icn, "limit": limit, "offset": offset}
            if panel_filter:
                params["panel_filter"] = panel_filter
            if days:
                params["days"] = days

            results = conn.execute(query, params).fetchall()

            labs = []
            for row in results:
                labs.append({
                    "lab_id": row[0],
                    "patient_key": row[1],
                    "lab_chem_sid": row[2],
                    "lab_test_sid": row[3],
                    "lab_test_name": row[4],
                    "lab_test_code": row[5],
                    "loinc_code": row[6],
                    "panel_name": row[7],
                    "accession_number": row[8],
                    "result_value": row[9],
                    "result_numeric": float(row[10]) if row[10] is not None else None,
                    "result_unit": row[11],
                    "abnormal_flag": row[12],
                    "is_abnormal": row[13],
                    "is_critical": row[14],
                    "ref_range_text": row[15],
                    "ref_range_low": float(row[16]) if row[16] is not None else None,
                    "ref_range_high": float(row[17]) if row[17] is not None else None,
                    "collection_datetime": str(row[18]) if row[18] else None,
                    "result_datetime": str(row[19]) if row[19] else None,
                    "location_id": row[20],
                    "collection_location": row[21],
                    "collection_location_type": row[22],
                    "specimen_type": row[23],
                    "sta3n": row[24],
                    "vista_package": row[25],
                    "last_updated": str(row[26]) if row[26] else None,
                })

            return labs

    except Exception as e:
        logger.error(f"Error fetching lab results for ICN {icn}: {e}")
        return []


def get_test_trend(
    icn: str,
    lab_test_name: str,
    days: Optional[int] = 365
) -> List[Dict[str, Any]]:
    """
    Get historical trend data for a specific lab test.
    Used for graphing a single test over time on the full page view.

    Args:
        icn: Integrated Care Number
        lab_test_name: Name of the lab test (e.g., "Glucose", "Creatinine")
        days: Number of days to look back (default 365)

    Returns:
        List of dictionaries with test values sorted by date (oldest first for charting)
    """
    query = text("""
        SELECT
            lab_id,
            collection_datetime,
            result_value,
            result_numeric,
            result_unit,
            abnormal_flag,
            is_abnormal,
            is_critical,
            ref_range_text,
            ref_range_low,
            ref_range_high,
            location_id,
            collection_location,
            collection_location_type,
            sta3n
        FROM clinical.patient_labs
        WHERE patient_key = :icn
          AND lab_test_name = :lab_test_name
          AND collection_datetime >= CURRENT_DATE - INTERVAL ':days days'
        ORDER BY collection_datetime ASC
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(
                query,
                {"icn": icn, "lab_test_name": lab_test_name, "days": days}
            ).fetchall()

            trend_data = []
            for row in results:
                trend_data.append({
                    "lab_id": row[0],
                    "collection_datetime": str(row[1]) if row[1] else None,
                    "result_value": row[2],
                    "result_numeric": float(row[3]) if row[3] is not None else None,
                    "result_unit": row[4],
                    "abnormal_flag": row[5],
                    "is_abnormal": row[6],
                    "is_critical": row[7],
                    "ref_range_text": row[8],
                    "ref_range_low": float(row[9]) if row[9] is not None else None,
                    "ref_range_high": float(row[10]) if row[10] is not None else None,
                    "location_id": row[11],
                    "collection_location": row[12],
                    "collection_location_type": row[13],
                    "sta3n": row[14],
                })

            return trend_data

    except Exception as e:
        logger.error(f"Error fetching test trend for ICN {icn}, test {lab_test_name}: {e}")
        return []


def get_lab_counts(icn: str) -> Dict[str, int]:
    """
    Get counts of lab results by panel for a patient.
    Useful for dashboard stats and navigation.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with panel names as keys and counts as values
    """
    query = text("""
        SELECT
            COALESCE(panel_name, 'Individual Tests') as panel_category,
            COUNT(*) as count
        FROM clinical.patient_labs
        WHERE patient_key = :icn
        GROUP BY panel_category
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
        logger.error(f"Error fetching lab counts for ICN {icn}: {e}")
        return {}
