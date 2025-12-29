"""
Simple test tools for infrastructure verification.

These tools are used to verify that the LangGraph agent skeleton works
correctly before implementing complex clinical tools. They provide simple,
predictable behavior for testing the agent-tool-agent conversation loop.

NOTE: This file is for testing only and will be deleted once real clinical
tools are implemented in Days 3-5.

Usage:
    from ai.tools.test_tools import echo_tool, add_numbers
    agent = create_insight_agent([echo_tool, add_numbers])
"""

from langchain_core.tools import tool


@tool
def echo_tool(message: str) -> str:
    """
    Simple echo tool for testing LangGraph infrastructure.

    Returns the input message with an "Echo: " prefix. This verifies that:
    - The agent can invoke tools
    - Tool results are returned to the agent
    - The conversation loop works correctly

    Args:
        message: Any text message to echo back

    Returns:
        The same message prefixed with "Echo: "

    Example:
        >>> echo_tool("Hello World")
        'Echo: Hello World'
    """
    return f"Echo: {message}"


@tool
def add_numbers(a: int, b: int) -> int:
    """
    Simple math tool for testing tool invocation with multiple parameters.

    Adds two numbers together. This verifies that:
    - The agent can parse multi-parameter tool signatures
    - Type conversion works correctly (LLM provides ints)
    - Tool execution completes successfully

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    Example:
        >>> add_numbers(5, 7)
        12
    """
    return a + b


@tool
def get_patient_info(patient_icn: str) -> str:
    """
    Mock patient info tool for testing patient-specific queries.

    Returns hardcoded patient information for testing. This verifies that:
    - The agent can handle patient-specific tool calls
    - String parameters work correctly
    - Multi-line responses are handled properly

    Args:
        patient_icn: Patient ICN (ignored in test, returns mock data)

    Returns:
        Mock patient information as formatted text

    Example:
        >>> get_patient_info("ICN123456")
        'Patient: John Doe (72 yo Male)\\nDiagnoses: HTN, DM2\\nMedications: 5 active'
    """
    return """Patient: John Doe (72 yo Male)
Diagnoses: HTN, DM2, Hyperlipidemia
Medications: 5 active prescriptions
Last visit: 14 days ago (Cardiology)
Allergies: Penicillin (rash)

Data source: Mock test data"""
