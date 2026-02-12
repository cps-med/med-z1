# AI Clinical Insights Subsystem

**Status:** Phase 1-5 Complete ✅
**Last Updated:** 2026-01-14

## Overview

The AI Clinical Insights subsystem provides an intelligent chatbot interface to help clinicians discover insights about patients through natural language conversation. The system uses Agentic RAG (Retrieval-Augmented Generation) with LangGraph to query existing med-z1 data sources and provide evidence-based responses.

## Current Capabilities (Phases 1-5 Complete)

### Available Tools (5)

1. **`check_ddi_risks`** - Drug-Drug Interaction Risk Assessment
   - Analyzes patient medications for potential interactions
   - Uses ~191K interaction database from DrugBank (via Kaggle)
   - Returns natural language summary with interaction descriptions
   - Example: "Found 1 interaction: GABAPENTIN + ALPRAZOLAM"

2. **`get_patient_summary`** - Comprehensive Patient Clinical Summary
   - Synthesizes demographics, problems, medications, vitals, allergies, family history, encounters, clinical notes
   - Returns multi-section natural language overview
   - Covers 6 clinical domains (added clinical notes in Phase 4)
   - Includes 3 most recent clinical notes automatically
   - Handles missing data gracefully ("No ... on record")

3. **`analyze_vitals_trends`** - Statistical Vital Sign Trend Analysis (Phase 3)
   - Linear regression analysis for BP, HR, temperature trends
   - Statistical variance and clinical norm comparisons
   - Identifies concerning patterns (e.g., rising BP, declining HR)
   - Uses PostgreSQL historical data + cached Vista RPC responses when available

4. **`get_clinical_notes_summary`** - Clinical Notes Query Tool (Phase 4)
   - Retrieves and summarizes clinical notes with filtering
   - Supports note type filtering: Progress Notes, Consults, Discharge Summaries, Imaging
   - Date range filtering (default 90 days lookback)
   - Returns 500-char note previews with full metadata
   - Example: "Show me cardiology consult notes from the last 6 months"

### Key Features

- ✅ **LangGraph Agent:** Uses GPT-4-turbo with tool binding (LangGraph 1.0.5 API)
- ✅ **Intelligent Tool Selection:** Agent autonomously decides which tools to invoke
- ✅ **Multi-Tool Synthesis:** Agent can combine multiple tools in a single response
- ✅ **Natural Language Formatting:** All data converted from structured (dicts/lists) to prose
- ✅ **Error Handling:** Graceful degradation when data is missing or unavailable
- ✅ **Web UI:** Chat interface at `/insight` with HTMX-powered interactions (Phase 2)
- ✅ **Statistical Analysis:** Linear regression and variance analysis for vitals trends (Phase 3)
- ✅ **Clinical Notes Integration:** Automatic inclusion in summaries + dedicated query tool (Phase 4)
- ✅ **Conversation Export:** Download chat transcripts as HTML files (Phase 5)
- ✅ **Vista Integration:** Supports cached Vista RPC responses for real-time data overlay

### Future Tool Enhancements (Planned)

**Note:** The following tools have been implemented as **MCP servers** (Sections 5-6) for external clients like Claude Desktop, but are not yet available in the web UI's LangGraph agent. They can be added by creating `@tool` wrappers in `ai/tools/` that reuse the existing business logic.

**Candidate Tools from MCP Server #2 (Clinical Decision Support):**
- **`assess_fall_risk`** - Fall risk scoring (age + medications + polypharmacy)
  - Logic exists in `mcpsvr/clinical_decision_support_server.py:_assess_fall_risk()`
  - Would add geriatric safety assessment to web UI
- **`calculate_ckd_egfr`** - CKD-EPI eGFR calculation for kidney function
  - Logic exists in `mcpsvr/clinical_decision_support_server.py:_calculate_ckd_egfr()`
  - Critical for medication dosing decisions
- **`recommend_cancer_screening`** - USPSTF guideline-based screening recommendations
  - Logic exists in `mcpsvr/clinical_decision_support_server.py:_recommend_cancer_screening()`
  - Supports preventive care planning

**Implementation Pattern:**
```python
# ai/tools/clinical_tools.py (new file)
from langchain_core.tools import tool

@tool
def assess_fall_risk(patient_icn: str) -> str:
    """Assess patient fall risk - LangGraph version"""
    # Reuse logic from MCP server
    # Same algorithm, different wrapper
    pass
```

Then add to `ai/tools/__init__.py:ALL_TOOLS` list.

