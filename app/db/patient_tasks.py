# ---------------------------------------------------------------------
# app/db/patient_tasks.py
# ---------------------------------------------------------------------
# Patient Tasks Database Query Layer
# Provides functions to query patient_tasks table in PostgreSQL
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


def get_patient_tasks(
    patient_icn: str,
    status: Optional[str] = None,
    created_by_user_id: Optional[str] = None,
    priority: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all tasks for a patient by ICN with optional filtering.

    Returns tasks sorted by:
    1. Priority (HIGH > MEDIUM > LOW)
    2. Most recent created_at first

    Args:
        patient_icn: Patient ICN (Integrated Care Number)
        status: Filter by status ('active' for TODO+IN_PROGRESS, 'TODO', 'IN_PROGRESS', 'COMPLETED', or None for all)
        created_by_user_id: Filter by creator user_id (UUID string or None for all)
        priority: Filter by priority ('HIGH', 'MEDIUM', 'LOW', or None for all)
        limit: Maximum number of tasks to return (None for all)

    Returns:
        List of task dictionaries with all task details
    """
    # Build query with dynamic WHERE clauses
    where_clauses = ["patient_key = :patient_icn"]
    params = {"patient_icn": patient_icn}

    # Handle special "active" status filter
    if status:
        if status == "active":
            where_clauses.append("status IN ('TODO', 'IN_PROGRESS')")
        else:
            where_clauses.append("status = :status")
            params["status"] = status

    if created_by_user_id:
        where_clauses.append("created_by_user_id = :created_by_user_id")
        params["created_by_user_id"] = created_by_user_id

    if priority:
        where_clauses.append("priority = :priority")
        params["priority"] = priority

    where_sql = " AND ".join(where_clauses)

    # Build LIMIT clause
    limit_sql = f"LIMIT {limit}" if limit else ""

    query = text(f"""
        SELECT
            task_id,
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            completed_by_user_id,
            completed_by_display_name,
            is_ai_generated,
            ai_suggestion_source,
            created_at,
            updated_at,
            completed_at
        FROM clinical.patient_tasks
        WHERE {where_sql}
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
            END,
            created_at DESC
        {limit_sql}
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()

            tasks = []
            for row in rows:
                tasks.append({
                    "task_id": row[0],
                    "patient_key": row[1],
                    "title": row[2],
                    "description": row[3],
                    "priority": row[4],
                    "status": row[5],
                    "created_by_user_id": str(row[6]) if row[6] else None,  # UUID to string
                    "created_by_display_name": row[7],
                    "completed_by_user_id": str(row[8]) if row[8] else None,  # UUID to string
                    "completed_by_display_name": row[9],
                    "is_ai_generated": row[10],
                    "ai_suggestion_source": row[11],
                    "created_at": row[12].isoformat() if row[12] else None,
                    "updated_at": row[13].isoformat() if row[13] else None,
                    "completed_at": row[14].isoformat() if row[14] else None,
                })

            logger.info(f"Retrieved {len(tasks)} tasks for patient {patient_icn} (status={status}, priority={priority}, limit={limit})")
            return tasks

    except Exception as e:
        logger.error(f"Error fetching patient tasks for ICN {patient_icn}: {e}")
        return []


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a single task by task_id.

    Args:
        task_id: Unique task identifier

    Returns:
        Task dictionary or None if not found
    """
    query = text("""
        SELECT
            task_id,
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            completed_by_user_id,
            completed_by_display_name,
            is_ai_generated,
            ai_suggestion_source,
            created_at,
            updated_at,
            completed_at
        FROM clinical.patient_tasks
        WHERE task_id = :task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"task_id": task_id})
            row = result.fetchone()

            if not row:
                logger.warning(f"Task not found: task_id={task_id}")
                return None

            task = {
                "task_id": row[0],
                "patient_key": row[1],
                "title": row[2],
                "description": row[3],
                "priority": row[4],
                "status": row[5],
                "created_by_user_id": str(row[6]) if row[6] else None,
                "created_by_display_name": row[7],
                "completed_by_user_id": str(row[8]) if row[8] else None,
                "completed_by_display_name": row[9],
                "is_ai_generated": row[10],
                "ai_suggestion_source": row[11],
                "created_at": row[12].isoformat() if row[12] else None,
                "updated_at": row[13].isoformat() if row[13] else None,
                "completed_at": row[14].isoformat() if row[14] else None,
            }

            logger.info(f"Retrieved task: task_id={task_id}")
            return task

    except Exception as e:
        logger.error(f"Error fetching task by ID {task_id}: {e}")
        return None


