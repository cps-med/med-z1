# ---------------------------------------------------------------------
# app/utils/ccow_client.py
# ---------------------------------------------------------------------
# CCOW Context Vault Client Utility
#
# Version: v2.0 (Multi-User Enhancement)
#
# Provides convenience functions for med-z1/app to interact with the
# CCOW vault. v2.0 supports per-user context isolation by forwarding
# session cookies to the CCOW vault for authentication and user extraction.
#
# v2.0 Changes:
# - All methods now accept Request object to forward session cookie
# - CCOW vault extracts user_id from session (no explicit passing)
# - Added get_active_patient_context() for full context metadata
# - Improved error handling and logging
#
# Usage:
#   from app.utils.ccow_client import ccow_client
#   from fastapi import Request
#
#   @router.get("/patient/{icn}")
#   async def patient_overview(icn: str, request: Request):
#       ccow_client.set_active_patient(request, icn)
#       # ...
# ---------------------------------------------------------------------

from __future__ import annotations
import logging
from typing import Optional, Dict, Any
import requests
from fastapi import Request
from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)


class CCOWClient:
    """
    HTTP client for interacting with the CCOW Context Vault.

    v2.0 changes:
    - Accepts Request object to forward session cookies
    - CCOW extracts user_id from session (no explicit passing)
    - Returns full context objects (not just patient_id)
    """

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(
        self,
        request: Request,
        patient_id: str,
        set_by: str = "med-z1"
    ) -> bool:
        """
        Set the active patient context for the current user.

        Args:
            request: FastAPI Request object (contains session cookie)
            patient_id: Patient ICN
            set_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise

        Security Note:
            user_id is extracted by CCOW vault from the session_id cookie.
            This prevents user_id spoofing attacks.
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping set_active_patient call")
            return False

        try:
            # Extract session cookie from request
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return False

            # Forward session cookie to CCOW vault
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                cookies={"session_id": session_id},
                timeout=2.0,
            )
            response.raise_for_status()

            # Extract user email from request.state if available
            user_email = "unknown"
            if hasattr(request.state, "user"):
                user_email = request.state.user.get("email", "unknown")

            logger.info(
                "Set CCOW active patient context to %s for user %s",
                patient_id,
                user_email
            )
            return True

        except requests.RequestException as exc:
            logger.error("Failed to set CCOW context: %s", exc)
            return False

    def get_active_patient(self, request: Request) -> Optional[str]:
        """
        Retrieve the current user's active patient ICN from CCOW.

        Args:
            request: FastAPI Request object (contains session cookie)

        Returns:
            Patient ICN if context exists, None otherwise

        Note:
            Returns only the patient_id for backward compatibility.
            Use get_active_patient_context() for full context metadata.
        """
        if not self.enabled:
            return None

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                cookies={"session_id": session_id},
                timeout=2.0,
            )

            if response.status_code == 404:
                return None  # No active context for this user

            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")

        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def get_active_patient_context(self, request: Request) -> Optional[Dict[str, Any]]:
        """
        Retrieve the full active patient context (including metadata).

        Args:
            request: FastAPI Request object (contains session cookie)

        Returns:
            Full PatientContext dict if exists, None otherwise
            {
                "user_id": str,
                "email": str,
                "patient_id": str,
                "set_by": str,
                "set_at": str (ISO 8601),
                "last_accessed_at": str (ISO 8601)
            }

        Example:
            context = ccow_client.get_active_patient_context(request)
            if context:
                patient_id = context["patient_id"]
                set_by = context["set_by"]
                set_at = context["set_at"]
        """
        if not self.enabled:
            return None

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                return None

            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                cookies={"session_id": session_id},
                timeout=2.0,
            )

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def clear_active_patient(
        self,
        request: Request,
        cleared_by: str = "med-z1"
    ) -> bool:
        """
        Clear the active patient context for the current user.

        Args:
            request: FastAPI Request object (contains session cookie)
            cleared_by: Application name (default: "med-z1")

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            session_id = request.cookies.get("session_id")
            if not session_id:
                logger.error("No session_id cookie found in request")
                return False

            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
                cookies={"session_id": session_id},
                timeout=2.0,
            )

            if response.status_code == 404:
                logger.warning("No active CCOW patient context to clear")
                return False

            response.raise_for_status()
            logger.info("Cleared CCOW active patient context")
            return True

        except requests.RequestException as exc:
            logger.error("Failed to clear CCOW context: %s", exc)
            return False


# Global client instance for convenience
ccow_client = CCOWClient()
