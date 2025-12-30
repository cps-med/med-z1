# ---------------------------------------------------------------------
# ai/tools/vitals_tools.py
# ---------------------------------------------------------------------
# LangChain Tools for Vitals Analysis
# Provides tools for analyzing vital sign trends over time
# Supports Vista data caching via request context
# ---------------------------------------------------------------------

from langchain_core.tools import tool
from ai.services.vitals_trend_analyzer import VitalsTrendAnalyzer
from typing import Optional, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)

# Thread-local storage for request context
_current_request: Optional["Request"] = None


def set_request_context(request: Optional["Request"]) -> None:
    """
    Set the current request context for tools to access.

    This enables tools to access cached Vista data from the user's session.
    Should be called by route handlers before invoking the agent.

    Args:
        request: FastAPI request object (or None to clear)
    """
    global _current_request
    _current_request = request


@tool
def analyze_vitals_trends(patient_icn: str, days: int = 90) -> str:
    """
    Analyzes vital sign trends over a specified time period.

    This tool identifies concerning patterns in blood pressure, heart rate,
    temperature, and weight measurements. It compares values against clinical
    norms and calculates statistical trends using linear regression.

    Use this tool when the user asks about:
    - Vital sign trends or patterns
    - Changes in blood pressure, heart rate, temperature, or weight over time
    - Concerning trends or abnormal vital signs
    - Whether vitals are improving or worsening

    Args:
        patient_icn: Patient's Integrated Care Number
        days: Number of days to analyze (default 90)

    Returns:
        Formatted text summary of vital sign trends with clinical interpretation.
        Includes status indicators (✅ normal, ⚠️ concerning) and specific recommendations.
    """
    logger.info(f"Tool invoked: analyze_vitals_trends for patient {patient_icn}, days={days}")

    try:
        # Initialize analyzer with request context (for Vista cache access)
        analyzer = VitalsTrendAnalyzer(patient_icn=patient_icn, request=_current_request)

        # Perform analysis (will use cached Vista data if available)
        trends = analyzer.analyze_trends(days=days)

        # Check for errors
        if 'error' in trends:
            return f"Unable to analyze vital trends: {trends['error']}"

        # Format results for LLM
        result = f"**VITAL SIGN TREND ANALYSIS (Last {trends['period_days']} Days)**\n\n"
        result += f"Period: {trends['date_range']}\n"
        result += f"Total readings: {trends['total_readings']}\n\n"

        # Blood Pressure
        if 'bp' in trends:
            bp = trends['bp']
            status_icon = "✅" if bp['status'] == 'normal' else "⚠️"
            result += f"{status_icon} **BLOOD PRESSURE** ({bp['reading_count']} readings)\n"
            result += f"   Average: {bp['avg_systolic']}/{bp['avg_diastolic']} mmHg\n"
            result += f"   Trend: {bp['trend_description']}\n"
            result += f"   Interpretation: {bp['interpretation']}\n"
            result += f"   Clinical Note: {bp['clinical_note']}\n"
            result += f"   First reading: {bp['first_reading']} mmHg → Last reading: {bp['last_reading']} mmHg\n\n"

        # Heart Rate
        if 'hr' in trends:
            hr = trends['hr']
            status_icon = "✅" if hr['status'] == 'normal' else "⚠️"
            result += f"{status_icon} **HEART RATE** ({hr['reading_count']} readings)\n"
            result += f"   Average: {hr['avg']} bpm\n"
            result += f"   Trend: {hr['trend_description']}\n"
            result += f"   Interpretation: {hr['interpretation']}\n"
            result += f"   Clinical Note: {hr['clinical_note']}\n"
            result += f"   First reading: {hr['first_reading']} bpm → Last reading: {hr['last_reading']} bpm\n\n"

        # Temperature
        if 'temp' in trends:
            temp = trends['temp']
            status_icon = "✅" if temp['status'] == 'normal' else "⚠️"
            result += f"{status_icon} **TEMPERATURE** ({temp['reading_count']} readings)\n"
            result += f"   Average: {temp['avg']}°F (Max: {temp['max']}°F)\n"
            result += f"   Febrile episodes: {temp['febrile_count']}\n"
            result += f"   Interpretation: {temp['interpretation']}\n"
            result += f"   Clinical Note: {temp['clinical_note']}\n\n"

        # Weight
        if 'weight' in trends:
            weight = trends['weight']
            status_icon = "✅" if weight['status'] == 'normal' else "⚠️"
            result += f"{status_icon} **WEIGHT** ({weight['reading_count']} readings)\n"
            result += f"   Average: {weight['avg']} lbs\n"
            result += f"   Change: {weight['change']} lbs ({weight['percent_change']}%)\n"
            result += f"   Interpretation: {weight['interpretation']}\n"
            result += f"   Clinical Note: {weight['clinical_note']}\n"
            result += f"   First: {weight['first_weight']} lbs → Last: {weight['last_weight']} lbs\n\n"

        # Data source attribution
        result += f"---\n"
        result += f"**Data source:** {trends.get('data_source', 'PostgreSQL')} ({trends['total_readings']} readings over {trends['period_days']} days)\n"
        result += f"**Analysis method:** Linear regression for trends, comparison against clinical guidelines"

        return result

    except Exception as e:
        logger.error(f"Error in analyze_vitals_trends tool for patient {patient_icn}: {e}", exc_info=True)
        return f"Error analyzing vital trends: {str(e)}"
