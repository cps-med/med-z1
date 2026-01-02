# ---------------------------------------------------------------------
# app/routes/insight.py
# ---------------------------------------------------------------------
# AI Clinical Insights Routes
# Handles AI-powered clinical decision support chat interface.
# Returns HTML for HTMX-powered conversational UI with LangGraph agent.
# ---------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import logging
import markdown

from langchain_core.messages import HumanMessage, SystemMessage

from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context
from app.services.vista_cache import VistaSessionCache
from ai.agents.insight_agent import create_insight_agent
from ai.tools import ALL_TOOLS, set_request_context

# Page router for full insight pages (no prefix for flexibility)
page_router = APIRouter(tags=["insight-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

# Create LangGraph agent (singleton for app lifecycle)
logger.info("Initializing LangGraph Clinical Insights Agent")
insight_agent = create_insight_agent(ALL_TOOLS)
logger.info(f"Agent initialized with {len(ALL_TOOLS)} tools: {[tool.name for tool in ALL_TOOLS]}")


# ============================================
# Full Page Routes
# ============================================

@page_router.get("/insight")
async def insight_redirect(request: Request):
    """
    Redirect to current patient's insights page.
    Gets patient from CCOW and redirects to /insight/{icn}.
    If no patient selected, redirects to dashboard.
    """
    from app.utils.ccow_client import ccow_client

    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        logger.warning("No active patient in CCOW for insights page")
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url=f"/insight/{patient_icn}", status_code=303)


@page_router.get("/insight/{icn}", response_class=HTMLResponse)
async def get_insight_page(request: Request, icn: str):
    """
    AI Clinical Insights chat interface page.

    Displays chat-style conversational UI where clinicians can ask questions
    about the patient and receive AI-powered insights using the LangGraph agent.

    Features:
    - Chat message history (user + AI responses)
    - Suggested questions as clickable chips
    - Tool usage transparency ("Sources checked: DDI analyzer, Patient summary")
    - HTMX-powered message submission (no page reload)

    Args:
        icn: Patient ICN

    Returns:
        Full HTML page with chat interface
    """
    try:
        # Get patient demographics for header
        patient = get_patient_demographics(icn)

        if not patient:
            logger.warning(f"Patient {icn} not found for insights page")
            return templates.TemplateResponse(
                "insight.html",
                get_base_context(
                    request,
                    patient=None,
                    error="Patient not found",
                    active_page="insight"
                )
            )

        # Initial suggested questions
        suggested_questions = [
            "What are the key clinical risks for this patient?",
            "Are there any drug-drug interaction concerns?",
            "Summarize this patient's recent clinical activity",
        ]

        # Get Vista cache status for this patient
        cache_info = VistaSessionCache.get_cache_info(request, icn)

        logger.info(f"Loaded insights page for {icn} ({patient.get('name', 'Unknown')})")

        return templates.TemplateResponse(
            "insight.html",
            get_base_context(
                request,
                patient=patient,
                suggested_questions=suggested_questions,
                chat_messages=[],  # Empty on initial load
                cache_info=cache_info,  # Vista cache status
                active_page="insight"
            )
        )

    except Exception as e:
        logger.error(f"Error loading insights page for {icn}: {e}")
        return templates.TemplateResponse(
            "insight.html",
            get_base_context(
                request,
                patient=None,
                error=str(e),
                active_page="insight"
            )
        )


@page_router.post("/insight/chat", response_class=HTMLResponse)
async def post_chat_message(
    request: Request,
    icn: str = Form(...),
    message: str = Form(...),
):
    """
    Handle chat message submission via HTMX.

    Invokes LangGraph agent with user's question, returns AI response as HTML partial.
    The agent may call tools (check_ddi_risks, get_patient_summary) to gather data
    before synthesizing the final response.

    Args:
        icn: Patient ICN (from hidden form field)
        message: User's chat message

    Returns:
        HTML partial with user message + AI response (chat_message.html rendered twice)
    """
    try:
        # Get patient for context
        patient = get_patient_demographics(icn)

        if not patient:
            logger.error(f"Patient {icn} not found in chat handler")
            raise HTTPException(status_code=404, detail="Patient not found")

        patient_name = patient.get("name", "Unknown Patient")

        logger.info(f"Processing chat message for {icn}: '{message[:100]}...'")

        # Set request context for tools (enables Vista cache access)
        set_request_context(request)

        try:
            # Create system message with patient context
            system_message = SystemMessage(
                content=f"""You are a clinical decision support AI assistant analyzing patient data.

CURRENT PATIENT CONTEXT:
- Patient Name: {patient_name}
- Patient ICN: {icn}

You have access to tools that can query this patient's clinical data.
If the user has refreshed data from Vista during this session, tools will automatically use that cached data.
When the user asks questions about "this patient" or "the patient", they are referring to {patient_name} (ICN: {icn}).

Use the available tools to gather relevant clinical information and provide evidence-based insights.
Always cite which data sources you used in your analysis (PostgreSQL, Vista, or both)."""
            )

            # Invoke LangGraph agent with system context + user message
            result = insight_agent.invoke({
                "messages": [system_message, HumanMessage(content=message)],
                "patient_icn": icn,
                "patient_name": patient_name,
                "tools_used": [],
                "data_sources": [],
                "error": None
            })

            # Extract AI response from final message
            ai_response = result["messages"][-1].content

            # Extract tools used (for transparency display)
            tools_used = []
            for msg in result["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown_tool")
                        if tool_name not in tools_used:
                            tools_used.append(tool_name)

            logger.info(f"Agent response generated for {icn}. Tools used: {tools_used}")

            # Convert AI response from markdown to HTML
            ai_response_html = markdown.markdown(
                ai_response,
                extensions=['fenced_code', 'tables', 'nl2br']
            )

            # Render user message + AI response as HTML
            # We'll render the chat_message partial twice (user, then AI)
            user_message_html = templates.get_template("partials/chat_message.html").render(
                message_type="user",
                message_text=message,
                timestamp="Just now"
            )

            ai_message_html = templates.get_template("partials/chat_message.html").render(
                message_type="ai",
                message_text=ai_response_html,  # Already converted to HTML
                timestamp="Just now",
                tools_used=tools_used if tools_used else None
            )

            # Return both messages concatenated
            return HTMLResponse(content=user_message_html + ai_message_html)

        finally:
            # Clear request context to avoid memory leaks
            set_request_context(None)

    except Exception as e:
        logger.error(f"Error processing chat message for {icn}: {e}")
        # Return error message as AI response
        error_html = templates.get_template("partials/chat_message.html").render(
            message_type="ai",
            message_text=f"I'm sorry, I encountered an error: {str(e)}",
            timestamp="Just now",
            is_error=True
        )
        return HTMLResponse(content=error_html)
