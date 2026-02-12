# MCP Servers for med-z1

Model Context Protocol servers that expose clinical data and AI capabilities to MCP clients like Claude Desktop.

## Quick Start

### Installation

```bash
# Install MCP SDK
pip install mcp

# Verify installation
python -c "import mcp; print('MCP ready')"
```

### Running MCP Servers

**For Normal Use (Claude Desktop):**

**You do NOT need to start MCP servers manually.** Once configured in `claude_desktop_config.json` (see [Connecting to Claude Desktop](#connecting-to-claude-desktop) below), Claude Desktop **automatically starts all configured servers** when it launches and manages their lifecycle (start, monitor, restart if crashed, stop on quit).

**For Testing/Debugging Only:**

If you need to test a server standalone (to check for errors), run it manually:

**EHR Data Server:**
```bash
cd /Users/chuck/swdev/med/med-z1
python mcpsvr/ehr_server.py
```

**Clinical Decision Support Server:**
```bash
cd /Users/chuck/swdev/med/med-z1
python mcpsvr/clinical_decision_support_server.py
```

**Alternative (module syntax):**
```bash
python -m mcpsvr.ehr_server
python -m mcpsvr.clinical_decision_support_server
```

Both methods work because the servers have path setup code built-in.

**Expected output (either server):**
```
DEBUG: Project root: /Users/chuck/swdev/med/med-z1
DEBUG: .env loaded successfully
INFO:...:Starting ... MCP Server...
INFO:...:Available tools: ...
```

Press `Ctrl+C` to stop.

**Note:** Manual startup is useful for:
- Verifying imports work correctly
- Checking database connectivity before configuring Claude Desktop
- Debugging error messages that aren't visible in Claude Desktop logs

## Available Servers

### 1. EHR Data Server (`ehr_server.py`) ✅ COMPLETE

**Status:** Operational (Section 5 complete)

**Tools:**
- `get_patient_summary` - Comprehensive patient overview
- `get_patient_medications` - Active medications list
- `get_patient_vitals` - Recent vital signs (last 7 days)
- `get_patient_allergies` - Known allergies with severity
- `get_patient_encounters` - Recent visits (last 90 days)

**What it does:**
- Wraps `app/db/` database query functions
- Formats data for AI consumption (Markdown)
- Handles async/sync bridge with `asyncio.to_thread()`

**Documentation:** See `docs/guide/code-walkthrough.md` Section 5

### 2. Clinical Decision Support Server (`clinical_decision_support_server.py`) ✅ COMPLETE

**Status:** Operational (Section 6 complete)

**Tools:**
- `check_drug_interactions` - DDI analysis using DrugBank reference (~191K interactions)
- `assess_fall_risk` - Fall risk scoring from medications, age, clinical factors
- `calculate_ckd_egfr` - CKD-EPI eGFR calculation for kidney function assessment
- `recommend_cancer_screening` - USPSTF guideline-based screening recommendations

**What it does:**
- Wraps `ai/services/` business logic (e.g., DDIAnalyzer)
- Implements clinical algorithms (fall risk, eGFR, screening guidelines)
- Provides safety-first formatting (risk highlighting, explicit confirmations)
- Returns actionable clinical decision support

**Documentation:** See `docs/guide/code-walkthrough.md` Section 6

### 3. Clinical Notes Search Server

**Status:** Coming in Section 7

## Data Provenance and Attribution

**Added:** 2026-02-02 (v1.3)

All MCP tools (9 total across both servers) include **data provenance footers** that show exactly what data sources, algorithms, and tools were used to generate each response.

### Why Attribution Matters

- **Clinical Safety:** Transparency about data sources builds trust in AI-generated responses
- **Regulatory Compliance:** Meets FDA guidance for clinical decision support transparency
- **Auditability:** Provides evidence trail for clinical decisions
- **Debugging:** Helps identify data quality issues by showing which databases were queried
- **Version Control:** Timestamps enable correlation with database state at query time

### What's Included in Attribution

Every tool response includes a standardized footer with:

1. **Tool Name:** Which MCP tool generated the response
2. **Data Sources:** List of databases, APIs, reference files, or algorithms used
3. **Analysis Timestamp:** UTC timestamp of when the query was executed
4. **Metadata:** Relevant context like record counts, risk levels, guideline versions

### Example Output

When you ask "What medications is patient ICN100001 on?" in Claude Desktop, you'll see:

```markdown
**MEDICATIONS** (7 active)
- GABAPENTIN 300MG CAP (take 1 capsule by mouth three times a day), started 2025-10-15
- LISINOPRIL 10MG TAB (take 1 tablet by mouth daily), started 2025-09-01
...

---

**Data Provenance:**
  • Tool: get_patient_medications
  • Data Sources: PostgreSQL patient_medications_outpatient table, PostgreSQL patient_medications_inpatient table
  • Analysis Timestamp: 2026-02-02 15:30 UTC
  • Medications retrieved: 7
```

### Clinical Decision Support Attribution

Clinical decision support tools include additional metadata:

- **Algorithm versions** (e.g., "CKD-EPI 2021 race-neutral equation")
- **Guideline editions** (e.g., "USPSTF 2024")
- **Reference databases** (e.g., "DrugBank ~191K interactions")
- **Risk assessments** (e.g., "Risk Score: 8/20, Risk Level: Moderate")

**Example: DDI Analysis**

```markdown
**DRUG-DRUG INTERACTION ANALYSIS**

⚠️ 2 INTERACTIONS FOUND ⚠️
...

---

**Data Provenance:**
  • Tool: check_drug_interactions
  • Data Sources: DrugBank reference database (~191K interactions), PostgreSQL patient_medications_outpatient table, PostgreSQL patient_medications_inpatient table, PostgreSQL reference.ddi table
  • Analysis Timestamp: 2026-02-02 15:45 UTC
  • Medications analyzed: 7
  • Interactions found: 2
```

### Implementation Details

The attribution pattern is implemented using a shared `_add_attribution_footer()` helper function in both servers. See `docs/guide/code-walkthrough.md` Sections 5 and 6 for detailed code explanations.

**Tools with Attribution:**
- **EHR Data Server (5 tools):** get_patient_summary, get_patient_medications, get_patient_vitals, get_patient_allergies, get_patient_encounters
- **Clinical Decision Support Server (4 tools):** check_drug_interactions, assess_fall_risk, calculate_ckd_egfr, recommend_cancer_screening

## Connecting to Claude Desktop

### Configuration

**macOS:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ehr-data": {
      "command": "/Users/chuck/swdev/med/med-z1/.venv/bin/python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcpsvr/ehr_server.py"],
      "cwd": "/Users/chuck/swdev/med/med-z1"
    },
    "clinical-decision-support": {
      "command": "/Users/chuck/swdev/med/med-z1/.venv/bin/python",
      "args": ["/Users/chuck/swdev/med/med-z1/mcpsvr/clinical_decision_support_server.py"],
      "cwd": "/Users/chuck/swdev/med/med-z1"
    }
  }
}
```

**⚠️ IMPORTANT:** Update all paths to match your actual project location!

**How It Works:**
- Claude Desktop **automatically starts both servers** when it launches
- Servers run in the background (you won't see terminal windows)
- Claude Desktop monitors health and restarts servers if they crash
- Servers stop automatically when Claude Desktop quits
- **You do NOT need to start servers manually** for normal use
- Both "ehr-data" and "clinical-decision-support" appear in Claude Desktop's MCP servers list

**Windows:**
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ehr-data": {
      "command": "C:\\Users\\YourUsername\\path\\to\\med-z1\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YourUsername\\path\\to\\med-z1\\mcpsvr\\ehr_server.py"],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\med-z1"
    },
    "clinical-decision-support": {
      "command": "C:\\Users\\YourUsername\\path\\to\\med-z1\\.venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YourUsername\\path\\to\\med-z1\\mcpsvr\\clinical_decision_support_server.py"],
      "cwd": "C:\\Users\\YourUsername\\path\\to\\med-z1"
    }
  }
}
```

