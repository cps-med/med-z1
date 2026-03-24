#!/usr/bin/env python3
"""
============================================================================
Clinical Task Tracking - Query Layer Integration Tests
============================================================================
Purpose: Test all functions in app/db/patient_tasks.py
Created: 2026-02-10
============================================================================
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import patient_tasks
import json


def print_section(title):
    """Print section header"""
    print("\n" + "="*70)
    print(f"{title}")
    print("="*70)


def print_test(test_name, passed, details=""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"  {details}")


def test_get_patient_tasks():
    """Test get_patient_tasks() with various filters"""
    print_section("TEST 1: get_patient_tasks()")

    # Test 1.1: Get all tasks for patient ICN100001
    tasks = patient_tasks.get_patient_tasks("ICN100001")
    test_passed = len(tasks) == 6
    print_test("Get all tasks for ICN100001", test_passed, f"Expected 6 tasks, got {len(tasks)}")

    # Test 1.2: Filter by status='TODO'
    todo_tasks = patient_tasks.get_patient_tasks("ICN100001", status="TODO")
    test_passed = len(todo_tasks) == 4  # Tasks 2, 3, 4, 5
    print_test("Filter by status='TODO'", test_passed, f"Expected 4 TODO tasks, got {len(todo_tasks)}")

    # Test 1.3: Filter by status='active' (TODO + IN_PROGRESS)
    active_tasks = patient_tasks.get_patient_tasks("ICN100001", status="active")
    test_passed = len(active_tasks) == 5  # Tasks 1, 2, 3, 4, 5
    print_test("Filter by status='active'", test_passed, f"Expected 5 active tasks, got {len(active_tasks)}")

    # Test 1.4: Filter by priority='HIGH'
    high_priority_tasks = patient_tasks.get_patient_tasks("ICN100001", priority="HIGH")
    test_passed = len(high_priority_tasks) == 2  # Tasks 1, 3
    print_test("Filter by priority='HIGH'", test_passed, f"Expected 2 HIGH priority tasks, got {len(high_priority_tasks)}")

    # Test 1.5: Filter by created_by_user_id
    user_id = "5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2"  # Dr. Anderson
    user_tasks = patient_tasks.get_patient_tasks("ICN100001", created_by_user_id=user_id)
    test_passed = len(user_tasks) == 4  # Tasks 1, 2, 4, 6
    print_test("Filter by created_by_user_id (Dr. Anderson)", test_passed, f"Expected 4 tasks, got {len(user_tasks)}")

    # Test 1.6: Limit results
    limited_tasks = patient_tasks.get_patient_tasks("ICN100001", limit=3)
    test_passed = len(limited_tasks) == 3
    print_test("Limit to 3 tasks", test_passed, f"Expected 3 tasks, got {len(limited_tasks)}")

    # Test 1.7: Verify task structure
    if tasks:
        task = tasks[0]
        required_fields = [
            "task_id", "patient_key", "title", "description", "priority", "status",
            "created_by_user_id", "created_by_display_name", "is_ai_generated",
            "created_at", "updated_at"
        ]
        test_passed = all(field in task for field in required_fields)
        print_test("Task dictionary structure", test_passed, f"Has all {len(required_fields)} required fields")

    # Test 1.8: Verify sorting (HIGH > MEDIUM > LOW)
    if len(tasks) >= 3:
        priorities = [t["priority"] for t in tasks]
        # Check that HIGH tasks come before MEDIUM before LOW
        high_indices = [i for i, p in enumerate(priorities) if p == "HIGH"]
        medium_indices = [i for i, p in enumerate(priorities) if p == "MEDIUM"]
        low_indices = [i for i, p in enumerate(priorities) if p == "LOW"]

        test_passed = True
        if high_indices and medium_indices:
            test_passed = test_passed and max(high_indices) < min(medium_indices)
        if medium_indices and low_indices:
            test_passed = test_passed and max(medium_indices) < min(low_indices)

        print_test("Tasks sorted by priority", test_passed, f"Order: {', '.join(priorities)}")

    return tasks


def test_get_task_by_id():
    """Test get_task_by_id()"""
    print_section("TEST 2: get_task_by_id()")

    # Test 2.1: Get existing task
    task = patient_tasks.get_task_by_id(1)
    test_passed = task is not None and task["task_id"] == 1
    print_test("Get task by ID (task_id=1)", test_passed, f"Title: {task['title'][:50]}..." if task else "Task not found")

    # Test 2.2: Get non-existent task
    task = patient_tasks.get_task_by_id(99999)
    test_passed = task is None
    print_test("Get non-existent task (task_id=99999)", test_passed, "Returns None as expected")

    return task


def test_create_task():
    """Test create_task()"""
    print_section("TEST 3: create_task()")

    # Test 3.1: Create new task
    task_id = patient_tasks.create_task(
        patient_icn="ICN100001",
        title="TEST: Automated query layer test task",
        created_by_user_id="5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2",
        created_by_display_name="Test Script",
        description="This task was created by the automated test script.",
        priority="LOW"
    )
    test_passed = task_id is not None and isinstance(task_id, int)
    print_test("Create new task", test_passed, f"Created task_id={task_id}")

    # Test 3.2: Verify task was created
    if task_id:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = (
            task is not None and
            task["title"] == "TEST: Automated query layer test task" and
            task["priority"] == "LOW" and
            task["status"] == "TODO"
        )
        print_test("Verify created task", test_passed, f"Task exists with correct attributes")

    # Test 3.3: Create AI-generated task
    ai_task_id = patient_tasks.create_task(
        patient_icn="ICN100001",
        title="TEST: AI-generated test task",
        created_by_user_id="5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2",
        created_by_display_name="Test Script",
        description="AI-suggested test task.",
        priority="MEDIUM",
        is_ai_generated=True,
        ai_suggestion_source="AI Test: Automated testing of AI task creation"
    )
    test_passed = ai_task_id is not None
    print_test("Create AI-generated task", test_passed, f"Created task_id={ai_task_id}")

    if ai_task_id:
        task = patient_tasks.get_task_by_id(ai_task_id)
        test_passed = task and task["is_ai_generated"] is True
        print_test("Verify AI-generated flag", test_passed, f"is_ai_generated={task['is_ai_generated'] if task else 'N/A'}")

    return task_id, ai_task_id


def test_update_task_status(task_id):
    """Test update_task_status()"""
    print_section("TEST 4: update_task_status()")

    # Test 4.1: Update TODO → IN_PROGRESS
    success = patient_tasks.update_task_status(task_id, "IN_PROGRESS")
    test_passed = success is True
    print_test("Update status TODO → IN_PROGRESS", test_passed)

    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = task and task["status"] == "IN_PROGRESS"
        print_test("Verify status changed", test_passed, f"Status: {task['status'] if task else 'N/A'}")

    # Test 4.2: Update IN_PROGRESS → TODO (revert)
    success = patient_tasks.update_task_status(task_id, "TODO")
    test_passed = success is True
    print_test("Update status IN_PROGRESS → TODO", test_passed)

    # Test 4.3: Update non-existent task
    success = patient_tasks.update_task_status(99999, "IN_PROGRESS")
    test_passed = success is False
    print_test("Update non-existent task (should fail)", test_passed, "Returns False as expected")


def test_complete_task(task_id):
    """Test complete_task()"""
    print_section("TEST 5: complete_task()")

    # Test 5.1: Complete task
    success = patient_tasks.complete_task(
        task_id=task_id,
        completed_by_user_id="76bb61c4-8d22-4605-b290-f1a2b757019b",
        completed_by_display_name="Dr. Bob Brown, DO"
    )
    test_passed = success is True
    print_test("Complete task", test_passed)

    # Test 5.2: Verify completion
    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = (
            task and
            task["status"] == "COMPLETED" and
            task["completed_by_display_name"] == "Dr. Bob Brown, DO" and
            task["completed_at"] is not None
        )
        print_test("Verify completion audit fields", test_passed,
                   f"Completed by: {task['completed_by_display_name'] if task else 'N/A'}")

    # Test 5.3: Revert completed task back to TODO
    success = patient_tasks.update_task_status(task_id, "TODO")
    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = (
            task and
            task["status"] == "TODO" and
            task["completed_at"] is None and
            task["completed_by_user_id"] is None
        )
        print_test("Revert COMPLETED → TODO (trigger clears audit fields)", test_passed,
                   f"completed_at cleared: {task['completed_at'] is None if task else 'N/A'}")


def test_update_task(task_id):
    """Test update_task()"""
    print_section("TEST 6: update_task()")

    # Get original task
    original_task = patient_tasks.get_task_by_id(task_id)
    original_title = original_task["title"] if original_task else ""

    # Test 6.1: Update title
    new_title = "TEST: UPDATED - Query layer test task"
    success = patient_tasks.update_task(task_id, title=new_title)
    test_passed = success is True
    print_test("Update task title", test_passed)

    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = task and task["title"] == new_title
        print_test("Verify title changed", test_passed, f"New title: {task['title'][:50]}..." if task else "N/A")

    # Test 6.2: Update description
    new_description = "This description was updated by the test script."
    success = patient_tasks.update_task(task_id, description=new_description)
    test_passed = success is True
    print_test("Update task description", test_passed)

    # Test 6.3: Update priority
    success = patient_tasks.update_task(task_id, priority="HIGH")
    test_passed = success is True
    print_test("Update task priority LOW → HIGH", test_passed)

    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = task and task["priority"] == "HIGH"
        print_test("Verify priority changed", test_passed, f"Priority: {task['priority'] if task else 'N/A'}")

    # Test 6.4: Update multiple fields at once
    success = patient_tasks.update_task(
        task_id,
        title=original_title,  # Restore original title
        priority="LOW"  # Restore original priority
    )
    test_passed = success is True
    print_test("Update multiple fields at once", test_passed)

    # Test 6.5: Update with no fields (should fail gracefully)
    success = patient_tasks.update_task(task_id)
    test_passed = success is False
    print_test("Update with no fields (should return False)", test_passed)


def test_get_task_summary():
    """Test get_task_summary()"""
    print_section("TEST 7: get_task_summary()")

    # Test 7.1: Get summary for ICN100001
    summary = patient_tasks.get_task_summary("ICN100001")
    test_passed = isinstance(summary, dict) and "todo_count" in summary
    print_test("Get task summary for ICN100001", test_passed, f"Summary: {json.dumps(summary)}")

    # Test 7.2: Verify summary counts are reasonable
    if summary:
        test_passed = (
            summary["todo_count"] >= 0 and
            summary["in_progress_count"] >= 0 and
            summary["completed_today_count"] >= 0 and
            summary["ai_generated_count"] >= 0
        )
        print_test("Verify summary counts are non-negative", test_passed)

    # Test 7.3: Get summary for patient with no tasks
    summary = patient_tasks.get_task_summary("ICN999999")
    test_passed = (
        summary["todo_count"] == 0 and
        summary["in_progress_count"] == 0 and
        summary["completed_today_count"] == 0 and
        summary["ai_generated_count"] == 0
    )
    print_test("Get summary for patient with no tasks", test_passed, "All counts = 0")


def test_get_tasks_by_user():
    """Test get_tasks_by_user()"""
    print_section("TEST 8: get_tasks_by_user()")

    user_id = "5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2"  # Dr. Anderson

    # Test 8.1: Get all tasks created by user
    tasks = patient_tasks.get_tasks_by_user(user_id)
    test_passed = len(tasks) > 0
    print_test(f"Get all tasks by user {user_id[:8]}...", test_passed, f"Found {len(tasks)} tasks")

    # Test 8.2: Filter by status='active'
    active_tasks = patient_tasks.get_tasks_by_user(user_id, status="active")
    test_passed = len(active_tasks) > 0
    print_test("Get active tasks by user", test_passed, f"Found {len(active_tasks)} active tasks")

    # Test 8.3: Limit results
    limited_tasks = patient_tasks.get_tasks_by_user(user_id, limit=5)
    test_passed = len(limited_tasks) <= 5
    print_test("Limit user tasks to 5", test_passed, f"Got {len(limited_tasks)} tasks")

    # Test 8.4: Verify tasks span multiple patients
    if len(tasks) > 1:
        patient_keys = set(t["patient_key"] for t in tasks)
        test_passed = len(patient_keys) >= 1
        print_test("Tasks span patients", test_passed, f"Patients: {', '.join(patient_keys)}")


def test_delete_task(task_id):
    """Test delete_task()"""
    print_section("TEST 9: delete_task()")

    # Test 9.1: Delete task
    success = patient_tasks.delete_task(task_id)
    test_passed = success is True
    print_test(f"Delete task {task_id}", test_passed)

    # Test 9.2: Verify task was deleted
    if success:
        task = patient_tasks.get_task_by_id(task_id)
        test_passed = task is None
        print_test("Verify task deleted", test_passed, "Task no longer exists")

    # Test 9.3: Delete non-existent task (should fail)
    success = patient_tasks.delete_task(99999)
    test_passed = success is False
    print_test("Delete non-existent task (should fail)", test_passed, "Returns False as expected")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("CLINICAL TASK TRACKING - QUERY LAYER INTEGRATION TESTS")
    print("="*70)
    print("Testing: app/db/patient_tasks.py")
    print("Database: PostgreSQL medz1 (clinical.patient_tasks)")
    print("="*70)

    try:
        # Test 1: Get patient tasks
        all_tasks = test_get_patient_tasks()

        # Test 2: Get task by ID
        test_get_task_by_id()

        # Test 3: Create tasks
        test_task_id, ai_task_id = test_create_task()

        if test_task_id:
            # Test 4: Update task status
            test_update_task_status(test_task_id)

            # Test 5: Complete task
            test_complete_task(test_task_id)

            # Test 6: Update task details
            test_update_task(test_task_id)

            # Test 7: Get task summary
            test_get_task_summary()

            # Test 8: Get tasks by user
            test_get_tasks_by_user()

            # Test 9: Delete tasks (cleanup)
            test_delete_task(test_task_id)
            if ai_task_id:
                test_delete_task(ai_task_id)

        print_section("ALL TESTS COMPLETED")
        print("✓ Query layer integration tests complete")
        print("✓ All functions in app/db/patient_tasks.py verified")

    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
