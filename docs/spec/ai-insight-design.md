# AI Clinical Insights Design Specification

**Document Version:** v1.0
**Created:** 2025-12-28
**Status:** Draft - Architecture Approved
**Target Completion:** Phase 1 MVP - 3 weeks from start

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

- **New sidebar menu item:** "Insights" (positioned after Labs, before Problems)
- **Page layout:** Chat-style interface (similar to ChatGPT, Claude)
- **Interaction model:** User types questions, AI responds with sourced answers
- **Technology:** FastAPI + HTMX (consistent with existing med-z1 patterns)

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
│                         User (Clinician)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTMX POST /insight/chat
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Route (/insight/chat)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LangGraph Agent (InsightAgent)               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ State: {messages, patient_icn, tools_used}                 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│    ┌────────────────────────┼────────────────────────┐          │
│    ▼                        ▼                        ▼          │
│  ┌──────┐              ┌──────┐                ┌──────┐        │
│  │Tool 1│              │Tool 2│                │Tool 3│        │
│  │ DDI  │              │Summ. │                │Vitals│        │
│  └──┬───┘              └──┬───┘                └──┬───┘        │
└─────┼─────────────────────┼───────────────────────┼────────────┘
      │                     │                       │
      ▼                     ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              ai/services/ (Business Logic Layer)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │DDIAnalyzer   │  │PatientContext│  │VitalsTrend   │          │
│  │(from notebook)│  │Builder       │  │Analyzer      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│           Existing app/services/ (Data Access Layer)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │medication_   │  │vitals_       │  │demographics_ │          │
│  │service       │  │service       │  │service       │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data Sources                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │PostgreSQL    │  │Vista RPC     │  │MinIO/Parquet │          │
│  │(T-1, historical)│ │(T-0, realtime)│ │(DDI reference)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Layer Strategy

**Decision:** Wrap existing `app/services/` layer rather than creating new data access code.

**Rationale:**
- ✅ Reuses 8 months of existing med-z1 development
- ✅ Single source of truth for data access logic
- ✅ Easier maintenance (one place to update queries)
- ✅ Faster implementation (no duplicate work)

**Pattern:**
```python
# ai/services/patient_context.py wraps existing services
from app.services import medication_service, vitals_service

class PatientContextBuilder:
    async def get_medication_summary(self) -> str:
        # Delegate to existing service
        meds = await medication_service.get_patient_medications(self.db, self.icn)
        # Format for LLM consumption (string, not DataFrame)
        return self._format_medications_as_text(meds)
```

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

---

## 3. Data Sources

### 3.1 Primary Data Sources (Phase 1)

| Data Source | Type | Content | Access Method |
|-------------|------|---------|---------------|
| **PostgreSQL (T-1)** | Relational DB | Demographics, Medications, Vitals, Allergies, Encounters, Labs | `app/services/*_service.py` |
| **Vista RPC (T-0)** | Real-time API | Current-day vitals, medications | `app/services/vista_client.py` |
| **DDI Reference** | Parquet/MinIO | 267K drug-drug interactions | Refactored from `notebook/src/ddi_transforms.py` |

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
- ~267K interactions, ~10MB in memory
- Fast lookups by drug name

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

⚠️ **MAJOR Risk**: Warfarin + Ibuprofen
- Risk: Increased bleeding risk
- Recommendation: Consider alternative to ibuprofen (e.g., acetaminophen)

⚠️ **MODERATE Risk**: Lisinopril + Potassium Chloride
- Risk: Hyperkalemia (elevated potassium)
- Recommendation: Monitor potassium levels regularly

Data sources: PostgreSQL medications (163 records), DDI reference (267K interactions)
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

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

# Define nodes
def agent_node(state: InsightState) -> InsightState:
    """LLM decides what to do (call tools or respond)."""
    # Invoke LLM with tools
    # Returns either tool calls or final response
    ...

def tool_node(state: InsightState) -> InsightState:
    """Execute requested tools."""
    # Run tools, append results to messages
    ...

