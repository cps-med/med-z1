# ---------------------------------------------------------------------
# main.py
# ---------------------------------------------------------------------
# FastAPI application providing HTTP REST API for CCOW Context Vault.
#
# Exposes the shared ContextVault singleton (from vault.py) via HTTP
# endpoints, enabling distributed applications to synchronize patient
# context across the med-z1 ecosystem. This is the production interface
# for context management (vs. direct vault access in test scripts).
#
# REST API Endpoints:
# - GET  /                       - Service info
# - GET  /ccow/health            - Health check
# - GET  /ccow/active-patient    - Get current patient context
# - PUT  /ccow/active-patient    - Set/update patient context
# - DELETE /ccow/active-patient  - Clear patient context
# - GET  /ccow/history           - Get context change history
#
# Key technical considerations:
# - Uses singleton vault instance from vault.py (thread-safe)
# - Pydantic models (models.py) for request/response validation
# - CORS enabled for development (tighten for production)
# - Returns 404 when no active context (vs. null/empty)
# - All timestamps in UTC (ISO 8601 with 'Z' suffix)
#
# Auto-generated API docs available at:
# - Swagger UI: http://localhost:8001/docs
# - ReDoc: http://localhost:8001/redoc
# ---------------------------------------------------------------------

from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .vault import vault
from .models import (
    PatientContext,
    SetPatientContextRequest,
    ClearPatientContextRequest,
    ContextHistoryEntry,
)

app = FastAPI(
    title="CCOW Context Vault",
    description="Simplified CCOW-style patient context synchronization service",
    version="1.0.0",
)

# CORS configuration (development-friendly; tighten for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production, restrict to known frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint for quick service introspection."""
    return {
        "service": "ccow",
        "message": "CCOW Context Vault is running",
        "version": "1.0.0",
    }


@app.get("/ccow/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ccow-vault",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@app.get("/ccow/active-patient", response_model=PatientContext)
async def get_active_patient():
    """Get the current active patient context."""
    context = vault.get_current()
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context",
        )
    return context


@app.put("/ccow/active-patient", response_model=PatientContext)
async def set_active_patient(request: SetPatientContextRequest):
    """Set or update the active patient context."""
    context = vault.set_context(
        patient_id=request.patient_id,
        set_by=request.set_by,
    )
    return context


@app.delete("/ccow/active-patient", status_code=status.HTTP_204_NO_CONTENT)
async def clear_active_patient(request: Optional[ClearPatientContextRequest] = None):
    """Clear the active patient context."""
    cleared_by = request.cleared_by if request else None
    cleared = vault.clear_context(cleared_by=cleared_by)

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active patient context to clear",
        )

    return None


@app.get("/ccow/history")
async def get_context_history():
    """Get recent context change history."""
    history: list[ContextHistoryEntry] = vault.get_history()
    return {"history": history}
