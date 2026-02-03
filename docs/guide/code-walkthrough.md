# Clinical AI Code Walkthrough Guide
**Complete Implementation Details for Career Preparation Learning Path**

**Document Version:** v1.3
**Created:** 2026-02-02
**Last Updated:** 2026-02-02
**Purpose:** Line-by-line explanations of complete production code
**Companion to:** `docs/guide/clinical-ai-career-preparation.md`

**v1.3 Changes (2026-02-02):**
- Added "Attribution Pattern for Clinical Auditability" sections to Section 5 and Section 6
- Documents data provenance footers for regulatory compliance and transparency
- Explains `_add_attribution_footer()` helper pattern used across all 9 MCP tools
- Provides examples of attribution output for medications, DDI analysis, eGFR calculations

**v1.2 Changes (2026-02-02):**
- Added Section 6: Clinical Decision Support Server (950 lines, 4 tools)
- Complete walkthrough of DDI analysis, fall risk, eGFR calculator, cancer screening
- Clinical algorithm explanations and safety-first formatting patterns
- Comprehensive testing instructions for all tools

**v1.1 Changes (2026-02-02):**
- Updated directory reference: `mcp/` → `mcp_servers/`
- Updated Claude Desktop config to use full paths (venv Python + script path)
- Added troubleshooting for "Server disconnected" error
- Added environment variables prerequisite
- Added explanation of why full paths are required for Claude Desktop

---

## Table of Contents

