"""
Family History tools for AI Clinical Insights.

Provides targeted retrieval of structured family-history findings with
first-degree/high-risk emphasis for clinical risk context.
"""

from typing import Annotated, Optional
import logging

from langchain_core.tools import tool

from app.db.patient_family_history import (
    get_patient_family_history,
    get_family_history_counts,
)

logger = logging.getLogger(__name__)


@tool
def get_family_history(
    patient_icn: Annotated[str, "Patient ICN (Integrated Care Number)"],
    relationship: Annotated[
        Optional[str],
        "Optional relationship filter (for example: mother, father, sibling)",
    ] = None,
    category: Annotated[
        Optional[str],
        "Optional condition category filter (for example: Cardio, Cancer, Metabolic)",
    ] = None,
    active_only: Annotated[
        bool,
        "If true, return active findings only (default true)",
    ] = True,
) -> str:
    """
    Retrieve structured family-history findings for a patient.

    Use this tool for targeted family-history questions such as:
    - "Any first-degree cardiac family history?"
    - "Family history of diabetes or cancer?"
    - "What family history risk factors are documented?"

    Returns a concise summary with first-degree callouts and source attribution.
    """
    logger.info(
        "get_family_history tool invoked: patient=%s, relationship=%s, category=%s, active_only=%s",
        patient_icn,
        relationship,
        category,
        active_only,
    )

    try:
        rows = get_patient_family_history(
            patient_icn,
            relationship=relationship,
            category=category,
            active_only=active_only,
        )
        counts = get_family_history_counts(patient_icn)

        if not rows:
            filter_bits = []
            if relationship:
                filter_bits.append(f"relationship='{relationship}'")
            if category:
                filter_bits.append(f"category='{category}'")
            if active_only:
                filter_bits.append("active_only=true")
            filter_text = ", ".join(filter_bits) if filter_bits else "no filters"
            return f"No family history findings found ({filter_text})."

        output = []
        output.append("**Family History Summary**")
        output.append(
            f"Total: {counts.get('total', 0)} | Active: {counts.get('active', 0)} | "
            f"First-degree: {counts.get('first_degree', 0)} | "
            f"First-degree high-risk: {counts.get('first_degree_high_risk', 0)}"
        )

        # Prioritize first-degree findings in the output.
        first_degree_rows = [r for r in rows if r.get("first_degree_relative_flag")]
        other_rows = [r for r in rows if not r.get("first_degree_relative_flag")]
        first_degree_rows.sort(key=lambda r: r.get("recorded_datetime") or "", reverse=True)
        other_rows.sort(key=lambda r: r.get("recorded_datetime") or "", reverse=True)
        prioritized = first_degree_rows + other_rows

        output.append("")
        output.append("Findings:")
        for idx, row in enumerate(prioritized[:12], start=1):
            relationship_name = row.get("relationship_name") or "Relative"
            condition = row.get("condition_name") or "Unknown condition"
            category_name = row.get("condition_category") or row.get("risk_condition_group") or "Other"
            status = row.get("clinical_status") or "UNKNOWN"
            recorded = row.get("recorded_datetime")
            recorded_date = recorded[:10] if isinstance(recorded, str) else "unknown date"
            source = row.get("source_system") or "UNKNOWN"

            flags = []
            if row.get("first_degree_relative_flag"):
                flags.append("FIRST-DEGREE")
            if row.get("hereditary_risk_flag"):
                flags.append("HEREDITARY-RISK")
            flag_text = f" [{' | '.join(flags)}]" if flags else ""

            output.append(
                f"{idx}. {relationship_name} - {condition} "
                f"({category_name}, status: {status}, recorded: {recorded_date}, source: {source}){flag_text}"
            )

        if len(rows) > 12:
            output.append(f"... and {len(rows) - 12} more findings")

        if counts.get("first_degree", 0) > 0:
            output.append("")
            output.append(
                "First-degree findings are present and should be considered in risk context "
                "(supportive context, not diagnostic)."
            )

        output.append("Data source: PostgreSQL clinical.patient_family_history")
        return "\n".join(output)

    except Exception as exc:
        logger.error("Error retrieving family history for %s: %s", patient_icn, exc, exc_info=True)
        return f"Error retrieving family history: {str(exc)}"
