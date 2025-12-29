"""
LangGraph agent for clinical insights.

This module implements the core conversational agent that uses LangGraph to
orchestrate tool calls and manage conversation state for clinical decision support.

Architecture:
- State: InsightState (messages, patient context, tool tracking)
- Graph: StateGraph with agent node, tool node, and conditional routing
- Tools: Bound to OpenAI LLM, executed via ToolNode
- Flow: agent -> tools -> agent -> END (iterative until final response)

Design Reference: docs/spec/ai-insight-design.md Section 5.2
"""

from typing import TypedDict, List, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI

# Import OpenAI configuration from root config
from config import OPENAI_MODEL, OPENAI_TEMPERATURE


class InsightState(TypedDict):
    """
    State schema for the clinical insight agent.

    Attributes:
        messages: Conversation history (managed by LangGraph with add_messages)
        patient_icn: Patient ICN (Integrated Care Number) - immutable for session
        patient_name: Patient display name - immutable for session
        tools_used: List of tool names invoked during conversation (for transparency)
        data_sources: List of data sources queried (e.g., "PostgreSQL", "Vista RPC")
        error: Error message if something went wrong, otherwise None
    """
    # Conversation history (managed by LangGraph)
    messages: Annotated[List[BaseMessage], add_messages]

    # Patient context (immutable for conversation session)
    patient_icn: str
    patient_name: str

    # Tracking (for transparency and debugging)
    tools_used: List[str]  # e.g., ["check_ddi_risks", "get_patient_vitals"]
    data_sources: List[str]  # e.g., ["PostgreSQL", "Vista RPC"]

    # Error handling
    error: str | None


def create_insight_agent(tools: list):
    """
    Creates a LangGraph agent for clinical insights.

    The agent uses GPT-4 to interpret clinical questions, decides which tools
    to invoke, executes them, and synthesizes responses. The conversation loop
    continues until the LLM produces a final answer without tool calls.

    Architecture:
        1. User message enters via initial state
        2. Agent node: LLM decides to call tools or respond
        3. If tool calls: Route to tools node
        4. Tools node: Execute tools, append results to messages
        5. Loop back to agent node with tool results
        6. Agent node: Synthesize final response
        7. END

    Args:
        tools: List of LangChain tools (decorated with @tool)
               Example: [check_ddi_risks, get_patient_summary, analyze_vitals_trends]

    Returns:
        Compiled LangGraph agent ready for invocation

    Example:
        >>> from ai.tools import ALL_TOOLS
        >>> agent = create_insight_agent(ALL_TOOLS)
        >>> result = agent.invoke({
        ...     "messages": [HumanMessage(content="Check DDI risks")],
        ...     "patient_icn": "ICN1011530429",
        ...     "patient_name": "John Doe",
        ...     "tools_used": [],
        ...     "data_sources": [],
        ...     "error": None
        ... })
        >>> print(result["messages"][-1].content)

    Design Reference: docs/spec/ai-insight-design.md Section 5.2
    """
    # Initialize OpenAI LLM with configuration from config.py
    llm = ChatOpenAI(
        model=OPENAI_MODEL,              # From config: "gpt-4-turbo"
        temperature=OPENAI_TEMPERATURE,  # From config: 0.3 (low for clinical accuracy)
    )

    # Bind tools to LLM (enables function calling)
    llm_with_tools = llm.bind_tools(tools)

    # Define agent node
    def agent_node(state: InsightState) -> dict:
        """
        Agent node: LLM decides what to do next.

        The LLM examines the conversation history (including any tool results)
        and either:
        - Makes tool calls to gather more information
        - Produces a final text response

        Args:
            state: Current conversation state

        Returns:
            dict with "messages" key containing LLM response
        """
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define router function
    def should_continue(state: InsightState) -> str:
        """
        Router: Determine if we should continue to tools or end.

        Examines the last message in the conversation. If the LLM made
        tool calls, route to the tools node. Otherwise, end the conversation.

        Args:
            state: Current conversation state

        Returns:
            "tools" if tool calls present, END otherwise
        """
        last_message = state["messages"][-1]

        # If LLM made tool calls, route to tools node
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # Otherwise, LLM produced final response - end conversation
        return END

    # Build graph
    workflow = StateGraph(InsightState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))  # ToolNode handles tool execution

    # Set entry point
    workflow.set_entry_point("agent")

    # Add edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",  # If tools needed, go to tools node
            END: END           # If done, end conversation
        }
    )
    workflow.add_edge("tools", "agent")  # After tools execute, loop back to agent

    # Compile and return
    return workflow.compile()