**See:** `docs/spec/ai-insight-design.md` for architectural guidance on expanding tools.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Agent                             │
│                    (GPT-4-turbo, temp=0.3)                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │ uses tools
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ai/tools/                                    │
│  • check_ddi_risks (medication_tools.py)                        │
│  • get_patient_summary (patient_tools.py)                       │
│  • analyze_vitals_trends (vitals_tools.py)                      │
│  • get_clinical_notes_summary (notes_tools.py)                  │
│  • get_family_history (family_history_tools.py)                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ wraps
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ai/services/                                  │
│  • DDIAnalyzer (ddi_analyzer.py)                                │
│  • PatientContextBuilder (patient_context.py)                   │
│  • VitalsTrendAnalyzer (vitals_trend_analyzer.py)               │
└──────────────────────┬──────────────────────────────────────────┘
                       │ queries
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              app/db/ + app/services/                            │
│  • get_patient_demographics()                                   │
│  • get_patient_medications()                                    │
│  • get_recent_vitals()                                          │
│  • get_patient_allergies()                                      │
│  • get_recent_encounters()                                      │
│  • get_all_notes() / get_recent_notes_for_ai()                  │
│  • get_ddi_reference() (MinIO Parquet)                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
                PostgreSQL + MinIO
```

## Directory Structure

```
ai/
├── README.md                      # This file
├── __init__.py                    # Package exports
├── agents/
│   ├── __init__.py
│   └── insight_agent.py           # LangGraph agent with ToolNode
├── tools/
│   ├── __init__.py                # ALL_TOOLS export (5 tools)
│   ├── medication_tools.py        # check_ddi_risks
│   ├── patient_tools.py           # get_patient_summary
│   ├── vitals_tools.py            # analyze_vitals_trends
│   └── notes_tools.py             # get_clinical_notes_summary
│   └── family_history_tools.py    # get_family_history
├── services/
│   ├── __init__.py
│   ├── ddi_analyzer.py            # DDI reference data analysis
│   ├── patient_context.py         # Patient data formatting
│   └── vitals_trend_analyzer.py   # Statistical trend analysis
└── prompts/
    ├── __init__.py
    └── system_prompts.py          # Centralized system prompts
```

## Implementation Details

### Technology Stack

- **LangChain:** 1.2.0
- **LangGraph:** 1.0.5 (uses ToolNode API)
- **LangChain-OpenAI:** 1.1.6
- **OpenAI:** 2.14.0
- **LLM:** GPT-4-turbo (temperature=0.3 for clinical accuracy)

### Design Patterns

1. **Synchronous Functions:** All functions are synchronous (matching existing `app/db/` pattern)
   - Future consideration: Refactor to async/await for concurrent queries
   - Future consideration: Session-based database access for connection pooling

2. **No Database Sessions:** Tools create their own connections (via `app/db/` functions)
   - Existing pattern uses SQLAlchemy engine directly, not session-based
   - Simplifies tool signatures (no `db_session` parameter needed)

3. **Natural Language Output:** All tools return plain text (not JSON/dicts)
   - Optimized for LLM consumption
   - Human-readable format

4. **Graceful Degradation:** Missing data returns "None on record" messages
   - Never fails due to missing data
   - All sections always present in summaries

## Testing

### Test Scripts

1. **`scripts/test_ddi_tool_with_agent.py`**
   - Tests DDI tool integration with LangGraph agent
   - Verifies ICN extraction from questions
   - Validates agent tool invocation and response synthesis

2. **`scripts/test_patient_summary.py`**
   - Tests PatientContextBuilder individual sections
   - Tests comprehensive patient summary (with clinical notes)
   - Tests missing data handling
   - Tests LangGraph agent integration with get_patient_summary

3. **`scripts/test_vitals_trends_tool.py`** (Phase 3)
   - Tests VitalsTrendAnalyzer statistical analysis
   - Tests linear regression for BP, HR, temperature trends
   - Tests Vista cached response integration
   - Validates concerning trend detection

4. **`scripts/test_notes_tool.py`** (Phase 4)
   - Tests get_clinical_notes_summary with type filtering
   - Tests date range filtering (30/60/90/180 days)
   - Tests note preview truncation (500 chars)
   - Tests LangGraph agent integration for note queries

### Test Results (ICN100010 - Alexander Aminor)

```
✅ Demographics: 60-year-old male veteran, SC 0%, Dayton OH
✅ Medications: 2 active (GABAPENTIN, ALPRAZOLAM)
✅ Vitals: No recent vitals (last 7 days)
✅ Allergies: 2 known allergies
✅ Encounters: 1 recent encounter (Bay Pines, FL)
✅ Clinical Notes: 3 recent notes (Progress Notes, Consults)
✅ DDI Risk: 1 interaction found (GABAPENTIN + ALPRAZOLAM)
✅ Vitals Trends: BP stable, HR normal range (when data available)
```

**Notable Agent Behavior:**
- Agent autonomously selects appropriate tools based on query intent
- Multi-tool synthesis: When asked to "summarize clinical status", agent calls:
  1. `get_patient_summary` (demographics, meds, vitals, allergies, encounters, notes)
  2. `check_ddi_risks` (medication safety analysis)
  3. `analyze_vitals_trends` (statistical trend analysis - when vitals data available)
- Targeted queries: "Show me consult notes" → agent calls `get_clinical_notes_summary` with note_type filter
- Synthesizes coherent multi-section responses from multiple tool outputs

## Usage Examples

### Using Tools Directly

```python
from ai.tools import (
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
    get_clinical_notes_summary
)

