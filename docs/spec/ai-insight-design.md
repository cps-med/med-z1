# AI Clinical Insights Design Specification

**Document Version:** v1.6
**Created:** 2025-12-28
**Updated:** 2025-12-30 (Phase 3 Week 3 Complete - Vital Trends + Vista Session Caching ✅)
**Status:** Production Ready - Phase 1 MVP Complete (All 3 Weeks ✅)
**Completion Date:** 2025-12-30

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Data Sources](#3-data-sources)
4. [Use Cases (Phase 1 MVP)](#4-use-cases-phase-1-mvp)
5. [LangGraph Agent Design](#5-langgraph-agent-design)
6. [Tool Definitions](#6-tool-definitions)
7. [Service Layer](#7-service-layer)
8. [API Endpoints](#8-api-endpoints)
9. [UI Components](#9-ui-components)
10. [Implementation Phases](#10-implementation-phases)
11. [Testing Strategy](#11-testing-strategy)
12. [Ethical Considerations](#12-ethical-considerations)
13. [Success Criteria](#13-success-criteria)
14. [Future Enhancements](#14-future-enhancements)

---

## 1. Overview

### 1.1 Purpose

The **AI Clinical Insights** feature adds an intelligent chatbot interface to med-z1 that helps clinicians discover insights about patients through natural language conversation. The system uses Agentic RAG (Retrieval-Augmented Generation) to query existing med-z1 data sources and provide evidence-based responses.

### 1.2 Key Capabilities (Phase 1 MVP)

1. **Drug-Drug Interaction (DDI) Risk Assessment**
   - Analyzes patient medications for potential interactions
   - Leverages existing notebook DDI reference data
   - Prioritizes risks by severity

2. **Patient Clinical Summary**
   - Synthesizes demographics, vitals, medications, allergies, encounters
   - Provides natural language overview
   - Highlights key clinical facts

3. **Vital Sign Trend Analysis**
   - Identifies concerning trends in blood pressure, heart rate, temperature
   - Compares against clinical norms
   - Flags abnormal patterns

### 1.3 User Interface

- **New sidebar menu item:** "Insights" (positioned after Procedures, below all clinical domains)
- **Icon:** `fa-regular fa-sparkles` (Font Awesome Pro - sparkle indicates AI-powered feature)
- **Page layout:** Chat-style interface (similar to ChatGPT, Claude)
- **Interaction model:** User types questions, AI responds with sourced answers
- **Technology:** FastAPI + HTMX (consistent with existing med-z1 patterns)

**Note:** Font Awesome Pro is already configured in `app/templates/base.html` via kit link:
```html
<link rel="stylesheet" href="https://kit.fontawesome.com/124182fb50.css" crossorigin="anonymous">
```
This provides access to all Pro icon variants (solid, regular, light, thin, duotone) across the entire application.

### 1.4 Design Principles

✅ **Leverage Existing Infrastructure** - Reuse `app/services/` layer, PostgreSQL, Vista RPC
✅ **Transparency** - Show which data sources were queried
✅ **Clinical Safety** - Always display AI-generated disclaimer
✅ **Consistency** - Follow FastAPI + HTMX patterns from rest of med-z1
✅ **Extensibility** - Easy to add new tools/capabilities later

---

## 2. Architecture Decisions

### 2.1 Agentic RAG with LangGraph

**Decision:** Use LangGraph (from LangChain) to orchestrate an AI agent with access to tools.

**Rationale:**
- **Tool-based architecture** allows querying multiple data sources (PostgreSQL, Vista, DDI reference)
- **Stateful conversation** maintains patient context across multiple messages
- **Transparency** - Can show which tools were invoked for each response
- **Extensibility** - Add new tools without changing core agent logic

**Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────────┐
│                         User (Clinician)                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTMX POST /insight/chat
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Route (/insight/chat)                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Agent (InsightAgent)              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ State: {messages, patient_icn, tools_used}                 │ │
│  └───────────────────────────┬────────────────────────────────┘ │
│                              │                                  │
│      ┌───────────────────────┼────────────────────────┐         │
│      ▼                       ▼                        ▼         │
│   ┌──────┐               ┌──────┐                ┌──────┐       │
│   │Tool 1│               │Tool 2│                │Tool 3│       │
│   │ DDI  │               │Summ. │                │Vitals│       │
│   └──┬───┘               └──┬───┘                └──┬───┘       │
└──────┼──────────────────────┼───────────────────────┼───────────┘
       │                      │                       │
       ▼                      ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              ai/services/ (Business Logic Layer)                │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │DDIAnalyzer    │  │PatientContext│  │VitalsTrend   │          │
│  │(from notebook)│  │Builder       │  │Analyzer      │          │
│  └──────┬────────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼─────────────────┼──────────────────┘
          │                  │                 │
          ▼                  ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│           Existing app/services/ (Data Access Layer)            │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│   │medication_   │  │vitals_       │  │demographics_ │          │
│   │service       │  │service       │  │service       │          │
│   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└──────────┼─────────────────┼─────────────────┼──────────────────┘
           │                 │                 │
           ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Sources                               │
│   ┌─────────────────┐  ┌───────────────┐  ┌───────────────┐     │
│   │PostgreSQL       │  │Vista RPC      │  │MinIO/Parquet  │     │
│   │(T-1, historical)│  │(T-0, realtime)│  │(DDI reference)│     │
│   └─────────────────┘  └───────────────┘  └───────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Layer Strategy

**Decision:** Wrap existing `app/db/` layer rather than creating new data access code.

**Rationale:**
- ✅ Reuses 8 months of existing med-z1 development
- ✅ Single source of truth for data access logic
- ✅ Easier maintenance (one place to update queries)
- ✅ Faster implementation (no duplicate work)

**Pattern:**
```python
# ai/services/patient_context.py wraps existing app/db functions
from app.db.patient import get_patient_demographics
from app.db.medications import get_patient_medications

class PatientContextBuilder:
    def get_medication_summary(self) -> str:
        # Delegate to existing database query function
        meds = get_patient_medications(self.icn, limit=10)
        # Format for LLM consumption (string, not DataFrame)
        return self._format_medications_as_text(meds)
```

**Implementation Note (Synchronous Pattern):**
- ✅ Phase 1 uses synchronous functions (matching existing `app/db/` pattern)
- ✅ `app/db/` functions create their own database connections (no session parameter needed)
- ⏳ Future consideration: Refactor to async/await pattern for better performance with concurrent requests
- ⏳ Future consideration: Session-based database access for connection pooling

### 2.3 LLM Provider

**Phase 1:** OpenAI GPT-4 (or GPT-4-turbo)
**Future:** Support for Anthropic Claude, Azure OpenAI

**Configuration:**
```python
# config.py additions
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))  # Low temp for clinical accuracy
```

### 2.4 Deferred Decisions

**MIMIC Community Care Integration:** Deferred to Phase 2
- Notebook work on MIMIC/PhysioNet stays in research layer
- Production "Insight" page uses PostgreSQL + Vista data only
- Re-evaluate after MVP user testing

**Women's Health Screening:** Deferred to Phase 2
- Requires additional clinical data not yet in med-z1
- Will implement after MVP proves value

### 2.5 Vista Session Caching Architecture

**Challenge:** Browser cookie size limit (4096 bytes) prevented storing full merged datasets in session cookies.

**Solution:** Session-based caching of Vista RPC responses with on-demand merging.

**Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│  User clicks "Refresh from Vista" on Vitals page                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Route: /patient/{icn}/vitals/realtime                  │
│  1. Fetch PG data (T-1, historical)                             │
│  2. Call Vista RPC (T-0, today's data)                          │
│  3. Merge PG + Vista data                                       │
│  4. Store ONLY Vista RPC responses in session (~1-2KB)          │
│  5. Return merged HTML to browser                               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Starlette SessionMiddleware (app/main.py)                      │
│  - Stores session data IN cookie (signed with secret_key)       │
│  - Session size: ~1500 bytes (well under 4096 limit)            │
│  - TTL: 30 minutes                                              │
│  - path="/" (accessible from all routes)                        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Session Cookie Structure:                                      │
│  {                                                              │
│    "vista_cache": {                                             │
│      "ICN100001": {                                             │
│        "vitals": {                                              │
│          "vista_responses": {                                   │
│            "200": "BP^120/80^T^98.6...",  // Raw RPC strings    │
│            "500": "BP^118/78^T^98.2..."                         │
│          },                                                     │
│          "timestamp": "2025-12-30T12:00:00",                    │
│          "sites": ["200", "500"],                               │
│          "stats": {"pg_count": 305, "vista_count": 10}          │
│        }                                                        │
│      }                                                          │
│    }                                                            │
│  }                                                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI Clinical Insights Tool: analyze_vitals_trends()             │
│  1. Check session for cached Vista responses                    │
│  2. If found: Fetch PG data + merge with cached Vista           │
│  3. If not found: Use PG data only                              │
│  4. Analyze merged dataset (315 vitals vs 305 PG-only)          │
│  5. Return analysis with data source attribution                │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Details:**

**Service Layer** (`app/services/vista_cache.py` - 367 lines):
- `VistaSessionCache.set_cached_data()` - Stores Vista RPC responses (NOT merged data)
- `VistaSessionCache.get_cached_data()` - Retrieves cached responses with TTL check
- 30-minute TTL with expiration checking
- Multi-patient, multi-domain support
- Cache size logging for operational visibility

**Middleware Configuration** (`app/main.py`):
```python
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    max_age=SESSION_COOKIE_MAX_AGE,  # 15 minutes
    https_only=False,  # True in production
    same_site="lax",
    path="/"  # CRITICAL: Ensures cookie sent with all requests
)
```

**Session Lifecycle:**
- **Creation**: User clicks "Refresh from Vista" → Vista responses cached
- **Persistence**: Session cookie sent with every request (path="/")
- **Expiration**: 30-minute TTL OR user logout
- **Cleanup**: `request.session.clear()` on logout (both cookies deleted)

**Key Design Decisions:**
1. ✅ **Store RPC responses, not merged data** - Reduces session size from ~40KB to ~1.5KB
2. ✅ **Merge on-demand** - Page loads and AI tools merge PG + cached Vista as needed
3. ✅ **Session cookie, not server-side storage** - Simple, stateless, no Redis/database needed
4. ✅ **Automatic cleanup on logout** - Clears both `session_id` (auth) and `session` (Vista cache) cookies

**Benefits:**
- ✅ AI tools automatically use real-time Vista data when available
- ✅ No separate "Refresh Vista for AI" button needed
- ✅ Transparent to users - cache status shown with green badge
- ✅ Performance: ~1-3 second merge latency (acceptable for AI analysis)
- ✅ Scalability: No server-side session storage required

**Files Modified:**
- `app/services/vista_cache.py` - Cache management service
- `app/routes/vitals.py` - Cache Vista responses, merge on page load
- `ai/services/vitals_trend_analyzer.py` - Use cached Vista data for analysis
- `app/main.py` - SessionMiddleware configuration
- `app/routes/auth.py` - Clear both cookies on logout

---

## 3. Data Sources

### 3.1 Primary Data Sources (Phase 1)

| Data Source | Type | Content | Access Method |
|-------------|------|---------|---------------|
| **PostgreSQL (T-1)** | Relational DB | Demographics, Medications, Vitals, Allergies, Encounters, Labs | `app/services/*_service.py` |
| **Vista RPC (T-0)** | Real-time API | Current-day vitals, medications | `app/services/vista_client.py` |
| **DDI Reference** | Parquet/MinIO | ~191K drug-drug interactions from DrugBank (via Kaggle) | Refactored from `notebook/src/ddi_transforms.py` |

**DDI Reference Data Details:**
- **Source:** Kaggle DrugBank dataset (https://www.kaggle.com/datasets/mghobashy/drug-drug-interactions/data)
- **Original format:** CSV (`db_drug_interactions.csv`)
- **Raw location:** MinIO `med-sandbox` bucket: `kaggle-data/ddi/db_drug_interactions.csv`
- **Processed location:** MinIO `med-z1` bucket (Parquet, medallion architecture: Bronze/Silver/Gold)
- **Schema:** `Drug 1`, `Drug 2`, `Interaction Description` (3 columns)
- **Note:** Phase 1 MVP does not use severity levels. Severity classification may be added in Phase 2 via LLM parsing or separate enrichment.

### 3.2 Data Access Patterns

**PostgreSQL Queries:**
- Reuse existing service layer functions
- No new SQL queries needed for Phase 1
- Tools wrap existing services

**Vista RPC:**
- Use existing `vista_client.py` integration
- Only query on explicit user request (not automatic)
- Show "Fetching real-time data..." indicator

**DDI Reference:**
- Load DDI Parquet file at startup (cached in memory)
- ~191K interactions, ~10MB in memory
- Fast lookups by drug name pair
- Schema: `drug_1`, `drug_2`, `interaction_description` (normalized from Kaggle column names)

### 3.3 Performance Considerations

**Caching Strategy:**
- LLM responses cached for 5 minutes (same patient + same question)
- DDI reference data cached in memory (static dataset)
- PostgreSQL queries use existing indexes

**Response Time Goals:**
- Simple questions (patient summary): < 3 seconds
- Complex questions (DDI analysis): < 5 seconds
- Vista real-time queries: +1-3 seconds (show progress indicator)

---

## 4. Use Cases (Phase 1 MVP)

### 4.1 Use Case 1: DDI Risk Assessment

**User Prompt:**
_"Are there any drug-drug interaction risks for this patient?"_

**Agent Flow:**
1. Parse intent: User wants DDI analysis
2. Invoke tool: `check_ddi_risks(patient_icn)`
3. Tool logic:
   - Get patient medications from PostgreSQL
   - Load DDI reference data
   - Find matching interactions
   - Rank by severity (Major > Moderate > Minor)
4. LLM synthesizes response with findings
5. Return: Natural language summary + list of interactions

**Example Response:**
```
I found 2 drug-drug interactions for this patient:

⚠️ **Warfarin + Ibuprofen**
- Interaction: The risk or severity of bleeding can be increased when Warfarin is combined with Ibuprofen
- Recommendation: Consider alternative to ibuprofen (e.g., acetaminophen) and monitor for bleeding

⚠️ **Lisinopril + Potassium Chloride**
- Interaction: The risk or severity of hyperkalemia can be increased when Lisinopril is combined with Potassium supplements
- Recommendation: Monitor potassium levels regularly

Data sources: PostgreSQL medications (163 records), DDI reference (~191K interactions)

Note: Phase 1 MVP shows all interactions without severity ranking. Severity classification may be added in Phase 2.
```

### 4.2 Use Case 2: Patient Clinical Summary

**User Prompt:**
_"Summarize this patient's current clinical status"_

**Agent Flow:**
1. Parse intent: User wants comprehensive overview
2. Invoke multiple tools in parallel:
   - `get_patient_demographics(patient_icn)`
   - `get_patient_medications(patient_icn)`
   - `get_patient_vitals(patient_icn)`
   - `get_patient_allergies(patient_icn)`
   - `get_recent_encounters(patient_icn)`
3. Tools return formatted text summaries
4. LLM synthesizes coherent narrative
5. Return: Multi-paragraph summary

**Example Response:**
```
**Patient Overview**

Demographics: 72-year-old male veteran, service-connected disability 70%

Active Conditions: Based on recent encounters, patient is being treated for:
- Atrial fibrillation
- Congestive heart failure
- Hypertension

Current Medications: On 8 medications including:
- Warfarin (anticoagulation for AFib)
- Furosemide (diuretic for CHF)
- Metoprolol (beta-blocker for HTN/AFib)

Recent Vitals (last 7 days):
- Blood pressure trending 135/85 (acceptable control)
- Heart rate 68-72 bpm (well-controlled)
- Weight stable at 185 lbs

Allergies: Penicillin (rash)

Recent Activity: Last encounter 14 days ago (cardiology follow-up)

Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters)
```

### 4.3 Use Case 3: Vital Sign Trend Analysis

**User Prompt:**
_"Are there any concerning trends in vital signs?"_

**Agent Flow:**
1. Parse intent: User wants trend analysis
2. Invoke tool: `analyze_vitals_trends(patient_icn)`
3. Tool logic:
   - Get vitals from last 90 days (PostgreSQL)
   - Calculate statistical trends (slope, variance)
   - Compare against clinical norms
   - Flag abnormal patterns
4. LLM interprets findings
5. Return: Trend analysis with recommendations

**Example Response:**
```
**Vital Sign Trend Analysis (Last 90 Days)**

✅ **Blood Pressure**: Stable and well-controlled
- Average: 132/84 mmHg
- Trend: Slight improvement (down 5 mmHg systolic)
- Status: Within target range for patient with HTN

⚠️ **Heart Rate**: Increasing trend noted
- Average: 78 bpm (up from 68 bpm 3 months ago)
- Trend: +10 bpm increase over 90 days
- Recommendation: Consider checking medication adherence (beta-blocker) and thyroid function

✅ **Temperature**: Normal and stable
- Average: 98.2°F
- No febrile episodes

Data sources: PostgreSQL vitals (47 readings over 90 days)
```

---

## 5. LangGraph Agent Design

### 5.1 State Schema

```python
# ai/agents/insight_agent.py

from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class InsightState(TypedDict):
    """State for the clinical insight agent."""

    # Conversation history (managed by LangGraph)
    messages: Annotated[List[BaseMessage], add_messages]

    # Patient context (immutable for conversation)
    patient_icn: str
    patient_name: str

    # Tracking (for transparency and debugging)
    tools_used: List[str]  # e.g., ["check_ddi_risks", "get_patient_vitals"]
    data_sources: List[str]  # e.g., ["PostgreSQL", "Vista RPC"]

    # Error handling
    error: str | None
```

### 5.2 Graph Definition

**Note:** Updated for LangGraph 1.0.5 API (January 2025)

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# Initialize LLM with tool binding
def create_insight_agent(tools: list):
    """
    Creates a LangGraph agent for clinical insights.

    Args:
        tools: List of LangChain tools (check_ddi_risks, get_patient_summary, etc.)

    Returns:
        Compiled LangGraph agent
    """
    # Initialize OpenAI LLM
    llm = ChatOpenAI(
        model="gpt-4-turbo",
        temperature=0.3,  # Low temperature for clinical accuracy
    )

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Define agent node
    def agent_node(state: InsightState) -> dict:
        """LLM decides what to do (call tools or respond)."""
        messages = state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Define router function
    def should_continue(state: InsightState) -> str:
        """Router: continue to tools or end?"""
        last_message = state["messages"][-1]
        # If LLM makes a tool call, route to tools node
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # Otherwise, end the conversation
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
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")  # Loop back to agent after tools

    # Compile and return
    return workflow.compile()

# Example usage:
# from ai.tools.medication_tools import check_ddi_risks
# from ai.tools.patient_tools import get_patient_summary
# from ai.tools.vitals_tools import analyze_vitals_trends
#
# tools = [check_ddi_risks, get_patient_summary, analyze_vitals_trends]
# agent = create_insight_agent(tools)
#
# # Invoke with a question
# initial_state = {
#     "messages": [HumanMessage(content="Are there any DDI risks?")],
#     "patient_icn": "ICN1011530429",
#     "patient_name": "John Doe",
#     "tools_used": [],
#     "data_sources": [],
#     "error": None
# }
# result = agent.invoke(initial_state)
# print(result["messages"][-1].content)
```

**Flow Diagram:**

```
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌──────────────┐
│    Agent     │ (LLM decides: call tools or respond?)
│   (GPT-4)    │
└───┬─────┬────┘
    │     │
    │     └────────────────────────────────┐
    │  (tool calls needed)                 │ (no tools, final response)
    ▼                                      ▼
┌──────────────┐                      ┌──────────┐
│    Tools     │                      │   END    │
│  (Execute)   │                      └──────────┘
└───┬──────────┘
    │
    │ (results added to messages)
    │
    └──────────────────► (loop back to agent)
```

### 5.3 System Prompt

```python
# ai/prompts/system_prompts.py

INSIGHT_SYSTEM_PROMPT = """You are a clinical decision support assistant for VA healthcare providers.

**Your Role:**
- Help clinicians understand patient data through natural language conversation
- Analyze medications, vitals, allergies, encounters, and lab results
- Identify risks like drug-drug interactions and concerning trends
- Provide evidence-based insights with clear data sources

**Available Tools:**
- check_ddi_risks: Analyze drug-drug interactions using reference database
- get_patient_summary: Retrieve comprehensive patient overview
- analyze_vitals_trends: Identify patterns in vital signs over time
- get_patient_medications: List current medications
- get_patient_vitals: Retrieve recent vital sign measurements
- get_patient_allergies: List documented allergies

**Guidelines:**
1. Always cite data sources (e.g., "Based on 47 vital sign readings from PostgreSQL...")
2. Prioritize patient safety - flag risks clearly with ⚠️ symbols
3. Use clinical terminology appropriate for healthcare providers
4. If asked about data you don't have access to, say so clearly
5. Never make diagnostic or treatment decisions - provide decision support only
6. When showing DDI risks, rank by severity (Major > Moderate > Minor)

**Current Patient:** {patient_name} (ICN: {patient_icn})

Respond professionally, concisely, and always show your reasoning."""
```

---

## 6. Tool Definitions

### 6.1 Tool: check_ddi_risks

**Purpose:** Analyze patient medications for drug-drug interactions

**Implementation:**
```python
# ai/tools/medication_tools.py

from langchain_core.tools import tool
from ai.services.ddi_analyzer import DDIAnalyzer
from app.services import medication_service

@tool
async def check_ddi_risks(patient_icn: str, db_session) -> str:
    """
    Analyzes drug-drug interaction risks for the patient.

    Returns a formatted text summary of interactions ranked by severity.
    Data sources: PostgreSQL medications + DDI reference database.
    """
    # Get patient medications from existing service
    medications = await medication_service.get_patient_medications(db_session, patient_icn)

    # Analyze DDIs using refactored notebook code
    analyzer = DDIAnalyzer()
    interactions = analyzer.find_interactions(medications)

    # Format for LLM
    if not interactions:
        return "No drug-drug interactions found for this patient."

    result = f"Found {len(interactions)} drug-drug interactions:\n\n"

    # List all interactions (Phase 1 MVP - no severity ranking)
    for i in interactions:
        result += f"⚠️ {i['drug_a']} + {i['drug_b']}\n"
        result += f"   {i['description']}\n\n"

    result += f"Data sources: {len(medications)} medications from PostgreSQL, ~191K interactions from DDI reference"
    result += f"\n\nNote: All interactions shown. Severity ranking may be added in future phases."

    return result
```

### 6.2 Tool: get_patient_summary

**Purpose:** Comprehensive patient overview combining all clinical domains

**Implementation:**
```python
# ai/tools/patient_tools.py

from langchain_core.tools import tool
from ai.services.patient_context import PatientContextBuilder

@tool
async def get_patient_summary(patient_icn: str, db_session) -> str:
    """
    Retrieves comprehensive patient summary including demographics, medications,
    vitals, allergies, and recent encounters.

    Returns formatted text suitable for LLM synthesis.
    """
    builder = PatientContextBuilder(db_session, patient_icn)

    # Gather all data (parallel if possible)
    demographics = await builder.get_demographics_summary()
    medications = await builder.get_medication_summary()
    vitals = await builder.get_vitals_summary()
    allergies = await builder.get_allergies_summary()
    encounters = await builder.get_encounters_summary()

    summary = f"""
PATIENT DEMOGRAPHICS:
{demographics}

CURRENT MEDICATIONS ({medications['count']} active):
{medications['text']}

RECENT VITALS (last 7 days):
{vitals}

ALLERGIES:
{allergies}

RECENT ENCOUNTERS (last 90 days):
{encounters}

Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters)
"""

    return summary.strip()
```

### 6.3 Tool: analyze_vitals_trends

**Purpose:** Statistical analysis of vital sign trends over time

**Implementation:**
```python
# ai/tools/vitals_tools.py

from langchain_core.tools import tool
from ai.services.vitals_trend_analyzer import VitalsTrendAnalyzer

@tool
async def analyze_vitals_trends(patient_icn: str, db_session, days: int = 90) -> str:
    """
    Analyzes vital sign trends over the specified time period.

    Identifies concerning patterns (increasing BP, tachycardia, etc.).
    Returns formatted trend analysis with clinical interpretation.
    """
    analyzer = VitalsTrendAnalyzer(db_session, patient_icn)

    # Get vitals from last N days
    trends = await analyzer.analyze_trends(days=days)

    result = f"VITAL SIGN TREND ANALYSIS (Last {days} Days)\n"
    result += f"Based on {trends['total_readings']} readings:\n\n"

    # Blood pressure
    if trends['bp']['status'] == 'concerning':
        result += f"⚠️ BLOOD PRESSURE: {trends['bp']['interpretation']}\n"
    else:
        result += f"✅ BLOOD PRESSURE: {trends['bp']['interpretation']}\n"
    result += f"   Average: {trends['bp']['avg_systolic']}/{trends['bp']['avg_diastolic']} mmHg\n"
    result += f"   Trend: {trends['bp']['trend_description']}\n\n"

    # Heart rate
    if trends['hr']['status'] == 'concerning':
        result += f"⚠️ HEART RATE: {trends['hr']['interpretation']}\n"
    else:
        result += f"✅ HEART RATE: {trends['hr']['interpretation']}\n"
    result += f"   Average: {trends['hr']['avg']} bpm\n"
    result += f"   Trend: {trends['hr']['trend_description']}\n\n"

    # Temperature (if available)
    if trends.get('temp'):
        result += f"✅ TEMPERATURE: {trends['temp']['interpretation']}\n"
        result += f"   Average: {trends['temp']['avg']}°F\n\n"

    result += f"Data source: PostgreSQL vitals table ({trends['total_readings']} readings)"

    return result
```

### 6.4 Additional Tools (Simpler wrappers)

```python
@tool
async def get_patient_medications(patient_icn: str, db_session) -> str:
    """Lists all current medications for the patient."""
    # Wrap medication_service.get_patient_medications()
    ...

@tool
async def get_patient_vitals(patient_icn: str, db_session) -> str:
    """Retrieves recent vital sign measurements."""
    # Wrap vitals_service.get_patient_vitals()
    ...

@tool
async def get_patient_allergies(patient_icn: str, db_session) -> str:
    """Lists documented allergies."""
    # Wrap allergies_service.get_patient_allergies()
    ...
```

---

## 7. Service Layer

### 7.1 DDIAnalyzer (Refactored from Notebooks)

```python
# ai/services/ddi_analyzer.py

import pandas as pd
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class DDIAnalyzer:
    """
    Drug-drug interaction analyzer.
    Refactored from notebook/src/ddi_transforms.py
    """

    def __init__(self):
        """Load DDI reference data at initialization (cached)."""
        self.ddi_data = self._load_ddi_reference()
        logger.info(f"Loaded {len(self.ddi_data):,} DDI reference records")

    def _load_ddi_reference(self) -> pd.DataFrame:
        """Load DDI Parquet from MinIO (cached in memory)."""
        # Use existing MinIO client from config
        from app.services.minio_client import get_ddi_reference
        return get_ddi_reference()  # Returns DataFrame

    def find_interactions(self, medications: List[Dict]) -> List[Dict]:
        """
        Find drug-drug interactions for a medication list.

        Args:
            medications: List of med dicts with 'drug_name' key

        Returns:
            List of interaction dicts with severity, description
        """
        drug_names = [med['drug_name'] for med in medications]
        interactions = []

        # Check all pairs
        for i, drug_a in enumerate(drug_names):
            for drug_b in drug_names[i+1:]:
                interaction = self._check_pair(drug_a, drug_b)
                if interaction:
                    interactions.append(interaction)

        # Phase 1 MVP: Return interactions without severity sorting
        # Future enhancement: Add severity classification via LLM or rule-based logic
        return interactions

    def _check_pair(self, drug_a: str, drug_b: str) -> Dict | None:
        """Check if two drugs interact."""
        # Normalize drug names (case-insensitive, remove doses)
        drug_a_clean = self._normalize_drug_name(drug_a)
        drug_b_clean = self._normalize_drug_name(drug_b)

        # Query DDI reference data
        # Note: Column names normalized from Kaggle "Drug 1", "Drug 2", "Interaction Description"
        match = self.ddi_data[
            ((self.ddi_data['drug_1'] == drug_a_clean) &
             (self.ddi_data['drug_2'] == drug_b_clean)) |
            ((self.ddi_data['drug_1'] == drug_b_clean) &
             (self.ddi_data['drug_2'] == drug_a_clean))
        ]

        if not match.empty:
            row = match.iloc[0]
            return {
                'drug_a': drug_a,
                'drug_b': drug_b,
                'description': row['interaction_description']
            }

        return None

    def _normalize_drug_name(self, drug: str) -> str:
        """Normalize drug name for matching."""
        # Remove dosages, lowercase, strip whitespace
        import re
        # Remove patterns like "100MG", "10ML", etc.
        clean = re.sub(r'\d+\s*(MG|ML|MCG|G|%)', '', drug, flags=re.IGNORECASE)
        return clean.strip().lower()
```

### 7.2 PatientContextBuilder

```python
# ai/services/patient_context.py

from app.services import (
    medication_service,
    vitals_service,
    demographics_service,
    allergies_service,
    encounters_service
)
from typing import Dict

class PatientContextBuilder:
    """
    Builds LLM-friendly context from existing med-z1 services.
    Wraps existing data access layer without duplicating logic.
    """

    def __init__(self, db_session, patient_icn: str):
        self.db = db_session
        self.icn = patient_icn

    async def get_demographics_summary(self) -> str:
        """Returns demographics as natural language text."""
        demo = await demographics_service.get_patient_demographics(self.db, self.icn)

        age = demo['age']
        gender = demo['gender']
        sc_pct = demo.get('service_connected_percent')

        text = f"{age}-year-old {gender.lower()} veteran"
        if sc_pct:
            text += f", service-connected disability {sc_pct}%"

        return text

    async def get_medication_summary(self) -> Dict:
        """Returns medication list formatted for LLM."""
        meds = await medication_service.get_patient_medications(self.db, self.icn)

        count = len(meds)
        text = ""
        for med in meds[:10]:  # Limit to 10 most recent for brevity
            text += f"- {med['drug_name']} {med['dosage']}, started {med['start_date']}\n"

        if count > 10:
            text += f"... and {count - 10} more medications\n"

        return {'count': count, 'text': text}

    async def get_vitals_summary(self) -> str:
        """Returns recent vitals formatted for LLM."""
        vitals = await vitals_service.get_recent_vitals(self.db, self.icn, days=7)

        if not vitals:
            return "No recent vitals recorded"

        # Latest reading
        latest = vitals[0]
        text = f"Most recent ({latest['taken_date']}):\n"
        text += f"- BP: {latest['systolic']}/{latest['diastolic']} mmHg\n"
        text += f"- HR: {latest['pulse']} bpm\n"
        text += f"- Temp: {latest['temperature']}°F\n"

        return text

    async def get_allergies_summary(self) -> str:
        """Returns allergies formatted for LLM."""
        allergies = await allergies_service.get_patient_allergies(self.db, self.icn)

        if not allergies:
            return "No known allergies"

        text = ""
        for allergy in allergies:
            text += f"- {allergy['allergen']}"
            if allergy.get('reaction'):
                text += f" ({allergy['reaction']})"
            text += "\n"

        return text

    async def get_encounters_summary(self) -> str:
        """Returns recent encounters formatted for LLM."""
        encounters = await encounters_service.get_recent_encounters(self.db, self.icn, limit=5)

        if not encounters:
            return "No recent encounters"

        text = f"{len(encounters)} encounters in last 90 days:\n"
        for enc in encounters[:3]:  # Show top 3
            text += f"- {enc['encounter_type']} on {enc['admit_date']}"
            if enc.get('primary_diagnosis'):
                text += f" ({enc['primary_diagnosis']})"
            text += "\n"

        return text
```

### 7.3 VitalsTrendAnalyzer

```python
# ai/services/vitals_trend_analyzer.py

import numpy as np
from typing import Dict
from app.services import vitals_service

class VitalsTrendAnalyzer:
    """Analyzes vital sign trends over time."""

    def __init__(self, db_session, patient_icn: str):
        self.db = db_session
        self.icn = patient_icn

    async def analyze_trends(self, days: int = 90) -> Dict:
        """
        Analyze vital sign trends over specified period.

        Returns dict with trend analysis for each vital sign.
        """
        vitals = await vitals_service.get_vitals_range(self.db, self.icn, days=days)

        if not vitals:
            return {'error': 'No vitals data available'}

        # Convert to numpy arrays for analysis
        systolic = np.array([v['systolic'] for v in vitals if v.get('systolic')])
        diastolic = np.array([v['diastolic'] for v in vitals if v.get('diastolic')])
        pulse = np.array([v['pulse'] for v in vitals if v.get('pulse')])

        return {
            'total_readings': len(vitals),
            'bp': self._analyze_bp(systolic, diastolic),
            'hr': self._analyze_hr(pulse),
            'temp': self._analyze_temp([v.get('temperature') for v in vitals])
        }

    def _analyze_bp(self, systolic, diastolic) -> Dict:
        """Analyze blood pressure trends."""
        avg_sys = np.mean(systolic)
        avg_dia = np.mean(diastolic)

        # Linear regression for trend
        x = np.arange(len(systolic))
        slope_sys = np.polyfit(x, systolic, 1)[0] if len(systolic) > 1 else 0

        # Interpret trend
        if slope_sys > 2:
            trend = "Increasing (concerning)"
            status = "concerning"
        elif slope_sys < -2:
            trend = "Decreasing (improving)"
            status = "normal"
        else:
            trend = "Stable"
            status = "normal"

        # Check against norms
        if avg_sys > 140 or avg_dia > 90:
            interpretation = f"Elevated (avg {avg_sys:.0f}/{avg_dia:.0f}). Consider medication adjustment."
            status = "concerning"
        else:
            interpretation = f"Well-controlled (avg {avg_sys:.0f}/{avg_dia:.0f})"

        return {
            'avg_systolic': f"{avg_sys:.0f}",
            'avg_diastolic': f"{avg_dia:.0f}",
            'trend_description': trend,
            'interpretation': interpretation,
            'status': status
        }

    def _analyze_hr(self, pulse) -> Dict:
        """Analyze heart rate trends."""
        avg_hr = np.mean(pulse)

        x = np.arange(len(pulse))
        slope = np.polyfit(x, pulse, 1)[0] if len(pulse) > 1 else 0

        if slope > 0.5:
            trend = f"Increasing (up ~{slope * len(pulse):.0f} bpm over period)"
            status = "concerning"
        elif slope < -0.5:
            trend = "Decreasing (improving)"
            status = "normal"
        else:
            trend = "Stable"
            status = "normal"

        # Check norms
        if avg_hr > 100:
            interpretation = "Tachycardic. Consider causes (pain, anxiety, meds, thyroid)."
            status = "concerning"
        elif avg_hr < 50:
            interpretation = "Bradycardic. Verify beta-blocker dose if applicable."
            status = "concerning"
        else:
            interpretation = "Normal sinus rhythm"

        return {
            'avg': f"{avg_hr:.0f}",
            'trend_description': trend,
            'interpretation': interpretation,
            'status': status
        }

    def _analyze_temp(self, temps) -> Dict:
        """Analyze temperature trends."""
        temps_clean = [t for t in temps if t is not None]
        if not temps_clean:
            return None

        avg_temp = np.mean(temps_clean)

        if avg_temp > 100.4:
            interpretation = "Febrile episodes detected"
            status = "concerning"
        else:
            interpretation = "Afebrile, stable"
            status = "normal"

        return {
            'avg': f"{avg_temp:.1f}",
            'interpretation': interpretation,
            'status': status
        }
```

---

## 8. API Endpoints

### 8.1 GET /insight/{icn}

**Purpose:** Render the main Insight page

**Route:**
```python
# app/routes/insight.py

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import demographics_service

router = APIRouter(prefix="/insight", tags=["AI Insight"])

@router.get("/{icn}", response_class=HTMLResponse)
async def insight_page(
    request: Request,
    icn: str,
    db: Session = Depends(get_db)
):
    """Render the AI Clinical Insights page."""

    # Get patient info for header
    patient = await demographics_service.get_patient_demographics(db, icn)

    if not patient:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Patient not found"
        })

    return templates.TemplateResponse("insight.html", {
        "request": request,
        "active_page": "insight",
        "patient": patient
    })
```

### 8.2 POST /insight/chat

**Purpose:** Handle chat messages via HTMX

**Route:**
```python
# app/routes/insight.py (continued)

from fastapi import Form
from ai.agents.insight_agent import InsightAgent
import logging

logger = logging.getLogger(__name__)

@router.post("/chat", response_class=HTMLResponse)
async def chat_endpoint(
    request: Request,
    patient_icn: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Handle chat message from user.
    Returns HTMX-compatible HTML fragment.
    """

    try:
        # Get patient name for context
        patient = await demographics_service.get_patient_demographics(db, patient_icn)

        # Initialize agent
        agent = InsightAgent(
            db_session=db,
            patient_icn=patient_icn,
            patient_name=patient['name']
        )

        # Invoke agent
        response = await agent.invoke(message)

        # Return AI message as HTML fragment
        return templates.TemplateResponse("partials/chat_message.html", {
            "request": request,
            "sender": "ai",
            "message": response['output'],
            "tools_used": response.get('tools_used', []),
            "timestamp": response.get('timestamp')
        })

    except Exception as e:
        logger.error(f"Chat error for patient {patient_icn}: {e}", exc_info=True)

        # Return error message as chat bubble
        return templates.TemplateResponse("partials/chat_message.html", {
            "request": request,
            "sender": "system",
            "message": "An error occurred processing your request. Please try again.",
            "error": True
        })
```

### 8.3 POST /insight/clear

**Purpose:** Clear chat history (optional, for user control)

```python
@router.post("/clear", response_class=HTMLResponse)
async def clear_chat(
    request: Request,
    patient_icn: str = Form(...)
):
    """Clear chat history for this patient session."""

    # Clear agent memory/cache for this patient
    # (Implementation depends on caching strategy)

    return templates.TemplateResponse("partials/chat_cleared.html", {
        "request": request
    })
```

---

## 9. UI Components

### 9.1 Main Page Template

```html
<!-- app/templates/insight.html -->
{% extends "base.html" %}

{% block content %}
<div class="page-container">
    <!-- Patient header (reuse existing partial) -->
    {% include "partials/patient_header.html" %}

    <!-- Page header -->
    <div class="page-header">
        <div class="page-header__title-group">
            <h1 class="page-header__title">
                <i class="fa-regular fa-sparkles"></i>
                Clinical Insights
            </h1>
            <p class="page-header__subtitle">AI-assisted analysis for {{ patient.name }}</p>
        </div>
    </div>

    <!-- Chat container -->
    <div class="insight-container">

        <!-- Suggested questions (initially visible, hide after first message) -->
        <div id="suggested-questions" class="suggested-questions">
            <h3>Try asking:</h3>
            <div class="suggestion-chips">
                <button class="chip" onclick="askQuestion('Are there any drug-drug interaction risks?')">
                    <i class="fa-solid fa-pills"></i>
                    DDI Risks
                </button>
                <button class="chip" onclick="askQuestion('Summarize this patient\'s current clinical status')">
                    <i class="fa-solid fa-file-medical"></i>
                    Patient Summary
                </button>
                <button class="chip" onclick="askQuestion('Are there any concerning trends in vital signs?')">
                    <i class="fa-solid fa-heart-pulse"></i>
                    Vital Trends
                </button>
            </div>
        </div>

        <!-- Chat history -->
        <div id="chat-history" class="chat-history">
            <!-- Messages will be appended here via HTMX -->
        </div>

        <!-- Input form -->
        <form
            id="chat-form"
            hx-post="/insight/chat"
            hx-target="#chat-history"
            hx-swap="beforeend"
            hx-on::after-request="this.reset(); hideSuggestions();"
            hx-indicator="#loading-indicator"
        >
            <input type="hidden" name="patient_icn" value="{{ patient.icn }}">

            <div class="chat-input-container">
                <textarea
                    name="message"
                    id="message-input"
                    placeholder="Ask about DDI risks, screening gaps, vital trends..."
                    rows="2"
                    required
                    onkeydown="if(event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); this.form.requestSubmit(); }"
                ></textarea>

                <button type="submit" class="btn btn--primary btn--icon">
                    <i class="fa-solid fa-paper-plane"></i>
                </button>
            </div>

            <!-- Loading indicator -->
            <div id="loading-indicator" class="htmx-indicator">
                <i class="fa-solid fa-circle-notch fa-spin"></i>
                Analyzing...
            </div>
        </form>

        <!-- AI Disclaimer -->
        <div class="ai-disclaimer">
            <i class="fa-solid fa-info-circle"></i>
            <strong>AI-generated insights.</strong> Always verify clinically before making decisions.
            This tool provides decision support, not medical advice.
        </div>

    </div>
</div>

<script>
function askQuestion(question) {
    document.getElementById('message-input').value = question;
    document.getElementById('chat-form').requestSubmit();
}

function hideSuggestions() {
    document.getElementById('suggested-questions').style.display = 'none';
}
</script>

{% endblock %}
```

### 9.2 Chat Message Partial

```html
<!-- app/templates/partials/chat_message.html -->

{% if sender == "user" %}
    <!-- User message -->
    <div class="chat-message chat-message--user">
        <div class="chat-message__avatar">
            <i class="fa-solid fa-user"></i>
        </div>
        <div class="chat-message__content">
            <div class="chat-message__text">{{ message }}</div>
            {% if timestamp %}
            <div class="chat-message__timestamp">{{ timestamp }}</div>
            {% endif %}
        </div>
    </div>

{% elif sender == "ai" %}
    <!-- AI message -->
    <div class="chat-message chat-message--ai">
        <div class="chat-message__avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="chat-message__content">
            <div class="chat-message__text">{{ message | safe }}</div>

            {% if tools_used %}
            <div class="chat-message__metadata">
                <i class="fa-solid fa-wrench"></i>
                <span>Tools used: {{ tools_used | join(', ') }}</span>
            </div>
            {% endif %}

            {% if timestamp %}
            <div class="chat-message__timestamp">{{ timestamp }}</div>
            {% endif %}
        </div>
    </div>

{% elif sender == "system" %}
    <!-- System message (errors, etc.) -->
    <div class="chat-message chat-message--system {% if error %}chat-message--error{% endif %}">
        <div class="chat-message__content">
            <i class="fa-solid fa-exclamation-triangle"></i>
            {{ message }}
        </div>
    </div>

{% endif %}
```

### 9.3 CSS Styling

```css
/* app/static/styles.css additions */

/* ===== Insight Page Styles ===== */

.insight-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Suggested questions */
.suggested-questions {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.5rem;
    text-align: center;
}

.suggested-questions h3 {
    margin-bottom: 1rem;
    font-size: 0.95rem;
    color: #6b7280;
    font-weight: 500;
}

.suggestion-chips {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    justify-content: center;
}

.chip {
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 20px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
}

.chip:hover {
    background: linear-gradient(135deg, #06b6d4, #4f46e5);
    color: white;
    border-color: transparent;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

/* Chat history */
.chat-history {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    min-height: 400px;
    max-height: 600px;
    overflow-y: auto;
    padding: 1rem;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
}

.chat-history:empty::before {
    content: "Ask a question to get started";
    display: block;
    text-align: center;
    color: #9ca3af;
    padding: 3rem;
    font-style: italic;
}

/* Chat messages */
.chat-message {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
}

.chat-message--user {
    flex-direction: row-reverse;
}

.chat-message__avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #06b6d4, #4f46e5);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.chat-message--user .chat-message__avatar {
    background: #6b7280;
}

.chat-message__content {
    flex: 1;
    max-width: 75%;
}

.chat-message__text {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1rem;
    font-size: 0.95rem;
    line-height: 1.6;
    white-space: pre-wrap;
}

.chat-message--user .chat-message__text {
    background: linear-gradient(135deg, #06b6d4, #4f46e5);
    color: white;
    border-color: transparent;
}

.chat-message--system .chat-message__text {
    background: #fef3c7;
    border-color: #fbbf24;
    color: #92400e;
}

.chat-message--error .chat-message__text {
    background: #fee2e2;
    border-color: #ef4444;
    color: #991b1b;
}

.chat-message__metadata {
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

.chat-message__timestamp {
    margin-top: 0.35rem;
    font-size: 0.75rem;
    color: #9ca3af;
}

/* Input form */
.chat-input-container {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
}

.chat-input-container textarea {
    flex: 1;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 0.75rem;
    font-size: 0.95rem;
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
}

.chat-input-container textarea:focus {
    outline: none;
    border-color: #06b6d4;
    box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1);
}

.btn--icon {
    width: 48px;
    height: 48px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Loading indicator */
#loading-indicator {
    display: none;
    text-align: center;
    color: #6b7280;
    font-size: 0.9rem;
    padding: 0.5rem;
}

#loading-indicator.htmx-request {
    display: block;
}

/* AI Disclaimer */
.ai-disclaimer {
    background: #fef3c7;
    border: 1px solid #fbbf24;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    font-size: 0.85rem;
    color: #92400e;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.ai-disclaimer i {
    color: #f59e0b;
}

/* Responsive */
@media (max-width: 768px) {
    .insight-container {
        padding: 1rem;
    }

    .chat-message__content {
        max-width: 85%;
    }

    .suggestion-chips {
        flex-direction: column;
    }

    .chip {
        width: 100%;
        justify-content: center;
    }
}
```

### 9.4 Sidebar Integration

**Positioning:** Place "Insights" after Procedures (at the bottom of clinical domains) to distinguish it as a meta-layer that synthesizes across all clinical data rather than being another domain-specific view.

```html
<!-- app/templates/base.html - Add to sidebar navigation -->

<!-- After Procedures (below all clinical domains) -->
<a href="/insight"
   class="sidebar__link {{ 'sidebar__link--active' if active_page == 'insight' else '' }}"
   data-tooltip="AI Clinical Insights">
    <i class="fa-regular fa-sparkles fa-lg"></i>
    <span class="sidebar__text">Insights</span>
</a>
```

**Icon Choice:** `fa-regular fa-sparkles` (Font Awesome Pro)
- Sparkles universally indicate "AI-powered" or "smart" features
- Regular weight provides elegant balance (not too heavy, not too light)
- Already available via existing Font Awesome Pro kit in base.html

---

## 10. Implementation Phases

### Phase 1: MVP Foundation (Week 1) ✅ **COMPLETE**

**Days 1-2: Infrastructure Setup** ✅ **COMPLETE**
- [x] Install dependencies: `langchain`, `langgraph`, `langchain-openai`, `openai`
- [x] Create `ai/` directory structure (including empty `__init__.py` files)
- [x] Add OpenAI API key to `.env`
- [x] Update root `config.py` to add OpenAI configuration variables
- [x] Create basic LangGraph agent skeleton (using 1.0.5 API with ToolNode)
- [x] Test LangGraph agent with simple echo tool

**Days 3-4: DDI Tool Implementation** ✅ **COMPLETE**
- [x] Refactor `notebook/src/ddi_transforms.py` → `ai/services/ddi_analyzer.py`
- [x] Create DDI reference data loader (MinIO → cached DataFrame)
- [x] Implement `check_ddi_risks()` tool
- [x] Unit test DDI analyzer with sample medications
- [x] Test DDI tool integration with LangGraph agent
- [x] **Task 5 (Optional):** LangGraph agent integration testing complete

**Day 5: Patient Summary Tool** ✅ **COMPLETE**
- [x] Create `ai/services/patient_context.py`
- [x] Implement `get_patient_summary()` tool
- [x] Wrap existing services (demographics, meds, vitals, allergies, encounters)
- [x] Test patient summary output formatting
- [x] Verify LangGraph agent can invoke tool and synthesize responses

**Implementation Notes (Days 3-4):**
- ✅ Created ETL pipeline (Bronze/Silver/Gold) for DDI reference data (~191K interactions)
- ✅ Implemented DDIAnalyzer with drug name normalization (handles dosage patterns: MG, ML, MCG, MEQ, G, %, UNITS)
- ✅ Supports multiple medication schema fields (drug_name, drug_name_national, drug_name_local, generic_name)
- ✅ Implemented in-memory caching for DDI reference (~52MB, fast lookups)
- ✅ Integrated with LangGraph agent - successful end-to-end testing with real patient data
- ✅ Test results: Found GABAPENTIN + ALPRAZOLAM interaction for patient ICN100010

**Implementation Notes (Day 5):**
- ✅ Created PatientContextBuilder service (~330 lines) wrapping app/db query functions
- ✅ Implemented natural language formatting for all 5 clinical domains:
  - Demographics: Age, gender, SC%, primary care station, address
  - Medications: Drug names, sig, start dates (max 10 shown)
  - Vitals: Latest BP, HR, temp, weight, height (last 7 days)
  - Allergies: Allergen names, reactions, severity
  - Encounters: Recent visits with dates and locations (last 90 days, max 5)
- ✅ Missing data handled gracefully ("No ... on record" messages)
- ✅ Implemented get_patient_summary() LangChain tool
- ✅ Updated ai/tools/__init__.py to export new tool (ALL_TOOLS now has 2 tools)
- ✅ Test results: Agent autonomously combines multiple tools (e.g., calls both get_patient_summary AND check_ddi_risks for comprehensive clinical status)

**Data Quality Enhancement (2025-12-29):** ✅ **COMPLETE**
Following Phase 1 Week 1 completion, data quality improvements were implemented across the full medallion pipeline to enhance AI tool outputs:

**Medications Domain Enrichment:**
- ✅ Extended Bronze extraction to include RxOut.RxOutpatSig table (20 sig records extracted)
- ✅ Enhanced Silver transformation to join sig data (matched 20/111 prescriptions = 18% coverage)
- ✅ Updated Gold layer to include sig, sig_route, sig_schedule fields in final output
- ✅ Modified PostgreSQL schema to add sig columns (TEXT, VARCHAR(50), VARCHAR(50))
- ✅ Updated load_medications.py to include sig fields in database load
- ✅ Enhanced app/db/medications.py to SELECT and return sig data to AI tools
- ✅ Result: PatientContextBuilder now displays: "GABAPENTIN (TAKE 1 TABLET BY MOUTH TWICE A DAY WITH MEALS)"

**Allergies Domain Enrichment:**
- ✅ Verified existing pipeline already includes full allergen enrichment via Dim.Allergen join
- ✅ Confirmed 100% coverage of standardized allergen names in Gold layer
- ✅ Added allergen_name alias in app/db/patient_allergies.py for PatientContextBuilder compatibility
- ✅ Result: Allergies now display: "PENICILLIN", "MORPHINE" instead of "Unknown allergen"

**Encounters Domain Bug Fix:**
- ✅ Fixed field mapping in ai/services/patient_context.py (get_encounters_summary)
- ✅ Changed from incorrect fields (encounter_type, admit_date) to correct PostgreSQL schema fields (admission_category, admit_datetime)
- ✅ Result: Encounters now display: "Observation on 2025-11-30" instead of "Unknown encounter type on unknown date"

**Data Sources Enhanced:**
- Bronze: 6 medication tables (added RxOutpatSig), 4 allergy tables, existing encounters
- Silver: Enriched joins for sig data and allergen standardization
- Gold: Final curated output with all enriched fields
- PostgreSQL: Updated schemas and query layers to expose enriched data

**AI Tool Impact:**
- PatientContextBuilder now provides clinically rich, actionable data to LLM
- DDI analyzer benefits from improved medication data quality
- Web UI automatically displays enriched data (medications widget, allergies widget, full pages)
- Test coverage: 4 patients (ICN100001, ICN100002, ICN100009, ICN100010) with enriched data

**Success Criteria:**
- ✅ LangGraph agent responds to basic questions
- ✅ DDI analysis returns correct interactions for test patient (ICN100010: 1 interaction found)
- ✅ Patient summary includes all 5 clinical domains (Demographics, Medications, Vitals, Allergies, Encounters)
- ✅ Agent intelligently combines tools when appropriate (observed in Test Case 1)

### Phase 2: Web UI Integration (Week 2) ✅ **COMPLETE**

**Days 1-2: FastAPI Routes + Templates** ✅ **COMPLETE**
- [x] Create `app/routes/insight.py`
- [x] Implement `GET /insight/{icn}` route
- [x] Implement `POST /insight/chat` route
- [x] Create `app/templates/insight.html`
- [x] Create `app/templates/partials/chat_message.html`
- [x] Add CSS styling to `app/static/styles.css`

**Days 3-4: HTMX Integration + UX Polish** ✅ **COMPLETE**
- [x] Wire up HTMX chat form
- [x] Test message submission and response display
- [x] Add loading indicators
- [x] Implement suggested questions chips
- [x] Add "tools used" transparency display
- [x] Test chat conversation flow

**Day 5: Sidebar Integration + Testing** ✅ **COMPLETE**
- [x] Add "Insights" link to sidebar navigation
- [x] Test page navigation from sidebar
- [x] End-to-end testing with multiple patients
- [x] Performance testing (response times)
- [x] Bug fixes and refinement

**Implementation Notes:**

**Backend Routes (app/routes/insight.py - 221 lines):**
- ✅ GET `/insight` - Redirects to current patient from CCOW context
- ✅ GET `/insight/{icn}` - Main Insights page with patient context
- ✅ POST `/insight/chat` - Handles AI chat interactions with LangGraph agent
- ✅ SystemMessage injection: Provides patient context (name + ICN) to LLM at conversation start
- ✅ Markdown-to-HTML conversion: Using `markdown` library with fenced_code, tables, nl2br extensions
- ✅ Tools transparency: Extracts and displays tool names used in agent execution
- ✅ Error handling: Graceful fallbacks for patient not found, agent errors

**Templates:**
- ✅ `app/templates/insight.html` (145 lines): Minimal, left-justified layout
  - Breadcrumb navigation (Dashboard → AI Insights)
  - Suggested questions section with 4 default prompts
  - Chat history container (HTMX target)
  - Message input form (full-width textarea + send button)
  - Loading indicator (spinner + "Analyzing..." text)
  - AI disclaimer (subtle top border, gray text)
- ✅ `app/templates/partials/chat_message.html` (43 lines): Reusable message bubbles
  - User messages: right-aligned, gray avatar, gradient background
  - AI messages: left-aligned, robot avatar, white background with markdown formatting
  - System/error messages: yellow/red backgrounds
  - Tools used display: "Sources checked: tool1, tool2..."
  - Timestamps: "Just now"

**Styling (app/static/styles.css - ~240 lines added):**
- ✅ Minimal design philosophy: No heavy container boxes, clean spacing
- ✅ Responsive suggested question chips:
  - `flex: 1 1 calc(25% - 0.4rem)` - expand/contract with sidebar state
  - Natural text wrapping (2-3 lines if needed)
  - Gray background with simple hover effect
  - Escaped apostrophes in onclick handlers (`replace("'", "\\'")`)
- ✅ Full-width input container (textarea + button flex layout)
- ✅ Comprehensive markdown formatting:
  - Headings (h1/h2/h3) with proper sizing
  - Bold/italic text
  - Lists (ul/ol) with indentation
  - Code blocks with gray background
  - Tables with borders
  - Blockquotes with left border
- ✅ Chat message styling:
  - User bubbles: gradient background, right-aligned
  - AI bubbles: white background, left-aligned, markdown-formatted content
  - Avatar icons: circular, gradient (AI) or gray (user)
  - Metadata display for tools used

**Integration:**
- ✅ Registered `insight.page_router` in `app/main.py`
- ✅ Added "Insights" link to sidebar navigation in `app/templates/base.html`
  - Icon: `fa-regular fa-sparkles`
  - Position: After Procedures (bottom of clinical domains)
  - Active state highlighting when `active_page == 'insight'`
- ✅ Uses LangGraph agent from Phase 1 (singleton pattern, initialized on app startup)
- ✅ Patient data queried via `app/db/patient.py::get_patient_demographics()`

**Dependencies Added:**
- ✅ `markdown==3.10` - for rendering AI markdown responses as HTML

**UX Refinements:**
- ✅ Suggested questions hide after first message (JavaScript: `hideSuggestions()`)
- ✅ Enter key submits form (Shift+Enter for newline)
- ✅ Form resets after submission (HTMX: `hx-on::after-request`)
- ✅ Loading indicator appears during agent processing (HTMX: `hx-indicator`)
- ✅ Messages append to chat history without page reload (HTMX: `hx-swap="beforeend"`)

**Performance Results:**
- ✅ Response times: ~5 seconds (meets requirement: <5 seconds for 90% of queries)
- ✅ LangGraph agent execution: 3-5 seconds depending on tool usage
- ✅ Markdown rendering: <50ms (negligible overhead)
- ✅ Page load: <500ms (fast initial render)

**Testing Coverage:**
- ✅ Tested with multiple patients (ICN100001, ICN100002, ICN100004, ICN100009, ICN100010)
- ✅ All 4 suggested questions functional (including apostrophe escaping fix)
- ✅ DDI risk analysis working end-to-end
- ✅ Patient summary displaying correctly with enriched data
- ✅ Markdown formatting verified (headings, lists, bold, code blocks)
- ✅ Tools transparency display confirmed (shows "check_ddi_risks", "get_patient_summary")
- ✅ Responsive layout tested (sidebar collapse/expand)

**Success Criteria:**
- ✅ Insight page loads for any patient
- ✅ Chat interface accepts questions and displays AI responses
- ✅ DDI analysis works end-to-end via chat
- ✅ Patient summary displays correctly
- ✅ Response time ~5 seconds for complex questions (VERIFIED)

### Phase 3: Vital Trends + Vista Session Caching (Week 3) ✅ **COMPLETE**

**Days 1-2: Vital Trends Tool** ✅ **COMPLETE**
- [x] Create `ai/services/vitals_trend_analyzer.py`
- [x] Implement statistical trend analysis (linear regression, variance)
- [x] Implement `analyze_vitals_trends()` tool
- [x] Test with multiple patients (normal, concerning trends)
- [x] Integrate with LangGraph agent

**Days 3-4: Vista Session Caching + Testing** ✅ **COMPLETE**
- [x] Implement session-based Vista caching architecture
- [x] Fix browser cookie size limit issue (4096 bytes)
- [x] Cache Vista RPC responses in session (not merged data)
- [x] Implement on-demand merging for AI tools
- [x] Performance optimization (session size reduced from ~40KB to ~1.5KB)
- [x] Error handling improvements
- [x] Logging and observability
- [x] Documentation updates

**Day 5: Production Cleanup** ✅ **COMPLETE**
- [x] Remove DEBUG logging statements
- [x] Verify session persistence across navigation
- [x] Verify cache cleanup on logout
- [x] End-to-end testing with all 3 use cases
- [x] Final QA testing
- [x] Documentation updates (ai-insight-design.md, architecture.md)

**Implementation Notes:**

**Vitals Trend Analyzer** (`ai/services/vitals_trend_analyzer.py` - 467 lines):
- ✅ Statistical analysis using numpy (linear regression, variance, mean)
- ✅ Clinical norms comparison:
  - Blood Pressure: HTN Stage 1/2, Crisis thresholds (>130/80, >140/90, >180/120)
  - Heart Rate: Tachycardia/Bradycardia detection (>100, <60 bpm)
  - Temperature: Fever/Hypothermia classification (>100.4°F, <95°F)
  - Weight: Trend detection with statistical significance
- ✅ Vista cache integration: Uses cached Vista data when available
- ✅ Data source attribution: "PostgreSQL + Vista (200, 500)" shown in responses
- ✅ Handles missing data gracefully

**LangChain Tool Wrapper** (`ai/tools/vitals_tools.py` - 138 lines):
- ✅ `analyze_vitals_trends()` tool with request context support
- ✅ Global `_current_request` variable for session access
- ✅ `set_request_context()` function called by insight route
- ✅ Request context cleared after agent execution (cleanup)
- ✅ Tool invocation logging for observability

**Vista Session Caching Implementation:**
- ✅ **Problem Solved**: Browser rejected cookies > 4096 bytes
  - Original approach: Store full merged datasets (~40KB)
  - Console error: "Set-Cookie header is ignored... size must be <= 4096 characters"
- ✅ **Solution**: Store only Vista RPC responses (~1-2KB)
  - Cache structure: `{"vista_responses": {"200": "BP^120/80...", "500": "..."}}`
  - Merge on-demand: AI tools fetch PG data + merge with cached Vista responses
  - Session size: ~1500 bytes (well under limit)
- ✅ **Middleware Configuration**: Added `path="/"` parameter to SessionMiddleware
  - Ensures session cookie sent with all requests (not just specific paths)
  - TTL: 30 minutes (configurable)
  - Signed with `SESSION_SECRET_KEY` for security
- ✅ **Session Lifecycle**:
  - **Creation**: User clicks "Refresh from Vista" → Vista responses cached
  - **Persistence**: Cookie sent with every request, cache survives navigation
  - **Usage**: Page loads merge PG + cached Vista, AI tools use merged data
  - **Cleanup**: `request.session.clear()` on logout → both cookies deleted
- ✅ **Integration Points**:
  - `app/routes/vitals.py`: Cache Vista responses, merge on page load
  - `ai/services/vitals_trend_analyzer.py`: Use cached Vista data for analysis
  - `app/routes/auth.py`: Clear both `session_id` and `session` cookies on logout
  - `app/routes/insight.py`: Set request context for AI tools

**Testing Results:**
- ✅ Vitals trend analysis working with cached Vista data (315 vitals vs 305 PG-only)
- ✅ AI tools correctly attribute data sources: "PostgreSQL + Vista (200, 500)"
- ✅ Session persistence verified: Navigate away and back, cache persists
- ✅ Logout cleanup verified: Vista cache cleared on logout
- ✅ No browser console errors: Session cookie size under limit
- ✅ Performance: ~3-5 seconds for AI analysis (meets < 5 sec goal)

**Production Cleanup:**
- ✅ Removed all DEBUG logging statements (9 log lines removed)
- ✅ Retained production logging: Cache operations, merge statistics, RPC results
- ✅ Clean log output for operational visibility

**Success Criteria:**
- ✅ All 3 Phase 1 use cases working flawlessly (DDI, Summary, Vitals Trends)
- ✅ No critical bugs
- ✅ Performance meets goals (< 5 sec responses for 90% of queries)
- ✅ Vista data automatically used by AI when cached
- ✅ Session management robust (persists across navigation, cleared on logout)

---

## 11. Testing Strategy

### 11.1 Unit Tests

**AI Services:**
```python
# tests/ai/services/test_ddi_analyzer.py

import pytest
from ai.services.ddi_analyzer import DDIAnalyzer

def test_ddi_analyzer_finds_major_interaction():
    """Test that DDI analyzer finds Warfarin + Ibuprofen interaction."""
    analyzer = DDIAnalyzer()

    medications = [
        {'drug_name': 'Warfarin 5MG'},
        {'drug_name': 'Ibuprofen 400MG'}
    ]

    interactions = analyzer.find_interactions(medications)

    assert len(interactions) > 0
    assert interactions[0]['severity'] == 'Major'
    assert 'bleeding' in interactions[0]['description'].lower()

def test_ddi_analyzer_no_interactions():
    """Test that non-interacting drugs return empty list."""
    analyzer = DDIAnalyzer()

    medications = [
        {'drug_name': 'Acetaminophen 500MG'},
        {'drug_name': 'Vitamin D 1000IU'}
    ]

    interactions = analyzer.find_interactions(medications)

    assert len(interactions) == 0
```

**LangGraph Tools:**
```python
# tests/ai/tools/test_medication_tools.py

import pytest
from unittest.mock import AsyncMock, patch
from ai.tools.medication_tools import check_ddi_risks

@pytest.mark.asyncio
async def test_check_ddi_risks_tool():
    """Test DDI risks tool returns formatted string."""

    # Mock database session
    mock_db = AsyncMock()

    # Mock medication service
    with patch('ai.tools.medication_tools.medication_service') as mock_med_svc:
        mock_med_svc.get_patient_medications.return_value = [
            {'drug_name': 'Warfarin 5MG', 'dosage': '5MG'},
            {'drug_name': 'Aspirin 81MG', 'dosage': '81MG'}
        ]

        result = await check_ddi_risks("ICN1011530429", mock_db)

        assert "MAJOR" in result
        assert "bleeding" in result.lower()
        assert "Data sources" in result
```

### 11.2 Integration Tests

```python
# tests/ai/agents/test_insight_agent.py

import pytest
from ai.agents.insight_agent import InsightAgent

@pytest.mark.asyncio
async def test_agent_ddi_question(mock_db):
    """Test agent correctly invokes DDI tool for relevant question."""

    agent = InsightAgent(
        db_session=mock_db,
        patient_icn="ICN1011530429",
        patient_name="Test Patient"
    )

    response = await agent.invoke("Are there any drug-drug interaction risks?")

    assert response['output'] is not None
    assert 'check_ddi_risks' in response['tools_used']
    assert len(response['output']) > 0
```

### 11.3 API Tests

```python
# tests/routes/test_insight_routes.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_insight_page_loads():
    """Test that insight page loads for valid patient."""
    response = client.get("/insight/ICN1011530429")

    assert response.status_code == 200
    assert "Clinical Insights" in response.text

def test_chat_endpoint():
    """Test chat endpoint returns HTML fragment."""
    response = client.post("/insight/chat", data={
        "patient_icn": "ICN1011530429",
        "message": "Are there any DDI risks?"
    })

    assert response.status_code == 200
    assert "chat-message--ai" in response.text
```

### 11.4 Clinical Validation Testing

**Manual Test Cases:**

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| **DDI-1** | "Check DDI risks" for patient with Warfarin + Ibuprofen | MAJOR risk flagged, bleeding warning | ⏳ |
| **DDI-2** | "Check DDI risks" for patient with no interactions | "No interactions found" | ⏳ |
| **Summary-1** | "Summarize patient" for patient 1011 | Includes demographics, 8 meds, recent vitals, allergies | ⏳ |
| **Trends-1** | "Vital trends" for patient with increasing BP | Flags concerning BP trend, recommends monitoring | ⏳ |
| **Trends-2** | "Vital trends" for patient with stable vitals | Reports all vitals normal and stable | ⏳ |

---

## 12. Ethical Considerations

### 12.1 Transparency Requirements

**MUST Display:**
1. ✅ Clear "AI-generated" disclaimer on every page
2. ✅ Show which tools/data sources were queried
3. ✅ Timestamp for when data was retrieved
4. ✅ Indication of data freshness (T-0 vs T-1)

**Example:**
```
AI Response: [content]

📊 Data sources: PostgreSQL (47 vital readings, last updated T-1),
Vista RPC (real-time query at 14:23)
🔧 Tools used: analyze_vitals_trends, get_patient_medications
```

### 12.2 Clinical Safety Guardrails

**Implemented Safeguards:**
1. ✅ **No autonomous actions** - AI only provides recommendations, never executes orders
2. ✅ **Always verify disclaimer** - "AI-generated insights. Always verify clinically."
3. ✅ **Risk flagging** - Use ⚠️ symbols for Major/Moderate DDI risks
4. ✅ **Source attribution** - Always cite data sources
5. ✅ **Low temperature** - Use temp=0.3 for clinical accuracy (minimize hallucinations)

**Explicitly NOT Allowed:**
- ❌ Making diagnoses
- ❌ Prescribing treatments
- ❌ Executing orders
- ❌ Documenting in chart
- ❌ Modifying patient data

### 12.3 Data Privacy

**VA Requirements:**
- ✅ All patient data stays within VA network (no external API calls with PHI)
- ✅ OpenAI API: Send only de-identified summaries, NOT raw PHI
- ✅ No logging of patient-specific queries to external services
- ✅ Comply with VHA Directive 6500 (Information Security Program)

**De-identification Pattern:**
```python
# GOOD: De-identified summary sent to LLM
"Patient is on 8 medications including anticoagulant, beta-blocker, diuretic..."

# BAD: Raw PHI sent to LLM
"John Smith (SSN 123-45-6789) is on Warfarin, Metoprolol, Furosemide..."
```

### 12.4 User Training Requirements

**Before Launch:**
1. ✅ Clinician training: How to use Insights page appropriately
2. ✅ Documentation: What questions work well vs poorly
3. ✅ Limitations: What AI cannot do (diagnose, prescribe, etc.)
4. ✅ Feedback mechanism: How to report inaccurate responses

---

## 13. Success Criteria

### 13.1 Phase 1 MVP Launch Criteria

**Functional Requirements:**
- [ ] Insight page accessible via sidebar for all patients
- [ ] Chat interface accepts natural language questions
- [ ] DDI risk assessment working for 95% of patients with medications
- [ ] Patient summary includes all 5 clinical domains
- [ ] Vital trends analysis working for patients with vitals data

**Performance Requirements:**
- [ ] Page load time < 2 seconds
- [ ] Simple questions (summary) response time < 3 seconds
- [ ] Complex questions (DDI analysis) response time < 5 seconds
- [ ] No crashes or unhandled exceptions

**UX Requirements:**
- [ ] Chat interface feels responsive and natural
- [ ] AI responses are clinically coherent and accurate
- [ ] Transparency (tools used, data sources) always displayed
- [ ] Works on desktop and tablet (responsive)

**Clinical Validation:**
- [ ] 10 test cases manually validated by clinical SME
- [ ] DDI detection matches known interaction database
- [ ] No false-positive critical risks
- [ ] Trend analysis aligns with clinical judgment

### 13.2 User Feedback Targets (Post-Launch)

**Qualitative Feedback:**
- Clinicians report Insights page saves time vs manual chart review
- Positive sentiment: "Helpful", "Insightful", "Saves time"
- Low friction: "Easy to use", "Intuitive"

**Quantitative Metrics:**
- Usage: >50% of active users try Insights page within 2 weeks
- Retention: >30% of users return to Insights page within 1 week
- Questions asked: Avg 3-5 questions per session
- Error rate: <5% of questions result in errors

---

## 14. Future Enhancements

### 14.1 Phase 2 Features (3-6 Months)

**DDI Severity Classification**
- Add severity ranking (Major, Moderate, Minor) to drug-drug interactions
- Approaches:
  - **LLM parsing:** Extract severity from interaction description text ("major risk", "severe", etc.)
  - **Rule-based:** Pattern matching on description keywords
  - **External API:** Query DrugBank API or other clinical databases for severity
  - **Manual curation:** Label high-priority interactions for training data
- Enables prioritized presentation (show Major risks first)
- Improves clinical utility by focusing attention on critical interactions

**Women's Health Screening Gaps**
- Check for overdue mammograms, pap smears, bone density scans
- Requires additional clinical data (procedure history, screening guidelines)
- Tools: `check_womens_health_screening(patient_icn, age, gender)`

**Community Care Integration (MIMIC)**
- Integrate PhysioNet MIMIC data as simulated community care
- Show care coordination insights ("Patient received care outside VA")
- Requires patient linkage table (ICN ↔ MIMIC subject_id)
- Tools: `get_community_care_meds(patient_icn)`

**Chart Overview Summarization**
- Generate natural language summary of entire chart
- "Patient is 72yo male veteran with AFib, CHF, HTN..."
- Read Gold Parquet for fast access to all domains
- Tools: `generate_chart_summary(patient_icn)`

### 14.2 Phase 3+ Advanced Features (6-12 Months)

**Multimodal (Images + Text)**
- Analyze uploaded EKGs, X-rays, lab flowsheets
- Requires image processing models
- Example: "Analyze this EKG for AFib"

**Proactive Alerts**
- Background agent monitors all patients
- Flags high-risk situations (e.g., "Patient 1011 has new Major DDI")
- Requires infrastructure for continuous monitoring

**Voice Interface**
- Clinicians ask questions via voice
- Hands-free operation during patient encounters
- Requires speech-to-text integration

**Custom Tools per Specialty**
- Cardiology tools (CHADS2-VASc score, GRACE risk)
- Mental health tools (PHQ-9 trends, suicide risk)
- Oncology tools (TNM staging, chemotherapy contraindications)

### 14.3 LLM Provider Alternatives

**Azure OpenAI**
- VA-approved cloud provider
- GPT-4 hosted within VA boundary
- Better data privacy guarantees

**Anthropic Claude**
- Longer context window (100K+ tokens)
- Better reasoning for complex clinical scenarios
- Constitutional AI (safer, more aligned)

**Open-Source Models (Llama, Mistral)**
- Run entirely on-premises (no external API)
- Full data control
- Requires GPU infrastructure

### 14.4 Vector Database (RAG Enhancement)

**Problem:** Current tools query structured data only
**Solution:** Add vector search for unstructured data (clinical notes, guidelines)

**Architecture:**
```
Clinical Notes (text)
    ↓
Embeddings (sentence-transformers)
    ↓
pgvector (PostgreSQL extension)
    ↓
Semantic search tool
    ↓
LangGraph agent
```

**Use Case:**
- "Has this patient been counseled about smoking cessation?"
- Search clinical notes for smoking-related keywords
- Return: "Yes, documented in note from 2024-03-15: 'Discussed..."

---

## Appendix A: Dependencies

### A.1 Python Packages  
(add to requirements.txt)

**Updated versions as of January 2025:**

```txt
# AI/ML packages (CURRENT VERSIONS - installed)
langchain==1.2.0
langgraph==1.0.5
langchain-openai==1.1.6
openai==2.14.0

# Existing packages (already in med-z1)
fastapi
jinja2
sqlalchemy
python-dotenv
pandas
pyarrow
boto3  # For MinIO

# Testing
pytest
pytest-asyncio
```

**Note:** These versions reflect significant improvements over the original design document versions:
- `langgraph` 1.0.5 includes stable API with `ToolNode` (replaces deprecated `ToolExecutor`)
- `langchain` 1.2.0 has better modular imports via `langchain_core` and `langchain_openai`
- `openai` 2.14.0 includes latest API features and bug fixes

### A.2 Environment Variables  
(add to .env)

```bash
# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo
OPENAI_TEMPERATURE=0.3

# Optional: Azure OpenAI (future)
# AZURE_OPENAI_ENDPOINT=https://....openai.azure.com/
# AZURE_OPENAI_API_KEY=...
```

---

## Appendix B: File Structure

```
med-z1/
├── ai/                              # NEW - AI/ML subsystem
│   ├── README.md
│   ├── __init__.py
│   ├── agents/                      # LangGraph agents
│   │   ├── __init__.py
│   │   └── insight_agent.py         # Main chatbot agent
│   ├── tools/                       # LangChain tools
│   │   ├── __init__.py
│   │   ├── medication_tools.py      # check_ddi_risks
│   │   ├── patient_tools.py         # get_patient_summary
│   │   └── vitals_tools.py          # analyze_vitals_trends
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── ddi_analyzer.py          # Refactored from notebooks
│   │   ├── patient_context.py       # Wraps existing app/services
│   │   └── vitals_trend_analyzer.py # Statistical trend analysis
│   └── prompts/                     # System prompts
│       ├── __init__.py
│       └── system_prompts.py
│
├── app/
│   ├── routes/
│   │   ├── insight.py               # NEW - /insight routes
│   │   └── ... (existing routes)
│   ├── templates/
│   │   ├── insight.html             # NEW - Main Insight page
│   │   ├── partials/
│   │   │   ├── chat_message.html    # NEW - Chat message partial
│   │   │   └── ... (existing partials)
│   │   └── ... (existing templates)
│   ├── static/
│   │   └── styles.css               # UPDATED - Add chat styles
│   └── services/                    # EXISTING - Reused by AI tools
│       ├── medication_service.py
│       ├── vitals_service.py
│       ├── demographics_service.py
│       └── ...
│
├── notebook/                        # EXISTING - Stays as research layer
│   ├── src/
│   │   ├── ddi_transforms.py        # SOURCE for ai/services/ddi_analyzer.py
│   │   ├── 04_features.ipynb        # SOURCE for risk scoring logic
│   │   └── ...
│   └── ...
│
├── docs/
│   ├── ai-insight-design.md         # THIS DOCUMENT
│   └── ... (existing design docs)
│
├── tests/
│   ├── ai/                          # NEW - AI tests
│   │   ├── services/
│   │   ├── tools/
│   │   └── agents/
│   └── ... (existing tests)
│
├── config.py                        # UPDATED - Add OpenAI config
├── requirements.txt                 # UPDATED - Add LangChain packages
└── .env                             # UPDATED - Add OPENAI_API_KEY
```

---

## Appendix C: Python Package Initialization
(`__init__.py` Files)

### C.1 Overview

Each directory in the `ai/` subsystem requires an `__init__.py` file to be recognized as a Python package. These files can range from empty (minimal) to functional (exposing key imports for cleaner API usage).

**Two Valid Approaches:**

1. **Empty files** - Quickest way to establish package structure (Python 3.3+)
2. **Export files** - Expose key classes/functions for cleaner imports (recommended for production)

### C.2 Recommended Content by File

#### `ai/__init__.py` (Top-level package)

**Purpose:** Expose main entry points and package metadata

```python
"""
AI/ML subsystem for med-z1.

Provides clinical insights through agentic RAG with LangGraph.
"""

__version__ = "0.1.0"

# Expose main components for convenient importing
from ai.agents.insight_agent import create_insight_agent

__all__ = [
    "create_insight_agent",
]
```

**Benefit:** Enables `from ai import create_insight_agent` instead of `from ai.agents.insight_agent import create_insight_agent`

---

#### `ai/agents/__init__.py`

**Purpose:** Expose agent creation function and state

```python
"""LangGraph agents for clinical insights."""

from ai.agents.insight_agent import create_insight_agent, InsightState

__all__ = [
    "create_insight_agent",
    "InsightState",
]
```

**Benefit:** Cleaner imports in routes: `from ai.agents import create_insight_agent, InsightState`

---

#### `ai/tools/__init__.py`
⭐ **MOST IMPORTANT**

**Purpose:** Expose all tools as a convenient list for agent initialization

```python
"""LangChain tools for clinical data access."""

from ai.tools.medication_tools import check_ddi_risks
from ai.tools.patient_tools import get_patient_summary
from ai.tools.vitals_tools import analyze_vitals_trends

# Convenient list of all available tools
ALL_TOOLS = [
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
]

__all__ = [
    "check_ddi_risks",
    "get_patient_summary",
    "analyze_vitals_trends",
    "ALL_TOOLS",
]
```

**Benefit:** Enables clean agent creation:
```python
from ai.tools import ALL_TOOLS
agent = create_insight_agent(ALL_TOOLS)
```

**Why This One Matters Most:** The `ALL_TOOLS` list is central to how the LangGraph agent gets initialized. As you add new tools, you simply append them to this list.

---

#### `ai/services/__init__.py`

**Purpose:** Expose service classes

```python
"""Business logic services for AI components."""

from ai.services.ddi_analyzer import DDIAnalyzer
from ai.services.patient_context import PatientContextBuilder
from ai.services.vitals_trend_analyzer import VitalsTrendAnalyzer

__all__ = [
    "DDIAnalyzer",
    "PatientContextBuilder",
    "VitalsTrendAnalyzer",
]
```

**Benefit:** Cleaner imports: `from ai.services import DDIAnalyzer` instead of full path

---

#### `ai/prompts/__init__.py`

**Purpose:** Expose system prompts and templates

```python
"""System prompts and prompt templates."""

from ai.prompts.system_prompts import INSIGHT_SYSTEM_PROMPT

__all__ = [
    "INSIGHT_SYSTEM_PROMPT",
]
```

**Benefit:** Simple access: `from ai.prompts import INSIGHT_SYSTEM_PROMPT`

---

### C.3 Summary Table

| File | Primary Purpose | Can Be Empty? | Priority |
|------|----------------|---------------|----------|
| `ai/__init__.py` | Package metadata + main exports | ✅ Yes | Medium |
| `ai/agents/__init__.py` | Agent exports | ✅ Yes | Medium |
| `ai/tools/__init__.py` | **ALL_TOOLS list** | ⚠️ Should have content | **HIGH** |
| `ai/services/__init__.py` | Service class exports | ✅ Yes | Low |
| `ai/prompts/__init__.py` | Prompt exports | ✅ Yes | Low |

### C.4 Incremental Development

**Recommended workflow for building the AI subsystem:**

#### Phase 1: Establish Package Structure
(Day 1)  

Create all `__init__.py` files as **empty** to quickly establish the Python package structure:

```bash
# From project root
touch ai/__init__.py
touch ai/agents/__init__.py
touch ai/tools/__init__.py
touch ai/services/__init__.py
touch ai/prompts/__init__.py
```

**Verification:**
```python
# Test that packages are recognized
python -c "import ai; import ai.agents; import ai.tools"
# Should run without errors
```

#### Phase 2: Populate as You Implement  
(Days 2-5)

Add exports to each `__init__.py` **as you create the corresponding modules**:

1. **Day 2:** Implement `ai/agents/insight_agent.py` → Update `ai/agents/__init__.py` to export it
2. **Day 3:** Implement `ai/tools/medication_tools.py` → Update `ai/tools/__init__.py` to include it in `ALL_TOOLS`
3. **Day 4:** Implement `ai/services/ddi_analyzer.py` → Update `ai/services/__init__.py` to export it
4. **Day 5:** Implement `ai/prompts/system_prompts.py` → Update `ai/prompts/__init__.py` to export it

This incremental approach:
- ✅ Prevents import errors during development
- ✅ Keeps `__init__.py` files synchronized with actual implementations
- ✅ Allows testing of each component as it's built

### C.5 Usage Examples

#### Before (Without `__init__.py` exports)
```python
# app/routes/insight.py
from ai.agents.insight_agent import create_insight_agent
from ai.tools.medication_tools import check_ddi_risks
from ai.tools.patient_tools import get_patient_summary
from ai.tools.vitals_tools import analyze_vitals_trends

tools = [check_ddi_risks, get_patient_summary, analyze_vitals_trends]
agent = create_insight_agent(tools)
```

#### After (With `__init__.py` exports)
```python
# app/routes/insight.py
from ai import create_insight_agent
from ai.tools import ALL_TOOLS

agent = create_insight_agent(ALL_TOOLS)
```

**Result:** Cleaner, more maintainable code with fewer import statements.

### C.6 Consistency with Existing med-z1 Patterns

Check existing `__init__.py` files in the med-z1 codebase for consistency:

```bash
# Review existing patterns
cat app/__init__.py
cat app/services/__init__.py
```

Follow the same export style and documentation conventions used elsewhere in the project.

---

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v1.0 | 2025-12-28 | Initial draft - Architecture approved, ready for implementation | Claude + User |
| v1.1 | 2025-12-29 | Updated for current library versions (langchain 1.2.0, langgraph 1.0.5, langchain-openai 1.1.6, openai 2.14.0). Updated Section 5.2 with ToolNode API pattern. Added Appendix C: Python Package Initialization guidelines. Clarified Days 1-2 tasks to include config.py update. | Claude + User |
| v1.2 | 2025-12-29 | Updated DDI reference data documentation (Section 3.1) with actual Kaggle/DrugBank source, schema, and MinIO paths. Removed severity field assumptions from Phase 1 MVP (Sections 4.1, 6.1, 7.1). Added DDI severity classification as Phase 2 enhancement (Section 14.1). Marked Days 1-2 complete. | Claude + User |
| v1.3 | 2025-12-29 | Marked Days 3-4 complete. Added implementation notes for DDI Tool (ETL pipeline, DDIAnalyzer, LangGraph integration). Updated success criteria with actual test results (ICN100010: GABAPENTIN + ALPRAZOLAM interaction found). | Claude + User |
| v1.4 | 2025-12-29 | Marked Day 5 complete. Added synchronous pattern notes to Section 2.2. Added implementation notes for PatientContextBuilder service and get_patient_summary tool. Updated success criteria. **Phase 1 Week 1 (MVP Foundation) Complete** - 2 tools implemented (check_ddi_risks, get_patient_summary). | Claude + User |

---

**Next Steps:**
1. ✅ Review and approve this design specification
2. ⏳ Begin Phase 1 Week 1 implementation (infrastructure setup)
3. ⏳ Refactor DDI analyzer from notebooks
4. ⏳ Build LangGraph agent with DDI tool
5. ⏳ Create FastAPI routes and HTMX UI

**Questions or Feedback:** Review with stakeholders before implementation begins.
