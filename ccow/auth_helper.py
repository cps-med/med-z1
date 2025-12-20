# ---------------------------------------------------------------------
# auth_helper.py
# ---------------------------------------------------------------------
# Session validation and user extraction for CCOW Context Vault.
#
# This module provides functions to validate session cookies and extract
# user information from med-z1's authentication system. The CCOW vault
# uses these functions to ensure requests are authenticated and to
# determine which user's context to operate on.
#
# Security Model:
# - CCOW vault validates session_id cookie against auth.sessions table
# - user_id is extracted from validated session (not trusted from request body)
# - This prevents user_id spoofing attacks
#
# Integration with med-z1 Auth:
# - Directly queries auth.sessions and auth.users tables
# - Uses same DATABASE_URL as med-z1 app
# - Validates is_active and expires_at for each session
#
# Version: v2.0 (Multi-User Enhancement)
# ---------------------------------------------------------------------

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import logging

from config import DATABASE_URL

logger = logging.getLogger(__name__)

# Create database engine (shared with med-z1 app)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,  # Set to True to see SQL queries in logs
)


def get_user_from_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Validate session and retrieve user information.

    This function performs the following security checks:
    1. Session exists in database (auth.sessions)
    2. Session is active (is_active = TRUE)
    3. Session has not expired (expires_at > NOW())
    4. User account exists and is active (auth.users.is_active = TRUE)

    Args:
        session_id: Session UUID from cookie

    Returns:
        Dictionary with user info if session is valid:
        {
            "user_id": str,        # User UUID
            "email": str,          # User email
            "display_name": str,   # User display name
        }
        Returns None if session is invalid or expired.

    Security Notes:
        - This is the authoritative source of user_id for CCOW operations
        - user_id from this function is trusted for context isolation
        - Never trust user_id from request body - always validate via session
    """
    query = text("""
        SELECT
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
                logger.warning(f"Session not found: {session_id}")
                return None

            # Extract fields
            user_id = str(row[0])
            session_active = row[1]
            expires_at = row[2]
            email = row[3]
            display_name = row[4]
            user_active = row[5]

            # Validate session is active
            if not session_active:
                logger.warning(f"Session {session_id} is not active")
                return None

            # Validate user account is active
            if not user_active:
                logger.warning(f"User {email} account is not active")
                return None

            # Validate session has not expired
            # Use timezone-naive comparison if expires_at is timezone-naive
            if expires_at.tzinfo is None:
                now = datetime.now()  # Local time, no timezone
            else:
                now = datetime.now(timezone.utc)  # UTC time

            if expires_at < now:
                logger.warning(
                    f"Session {session_id} has expired "
                    f"(expired at {expires_at}, now is {now})"
                )
                return None

            # Session is valid - return user info
            return {
                "user_id": user_id,
                "email": email,
                "display_name": display_name,
            }

    except Exception as e:
        logger.error(f"Error validating session {session_id}: {e}")
        return None
