"""
LangChain tools for AI Clinical Insights.

This module exports all available tools that the LangGraph agent can invoke
to access clinical data and perform analysis.

Usage:
    from ai.tools import ALL_TOOLS
    agent = create_insight_agent(ALL_TOOLS)

Available Tools:
    - check_ddi_risks: Analyze drug-drug interaction risks for a patient
    - get_patient_summary: Retrieve comprehensive patient clinical summary
    - analyze_vitals_trends: Analyze vital sign trends over time with statistical analysis
"""

from ai.tools.medication_tools import check_ddi_risks
from ai.tools.patient_tools import get_patient_summary
from ai.tools.vitals_tools import analyze_vitals_trends, set_request_context

# List of all available tools for the LangGraph agent
# Add new tools to this list as they are implemented
ALL_TOOLS = [
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
]

__all__ = [
    "check_ddi_risks",
    "get_patient_summary",
    "analyze_vitals_trends",
    "set_request_context",
    "ALL_TOOLS",
]
