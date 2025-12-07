# ---------------------------------------------------------------------
# vault.py
# ---------------------------------------------------------------------
# Thread-safe in-memory vault for CCOW patient context management.
#
# The ContextVault maintains the current active patient context and
# a rolling history of context change events (set/clear actions).
# This enables CCOW-style context synchronization across multiple
# applications in the med-z1 ecosystem.
#
# Key technical considerations:
# - Thread-safe: Uses threading.Lock for concurrent access safety
# - In-memory storage: Fast access, but state lost on service restart
# - Singleton pattern: Single shared vault instance (line 78)
# - UTC timestamps: All datetime fields use UTC for consistency across
#   distributed VA environment (multiple time zones, facilities)
# - Rolling history: Bounded deque (max 20 entries) prevents unbounded
#   memory growth
#
# Usage:
# - Direct access: test_vault_manual.py (testing/debugging)
# - HTTP access: ccow/main.py FastAPI endpoints (production)
# ---------------------------------------------------------------------

import threading
from collections import deque
from datetime import datetime, timezone
from typing import Optional

from .models import PatientContext, ContextHistoryEntry


class ContextVault:
    """Thread-safe in-memory vault for active patient context."""

    def __init__(self, max_history: int = 20):
        self._lock = threading.Lock()
        self._current: Optional[PatientContext] = None
        self._history: deque[ContextHistoryEntry] = deque(maxlen=max_history)

    def get_current(self) -> Optional[PatientContext]:
        """Retrieve the current active patient context, or None if not set."""
        with self._lock:
            return self._current

    def set_context(self, patient_id: str, set_by: str) -> PatientContext:
        """Set the active patient context and record a history entry."""
        with self._lock:
            context = PatientContext(
                patient_id=patient_id,
                set_by=set_by,
                set_at=datetime.now(timezone.utc),
            )

            self._current = context

            self._history.append(
                ContextHistoryEntry(
                    action="set",
                    patient_id=patient_id,
                    actor=set_by,
                    timestamp=context.set_at,
                )
            )

            return context

    def clear_context(self, cleared_by: Optional[str] = None) -> bool:
        """
        Clear the active patient context.

        Returns:
            True if there was an active context that was cleared,
            False if there was no active context.
        """
        with self._lock:
            if self._current is None:
                return False

            self._current = None
            self._history.append(
                ContextHistoryEntry(
                    action="clear",
                    patient_id=None,
                    actor=cleared_by or "unknown",
                    timestamp=datetime.now(timezone.utc),
                )
            )
            return True

    def get_history(self) -> list[ContextHistoryEntry]:
        """Return a snapshot list of historical context change events."""
        with self._lock:
            return list(self._history)


# Global singleton instance used by the FastAPI app
vault = ContextVault(max_history=20)
