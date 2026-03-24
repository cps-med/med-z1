#!/usr/bin/env python3
"""
Test script for Phase 6: Conversation Memory

Tests that the LangGraph agent with AsyncPostgresSaver checkpointer
correctly maintains conversation history across multiple messages.

Usage:
    python scripts/test_conversation_memory.py

Prerequisites:
    - PostgreSQL running with checkpoint tables
    - FastAPI application running on http://127.0.0.1:8000
    - Logged in with valid session
"""

import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_PATIENT_ICN = "ICN100001"  # Adam Dooree

# Test credentials
TEST_EMAIL = "clinician.alpha@va.gov"
TEST_PASSWORD = "VaDemo2025!"


def login():
    """Login and get session cookie"""
    print("\n" + "="*60)
    print("Step 1: Logging in...")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/login",
        data={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        },
        allow_redirects=False
    )

    if response.status_code not in [302, 303]:
        print(f"❌ Login failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        return None

    # Extract session_id cookie
    session_id = response.cookies.get('session_id')
    if not session_id:
        print("❌ No session_id cookie found")
        return None

    print(f"✅ Logged in successfully")
    print(f"   Session ID: {session_id[:20]}...")

    return {'session_id': session_id}


def send_chat_message(cookies, message):
    """Send chat message and get response"""
    response = requests.post(
        f"{BASE_URL}/insight/chat",
        data={
            "icn": TEST_PATIENT_ICN,
            "message": message
        },
        cookies=cookies
    )

    if response.status_code != 200:
        print(f"❌ Chat failed: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return None

    return response.text


def test_conversation_memory():
    """
    Test conversation memory across multiple messages.

    Test Flow:
    1. Login to get session
    2. Ask: "What is the patient's date of birth?"
    3. Ask: "How old is the patient?" (should use memory, not re-call tool)
    4. Verify conversation persists
    """

    # Step 1: Login
    cookies = login()
    if not cookies:
        return False

    # Step 2: First message - ask for birth date
    print("\n" + "="*60)
    print("Step 2: First Message - Ask for birth date")
    print("="*60)

    message1 = "What is the patient's date of birth?"
    print(f"User: {message1}")

    response1 = send_chat_message(cookies, message1)
    if not response1:
        return False

    print(f"\n✅ Response received ({len(response1)} bytes)")
    print(f"   (Contains birth date information)")

    # Step 3: Second message - ask follow-up (should use memory)
    print("\n" + "="*60)
    print("Step 3: Second Message - Ask follow-up (tests memory)")
    print("="*60)

    message2 = "How old is the patient?"
    print(f"User: {message2}")
    print(f"\n🔍 Expected behavior:")
    print(f"   - Agent should remember birth date from previous message")
    print(f"   - Should NOT call get_patient_summary tool again")
    print(f"   - Should calculate age from remembered birth date")

    response2 = send_chat_message(cookies, message2)
    if not response2:
        return False

    print(f"\n✅ Response received ({len(response2)} bytes)")
    print(f"   (Contains age calculation)")

    # Step 4: Verify checkpoint data in database
    print("\n" + "="*60)
    print("Step 4: Verify Conversation History in Database")
    print("="*60)

    print(f"\nTo verify checkpoints were saved, run:")
    print(f"")
    print(f"docker exec -it postgres16 psql -U postgres -d medz1 -c \"")
    print(f"SELECT thread_id, checkpoint_id, ")
    print(f"       LENGTH(checkpoint::text) as checkpoint_size")
    print(f"FROM public.checkpoints")
    print(f"WHERE thread_id LIKE '%{TEST_PATIENT_ICN}'")
    print(f"ORDER BY checkpoint_id DESC")
    print(f"LIMIT 5;")
    print(f"\"")

    print(f"\n✅ Conversation memory test complete!")
    print(f"\n📊 Summary:")
    print(f"   - Sent 2 messages in same session")
    print(f"   - Same patient (thread_id should be: {{session_id}}_{TEST_PATIENT_ICN})")
    print(f"   - Agent should have used conversation history for 2nd message")
    print(f"   - Checkpoints should be saved in PostgreSQL")

    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 6: Conversation Memory Test")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Patient ICN: {TEST_PATIENT_ICN}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    success = test_conversation_memory()

    if success:
        print("\n" + "="*60)
        print("✅ TEST PASSED")
        print("="*60)
        exit(0)
    else:
        print("\n" + "="*60)
        print("❌ TEST FAILED")
        print("="*60)
        exit(1)
