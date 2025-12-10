# ---------------------------------------------------------------------
# app/utils/ccow_client.py
# ---------------------------------------------------------------------
# CCOW Context Vault Client Utility
# Provides convenience functions for med-z1/app to interact
# with the CCOW vault.
# ---------------------------------------------------------------------

from __future__ import annotations
import logging
from typing import Optional
import requests
from config import CCOW_ENABLED, CCOW_URL

logger = logging.getLogger(__name__)


class CCOWClient:
    """Simple HTTP client for interacting with the CCOW Context Vault."""

    def __init__(self, base_url: str = CCOW_URL, enabled: bool = CCOW_ENABLED):
        self.base_url = base_url.rstrip("/")
        self.enabled = enabled

    def set_active_patient(self, patient_id: str, set_by: str = "med-z1") -> bool:
        """
        Notify CCOW vault of an active patient change.

        Args:
            patient_id: ICN of the patient to set
            set_by: Application name setting the context

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            logger.debug("CCOW is disabled; skipping set_active_patient call")
            return False

        try:
            response = requests.put(
                f"{self.base_url}/ccow/active-patient",
                json={"patient_id": patient_id, "set_by": set_by},
                timeout=2.0,
            )
            response.raise_for_status()
            logger.info("Set CCOW active patient context to %s", patient_id)
            return True
        except requests.RequestException as exc:
            logger.error("Failed to set CCOW context: %s", exc)
            return False

    def get_active_patient(self) -> Optional[str]:
        """
        Retrieve the current patient_id (ICN) from CCOW.

        Returns:
            patient_id if set, or None if no active context or on error.
        """
        if not self.enabled:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/ccow/active-patient",
                timeout=2.0,
            )
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return data.get("patient_id")
        except requests.RequestException as exc:
            logger.error("Failed to get CCOW context: %s", exc)
            return None

    def clear_active_patient(self, cleared_by: str = "med-z1") -> bool:
        """
        Clear the active patient context in CCOW.

        Args:
            cleared_by: Application name clearing the context

        Returns:
            True if successful, False otherwise.
        """
        if not self.enabled:
            return False

        try:
            response = requests.delete(
                f"{self.base_url}/ccow/active-patient",
                json={"cleared_by": cleared_by},
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