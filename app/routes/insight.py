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
from datetime import datetime
import logging
import markdown

from langchain_core.messages import HumanMessage, SystemMessage

from app.db.patient import get_patient_demographics
from app.utils.template_context import get_base_context
from app.services.vista_cache import VistaSessionCache
from ai.agents.insight_agent import create_insight_agent
from ai.tools import ALL_TOOLS, set_request_context
from ai.prompts.system_prompts import get_system_prompt
from ai.prompts.suggested_questions import SUGGESTED_QUESTIONS

# Page router for full insight pages (no prefix for flexibility)
page_router = APIRouter(tags=["insight-pages"])

templates = Jinja2Templates(directory="app/templates")
logger = logging.getLogger(__name__)

# Phase 6: Agent is created with checkpointer in app/main.py lifespan handler
# Access via request.app.state.insight_agent
# No fallback needed - agent is guaranteed to exist at startup or app.state.insight_agent = None


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

    Phase 6: Conversation Memory
    - Loads previous conversation history from PostgreSQL checkpointer
    - Displays full chat history on page load (user + AI messages only)
    - Filters out system messages and tool calls for clean UI

    Features:
    - Chat message history (user + AI responses)
    - Suggested questions as clickable chips
    - Tool usage transparency ("Sources checked: DDI analyzer, Patient summary")
    - HTMX-powered message submission (no page reload)
    - Persistent conversation across page refreshes

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

        # Phase 6: Load conversation history from checkpointer
        chat_messages = []
        # Use user_id instead of session_id for thread_id to persist conversations across login sessions
        user = getattr(request.state, 'user', None)
        user_id = user.get('user_id', 'no-user') if user else 'no-user'
        thread_id = f"{user_id}_{icn}"

        checkpointer = request.app.state.checkpointer
        if checkpointer is not None:
            try:
                # Try to load existing conversation state for this thread
                config = {"configurable": {"thread_id": thread_id}}
                logger.info(f"Attempting to load checkpoint for thread_id: {thread_id[:50]}...")
                existing_state = await checkpointer.aget(config)

                logger.info(f"Checkpoint aget() returned: {type(existing_state)}, is None: {existing_state is None}")

                if existing_state is not None:
                    logger.info(f"Checkpoint state keys: {existing_state.keys() if hasattr(existing_state, 'keys') else 'N/A'}")
                    # LangGraph checkpoints store state in 'channel_values', not 'values'
                    state_values = existing_state.get("channel_values", {})
                    logger.info(f"Channel values type: {type(state_values)}")
                    logger.info(f"Channel values keys: {state_values.keys() if hasattr(state_values, 'keys') else 'N/A'}")

                    # Try to get messages
                    messages = state_values.get("messages", []) if isinstance(state_values, dict) else []
                    logger.info(f"Messages type: {type(messages)}")
                    logger.info(f"Messages found: {len(messages) if isinstance(messages, list) else 'NOT A LIST'}")

                    # If messages exists, log first message type for debugging
                    if messages and len(messages) > 0:
                        logger.info(f"First message type: {type(messages[0])}, has 'type' attr: {hasattr(messages[0], 'type')}")

                    if messages:
                        logger.info(f"Loaded {len(messages)} messages from checkpoint for {thread_id[:50]}...")

                        # Convert checkpoint messages to UI format
                        # Filter out system messages and tool calls, keep only user/AI exchanges
                        for msg in messages:
                            # Skip system messages
                            if hasattr(msg, 'type') and msg.type == 'system':
                                continue

                            # Skip tool messages
                            if hasattr(msg, 'type') and msg.type == 'tool':
                                continue

                            # Human messages (user questions)
                            if hasattr(msg, 'type') and msg.type == 'human':
                                chat_messages.append({
                                    'message_type': 'user',
                                    'message_text': msg.content,
                                    'timestamp': None  # Timestamps not stored in checkpoint
                                })

                            # AI messages (assistant responses)
                            elif hasattr(msg, 'type') and msg.type == 'ai':
                                # Skip AI messages with no content (tool-only messages)
                                if not msg.content or not msg.content.strip():
                                    continue

                                # Convert markdown to HTML for display
                                ai_response_html = markdown.markdown(
                                    msg.content,
                                    extensions=['fenced_code', 'tables', 'nl2br']
                                )

                                # Extract tools used from this message
                                tools_used = []
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        tool_name = tool_call.get("name", "unknown_tool")
                                        if tool_name not in tools_used:
                                            tools_used.append(tool_name)

                                chat_messages.append({
                                    'message_type': 'ai',
                                    'message_text': ai_response_html,
                                    'timestamp': None,
                                    'tools_used': tools_used if tools_used else None
                                })

                        logger.info(f"Formatted {len(chat_messages)} messages for UI display")

            except Exception as e:
                logger.warning(f"Could not load conversation history: {e}")
                # Continue with empty chat_messages - don't fail page load

        # Suggested questions for UI (managed in ai/prompts/suggested_questions.py)
        suggested_questions = SUGGESTED_QUESTIONS

        # Get Vista cache status for this patient
        cache_info = VistaSessionCache.get_cache_info(request, icn)

        logger.info(f"Loaded insights page for {icn} ({patient.get('name', 'Unknown')})")

        return templates.TemplateResponse(
            "insight.html",
            get_base_context(
                request,
                patient=patient,
                suggested_questions=suggested_questions,
                chat_messages=chat_messages,  # Phase 6: Load from checkpoint
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

    Phase 6: Conversation Memory
    - Uses AsyncPostgresSaver checkpointer for persistent conversation history
    - thread_id = {session_id}_{patient_icn} for session+patient isolation
    - History persists across page refreshes for 25-minute session duration
    - Different patients = different thread_ids = isolated conversations

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

        patient_name = patient.get("name_display", "Unknown Patient")

        logger.info(f"Processing chat message for {icn}: '{message[:100]}...'")

        # Generate timestamp for this message exchange
        # Format: "2:45:32 PM" (12-hour format with seconds for precision)
        message_timestamp = datetime.now().strftime('%I:%M:%S %p')

        # Phase 6: Generate thread_id for conversation memory
        # Format: {user_id}_{patient_icn}
        # - Same user + same patient = conversation continues (persists across login sessions)
        # - Same user + different patient = new conversation
        # - Different user = new conversation
        user = getattr(request.state, 'user', None)
        user_id = user.get('user_id', 'no-user') if user else 'no-user'
        thread_id = f"{user_id}_{icn}"

        logger.info(f"Thread ID: {thread_id[:50]}... (user+patient isolation)")

        # Set request context for tools (enables Vista cache access)
        set_request_context(request)

        try:
            # Phase 6: Get agent from app.state (created with checkpointer in lifespan handler)
            agent = request.app.state.insight_agent
            checkpointer = request.app.state.checkpointer

            if agent is None:
                logger.error("AI agent not initialized - check app startup logs")
                raise HTTPException(status_code=500, detail="AI agent unavailable")

            # Phase 6: Check if this is the first message in this thread
            # If so, we need to include the system prompt
            is_new_thread = False
            if checkpointer is not None:
                try:
                    # Try to get existing state for this thread
                    config = {"configurable": {"thread_id": thread_id}}
                    existing_state = await checkpointer.aget(config)

                    # If no existing state or no messages, this is a new thread
                    if existing_state is None:
                        is_new_thread = True
                        logger.info(f"New conversation thread: {thread_id[:50]}...")
                    else:
                        # Check if there are any messages in the state
                        # LangGraph checkpoints store state in 'channel_values', not 'values'
                        state_values = existing_state.get("channel_values", {})
                        existing_messages = state_values.get("messages", [])
                        is_new_thread = len(existing_messages) == 0

                        if not is_new_thread:
                            logger.info(f"Continuing conversation with {len(existing_messages)} existing messages")
                except Exception as e:
                    logger.warning(f"Could not check thread state: {e}, treating as new thread")
                    is_new_thread = True

            # Build messages list
            messages_to_send = []

            # Only add system message for new threads
            if is_new_thread:
                # Get comprehensive system prompt from prompts module
                base_system_prompt = get_system_prompt("clinical_insights")

                # Add patient-specific context to system prompt
                system_message = SystemMessage(
                    content=f"""{base_system_prompt}

CURRENT PATIENT CONTEXT:
- Patient Name: {patient_name}
- Patient ICN: {icn}

When the user asks questions about "this patient" or "the patient", they are referring to {patient_name} (ICN: {icn}).

Vista Data Integration:
- If the user has refreshed data from Vista during this session, tools will automatically use that cached data
- Tools will cite which data source was used (PostgreSQL historical data vs Vista real-time data)
- Always mention the data source in your response for transparency"""
                )
                messages_to_send.append(system_message)
                logger.info("Including system prompt (new thread)")

            # Always add the new user message
            messages_to_send.append(HumanMessage(content=message))

            # Phase 6: Use ainvoke() (async) with thread_id for conversation memory
            # The checkpointer will automatically:
            # 1. Load previous conversation history for this thread_id
            # 2. Append new messages to history
            # 3. Invoke agent with full context
            # 4. Save updated conversation state back to PostgreSQL
            result = await agent.ainvoke(
                {
                    "messages": messages_to_send,
                    "patient_icn": icn,
                    "patient_name": patient_name,
                    "tools_used": [],
                    "data_sources": [],
                    "error": None
                },
                config={"configurable": {"thread_id": thread_id}}
            )

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
                timestamp=message_timestamp
            )

            ai_message_html = templates.get_template("partials/chat_message.html").render(
                message_type="ai",
                message_text=ai_response_html,  # Already converted to HTML
                timestamp=message_timestamp,
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
        error_timestamp = datetime.now().strftime('%I:%M:%S %p')
        error_html = templates.get_template("partials/chat_message.html").render(
            message_type="ai",
            message_text=f"I'm sorry, I encountered an error: {str(e)}",
            timestamp=error_timestamp,
            is_error=True
        )
        return HTMLResponse(content=error_html)


@page_router.post("/insight/clear-history", response_class=HTMLResponse)
async def clear_chat_history(
    request: Request,
    icn: str = Form(...),
):
    """
    Clear conversation history for current patient.

    Phase 6: Conversation Memory - Clear History
    Deletes all checkpoints for the current thread_id from PostgreSQL,
    effectively clearing the conversation history. The next message will
    start a fresh conversation with a new system prompt.

    Args:
        icn: Patient ICN (from form data)

    Returns:
        Empty HTML (clears chat history div via HTMX)
    """
    try:
        # Generate thread_id for this user + patient
        user = getattr(request.state, 'user', None)
        user_id = user.get('user_id', 'no-user') if user else 'no-user'
        thread_id = f"{user_id}_{icn}"

        logger.info(f"Clearing conversation history for thread: {thread_id[:50]}...")

        # Get checkpointer from app state
        checkpointer = request.app.state.checkpointer

        if checkpointer is None:
            logger.warning("Checkpointer not available - cannot clear history")
            return HTMLResponse(content="")

        # Delete checkpoint for this thread_id
        # LangGraph AsyncPostgresSaver stores an AsyncConnection in 'conn' attribute
        # Use it directly to execute DELETE statements
        try:
            # Use the connection directly (it's already an AsyncConnection, not a pool)
            conn = checkpointer.conn

            # Delete all checkpoints for this thread_id
            # psycopg v3 uses %s for placeholders (not $1), and parameters as tuple/list
            await conn.execute(
                "DELETE FROM checkpoints WHERE thread_id = %s",
                (thread_id,)
            )
            await conn.execute(
                "DELETE FROM checkpoint_writes WHERE thread_id = %s",
                (thread_id,)
            )
            # checkpoint_blobs may need explicit deletion
            await conn.execute(
                "DELETE FROM checkpoint_blobs WHERE thread_id = %s",
                (thread_id,)
            )

            logger.info(f"✅ Cleared conversation history for {thread_id[:50]}...")

        except Exception as e:
            logger.error(f"Error deleting checkpoints from database: {e}")
            logger.exception("Full traceback:")
            # Continue anyway - return empty content

        # Return empty content to clear the chat history div
        return HTMLResponse(content="")

    except Exception as e:
        logger.error(f"Error clearing chat history for {icn}: {e}")
        # Return empty content even on error
        return HTMLResponse(content="")
