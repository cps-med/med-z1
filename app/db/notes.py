# ---------------------------------------------------------------------
# app/db/notes.py
# ---------------------------------------------------------------------
# Clinical Notes Database Query Layer
# Provides functions to query patient_clinical_notes table in PostgreSQL
# This module encapsulates all SQL queries for clinical notes data
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


def get_recent_notes(
    icn: str,
    limit: int = 4
) -> List[Dict[str, Any]]:
    """
    Get the most recent clinical notes for a patient.
    Used for dashboard widget display.

    Args:
        icn: Integrated Care Number (patient_key)
        limit: Maximum number of notes to return (default 4)

    Returns:
        List of dictionaries with recent note data
    """
    query = text("""
        SELECT
            note_id,
            tiu_document_sid,
            document_title,
            document_class,
            vha_standard_title,
            reference_datetime,
            entry_datetime,
            author_name,
            facility_name,
            text_preview,
            text_length,
            status,
            days_since_note,
            note_age_category
        FROM clinical.patient_clinical_notes
        WHERE patient_key = :icn
          AND status = 'COMPLETED'  -- Exclude unsigned/retracted from widget
        ORDER BY reference_datetime DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn, "limit": limit}).fetchall()

            notes = []
            for row in results:
                notes.append({
                    "note_id": row[0],
                    "tiu_document_sid": row[1],
                    "document_title": row[2],
                    "document_class": row[3],
                    "vha_standard_title": row[4],
                    "reference_datetime": str(row[5]) if row[5] else None,
                    "entry_datetime": str(row[6]) if row[6] else None,
                    "author_name": row[7],
                    "facility_name": row[8],
                    "text_preview": row[9],
                    "text_length": row[10],
                    "status": row[11],
                    "days_since_note": row[12],
                    "note_age_category": row[13]
                })

            logger.info(f"Retrieved {len(notes)} recent notes for patient {icn}")
            return notes

    except Exception as e:
        logger.error(f"Error retrieving recent notes for {icn}: {e}")
        raise


def get_recent_notes_for_ai(
    icn: str,
    limit: int = 3,
    preview_length: int = 500
) -> List[Dict[str, Any]]:
    """
    Get recent clinical notes optimized for AI consumption.

    Similar to get_recent_notes() but with configurable preview length
    for AI context building. Separates UI concerns (200-char previews)
    from AI concerns (500-char previews for better clinical context).

    This function is used by:
    - PatientContextBuilder.get_notes_summary() for comprehensive patient summaries
    - AI tools that need more context than the UI text_preview provides

    Args:
        icn: Integrated Care Number (patient_key)
        limit: Number of notes to return (default 3 from config.AI_NOTES_SUMMARY_LIMIT)
        preview_length: Characters of note text to include (default 500 from config.AI_NOTES_PREVIEW_LENGTH)

    Returns:
        List of dictionaries with extended note preview text

    Example:
        >>> from config import AI_NOTES_SUMMARY_LIMIT, AI_NOTES_PREVIEW_LENGTH
        >>> notes = get_recent_notes_for_ai("ICN100001", limit=AI_NOTES_SUMMARY_LIMIT, preview_length=AI_NOTES_PREVIEW_LENGTH)
        >>> len(notes)
        3
        >>> len(notes[0]['text_preview'])  # Will be ~500 chars instead of 200
        487

    Design Notes:
        - 500 chars captures SOAP opening (Subjective, Objective, Assessment start)
        - ~125 tokens per note = 375 tokens for 3 notes (negligible cost)
        - Much cheaper than full text (~5000 tokens per note)
        - Provides sufficient clinical context for LLM analysis
    """
    query = text("""
        SELECT
            note_id,
            tiu_document_sid,
            document_title,
            document_class,
            vha_standard_title,
            reference_datetime,
            entry_datetime,
            author_name,
            facility_name,
            SUBSTRING(document_text, 1, :preview_length) as text_preview,
            text_length,
            status,
            days_since_note,
            note_age_category
        FROM clinical.patient_clinical_notes
        WHERE patient_key = :icn
          AND status = 'COMPLETED'  -- Exclude unsigned/retracted notes
        ORDER BY reference_datetime DESC
        LIMIT :limit
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(
                query,
                {"icn": icn, "limit": limit, "preview_length": preview_length}
            ).fetchall()

            notes = []
            for row in results:
                notes.append({
                    "note_id": row[0],
                    "tiu_document_sid": row[1],
                    "document_title": row[2],
                    "document_class": row[3],
                    "vha_standard_title": row[4],
                    "reference_datetime": str(row[5]) if row[5] else None,
                    "entry_datetime": str(row[6]) if row[6] else None,
                    "author_name": row[7],
                    "facility_name": row[8],
                    "text_preview": row[9],  # Extended preview (500 chars)
                    "text_length": row[10],
                    "status": row[11],
                    "days_since_note": row[12],
                    "note_age_category": row[13]
                })

            logger.info(
                f"Retrieved {len(notes)} recent notes for AI (patient {icn}, "
                f"preview_length={preview_length})"
            )
            return notes

    except Exception as e:
        logger.error(f"Error retrieving AI notes for {icn}: {e}")
        raise


def get_notes_summary(icn: str) -> Dict[str, Any]:
    """
    Get summary statistics for a patient's clinical notes.
    Used for widget header and filter pills.

    Args:
        icn: Integrated Care Number (patient_key)

    Returns:
        Dictionary with total count and counts by document class
    """
    query = text("""
        SELECT
            COUNT(*) as total_notes,
            document_class,
            COUNT(*) as class_count
        FROM clinical.patient_clinical_notes
        WHERE patient_key = :icn
        GROUP BY document_class
        ORDER BY document_class
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            total_notes = sum(row[2] for row in results)
            notes_by_class = {row[1]: row[2] for row in results}

            summary = {
                "total_notes": total_notes,
                "notes_by_class": notes_by_class
            }

            logger.info(f"Retrieved notes summary for patient {icn}: {total_notes} total notes")
            return summary

    except Exception as e:
        logger.error(f"Error retrieving notes summary for {icn}: {e}")
        raise


def get_all_notes(
    icn: str,
    note_class: str = 'all',
    date_range: Optional[int] = None,
    author: Optional[str] = None,
    status: str = 'all',
    sort_by: str = 'reference_datetime',
    sort_order: str = 'desc',
    limit: int = 20,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Get all clinical notes for a patient with filtering, sorting, and pagination.
    Used for full notes page view.

    Args:
        icn: Integrated Care Number (patient_key)
        note_class: Filter by document class ('all', 'Progress Notes', 'Consults', etc.)
        date_range: Filter by days (e.g., 30, 90, 180, 365, None for all)
        author: Filter by author name
        status: Filter by status ('all', 'COMPLETED', 'UNSIGNED', etc.)
        sort_by: Column to sort by ('reference_datetime', 'document_class', 'author_name')
        sort_order: Sort order ('asc' or 'desc')
        limit: Number of notes per page
        offset: Pagination offset

    Returns:
        Dictionary with notes list and pagination info
    """
    # Build WHERE clause with filters
    where_conditions = ["patient_key = :icn"]
    params = {"icn": icn, "limit": limit, "offset": offset}

    if note_class != 'all':
        where_conditions.append("document_class = :note_class")
        params["note_class"] = note_class

    if date_range:
        where_conditions.append("reference_datetime >= NOW() - INTERVAL :date_range DAY")
        params["date_range"] = str(date_range)

    if author:
        where_conditions.append("author_name = :author")
        params["author"] = author

    if status != 'all':
        where_conditions.append("status = :status")
        params["status"] = status

    where_clause = " AND ".join(where_conditions)

    # Build ORDER BY clause
    sort_column_map = {
        'reference_datetime': 'reference_datetime',
        'document_class': 'document_class',
        'author_name': 'author_name',
        'document_title': 'document_title'
    }
    sort_column = sort_column_map.get(sort_by, 'reference_datetime')
    order_direction = 'ASC' if sort_order == 'asc' else 'DESC'

    # Query for notes with filters
    query = text(f"""
        SELECT
            note_id,
            tiu_document_sid,
            document_title,
            document_class,
            vha_standard_title,
            reference_datetime,
            entry_datetime,
            status,
            author_name,
            cosigner_name,
            facility_name,
            sta3n,
            text_preview,
            text_length,
            days_since_note,
            note_age_category
        FROM clinical.patient_clinical_notes
        WHERE {where_clause}
        ORDER BY {sort_column} {order_direction}
        LIMIT :limit OFFSET :offset
    """)

    # Query for total count (without pagination)
    count_query = text(f"""
        SELECT COUNT(*)
        FROM clinical.patient_clinical_notes
        WHERE {where_clause}
    """)

    try:
        with engine.connect() as conn:
            # Get total count for pagination
            total_count = conn.execute(count_query, {k: v for k, v in params.items() if k not in ['limit', 'offset']}).scalar()

            # Get notes page
            results = conn.execute(query, params).fetchall()

            notes = []
            for row in results:
                notes.append({
                    "note_id": row[0],
                    "tiu_document_sid": row[1],
                    "document_title": row[2],
                    "document_class": row[3],
                    "vha_standard_title": row[4],
                    "reference_datetime": str(row[5]) if row[5] else None,
                    "entry_datetime": str(row[6]) if row[6] else None,
                    "status": row[7],
                    "author_name": row[8],
                    "cosigner_name": row[9],
                    "facility_name": row[10],
                    "sta3n": row[11],
                    "text_preview": row[12],
                    "text_length": row[13],
                    "days_since_note": row[14],
                    "note_age_category": row[15]
                })

            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
            current_page = (offset // limit) + 1

            result = {
                "notes": notes,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "current_page": current_page,
                    "per_page": limit,
                    "has_next": current_page < total_pages,
                    "has_prev": current_page > 1
                }
            }

            logger.info(
                f"Retrieved {len(notes)} notes for patient {icn} "
                f"(page {current_page}/{total_pages}, total {total_count})"
            )
            return result

    except Exception as e:
        logger.error(f"Error retrieving notes for {icn}: {e}")
        raise


def get_note_detail(icn: str, note_id: int) -> Optional[Dict[str, Any]]:
    """
    Get full clinical note details including complete document text.
    Used for expandable row display.

    Args:
        icn: Integrated Care Number (patient_key)
        note_id: Note ID (primary key)

    Returns:
        Dictionary with complete note data, or None if not found
    """
    query = text("""
        SELECT
            note_id,
            tiu_document_sid,
            document_title,
            document_class,
            vha_standard_title,
            reference_datetime,
            entry_datetime,
            status,
            author_name,
            author_sid,
            cosigner_name,
            cosigner_sid,
            visit_sid,
            facility_name,
            sta3n,
            document_text,
            text_length,
            text_preview,
            days_since_note,
            note_age_category,
            tiu_document_ien,
            source_system
        FROM clinical.patient_clinical_notes
        WHERE patient_key = :icn
          AND note_id = :note_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"icn": icn, "note_id": note_id}).fetchone()

            if not result:
                logger.warning(f"Note {note_id} not found for patient {icn}")
                return None

            note = {
                "note_id": result[0],
                "tiu_document_sid": result[1],
                "document_title": result[2],
                "document_class": result[3],
                "vha_standard_title": result[4],
                "reference_datetime": str(result[5]) if result[5] else None,
                "entry_datetime": str(result[6]) if result[6] else None,
                "status": result[7],
                "author_name": result[8],
                "author_sid": result[9],
                "cosigner_name": result[10],
                "cosigner_sid": result[11],
                "visit_sid": result[12],
                "facility_name": result[13],
                "sta3n": result[14],
                "document_text": result[15],
                "text_length": result[16],
                "text_preview": result[17],
                "days_since_note": result[18],
                "note_age_category": result[19],
                "tiu_document_ien": result[20],
                "source_system": result[21]
            }

            logger.info(f"Retrieved full note {note_id} for patient {icn}")
            return note

    except Exception as e:
        logger.error(f"Error retrieving note {note_id} for {icn}: {e}")
        raise


def get_note_authors(icn: str) -> List[str]:
    """
    Get list of unique note authors for a patient.
    Used for author filter dropdown.

    Args:
        icn: Integrated Care Number (patient_key)

    Returns:
        List of unique author names, sorted alphabetically
    """
    query = text("""
        SELECT DISTINCT author_name
        FROM clinical.patient_clinical_notes
        WHERE patient_key = :icn
          AND author_name IS NOT NULL
        ORDER BY author_name
    """)

    try:
        with engine.connect() as conn:
            results = conn.execute(query, {"icn": icn}).fetchall()

            authors = [row[0] for row in results]

            logger.info(f"Retrieved {len(authors)} unique authors for patient {icn}")
            return authors

    except Exception as e:
        logger.error(f"Error retrieving authors for {icn}: {e}")
        raise
