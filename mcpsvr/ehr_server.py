"""
EHR Data MCP Server - COMPLETE IMPLEMENTATION

Exposes patient clinical data from med-z1 PostgreSQL database to MCP clients.
This server wraps existing app/db query functions without duplicating logic.

Tools provided:
- get_patient_summary: Comprehensive patient overview
- get_patient_medications: Active medications list
- get_patient_vitals: Recent vital signs
- get_patient_allergies: Known allergies
- get_patient_encounters: Recent encounters

Usage:
    python mcp/ehr_server.py

Configuration:
    Reads from root .env file (DATABASE_URL, etc.)

Author: Created for med-z1 Clinical AI Career Preparation Guide
Version: 1.0
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

# MCP SDK imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types

# Ensure project root is in Python path and .env is loaded
# CRITICAL: This must happen BEFORE any app.db imports
try:
    project_root = Path(__file__).resolve().parent.parent
    print(f"DEBUG: Project root: {project_root}", file=sys.stderr)

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"DEBUG: Added to sys.path: {project_root}", file=sys.stderr)

    # Explicitly load .env file
    env_path = project_root / ".env"
    print(f"DEBUG: Loading .env from: {env_path}", file=sys.stderr)
    print(f"DEBUG: .env exists: {env_path.exists()}", file=sys.stderr)
    load_dotenv(env_path)
    print(f"DEBUG: .env loaded successfully", file=sys.stderr)

except Exception as e:
    print(f"ERROR: Failed to set up environment: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Import existing med-z1 database functions
# NOTE: These are synchronous functions, we'll wrap them for async MCP
try:
    print(f"DEBUG: Importing database modules...", file=sys.stderr)
    from app.db.patient import get_patient_demographics
    print(f"DEBUG: Imported patient module", file=sys.stderr)
    from app.db.medications import get_patient_medications as db_get_medications
    print(f"DEBUG: Imported medications module", file=sys.stderr)
    from app.db.vitals import get_recent_vitals
    print(f"DEBUG: Imported vitals module", file=sys.stderr)
    from app.db.patient_allergies import get_patient_allergies
    print(f"DEBUG: Imported allergies module", file=sys.stderr)
    from app.db.encounters import get_recent_encounters
    print(f"DEBUG: All database modules imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"ERROR: Failed to import database modules: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    print(f"Make sure you're running from project root: {project_root}", file=sys.stderr)
    sys.exit(1)

# Configure logging with standard output & file output for debugging (2 handlers)
log_file = Path(__file__).parent.parent / "log" / "mcp_server_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)-27s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("ehr-mcp-server")
logger.info(f"Logging to: {log_file}")

# Initialize MCP server
# The server instance handles all MCP protocol communication
server = Server("ehr-data-server")


# ============================================================================
# ATTRIBUTION HELPER - For clinical auditability and regulatory compliance
# ============================================================================

def _add_attribution_footer(
    result: str,
    tool_name: str,
    data_sources: list[str],
    metadata: dict = None
) -> str:
    """
    Add standardized attribution footer to tool responses.

    Critical for clinical auditability, regulatory compliance, and trust.
    Shows exactly what data sources and tools were used to generate each response.

    Args:
        result: The main tool response text
        tool_name: Name of the tool that generated this response
        data_sources: List of data sources queried (databases, APIs, reference files)
        metadata: Optional additional context (e.g., record counts, date ranges)

    Returns:
        Original result + attribution footer

    Example output footer:
        ---
        **Data Provenance:**
          • Tool: get_patient_summary
          • Data Sources: patient_demographics, patient_medications_outpatient, recent_vitals
          • Analysis Timestamp: 2026-02-02 14:30 UTC
          • Records retrieved: 23 vitals, 7 medications, 3 allergies
    """
    footer = "\n\n---\n\n"
    footer += "**Data Provenance:**\n"
    footer += f"  • **Tool:** `{tool_name}`\n"
    footer += f"  • **Data Sources:** {', '.join(data_sources)}\n"
    footer += f"  • **Analysis Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"

    if metadata:
        for key, value in metadata.items():
            footer += f"  • **{key}:** {value}\n"

    return result + footer


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================
# Tools are functions that the AI can call. Each tool needs:
# 1. A name (unique identifier)
# 2. A description (tells AI when to use this tool)
# 3. An input schema (JSON Schema defining parameters)
# ============================================================================

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Return list of available tools to MCP clients.

    This is called when Claude Desktop (or other MCP client) connects to
    understand what capabilities the server provides.

    Each tool definition includes:
    - name: Function identifier for tool calls
    - description: Helps AI decide when to use this tool
    - inputSchema: JSON Schema defining required/optional parameters
    """
    return [
        # Tool 1: Patient Summary
        types.Tool(
            name="get_patient_summary",
            description=(
                "Get comprehensive patient clinical summary including demographics, "
                "active medications, recent vitals, allergies, and encounters. "
                "Use this for general 'tell me about this patient' questions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient ICN (Integrated Care Number), e.g., 'ICN100001'"
                    }
                },
                "required": ["patient_icn"]
            }
        ),

        # Tool 2: Medications
        types.Tool(
            name="get_patient_medications",
            description=(
                "Get active medications for a patient. Returns drug name, sig "
                "(directions), start date, and prescribing provider. "
                "Use when specifically asked about medications or prescriptions."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient ICN"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of medications to return (default 10)",
                        "default": 10
                    }
                },
                "required": ["patient_icn"]
            }
        ),

        # Tool 3: Vital Signs
        types.Tool(
            name="get_patient_vitals",
            description=(
                "Get recent vital signs for a patient (blood pressure, heart rate, "
                "temperature, weight, height). Defaults to last 7 days. "
                "Use when asked about vitals, BP, weight, etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient ICN"
                    }
                },
                "required": ["patient_icn"]
            }
        ),

        # Tool 4: Allergies
        types.Tool(
            name="get_patient_allergies",
            description=(
                "Get known allergies for a patient including allergen name, "
                "reaction type, and severity. Critical for medication safety checks."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient ICN"
                    }
                },
                "required": ["patient_icn"]
            }
        ),

        # Tool 5: Encounters
        types.Tool(
            name="get_patient_encounters",
            description=(
                "Get recent encounters/visits for a patient (last 90 days). "
                "Includes encounter type, date, facility, and disposition."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient ICN"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum encounters to return (default 5)",
                        "default": 5
                    }
                },
                "required": ["patient_icn"]
            }
        ),
    ]


