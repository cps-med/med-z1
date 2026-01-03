"""
Clinical Notes Tools for AI Insights

LangChain tools for retrieving and analyzing clinical notes with filtering capabilities.

These tools enable the AI agent to answer note-specific queries like:
- "What did the cardiology consult recommend?"
- "Show me recent progress notes"
- "What imaging studies were done in the last 6 months?"

Design Reference: docs/spec/ai-insight-design.md Section 6.5, Phase 4
"""

from typing import Annotated, Optional
from langchain_core.tools import tool
import logging

from app.db.notes import get_all_notes

logger = logging.getLogger(__name__)


@tool
def get_clinical_notes_summary(
    patient_icn: Annotated[str, "Patient ICN (Integrated Care Number)"],
    note_type: Annotated[
        Optional[str],
        "Note type filter: 'all', 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging Reports'"
    ] = None,
    days: Annotated[
        Optional[int],
        "Number of days to look back (default 90, common: 30, 180, 365)"
    ] = None,
    limit: Annotated[
        Optional[int],
        "Maximum number of notes to return (default 5, max 10)"
    ] = None
) -> str:
    """
    Retrieve recent clinical notes for a patient with optional filtering.

    Provides narrative clinical context including SOAP documentation,
    consultant recommendations, discharge summaries, and imaging reports.

    This tool is designed for targeted note queries where the user asks
    specific questions about clinical documentation. For general patient
    overview, use get_patient_summary() which includes recent notes automatically.

    Args:
        patient_icn: Patient ICN (Integrated Care Number)
        note_type: Optional filter by note class:
                   - 'all' (default): All note types
                   - 'Progress Notes': Clinical progress notes (SOAP format)
                   - 'Consults': Specialist consultation reports
                   - 'Discharge Summaries': Hospital discharge documentation
                   - 'Imaging Reports': Radiology and imaging results
        days: Number of days to look back (default from config: 90)
        limit: Maximum notes to return (default 5, capped at config max: 10)

    Returns:
        Formatted string with note summaries including type, date, author, facility, and preview text

    Example Queries Enabled:
        - "What did the last cardiology consult recommend?"
        - "Summarize the discharge summary from November"
        - "What imaging studies were done in the last 6 months?"
        - "Has the patient seen a specialist recently?"
        - "Show me progress notes from the last month"

    Performance Notes:
        - Default limit of 5 notes balances context richness vs token usage
        - Max limit of 10 notes (~1,250 tokens) to stay within context window
        - Text preview (500 chars) captures SOAP opening for clinical context
        - Query time: <200ms for filtered note retrieval
    """
    from config import AI_NOTES_QUERY_DAYS, AI_NOTES_MAX_LIMIT, AI_NOTES_PREVIEW_LENGTH

    # Apply defaults and caps from config
    days_param = days if days is not None else AI_NOTES_QUERY_DAYS
    limit_param = min(limit if limit is not None else 5, AI_NOTES_MAX_LIMIT)
    note_type_param = note_type if note_type else 'all'

    logger.info(
        f"get_clinical_notes_summary invoked: patient={patient_icn}, "
        f"note_type={note_type_param}, days={days_param}, limit={limit_param}"
    )

    try:
        # Query notes with filters using existing database function
        result = get_all_notes(
            icn=patient_icn,
            note_class=note_type_param,
            date_range=days_param,
            limit=limit_param,
            offset=0
        )

        notes = result.get("notes", [])
        pagination = result.get("pagination", {})
        total_count = pagination.get("total_count", 0)

        if not notes:
            return f"No clinical notes found for this patient in the last {days_param} days{' of type ' + note_type_param if note_type_param != 'all' else ''}."

        # Format notes for LLM consumption
        note_type_display = f" ({note_type_param})" if note_type_param != 'all' else ""
        output = f"**Clinical Notes Summary (Last {days_param} days{note_type_display})**\n"
        output += f"Found {len(notes)} note(s) (Total matching: {total_count})\n\n"

        for idx, note in enumerate(notes, 1):
            # Date and note type
            note_date = note.get('reference_datetime', 'unknown date')
            if note_date and ' ' in note_date:
                # Extract date part from datetime string
                note_date = note_date.split(' ')[0]

            note_class = note.get('document_class', 'Clinical Note')
            note_title = note.get('document_title', 'Untitled')

            output += f"{idx}. **{note_date} - {note_class}**\n"

            # Document title (often more specific than class)
            if note_title and note_title != note_class:
                output += f"   - Title: {note_title}\n"

            # Author
            author = note.get('author_name')
            if author:
                output += f"   - Author: {author}\n"

            # Cosigner (if different from author)
            cosigner = note.get('cosigner_name')
            if cosigner and cosigner != author:
                output += f"   - Cosigner: {cosigner}\n"

            # Facility
            facility = note.get('facility_name')
            if facility:
                output += f"   - Facility: {facility}\n"

            # Status (if not completed)
            status = note.get('status', 'COMPLETED')
            if status != 'COMPLETED':
                output += f"   - Status: {status}\n"

            # Preview text (500 chars, captures SOAP opening)
            preview = note.get('text_preview')
            if preview:
                # Clean up preview text (normalize whitespace)
                preview_clean = ' '.join(preview.split())
                # Truncate if needed and add ellipsis
                if len(preview_clean) > AI_NOTES_PREVIEW_LENGTH:
                    preview_clean = preview_clean[:AI_NOTES_PREVIEW_LENGTH - 3] + "..."
                output += f"   - Preview: {preview_clean}\n"
            else:
                output += f"   - Preview: (No text available)\n"

            output += "\n"

        # Add context about data completeness
        if total_count > len(notes):
            output += f"**Note:** Showing {len(notes)} of {total_count} total matching notes. "
            output += f"Use more specific filters or shorter date ranges to see different notes.\n\n"

        output += f"**Data source:** PostgreSQL clinical.patient_clinical_notes table\n"
        output += f"**Query parameters:** note_type={note_type_param}, days={days_param}, limit={limit_param}"

        logger.info(
            f"Clinical notes summary generated: {len(notes)} notes, "
            f"{len(output)} chars, patient={patient_icn}"
        )

        return output

    except Exception as e:
        logger.error(
            f"Error retrieving clinical notes for {patient_icn}: {e}",
            exc_info=True
        )
        return f"Error retrieving clinical notes: {str(e)}"
