# ---------------------------------------------------------------------
# app/db/medications.py
# ---------------------------------------------------------------------
# Medications Database Query Layer
# Provides functions to query patient_medications_outpatient and
# patient_medications_inpatient tables in PostgreSQL
# This module encapsulates all SQL queries for medications data
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


def get_patient_medications(
    icn: str,
    limit: Optional[int] = 100,
    medication_type: Optional[str] = None,
    status: Optional[str] = None,
    days: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all medications for a patient by ICN (both outpatient and inpatient).

    Args:
        icn: Integrated Care Number
        limit: Maximum number of medications to return (default 100)
        medication_type: Optional filter by type ('outpatient', 'inpatient', or None for both)
        status: Optional filter by status (for outpatient: 'ACTIVE', 'DISCONTINUED', etc.)
        days: Optional filter to last N days (default: all)

    Returns:
        List of dictionaries with medication data from both sources, unified format
    """
    medications = []

    # Get outpatient medications if requested
    if medication_type is None or medication_type == 'outpatient':
        outpatient_meds = _get_outpatient_medications(icn, limit, status, days)
        medications.extend(outpatient_meds)

    # Get inpatient medications if requested
    if medication_type is None or medication_type == 'inpatient':
        inpatient_meds = _get_inpatient_medications(icn, limit, days)
        medications.extend(inpatient_meds)

    # Sort by date descending (most recent first)
    medications.sort(key=lambda m: m.get('date') or '', reverse=True)

    # Apply limit to combined results
    if limit:
        medications = medications[:limit]

    return medications


def _get_outpatient_medications(
    icn: str,
    limit: Optional[int] = None,
    status: Optional[str] = None,
    days: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get outpatient medications (RxOut) for a patient.

    Returns:
        List of dictionaries with outpatient medication data
    """
    # Build WHERE clause
    where_clauses = ["patient_icn = :icn"]

    if status:
        where_clauses.append("rx_status_computed = :status")

    if days:
        where_clauses.append("issue_date >= :cutoff_date")

    where_clause = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            medication_outpatient_id,
            patient_icn,
            rx_outpat_id,
            prescription_number,
            drug_name_local,
            drug_name_national,
            generic_name,
            drug_strength,
            drug_unit,
            dosage_form,
            drug_class,
            dea_schedule,
            issue_date,
            rx_status,
            rx_status_computed,
            quantity_ordered,
            days_supply,
            refills_allowed,
            refills_remaining,
            latest_fill_date,
            latest_fill_status,
            expiration_date,
            discontinued_date,
            discontinue_reason,
            is_controlled_substance,
            is_active,
            days_until_expiration,
            provider_name,
            pharmacy_name,
            facility_name,
            cmop_indicator,
            mail_indicator
        FROM clinical.patient_medications_outpatient
        WHERE {where_clause}
        ORDER BY issue_date DESC
        {f"LIMIT {limit}" if limit else ""}
    """)

    try:
        with engine.connect() as conn:
            params = {"icn": icn}
            if status:
                params["status"] = status
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                params["cutoff_date"] = cutoff

            results = conn.execute(query, params).fetchall()

            medications = []
            for row in results:
                medications.append({
                    "medication_id": f"rxout_{row[0]}",  # Prefix for uniqueness
                    "type": "outpatient",
                    "patient_icn": row[1],
                    "source_id": row[2],  # rx_outpat_id
                    "prescription_number": row[3],
                    "drug_name_local": row[4],
                    "drug_name_national": row[5],
                    "generic_name": row[6],
                    "drug_strength": row[7],
                    "drug_unit": row[8],
                    "dosage_form": row[9],
                    "drug_class": row[10],
                    "dea_schedule": row[11],
                    "date": str(row[12]) if row[12] else None,  # issue_date
                    "status": row[14],  # rx_status_computed
                    "status_original": row[13],  # rx_status
                    "quantity_ordered": float(row[15]) if row[15] is not None else None,
                    "days_supply": row[16],
                    "refills_allowed": row[17],
                    "refills_remaining": row[18],
                    "latest_fill_date": str(row[19]) if row[19] else None,
                    "latest_fill_status": row[20],
                    "expiration_date": str(row[21]) if row[21] else None,
                    "discontinued_date": str(row[22]) if row[22] else None,
                    "discontinue_reason": row[23],
                    "is_controlled_substance": row[24],
                    "is_active": row[25],
                    "days_until_expiration": row[26],
                    "provider_name": row[27],
                    "pharmacy_name": row[28],
                    "facility_name": row[29],
                    "cmop_indicator": row[30],
                    "mail_indicator": row[31],
                })

            return medications

    except Exception as e:
        logger.error(f"Error fetching outpatient medications for ICN {icn}: {e}")
        return []


def _get_inpatient_medications(
    icn: str,
    limit: Optional[int] = None,
    days: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get inpatient medications (BCMA) for a patient.

    Returns:
        List of dictionaries with inpatient medication data
    """
    # Build WHERE clause
    where_clauses = ["patient_icn = :icn"]

    if days:
        where_clauses.append("action_datetime >= :cutoff_date")

    where_clause = " AND ".join(where_clauses)

    query = text(f"""
        SELECT
            medication_inpatient_id,
            patient_icn,
            bcma_log_id,
            order_number,
            drug_name_local,
            drug_name_national,
            generic_name,
            drug_strength,
            drug_unit,
            dosage_form,
            drug_class,
            dea_schedule,
            action_type,
            action_status,
            action_datetime,
            scheduled_datetime,
            dosage_ordered,
            dosage_given,
            route,
            schedule,
            administration_variance,
            variance_type,
            variance_reason,
            is_iv_medication,
            iv_type,
            infusion_rate,
            is_controlled_substance,
            administered_by,
            ordering_provider,
            ward_name,
            facility_name
        FROM clinical.patient_medications_inpatient
        WHERE {where_clause}
        ORDER BY action_datetime DESC
        {f"LIMIT {limit}" if limit else ""}
    """)

    try:
        with engine.connect() as conn:
            params = {"icn": icn}
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                params["cutoff_date"] = cutoff

            results = conn.execute(query, params).fetchall()

            medications = []
            for row in results:
                medications.append({
                    "medication_id": f"bcma_{row[0]}",  # Prefix for uniqueness
                    "type": "inpatient",
                    "patient_icn": row[1],
                    "source_id": row[2],  # bcma_log_id
                    "order_number": row[3],
                    "drug_name_local": row[4],
                    "drug_name_national": row[5],
                    "generic_name": row[6],
                    "drug_strength": row[7],
                    "drug_unit": row[8],
                    "dosage_form": row[9],
                    "drug_class": row[10],
                    "dea_schedule": row[11],
                    "action_type": row[12],
                    "action_status": row[13],
                    "date": str(row[14]) if row[14] else None,  # action_datetime
                    "scheduled_datetime": str(row[15]) if row[15] else None,
                    "dosage_ordered": row[16],
                    "dosage_given": row[17],
                    "route": row[18],
                    "schedule": row[19],
                    "administration_variance": row[20],
                    "variance_type": row[21],
                    "variance_reason": row[22],
                    "is_iv_medication": row[23],
                    "iv_type": row[24],
                    "infusion_rate": row[25],
                    "is_controlled_substance": row[26],
                    "administered_by": row[27],
                    "ordering_provider": row[28],
                    "ward_name": row[29],
                    "facility_name": row[30],
                })

            return medications

    except Exception as e:
        logger.error(f"Error fetching inpatient medications for ICN {icn}: {e}")
        return []


def get_recent_medications(icn: str, limit: int = 8) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get recent medications for dashboard widget.
    Returns both outpatient and inpatient medications separately.

    Args:
        icn: Integrated Care Number
        limit: Number of medications per type (default 8, will get 4 per type)

    Returns:
        Dictionary with 'outpatient' and 'inpatient' keys, each containing list of medications
    """
    per_type_limit = limit // 2  # Split between outpatient and inpatient

    # Get recent outpatient medications (no date filter, just most recent by issue_date)
    outpatient = _get_outpatient_medications(icn, limit=per_type_limit)

    # Get recent inpatient medications (no date filter, just most recent by action_datetime)
    inpatient = _get_inpatient_medications(icn, limit=per_type_limit)

    return {
        "outpatient": outpatient,
        "inpatient": inpatient
    }


def get_medication_counts(icn: str) -> Dict[str, int]:
    """
    Get counts of medications by type for a patient.
    Useful for dashboard stats and navigation.

    Args:
        icn: Integrated Care Number

    Returns:
        Dictionary with medication counts
    """
    counts = {
        "outpatient_total": 0,
        "outpatient_active": 0,
        "outpatient_controlled": 0,
        "inpatient_total": 0,
        "inpatient_controlled": 0,
    }

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
            if result:
                counts["outpatient_total"] = result[0]
                counts["outpatient_active"] = result[1]
                counts["outpatient_controlled"] = result[2]

            # Inpatient counts
            inpatient_query = text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE is_controlled_substance = TRUE) as controlled
                FROM clinical.patient_medications_inpatient
                WHERE patient_icn = :icn
            """)

            result = conn.execute(inpatient_query, {"icn": icn}).fetchone()
            if result:
                counts["inpatient_total"] = result[0]
                counts["inpatient_controlled"] = result[1]

        return counts

    except Exception as e:
        logger.error(f"Error fetching medication counts for ICN {icn}: {e}")
        return counts
