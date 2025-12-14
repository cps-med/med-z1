# ---------------------------------------------------------------------
# app/db/patient.py
# ---------------------------------------------------------------------
# Patient Database Query Layer
# Provides functions to query patient_demographics table in PostgreSQL
# This module encapsulates all SQL queries for patient data
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


def get_patient_demographics(icn: str) -> Optional[Dict[str, Any]]:
    """
    Get patient demographics by ICN.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with patient demographics or None if not found
    """
    query = text("""
        SELECT
            patient_key,
            icn,
            ssn_last4,
            name_last,
            name_first,
            name_display,
            dob,
            age,
            sex,
            primary_station,
            primary_station_name,
            address_street1,
            address_street2,
            address_city,
            address_state,
            address_zip,
            phone_primary,
            insurance_company_name,
            marital_status,
            religion,
            service_connected_percent,
            deceased_flag,
            death_date,
            source_system,
            last_updated
        FROM patient_demographics
        WHERE icn = :icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn}).fetchone()

            if result:
                return {
                    "patient_key": result[0],
                    "icn": result[1],
                    "ssn_last4": result[2],
                    "name_last": result[3],
                    "name_first": result[4],
                    "name_display": result[5],
                    "dob": str(result[6]) if result[6] else None,
                    "age": result[7],
                    "sex": result[8],
                    "primary_station": result[9],
                    "primary_station_name": result[10],
                    "address_street1": result[11],
                    "address_street2": result[12],
                    "address_city": result[13],
                    "address_state": result[14],
                    "address_zip": result[15],
                    "phone_primary": result[16],
                    "insurance_company_name": result[17],
                    "marital_status": result[18],
                    "religion": result[19],
                    "service_connected_percent": float(result[20]) if result[20] is not None else None,
                    "deceased_flag": result[21],
                    "death_date": str(result[22]) if result[22] else None,
                    "source_system": result[23],
                    "last_updated": str(result[24]) if result[24] else None,
                }

            return None

    except Exception as e:
        logger.error(f"Error fetching patient demographics for ICN {icn}: {e}")
        return None


def search_patients(
    query: str,
    search_type: str = "name",
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Search for patients.

    Args:
        query: Search query string
        search_type: Type of search - 'name', 'icn', or 'edipi'
        limit: Maximum number of results

    Returns:
        List of patient dictionaries
    """
    try:
        if search_type == "name":
            sql_query = text("""
                SELECT
                    icn,
                    name_display,
                    dob,
                    age,
                    sex,
                    ssn_last4,
                    primary_station
                FROM patient_demographics
                WHERE name_last ILIKE :query OR name_first ILIKE :query
                ORDER BY name_last, name_first
                LIMIT :limit
            """)
            params = {"query": f"%{query}%", "limit": limit}

        elif search_type == "icn":
            sql_query = text("""
                SELECT
                    icn,
                    name_display,
                    dob,
                    age,
                    sex,
                    ssn_last4,
                    primary_station
                FROM patient_demographics
                WHERE icn = :query
                LIMIT :limit
            """)
            params = {"query": query, "limit": limit}

        elif search_type == "edipi":
            # EDIPI not yet implemented in database
            # Return empty results for now
            logger.warning("EDIPI search not yet implemented")
            return []

        else:
            logger.warning(f"Unknown search type: {search_type}")
            return []

        with engine.connect() as conn:
            results = conn.execute(sql_query, params).fetchall()

            return [
                {
                    "icn": row[0],
                    "name_display": row[1],
                    "dob": str(row[2]) if row[2] else None,
                    "age": row[3],
                    "sex": row[4],
                    "ssn_last4": row[5],
                    "station": row[6],
                }
                for row in results
            ]

    except Exception as e:
        logger.error(f"Error searching patients: {e}")
        return []


def get_patient_flags(icn: str) -> Dict[str, Any]:
    """
    Get patient flags by ICN.

    NOTE: This is a placeholder for Phase 3 implementation.
    Currently returns mock data for UI development.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with flags array and count
    """
    # TODO: Phase 3 - Query patient_flags table
    logger.info(f"get_patient_flags called for {icn} (Phase 3 placeholder)")

    # Mock data for Phase 2
    return {
        "flags": [
            {
                "flag_name": "High Risk for Suicide",
                "category": "BEHAVIORAL",
                "narrative": "Patient flagged for suicide risk assessment",
                "active_date": "2024-01-15",
                "review_date": "2025-01-15"
            },
            {
                "flag_name": "Potential Drug-Drug Interaction Risk",
                "category": "MEDICATION",
                "narrative": "This is sample narrative text",
                "active_date": "2024-01-15",
                "review_date": "2025-01-15"
            }
        ],
        "count": 2
    }