def should_continue(state: InsightState) -> str:
    """Router: continue to tools or end?"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    else:
        return END

# Build graph
workflow = StateGraph(InsightState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)
workflow.add_edge("tools", "agent")  # Loop back to agent after tools

# Compile
graph = workflow.compile()
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
│  (GPT-4)     │
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

    # Rank by severity
    major = [i for i in interactions if i['severity'] == 'Major']
    moderate = [i for i in interactions if i['severity'] == 'Moderate']
    minor = [i for i in interactions if i['severity'] == 'Minor']

    result = f"Found {len(interactions)} drug-drug interactions:\n\n"

    if major:
        result += "⚠️ MAJOR RISKS:\n"
        for i in major:
            result += f"- {i['drug_a']} + {i['drug_b']}: {i['description']}\n"

    if moderate:
        result += "\n⚠️ MODERATE RISKS:\n"
        for i in moderate:
            result += f"- {i['drug_a']} + {i['drug_b']}: {i['description']}\n"

    if minor:
        result += f"\n({len(minor)} minor interactions - generally safe but monitor)\n"

    result += f"\nData sources: {len(medications)} medications from PostgreSQL, 267K interactions from DDI reference"

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

        # Sort by severity
        severity_order = {'Major': 0, 'Moderate': 1, 'Minor': 2}
        interactions.sort(key=lambda x: severity_order.get(x['severity'], 99))

        return interactions

    def _check_pair(self, drug_a: str, drug_b: str) -> Dict | None:
        """Check if two drugs interact."""
        # Normalize drug names (case-insensitive, remove doses)
        drug_a_clean = self._normalize_drug_name(drug_a)
        drug_b_clean = self._normalize_drug_name(drug_b)

        # Query DDI reference data
        match = self.ddi_data[
            ((self.ddi_data['drug_a'] == drug_a_clean) &
             (self.ddi_data['drug_b'] == drug_b_clean)) |
            ((self.ddi_data['drug_a'] == drug_b_clean) &
             (self.ddi_data['drug_b'] == drug_a_clean))
        ]

        if not match.empty:
            row = match.iloc[0]
            return {
                'drug_a': drug_a,
                'drug_b': drug_b,
                'severity': row['severity'],
                'description': row['description']
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
                <i class="fa-solid fa-brain"></i>
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

```html
<!-- app/templates/base.html - Add to sidebar navigation -->

<!-- After Labs, before Problems -->
<a href="/insight"
   class="sidebar__link {{ 'sidebar__link--active' if active_page == 'insight' else '' }}"
   data-tooltip="AI Clinical Insights">
    <i class="fa-solid fa-brain fa-lg"></i>
    <span class="sidebar__text">Insights</span>
</a>
```

---

## 10. Implementation Phases

### Phase 1: MVP Foundation (Week 1)

**Days 1-2: Infrastructure Setup**
- [ ] Install dependencies: `langchain`, `langgraph`, `openai`
- [ ] Create `ai/` directory structure
- [ ] Add OpenAI API key to `.env`
- [ ] Create basic LangGraph agent skeleton
- [ ] Test LangGraph agent with simple echo tool

**Days 3-4: DDI Tool Implementation**
- [ ] Refactor `notebook/src/ddi_transforms.py` → `ai/services/ddi_analyzer.py`
- [ ] Create DDI reference data loader (MinIO → cached DataFrame)
- [ ] Implement `check_ddi_risks()` tool
- [ ] Unit test DDI analyzer with sample medications
- [ ] Test DDI tool integration with LangGraph agent

**Day 5: Patient Summary Tool**
- [ ] Create `ai/services/patient_context.py`
- [ ] Implement `get_patient_summary()` tool
- [ ] Wrap existing services (demographics, meds, vitals, allergies, encounters)
- [ ] Test patient summary output formatting

**Success Criteria:**
- ✅ LangGraph agent responds to basic questions
- ✅ DDI analysis returns correct interactions for test patient
- ✅ Patient summary includes all 5 clinical domains

### Phase 2: Web UI Integration (Week 2)

**Days 1-2: FastAPI Routes + Templates**
- [ ] Create `app/routes/insight.py`
- [ ] Implement `GET /insight/{icn}` route
- [ ] Implement `POST /insight/chat` route
- [ ] Create `app/templates/insight.html`
- [ ] Create `app/templates/partials/chat_message.html`
- [ ] Add CSS styling to `app/static/styles.css`

**Days 3-4: HTMX Integration + UX Polish**
- [ ] Wire up HTMX chat form
- [ ] Test message submission and response display
- [ ] Add loading indicators
- [ ] Implement suggested questions chips
- [ ] Add "tools used" transparency display
- [ ] Test chat conversation flow

**Day 5: Sidebar Integration + Testing**
- [ ] Add "Insights" link to sidebar navigation
- [ ] Test page navigation from sidebar
- [ ] End-to-end testing with multiple patients
- [ ] Performance testing (response times)
- [ ] Bug fixes and refinement

**Success Criteria:**
- ✅ Insight page loads for any patient
- ✅ Chat interface accepts questions and displays AI responses
- ✅ DDI analysis works end-to-end via chat
- ✅ Patient summary displays correctly
- ✅ Response time < 5 seconds for complex questions

### Phase 3: Vital Trends + Polish (Week 3)

**Days 1-2: Vital Trends Tool**
- [ ] Create `ai/services/vitals_trend_analyzer.py`
- [ ] Implement statistical trend analysis (linear regression, variance)
- [ ] Implement `analyze_vitals_trends()` tool
- [ ] Test with multiple patients (normal, concerning trends)
- [ ] Integrate with LangGraph agent

**Days 3-4: Testing + Refinement**
- [ ] User acceptance testing with all 3 use cases
- [ ] Performance optimization (caching, query tuning)
- [ ] Error handling improvements
- [ ] Logging and observability
- [ ] Documentation updates

**Day 5: Launch Preparation**
- [ ] Final QA testing
- [ ] Update `CLAUDE.md` with Insights page info
- [ ] Create user guide / help text
- [ ] Deploy to staging environment
- [ ] Stakeholder demo

**Success Criteria:**
- ✅ All 3 Phase 1 use cases working flawlessly
- ✅ No critical bugs
- ✅ Performance meets goals (< 5 sec responses)
- ✅ Positive feedback from initial users

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

### A.1 Python Packages (add to requirements.txt)

```txt
# AI/ML packages
langchain==0.1.0
langgraph==0.0.20
langchain-openai==0.0.5
openai==1.12.0

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

### A.2 Environment Variables (add to .env)

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

## Document Revision History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| v1.0 | 2025-12-28 | Initial draft - Architecture approved, ready for implementation | Claude + User |

---

**Next Steps:**
1. ✅ Review and approve this design specification
2. ⏳ Begin Phase 1 Week 1 implementation (infrastructure setup)
3. ⏳ Refactor DDI analyzer from notebooks
4. ⏳ Build LangGraph agent with DDI tool
5. ⏳ Create FastAPI routes and HTMX UI

**Questions or Feedback:** Review with stakeholders before implementation begins.
