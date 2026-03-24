#!/usr/bin/env python3
"""
Test script for auth.py database functions.
Tests user queries, password verification, session management, and audit logging.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.db import auth

def test_get_user_by_email():
    """Test getting user by email."""
    print("\n=== Test: get_user_by_email ===")

    email = "clinician.alpha@va.gov"
    user = auth.get_user_by_email(email)

    if user:
        print(f"✓ Found user: {user['display_name']}")
        print(f"  Email: {user['email']}")
        print(f"  User ID: {user['user_id']}")
        print(f"  Home Site: {user['home_site_sta3n']}")
        print(f"  Active: {user['is_active']}")
        return user
    else:
        print(f"✗ User not found for email: {email}")
        return None


def test_get_user_by_id(user_id):
    """Test getting user by ID."""
    print("\n=== Test: get_user_by_id ===")

    user = auth.get_user_by_id(user_id)

    if user:
        print(f"✓ Found user: {user['display_name']}")
        print(f"  Email: {user['email']}")
        return True
    else:
        print(f"✗ User not found for ID: {user_id}")
        return False


def test_password_verification():
    """Test password verification."""
    print("\n=== Test: verify_password ===")

    email = "clinician.alpha@va.gov"
    user = auth.get_user_by_email(email)

    if not user:
        print("✗ Cannot test password - user not found")
        return False

    # Test correct password
    correct_password = "VaDemo2025!"
    is_valid = auth.verify_password(correct_password, user['password_hash'])

    if is_valid:
        print(f"✓ Correct password verified successfully")
    else:
        print(f"✗ Correct password failed verification")
        return False

    # Test incorrect password
    wrong_password = "WrongPassword123!"
    is_valid = auth.verify_password(wrong_password, user['password_hash'])

    if not is_valid:
        print(f"✓ Incorrect password correctly rejected")
        return True
    else:
        print(f"✗ Incorrect password was accepted (should fail!)")
        return False


def test_session_management(user_id):
    """Test session creation, retrieval, extension, and invalidation."""
    print("\n=== Test: Session Management ===")

    # Create session
    print("Creating session...")
    session_id = auth.create_session(
        user_id=user_id,
        ip_address="127.0.0.1",
        user_agent="Test Script"
    )

    if not session_id:
        print("✗ Failed to create session")
        return False

    print(f"✓ Created session: {session_id}")

    # Get session
    print("Retrieving session...")
    session = auth.get_session(session_id)

    if not session:
        print("✗ Failed to retrieve session")
        return False

    print(f"✓ Retrieved session")
    print(f"  User ID: {session['user_id']}")
    print(f"  Created: {session['created_at']}")
    print(f"  Expires: {session['expires_at']}")
    print(f"  Active: {session['is_active']}")

    # Extend session
    print("Extending session...")
    extended = auth.extend_session(session_id)

    if not extended:
        print("✗ Failed to extend session")
        return False

    print(f"✓ Extended session")

    # Get updated session
    updated_session = auth.get_session(session_id)
    if updated_session and updated_session['last_activity_at'] != session['last_activity_at']:
        print(f"✓ Session activity timestamp updated")

    # Invalidate session
    print("Invalidating session...")
    invalidated = auth.invalidate_session(session_id)

    if not invalidated:
        print("✗ Failed to invalidate session")
        return False

    print(f"✓ Invalidated session")

    # Verify session is inactive
    inactive_session = auth.get_session(session_id)
    if inactive_session is None:
        print(f"✓ Session correctly returns None when inactive")
        return True
    else:
        print(f"✗ Session still active after invalidation")
        return False


def test_audit_logging():
    """Test audit event logging."""
    print("\n=== Test: Audit Logging ===")

    # Log successful login
    success = auth.log_audit_event(
        event_type="login",
        email="clinician.alpha@va.gov",
        ip_address="127.0.0.1",
        user_agent="Test Script",
        success=True
    )

    if success:
        print("✓ Logged successful login event")
    else:
        print("✗ Failed to log successful login")
        return False

    # Log failed login
    success = auth.log_audit_event(
        event_type="login_failed",
        email="clinician.alpha@va.gov",
        ip_address="127.0.0.1",
        user_agent="Test Script",
        success=False,
        failure_reason="Invalid password"
    )

    if success:
        print("✓ Logged failed login event")
        return True
    else:
        print("✗ Failed to log failed login")
        return False


def test_invalidate_user_sessions(user_id):
    """Test invalidating all user sessions."""
    print("\n=== Test: Invalidate User Sessions ===")

    # Create 2 sessions
    session1 = auth.create_session(user_id, "127.0.0.1", "Browser 1")
    session2 = auth.create_session(user_id, "127.0.0.1", "Browser 2")

    print(f"Created 2 sessions: {session1}, {session2}")

    # Invalidate all
    success = auth.invalidate_user_sessions(user_id)

    if not success:
        print("✗ Failed to invalidate user sessions")
        return False

    print("✓ Invalidated all user sessions")

    # Verify both are inactive
    s1 = auth.get_session(session1)
    s2 = auth.get_session(session2)

    if s1 is None and s2 is None:
        print("✓ Both sessions correctly inactive")
        return True
    else:
        print("✗ Sessions still active after invalidation")
        return False


def test_update_last_login(user_id):
    """Test updating last login timestamp."""
    print("\n=== Test: Update Last Login ===")

    success = auth.update_last_login(user_id)

    if success:
        print("✓ Updated last login timestamp")

        # Verify update
        user = auth.get_user_by_id(user_id)
        if user and user['last_login_at']:
            print(f"  Last login: {user['last_login_at']}")
            return True
    else:
        print("✗ Failed to update last login")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing app/db/auth.py Database Functions")
    print("="*60)

    # Test 1: Get user by email
    user = test_get_user_by_email()
    if not user:
        print("\n✗ Cannot continue tests without valid user")
        return

    user_id = user['user_id']

    # Test 2: Get user by ID
    test_get_user_by_id(user_id)

    # Test 3: Password verification
    test_password_verification()

    # Test 4: Session management
    test_session_management(user_id)

    # Test 5: Audit logging
    test_audit_logging()

    # Test 6: Invalidate user sessions
    test_invalidate_user_sessions(user_id)

    # Test 7: Update last login
    test_update_last_login(user_id)

    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