**Configuration Explained:**
- **`command`** - **Full path** to your virtual environment's Python interpreter (required - Claude Desktop doesn't inherit activated venv)
- **`args`** - **Full path** to the server script (more reliable than `-m` module syntax)
- **`cwd`** - Sets working directory to project root (required for imports to work)

**Why Full Paths?**
Claude Desktop runs in its own environment and doesn't see your activated virtual environment. Using full paths ensures it finds the correct Python with all dependencies installed.

### Testing

1. **Restart Claude Desktop** after config changes
2. **Verify connection:** Look for "ehr-data" and "clinical-decision-support" in MCP servers list
3. **Test EHR Data Server:**
   - "What medications is patient ICN100001 on?"
   - "Give me a clinical summary of patient ICN100001"
   - "What are the latest vitals for ICN100001?"
4. **Test Clinical Decision Support Server:**
   - "Are there any drug interactions for patient ICN100001?"
   - "What is the fall risk for patient ICN100001?"
   - "Calculate eGFR for a 70-year-old male with creatinine 1.5 mg/dL"
   - "What cancer screenings are recommended for patient ICN100001?"

## Test Patients

The following test patients have comprehensive data:

- **ICN100001** (Dooree, Adam) - Full data across all domains
- **ICN100010** (Aminor, Alexander) - Multi-site data, 2-4 sites
- **ICN100013** (Thompson, Irving) - 3 sites, 6 DFNs (deduplication stress test)
- **ICN100002** (Miifaa, Barry) - 3 sites with varied data

