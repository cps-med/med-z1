# ---------------------------------------------------------------------
# app/db/patient_immunizations.py
# ---------------------------------------------------------------------
# Patient Immunizations Database Query Layer
# Provides functions to query clinical.patient_immunizations table
# This module encapsulates all SQL queries for immunization data
# ---------------------------------------------------------------------

from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta
import logging
from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,  # Set to True to see SQL queries in logs
)


def get_patient_immunizations(
    icn: str,
    limit: Optional[int] = 100,
    vaccine_group: Optional[str] = None,
    cvx_code: Optional[str] = None,
    days: Optional[int] = None,
    incomplete_only: bool = False,
    adverse_reactions_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Get all immunizations for a patient by ICN.

    Args:
        icn: Integrated Care Number
        limit: Maximum number of immunizations to return (default 100)
        vaccine_group: Optional filter by vaccine group ('Influenza', 'COVID-19', 'Hepatitis', etc.)
        cvx_code: Optional filter by CVX code
        days: Optional filter to last N days (default: all)
        incomplete_only: Filter to incomplete series only (default: False)
        adverse_reactions_only: Filter to records with adverse reactions (default: False)

    Returns:
        List of dictionaries with immunization data
    """
    # Build WHERE clause
    where_clauses = ["patient_key = :icn"]

    if vaccine_group:
        if vaccine_group.lower() == 'influenza':
            where_clauses.append("is_annual_vaccine = TRUE")
        elif vaccine_group.lower() == 'covid-19':
            where_clauses.append("is_covid_vaccine = TRUE")
        else:
            # General vaccine group filter (would require join to reference.vaccine)
            where_clauses.append("vaccine_name ILIKE :vaccine_group")

    if cvx_code:
        where_clauses.append("cvx_code = :cvx_code")

    if days:
        where_clauses.append("administered_datetime >= :cutoff_date")

    if incomplete_only:
        where_clauses.append("is_series_complete = FALSE")

    if adverse_reactions_only:
        where_clauses.append("has_adverse_reaction = TRUE")

    where_clause = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            immunization_id,
            patient_key,
            immunization_sid,
            cvx_code,
            vaccine_name,
            vaccine_name_local,
            administered_datetime,
            series,
            dose_number,
            total_doses,
            is_series_complete,
            dose,
            route,
            site_of_administration,
            adverse_reaction,
            has_adverse_reaction,
            provider_name,
            location_sid,
            location_name,
            location_type,
            station_name,
            sta3n,
            comments,
            is_annual_vaccine,
            is_covid_vaccine,
            source_system,
            last_updated
        FROM clinical.patient_immunizations
        WHERE {where_clause}
        ORDER BY administered_datetime DESC
        {f"LIMIT {limit}" if limit else ""}
    """)

    try:
        with engine.connect() as conn:
            params = {"icn": icn}
            if vaccine_group and vaccine_group.lower() not in ['influenza', 'covid-19']:
                params["vaccine_group"] = f"%{vaccine_group}%"
            if cvx_code:
                params["cvx_code"] = cvx_code
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                params["cutoff_date"] = cutoff

            results = conn.execute(query, params).fetchall()

            immunizations = []
            for row in results:
                immunizations.append({
                    "immunization_id": row[0],
                    "patient_key": row[1],
                    "immunization_sid": row[2],
                    "cvx_code": row[3],
                    "vaccine_name": row[4],
                    "vaccine_name_local": row[5],
                    "administered_datetime": row[6].isoformat() if row[6] else None,
                    "administered_date": row[6].strftime("%Y-%m-%d") if row[6] else None,
                    "series": row[7],
                    "dose_number": row[8],
                    "total_doses": row[9],
                    "is_series_complete": row[10],
                    "dose": row[11],
                    "route": row[12],
                    "site_of_administration": row[13],
                    "adverse_reaction": row[14],
                    "has_adverse_reaction": row[15],
                    "provider_name": row[16],
                    "location_sid": row[17],
                    "location_name": row[18],
                    "location_type": row[19],
                    "station_name": row[20],
                    "sta3n": row[21],
                    "comments": row[22],
                    "is_annual_vaccine": row[23],
                    "is_covid_vaccine": row[24],
                    "source_system": row[25],
                    "last_updated": row[26].isoformat() if row[26] else None
                })

            logger.info(f"Fetched {len(immunizations)} immunizations for patient {icn}")
            return immunizations

    except Exception as e:
        logger.error(f"Error fetching immunizations for {icn}: {e}")
        raise


def get_recent_immunizations(icn: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get recent immunizations for dashboard widget (last 2 years).

    Args:
        icn: Integrated Care Number
        limit: Maximum number to return (default 5)

    Returns:
        List of dictionaries with recent immunization data
    """
    return get_patient_immunizations(icn, limit=limit, days=730)  # 2 years


def get_immunization_counts(icn: str) -> Dict[str, int]:
    """
    Get count summary of immunizations by category.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with counts by category
    """
    query = text("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN is_annual_vaccine = TRUE THEN 1 ELSE 0 END) as annual,
            SUM(CASE WHEN is_covid_vaccine = TRUE THEN 1 ELSE 0 END) as covid,
            SUM(CASE WHEN is_series_complete = FALSE THEN 1 ELSE 0 END) as incomplete,
            SUM(CASE WHEN has_adverse_reaction = TRUE THEN 1 ELSE 0 END) as with_reactions,
            SUM(CASE WHEN administered_datetime >= NOW() - INTERVAL '2 years' THEN 1 ELSE 0 END) as recent_2y
        FROM clinical.patient_immunizations
        WHERE patient_key = :icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn}).fetchone()

            if result:
                return {
                    "total": result[0] or 0,
                    "annual": result[1] or 0,
                    "covid": result[2] or 0,
                    "incomplete": result[3] or 0,
                    "with_reactions": result[4] or 0,
                    "recent_2y": result[5] or 0
                }
            else:
                return {
                    "total": 0,
                    "annual": 0,
                    "covid": 0,
                    "incomplete": 0,
                    "with_reactions": 0,
                    "recent_2y": 0
                }

    except Exception as e:
        logger.error(f"Error fetching immunization counts for {icn}: {e}")
        raise


def get_vaccine_reference() -> List[Dict[str, Any]]:
    """
    Get all vaccines from reference.vaccine table.

    Returns:
        List of dictionaries with vaccine reference data
    """
    query = text("""
        SELECT
            cvx_code,
            vaccine_name,
            vaccine_short_name,
            vaccine_group,
            typical_series_pattern,
            is_active,
            notes
        FROM reference.vaccine
        WHERE is_active = TRUE
        ORDER BY vaccine_group, vaccine_name
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query).fetchall()

            vaccines = []
            for row in results:
                vaccines.append({
                    "cvx_code": row[0],
                    "vaccine_name": row[1],
                    "vaccine_short_name": row[2],
                    "vaccine_group": row[3],
                    "typical_series_pattern": row[4],
                    "is_active": row[5],
                    "notes": row[6]
                })

            return vaccines

    except Exception as e:
        logger.error(f"Error fetching vaccine reference data: {e}")
        raise
