# ---------------------------------------------------------------------
# models.py
# ---------------------------------------------------------------------
# Pydantic data models for the CCOW Context Vault service.
#
# Version: v2.0 (Multi-User Enhancement)
#
# Defines the core data structures used throughout the CCOW vault:
# - PatientContext: Active patient context (per-user in v2.0)
# - ContextHistoryEntry: Historical context change events (user-tagged)
# - Request/Response models for FastAPI endpoints
#
# v2.0 Changes:
# - PatientContext now includes user_id, email, last_accessed_at
# - ContextHistoryEntry includes user_id, email for filtering
# - New response models for multi-user scenarios
#
# These Pydantic BaseModels provide:
# - Automatic type validation (e.g., action must be "set" or "clear")
# - JSON serialization/deserialization for HTTP APIs
# - OpenAPI schema generation for FastAPI documentation
# - IDE autocomplete and type checking support
#
# All datetime fields use UTC timezone for consistency across
# the distributed VA environment (see vault.py for rationale).
# ---------------------------------------------------------------------

from datetime import datetime, timezone
from typing import Optional, Literal, List

from pydantic import BaseModel, Field


class PatientContext(BaseModel):
    """Represents the active patient context for a specific user (v2.0)."""

    # v2.0: User identification
    user_id: str = Field(..., description="User UUID from auth.users.user_id")
    email: Optional[str] = Field(None, description="User email for display/debugging")

    # Patient context (unchanged from v1.1)
    patient_id: str = Field(..., description="Canonical patient identifier (e.g., ICN)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the context was last set",
    )

    # v2.0: Context lifecycle tracking
    last_accessed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of last access (for cleanup)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "clinician.alpha@va.gov",
                "patient_id": "1012845331V153053",
                "set_by": "med-z1",
                "set_at": "2025-12-20T15:30:00.000Z",
                "last_accessed_at": "2025-12-20T15:45:00.000Z"
            }
        }


class SetPatientContextRequest(BaseModel):
    """Request body for setting the active patient context (v2.0)."""

    patient_id: str = Field(..., min_length=1, description="Patient identifier (ICN)")
    set_by: str = Field(
        default="med-z1",
        min_length=1,
        description="Application name setting the context",
    )

    # NOTE: user_id is NOT in request body - extracted from session cookie
    # This prevents user_id spoofing attacks


class ClearPatientContextRequest(BaseModel):
    """Optional request body for clearing context with metadata (v2.0)."""

    cleared_by: Optional[str] = Field(
        default=None,
        description="Application name clearing the context",
    )

    # NOTE: user_id extracted from session, not request body


class ContextHistoryEntry(BaseModel):
    """Represents a historical context change event (v2.0 - user-tagged)."""

    action: Literal["set", "clear"] = Field(
        ...,
        description="Type of action performed: 'set' or 'clear'",
    )

    # v2.0: User identification for filtering
    user_id: str = Field(
        ...,
        description="User UUID who performed the action",
    )
    email: Optional[str] = Field(
        None,
        description="User email for display (optional)",
    )

    # Context information (unchanged from v1.1)
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier (None if context was cleared)",
    )
    actor: str = Field(
        ...,
        description="Application that performed the action (e.g., 'med-z1', 'cprs')",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of the action",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "action": "set",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "clinician.alpha@va.gov",
                "patient_id": "1012845331V153053",
                "actor": "med-z1",
                "timestamp": "2025-12-20T15:30:00.000Z"
            }
        }


# ---------------------------------------------------------------------
# v2.0: New Response Models for Multi-User Scenarios
# ---------------------------------------------------------------------


class GetAllActiveContextsResponse(BaseModel):
    """Response for GET /ccow/active-patients (admin/debugging)."""

    contexts: List[PatientContext] = Field(
        ...,
        description="All active user contexts"
    )
    total_count: int = Field(..., description="Number of active contexts")

    class Config:
        json_schema_extra = {
            "example": {
                "contexts": [
                    {
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "clinician.alpha@va.gov",
                        "patient_id": "1012845331V153053",
                        "set_by": "med-z1",
                        "set_at": "2025-12-20T10:00:00.000Z",
                        "last_accessed_at": "2025-12-20T10:30:00.000Z"
                    },
                    {
                        "user_id": "456e7890-abcd-12d3-a456-426614174001",
                        "email": "clinician.bravo@va.gov",
                        "patient_id": "1013012345V678901",
                        "set_by": "cprs",
                        "set_at": "2025-12-20T09:45:00.000Z",
                        "last_accessed_at": "2025-12-20T10:15:00.000Z"
                    }
                ],
                "total_count": 2
            }
        }


class GetHistoryResponse(BaseModel):
    """Response for GET /ccow/history with scope filtering (v2.0)."""

    history: List[ContextHistoryEntry] = Field(..., description="Context change events")
    scope: Literal["user", "global"] = Field(
        ...,
        description="Scope of history returned"
    )
    total_count: int = Field(..., description="Number of events returned")
    user_id: Optional[str] = Field(
        None,
        description="User ID if scope=user"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "history": [
                    {
                        "action": "set",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "clinician.alpha@va.gov",
                        "patient_id": "1012845331V153053",
                        "actor": "med-z1",
                        "timestamp": "2025-12-20T15:30:00.000Z"
                    },
                    {
                        "action": "clear",
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "clinician.alpha@va.gov",
                        "patient_id": None,
                        "actor": "med-z1",
                        "timestamp": "2025-12-20T14:20:00.000Z"
                    }
                ],
                "scope": "user",
                "total_count": 2,
                "user_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


class CleanupResponse(BaseModel):
    """Response for POST /ccow/cleanup (admin/debugging)."""

    removed_count: int = Field(..., description="Number of stale contexts removed")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "removed_count": 3,
                "message": "Cleaned up 3 stale contexts"
            }
        }
