# AI Clinical Insights Subsystem

**Status:** Phase 1 Week 1 Complete ✅
**Last Updated:** 2025-12-29

## Overview

The AI Clinical Insights subsystem provides an intelligent chatbot interface to help clinicians discover insights about patients through natural language conversation. The system uses Agentic RAG (Retrieval-Augmented Generation) with LangGraph to query existing med-z1 data sources and provide evidence-based responses.

## Current Capabilities (Phase 1 Week 1)

### Available Tools (2)

1. **`check_ddi_risks`** - Drug-Drug Interaction Risk Assessment
   - Analyzes patient medications for potential interactions
   - Uses ~191K interaction database from DrugBank (via Kaggle)
   - Returns natural language summary with interaction descriptions
   - Example: "Found 1 interaction: GABAPENTIN + ALPRAZOLAM"

2. **`get_patient_summary`** - Comprehensive Patient Clinical Summary
   - Synthesizes demographics, medications, vitals, allergies, encounters
   - Returns multi-section natural language overview
   - Covers all 5 clinical domains
   - Handles missing data gracefully ("No ... on record")

### Key Features

- ✅ **LangGraph Agent:** Uses GPT-4-turbo with tool binding (LangGraph 1.0.5 API)
- ✅ **Intelligent Tool Selection:** Agent autonomously decides which tools to invoke
- ✅ **Multi-Tool Synthesis:** Agent can combine multiple tools in a single response
- ✅ **Natural Language Formatting:** All data converted from structured (dicts/lists) to prose
- ✅ **Error Handling:** Graceful degradation when data is missing or unavailable

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
└──────────────────────┬──────────────────────────────────────────┘
                       │ wraps
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ai/services/                                  │
│  • DDIAnalyzer (ddi_analyzer.py)                                │
│  • PatientContextBuilder (patient_context.py)                   │
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
│   ├── __init__.py                # ALL_TOOLS export (2 tools)
│   ├── medication_tools.py        # check_ddi_risks
│   └── patient_tools.py           # get_patient_summary
├── services/
│   ├── __init__.py
│   ├── ddi_analyzer.py            # DDI reference data analysis
│   └── patient_context.py         # Patient data formatting
└── prompts/
    ├── __init__.py
    └── system_prompts.py          # (Future: system prompts)
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
   - Tests comprehensive patient summary
   - Tests missing data handling
   - Tests LangGraph agent integration with get_patient_summary

### Test Results (ICN100010 - Alexander Aminor)

```
✅ Demographics: 60-year-old male veteran, SC 0%, Dayton OH
✅ Medications: 2 active (GABAPENTIN, ALPRAZOLAM)
✅ Vitals: No recent vitals (last 7 days)
✅ Allergies: 2 known allergies
✅ Encounters: 1 recent encounter (Bay Pines, FL)
✅ DDI Risk: 1 interaction found (GABAPENTIN + ALPRAZOLAM)
```

**Notable Agent Behavior:**
- Agent autonomously combined both tools in Test Case 1
- When asked to "summarize clinical status", agent called:
  1. `get_patient_summary` (for demographics, meds, vitals, allergies, encounters)
  2. `check_ddi_risks` (for medication safety analysis)
- Synthesized coherent multi-section response from both tool outputs

## Usage Examples

### Using Tools Directly

```python
from ai.tools import check_ddi_risks, get_patient_summary

# Check DDI risks
ddi_result = check_ddi_risks("ICN100010")
print(ddi_result)
# "Found 1 drug-drug interaction:
#  ⚠️ Gabapentin + Alprazolam
#     The risk or severity of adverse effects..."

# Get patient summary
summary = get_patient_summary("ICN100010")
print(summary)
# "PATIENT DEMOGRAPHICS
#  60-year-old male veteran...
#
#  CURRENT MEDICATIONS
#  Currently on 2 active medications..."
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
```

Configuration is centralized in `config.py` at project root:

```python
# AI Subsystem Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
```

## Next Steps

### Phase 2: Web UI Integration (Week 2)

Planned tasks:
- [ ] Create `app/routes/insight.py` (FastAPI routes)
- [ ] Create `app/templates/insight.html` (chat interface)
- [ ] Create `app/templates/partials/chat_message.html` (message partial)
- [ ] Add CSS styling to `app/static/styles.css`
- [ ] Wire up HTMX chat form
- [ ] Add "Insights" link to sidebar navigation
- [ ] End-to-end testing with multiple patients

### Phase 3: Vital Trends + Polish (Week 3)

Planned tools:
- [ ] `analyze_vitals_trends()` - Statistical trend analysis
  - Linear regression for BP, HR trends
  - Variance analysis
  - Clinical norm comparisons

## Documentation

- **Design Specification:** `docs/spec/ai-insight-design.md` (v1.4)
- **Architecture Decisions:** See Section 2 of design doc
- **Use Cases:** See Section 4 of design doc (DDI Assessment, Patient Summary, Vital Trends)
- **Implementation Phases:** See Section 10 of design doc

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

**Phase 1 Week 1 Status:** ✅ **COMPLETE**
**Tools Implemented:** 2/3 (DDI Risk Assessment, Patient Summary)
**Ready For:** Phase 2 - Web UI Integration