## Troubleshooting

### Server won't start

**Error:** `ModuleNotFoundError: No module named 'mcp'`
```bash
pip install mcp
```

**Error:** `ModuleNotFoundError: No module named 'app'`
- Run from project root: `/Users/chuck/swdev/med/med-z1`
- Check PYTHONPATH in Claude config

### Claude Desktop can't connect

**Error:** "Server disconnected"

1. Check Claude Desktop logs: `~/Library/Logs/Claude/mcp-server-ehr-data.log` (macOS)
2. Most common cause: Using system Python instead of venv Python
   - **Solution:** Use full path to venv Python in config (see Configuration section)
3. Check `claude_desktop_config.json` is valid JSON (no trailing commas!)
4. Verify all paths are absolute (not relative)
5. Restart Claude Desktop completely (quit, not just close window)
6. Check server starts without errors when run standalone
7. Verify `.env` has `POSTGRES_*` environment variables configured

### Tool calls fail

**Check database connection:**
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM patient_demographics"
```

**Check logs:**
Run server standalone and watch for errors:
```bash
cd /Users/chuck/swdev/med/med-z1
python mcpsvr/ehr_server.py
# Then trigger tool call from Claude Desktop
# Check terminal for error messages
```

## Architecture

```
Claude Desktop
    ↓ (MCP Protocol - stdio)
mcpsvr/ehr_server.py
    ↓ (asyncio.to_thread)
app/db/*.py (Data Access Layer)
    ↓ (SQLAlchemy)
PostgreSQL Database
```

**Key Pattern:** MCP server is async, database queries are sync. Bridge with `asyncio.to_thread()`.

## Development

### Adding a New Tool

1. **Define tool** in `@server.list_tools()`:
```python
types.Tool(
    name="get_patient_labs",
    description="Get recent lab results for a patient",
    inputSchema={
        "type": "object",
        "properties": {
            "patient_icn": {"type": "string"}
        },
        "required": ["patient_icn"]
    }
)
```

2. **Implement handler** in `@server.call_tool()`:
```python
elif name == "get_patient_labs":
    patient_icn = arguments["patient_icn"]
    labs = await asyncio.to_thread(get_patient_labs, patient_icn)
    result = _format_labs(labs)
```

3. **Add formatting function:**
```python
def _format_labs(labs: list[dict]) -> str:
    # Format for AI consumption
    return formatted_text
```

4. **Test** with Claude Desktop

## Resources

- **MCP Specification:** https://modelcontextprotocol.io/
- **Python SDK Docs:** https://github.com/modelcontextprotocol/python-sdk
- **Code Walkthrough:** `docs/guide/code-walkthrough.md`
- **Main Learning Guide:** `docs/guide/clinical-ai-career-preparation.md`

## Next Steps

- ✅ Section 5 complete (EHR Data Server)
- ✅ Section 6 complete (Clinical Decision Support Server)
- ⏭️ Section 7: Build Clinical Notes Search Server

---

**Version:** 1.3
**Last Updated:** 2026-02-02
**Status:** Two servers operational (EHR Data + Clinical Decision Support), Section 7 in development

**v1.3 Changes (2026-02-02):**
- Added "Data Provenance and Attribution" section documenting attribution footers
- All 9 tools now include data source transparency for clinical auditability
- Documented attribution pattern with examples for medications and DDI analysis
- Updated for regulatory compliance and FDA guidance on clinical decision support transparency

**v1.2 Changes (2026-02-02):**
- Added Server #2: Clinical Decision Support (4 tools: DDI, fall risk, eGFR, cancer screening)
- Updated configuration examples to show both servers running simultaneously
- Clarified automatic server lifecycle management by Claude Desktop
- Added note that manual startup is only for testing/debugging
- Updated testing section with prompts for both servers

**v1.1 Changes (2026-02-02):**
- Updated Claude Desktop config to use full paths (resolves "Server disconnected" errors)
- Added troubleshooting for common connection issues
- Added explanation of why full paths are required
- Updated all command examples to use correct module syntax
