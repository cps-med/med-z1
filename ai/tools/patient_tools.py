"""
Patient Clinical Summary Tools

LangChain tools for retrieving comprehensive patient clinical summaries.

These tools wrap the PatientContextBuilder service to provide natural language
summaries of patient data across all clinical domains.

Design Reference: docs/spec/ai-insight-design.md Section 6.2

Implementation Note:
- Uses synchronous functions (matching existing app/db pattern)
- No database session parameter needed (app/db functions handle connections)
"""

from typing import Annotated
from langchain_core.tools import tool
import logging

from ai.services.patient_context import PatientContextBuilder

logger = logging.getLogger(__name__)


@tool
def get_patient_summary(
    patient_icn: Annotated[str, "Patient ICN (Integrated Care Number)"]
) -> str:
    """
    Retrieve comprehensive patient clinical summary.

    Provides a multi-section overview including demographics, medications,
    vitals, allergies, and recent encounters. Returns formatted text
    suitable for natural language analysis.

    Args:
        patient_icn: Patient ICN (Integrated Care Number)

    Returns:
        Formatted text summary with all clinical domains

    Example:
        >>> summary = get_patient_summary("ICN100010")
        >>> print(summary)
        "PATIENT DEMOGRAPHICS
         45-year-old male veteran...

         CURRENT MEDICATIONS
         Currently on 7 active medications...

         RECENT VITALS
         Latest reading (2025-12-28)...

         ALLERGIES
         Known allergies...

         RECENT ENCOUNTERS
         Recent encounters...

         Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters)"
    """
    logger.info(f"get_patient_summary tool invoked for patient {patient_icn}")

    try:
        # Create context builder
        builder = PatientContextBuilder(patient_icn)

        # Build comprehensive summary
        summary = builder.build_comprehensive_summary()

        logger.info(f"Patient summary generated for {patient_icn} ({len(summary)} characters)")

        return summary

    except Exception as e:
        logger.error(f"Error generating patient summary for {patient_icn}: {e}", exc_info=True)
        return f"Error retrieving patient summary: {str(e)}"
