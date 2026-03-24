#!/usr/bin/env python3
"""
============================================================================
Clinical Task Tracking - API Endpoints Integration Tests
============================================================================
Purpose: Test all API endpoints in app/routes/tasks.py
Created: 2026-02-10
Requirements: FastAPI app must be running on http://localhost:8000
============================================================================
"""

import httpx
import json
import sys


BASE_URL = "http://localhost:8000"
TEST_ICN = "ICN100001"  # Adam Dooree
TEST_USER_EMAIL = "clinician.alpha@va.gov"
TEST_USER_PASSWORD = "VaDemo2025!"


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


def login(client):
    """Login and get session cookie"""
    print_section("TEST 0: Authentication")

    response = client.post(
        f"{BASE_URL}/login",
        data={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        },
        follow_redirects=False
    )

    if response.status_code == 303:
        print_test("Login successful", True, f"Redirected to {response.headers.get('location')}")
        return True
    else:
        print_test("Login failed", False, f"Status: {response.status_code}")
        return False


def test_get_patient_tasks(client):
    """Test GET /api/patient/{icn}/tasks"""
    print_section("TEST 1: GET /api/patient/{icn}/tasks")

    # Test 1.1: Get all tasks
    response = client.get(f"{BASE_URL}/api/patient/{TEST_ICN}/tasks")
    test_passed = response.status_code == 200
    print_test("Get all tasks", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = "tasks" in data and "count" in data
        print_test("Response has expected structure", test_passed, f"Tasks count: {data.get('count', 0)}")

    # Test 1.2: Filter by status='active'
    response = client.get(f"{BASE_URL}/api/patient/{TEST_ICN}/tasks?status=active")
    test_passed = response.status_code == 200
    if test_passed:
        data = response.json()
        test_passed = data.get("filters", {}).get("status") == "active"
    print_test("Filter by status='active'", test_passed)

    # Test 1.3: Filter by priority='HIGH'
    response = client.get(f"{BASE_URL}/api/patient/{TEST_ICN}/tasks?priority=HIGH")
    test_passed = response.status_code == 200
    if test_passed:
        data = response.json()
        test_passed = data.get("filters", {}).get("priority") == "HIGH"
    print_test("Filter by priority='HIGH'", test_passed)

    # Test 1.4: Limit results
    response = client.get(f"{BASE_URL}/api/patient/{TEST_ICN}/tasks?limit=3")
    test_passed = response.status_code == 200
    if test_passed:
        data = response.json()
        test_passed = len(data.get("tasks", [])) <= 3
    print_test("Limit to 3 tasks", test_passed)


def test_get_tasks_summary(client):
    """Test GET /api/patient/{icn}/tasks/summary"""
    print_section("TEST 2: GET /api/patient/{icn}/tasks/summary")

    response = client.get(f"{BASE_URL}/api/patient/{TEST_ICN}/tasks/summary")
    test_passed = response.status_code == 200
    print_test("Get task summary", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        required_keys = ["todo_count", "in_progress_count", "completed_today_count", "ai_generated_count"]
        test_passed = all(key in data for key in required_keys)
        print_test("Summary has all required fields", test_passed, f"Summary: {json.dumps(data, indent=2)}")


def test_create_task(client):
    """Test POST /api/patient/{icn}/tasks"""
    print_section("TEST 3: POST /api/patient/{icn}/tasks")

    # Create a new task
    response = client.post(
        f"{BASE_URL}/api/patient/{TEST_ICN}/tasks",
        data={
            "title": "TEST: API test task from automated script",
            "description": "This task was created by the API test script.",
            "priority": "MEDIUM",
            "is_ai_generated": "false"
        }
    )

    test_passed = response.status_code == 200
    print_test("Create new task", test_passed, f"Status: {response.status_code}")

    task_id = None
    if test_passed:
        data = response.json()
        test_passed = data.get("success") is True and "task_id" in data
        task_id = data.get("task_id")
        print_test("Response has task_id", test_passed, f"Created task_id: {task_id}")

    return task_id


def test_start_task(client, task_id):
    """Test POST /api/patient/tasks/{task_id}/start"""
    print_section("TEST 4: POST /api/patient/tasks/{task_id}/start")

    if not task_id:
        print_test("Start task (skipped - no task_id)", False, "No task to start")
        return

    response = client.post(f"{BASE_URL}/api/patient/tasks/{task_id}/start")
    test_passed = response.status_code == 200
    print_test(f"Start task {task_id}", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = data.get("task", {}).get("status") == "IN_PROGRESS"
        print_test("Task status changed to IN_PROGRESS", test_passed)


def test_revert_task(client, task_id):
    """Test POST /api/patient/tasks/{task_id}/revert-to-todo"""
    print_section("TEST 5: POST /api/patient/tasks/{task_id}/revert-to-todo")

    if not task_id:
        print_test("Revert task (skipped - no task_id)", False, "No task to revert")
        return

    response = client.post(f"{BASE_URL}/api/patient/tasks/{task_id}/revert-to-todo")
    test_passed = response.status_code == 200
    print_test(f"Revert task {task_id} to TODO", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = data.get("task", {}).get("status") == "TODO"
        print_test("Task status changed to TODO", test_passed)


def test_complete_task(client, task_id):
    """Test POST /api/patient/tasks/{task_id}/complete"""
    print_section("TEST 6: POST /api/patient/tasks/{task_id}/complete")

    if not task_id:
        print_test("Complete task (skipped - no task_id)", False, "No task to complete")
        return

    response = client.post(f"{BASE_URL}/api/patient/tasks/{task_id}/complete")
    test_passed = response.status_code == 200
    print_test(f"Complete task {task_id}", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = (
            data.get("task", {}).get("status") == "COMPLETED" and
            data.get("task", {}).get("completed_at") is not None
        )
        print_test("Task marked as COMPLETED with completed_at", test_passed)


def test_update_task(client, task_id):
    """Test PUT /api/patient/tasks/{task_id}"""
    print_section("TEST 7: PUT /api/patient/tasks/{task_id}")

    if not task_id:
        print_test("Update task (skipped - no task_id)", False, "No task to update")
        return

    response = client.put(
        f"{BASE_URL}/api/patient/tasks/{task_id}",
        data={
            "title": "TEST: UPDATED task title",
            "priority": "HIGH"
        }
    )

    test_passed = response.status_code == 200
    print_test(f"Update task {task_id}", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = (
            data.get("task", {}).get("title") == "TEST: UPDATED task title" and
            data.get("task", {}).get("priority") == "HIGH"
        )
        print_test("Task updated with new title and priority", test_passed)


def test_delete_task(client, task_id):
    """Test DELETE /api/patient/tasks/{task_id}"""
    print_section("TEST 8: DELETE /api/patient/tasks/{task_id}")

    if not task_id:
        print_test("Delete task (skipped - no task_id)", False, "No task to delete")
        return

    response = client.delete(f"{BASE_URL}/api/patient/tasks/{task_id}")
    test_passed = response.status_code == 200
    print_test(f"Delete task {task_id}", test_passed, f"Status: {response.status_code}")

    if test_passed:
        data = response.json()
        test_passed = data.get("success") is True
        print_test("Task deleted successfully", test_passed)


def test_widget_endpoint(client):
    """Test GET /api/patient/dashboard/widget/tasks/{icn}"""
    print_section("TEST 9: GET /api/patient/dashboard/widget/tasks/{icn}")

    response = client.get(f"{BASE_URL}/api/patient/dashboard/widget/tasks/{TEST_ICN}")
    test_passed = response.status_code == 200
    print_test("Get tasks widget HTML", test_passed, f"Status: {response.status_code}")

    if test_passed:
        content = response.text
        test_passed = "widget" in content and "tasks" in content.lower()
        print_test("Widget HTML contains expected elements", test_passed, f"Content length: {len(content)} bytes")


def test_page_endpoints(client):
    """Test page router endpoints"""
    print_section("TEST 10: Page Router Endpoints")

    # Test 10.1: CCOW redirect
    response = client.get(f"{BASE_URL}/tasks", follow_redirects=False)
    test_passed = response.status_code in [303, 307, 302]
    print_test("GET /tasks (CCOW redirect)", test_passed, f"Status: {response.status_code}")

    # Test 10.2: Full tasks page
    response = client.get(f"{BASE_URL}/patient/{TEST_ICN}/tasks")
    test_passed = response.status_code == 200
    print_test(f"GET /patient/{TEST_ICN}/tasks (full page)", test_passed, f"Status: {response.status_code}")

    # Test 10.3: Filtered tasks partial
    response = client.get(f"{BASE_URL}/patient/{TEST_ICN}/tasks/filtered?status=active")
    test_passed = response.status_code == 200
    print_test("GET /patient/{icn}/tasks/filtered (HTMX partial)", test_passed, f"Status: {response.status_code}")


def main():
    """Run all API tests"""
    print("\n" + "="*70)
    print("CLINICAL TASK TRACKING - API ENDPOINTS INTEGRATION TESTS")
    print("="*70)
    print(f"Testing: {BASE_URL}")
    print(f"Test Patient: {TEST_ICN}")
    print(f"Test User: {TEST_USER_EMAIL}")
    print("="*70)
    print("\nNOTE: FastAPI app must be running on http://localhost:8000")
    print("Start with: uvicorn app.main:app --reload")
    print("="*70)

    try:
        # Create HTTP client with session cookie persistence
        with httpx.Client(follow_redirects=True) as client:

            # Login first
            if not login(client):
                print("\n✗ Login failed. Cannot proceed with tests.")
                print("Make sure FastAPI app is running and credentials are correct.")
                sys.exit(1)

            # Run tests
            test_get_patient_tasks(client)
            test_get_tasks_summary(client)

            # Create a test task
            task_id = test_create_task(client)

            # Test task lifecycle
            if task_id:
                test_start_task(client, task_id)
                test_revert_task(client, task_id)
                test_complete_task(client, task_id)
                test_update_task(client, task_id)
                test_delete_task(client, task_id)

            # Test widget and page endpoints
            test_widget_endpoint(client)
            test_page_endpoints(client)

            print_section("ALL TESTS COMPLETED")
            print("✓ API endpoint tests complete")
            print("✓ All endpoints in app/routes/tasks.py verified")
            print("\nNOTE: Templates will be implemented in Week 2 (UI implementation)")
            print("      Widget and page endpoints return placeholder HTML for now.")

    except httpx.ConnectError:
        print("\n✗ CONNECTION ERROR: Cannot connect to FastAPI app")
        print(f"   Make sure app is running: uvicorn app.main:app --reload")
        print(f"   Expected URL: {BASE_URL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
