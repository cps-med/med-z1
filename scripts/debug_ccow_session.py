#!/usr/bin/env python3
"""
Debug script to test CCOW session validation.

This script helps diagnose why CCOW context setting might be failing
by testing the session validation chain:
1. Check if session exists in database
2. Check if session is active and not expired
3. Test CCOW API with session cookie

Usage:
    python scripts/debug_ccow_session.py <session_id>
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from config import DATABASE_URL, CCOW_URL

def check_session_in_db(session_id: str):
    """Check if session exists and is valid in database."""
    print("\n" + "="*60)
    print("STEP 1: Checking session in database...")
    print("="*60)

    engine = create_engine(DATABASE_URL, echo=False)

    query = text("""
        SELECT
            s.session_id,
            s.user_id,
            s.is_active AS session_active,
            s.expires_at,
            u.email,
            u.display_name,
            u.is_active AS user_active
        FROM auth.sessions s
        JOIN auth.users u ON s.user_id = u.user_id
        WHERE s.session_id = CAST(:session_id AS UUID)
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            row = result.fetchone()

            if not row:
                print(f"❌ Session NOT FOUND in database: {session_id}")
                return False

            session_id_db = str(row[0])
            user_id = str(row[1])
            session_active = row[2]
            expires_at = row[3]
            email = row[4]
            display_name = row[5]
            user_active = row[6]

            print(f"✅ Session found in database")
            print(f"   Session ID: {session_id_db}")
            print(f"   User ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Display Name: {display_name}")
            print(f"   Session Active: {session_active}")
            print(f"   User Active: {user_active}")
            print(f"   Expires At: {expires_at}")

            # Check if session is active
            if not session_active:
                print(f"❌ Session is NOT ACTIVE")
                return False
            else:
                print(f"✅ Session is active")

            # Check if user is active
            if not user_active:
                print(f"❌ User account is NOT ACTIVE")
                return False
            else:
                print(f"✅ User account is active")

            # Check if session has expired
            # Use timezone-naive comparison if expires_at is timezone-naive
            if expires_at.tzinfo is None:
                now = datetime.now()  # Local time, no timezone
            else:
                now = datetime.now(timezone.utc)  # UTC time

            if expires_at < now:
                print(f"❌ Session EXPIRED at {expires_at} (now: {now})")
                return False
            else:
                time_remaining = expires_at - now
                print(f"✅ Session valid for {time_remaining}")

            return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_ccow_health():
    """Test CCOW vault health endpoint."""
    print("\n" + "="*60)
    print("STEP 2: Testing CCOW vault health...")
    print("="*60)

    try:
        response = requests.get(f"{CCOW_URL}/ccow/health", timeout=2.0)
        response.raise_for_status()
        data = response.json()
        print(f"✅ CCOW vault is healthy")
        print(f"   Service: {data.get('service')}")
        print(f"   Version: {data.get('version')}")
        print(f"   Active Contexts: {data.get('active_contexts')}")
        return True
    except Exception as e:
        print(f"❌ CCOW vault not responding: {e}")
        return False

def test_ccow_set_patient(session_id: str, patient_icn: str = "ICN100001"):
    """Test setting patient context via CCOW API."""
    print("\n" + "="*60)
    print("STEP 3: Testing CCOW set patient context...")
    print("="*60)

    print(f"Attempting to set patient: {patient_icn}")
    print(f"Using session_id: {session_id}")

    try:
        response = requests.put(
            f"{CCOW_URL}/ccow/active-patient",
            json={"patient_id": patient_icn, "set_by": "debug-script"},
            cookies={"session_id": session_id},
            timeout=2.0
        )

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully set patient context")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Patient ID: {data.get('patient_id')}")
            print(f"   Set By: {data.get('set_by')}")
            print(f"   Set At: {data.get('set_at')}")
            return True
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail')}")
            except:
                print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_ccow_get_patient(session_id: str):
    """Test getting patient context via CCOW API."""
    print("\n" + "="*60)
    print("STEP 4: Testing CCOW get patient context...")
    print("="*60)

    try:
        response = requests.get(
            f"{CCOW_URL}/ccow/active-patient",
            cookies={"session_id": session_id},
            timeout=2.0
        )

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved patient context")
            print(f"   User ID: {data.get('user_id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Patient ID: {data.get('patient_id')}")
            print(f"   Set By: {data.get('set_by')}")
            return True
        elif response.status_code == 404:
            print(f"ℹ️  No active patient context (404 Not Found)")
            return True  # This is OK, just means no context set
        elif response.status_code == 401:
            print(f"❌ Authentication failed (401 Unauthorized)")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail')}")
            except:
                print(f"   Response: {response.text}")
            return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/debug_ccow_session.py <session_id>")
        print("\nTo get your session_id:")
        print("1. Login to med-z1 app in browser")
        print("2. Open browser DevTools (F12)")
        print("3. Go to Application/Storage > Cookies")
        print("4. Copy the value of 'session_id' cookie")
        sys.exit(1)

    session_id = sys.argv[1].strip()

    print("\n" + "="*60)
    print("CCOW Session Validation Debug Script")
    print("="*60)
    print(f"Session ID: {session_id}")
    print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print(f"CCOW URL: {CCOW_URL}")

    # Run diagnostic steps
    step1_ok = check_session_in_db(session_id)
    step2_ok = test_ccow_health()
    step3_ok = test_ccow_set_patient(session_id) if step1_ok and step2_ok else False
    step4_ok = test_ccow_get_patient(session_id) if step3_ok else False

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Step 1 - Database Session Check: {'✅ PASS' if step1_ok else '❌ FAIL'}")
    print(f"Step 2 - CCOW Health Check: {'✅ PASS' if step2_ok else '❌ FAIL'}")
    print(f"Step 3 - Set Patient Context: {'✅ PASS' if step3_ok else '❌ FAIL'}")
    print(f"Step 4 - Get Patient Context: {'✅ PASS' if step4_ok else '❌ FAIL'}")

    if all([step1_ok, step2_ok, step3_ok, step4_ok]):
        print("\n✅ All tests passed! CCOW session validation is working.")
    else:
        print("\n❌ Some tests failed. See details above.")
        if not step1_ok:
            print("\n🔍 Troubleshooting: Session not valid in database.")
            print("   - Try logging out and logging back in to get fresh session")
            print("   - Check if session has expired")
            print("   - Verify user account is active")
        elif not step2_ok:
            print("\n🔍 Troubleshooting: CCOW vault not responding.")
            print("   - Ensure CCOW service is running: uvicorn ccow.main:app --reload --port 8001")
            print("   - Check CCOW_URL in config matches actual service URL")
        elif not step3_ok:
            print("\n🔍 Troubleshooting: Failed to set patient context.")
            print("   - Check CCOW service logs for errors")
            print("   - Verify session cookie is being passed correctly")

if __name__ == "__main__":
    main()
