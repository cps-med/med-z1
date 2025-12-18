# ---------------------------------------------------------------------
# app/db/auth.py
# ---------------------------------------------------------------------
# Authentication Database Query Layer
# Provides functions to query auth schema tables in PostgreSQL
# This module encapsulates all SQL queries for user authentication,
# session management, and audit logging
# ---------------------------------------------------------------------

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import bcrypt
import logging
from config import DATABASE_URL, AUTH_CONFIG

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Simple pooling for development
    echo=False,  # Set to True to see SQL queries in logs
)


# ---------------------------------------------------------------------
# User Query Functions
# ---------------------------------------------------------------------

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Get user by email address.

    Args:
        email: User email address (username for login)

    Returns:
        Dictionary with user data or None if not found
    """
    query = text("""
        SELECT
            user_id,
            email,
            password_hash,
            display_name,
            first_name,
            last_name,
            home_site_sta3n,
            is_active,
            is_locked,
            failed_login_attempts,
            last_login_at,
            created_at,
            updated_at
        FROM auth.users
        WHERE email = :email
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"email": email})
            row = result.fetchone()

            if row:
                return {
                    "user_id": str(row[0]),  # Convert UUID to string
                    "email": row[1],
                    "password_hash": row[2],
                    "display_name": row[3],
                    "first_name": row[4],
                    "last_name": row[5],
                    "home_site_sta3n": row[6],
                    "is_active": row[7],
                    "is_locked": row[8],
                    "failed_login_attempts": row[9],
                    "last_login_at": row[10],
                    "created_at": row[11],
                    "updated_at": row[12],
                }
            return None

    except Exception as e:
        logger.error(f"Error getting user by email {email}: {e}")
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get user by user_id (UUID).

    Args:
        user_id: User UUID

    Returns:
        Dictionary with user data or None if not found
    """
    query = text("""
        SELECT
            user_id,
            email,
            display_name,
            first_name,
            last_name,
            home_site_sta3n,
            is_active,
            is_locked,
            last_login_at
        FROM auth.users
        WHERE user_id = CAST(:user_id AS UUID)
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()

            if row:
                return {
                    "user_id": str(row[0]),  # Convert UUID to string
                    "email": row[1],
                    "display_name": row[2],
                    "first_name": row[3],
                    "last_name": row[4],
                    "home_site_sta3n": row[5],
                    "is_active": row[6],
                    "is_locked": row[7],
                    "last_login_at": row[8],
                }
            return None

    except Exception as e:
        logger.error(f"Error getting user by ID {user_id}: {e}")
        return None


# ---------------------------------------------------------------------
# Password Verification Functions
# ---------------------------------------------------------------------

def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plain password against a bcrypt hash.

    Args:
        plain_password: Plain text password to verify
        password_hash: Bcrypt hash from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def hash_password(plain_password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        plain_password: Plain text password

    Returns:
        Bcrypt hash string
    """
    salt = bcrypt.gensalt(rounds=AUTH_CONFIG["bcrypt_rounds"])
    password_hash = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


# ---------------------------------------------------------------------
# Session Management Functions
# ---------------------------------------------------------------------

def create_session(
    user_id: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[str]:
    """
    Create a new session for a user.

    Args:
        user_id: User UUID
        ip_address: Client IP address (optional)
        user_agent: Client user agent string (optional)

    Returns:
        Session ID (UUID string) if successful, None otherwise
    """
    timeout_minutes = AUTH_CONFIG["session_timeout_minutes"]
    now = datetime.now()
    expires_at = now + timedelta(minutes=timeout_minutes)

    query = text("""
        INSERT INTO auth.sessions (
            user_id,
            created_at,
            last_activity_at,
            expires_at,
            is_active,
            ip_address,
            user_agent
        ) VALUES (
            CAST(:user_id AS UUID),
            :created_at,
            :last_activity_at,
            :expires_at,
            TRUE,
            :ip_address,
            :user_agent
        )
        RETURNING session_id
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "created_at": now,
                "last_activity_at": now,
                "expires_at": expires_at,
                "ip_address": ip_address,
                "user_agent": user_agent,
            })
            conn.commit()
            row = result.fetchone()
            if row:
                return str(row[0])  # Return session_id as string
            return None

    except Exception as e:
        logger.error(f"Error creating session for user {user_id}: {e}")
        return None


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session by session_id.

    Args:
        session_id: Session UUID

    Returns:
        Dictionary with session data or None if not found/expired
    """
    query = text("""
        SELECT
            session_id,
            user_id,
            created_at,
            last_activity_at,
            expires_at,
            is_active,
            ip_address,
            user_agent
        FROM auth.sessions
        WHERE session_id = CAST(:session_id AS UUID)
        AND is_active = TRUE
        LIMIT 1
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            row = result.fetchone()

            if row:
                return {
                    "session_id": str(row[0]),
                    "user_id": str(row[1]),
                    "created_at": row[2],
                    "last_activity_at": row[3],
                    "expires_at": row[4],
                    "is_active": row[5],
                    "ip_address": row[6],
                    "user_agent": row[7],
                }
            return None

    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        return None


