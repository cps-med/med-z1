# ---------------------------------------------------------------------
# app/utils/template_context.py
# ---------------------------------------------------------------------
# Template Context Utilities
# Provides helper functions for building template contexts with
# common data like authenticated user information.
# ---------------------------------------------------------------------

from typing import Dict, Any
from fastapi import Request


def get_base_context(request: Request, **kwargs) -> Dict[str, Any]:
    """
    Build base template context with authenticated user and custom data.

    This helper ensures all templates have access to:
    - request: FastAPI Request object (required by Jinja2Templates)
    - user: Authenticated user from request.state.user (injected by AuthMiddleware)
    - **kwargs: Any additional context data specific to the route

    Args:
        request: FastAPI Request object
        **kwargs: Additional context data to merge

    Returns:
        Dictionary with base context and custom data merged

    Example:
        return templates.TemplateResponse(
            "dashboard.html",
            get_base_context(
                request,
                patient=patient,
                active_page="dashboard"
            )
        )
    """
    context = {
        "request": request,
        "user": getattr(request.state, "user", None),
    }
    context.update(kwargs)
    return context