# ============================================================================
# TOOL EXECUTION
# ============================================================================
# When AI calls a tool, this handler executes the corresponding function
# ============================================================================

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[types.TextContent]:
    """
    Execute a tool when called by the AI.

    Args:
        name: Tool name (must match one from list_tools)
        arguments: Tool parameters from AI (validated against inputSchema)

    Returns:
        List of TextContent with tool results

    Note on sync/async:
        Our app/db functions are synchronous, but MCP requires async.
        We use asyncio.to_thread() to run sync functions in thread pool.
        This prevents blocking the MCP event loop.
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        # Route to appropriate tool handler
        if name == "get_patient_summary":
            result = await _get_patient_summary(arguments["patient_icn"])

        elif name == "get_patient_medications":
            patient_icn = arguments["patient_icn"]
            limit = arguments.get("limit", 10)
            # Run sync function in thread pool to avoid blocking
            meds = await asyncio.to_thread(db_get_medications, patient_icn, limit)
            result = _format_medications(meds)

        elif name == "get_patient_vitals":
            patient_icn = arguments["patient_icn"]
            vitals_data = await asyncio.to_thread(get_recent_vitals, patient_icn)
            result = _format_vitals(vitals_data)

        elif name == "get_patient_allergies":
            patient_icn = arguments["patient_icn"]
            allergies = await asyncio.to_thread(get_patient_allergies, patient_icn)
            result = _format_allergies(allergies)

        elif name == "get_patient_encounters":
            patient_icn = arguments["patient_icn"]
            limit = arguments.get("limit", 5)
            encounters = await asyncio.to_thread(get_recent_encounters, patient_icn, limit)
            result = _format_encounters(encounters)

        else:
            raise ValueError(f"Unknown tool: {name}")

        # Return formatted result to AI
        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_msg = f"Error: {str(e)}"
        return [types.TextContent(type="text", text=error_msg)]


# ============================================================================
# HELPER FUNCTIONS - Format database results for AI consumption
# ============================================================================

async def _get_patient_summary(patient_icn: str) -> str:
    """
    Build comprehensive patient summary by calling multiple data sources.

    This demonstrates how one MCP tool can orchestrate multiple database
    queries to provide a rich context to the AI.

    Args:
        patient_icn: Patient ICN

    Returns:
        Formatted multi-section patient summary with attribution footer
    """
    # Query all domains (run sync functions in thread pool)
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)
    medications = await asyncio.to_thread(db_get_medications, patient_icn, limit=10)
    vitals_data = await asyncio.to_thread(get_recent_vitals, patient_icn)
    allergies = await asyncio.to_thread(get_patient_allergies, patient_icn)
    encounters = await asyncio.to_thread(get_recent_encounters, patient_icn, limit=5)

    # Build comprehensive summary
    summary_parts = []

    # Demographics section
    if demographics:
        demo_text = f"**PATIENT DEMOGRAPHICS**\n"
        demo_text += f"Name: {demographics.get('name_display', 'Unknown')}\n"
        demo_text += f"Age: {demographics.get('age', 'unknown')} years old\n"
        demo_text += f"Sex: {demographics.get('sex', 'unknown')}\n"
        demo_text += f"DOB: {demographics.get('dob', 'unknown')}\n"
        if demographics.get('service_connected_percent'):
            demo_text += f"Service-Connected: {int(demographics['service_connected_percent'])}%\n"
        summary_parts.append(demo_text)
    else:
        summary_parts.append("**PATIENT DEMOGRAPHICS**\nNo demographic data found")

    # Medications section (includes its own attribution footer)
    summary_parts.append(_format_medications(medications))

    # Vitals section (includes its own attribution footer)
    summary_parts.append(_format_vitals(vitals_data))

    # Allergies section (includes its own attribution footer)
    summary_parts.append(_format_allergies(allergies))

    # Encounters section (includes its own attribution footer)
    summary_parts.append(_format_encounters(encounters))

    # Join all sections
    result = "\n\n".join(summary_parts)

    # Add top-level attribution footer showing data aggregation
    # Note: Each section above has its own detailed attribution
    vitals_count = len(vitals_data.get('vitals', [])) if vitals_data else 0

    return _add_attribution_footer(
        result=result,
        tool_name="get_patient_summary",
        data_sources=[
            "PostgreSQL patient_demographics table",
            "PostgreSQL patient_medications_outpatient table",
            "PostgreSQL patient_medications_inpatient table",
            "PostgreSQL recent_vitals table",
            "PostgreSQL patient_allergies table",
            "PostgreSQL recent_encounters table"
        ],
        metadata={
            "Summary sections": "Demographics, Medications, Vitals, Allergies, Encounters",
            "Total medications": len(medications),
            "Total vitals": vitals_count,
            "Total allergies": len(allergies),
            "Total encounters": len(encounters)
        }
    )


def _format_medications(meds: list[dict]) -> str:
    """
    Format medications list for AI readability.

    Args:
        meds: List of medication dicts from database

    Returns:
        Formatted markdown text with attribution footer
    """
    if not meds:
        text = "**MEDICATIONS**\nNo active medications on record"
    else:
        text = f"**MEDICATIONS** ({len(meds)} active)\n"
        for med in meds:
            # Handle multiple possible drug name fields
            drug_name = (
                med.get('drug_name_national') or
                med.get('drug_name') or
                'Unknown medication'
            )
            text += f"- {drug_name}"

            # Add sig (directions) if available
            sig = med.get('sig')
            if sig:
                text += f" ({sig})"

            # Add start date if available
            start_date = med.get('issue_date') or med.get('start_date')
            if start_date:
                text += f", started {start_date}"

            text += "\n"

        text = text.strip()

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=text,
        tool_name="get_patient_medications",
        data_sources=[
            "PostgreSQL patient_medications_outpatient table",
            "PostgreSQL patient_medications_inpatient table"
        ],
        metadata={
            "Medications retrieved": len(meds)
        }
    )


def _format_vitals(vitals_data: dict) -> str:
    """
    Format vital signs for AI readability.

    Args:
        vitals_data: Dict with 'vitals' key containing list of vitals

    Returns:
        Formatted markdown text with attribution footer
    """
    if not vitals_data or not vitals_data.get('vitals'):
        text = "**VITAL SIGNS**\nNo recent vitals (last 7 days)"
        vitals_count = 0
        taken_date = None
    else:
        vitals_list = vitals_data['vitals']
        if not vitals_list:
            text = "**VITAL SIGNS**\nNo recent vitals (last 7 days)"
            vitals_count = 0
            taken_date = None
        else:
            # Get most recent vital sign
            latest = vitals_list[0]  # Assumed to be sorted by date descending
            vitals_count = len(vitals_list)

            taken_date = latest.get('vital_taken_date', 'unknown date')
            text = f"**VITAL SIGNS** (Latest: {taken_date})\n"

            # Blood pressure
            systolic = latest.get('systolic')
            diastolic = latest.get('diastolic')
            if systolic and diastolic:
                text += f"- BP: {systolic}/{diastolic} mmHg\n"

            # Heart rate
            pulse = latest.get('pulse')
            if pulse:
                text += f"- HR: {pulse} bpm\n"

            # Temperature
            temp = latest.get('temperature')
            if temp:
                text += f"- Temp: {temp}°F\n"

            # Weight
            weight = latest.get('weight')
            if weight:
                text += f"- Weight: {weight} lbs\n"

            # Height
            height = latest.get('height')
            if height:
                text += f"- Height: {height} inches\n"

            text = text.strip()

    # Add attribution footer for clinical auditability
    metadata = {
        "Vitals retrieved": vitals_count,
        "Lookback period": "7 days"
    }
    if taken_date:
        metadata["Latest vital date"] = str(taken_date)

    return _add_attribution_footer(
        result=text,
        tool_name="get_patient_vitals",
        data_sources=[
            "PostgreSQL recent_vitals table"
        ],
        metadata=metadata
    )


def _format_allergies(allergies: list[dict]) -> str:
    """
    Format allergies for AI readability.

    Args:
        allergies: List of allergy dicts from database

    Returns:
        Formatted markdown text with attribution footer
    """
    if not allergies:
        text = "**ALLERGIES**\nNo known allergies (NKDA)"
    else:
        text = f"**ALLERGIES** ({len(allergies)} documented)\n"
        for allergy in allergies:
            allergen = allergy.get('allergen_name', 'Unknown allergen')
            text += f"- {allergen}"

            # Add reaction type if available
            reaction = allergy.get('reaction_type')
            if reaction:
                text += f" (reaction: {reaction.lower()}"

                # Add severity if available
                severity = allergy.get('severity')
                if severity:
                    text += f", severity: {severity.lower()}"

                text += ")"

            text += "\n"

        text = text.strip()

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=text,
        tool_name="get_patient_allergies",
        data_sources=[
            "PostgreSQL patient_allergies table"
        ],
        metadata={
            "Allergies retrieved": len(allergies)
        }
    )


def _format_encounters(encounters: list[dict]) -> str:
    """
    Format encounters for AI readability.

    Args:
        encounters: List of encounter dicts from database

    Returns:
        Formatted markdown text with attribution footer
    """
    if not encounters:
        text = "**ENCOUNTERS**\nNo recent encounters (last 90 days)"
    else:
        text = f"**ENCOUNTERS** (Last 90 days, {len(encounters)} shown)\n"
        for enc in encounters:
            # Encounter type or category
            enc_type = enc.get('admission_category', 'Unknown encounter')

            # Date (admit_datetime from PostgreSQL)
            enc_date_raw = enc.get('admit_datetime')
            if enc_date_raw:
                # Extract date part from datetime (format: "2025-12-28 08:00:00" -> "2025-12-28")
                enc_date = str(enc_date_raw).split(' ')[0]
            else:
                enc_date = 'unknown date'

            text += f"- {enc_type} on {enc_date}"

            # Location (facility_name from PostgreSQL)
            location = enc.get('facility_name')
            if location:
                text += f" ({location})"

            text += "\n"

        text = text.strip()

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=text,
        tool_name="get_patient_encounters",
        data_sources=[
            "PostgreSQL recent_encounters table"
        ],
        metadata={
            "Encounters retrieved": len(encounters),
            "Lookback period": "90 days"
        }
    )


# ============================================================================
# SERVER STARTUP
# ============================================================================

async def main():
    """
    Run the MCP server.

    This function initializes the MCP server with stdio transport,
    which allows Claude Desktop to communicate via stdin/stdout.
    """
    try:
        # Import stdio transport (communicates via standard input/output)
        from mcp.server.stdio import stdio_server

        logger.info("Starting EHR Data MCP Server...")
        logger.info("Available tools: get_patient_summary, get_patient_medications, "
                    "get_patient_vitals, get_patient_allergies, get_patient_encounters")

        # Run server with stdio transport
        # This allows Claude Desktop to communicate with the server via stdin/stdout
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="ehr-data-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server failed to start: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Entry point - run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
