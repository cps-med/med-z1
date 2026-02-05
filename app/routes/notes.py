# ---------------------------------------------------------------------
# app/routes/notes.py
# ---------------------------------------------------------------------
# Clinical Notes API Routes and Pages
# Handles all clinical notes API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Union
import logging

from app.db.notes import (
    get_recent_notes,
    get_notes_summary,
    get_all_notes,
    get_note_detail,
    get_note_authors
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context

# API router for notes endpoints
router = APIRouter(prefix="/api/patient", tags=["notes"])

# Page router for full notes pages (no prefix for flexibility)
page_router = APIRouter(tags=["notes-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


@router.get("/{icn}/notes")
async def get_patient_notes_endpoint(
    icn: str,
    note_class: Optional[str] = Query('all'),
    date_range: Union[int, str, None] = Query(None),
    author: Optional[str] = None,
    status: Optional[str] = Query('all'),
    sort_by: Optional[str] = Query('reference_datetime'),
    sort_order: Optional[str] = Query('desc'),
    page: Optional[int] = Query(1, ge=1),
    per_page: Optional[int] = Query(20, ge=1, le=100)
):
    """
    Get all clinical notes for a patient with filtering, sorting, and pagination.

    Args:
        icn: Integrated Care Number
        note_class: Filter by document class ('all', 'Progress Notes', 'Consults', etc.)
        date_range: Filter by days (30, 90, 180, 365, None for all)
        author: Filter by author name
        status: Filter by status ('all', 'COMPLETED', 'UNSIGNED', etc.)
        sort_by: Column to sort by ('reference_datetime', 'document_class', 'author_name')
        sort_order: Sort order ('asc' or 'desc')
        page: Page number (1-based)
        per_page: Notes per page (1-100, default 20)

    Returns:
        JSON with list of clinical notes and pagination info
    """
    try:
        # Convert empty string to None for date_range
        if date_range == '' or date_range == 'all':
            date_range = None
        elif isinstance(date_range, str):
            try:
                date_range = int(date_range)
            except ValueError:
                date_range = None

        offset = (page - 1) * per_page

        result = get_all_notes(
            icn=icn,
            note_class=note_class,
            date_range=date_range,
            author=author,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=per_page,
            offset=offset
        )

        return {
            "patient_icn": icn,
            "notes": result["notes"],
            "pagination": result["pagination"],
            "filters": {
                "note_class": note_class,
                "date_range": date_range,
                "author": author,
                "status": status,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }

    except Exception as e:
        logger.error(f"Error fetching notes for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/notes/recent")
async def get_recent_notes_endpoint(icn: str):
    """
    Get the most recent clinical notes for a patient.
    Used for dashboard widget.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with recent notes and summary statistics
    """
    try:
        recent = get_recent_notes(icn, limit=4)
        summary = get_notes_summary(icn)

        return {
            "patient_icn": icn,
            "total_notes": summary["total_notes"],
            "notes_by_class": summary["notes_by_class"],
            "recent_notes": recent
        }

    except Exception as e:
        logger.error(f"Error fetching recent notes for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/notes/{note_id}")
async def get_note_detail_endpoint(icn: str, note_id: int):
    """
    Get full clinical note details including complete document text.

    Args:
        icn: Integrated Care Number
        note_id: Note ID

    Returns:
        JSON with complete note data including full document text
    """
    try:
        note = get_note_detail(icn, note_id)

        if not note:
            raise HTTPException(status_code=404, detail=f"Note {note_id} not found for patient {icn}")

        return {
            "patient_icn": icn,
            "note": note
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching note {note_id} for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/notes/authors/list")
async def get_note_authors_endpoint(icn: str):
    """
    Get list of unique note authors for a patient.
    Used for author filter dropdown.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with list of unique author names
    """
    try:
        authors = get_note_authors(icn)

        return {
            "patient_icn": icn,
            "authors": authors,
            "count": len(authors)
        }

    except Exception as e:
        logger.error(f"Error fetching note authors for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/notes/{icn}", response_class=HTMLResponse)
async def get_notes_widget(request: Request, icn: str):
    """
    Render clinical notes widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing recent clinical notes.

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for notes widget
    """
    try:
        # Get recent notes (3 for 2x1 compact widget)
        recent = get_recent_notes(icn, limit=3)

        # Get summary for header
        summary = get_notes_summary(icn)

        return templates.TemplateResponse(
            "partials/notes_widget.html",
            {
                "request": request,
                "icn": icn,
                "notes": recent,
                "total_notes": summary["total_notes"],
                "notes_by_class": summary["notes_by_class"],
                "has_notes": len(recent) > 0
            }
        )

    except Exception as e:
        logger.error(f"Error rendering notes widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/notes_widget.html",
            {
                "request": request,
                "icn": icn,
                "notes": [],
                "total_notes": 0,
                "notes_by_class": {},
                "has_notes": False,
                "error": str(e)
            }
        )


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/notes")
async def notes_redirect(request: Request):
    """
    Redirect to current patient's notes page.
    Gets patient from CCOW and redirects to /patient/{icn}/notes.
    If no patient selected, redirects to dashboard.
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for notes page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/patient/{patient_icn}/notes", status_code=303)


@page_router.get("/patient/{icn}/notes", response_class=HTMLResponse)
async def get_notes_page(
    request: Request,
    icn: str,
    note_class: Optional[str] = Query('all'),
    date_range: Union[int, str, None] = Query(90),  # Default 90 days
    author: Optional[str] = None,
    status: Optional[str] = Query('all'),
    sort_by: Optional[str] = Query('reference_datetime'),
    sort_order: Optional[str] = Query('desc'),
    page: Optional[int] = Query(1, ge=1),
    per_page: Optional[int] = Query(20, ge=1, le=100)
):
    """
    Full clinical notes page for a patient.

    Shows comprehensive table of all notes with filtering, sorting, and pagination.

    Args:
        icn: Patient ICN
        note_class: Filter by document class
        date_range: Filter by days (30, 90, 180, 365, None for all)
        author: Filter by author name
        status: Filter by status
        sort_by: Column to sort by
        sort_order: Sort order (asc or desc)
        page: Page number
        per_page: Notes per page

    Returns:
        Full HTML page with notes table
    """
    try:
        # Convert empty string to None for date_range
        if date_range == '' or date_range == 'all':
            date_range = None
        elif isinstance(date_range, str):
            try:
                date_range = int(date_range)
            except ValueError:
                date_range = None

        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found")
            return templates.TemplateResponse(
                "patient_notes.html",
                get_base_context(
                    request,
                    patient=None,
                    error="Patient not found"
                )
            )

        # Get notes with filters and pagination
        offset = (page - 1) * per_page

        result = get_all_notes(
            icn=icn,
            note_class=note_class,
            date_range=date_range,
            author=author,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=per_page,
            offset=offset
        )

        # Get available authors for filter dropdown
        authors = get_note_authors(icn)

        # Get summary for filter pills
        summary = get_notes_summary(icn)

        logger.info(
            f"Loaded notes page for {icn}: {len(result['notes'])} notes "
            f"(page {result['pagination']['current_page']}/{result['pagination']['total_pages']})"
        )

        return templates.TemplateResponse(
            "patient_notes.html",
            get_base_context(
                request,
                patient=patient,
                notes=result["notes"],
                total_count=result["pagination"]["total_count"],
                note_counts=summary["notes_by_class"],
                authors=authors,
                # Filter values
                note_class_filter=note_class,
                date_range_filter=date_range,
                author_filter=author,
                status_filter=status,
                # Sort values
                sort_by=sort_by,
                sort_order=sort_order,
                # Pagination values
                page=result["pagination"]["current_page"],
                total_pages=result["pagination"]["total_pages"],
                per_page=per_page,
                active_page="notes"
            )
        )

    except Exception as e:
        logger.error(f"Error loading notes page for {icn}: {e}")
        return templates.TemplateResponse(
            "patient_notes.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="notes"
            )
        )


@page_router.get("/patient/{icn}/notes/{note_id}/detail", response_class=HTMLResponse)
async def get_note_detail_partial(request: Request, icn: str, note_id: int):
    """
    Get note detail HTML partial for expandable row.
    Returns HTMX-compatible HTML with full note text.

    Args:
        icn: Patient ICN
        note_id: Note ID

    Returns:
        HTML partial with full note details
    """
    try:
        note = get_note_detail(icn, note_id)

        if not note:
            logger.warning(f"Note {note_id} not found for patient {icn}")
            return HTMLResponse(
                content="<div class='error'>Note not found</div>",
                status_code=404
            )

        return templates.TemplateResponse(
            "partials/note_detail.html",
            {
                "request": request,
                "icn": icn,
                "note": note
            }
        )

    except Exception as e:
        logger.error(f"Error loading note detail {note_id} for {icn}: {e}")
        return HTMLResponse(
            content=f"<div class='error'>Error loading note: {str(e)}</div>",
            status_code=500
        )