def create_task(
    patient_icn: str,
    title: str,
    created_by_user_id: str,
    created_by_display_name: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM",
    is_ai_generated: bool = False,
    ai_suggestion_source: Optional[str] = None
) -> Optional[int]:
    """
    Create a new task for a patient.

    Args:
        patient_icn: Patient ICN
        title: Task title (required, max 500 chars)
        created_by_user_id: UUID of user creating the task
        created_by_display_name: Display name of user (e.g., "Dr. Anderson")
        description: Optional detailed description
        priority: Task priority ('HIGH', 'MEDIUM', 'LOW'), default 'MEDIUM'
        is_ai_generated: True if task created via AI Insights, default False
        ai_suggestion_source: AI reasoning text (only if is_ai_generated=True)

    Returns:
        task_id of newly created task, or None if creation failed
    """
    query = text("""
        INSERT INTO clinical.patient_tasks (
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            is_ai_generated,
            ai_suggestion_source
        ) VALUES (
            :patient_icn,
            :title,
            :description,
            :priority,
            'TODO',
            :created_by_user_id,
            :created_by_display_name,
            :is_ai_generated,
            :ai_suggestion_source
        )
        RETURNING task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "patient_icn": patient_icn,
                "title": title,
                "description": description,
                "priority": priority,
                "created_by_user_id": created_by_user_id,
                "created_by_display_name": created_by_display_name,
                "is_ai_generated": is_ai_generated,
                "ai_suggestion_source": ai_suggestion_source
            })
            conn.commit()
            task_id = result.scalar()

            logger.info(f"Created task: task_id={task_id}, patient={patient_icn}, title='{title[:50]}...', created_by={created_by_display_name}")
            return task_id

    except Exception as e:
        logger.error(f"Error creating task for patient {patient_icn}: {e}")
        return None


def update_task_status(task_id: int, new_status: str) -> bool:
    """
    Update task status (TODO, IN_PROGRESS, COMPLETED).

    Note: For COMPLETED status, use complete_task() instead to populate audit fields.

    Args:
        task_id: Task identifier
        new_status: New status ('TODO', 'IN_PROGRESS', 'COMPLETED')

    Returns:
        True if update succeeded, False otherwise
    """
    query = text("""
        UPDATE clinical.patient_tasks
        SET status = :new_status
        WHERE task_id = :task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"task_id": task_id, "new_status": new_status})
            conn.commit()

            if result.rowcount == 0:
                logger.warning(f"Task not found for status update: task_id={task_id}")
                return False

            logger.info(f"Updated task status: task_id={task_id}, new_status={new_status}")
            return True

    except Exception as e:
        logger.error(f"Error updating task status for task_id {task_id}: {e}")
        return False


