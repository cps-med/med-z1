# ---------------------------------------------------------------------
# app/db/military_history.py
# ---------------------------------------------------------------------
# Database query functions for patient military history
# ---------------------------------------------------------------------

from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)


def get_patient_military_history(icn: str) -> Optional[Dict[str, Any]]:
    """
    Get military history for a specific patient by ICN.

    Args:
        icn: Patient ICN (Integrated Care Number)

    Returns:
        Dictionary with military history data, or None if not found

    Example:
        {
            'service_connected_flag': 'Y',
            'service_connected_percent': 70.0,
            'agent_orange_exposure': 'Y',
            'agent_orange_location': 'VIETNAM',
            'ionizing_radiation': 'N',
            'pow_status': 'N',
            'pow_location': None,
            'shad_flag': 'N',
            'sw_asia_exposure': 'Y',
            'camp_lejeune_flag': 'N',
        }
    """
    engine = create_engine(DATABASE_URL)

    query = text("""
        SELECT
            patient_key,
            icn,
            service_connected_flag,
            service_connected_percent,
            agent_orange_exposure,
            agent_orange_location,
            ionizing_radiation,
            pow_status,
            pow_location,
            shad_flag,
            sw_asia_exposure,
            camp_lejeune_flag,
            source_system,
            last_updated
        FROM clinical.patient_military_history
        WHERE icn = :icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"icn": icn}).fetchone()

        if not result:
            logger.debug(f"No military history found for patient ICN: {icn}")
            return None

        return {
            "patient_key": result[0],
            "icn": result[1],
            "service_connected_flag": result[2],
            "service_connected_percent": float(result[3]) if result[3] is not None else None,
            "agent_orange_exposure": result[4],
            "agent_orange_location": result[5],
            "ionizing_radiation": result[6],
            "pow_status": result[7],
            "pow_location": result[8],
            "shad_flag": result[9],
            "sw_asia_exposure": result[10],
            "camp_lejeune_flag": result[11],
            "source_system": result[12],
            "last_updated": result[13],
        }


def get_priority_group(service_connected_percent: Optional[float]) -> Dict[str, Any]:
    """
    Determine VA priority group based on service-connected percentage.

    Args:
        service_connected_percent: Service-connected disability percentage (0-100)

    Returns:
        Dictionary with priority group info

    Example:
        {
            'group': '1',
            'label': 'Priority Group 1',
            'badge_class': 'badge--danger',
            'description': 'High priority - 70%+ service connected'
        }
    """
    if service_connected_percent is None:
        return {
            'group': None,
            'label': None,
            'badge_class': None,
            'description': None
        }

    if service_connected_percent >= 70:
        return {
            'group': '1',
            'label': 'Priority Group 1',
            'badge_class': 'badge--danger',
            'description': 'High priority - 70%+ service connected'
        }
    elif service_connected_percent >= 50:
        return {
            'group': '2',
            'label': 'Priority Group 2',
            'badge_class': 'badge--warning',
            'description': 'Priority - 50-69% service connected'
        }
    elif service_connected_percent >= 30:
        return {
            'group': '3',
            'label': 'Priority Group 3',
            'badge_class': 'badge--info',
            'description': 'Standard - 30-49% service connected'
        }
    elif service_connected_percent >= 10:
        return {
            'group': '4-6',
            'label': 'Priority Group 4-6',
            'badge_class': 'badge--secondary',
            'description': 'Standard - 10-29% service connected'
        }
    else:
        return {
            'group': '7-8',
            'label': 'Priority Group 7-8',
            'badge_class': 'badge--secondary',
            'description': 'Standard eligibility'
        }
