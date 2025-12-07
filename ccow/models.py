# -----------------------------------------------------------
# models.py
# -----------------------------------------------------------

from datetime import datetime, timezone
from typing import Optional, Literal

from pydantic import BaseModel, Field


class PatientContext(BaseModel):
    """Represents the active patient context stored in the vault."""

    patient_id: str = Field(..., description="Canonical patient identifier (e.g., ICN)")
    set_by: str = Field(..., description="Application or source that set this context")
    set_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp when the context was last set",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "1234567V890123",
                "set_by": "med-z1",
                "set_at": "2025-12-06T15:30:00.000Z",
            }
        }


class SetPatientContextRequest(BaseModel):
    """Request body for setting the active patient context."""

    patient_id: str = Field(..., min_length=1, description="Patient identifier")
    set_by: str = Field(
        default="med-z1",
        min_length=1,
        description="Application name setting the context",
    )


class ClearPatientContextRequest(BaseModel):
    """Optional request body for clearing context with metadata."""

    cleared_by: Optional[str] = Field(
        default=None,
        description="Application name clearing the context",
    )


class ContextHistoryEntry(BaseModel):
    """Represents a historical context change event."""

    action: Literal["set", "clear"] = Field(
        ...,
        description="Type of action performed: 'set' or 'clear'",
    )
    patient_id: Optional[str] = Field(
        default=None,
        description="Patient identifier (None if context was cleared)",
    )
    actor: str = Field(
        ...,
        description="Application that performed the action",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of the action",
    )