1. [How to Use This Guide](#how-to-use-this-guide)
2. [Section 5: MCP Server #1 - EHR Data Server](#section-5-mcp-server-1---ehr-data-server)
3. [Section 6: MCP Server #2 - Clinical Decision Support](#section-6-mcp-server-2---clinical-decision-support) *(Coming when you're ready)*
4. [Section 7: MCP Server #3 - Clinical Notes Search](#section-7-mcp-server-3---clinical-notes-search) *(Coming when you're ready)*
5. [Section 9: Vector RAG Implementation](#section-9-vector-rag-implementation) *(Coming when you're ready)*
6. [Section 11: PyTorch Model #1 - Readmission Risk](#section-11-pytorch-model-1---readmission-risk) *(Coming when you're ready)*
7. [Section 12: PyTorch Model #2 - Vital Anomaly Detection](#section-12-pytorch-model-2---vital-anomaly-detection) *(Coming when you're ready)*
8. [Section 13: PyTorch Model #3 - Clinical NER](#section-13-pytorch-model-3---clinical-ner) *(Coming when you're ready)*

---

## How to Use This Guide

### Workflow

1. **Read main guide section** (e.g., Section 5 in `clinical-ai-career-preparation.md`)
2. **Review this walkthrough** for implementation details
3. **Run the code** to validate it works
4. **Test thoroughly** before moving to next section
5. **Ask questions** if anything is unclear

### Code Organization

All code is in proper directories matching production structure:
```
med-z1/
  mcp_servers/            # MCP servers
  ai/ml/                  # PyTorch models
  ai/services/            # Business logic
  ai/tools/               # LangGraph tools
```

### Navigation

- **Ctrl+F / Cmd+F** to search for specific functions
- Each section links to main guide concepts
- Code blocks show line number ranges for reference

---

## Section 5: MCP Server #1 - EHR Data Server

**Main Guide Reference:** Section 5 in `clinical-ai-career-preparation.md`
**File:** `mcp_servers/ehr_server.py`
**Lines:** 550 total
**Complexity:** Beginner-Intermediate
**Estimated Study Time:** 2-3 hours

### Overview

This MCP server exposes your PostgreSQL patient database to AI assistants like Claude Desktop. It wraps existing `app/db/` functions without duplicating database logic.

**Key Learning Goals:**
- Understand MCP server lifecycle (initialization → tool listing → tool execution)
- Learn async/sync patterns (wrapping synchronous database calls for async MCP)
- Practice data formatting for AI consumption
- Test integration with Claude Desktop

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Desktop (MCP Client)                                │
│  User: "What medications is patient ICN100001 on?"          │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol (JSON-RPC over stdio)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  mcp_servers/ehr_server.py                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ @server.call_tool()                                  │   │
│  │ → handle_call_tool("get_patient_medications", ...)   │   │
│  └───────────────────┬──────────────────────────────────┘   │
└──────────────────────┼──────────────────────────────────────┘
                       │ asyncio.to_thread()
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  app/db/medications.py                                      │
│  get_patient_medications(icn="ICN100001", limit=10)         │
│  → Executes SQL query on PostgreSQL                         │
│  → Returns List[Dict] of medications                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL Database (patient_medications_outpatient)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (results returned back up the chain)
┌─────────────────────────────────────────────────────────────┐
│  mcp_servers/ehr_server.py                                  │
│  _format_medications(meds) → Markdown text                  │
│  Returns: "**MEDICATIONS** (7 active)\n- GABAPENTIN..."     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude Desktop displays formatted response to user         │
└─────────────────────────────────────────────────────────────┘
```

### Attribution Pattern for Clinical Auditability

**Added:** 2026-02-02 (v1.3)

All MCP tools in both Server #1 (EHR Data) and Server #2 (Clinical Decision Support) include **data provenance footers** for clinical auditability and regulatory compliance.

**Why Attribution Matters:**
- **Clinical Safety:** Shows exactly what data sources were queried
- **Regulatory Compliance:** Provides evidence trail for clinical decisions
- **Trust:** Transparency about tool usage builds confidence in AI responses
- **Debugging:** Helps identify data quality issues by showing sources

**Implementation Pattern:**

Every formatting function calls `_add_attribution_footer()` before returning:

```python
def _add_attribution_footer(
    result: str,
    tool_name: str,
    data_sources: list[str],
    metadata: dict = None
) -> str:
    """Add standardized attribution footer to tool responses."""
    footer = "\n\n---\n\n"
    footer += "**Data Provenance:**\n"
    footer += f"  • **Tool:** `{tool_name}`\n"
    footer += f"  • **Data Sources:** {', '.join(data_sources)}\n"
    footer += f"  • **Analysis Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"

    if metadata:
        for key, value in metadata.items():
            footer += f"  • **{key}:** {value}\n"

    return result + footer
```

**Example Output (get_patient_medications):**

```markdown
**MEDICATIONS** (7 active)
- GABAPENTIN 300MG CAP (take 1 capsule by mouth three times a day), started 2025-10-15
- LISINOPRIL 10MG TAB (take 1 tablet by mouth daily), started 2025-09-01
...

---

**Data Provenance:**
  • **Tool:** `get_patient_medications`
  • **Data Sources:** PostgreSQL patient_medications_outpatient table, PostgreSQL patient_medications_inpatient table
  • **Analysis Timestamp:** 2026-02-02 15:30 UTC
  • **Medications retrieved:** 7
```

**Benefits in Clinical Context:**
1. Clinicians see which databases were queried
2. Timestamp enables correlation with database state at query time
3. Record counts help identify incomplete data (e.g., "Only 2 medications - is this complete?")
4. Tool name enables tracing back to source code for validation

**Consistency Across Both Servers:**
- EHR Data Server: All 5 tools include attribution (medications, vitals, allergies, encounters, patient_summary)
- Clinical Decision Support Server: All 4 tools include attribution (DDI, fall risk, eGFR, cancer screening)

---

### Code Walkthrough

---

#### **Lines 1-23: Module Docstring and Imports**

```python
"""
EHR Data MCP Server - COMPLETE IMPLEMENTATION
...
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types

from app.db.patient import get_patient_demographics
from app.db.medications import get_patient_medications as db_get_medications
from app.db.vitals import get_recent_vitals
from app.db.patient_allergies import get_patient_allergies
from app.db.encounters import get_recent_encounters
```

**Key Imports Explained:**

1. **`asyncio`** - CRITICAL for `asyncio.to_thread()`
   - Your `app/db` functions are **synchronous** (blocking)
   - MCP server is **asynchronous** (non-blocking)
   - `asyncio.to_thread()` runs sync functions in a thread pool
   - Without this: Server would freeze waiting for database queries

2. **`mcp.server.Server`** - Core MCP server class
   - Handles MCP protocol communication
   - Manages tool registration and execution
   - Provides stdio transport for Claude Desktop

3. **`mcp.types`** - Type definitions for tools
   - `types.Tool` - Tool definition with schema
   - `types.TextContent` - Response format for AI

4. **`app.db.*` imports** - Your existing Data Access Layer
   - Reusing production database queries (no duplication!)
   - `db_get_medications` alias avoids name conflict with function parameter

**Why This Matters:**
- **Separation of concerns:** MCP layer doesn't know about SQL, just calls DAL functions
- **Testability:** Can mock `app.db` functions in tests
- **Maintainability:** Database query changes don't break MCP server

---

#### **Lines 25-45: Logging and Server Initialization**

```python
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ehr-mcp-server")

# Initialize MCP server
server = Server("ehr-data-server")
```

**Design Decisions:**

1. **Logging Level: INFO**
   - Development: See all tool calls and results
   - Production: Change to WARNING to reduce noise
   - Debug: Set to DEBUG for troubleshooting

2. **Server Name: "ehr-data-server"**
   - Identifies this server in Claude Desktop
   - Shows up in MCP client tool lists
   - Should be descriptive and unique

**Logging Strategy:**
```python
# In handle_call_tool (line 212):
logger.info(f"Tool called: {name} with arguments: {arguments}")
# Produces: "INFO:ehr-mcp-server:Tool called: get_patient_medications with arguments: {'patient_icn': 'ICN100001'}"

# In exception handler (line 241):
logger.error(f"Error executing tool {name}: {e}", exc_info=True)
# Produces full stack trace for debugging
```

---

#### **Lines 50-165: Tool Definitions (@server.list_tools)**

This is the **contract** between your server and AI clients. Each tool needs:
1. **name** - Unique identifier
2. **description** - Tells AI when to use this tool (critical for routing)
3. **inputSchema** - JSON Schema defining parameters

**Tool 1: get_patient_summary (lines 75-92)**

```python
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
)
```

**Description Best Practices:**
- ✅ "Use this for general 'tell me about this patient' questions" - Guides AI when to choose this tool
- ✅ Mentions what data is included (demographics, meds, vitals, etc.)
- ❌ Don't just say "Get patient summary" - too vague

**Input Schema:**
- JSON Schema standard (same as OpenAPI/Swagger)
- `required: ["patient_icn"]` - AI must provide this parameter
- `type: "string"` - Validates input type
- `description` inside properties - Helps AI understand what to pass

**Why This Tool Exists:**
- **One-call patient overview** - AI doesn't need to call 5 separate tools
- **Efficient** - Single MCP round-trip instead of 5
- **User-friendly** - Answers "tell me about this patient" directly

---

**Tool 2: get_patient_medications (lines 95-117)**

```python
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
)
```

**Key Differences from Tool 1:**
- **Optional parameter:** `limit` has a default value
- **Focused description:** "Use when specifically asked about medications"
- **More detailed output description:** "Returns drug name, sig, start date, provider"

**When AI Chooses This vs. get_patient_summary:**
- User: "What medications is patient ICN100001 on?" → **This tool**
- User: "Tell me about patient ICN100001" → **get_patient_summary** (includes meds)

**Optional Parameters Pattern:**
```python
"limit": {
    "type": "integer",
    "description": "Maximum number of medications to return (default 10)",
    "default": 10  # ← AI can omit this, will use 10
}
```

In `handle_call_tool` (line 220):
```python
limit = arguments.get("limit", 10)  # Falls back to 10 if not provided
```

---

**Tools 3-5: Vitals, Allergies, Encounters (lines 120-165)**

Same pattern, progressively simpler:
- **get_patient_vitals:** No optional params, just ICN
- **get_patient_allergies:** Critical for medication safety (description emphasizes this)
- **get_patient_encounters:** Optional `limit` param like medications

**Design Principle: Granular Tools**

Why 5 separate tools instead of just `get_patient_summary`?

✅ **Performance:** Don't fetch vitals if user only asks about medications
✅ **Flexibility:** AI can combine tools creatively
✅ **Clarity:** Each tool has a clear, single responsibility
✅ **User control:** User can ask specific questions

**Example AI Reasoning:**
```
User: "What's the patient's blood pressure?"
AI thinks:
  - Could call get_patient_summary (gets everything)
  - Better to call get_patient_vitals (targeted, faster)
AI calls: get_patient_vitals("ICN100001")
```

---

#### **Lines 170-245: Tool Execution (@server.call_tool)**

This is the **router** that executes the correct function when AI calls a tool.

```python
@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[types.TextContent]:
```

**Function Signature:**
- `name: str` - Which tool AI wants to call (e.g., "get_patient_medications")
- `arguments: dict` - Parameters AI provided (e.g., `{"patient_icn": "ICN100001", "limit": 10}`)
- `Returns: list[types.TextContent]` - MCP protocol requires list of content blocks

**Routing Logic (lines 212-236):**

```python
if name == "get_patient_summary":
    result = await _get_patient_summary(arguments["patient_icn"])

elif name == "get_patient_medications":
    patient_icn = arguments["patient_icn"]
    limit = arguments.get("limit", 10)
    meds = await asyncio.to_thread(db_get_medications, patient_icn, limit)
    result = _format_medications(meds)

elif name == "get_patient_vitals":
    # ... similar pattern
```

**Critical Pattern: asyncio.to_thread()**

```python
# WRONG - This would block the MCP server:
meds = db_get_medications(patient_icn, limit)  # ❌ Synchronous call in async context

# CORRECT - Run in thread pool:
meds = await asyncio.to_thread(db_get_medications, patient_icn, limit)  # ✅
```

**Why This Matters:**
1. `db_get_medications()` is synchronous (uses SQLAlchemy blocking calls)
2. MCP server is async (handles multiple concurrent requests)
3. Without `asyncio.to_thread()`:
   - Server freezes during database query (~100-500ms)
   - Can't handle other MCP requests during that time
   - Claude Desktop may timeout
4. With `asyncio.to_thread()`:
   - Database query runs in background thread
   - MCP event loop stays responsive
   - Other requests can be processed concurrently

**Exception Handling (lines 238-244):**

```python
except Exception as e:
    logger.error(f"Error executing tool {name}: {e}", exc_info=True)
    error_msg = f"Error: {str(e)}"
    return [types.TextContent(type="text", text=error_msg)]
```

**Graceful Degradation:**
- Logs full stack trace for debugging
- Returns error message to AI (not raw exception)
- AI can inform user something went wrong
- Server doesn't crash - stays running for next request

---

#### **Lines 250-350: Helper Functions - Patient Summary**

**`_get_patient_summary()` - The Orchestrator (lines 258-305)**

```python
async def _get_patient_summary(patient_icn: str) -> str:
    # Query all domains (run sync functions in thread pool)
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)
    medications = await asyncio.to_thread(db_get_medications, patient_icn, limit=10)
    vitals_data = await asyncio.to_thread(get_recent_vitals, patient_icn)
    allergies = await asyncio.to_thread(get_patient_allergies, patient_icn)
    encounters = await asyncio.to_thread(get_recent_encounters, patient_icn, limit=5)
```

**Design Decision: Sequential vs. Concurrent Queries**

**Current Implementation (Sequential):**
```python
demographics = await asyncio.to_thread(...)  # 100ms
medications = await asyncio.to_thread(...)   # 150ms
vitals = await asyncio.to_thread(...)        # 120ms
# Total: 100 + 150 + 120 = 370ms
```

**Alternative (Concurrent with asyncio.gather):**
```python
results = await asyncio.gather(
    asyncio.to_thread(get_patient_demographics, patient_icn),
    asyncio.to_thread(db_get_medications, patient_icn, limit=10),
    asyncio.to_thread(get_recent_vitals, patient_icn),
    # ...
)
# Total: max(100, 150, 120) = 150ms (2.5x faster!)
```

**Why Sequential Was Chosen:**
- ✅ Simpler to understand (learning focus)
- ✅ Easier to debug (see which query failed)
- ✅ 370ms is still fast enough for this use case
- ⚠️ Could optimize later with `asyncio.gather()` if needed

**Exercise for Learning:** Try implementing concurrent version after mastering sequential.

---

#### **Lines 310-350: Formatting Functions**

**`_format_medications()` - Example (lines 318-345)**

```python
def _format_medications(meds: list[dict]) -> str:
    if not meds:
        return "**MEDICATIONS**\nNo active medications on record"

    text = f"**MEDICATIONS** ({len(meds)} active)\n"
    for med in meds:
        drug_name = (
            med.get('drug_name_national') or
            med.get('drug_name') or
            'Unknown medication'
        )
        text += f"- {drug_name}"

        sig = med.get('sig')
        if sig:
            text += f" ({sig})"

        start_date = med.get('issue_date') or med.get('start_date')
        if start_date:
            text += f", started {start_date}"

        text += "\n"

    return text.strip()
```

**Formatting Strategy: AI-Friendly Markdown**

**Why Markdown:**
- ✅ Claude understands Markdown natively
- ✅ Renders nicely in chat interface
- ✅ Structured yet human-readable
- ✅ Easy to parse programmatically if needed

**Example Output:**
```
**MEDICATIONS** (7 active)
- GABAPENTIN 300MG CAP (TAKE 1 CAPSULE BY MOUTH 3 TIMES DAILY), started 2024-01-15
- METFORMIN 500MG TAB (TAKE 1 TABLET BY MOUTH TWICE DAILY), started 2023-11-20
- LISINOPRIL 10MG TAB (TAKE 1 TABLET BY MOUTH DAILY), started 2023-09-10
...
```

**Defensive Programming:**
```python
drug_name = (
    med.get('drug_name_national') or  # Try VA national name first
    med.get('drug_name') or           # Fallback to generic name
    'Unknown medication'              # Last resort
)
```

**Why Multiple Fallbacks:**
- Data quality varies across VA systems
- Some records have `drug_name_national`, some only `drug_name`
- Better to show "Unknown medication" than crash

**Similar Pattern for All Formatting Functions:**
1. Check for empty data → Return "No X on record"
2. Build header with count
3. Loop through items, format each
4. Use `.get()` with fallbacks (never assume keys exist)
5. Return `.strip()` to remove trailing newlines

---

#### **Lines 505-550: Server Startup**

```python
async def main():
    from mcp.server.stdio import stdio_server

    logger.info("Starting EHR Data MCP Server...")
    logger.info("Available tools: get_patient_summary, get_patient_medications, ...")

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

if __name__ == "__main__":
    asyncio.run(main())
```

**MCP Transport: stdio (Standard Input/Output)**

**How Claude Desktop Communicates:**
1. Claude Desktop starts your server as subprocess: `python mcp_servers/ehr_server.py`
2. Sends MCP requests via **stdin** (standard input)
3. Reads MCP responses from **stdout** (standard output)
4. All communication is JSON-RPC over stdio

**Why stdio instead of HTTP:**
- ✅ No network ports to configure
- ✅ Automatic process lifecycle (server dies when Claude Desktop closes)
- ✅ Simpler security model (no authentication needed)
- ✅ Works locally without network access

**Alternative Transports (Future):**
- HTTP/WebSocket - For remote servers
- SSE (Server-Sent Events) - For streaming responses

**Capabilities Registration:**
```python
capabilities=server.get_capabilities(
    notification_options=NotificationOptions(),
    experimental_capabilities={},
)
```

**What This Declares:**
- Server supports tool calling (via `@server.call_tool()`)
- No experimental features enabled
- Can add notifications later (e.g., "Patient data updated")

---

### Key Takeaways from This Code

**1. Async/Sync Bridge Pattern**
- MCP is async, your database layer is sync
- `asyncio.to_thread()` bridges the gap
- This pattern applies to all I/O-bound operations

**2. Separation of Concerns**
- MCP server doesn't know about SQL (calls `app/db`)
- `app/db` doesn't know about MCP (returns plain dicts)
- Formatting layer makes data AI-friendly

**3. Graceful Error Handling**
- Never crash the server - catch exceptions
- Log errors for debugging
- Return user-friendly error messages

**4. AI-First Design**
- Tool descriptions guide AI routing
- Output format optimized for LLM consumption (Markdown)
- Multiple tools for flexibility vs. one monolithic tool

**5. Production Patterns**
- Logging for observability
- Type hints for maintainability
- Defensive programming (`.get()` with fallbacks)

---

### Testing & Validation

**See Section: Testing Steps for Section 5** (below in this document)

---

## Testing Steps for Section 5

### Prerequisites

1. **Environment Variables Configured**
```bash
# Verify .env has PostgreSQL configuration
grep "POSTGRES_" /Users/chuck/swdev/med/med-z1/.env

# Should show:
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=medz1
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password

# Note: config.py automatically builds DATABASE_URL from these variables
```

2. **PostgreSQL Running**
```bash
# Check if PostgreSQL serving database is accessible
psql $DATABASE_URL -c "SELECT COUNT(*) FROM patient_demographics"
# Should return count of patient records
```

3. **MCP SDK Installed**
```bash
pip install mcp
python -c "import mcp; print('MCP installed')"
```

4. **Claude Desktop Installed**
- Download from https://claude.ai/download (if not already installed)

---

### Test 1: Run Server Standalone (Basic Smoke Test)

**Purpose:** Verify server starts without errors

```bash
cd /Users/chuck/swdev/med/med-z1
python mcp_servers/ehr_server.py
```

**Note:** You can also use module syntax: `python -m mcp_servers.ehr_server` - both work because the script has path setup code at the top.

**Expected Output:**
```
INFO:ehr-mcp-server:Starting EHR Data MCP Server...
INFO:ehr-mcp-server:Available tools: get_patient_summary, get_patient_medications, get_patient_vitals, get_patient_allergies, get_patient_encounters
```

**Server is now waiting for stdio input** (this is normal - it's listening for MCP requests)

**How to Exit:** Press `Ctrl+C`

**What This Tests:**
- ✅ All imports work (no ModuleNotFoundError)
- ✅ Server initialization succeeds
- ✅ No syntax errors in decorators

**If It Fails:**
- Check error message carefully
- Common issues:
  - Missing `mcp` package → `pip install mcp`
  - Can't import `app.db` → Ensure you're in project root
  - Database connection error → Check `DATABASE_URL` in `.env`

---

### Test 2: Configure Claude Desktop

**Purpose:** Connect Claude Desktop to your MCP server

**Step 1: Find Claude Desktop Config File**

**macOS:**
```bash
# Config location
open ~/Library/Application\ Support/Claude/
# File to edit: claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Step 2: Edit Configuration**

Create or edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ehr-data": {
      "command": "/Users/chuck/swdev/med/med-z1/.venv/bin/python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcp_servers/ehr_server.py"],
      "cwd": "/Users/chuck/swdev/med/med-z1"
    }
  }
}
```

**IMPORTANT: Update paths to match your actual project location!**

**Configuration Explained:**
- **`ehr-data`** - Name shown in Claude Desktop (can be anything)
- **`command`** - **Full path** to your virtual environment's Python interpreter (required - Claude Desktop doesn't inherit activated venv)
- **`args`** - **Full path** to the server script (more reliable than `-m` module syntax for MCP servers)
- **`cwd`** - Working directory set to project root (required for `from app.db` imports to work)

**Why Full Paths?**
- Claude Desktop runs in its own environment and doesn't see your activated virtual environment
- Using full paths ensures Claude Desktop finds the correct Python with all dependencies installed
- This avoids "ModuleNotFoundError" issues that occur when using system Python

**Step 3: Restart Claude Desktop**
- Quit Claude Desktop completely
- Reopen

**Step 4: Verify Connection**

In Claude Desktop, look for MCP indicator (usually in bottom corner or settings).

If MCP servers are connected, you should see "ehr-data" listed.

---

### Test 3: Test Each Tool with Claude Desktop

**Test 3a: get_patient_medications**

In Claude Desktop chat, type:

```
What medications is patient ICN100001 on?
```

**What Should Happen:**
1. Claude recognizes "medications" and "patient ICN100001"
2. Calls `get_patient_medications` tool
3. Your server queries PostgreSQL
4. Returns formatted medication list
5. Claude synthesizes natural language response

**Expected Response (from Claude):**
```
Patient ICN100001 is currently on 7 active medications:

1. GABAPENTIN 300MG CAP - Take 1 capsule by mouth 3 times daily, started 2024-01-15
2. ALPRAZOLAM 0.5MG TAB - Take 1 tablet by mouth as needed, started 2024-02-20
...
```

**Debug if It Fails:**
- Check server logs (if you ran it standalone before, check terminal output)
- Claude Desktop may show error message - read it carefully
- Common issues:
  - Patient ICN doesn't exist → Try `ICN100010`, `ICN100013`
  - Database not running
  - Path in config is wrong

---

**Test 3b: get_patient_vitals**

```
What are the latest vital signs for patient ICN100001?
```

**Expected:**
- Claude calls `get_patient_vitals`
- Returns BP, HR, temperature, weight from last 7 days

---

**Test 3c: get_patient_allergies**

```
Does patient ICN100001 have any allergies?
```

**Expected:**
- Claude calls `get_patient_allergies`
- Lists allergies with reaction types and severity

---

**Test 3d: get_patient_encounters**

```
What recent visits has patient ICN100001 had?
```

**Expected:**
- Claude calls `get_patient_encounters`
- Lists recent encounters (last 90 days)

---

**Test 3e: get_patient_summary (The Big One)**

```
Give me a complete clinical summary of patient ICN100001
```

**Expected:**
- Claude calls `get_patient_summary` (one tool call, not 5 separate ones)
- Returns comprehensive multi-section summary:
  - Demographics
  - Medications
  - Vitals
  - Allergies
  - Encounters

**This tests:**
- ✅ Orchestration across multiple database queries
- ✅ Async handling of multiple `asyncio.to_thread()` calls
- ✅ Formatting of combined data
- ✅ Large response handling (should be ~500-1000 tokens)

---

### Test 4: Error Handling

**Test 4a: Invalid Patient ICN**

```
What medications is patient ICN999999 on?
```

**Expected:**
- Server doesn't crash
- Returns something like "No active medications on record" or "Patient not found"
- Claude explains to user that patient doesn't exist

---

**Test 4b: Database Offline**

**Temporarily break database connection:**
1. Edit `.env` - change DATABASE_URL to invalid value
2. Restart server (if running standalone)
3. Try any query in Claude Desktop

**Expected:**
- Server logs error
- Returns error message to Claude
- Claude tells user there's a database issue
- Server stays running (doesn't crash)

**Don't forget to fix `.env` after this test!**

---

### Test 5: Performance Check

**Purpose:** Ensure queries are fast enough for good UX

```
Give me a complete clinical summary of patient ICN100001
```

**Measure Time:**
- From when you hit Enter in Claude Desktop
- To when complete response appears

**Acceptable Performance:**
- **< 3 seconds:** ✅ Excellent
- **3-5 seconds:** ✅ Good (typical)
- **5-10 seconds:** ⚠️ Acceptable but slow (optimize later)
- **> 10 seconds:** ❌ Too slow (investigate bottleneck)

**Common Bottlenecks:**
1. Database query time → Check query performance with `EXPLAIN ANALYZE`
2. Network latency → Are you on VPN? Remote database?
3. Sequential queries → Consider `asyncio.gather()` for parallel

---

### Test 6: Logging Verification

**Purpose:** Ensure observability for debugging

**Run server standalone:**
```bash
python mcp_servers/ehr_server.py
```

**In Claude Desktop, make a request:**
```
What medications is patient ICN100001 on?
```

**Check Terminal (where server is running):**

**Expected Log Output:**
```
INFO:ehr-mcp-server:Starting EHR Data MCP Server...
INFO:ehr-mcp-server:Available tools: get_patient_summary, ...
INFO:ehr-mcp-server:Tool called: get_patient_medications with arguments: {'patient_icn': 'ICN100001', 'limit': 10}
```

**This Confirms:**
- ✅ Logging is working
- ✅ Tool name and arguments logged correctly
- ✅ Can debug issues by seeing what tools were called

---

### Validation Checklist

Before moving to Section 6, confirm:

- [ ] ✅ Server starts without errors (Test 1)
- [ ] ✅ Claude Desktop connects to server (Test 2)
- [ ] ✅ All 5 tools work correctly (Test 3a-e)
- [ ] ✅ Error handling is graceful (Test 4a-b)
- [ ] ✅ Response time < 5 seconds (Test 5)
- [ ] ✅ Logging shows tool calls (Test 6)
- [ ] ✅ Code is commented and understandable
- [ ] ✅ You understand async/sync pattern (`asyncio.to_thread()`)
- [ ] ✅ You understand MCP request/response flow

**If any checkbox is unchecked, debug before proceeding!**

---

### Common Issues & Solutions

**Issue: "ModuleNotFoundError: No module named 'mcp'"**
```bash
pip install mcp
```

**Issue: "ModuleNotFoundError: No module named 'app'"**
- Ensure you're running from project root: `/Users/chuck/swdev/med/med-z1`
- Check PYTHONPATH in Claude Desktop config

**Issue: "name 'asyncio' is not defined"**
- Missing `import asyncio` at top of file
- Use the complete `ehr_server.py` (not abbreviated version)

**Issue: "function '_format_medications' is not defined"**
- File is incomplete - use `ehr_server_complete.py`

**Issue: Claude Desktop doesn't show my server**
- Check `claude_desktop_config.json` syntax (valid JSON?)
- Restart Claude Desktop (quit completely, not just close window)
- Check path in config is absolute and correct

**Issue: "Server disconnected" error in Claude Desktop**
- Check Claude Desktop logs: `~/Library/Logs/Claude/mcp-server-ehr-data.log` (macOS)
- Most common cause: Using system Python instead of venv Python
- **Solution:** Use full path to venv Python in config (see Test 2 above)
- Also check: `DATABASE_URL` environment variable exists in `.env`
- Debug: Look for "Failed to spawn process" or "ModuleNotFoundError" in logs

**Issue: Server crashes on database error**
- Check `try/except` block in `handle_call_tool`
- Ensure database is running: `psql $DATABASE_URL -c "SELECT 1"`
- Verify `.env` has `POSTGRES_*` variables configured

---

### Next Steps

Once all tests pass:

1. ✅ **Section 5 Complete!** You have a working MCP server.
2. 📚 **Review code walkthrough above** - Ensure you understand key patterns
3. 💡 **Experiment:** Try modifying descriptions, add a new simple tool
4. ➡️ **Ready for Section 6?** Let me know and I'll create Clinical Decision Support server

---

**End of Section 5 Walkthrough**

*Sections 6-13 will be added as you progress through the learning guide.*

---

## Section 6: MCP Server #2 - Clinical Decision Support

**Main Guide Reference:** Section 6 in `clinical-ai-career-preparation.md`
**File:** `mcp_servers/clinical_decision_support_server.py`
**Lines:** ~950 total
**Complexity:** Intermediate-Advanced
**Estimated Study Time:** 3-4 hours

### Overview

This MCP server exposes clinical algorithms and risk assessment tools. Unlike Server #1 (simple data retrieval), this server implements **complex business logic** including DDI analysis, risk scoring, medical calculations, and guideline-based recommendations.

**Key Learning Goals:**
- Understand how to wrap existing AI services as MCP tools (no code duplication)
- Learn clinical safety patterns (explicit confirmations, risk highlighting)
- Practice medical calculations (eGFR, fall risk scoring)
- Implement guideline-based decision support (USPSTF screening)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Desktop                                              │
│  User: "Are there any drug interactions for this patient?"  │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  mcp_servers/clinical_decision_support_server.py            │
│  @server.call_tool() → check_drug_interactions              │
└───────────────────────────┬─────────────────────────────────┘
                            │
      ┌─────────────────────┴──────────────────────┐
      │                                             │
      ▼                                             ▼
┌──────────────────┐                    ┌────────────────────┐
│  app/db/         │                    │  ai/services/      │
│  medications.py  │                    │  ddi_analyzer.py   │
│  (get meds)      │                    │  (analyze DDI)     │
└──────────────────┘                    └────────────────────┘
      │                                             │
      └─────────────────────┬──────────────────────┘
                            │
                            ▼
          Formatted DDI report with safety indicators
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Claude Desktop displays clinical decision support          │
└─────────────────────────────────────────────────────────────┘
```

**Key Difference from Server #1:**
- Server #1: Database queries → format → return
- Server #2: Database queries → **algorithms/analysis** → format → return

---

### Code Structure Overview

The server has 4 main sections:

1. **Setup & Imports** (lines 1-90): Environment, logging, dependencies
2. **Tool Definitions** (lines 95-205): MCP tool schemas with detailed descriptions
3. **Tool Execution** (lines 210-270): Router that calls appropriate handler
4. **Tool Implementations** (lines 275-750): Clinical algorithms and business logic

---

### Attribution Pattern (Clinical Auditability)

**Added:** 2026-02-02 (v1.3)

Like Server #1, all tools in this server include **data provenance attribution** showing exactly what data sources, algorithms, and guidelines were used.

**Clinical Decision Support-Specific Attribution:**

Beyond basic data sources, clinical tools include:
- **Algorithm versions** (e.g., "CKD-EPI 2021 race-neutral")
- **Guideline editions** (e.g., "USPSTF 2024")
- **Reference databases** (e.g., "DrugBank ~191K interactions")
- **Risk levels** (e.g., "Risk Score: 8/20, Risk Level: Moderate")

**Example: DDI Analysis Attribution**

```markdown
**DRUG-DRUG INTERACTION ANALYSIS**

⚠️ 2 INTERACTIONS FOUND ⚠️

1. GABAPENTIN + MORPHINE → **MAJOR** severity
   Effect: Increased CNS depression...

---

**Data Provenance:**
  • **Tool:** `check_drug_interactions`
  • **Data Sources:** DrugBank reference database (~191K interactions), PostgreSQL patient_medications_outpatient table, PostgreSQL patient_medications_inpatient table, MinIO Parquet (gold/ddi_reference.parquet)
  • **Analysis Timestamp:** 2026-02-02 15:45 UTC
  • **Medications analyzed:** 7
  • **Interactions found:** 2
```

**Example: eGFR Calculation Attribution**

```markdown
**eGFR CALCULATION**

Result: 52.3 mL/min/1.73m²
Stage: CKD Stage 3a (Moderate)

---

**Data Provenance:**
  • **Tool:** `calculate_ckd_egfr`
  • **Data Sources:** CKD-EPI 2021 equation (race-neutral), User-provided lab values (serum creatinine)
  • **Analysis Timestamp:** 2026-02-02 15:50 UTC
  • **eGFR Result:** 52.3 mL/min/1.73m²
  • **CKD Stage:** CKD Stage 3a (Moderate)
  • **Equation Reference:** Inker et al., NEJM 2021
```

**Why This Matters for Clinical Decision Support:**
1. **Algorithm Traceability:** Clinicians can verify which equations/guidelines were used
2. **Version Control:** Timestamps + references enable retrospective validation
3. **Regulatory Compliance:** Meets FDA guidance for clinical decision support transparency
4. **Safety:** Explicit display of risk levels and data completeness

**Implementation Pattern:** Same `_add_attribution_footer()` helper as Server #1 (lines 91-135)

---

### Section 1: Setup & Imports (Lines 1-90)

**Same pattern as Server #1:**
- Path setup before imports
- Explicit `.env` loading
- Comprehensive error handling
- File logging for debugging

**New Addition: DDIAnalyzer Import (Line 67)**

```python
from ai.services.ddi_analyzer import DDIAnalyzer
```

This is **code reuse, not duplication**. The MCP server wraps existing AI business logic.

**Why This Matters:**
- DRY principle: Don't duplicate DDI logic
- Single source of truth for drug interaction analysis
- MCP server is a **thin wrapper** over existing services

---

### Section 2: Tool Definitions (Lines 95-205)

**Tool 1: check_drug_interactions**

```python
types.Tool(
    name="check_drug_interactions",
    description=(
        "Analyze patient's medications for drug-drug interactions (DDI). "
        "Uses DrugBank reference database (~191K interactions). "
        "Returns DDI details with descriptions of interaction effects. "
        "Critical for medication safety review."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "patient_icn": {
                "type": "string",
                "description": "Patient Integrated Care Number (ICN)"
            }
        },
        "required": ["patient_icn"]
    }
)
```

**Description Best Practices:**
- What it does: "Analyze patient's medications for drug-drug interactions"
- Data source: "Uses DrugBank reference database (~191K interactions)"
- Return value: "Returns DDI details with descriptions"
- Clinical context: "Critical for medication safety review"

**Why Detailed Descriptions Matter:**
Claude uses descriptions to decide **when** to call the tool. Good descriptions = better agent behavior.

---

**Tool 2: assess_fall_risk**

```python
types.Tool(
    name="assess_fall_risk",
    description=(
        "Calculate patient's fall risk score based on medications, age, "
        "and clinical factors. Uses standardized fall risk assessment criteria. "
        "Returns risk level (Low/Moderate/High) with contributing factors. "
        "Useful for geriatric and inpatient safety planning."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "patient_icn": {"type": "string", "description": "..."}
        },
        "required": ["patient_icn"]
    }
)
```

**Clinical Algorithm Tool Pattern:**
- Input: Patient identifier only (fetches other data internally)
- Output: Risk level + contributing factors + recommendations
- Use case specified: "geriatric and inpatient safety planning"

---

**Tool 3: calculate_ckd_egfr**

```python
types.Tool(
    name="calculate_ckd_egfr",
    description=(
        "Calculate estimated Glomerular Filtration Rate (eGFR) using CKD-EPI equation. "
        "Assesses kidney function for chronic kidney disease staging. "
        "Returns eGFR value and CKD stage interpretation (1-5). "
        "Essential for medication dosing adjustments."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "creatinine_mg_dl": {"type": "number", "description": "..."},
            "age": {"type": "integer", "description": "..."},
            "sex": {
                "type": "string",
                "enum": ["M", "F", "male", "female"],
                "description": "Patient sex (M/F or male/female)"
            },
            "race_black": {
                "type": "boolean",
                "description": "Is patient Black/African American? (default: false)",
                "default": False
            }
        },
        "required": ["creatinine_mg_dl", "age", "sex"]
    }
)
```

**Medical Calculator Pattern:**
- Multiple required inputs (not just patient_icn)
- Enums for constrained values (sex: M/F)
- Optional parameters with defaults (race_black)
- Clinical application stated: "Essential for medication dosing adjustments"

---

**Tool 4: recommend_cancer_screening**

```python
types.Tool(
    name="recommend_cancer_screening",
    description=(
        "Recommend age-appropriate cancer screenings based on USPSTF guidelines. "
        "Evaluates patient eligibility for colorectal, breast, cervical, lung, "
        "and prostate cancer screening. Returns personalized screening recommendations "
        "with rationale. Supports preventive care planning."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "patient_icn": {"type": "string", "description": "..."}
        },
        "required": ["patient_icn"]
    }
)
```

**Guideline-Based Tool Pattern:**
- External reference: "USPSTF guidelines"
- Comprehensive scope: Lists all screening types covered
- Personalized output: "with rationale"
- Clinical workflow: "preventive care planning"

---

### Section 3: Tool Execution Router (Lines 210-270)

**Same pattern as Server #1** with enhanced error handling:

```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        if name == "check_drug_interactions":
            result = await _check_drug_interactions(arguments["patient_icn"])

        elif name == "assess_fall_risk":
            result = await _assess_fall_risk(arguments["patient_icn"])

        elif name == "calculate_ckd_egfr":
            result = _calculate_ckd_egfr(
                creatinine=arguments["creatinine_mg_dl"],
                age=arguments["age"],
                sex=arguments["sex"],
                race_black=arguments.get("race_black", False)
            )
        # ... more tools

        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_msg = f"⚠️ Error: {str(e)}\n\nPlease verify patient data and try again."
        return [types.TextContent(type="text", text=error_msg)]
```

**Key Differences from Server #1:**
1. **calculate_ckd_egfr** is **synchronous** (pure calculation, no DB/IO)
   - No `await` - it's a math function
   - No `asyncio.to_thread()` needed
2. **Error messages use warning emoji** (⚠️) for clinical safety
3. **User-friendly error guidance** ("Please verify patient data and try again")

---

### Section 4: Tool Implementations

#### Implementation 1: check_drug_interactions (Lines 275-315)

**Code Walkthrough:**

```python
async def _check_drug_interactions(patient_icn: str) -> str:
    # Step 1: Get patient medications (async database query)
    medications = await asyncio.to_thread(
        get_patient_medications,
        patient_icn
    )

    # Step 2: Guard clause - handle missing data
    if not medications:
        return "No active medications found. Cannot perform DDI analysis."

    # Step 3: Initialize DDI analyzer (loads ~191K interactions from MinIO)
    analyzer = DDIAnalyzer()

    # Step 4: Run analysis (wraps existing AI service)
    interactions = await asyncio.to_thread(
        analyzer.find_interactions,
        medications
    )

    # Step 5: Format results for AI consumption
    return _format_ddi_results(interactions, len(medications))
```

**Pattern: Wrap Existing Service**
1. Fetch data (medications)
2. Initialize analyzer (existing class from `ai/services/`)
3. Call analyzer method (`find_interactions`)
4. Format results

**No Code Duplication:**
- DDI logic lives in `ai/services/ddi_analyzer.py`
- MCP server is a **thin wrapper**
- Same DDI analyzer used by LangGraph agent and MCP server

---

#### Implementation 2: assess_fall_risk (Lines 320-430)

**Clinical Algorithm Example:**

```python
async def _assess_fall_risk(patient_icn: str) -> str:
    # Fetch data
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)
    medications = await asyncio.to_thread(get_patient_medications, patient_icn)

    # Initialize scoring
    risk_score = 0
    factors = []

    # Factor 1: Age ≥65 (+2 points)
    if age >= 65:
        risk_score += 2
        factors.append(f"Age {age} (≥65 years)")

    # Factor 2: Polypharmacy ≥5 medications (+1 point)
    if med_count >= 5:
        risk_score += 1
        factors.append(f"Polypharmacy ({med_count} medications)")

    # Factor 3: High-risk medication classes (+1 each)
    high_risk_classes = [
        'benzodiazepine', 'sedative', 'hypnotic', 'antihypertensive',
        'diuretic', 'opioid', 'antipsychotic', 'anticonvulsant'
    ]
    # ... check medications for high-risk classes

    # Determine risk level
    if risk_score <= 1:
        risk_level = "LOW"
    elif risk_score <= 3:
        risk_level = "MODERATE"
    else:
        risk_level = "HIGH"

    # Return formatted assessment
    return formatted_result
```

**Clinical Scoring Pattern:**
- Clear scoring criteria (age, polypharmacy, high-risk meds)
- Evidence-based medication classes
- Risk stratification (Low/Moderate/High)
- Actionable recommendations based on risk level

**Real-World Application:**
This is a simplified fall risk assessment. Production systems would use validated tools like:
- Morse Fall Scale (6 items, validated in hospitals)
- STRATIFY (5 items, validated in elderly care)
- Hendrich II Fall Risk Model (8 items, widely used)

---

#### Implementation 3: calculate_ckd_egfr (Lines 435-580)

**Medical Calculator Example:**

```python
def _calculate_ckd_egfr(creatinine: float, age: int, sex: str, race_black: bool = False) -> str:
    """
    CKD-EPI Equation (2021 race-neutral version):
    eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.200 × 0.9938^Age × [1.012 if female]
    """

    # Normalize input
    sex = sex.upper()[0]  # 'M' or 'F'

    # CKD-EPI parameters by sex
    if sex == 'F':
        kappa = 0.7
        alpha = -0.241
        sex_multiplier = 1.012
    else:
        kappa = 0.9
        alpha = -0.302
        sex_multiplier = 1.0

    # Calculate eGFR
    min_term = min(creatinine / kappa, 1.0) ** alpha
    max_term = max(creatinine / kappa, 1.0) ** -1.200
    age_term = 0.9938 ** age
    egfr = 142 * min_term * max_term * age_term * sex_multiplier

    # Stage CKD (G1-G5)
    if egfr >= 90:
        stage = "G1 (Normal or high)"
    # ... other stages

    return formatted_result
```

**Medical Calculator Pattern:**
- **Cited equation**: CKD-EPI 2021 (includes reference)
- **Precise implementation**: Exact formula from medical literature
- **Clinical interpretation**: eGFR value → CKD stage → risk level
- **Actionable output**: Recommendations for each stage

**Why This Matters:**
- eGFR is **critical** for medication dosing (many drugs renally cleared)
- CKD staging guides clinical management
- This is a **real clinical calculator** used daily in healthcare

---

#### Implementation 4: recommend_cancer_screening (Lines 585-750)

**Guideline-Based Decision Support:**

```python
async def _recommend_cancer_screening(patient_icn: str) -> str:
    # Get patient demographics
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)
    age = calculate_age_from_dob(demographics['date_of_birth'])
    sex = demographics['sex']

    recommendations = []

    # Colorectal cancer (all adults 45-75)
    if 45 <= age <= 75:
        recommendations.append({
            'cancer': 'Colorectal Cancer',
            'screening': 'Colonoscopy every 10 years OR FIT annual',
            'grade': 'A',  # USPSTF grade
            'reason': f'Age {age} (recommended 45-75)'
        })

    # Breast cancer (females 50-74)
    if sex == 'F' and 50 <= age <= 74:
        recommendations.append({
            'cancer': 'Breast Cancer',
            'screening': 'Mammography every 2 years',
            'grade': 'B',
            'reason': f'Female, age {age} (recommended 50-74)'
        })

    # ... cervical, lung, prostate screenings

    return formatted_recommendations
```

**Guideline Implementation Pattern:**
- **External authority**: USPSTF (U.S. Preventive Services Task Force)
- **Evidence grades**: A (strongly recommended), B (recommended), C (selective)
- **Age/sex stratification**: Different guidelines for different populations
- **Personalized output**: Shows WHY each screening is recommended

**Production Considerations:**
- Guideline updates: USPSTF reviews recommendations every 5 years
- Additional risk factors: Family history, genetic mutations (BRCA)
- Shared decision-making: Grade C = discuss with patient

---

### Section 5: Helper Functions

#### _format_ddi_results (Lines 760-810)

**Safety-First Formatting Pattern:**

```python
def _format_ddi_results(interactions: list[dict], med_count: int) -> str:
    # Case 1: No interactions - EXPLICIT confirmation (not silence)
    if not interactions:
        return (
            f"✅ **No Drug-Drug Interactions Detected**\n\n"
            f"Analyzed {med_count} medications - no significant interactions found.\n"
        )

    # Case 2: Interactions found - Safety highlighting
    result = f"⚠️ **Drug-Drug Interactions Found**\n\n"
    result += f"Analyzed {med_count} medications, found **{len(interactions)} interactions**:\n\n"

    for i, ddi in enumerate(interactions, 1):
        result += f"**{i}. {ddi['drug_a']} + {ddi['drug_b']}**\n"
        result += f"   Interaction: {ddi['description']}\n\n"

    # Always include recommendations
    result += "\n**Clinical Recommendations:**\n"
    result += "  • Review interaction severity with clinical pharmacist\n"
    result += "  • Consider dose adjustments or alternative medications\n"

    return result
```

**Clinical Safety Principles:**
1. **No Silent Failures**: "No interactions" is explicitly stated (not empty return)
2. **Visual Indicators**: ✅ for safe, ⚠️ for caution
3. **Transparency**: Show what was analyzed ("Analyzed X medications")
4. **Action-Oriented**: Always include clinical recommendations
5. **Context Preservation**: Include both drug names + interaction description

---

## Testing Steps for Section 6

### Prerequisites

1. **Section 5 Complete and Working**
   - EHR Data Server must be operational
   - Database connection verified
   - DDI reference data loaded in MinIO

2. **Verify DDI Reference Data**
```bash
# Check if DDI data exists
python -c "from ai.services.ddi_analyzer import DDIAnalyzer; analyzer = DDIAnalyzer(); print(f'Loaded {len(analyzer.ddi_data):,} interactions')"

# Expected output: "Loaded 191,xxx interactions"
```

If this fails, you may need to run the DDI ETL pipeline first.

---

### Test 1: Run Server Standalone

```bash
cd /Users/chuck/swdev/med/med-z1
python mcp_servers/clinical_decision_support_server.py
```

**Expected Output:**
```
DEBUG: Project root: /Users/chuck/swdev/med/med-z1
DEBUG: .env loaded successfully
DEBUG: All modules imported successfully
INFO:clinical-decision-support-server:Starting Clinical Decision Support MCP Server...
INFO:clinical-decision-support-server:Available tools: check_drug_interactions, assess_fall_risk, calculate_ckd_egfr, recommend_cancer_screening
```

Press `Ctrl+C` to stop.

---

### Test 2: Configure Claude Desktop

**macOS Config:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ehr-data": {
      "command": "/Users/chuck/swdev/med/med-z1/.venv/bin/python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcp_servers/ehr_server.py"],
      "cwd": "/Users/chuck/swdev/med/med-z1"
    },
    "clinical-decision-support": {
      "command": "/Users/chuck/swdev/med/med-z1/.venv/bin/python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcp_servers/clinical_decision_support_server.py"],
      "cwd": "/Users/chuck/swdev/med/med-z1"
    }
  }
}
```

**Note:** You now have **2 MCP servers** running simultaneously!

**Restart Claude Desktop** after config changes.

---

### Test 3: Test Each Tool

**Test 3a: check_drug_interactions**

```
Are there any drug interactions for patient ICN100001?
```

**Expected Response:**
- Claude calls `check_drug_interactions` tool
- Server queries medications, runs DDI analysis
- Returns formatted DDI report
- Claude synthesizes natural language response

**Expected Output (example):**
```
⚠️ **Drug-Drug Interactions Found**

Analyzed 7 medications, found 2 interactions:

1. Gabapentin + Alprazolam
   Interaction: The risk or severity of adverse effects can be increased...

2. Aspirin + Warfarin
   Interaction: The risk or severity of bleeding can be increased...
```

---

**Test 3b: assess_fall_risk**

```
What is the fall risk for patient ICN100001?
```

**Expected Response:**
- Claude calls `assess_fall_risk` tool
- Server calculates risk score from age + medications
- Returns risk level + contributing factors

**Expected Output (example):**
```
🟡 **Fall Risk Assessment: MODERATE**
Risk Score: 3 points

Contributing Factors:
  • Age 68 (≥65 years)
  • Polypharmacy (7 medications)
  • High-risk medications: Gabapentin, Alprazolam

Recommendations:
  • Monitor for fall risk factors
  • Review medications periodically
```

---

**Test 3c: calculate_ckd_egfr**

```
Calculate eGFR for a 70-year-old male with creatinine 1.5 mg/dL
```

**Expected Response:**
- Claude calls `calculate_ckd_egfr` with parameters
- Server runs CKD-EPI equation
- Returns eGFR value + CKD stage

**Expected Output (example):**
```
🟡 **eGFR Result: 47.3 mL/min/1.73m²**

CKD Stage: G3a (Mildly to moderately decreased)
Clinical Risk: Moderate risk

Input Parameters:
  • Creatinine: 1.5 mg/dL
  • Age: 70 years
  • Sex: Male
```

---

**Test 3d: recommend_cancer_screening**

```
What cancer screenings are recommended for patient ICN100001?
```

**Expected Response:**
- Claude calls `recommend_cancer_screening` tool
- Server checks age/sex against USPSTF guidelines
- Returns personalized screening recommendations

**Expected Output (example):**
```
**Cancer Screening Recommendations** (M, age 68)

🟢 Colorectal Cancer (Grade A)
   Screening: Colonoscopy every 10 years OR FIT annual
   Reason: Age 68 (recommended 45-75)

🟡 Lung Cancer (Grade B)
   Screening: Low-dose CT if ≥20 pack-year smoking history
   Reason: Age 68 - verify smoking history
```

---

### Test 4: Multi-Tool Conversation

**Advanced Test** - Claude uses multiple tools in one conversation:

```
Give me a comprehensive clinical safety assessment for patient ICN100001.
Include drug interactions, fall risk, and screening recommendations.
```

**What Should Happen:**
1. Claude calls `check_drug_interactions`
2. Claude calls `assess_fall_risk`
3. Claude calls `recommend_cancer_screening`
4. Claude synthesizes all 3 results into coherent narrative

**This tests:**
- Multi-tool orchestration
- Tool selection logic (Claude decides what to call)
- Result synthesis (combining structured data into clinical summary)

---

### Validation Checklist

After testing, verify:

- ✅ Server starts without errors
- ✅ All 4 tools appear in Claude Desktop MCP list
- ✅ DDI analysis returns interactions (if patient has interacting meds)
- ✅ Fall risk calculation includes age, polypharmacy, and medication factors
- ✅ eGFR calculator produces clinically accurate results
- ✅ Screening recommendations match USPSTF guidelines for patient age/sex
- ✅ Error handling works (try invalid patient ICN, missing data)
- ✅ Results are formatted clearly with clinical safety emphasis

---

### Common Issues & Solutions

**Issue: "No module named 'ai.services.ddi_analyzer'"**
- DDI analyzer module is missing or not imported correctly
- **Solution:** Verify `ai/services/ddi_analyzer.py` exists
- Check: `ls -la /Users/chuck/swdev/med/med-z1/ai/services/ddi_analyzer.py`

**Issue: DDI analysis fails with "DDI reference data not found"**
- DDI Parquet file not loaded in MinIO
- **Solution:** Run DDI ETL pipeline to load reference data
- Or: Use mock DDI data for testing (see `ai/services/ddi_analyzer.py` init)

**Issue: Fall risk returns "LOW" for everyone**
- Age calculation failing (DOB parsing issue)
- **Solution:** Check patient demographics have valid `date_of_birth` field
- Debug: Add logging to see calculated age

**Issue: eGFR calculation returns unexpected values**
- Input units mismatch (creatinine in umol/L instead of mg/dL)
- **Solution:** Verify creatinine input is in mg/dL (standard US units)
- Conversion: umol/L ÷ 88.4 = mg/dL

**Issue: Cancer screening shows no recommendations**
- Patient age outside screening ranges
- **Solution:** This is expected! Not all ages have grade A/B screenings
- Test with different patient ages (e.g., 50-year-old for breast cancer)

**Issue: Claude doesn't call the tools**
- Tool descriptions may be unclear
- **Solution:** Ask Claude explicitly: "Use the check_drug_interactions tool for patient ICN100001"
- This helps debug if issue is tool calling vs. tool execution

---

### Next Steps

Once all tests pass:

1. ✅ **Section 6 Complete!** You have clinical decision support tools.
2. 📚 **Review algorithm implementations** - Understand fall risk scoring, eGFR equation, USPSTF guidelines
3. 💡 **Experiment:** Add severity classification to DDI results (Major/Moderate/Minor)
4. 🎯 **Real-world enhancement:** Integrate real smoking history for lung cancer screening
5. ➡️ **Ready for Section 7?** Clinical Notes Search Server (keyword → vector search)

---

**End of Section 6 Walkthrough**

*Section 7 will be added when you're ready to implement Clinical Notes Search.*