def complete_task(
    task_id: int,
    completed_by_user_id: str,
    completed_by_display_name: str
) -> bool:
    """
    Mark task as COMPLETED and populate audit fields.

    This function is preferred over update_task_status() for completing tasks
    because it properly records who completed the task and when.

    Args:
        task_id: Task identifier
        completed_by_user_id: UUID of user completing the task
        completed_by_display_name: Display name of user (e.g., "Dr. Brown")

    Returns:
        True if completion succeeded, False otherwise
    """
    query = text("""
        UPDATE clinical.patient_tasks
        SET
            status = 'COMPLETED',
            completed_by_user_id = :completed_by_user_id,
            completed_by_display_name = :completed_by_display_name,
            completed_at = NOW()
        WHERE task_id = :task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "task_id": task_id,
                "completed_by_user_id": completed_by_user_id,
                "completed_by_display_name": completed_by_display_name
            })
            conn.commit()

            if result.rowcount == 0:
                logger.warning(f"Task not found for completion: task_id={task_id}")
                return False

            logger.info(f"Completed task: task_id={task_id}, completed_by={completed_by_display_name}")
            return True

    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        return False


def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> bool:
    """
    Update task details (title, description, priority).

    Only updates fields that are not None. Use update_task_status() or
    complete_task() for status changes.

    Args:
        task_id: Task identifier
        title: New title (max 500 chars) or None to keep existing
        description: New description or None to keep existing
        priority: New priority ('HIGH', 'MEDIUM', 'LOW') or None to keep existing

    Returns:
        True if update succeeded, False otherwise
    """
    # Build SET clauses for non-None fields
    updates = []
    params = {"task_id": task_id}

    if title is not None:
        updates.append("title = :title")
        params["title"] = title

    if description is not None:
        updates.append("description = :description")
        params["description"] = description

    if priority is not None:
        updates.append("priority = :priority")
        params["priority"] = priority

    if not updates:
        logger.warning(f"No fields to update for task_id={task_id}")
        return False

    update_sql = ", ".join(updates)
    query = text(f"""
        UPDATE clinical.patient_tasks
        SET {update_sql}
        WHERE task_id = :task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            conn.commit()

            if result.rowcount == 0:
                logger.warning(f"Task not found for update: task_id={task_id}")
                return False

            logger.info(f"Updated task: task_id={task_id}, fields={list(params.keys())}")
            return True

    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return False


def delete_task(task_id: int) -> bool:
    """
    Delete task from database (hard delete).

    Phase 2+ should implement soft delete with archived flag instead.

    Args:
        task_id: Task identifier

    Returns:
        True if deletion succeeded, False otherwise
    """
    query = text("""
        DELETE FROM clinical.patient_tasks
        WHERE task_id = :task_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"task_id": task_id})
            conn.commit()

            if result.rowcount == 0:
                logger.warning(f"Task not found for deletion: task_id={task_id}")
                return False

            logger.info(f"Deleted task: task_id={task_id}")
            return True

    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return False


def get_task_summary(patient_icn: str) -> Dict[str, int]:
    """
    Get summary statistics for patient's tasks.

    Used for full page summary cards display.

    Args:
        patient_icn: Patient ICN

    Returns:
        Dictionary with counts:
        - todo_count: Number of TODO tasks
        - in_progress_count: Number of IN_PROGRESS tasks
        - completed_today_count: Number of tasks completed today
        - ai_generated_count: Number of active AI-generated tasks
    """
    query = text("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'TODO') AS todo_count,
            COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress_count,
            COUNT(*) FILTER (WHERE status = 'COMPLETED' AND completed_at::DATE = CURRENT_DATE) AS completed_today_count,
            COUNT(*) FILTER (WHERE is_ai_generated = TRUE AND status != 'COMPLETED') AS ai_generated_count
        FROM clinical.patient_tasks
        WHERE patient_key = :patient_icn
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"patient_icn": patient_icn})
            row = result.fetchone()

            if not row:
                return {
                    "todo_count": 0,
                    "in_progress_count": 0,
                    "completed_today_count": 0,
                    "ai_generated_count": 0
                }

            summary = {
                "todo_count": row[0] or 0,
                "in_progress_count": row[1] or 0,
                "completed_today_count": row[2] or 0,
                "ai_generated_count": row[3] or 0
            }

            logger.info(f"Retrieved task summary for patient {patient_icn}: {summary}")
            return summary

    except Exception as e:
        logger.error(f"Error fetching task summary for patient {patient_icn}: {e}")
        return {
            "todo_count": 0,
            "in_progress_count": 0,
            "completed_today_count": 0,
            "ai_generated_count": 0
        }


def get_tasks_by_user(
    user_id: str,
    status: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all tasks created by a specific user (across all patients).

    Useful for "My Tasks" view across multiple patients.

    Args:
        user_id: User UUID
        status: Filter by status ('active', 'TODO', 'IN_PROGRESS', 'COMPLETED', or None)
        limit: Maximum number of tasks to return

    Returns:
        List of task dictionaries sorted by priority and created_at
    """
    where_clauses = ["created_by_user_id = :user_id"]
    params = {"user_id": user_id}

    if status:
        if status == "active":
            where_clauses.append("status IN ('TODO', 'IN_PROGRESS')")
        else:
            where_clauses.append("status = :status")
            params["status"] = status

    where_sql = " AND ".join(where_clauses)
    limit_sql = f"LIMIT {limit}" if limit else ""

    query = text(f"""
        SELECT
            task_id,
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            completed_by_user_id,
            completed_by_display_name,
            is_ai_generated,
            ai_suggestion_source,
            created_at,
            updated_at,
            completed_at
        FROM clinical.patient_tasks
        WHERE {where_sql}
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
            END,
            created_at DESC
        {limit_sql}
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, params)
            rows = result.fetchall()

            tasks = []
            for row in rows:
                tasks.append({
                    "task_id": row[0],
                    "patient_key": row[1],
                    "title": row[2],
                    "description": row[3],
                    "priority": row[4],
                    "status": row[5],
                    "created_by_user_id": str(row[6]) if row[6] else None,
                    "created_by_display_name": row[7],
                    "completed_by_user_id": str(row[8]) if row[8] else None,
                    "completed_by_display_name": row[9],
                    "is_ai_generated": row[10],
                    "ai_suggestion_source": row[11],
                    "created_at": row[12].isoformat() if row[12] else None,
                    "updated_at": row[13].isoformat() if row[13] else None,
                    "completed_at": row[14].isoformat() if row[14] else None,
                })

            logger.info(f"Retrieved {len(tasks)} tasks for user {user_id} (status={status}, limit={limit})")
            return tasks

    except Exception as e:
        logger.error(f"Error fetching tasks by user {user_id}: {e}")
        return []
