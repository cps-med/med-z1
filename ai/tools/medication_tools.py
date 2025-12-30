"""
Medication-related LangChain tools for AI Clinical Insights.

Provides tools that the LangGraph agent can invoke to analyze patient
medications, including drug-drug interaction (DDI) risk assessment.

Design Reference: docs/spec/ai-insight-design.md Section 6.1
"""

import logging
from typing import Annotated

from langchain_core.tools import tool
from ai.services.ddi_analyzer import DDIAnalyzer

logger = logging.getLogger(__name__)


@tool
def check_ddi_risks(
    patient_icn: Annotated[str, "Patient ICN (Integrated Care Number)"]
) -> str:
    """
    Analyzes drug-drug interaction risks for a patient.

    Retrieves the patient's current medication list from PostgreSQL and
    checks all medication pairs against the DrugBank DDI reference database.
    Returns a formatted text summary of interactions suitable for LLM interpretation.

    This tool:
    1. Fetches patient medications from PostgreSQL (T-1, historical data)
    2. Analyzes all medication pairs using DDIAnalyzer
    3. Formats results as natural language summary
    4. Returns interaction descriptions without severity ranking (Phase 1 MVP)

    Args:
        patient_icn: Patient's Integrated Care Number (ICN)

    Returns:
        Formatted text summary of drug-drug interactions, or message if none found.
        Includes:
        - Total count of interactions
        - List of each interaction with drug names and description
        - Data source attribution

    Example output:
        "Found 2 drug-drug interactions:

        ⚠️ Warfarin + Ibuprofen
           The risk or severity of bleeding can be increased when Warfarin
           is combined with Ibuprofen

        ⚠️ Lisinopril + Potassium Chloride
           The risk or severity of hyperkalemia can be increased when Lisinopril
           is combined with Potassium supplements

        Data sources: 5 medications from PostgreSQL, ~191K interactions from DDI reference

        Note: All interactions shown. Severity ranking may be added in future phases."

    Design Reference: docs/spec/ai-insight-design.md Section 6.1
    """
    try:
        logger.info(f"Checking DDI risks for patient {patient_icn}")

        # Get patient medications from database layer
        from app.db.medications import get_patient_medications

        # Fetch medications (T-1 historical data)
        # Returns list of dicts with 'drug_name' key among others
        medications = get_patient_medications(patient_icn)

        if not medications:
            return f"No medications found for patient {patient_icn}. Unable to assess DDI risks."

        # Medications already returned as list of dicts with 'drug_name' key
        # No conversion needed - DDIAnalyzer expects this format
        med_list = medications

        # Analyze DDIs using DDIAnalyzer
        analyzer = DDIAnalyzer()
        interactions = analyzer.find_interactions(med_list)

        # Format for LLM
        if not interactions:
            return f"No drug-drug interactions found for this patient ({len(medications)} medications checked)."

        result = f"Found {len(interactions)} drug-drug interactions:\n\n"

        # List all interactions (Phase 1 MVP - no severity ranking)
        for i in interactions:
            result += f"⚠️ {i['drug_a']} + {i['drug_b']}\n"
            result += f"   {i['description']}\n\n"

        result += f"Data sources: {len(medications)} medications from PostgreSQL, ~191K interactions from DDI reference"
        result += f"\n\nNote: All interactions shown. Severity ranking may be added in future phases."

        logger.info(f"Found {len(interactions)} DDI risks for patient {patient_icn}")

        return result

    except Exception as e:
        error_msg = f"Error checking DDI risks for patient {patient_icn}: {str(e)}"
        logger.error(error_msg)
        return error_msg
