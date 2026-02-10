# ---------------------------------------------------------------------
# app/routes/tasks.py
# ---------------------------------------------------------------------
# Clinical Task Tracking API Routes and Pages
# Handles all patient task API endpoints, widget rendering, and full pages.
# Returns JSON for API consumers, HTML partials for HTMX widgets, and full pages.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging

from app.db.patient_tasks import (
    get_patient_tasks,
    get_task_by_id,
    create_task,
    update_task_status,
    complete_task,
    update_task,
    delete_task,
    get_task_summary
)
from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context
from app.utils.ccow_client import ccow_client

# API router for tasks endpoints
router = APIRouter(prefix="/api/patient", tags=["tasks"])

# Page router for full task pages (no prefix for flexibility)
page_router = APIRouter(tags=["tasks-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)


# ============================================================================
# API ROUTER ENDPOINTS (JSON + HTML Widgets)
# ============================================================================

@router.get("/{icn}/tasks")
async def get_patient_tasks_endpoint(
    icn: str,
    status: Optional[str] = Query(None, description="Filter by status (active, TODO, IN_PROGRESS, COMPLETED)"),
    created_by: Optional[str] = Query(None, description="Filter by creator user_id"),
    priority: Optional[str] = Query(None, description="Filter by priority (HIGH, MEDIUM, LOW)"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Max tasks to return")
):
    """
    Get all tasks for a patient with optional filtering.

    Args:
        icn: Integrated Care Number
        status: Optional filter (active=TODO+IN_PROGRESS, TODO, IN_PROGRESS, COMPLETED)
        created_by: Optional filter by creator user_id
        priority: Optional filter by priority (HIGH, MEDIUM, LOW)
        limit: Maximum number of tasks to return

    Returns:
        JSON with list of patient tasks
    """
    try:
        tasks = get_patient_tasks(
            patient_icn=icn,
            status=status,
            created_by_user_id=created_by,
            priority=priority,
            limit=limit
        )

        return {
            "patient_icn": icn,
            "count": len(tasks),
            "filters": {
                "status": status,
                "created_by": created_by,
                "priority": priority,
                "limit": limit
            },
            "tasks": tasks
        }

    except Exception as e:
        logger.error(f"Error fetching tasks for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{icn}/tasks/summary")
async def get_tasks_summary_endpoint(icn: str):
    """
    Get task summary statistics for a patient.

    Returns counts for todo, in_progress, completed_today, ai_generated tasks.

    Args:
        icn: Integrated Care Number

    Returns:
        JSON with summary statistics
    """
    try:
        summary = get_task_summary(icn)

        return {
            "patient_icn": icn,
            **summary
        }

    except Exception as e:
        logger.error(f"Error fetching task summary for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{icn}/tasks")
async def create_task_endpoint(
    request: Request,
    icn: str,
    title: str = Form(..., max_length=500),
    description: Optional[str] = Form(None),
    priority: str = Form("MEDIUM"),
    is_ai_generated: bool = Form(False),
    ai_suggestion_source: Optional[str] = Form(None)
):
    """
    Create a new task for a patient.

    Args:
        icn: Integrated Care Number
        title: Task title (required, max 500 chars)
        description: Optional detailed description
        priority: Task priority (HIGH, MEDIUM, LOW), default MEDIUM
        is_ai_generated: True if created via AI Insights
        ai_suggestion_source: AI reasoning (if is_ai_generated=True)

    Returns:
        JSON with created task_id
    """
    try:
        # Get user from session (injected by AuthMiddleware)
        user = request.state.user

        # Validate priority
        if priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise HTTPException(status_code=400, detail="Invalid priority. Must be HIGH, MEDIUM, or LOW")

        # Create task
        task_id = create_task(
            patient_icn=icn,
            title=title,
            description=description,
            priority=priority,
            created_by_user_id=user["user_id"],
            created_by_display_name=user["display_name"],
            is_ai_generated=is_ai_generated,
            ai_suggestion_source=ai_suggestion_source
        )

        if not task_id:
            raise HTTPException(status_code=500, detail="Failed to create task")

        logger.info(f"Created task {task_id} for patient {icn} by {user['display_name']}")

        return {
            "success": True,
            "task_id": task_id,
            "patient_icn": icn
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/start")
async def start_task_endpoint(request: Request, task_id: int):
    """
    Update task status from TODO to IN_PROGRESS.

    Args:
        task_id: Task identifier

    Returns:
        JSON with updated task
    """
    try:
        # Update status
        success = update_task_status(task_id, "IN_PROGRESS")

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        # Get updated task
        task = get_task_by_id(task_id)

        logger.info(f"Started task {task_id}")

        return {
            "success": True,
            "task": task
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/complete")
async def complete_task_endpoint(request: Request, task_id: int):
    """
    Mark task as COMPLETED and populate audit fields.

    Args:
        task_id: Task identifier

    Returns:
        JSON with completed task
    """
    try:
        # Get user from session
        user = request.state.user

        # Complete task
        success = complete_task(
            task_id=task_id,
            completed_by_user_id=user["user_id"],
            completed_by_display_name=user["display_name"]
        )

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        # Get updated task
        task = get_task_by_id(task_id)

        logger.info(f"Completed task {task_id} by {user['display_name']}")

        return {
            "success": True,
            "task": task
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/revert-to-todo")
async def revert_task_to_todo_endpoint(request: Request, task_id: int):
    """
    Revert task from IN_PROGRESS back to TODO.

    Args:
        task_id: Task identifier

    Returns:
        JSON with reverted task
    """
    try:
        # Update status
        success = update_task_status(task_id, "TODO")

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        # Get updated task
        task = get_task_by_id(task_id)

        logger.info(f"Reverted task {task_id} to TODO")

        return {
            "success": True,
            "task": task
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reverting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}")
async def update_task_endpoint(
    request: Request,
    task_id: int,
    title: Optional[str] = Form(None, max_length=500),
    description: Optional[str] = Form(None),
    priority: Optional[str] = Form(None)
):
    """
    Update task details (title, description, priority).

    Only updates fields that are provided (not None).

    Args:
        task_id: Task identifier
        title: New title (optional)
        description: New description (optional)
        priority: New priority (HIGH, MEDIUM, LOW) (optional)

    Returns:
        JSON with updated task
    """
    try:
        # Validate priority if provided
        if priority and priority not in ["HIGH", "MEDIUM", "LOW"]:
            raise HTTPException(status_code=400, detail="Invalid priority. Must be HIGH, MEDIUM, or LOW")

        # Update task
        success = update_task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority
        )

        if not success:
            raise HTTPException(status_code=404, detail="Task not found or no fields to update")

        # Get updated task
        task = get_task_by_id(task_id)

        logger.info(f"Updated task {task_id}")

        return {
            "success": True,
            "task": task
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tasks/{task_id}")
async def delete_task_endpoint(request: Request, task_id: int):
    """
    Delete task (hard delete from database).

    Args:
        task_id: Task identifier

    Returns:
        JSON with success status
    """
    try:
        success = delete_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        logger.info(f"Deleted task {task_id}")

        return {
            "success": True,
            "task_id": task_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/widget/tasks/{icn}", response_class=HTMLResponse)
async def get_tasks_widget(request: Request, icn: str):
    """
    Render tasks widget HTML partial for dashboard.
    Returns HTMX-compatible HTML showing active tasks.

    Widget shows:
    - Task count badge
    - 5-8 most urgent tasks (TODO + IN_PROGRESS, sorted by priority)
    - Quick actions: Start, Complete, Revert
    - Quick create button

    Args:
        icn: Integrated Care Number

    Returns:
        HTML partial for tasks widget
    """
    try:
        # Get active tasks (TODO + IN_PROGRESS), limit to 8 for widget
        tasks = get_patient_tasks(
            patient_icn=icn,
            status="active",
            limit=8
        )

        # Get summary for badge count
        summary = get_task_summary(icn)
        task_count = summary["todo_count"] + summary["in_progress_count"]

        return templates.TemplateResponse(
            "partials/tasks_widget.html",
            {
                "request": request,
                "patient_icn": icn,
                "tasks": tasks,
                "task_count": task_count,
                "has_tasks": len(tasks) > 0,
                "error": False
            }
        )

    except Exception as e:
        logger.error(f"Error rendering tasks widget for {icn}: {e}")
        # Return error state widget
        return templates.TemplateResponse(
            "partials/tasks_widget.html",
            {
                "request": request,
                "patient_icn": icn,
                "tasks": [],
                "task_count": 0,
                "has_tasks": False,
                "error": True
            }
        )


# ============================================================================
# MODAL ENDPOINTS (HTMX Modal HTML)
# ============================================================================

@router.get("/tasks/quick-create-modal", response_class=HTMLResponse)
async def get_quick_create_modal(
    request: Request,
    icn: str = Query(..., description="Patient ICN")
):
    """
    Render quick create task modal HTML.

    Args:
        icn: Integrated Care Number for the patient

    Returns:
        HTML modal partial
    """
    try:
        context = {
            "request": request,
            "patient_icn": icn
        }

        return templates.TemplateResponse("partials/task_create_modal.html", context)

    except Exception as e:
        logger.error(f"Error rendering quick create modal for {icn}: {e}")
        return HTMLResponse(content="<p>Error loading modal</p>", status_code=500)


@router.post("/tasks/{icn}/create", response_class=HTMLResponse)
async def create_task_modal_submit(
    request: Request,
    icn: str,
    title: str = Form(..., max_length=500),
    description: Optional[str] = Form(None),
    priority: str = Form("MEDIUM"),
    is_ai_generated: bool = Form(False),
    ai_suggestion_source: Optional[str] = Form(None)
):
    """
    Create a new task from modal form submission.

    Returns success HTML to close modal and refresh task list.
    """
    try:
        # Get user from session
        user = request.state.user

        # Validate priority
        if priority not in ["HIGH", "MEDIUM", "LOW"]:
            return HTMLResponse(
                content=f'<div class="alert alert--danger">Invalid priority. Must be HIGH, MEDIUM, or LOW</div>',
                status_code=400
            )

        # Create task
        task_id = create_task(
            patient_icn=icn,
            title=title,
            description=description,
            priority=priority,
            created_by_user_id=user["user_id"],
            created_by_display_name=user["display_name"],
            is_ai_generated=is_ai_generated,
            ai_suggestion_source=ai_suggestion_source
        )

        if not task_id:
            return HTMLResponse(
                content='<div class="alert alert--danger">Failed to create task</div>',
                status_code=500
            )

        logger.info(f"Created task {task_id} for patient {icn} by {user['display_name']}")

        # Return success HTML that closes modal and triggers refresh
        return HTMLResponse(content=f"""
            <script>
                // Close modal
                const modal = document.getElementById('task-create-modal');
                if (modal) modal.remove();

                // Restore scroll
                document.body.style.overflow = '';

                // Directly refresh the widget if it exists (dashboard)
                const widgetElement = document.getElementById('widget-tasks');
                if (widgetElement) {{
                    const endpoint = widgetElement.getAttribute('hx-get');
                    if (endpoint) {{
                        console.log('Refreshing widget via direct HTMX call...');
                        htmx.ajax('GET', endpoint, {{
                            target: '#widget-tasks',
                            swap: 'innerHTML'
                        }});
                    }}
                }}

                // Also trigger event for task list page if it exists
                console.log('Dispatching taskUpdated event for list page...');
                document.body.dispatchEvent(new CustomEvent('taskUpdated', {{ bubbles: true }}));

                // Show success toast
                console.log('Task created successfully: ID {task_id}');
            </script>
        """)

    except Exception as e:
        logger.error(f"Error creating task for {icn}: {e}")
        return HTMLResponse(
            content=f'<div class="alert alert--danger">Error creating task: {str(e)}</div>',
            status_code=500
        )


@router.get("/tasks/{task_id}/edit-modal", response_class=HTMLResponse)
async def get_edit_modal(
    request: Request,
    task_id: int
):
    """
    Render edit task modal HTML with pre-populated values.

    Args:
        task_id: Task ID to edit

    Returns:
        HTML modal partial
    """
    try:
        # Get task by ID
        task = get_task_by_id(task_id)

        if not task:
            return HTMLResponse(
                content="<p>Task not found</p>",
                status_code=404
            )

        context = {
            "request": request,
            "task": task
        }

        return templates.TemplateResponse("partials/task_edit_modal.html", context)

    except Exception as e:
        logger.error(f"Error rendering edit modal for task {task_id}: {e}")
        return HTMLResponse(content="<p>Error loading modal</p>", status_code=500)


@router.put("/tasks/{task_id}/update", response_class=HTMLResponse)
async def update_task_modal_submit(
    request: Request,
    task_id: int,
    title: str = Form(..., max_length=500),
    description: Optional[str] = Form(None),
    priority: str = Form("MEDIUM")
):
    """
    Update task from modal form submission.

    Returns success HTML to close modal and refresh task list.
    """
    try:
        # Validate priority
        if priority not in ["HIGH", "MEDIUM", "LOW"]:
            return HTMLResponse(
                content='<div class="alert alert--danger">Invalid priority. Must be HIGH, MEDIUM, or LOW</div>',
                status_code=400
            )

        # Update task
        success = update_task(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority
        )

        if not success:
            return HTMLResponse(
                content='<div class="alert alert--danger">Failed to update task</div>',
                status_code=500
            )

        logger.info(f"Updated task {task_id}")

        # Return success HTML that closes modal and triggers refresh
        return HTMLResponse(content="""
            <script>
                // Close modal
                const modal = document.getElementById('task-edit-modal');
                if (modal) modal.remove();

                // Restore scroll
                document.body.style.overflow = '';

                // Directly refresh the widget if it exists (dashboard)
                const widgetElement = document.getElementById('widget-tasks');
                if (widgetElement) {
                    const endpoint = widgetElement.getAttribute('hx-get');
                    if (endpoint) {
                        console.log('Refreshing widget via direct HTMX call...');
                        htmx.ajax('GET', endpoint, {
                            target: '#widget-tasks',
                            swap: 'innerHTML'
                        });
                    }
                }

                // Also trigger event for task list page if it exists
                console.log('Dispatching taskUpdated event for list page...');
                document.body.dispatchEvent(new CustomEvent('taskUpdated', { bubbles: true }));

                // Show success toast
                console.log('Task updated successfully');
            </script>
        """)

    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return HTMLResponse(
            content=f'<div class="alert alert--danger">Error updating task: {str(e)}</div>',
            status_code=500
        )


# ============================================================================
# PAGE ROUTER ENDPOINTS (Full HTML Pages)
# ============================================================================

@page_router.get("/tasks")
async def tasks_redirect(request: Request):
    """
    Redirect to current patient's tasks page.
    Gets patient from CCOW and redirects to /patient/{icn}/tasks.
    If no patient selected, redirects to dashboard.
    """
    try:
        # Get active patient from CCOW
        patient_id = ccow_client.get_active_patient(request)

        if not patient_id:
            logger.warning("No active patient in CCOW, redirecting to dashboard")
            return RedirectResponse(url="/", status_code=303)

        # Redirect to patient-specific tasks page
        return RedirectResponse(url=f"/patient/{patient_id}/tasks", status_code=303)

    except Exception as e:
        logger.error(f"Error in tasks redirect: {e}")
        return RedirectResponse(url="/", status_code=303)


@page_router.get("/patient/{icn}/tasks", response_class=HTMLResponse)
async def patient_tasks_page(
    request: Request,
    icn: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    created_by: Optional[str] = Query(None, description="Filter by creator (user_id or 'ai')"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """
    Render full patient tasks page with filtering.

    Shows:
    - Summary cards (TODO count, In Progress count, Completed Today, AI Suggested, High Priority)
    - Tasks list with detailed cards
    - Filters for status, created_by, priority (HTMX-powered)
    - New Task button
    - Task cards with inline actions

    Args:
        icn: Integrated Care Number
        status: Filter by status (active, TODO, IN_PROGRESS, COMPLETED, or None/all)
        created_by: Filter by creator (user_id, 'ai', or None for all)
        priority: Filter by priority (HIGH, MEDIUM, LOW, or None)

    Returns:
        Full HTML page
    """
    try:
        # Get user from session
        user = request.state.user
        current_user_id = user["user_id"]

        # Get patient demographics
        patient = get_patient_demographics(icn)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Determine user_id filter
        user_id_filter = None
        if created_by and created_by != "ai":
            user_id_filter = created_by

        # Get tasks with filters
        tasks = get_patient_tasks(
            patient_icn=icn,
            status=status if status and status != "all" else None,
            created_by_user_id=user_id_filter,
            priority=priority if priority and priority != "all" else None
        )

        # Filter AI-generated tasks if requested
        if created_by == "ai":
            tasks = [t for t in tasks if t.get("is_ai_generated")]

        # Get summary stats
        summary = get_task_summary(icn)

        # Calculate additional summary stats
        all_tasks = get_patient_tasks(patient_icn=icn)
        high_priority_count = len([t for t in all_tasks if t["priority"] == "HIGH"])
        summary["high_priority_count"] = high_priority_count
        summary["total_count"] = summary["todo_count"] + summary["in_progress_count"]

        # Get base context (includes sidebar, user, etc.)
        context = get_base_context(request)
        context.update({
            "patient": patient,
            "patient_icn": icn,
            "tasks": tasks,
            "summary": summary,
            "filters": {
                "status": status,
                "created_by": created_by,
                "priority": priority
            },
            "current_user_id": current_user_id,
            "active_page": "tasks"
        })

        return templates.TemplateResponse("patient_tasks.html", context)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering tasks page for {icn}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@page_router.get("/patient/{icn}/tasks/filtered", response_class=HTMLResponse)
async def get_filtered_tasks(
    request: Request,
    icn: str,
    status: Optional[str] = Query(None),
    created_by: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    """
    Render filtered tasks partial (for HTMX swap into #tasks-list-container).

    Args:
        icn: Integrated Care Number
        status: Filter by status (active, TODO, IN_PROGRESS, COMPLETED, or None/all)
        created_by: Filter by creator (user_id, 'ai', or None for all)
        priority: Filter by priority (HIGH, MEDIUM, LOW, or None)

    Returns:
        HTML partial with filtered tasks (tasks_list.html)
    """
    try:
        # Get user from session
        user = request.state.user

        # Determine user_id filter
        user_id_filter = None
        if created_by and created_by != "ai":
            user_id_filter = created_by

        # Get tasks with filters
        tasks = get_patient_tasks(
            patient_icn=icn,
            status=status if status and status != "all" else None,
            created_by_user_id=user_id_filter,
            priority=priority if priority and priority != "all" else None
        )

        # Filter AI-generated tasks if requested
        if created_by == "ai":
            tasks = [t for t in tasks if t.get("is_ai_generated")]

        context = {
            "tasks": tasks,
            "patient_icn": icn,
            "filters": {
                "status": status,
                "created_by": created_by,
                "priority": priority
            }
        }

        return templates.TemplateResponse("partials/tasks_list.html", context)

    except Exception as e:
        logger.error(f"Error rendering filtered tasks for {icn}: {e}")
        return HTMLResponse(content="<p>Error loading filtered tasks</p>")
