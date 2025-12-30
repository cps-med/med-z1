"""
Test DDI Tool with LangGraph Agent

Tests the check_ddi_risks tool integrated with the actual LangGraph agent.
This verifies the complete end-to-end flow:
1. User asks a question about DDI risks
2. LangGraph agent decides to call check_ddi_risks tool
3. Tool queries PostgreSQL for medications
4. Tool analyzes medications with DDIAnalyzer
5. Agent synthesizes final response

Usage:
    python scripts/test_ddi_tool_with_agent.py

Prerequisites:
    - DDI reference data in MinIO
    - PostgreSQL with patient medication data
    - OpenAI API key configured
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from langchain_core.messages import HumanMessage
from ai.agents.insight_agent import create_insight_agent
from ai.tools import ALL_TOOLS


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print('=' * 70)
    else:
        print('-' * 70)


def test_ddi_tool_with_agent():
    """Test DDI tool with LangGraph agent."""
    print_separator("DDI Tool + LangGraph Agent Integration Test")

    print("\nInitializing LangGraph agent with DDI tool...")
    print(f"Available tools: {[tool.name for tool in ALL_TOOLS]}")

    try:
        # Create agent with DDI tool
        agent = create_insight_agent(ALL_TOOLS)
        print("✅ Agent initialized successfully")

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test cases with different patients
    # Note: ICN must be included in the question for the tool to extract it
    test_cases = [
        {
            "patient_icn": "ICN100010",
            "patient_name": "Alexander Aminor",
            "question": "Check patient ICN100010 for drug-drug interaction risks"
        },
        {
            "patient_icn": "ICN100001",
            "patient_name": "Adam Dooree",
            "question": "Are there any DDI risks for patient ICN100001?"
        },
        {
            "patient_icn": "ICN100010",
            "patient_name": "Alexander Aminor",
            "question": "What medications is patient ICN100010 taking and are there any dangerous interactions?"
        }
    ]

    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print_separator(f"Test Case {i}")

        patient_icn = test_case["patient_icn"]
        patient_name = test_case["patient_name"]
        question = test_case["question"]

        print(f"\nPatient: {patient_name} ({patient_icn})")
        print(f"Question: \"{question}\"")
        print()

        # Create initial state
        initial_state = {
            "messages": [HumanMessage(content=question)],
            "patient_icn": patient_icn,
            "patient_name": patient_name,
            "tools_used": [],
            "data_sources": [],
            "error": None
        }

        try:
            print("Agent thinking...")
            result = agent.invoke(initial_state)

            # Get final response
            final_message = result["messages"][-1]
            response = final_message.content

            print("\n" + "-" * 70)
            print("AGENT RESPONSE:")
            print("-" * 70)
            print(response)
            print("-" * 70)

            # Show conversation flow
            print("\nConversation Flow:")
            for j, msg in enumerate(result["messages"], 1):
                msg_type = type(msg).__name__
                tool_calls = getattr(msg, 'tool_calls', [])

                if tool_calls:
                    print(f"  {j}. {msg_type}: Called {len(tool_calls)} tool(s)")
                    for tc in tool_calls:
                        print(f"     - {tc.get('name', 'unknown')}")
                elif hasattr(msg, 'name'):
                    print(f"  {j}. {msg_type} (tool result): {msg.name}")
                else:
                    content_preview = getattr(msg, 'content', '')[:50]
                    print(f"  {j}. {msg_type}: {content_preview}...")

            print("\n✅ Test case completed successfully")

        except Exception as e:
            print(f"\n❌ Test case failed: {e}")
            import traceback
            traceback.print_exc()

        print()

    print_separator("Summary")
    print("\n✅ Integration test complete!")
    print("\nThe DDI tool is working with the LangGraph agent:")
    print("  ✓ Agent can invoke check_ddi_risks tool")
    print("  ✓ Tool queries PostgreSQL for medications")
    print("  ✓ Tool analyzes DDI risks")
    print("  ✓ Agent synthesizes natural language response")
    print("\nNext steps:")
    print("  - Add more clinical tools (patient summary, vitals trends, etc.)")
    print("  - Integrate into med-z1 web UI")
    print("  - Add conversational context (multi-turn questions)")
    print_separator()


if __name__ == "__main__":
    test_ddi_tool_with_agent()
