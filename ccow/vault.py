# ---------------------------------------------------------------------
# vault.py
# ---------------------------------------------------------------------
# Thread-safe in-memory vault for CCOW patient context management.
#
# Version: v2.0 (Multi-User Enhancement)
#
# The ContextVault maintains per-user active patient contexts and
# a rolling history of context change events (set/clear actions).
# This enables CCOW-style context synchronization across multiple
# applications in the med-z1 ecosystem with proper user isolation.
#
# Key technical considerations:
# - Thread-safe: Uses threading.Lock for concurrent access safety
# - In-memory storage: Fast access, but state lost on service restart
# - Singleton pattern: Single shared vault instance (bottom of file)
# - UTC timestamps: All datetime fields use UTC for consistency across
#   distributed VA environment (multiple time zones, facilities)
# - Rolling history: Bounded deque (max 100 entries) prevents unbounded
#   memory growth
# - Auto-cleanup: Stale contexts (inactive >24h) are automatically removed
#
# v2.0 Changes:
# - _contexts: Dict[user_id, PatientContext] (was: _current: Optional[PatientContext])
# - All methods take user_id parameter for context isolation
# - get_history() supports user-scoped and global filtering
# - cleanup_stale_contexts() prevents memory leaks
# - get_all_contexts() for admin/debugging
#
# Usage:
# - Direct access: test_vault_manual.py (testing/debugging)
# - HTTP access: ccow/main.py FastAPI endpoints (production)
# ---------------------------------------------------------------------

import threading
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List

from .models import PatientContext, ContextHistoryEntry


class ContextVault:
    """
    Thread-safe in-memory vault for per-user active patient contexts.

    Each user (identified by user_id from auth.users) maintains an independent
    active patient context. Contexts persist across med-z1 login/logout cycles
    and are shared across CCOW-aware applications (med-z1, CPRS, imaging).

    Key Design Choices:
    - user_id (not session_id) as key: Context survives app logout
    - Auto-cleanup of stale contexts: Prevent unbounded memory growth
    - User-scoped history: Privacy-focused, with admin override
    """

    def __init__(self, max_history: int = 100, cleanup_threshold_hours: int = 24):
        """
        Initialize the vault.

        Args:
            max_history: Maximum number of history entries to retain (default 100)
            cleanup_threshold_hours: Remove contexts inactive for this many hours (default 24)
        """
        self._lock = threading.Lock()

        # Core storage: user_id -> PatientContext
        self._contexts: Dict[str, PatientContext] = {}

        # History: All events from all users (tagged with user_id for filtering)
        self._history: deque[ContextHistoryEntry] = deque(maxlen=max_history)

        # Configuration
        self._cleanup_threshold = timedelta(hours=cleanup_threshold_hours)

    # -------------------------------------------------------------------------
    # Core Context Operations
    # -------------------------------------------------------------------------

    def get_context(self, user_id: str) -> Optional[PatientContext]:
        """
        Retrieve the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id

        Returns:
            PatientContext if user has active context, None otherwise
        """
        with self._lock:
            context = self._contexts.get(user_id)
            if context:
                # Update last_accessed_at (for cleanup logic)
                context.last_accessed_at = datetime.now(timezone.utc)
            return context

    def set_context(
        self,
        user_id: str,
        patient_id: str,
        set_by: str,
        email: Optional[str] = None
    ) -> PatientContext:
        """
        Set the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id
            patient_id: Patient ICN
            set_by: Application name (e.g., 'med-z1', 'cprs')
            email: User email for display/debugging (optional)

        Returns:
            The created PatientContext
        """
        with self._lock:
            now = datetime.now(timezone.utc)

            context = PatientContext(
                user_id=user_id,
                email=email,
                patient_id=patient_id,
                set_by=set_by,
                set_at=now,
                last_accessed_at=now,
            )

            # Store context for this user
            self._contexts[user_id] = context

            # Record in history
            self._history.append(
                ContextHistoryEntry(
                    action="set",
                    user_id=user_id,
                    email=email,
                    patient_id=patient_id,
                    actor=set_by,
                    timestamp=now,
                )
            )

            return context

    def clear_context(
        self,
        user_id: str,
        cleared_by: Optional[str] = None,
        email: Optional[str] = None
    ) -> bool:
        """
        Clear the active patient context for a specific user.

        Args:
            user_id: User UUID from auth.users.user_id
            cleared_by: Application name that cleared context (optional)
            email: User email for audit trail (optional)

        Returns:
            True if context was cleared, False if no context existed
        """
        with self._lock:
            if user_id not in self._contexts:
                return False

            # Remove context for this user
            del self._contexts[user_id]

            # Record in history
            self._history.append(
                ContextHistoryEntry(
                    action="clear",
                    user_id=user_id,
                    email=email,
                    patient_id=None,
                    actor=cleared_by or "unknown",
                    timestamp=datetime.now(timezone.utc),
                )
            )

            return True

    # -------------------------------------------------------------------------
    # History Operations
    # -------------------------------------------------------------------------

    def get_history(
        self,
        user_id: Optional[str] = None,
        scope: str = "user"
    ) -> List[ContextHistoryEntry]:
        """
        Retrieve context change history, optionally filtered by user.

        Args:
            user_id: User UUID to filter by (required if scope='user')
            scope: Scope of history to return:
                - 'user': Only events for specified user_id
                - 'global': All events from all users

        Returns:
            List of ContextHistoryEntry objects (most recent first)
        """
        with self._lock:
            if scope == "global":
                # Return all history
                return list(self._history)
            elif scope == "user":
                # Filter history for specific user
                if not user_id:
                    raise ValueError("user_id required for scope='user'")
                return [
                    entry for entry in self._history
                    if entry.user_id == user_id
                ]
            else:
                raise ValueError(f"Invalid scope: {scope}. Must be 'user' or 'global'")

    # -------------------------------------------------------------------------
    # Admin / Debugging Operations
    # -------------------------------------------------------------------------

    def get_all_contexts(self) -> List[PatientContext]:
        """
        Retrieve all active user contexts (admin/debugging).

        Returns:
            List of all PatientContext objects
        """
        with self._lock:
            return list(self._contexts.values())

    def get_context_count(self) -> int:
        """Get the number of active user contexts."""
        with self._lock:
            return len(self._contexts)

    # -------------------------------------------------------------------------
    # Cleanup Operations
    # -------------------------------------------------------------------------

    def cleanup_stale_contexts(self) -> int:
        """
        Remove contexts that haven't been accessed in cleanup_threshold_hours.

        This prevents unbounded memory growth from users who never explicitly
        clear their context.

        Returns:
            Number of contexts removed
        """
        with self._lock:
            now = datetime.now(timezone.utc)
            stale_threshold = now - self._cleanup_threshold

            # Find stale user_ids
            stale_user_ids = [
                user_id for user_id, ctx in self._contexts.items()
                if ctx.last_accessed_at < stale_threshold
            ]

            # Remove stale contexts
            for user_id in stale_user_ids:
                context = self._contexts[user_id]
                del self._contexts[user_id]

                # Log cleanup in history
                self._history.append(
                    ContextHistoryEntry(
                        action="clear",
                        user_id=user_id,
                        email=context.email,
                        patient_id=None,
                        actor="system:cleanup",
                        timestamp=now,
                    )
                )

            return len(stale_user_ids)


# Global singleton instance used by the FastAPI app
vault = ContextVault(max_history=100, cleanup_threshold_hours=24)