# Check DDI risks
ddi_result = check_ddi_risks("ICN100010")
print(ddi_result)
# "Found 1 drug-drug interaction:
#  ⚠️ Gabapentin + Alprazolam
#     The risk or severity of adverse effects..."

# Get patient summary (includes demographics, meds, vitals, allergies, encounters, notes)
summary = get_patient_summary("ICN100010")
print(summary)
# "PATIENT DEMOGRAPHICS
#  60-year-old male veteran...
#
#  CURRENT MEDICATIONS
#  Currently on 2 active medications...
#
#  RECENT CLINICAL NOTES
#  3 notes in the last 90 days..."

# Analyze vitals trends (requires request context for Vista integration)
from ai.tools import set_request_context
set_request_context(request)  # Set request context for session access
trends = analyze_vitals_trends("ICN100010", days=90)
print(trends)
# "Blood pressure shows stable trend over 90 days...
#  Heart rate within normal range..."

# Query clinical notes with filtering
consult_notes = get_clinical_notes_summary(
    patient_icn="ICN100010",
    note_type="Consults",
    days=180,
    limit=5
)
print(consult_notes)
# "Found 2 Consult notes in the last 180 days:
#  1. Cardiology Consult (2025-12-15)..."
```

### Using LangGraph Agent

```python
from ai.agents.insight_agent import create_insight_agent
from ai.tools import ALL_TOOLS
from langchain_core.messages import HumanMessage

# Create agent
agent = create_insight_agent(ALL_TOOLS)

# Invoke with question
result = agent.invoke({
    "messages": [HumanMessage(content="Check DDI risks for patient ICN100010")],
    "patient_icn": "ICN100010",
    "patient_name": "Alexander Aminor",
    "tools_used": [],
    "data_sources": [],
    "error": None
})

# Get response
print(result["messages"][-1].content)
```

## Configuration

Required environment variables (in `.env`):

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.3

# AI Clinical Notes Configuration (Phase 4)
AI_NOTES_PREVIEW_LENGTH=500          # Characters for note previews
AI_NOTES_SUMMARY_LIMIT=3             # Notes in get_patient_summary
AI_NOTES_QUERY_DEFAULT_LIMIT=5       # Notes in get_clinical_notes_summary
AI_NOTES_QUERY_DEFAULT_DAYS=90       # Default lookback period
AI_NOTES_QUERY_MAX_LIMIT=20          # Maximum notes per query
```

Configuration is centralized in `config.py` at project root:

```python
# AI Subsystem Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# AI Clinical Notes Config (Phase 4)
AI_NOTES_PREVIEW_LENGTH = int(os.getenv("AI_NOTES_PREVIEW_LENGTH", "500"))
AI_NOTES_SUMMARY_LIMIT = int(os.getenv("AI_NOTES_SUMMARY_LIMIT", "3"))
AI_NOTES_QUERY_DEFAULT_LIMIT = int(os.getenv("AI_NOTES_QUERY_DEFAULT_LIMIT", "5"))
AI_NOTES_QUERY_DEFAULT_DAYS = int(os.getenv("AI_NOTES_QUERY_DEFAULT_DAYS", "90"))
AI_NOTES_QUERY_MAX_LIMIT = int(os.getenv("AI_NOTES_QUERY_MAX_LIMIT", "20"))
```

## Completed Phases

### Phase 1: Core Tools (Week 1) ✅
- ✅ `check_ddi_risks()` - Drug-drug interaction analysis
- ✅ `get_patient_summary()` - Comprehensive patient overview
- ✅ LangGraph agent with tool binding
- ✅ DDI reference data pipeline (MinIO Parquet)

### Phase 2: Web UI Integration (Week 2) ✅
- ✅ FastAPI routes at `/insight`
- ✅ HTMX-powered chat interface
- ✅ Message partials with streaming responses
- ✅ Sidebar navigation integration
- ✅ CSS styling and 508 compliance