def extend_session(session_id: str) -> bool:
    """
    Extend session expiration (update last_activity_at and expires_at).

    Args:
        session_id: Session UUID

    Returns:
        True if successful, False otherwise
    """
    timeout_minutes = AUTH_CONFIG["session_timeout_minutes"]
    now = datetime.now()
    new_expires_at = now + timedelta(minutes=timeout_minutes)

    query = text("""
        UPDATE auth.sessions
        SET
            last_activity_at = :last_activity_at,
            expires_at = :expires_at
        WHERE session_id = CAST(:session_id AS UUID)
        AND is_active = TRUE
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "session_id": session_id,
                "last_activity_at": now,
                "expires_at": new_expires_at,
            })
            conn.commit()
            return result.rowcount > 0

    except Exception as e:
        logger.error(f"Error extending session {session_id}: {e}")
        return False


def invalidate_session(session_id: str) -> bool:
    """
    Invalidate a session (mark as inactive).

    Args:
        session_id: Session UUID

    Returns:
        True if successful, False otherwise
    """
    query = text("""
        UPDATE auth.sessions
        SET is_active = FALSE
        WHERE session_id = CAST(:session_id AS UUID)
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"session_id": session_id})
            conn.commit()
            return result.rowcount > 0

    except Exception as e:
        logger.error(f"Error invalidating session {session_id}: {e}")
        return False


def invalidate_user_sessions(user_id: str) -> bool:
    """
    Invalidate all sessions for a user (single-session enforcement).

    Args:
        user_id: User UUID

    Returns:
        True if successful, False otherwise
    """
    query = text("""
        UPDATE auth.sessions
        SET is_active = FALSE
        WHERE user_id = CAST(:user_id AS UUID)
        AND is_active = TRUE
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            conn.commit()
            logger.info(f"Invalidated {result.rowcount} session(s) for user {user_id}")
            return True

    except Exception as e:
        logger.error(f"Error invalidating sessions for user {user_id}: {e}")
        return False


def update_last_login(user_id: str) -> bool:
    """
    Update user's last_login_at timestamp.

    Args:
        user_id: User UUID

    Returns:
        True if successful, False otherwise
    """
    query = text("""
        UPDATE auth.users
        SET last_login_at = :timestamp
        WHERE user_id = CAST(:user_id AS UUID)
    """)

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "timestamp": datetime.now(),
            })
            conn.commit()
            return result.rowcount > 0

    except Exception as e:
        logger.error(f"Error updating last login for user {user_id}: {e}")
        return False


# ---------------------------------------------------------------------
# Audit Logging Functions
# ---------------------------------------------------------------------

def log_audit_event(
    event_type: str,
    user_id: Optional[str] = None,
    email: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    success: Optional[bool] = None,
    failure_reason: Optional[str] = None,
    session_id: Optional[str] = None
) -> bool:
    """
    Log an authentication audit event.

    Args:
        event_type: Type of event (login, logout, login_failed, etc.)
        user_id: User UUID (optional)
        email: User email (optional)
        ip_address: Client IP (optional)
        user_agent: Client user agent (optional)
        success: Whether event succeeded (optional)
        failure_reason: Reason for failure (optional)
        session_id: Session UUID (optional)

    Returns:
        True if successful, False otherwise
    """
    query = text("""
        INSERT INTO auth.audit_logs (
            user_id,
            event_type,
            event_timestamp,
            email,
            ip_address,
            user_agent,
            success,
            failure_reason,
            session_id
        ) VALUES (
            CAST(:user_id AS UUID),
            :event_type,
            :event_timestamp,
            :email,
            :ip_address,
            :user_agent,
            :success,
            :failure_reason,
            CAST(:session_id AS UUID)
        )
    """)

    try:
        with engine.connect() as conn:
            conn.execute(query, {
                "user_id": user_id if user_id else None,
                "event_type": event_type,
                "event_timestamp": datetime.now(),
                "email": email,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                "failure_reason": failure_reason,
                "session_id": session_id if session_id else None,
            })
            conn.commit()
            return True

    except Exception as e:
        logger.error(f"Error logging audit event {event_type}: {e}")
        return False


# ---------------------------------------------------------------------
# Session Cleanup (Maintenance)
# ---------------------------------------------------------------------

def cleanup_expired_sessions() -> int:
    """
    Delete expired sessions from database (maintenance function).

    Returns:
        Number of sessions deleted
    """
    query = text("""
        DELETE FROM auth.sessions
        WHERE expires_at < :now
        OR (is_active = FALSE AND created_at < :cutoff)
    """)

    cutoff = datetime.now() - timedelta(days=7)  # Delete inactive sessions older than 7 days

    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                "now": datetime.now(),
                "cutoff": cutoff,
            })
            conn.commit()
            deleted_count = result.rowcount
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired/inactive session(s)")
            return deleted_count

    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        return 0