### Phase 3: Vital Trends + Vista Integration (Week 3) ✅
- ✅ `analyze_vitals_trends()` - Statistical trend analysis
- ✅ Linear regression for BP, HR, temperature
- ✅ Vista RPC cached response integration
- ✅ Session-based caching (30-min TTL)

### Phase 4: Clinical Notes Integration (Week 4) ✅
- ✅ `get_clinical_notes_summary()` - Dedicated notes query tool
- ✅ Enhanced `get_patient_summary()` with automatic note inclusion
- ✅ System prompts architecture (`ai/prompts/system_prompts.py`)
- ✅ Note type and date range filtering

### Phase 5: UX Enhancements (Week 5) ✅
- ✅ Conversation transcript download (HTML export)
- ✅ Suggested questions modal refactoring
- ✅ Centralized suggested questions configuration
- ✅ Unified chat button styling

## Planned Enhancements

### Immunizations Integration (Phase 6 - Pending)

Following the successful completion of the Immunizations domain (2026-01-14), three new AI tools are planned:

**New Tools (3):**
1. **`get_immunization_history`** - Query patient vaccine history with CVX codes
   - Retrieve all vaccines patient has received
   - Filter by vaccine group or CVX code
   - Include series status (complete/incomplete)

2. **`check_vaccine_compliance`** - RAG-based CDC ACIP guideline compliance
   - Compare patient history to CDC ACIP schedules
   - Identify missing vaccines based on age and risk factors
   - Support age-specific recommendations (pediatric, adult, geriatric)

3. **`forecast_next_dose`** - Calculate due dates for multi-dose vaccine series
   - Parse series information ("1 of 2", "2 of 3 COMPLETE")
   - Apply vaccine-specific interval rules
   - Return next due date and series completion status

**Enhanced Tool:**
- **`get_patient_summary`** - Add immunizations section
  - Include recent immunizations (last 2 years)
  - Highlight incomplete series
  - Note vaccines with adverse reactions

**Use Cases:**
- "What vaccines has this patient received?"
- "Is this patient due for Shingrix?" (age 65+, 2-dose series)
- "Show me incomplete vaccine series"
- "Has the patient completed their COVID-19 primary series?"
- "Are there any vaccines with adverse reactions?"

**Implementation Notes:**
- Leverage existing `app/db/patient_immunizations.py` database layer
- Use CVX codes for precise vaccine identification
- Estimated effort: 3-4 days (follows pattern from Medications, Vitals, Notes tools)

## Documentation

- **Design Specification:** `docs/spec/ai-insight-design.md` (v2.1)
- **Architecture Decisions:** See Section 2 of design doc
- **Use Cases:** See Section 4 of design doc (DDI Assessment, Patient Summary, Vital Trends, Clinical Notes)
- **Implementation Phases:** See Section 10 of design doc (Phases 1-5 complete)
- **Immunizations Design:** `docs/spec/immunizations-design.md` Section 9 (AI Integration)

## Development Notes

### Adding New Tools

1. Create tool function in `ai/tools/<domain>_tools.py`:
   ```python
   from langchain_core.tools import tool

   @tool
   def my_new_tool(patient_icn: str) -> str:
       """Tool description for LLM."""
       # Implementation
       return "formatted text result"
   ```

2. Create service layer if needed in `ai/services/`:
   ```python
   class MyAnalyzer:
       def analyze(self, data):
           # Business logic
           return formatted_result
   ```

3. Update `ai/tools/__init__.py`:
   ```python
   from ai.tools.my_tools import my_new_tool

   ALL_TOOLS = [
       check_ddi_risks,
       get_patient_summary,
       analyze_vitals_trends,
       get_clinical_notes_summary,
       my_new_tool,  # Add here
   ]
   ```

4. Test with `scripts/test_my_tool.py`

### Code Style

- Use descriptive docstrings (Google style)
- Log important operations at INFO level
- Log errors at ERROR level with stack traces
- Return natural language text from tools (not JSON)
- Handle missing data gracefully
- Include data source attribution in responses

## Support

For questions or issues:
- See design document: `docs/spec/ai-insight-design.md`
- Review architecture decisions in design doc Section 2
- Check test scripts for usage examples

---

**Phases 1-5 Status:** ✅ **COMPLETE**
**Tools Implemented:** 4 (DDI Risk Assessment, Patient Summary, Vitals Trends, Clinical Notes)
**Production Status:** Operational at `/insight`
**Next:** Phase 6 - Immunizations Integration (Pending)
5. **`get_family_history`** - Family History Retrieval Tool (Phase 6)
   - Retrieves structured family-history findings from `clinical.patient_family_history`
   - Supports relationship/category filters and active-only filtering
   - Explicitly highlights first-degree and first-degree high-risk findings
   - Example: "Any first-degree cardiac family history?"
