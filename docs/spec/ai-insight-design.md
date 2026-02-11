# AI Clinical Insights Design Specification

**Document Version:** v2.4
**Created:** 2025-12-28
**Updated:** 2026-01-20 (Phase 6: Conversation Memory - COMPLETE)
**Status:** Phase 1-6 Complete | Post-Phase 4 Enhancements Complete | Post-Phase 5 Enhancements Complete | Phase 7 (Immunizations) Ready for Implementation
**Phase 1-3 Completion Date:** 2025-12-30
**Phase 4 Completion Date:** 2026-01-03
**Post-Phase 4 Enhancements Completion Date:** 2026-01-03
**Phase 5 Completion Date:** 2026-01-04
**Post-Phase 5 Enhancements Completion Date:** 2026-01-04
**Phase 6 Completion Date:** 2026-01-20    

**Implementation Status Source:** `docs/spec/implementation-status.md`

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Data Sources](#3-data-sources)
4. [Use Cases - MVP](#4-use-cases---mvp)
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

### 1.2 Key Capabilities

**Phase 1-3 Complete ✅:**
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

**Phase 4 (Clinical Notes Integration) 📝:**
4. **Clinical Notes Summary**
   - Provides narrative clinical context from recent notes
   - Summarizes Progress Notes, Consults, Discharge Summaries, Imaging Reports
   - Answers note-specific queries ("What did the cardiology consult say?")

5. **Enhanced Patient Context**
   - Integrates narrative clinical documentation with structured data
   - Bridges the gap between "what happened" (structured) and "why/how" (narrative)
   - Enriches AI responses with clinician observations and assessments

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

**Leverage Existing Infrastructure** - Reuse `app/services/` layer, PostgreSQL, Vista RPC  
**Transparency** - Show which data sources were queried  
**Clinical Safety** - Always display AI-generated disclaimer  
**Consistency** - Follow FastAPI + HTMX patterns from rest of med-z1  
**Extensibility** - Easy to add new tools/capabilities later  

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
- Reuses existing med-z1 development
- Single source of truth for data access logic
- Easier maintenance (one place to update queries)
- Faster implementation (no duplicate work)

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
- Phase 1 uses synchronous functions (matching existing `app/db/` pattern)
- `app/db/` functions create their own database connections (no session parameter needed)
- Future consideration: Refactor to async/await pattern for better performance with concurrent requests
- Future consideration: Session-based database access for connection pooling

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
1. **Store RPC responses, not merged data** - Reduces session size from ~40KB to ~1.5KB
2. **Merge on-demand** - Page loads and AI tools merge PG + cached Vista as needed
3. **Session cookie, not server-side storage** - Simple, stateless, no Redis/database needed
4. **Automatic cleanup on logout** - Clears both `session_id` (auth) and `session` (Vista cache) cookies

**Benefits:**
- AI tools automatically use real-time Vista data when available
- No separate "Refresh Vista for AI" button needed
- Transparent to users - cache status shown with green badge
- Performance: ~1-3 second merge latency (acceptable for AI analysis)
- Scalability: No server-side session storage required

**Files Modified:**
- `app/services/vista_cache.py` - Cache management service
- `app/routes/vitals.py` - Cache Vista responses, merge on page load
- `ai/services/vitals_trend_analyzer.py` - Use cached Vista data for analysis
- `app/main.py` - SessionMiddleware configuration
- `app/routes/auth.py` - Clear both cookies on logout

---

## 3. Data Sources

**⚠️ Authoritative Database Schemas:** For complete, accurate database schemas, see:
- **SQL Server (CDW Mock):** [`docs/guide/med-z1-sqlserver-guide.md`](../guide/med-z1-sqlserver-guide.md)
- **PostgreSQL (Serving DB):** [`docs/guide/med-z1-postgres-guide.md`](../guide/med-z1-postgres-guide.md)

This section provides implementation context and design rationale. Refer to the database guides for authoritative schema definitions.

### 3.1 Primary Data Sources

**Phase 1-3 (Complete):**

| Data Source | Type | Content | Access Method |
|-------------|------|---------|---------------|
| **PostgreSQL (T-1)** | Relational DB | Demographics, Medications, Vitals, Allergies, Encounters, Labs | `app/services/*_service.py` |
| **Vista RPC (T-0)** | Real-time API | Current-day vitals, medications | `app/services/vista_client.py` |
| **DDI Reference** | Parquet/MinIO | ~191K drug-drug interactions from DrugBank (via Kaggle) | Refactored from `notebook/src/ddi_transforms.py` |

**Phase 4 (Clinical Notes Integration):**

| Data Source | Type | Content | Access Method |
|-------------|------|---------|---------------|
| **Clinical Notes (PostgreSQL)** | Relational DB | 106 clinical notes across 36 patients (Progress Notes, Consults, Discharge Summaries, Imaging Reports) | `app/db/notes.py` |

**Clinical Notes Data Details:**
- **Source:** VistA CDWWork (TIU.TIUDocument_8925, TIU.TIUDocumentText)
- **Format:** Full narrative SOAP documentation (Subjective, Objective, Assessment, Plan)
- **Schema:** `patient_clinical_notes` table with 19 columns
- **Key Fields:**
  - `document_text` - Full note narrative (TEXT, avg ~2000 tokens)
  - `text_preview` - First 200 characters (VARCHAR)
  - `document_class` - Note type (Progress Notes, Consults, Discharge Summaries, Imaging)
  - `reference_datetime` - Clinical date of note
  - `author_name`, `facility_name`, `status`
  - **AI-Ready Columns:** `embedding_vector` (VECTOR - pgvector), `ai_summary` (TEXT), `key_entities` (JSONB)
- **Coverage:** 106 notes across 36 patients (avg 2.9 notes per patient, max 8 notes for ICN100001)
- **Access Functions:** `get_recent_notes()`, `get_notes_summary()`, `get_all_notes()`, `get_note_detail()`, `get_note_authors()`

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

## 4. Use Cases - MVP

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

### 4.4 Use Case 4: Clinical Notes Summary (Phase 4)

**User Prompt:**
_"Summarize the recent clinical notes for this patient"_

**Agent Flow:**
1. Parse intent: User wants clinical notes overview
2. Invoke tool: `get_patient_summary(patient_icn)` (enhanced version includes notes)
3. Tool logic:
   - Get patient demographics, medications, vitals, allergies, encounters (existing)
   - **NEW:** Get recent clinical notes (last 3 notes, default 90 days)
   - Format note summaries with type, date, author, preview text
4. LLM synthesizes response combining structured and narrative data
5. Return: Comprehensive patient overview with clinical narrative context

**Example Response:**
```
**Patient Clinical Summary**

Demographics: 68-year-old male, Service-Connected 70%, Primary Care at Atlanta VA

Active Medications (5):
- Lisinopril 20mg daily (HTN)
- Metformin 1000mg twice daily (Diabetes)
- Atorvastatin 40mg daily (Hyperlipidemia)
- Aspirin 81mg daily (CAD prophylaxis)
- Gabapentin 300mg three times daily (Neuropathy)

Recent Vitals: BP 142/88, HR 76, Weight 185 lbs, BMI 27.4

Allergies: Penicillin (rash), Morphine (nausea)

Recent Clinical Notes (Last 3):
1. **2025-12-28 Progress Note** by Dr. Jonathan Smith, MD (Atlanta VA)
   - "SUBJECTIVE: Patient presents for routine follow-up of hypertension and diabetes. Reports good medication compliance. Blood sugars have been running 120-140 mg/dL..."
   - Type: Primary Care Follow-up

2. **2025-12-15 Cardiology Consult** by Dr. Emily Johnson, MD (Atlanta VA)
   - "REASON FOR CONSULT: Evaluate for coronary artery disease. Patient with chest pain on exertion. HISTORY OF PRESENT ILLNESS: 68-year-old male with HTN, DM, hyperlipidemia..."
   - Type: Specialty Consultation

3. **2025-11-20 Discharge Summary** by Dr. Michael Williams, MD (Bay Pines VA)
   - "ADMISSION DATE: 11/17/2025. DISCHARGE DATE: 11/20/2025. ADMITTING DIAGNOSIS: Acute exacerbation of COPD. HOSPITAL COURSE: Patient admitted with dyspnea and productive cough..."
   - Type: Hospital Discharge

Data sources: PostgreSQL (demographics, medications, vitals, allergies, encounters, clinical notes - 106 total notes)
```

### 4.5 Use Case 5: Note-Specific Queries (Phase 4)

**User Prompt:**
_"What did the cardiology consult recommend?"_

**Agent Flow:**
1. Parse intent: User wants specific information from a clinical note
2. Invoke tool: `get_clinical_notes_summary(patient_icn, note_type="Consults", days=90)`
3. Tool logic:
   - Query clinical notes filtered by type (Consults)
   - Retrieve recent consult notes (default 90 days)
   - Extract note text, metadata, key recommendations
4. LLM analyzes note content and extracts relevant information
5. Return: Specific answer from note with citation

**Example Response:**
```
**Cardiology Consult Recommendations (12/15/2025)**

The cardiology consult by Dr. Emily Johnson on 12/15/2025 made the following recommendations:

1. **Diagnostic Testing:**
   - Schedule exercise stress test (or pharmacologic stress if unable to exercise)
   - Echocardiogram to assess left ventricular function
   - Lipid panel and HbA1c (due to diabetes)

2. **Medication Changes:**
   - Started metoprolol 25mg twice daily (beta-blocker for angina)
   - Continue aspirin 81mg daily
   - Optimize statin therapy (atorvastatin 40mg is appropriate)

3. **Follow-up:**
   - Return to cardiology in 2 weeks after stress test results
   - Patient education on chest pain recognition and when to seek emergency care
   - Encouraged cardiac rehabilitation referral if stress test positive

4. **Risk Factors:**
   - Emphasized diabetes control (target HbA1c < 7%)
   - Smoking cessation counseling (patient denies current smoking)
   - Weight management (BMI 27.4, encouraged 5-10 lb weight loss)

**Clinical Context:**
Patient presented with exertional chest pain, concerning for possible coronary artery disease. Multiple cardiac risk factors present: age, male, HTN, DM, hyperlipidemia.

Data source: Clinical Notes - Cardiology Consult (12/15/2025) by Dr. Emily Johnson, MD
```

**Additional Example Queries Enabled:**
- "What was the reason for the hospital admission in November?"
- "Show me imaging reports from the last 6 months"
- "What medications were mentioned in the discharge summary?"
- "Has the patient seen a specialist recently?"

### 4.6 Use Case 6: Vaccination Compliance and Gap Analysis (Phase 7) **_PENDING_**

**User Prompts:**
- _"What vaccines has this patient received?"_
- _"Is the patient up to date on COVID-19 vaccinations?"_
- _"What immunizations are due based on CDC guidelines?"_
- _"Has the patient completed the Shingrix series?"_

**Agent Flow:**
1. Parse intent: User wants immunization history or compliance check
2. Invoke appropriate tool:
   - `get_immunization_history(patient_icn)` for history queries
   - `check_vaccine_compliance(patient_icn, age)` for compliance/gap analysis
   - `forecast_next_dose(patient_icn, cvx_code)` for series status
3. Tool logic:
   - Query PostgreSQL immunizations (138 records, 8 patients)
   - Check against CDC ACIP age-based guidelines
   - Calculate next due dates for incomplete series
   - Flag high-priority missing vaccines (elderly: pneumococcal, Shingrix)
4. LLM synthesizes findings with clinical context
5. Return: Vaccination summary with recommendations

**Example Response (Compliance Check for 68-year-old patient):**
```
**Immunization Status for Patient (Age 68)**

**Completed Vaccinations:**
- COVID-19: Primary series complete (2 doses Pfizer, CVX 208)
  - Dose 1: 2021-01-15
  - Dose 2: 2021-02-05
  - Booster: 2022-09-10
- Influenza: Last received 2024-09-15 (current season)
- Tetanus/Diphtheria: 2018-03-20 (booster due ~2028)

**Incomplete Series (⚠️ Requires Follow-up):**
- **Shingrix (CVX 187):** 1 of 2 doses received
  - Dose 1: 2024-06-10
  - **Next due:** 2024-08-10 to 2024-12-10 (2-6 months after first dose)
  - **Priority:** HIGH - Strong CDC recommendation for adults 50+

**Missing Vaccines (⚠️ Recommended for Age Group):**
- **Pneumococcal PPSV23 (CVX 033):** Not on record
  - **Reason:** Recommended for all adults 65+
  - **Priority:** HIGH - Protects against pneumococcal pneumonia

**Adverse Reactions:**
- None documented in patient history

**Recommendations:**
1. **Schedule Shingrix dose 2** - Patient is overdue (within 2-6 month window)
2. **Administer Pneumococcal PPSV23** - Age-appropriate vaccine missing
3. **Continue annual influenza vaccine** - Currently up-to-date

**Compliance Summary:**
Patient (age 68) has 2 vaccine gaps requiring attention: 1 incomplete series (Shingrix) and 1 missing age-appropriate vaccine (Pneumococcal). Recommend scheduling both at next visit.

Data source: PostgreSQL immunizations (24 vaccines on record), CDC ACIP guidelines (age 65+ recommendations)
```

**Additional Example Queries Enabled:**
- "Does this 68-year-old patient need pneumococcal vaccine?" → `check_vaccine_compliance()`
- "When is the next Shingrix dose due?" → `forecast_next_dose(patient_icn, "187")`
- "Has the patient had any adverse reactions to vaccines?" → `get_immunization_history()`
- "Show me all flu shots in the last 5 years" → `get_immunization_history()` with filtering

**Integration with Patient Summary:**
The `get_patient_summary()` tool will automatically include recent immunizations (last 10 vaccines, 2-year lookback) with series completion status and adverse reaction flags. This ensures immunization status is visible in comprehensive patient overviews without requiring specific queries.

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

**Current Domains (Phase 1-5):**
- Demographics (age, DOB, veteran status, primary care station)
- Medications (active prescriptions with sig)
- Vitals (most recent BP, HR, temp, weight)
- Allergies (known allergens with reactions)
- Encounters (recent 90 days)
- Clinical Notes (recent notes with previews) - Phase 4
- **Immunizations (recent vaccination history)** - Phase 7 **_PLANNED_**

**Implementation:**
```python
# ai/tools/patient_tools.py

from langchain_core.tools import tool
from ai.services.patient_context import PatientContextBuilder

@tool
async def get_patient_summary(patient_icn: str, db_session) -> str:
    """
    Retrieves comprehensive patient summary including demographics, medications,
    vitals, allergies, encounters, clinical notes, and immunizations.

    Returns formatted text suitable for LLM synthesis.
    """
    builder = PatientContextBuilder(db_session, patient_icn)

    # Gather all data (parallel if possible)
    demographics = await builder.get_demographics_summary()
    medications = await builder.get_medication_summary()
    vitals = await builder.get_vitals_summary()
    allergies = await builder.get_allergies_summary()
    encounters = await builder.get_encounters_summary()
    notes = await builder.get_notes_summary()  # Phase 4
    immunizations = await builder.get_immunizations_summary()  # Phase 7

    summary = f"""
PATIENT DEMOGRAPHICS:
{demographics}

CURRENT MEDICATIONS ({medications['count']} active):
{medications['text']}

RECENT VITALS (last 7 days):
{vitals}

ALLERGIES:
{allergies}

RECENT IMMUNIZATIONS:
{immunizations}

RECENT ENCOUNTERS (last 90 days):
{encounters}

RECENT CLINICAL NOTES (last 90 days):
{notes}

Data sources: PostgreSQL (demographics, medications, vitals, allergies, immunizations, encounters, clinical_notes)
"""

    return summary.strip()
```

**Phase 7 Enhancement Note:**
Immunizations will be added to comprehensive patient summaries. Shows last 10 vaccines with:
- Vaccine name and administered date
- Series completion status (e.g., "2 of 2 complete" or "1 of 2 INCOMPLETE")
- Adverse reaction flags
- Critical for identifying care gaps (e.g., elderly patients missing pneumococcal vaccine)

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

### 6.5 Tool: get_clinical_notes_summary (Phase 4)

**Purpose:** Retrieve and summarize clinical notes for a patient with optional filtering

**Implementation:**
```python
# ai/tools/notes_tools.py

from langchain_core.tools import tool
from typing import Annotated, Optional
from app.db.notes import get_recent_notes, get_all_notes

@tool
def get_clinical_notes_summary(
    patient_icn: Annotated[str, "Patient ICN (Integrated Care Number)"],
    note_type: Annotated[Optional[str], "Note type filter: 'all', 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging'"] = None,
    days: Annotated[Optional[int], "Number of days to look back (default 90)"] = 90,
    limit: Annotated[Optional[int], "Maximum number of notes to return (default 5)"] = 5
) -> str:
    """
    Retrieve recent clinical notes for a patient with optional filtering.

    Provides narrative clinical context including SOAP documentation,
    consultant recommendations, discharge summaries, and imaging reports.

    Args:
        patient_icn: Patient ICN
        note_type: Optional filter by note class ('Progress Notes', 'Consults', etc.)
        days: Number of days to look back (default 90)
        limit: Maximum notes to return (default 5, max 10 for performance)

    Returns:
        Formatted string with note summaries including type, date, author, and preview text
    """
    from app.db.notes import get_all_notes

    # Query notes with filters
    result = get_all_notes(
        icn=patient_icn,
        note_class=note_type or 'all',
        date_range=days,
        limit=min(limit, 10),  # Cap at 10 for performance
        offset=0
    )

    notes = result["notes"]

    if not notes:
        return f"No clinical notes found for this patient in the last {days} days."

    # Format notes for LLM
    output = f"**Clinical Notes Summary (Last {days} days)**\n"
    output += f"Found {len(notes)} note(s)\n\n"

    for idx, note in enumerate(notes, 1):
        output += f"{idx}. **{note['reference_datetime'][:10]} {note['document_class']}**\n"
        output += f"   - Author: {note['author_name'] or 'Unknown'}\n"
        output += f"   - Facility: {note['facility_name'] or 'N/A'}\n"
        output += f"   - Title: {note['document_title']}\n"

        if note.get('text_preview'):
            output += f"   - Preview: {note['text_preview']}...\n"

        output += "\n"

    output += f"Data source: PostgreSQL clinical_notes table ({result['pagination']['total_count']} total notes for this patient)"

    return output
```

**Usage Examples:**
```python
# Get all recent notes (last 90 days, limit 5)
get_clinical_notes_summary("ICN100001")

# Get recent consult notes only
get_clinical_notes_summary("ICN100001", note_type="Consults", days=180)

# Get imaging reports from last 6 months
get_clinical_notes_summary("ICN100001", note_type="Imaging", days=180, limit=3)
```

**Performance Considerations:**
- Default limit of 5 notes balances context richness vs LLM token usage
- Max limit of 10 notes (~20,000 tokens) to stay within GPT-4 context window
- Text preview (200 chars) used for summaries; full text available via separate query if needed
- Query time: <100ms for filtered note retrieval

---

### 6.6 Immunization Tools (Phase 7) **_PENDING_**

**Status:** Pending implementation (Immunizations domain UI complete as of 2026-01-14)

**Purpose:** Enable AI to query vaccination history, check CDC guideline compliance, and identify care gaps

**Key AI Capabilities:**
1. Query patient vaccination history with CVX codes
2. Check compliance against CDC ACIP guidelines (RAG-based future enhancement)
3. Forecast next dose due dates for multi-dose series
4. Identify vaccine gaps based on age and medical history

**Location:** `ai/tools/immunization_tools.py`

**Database Layer:** `app/db/patient_immunizations.py` (already implemented - 138 immunizations in PostgreSQL)

---

#### 6.6.1 Tool: get_immunization_history

**Purpose:** Retrieve patient's complete immunization history with CVX codes

**Implementation:**
```python
# ai/tools/immunization_tools.py
from langchain_core.tools import tool
from app.db import immunizations as db_immunizations

@tool
def get_immunization_history(patient_key: str) -> dict:
    """
    Retrieve patient's immunization history with CVX codes.

    Args:
        patient_key (str): Patient ICN

    Returns:
        dict: {
            "patient_key": str,
            "total_count": int,
            "immunizations": [
                {
                    "cvx_code": str,
                    "vaccine_name": str,
                    "administered_datetime": str,
                    "series": str,
                    "is_series_complete": bool,
                    "adverse_reaction": str (if any)
                }
            ]
        }
    """
    immunizations = db_immunizations.get_all_immunizations(patient_key, limit=100)

    return {
        "patient_key": patient_key,
        "total_count": len(immunizations),
        "immunizations": [
            {
                "cvx_code": i["cvx_code"],
                "vaccine_name": i["vaccine_name"],
                "administered_datetime": i["administered_datetime"],
                "series": i["series"],
                "is_series_complete": i["is_series_complete"],
                "adverse_reaction": i["adverse_reaction"],
                "vaccine_group": i.get("vaccine_group")
            }
            for i in immunizations
        ]
    }
```

**Use Cases:**
- "What vaccines has this patient received?"
- "Show me the patient's flu shot history"
- "List all immunizations with CVX codes"

---

#### 6.6.2 Tool: check_vaccine_compliance

**Purpose:** Check CDC ACIP guideline compliance for patient's age

**Note:** MVP implementation uses deterministic age-based rules. Future enhancement will use RAG with CDC ACIP guidelines.

**Implementation** (abbreviated - see full helper functions below):
```python
@tool
def check_vaccine_compliance(patient_key: str, age: int) -> dict:
    """
    Check CDC ACIP compliance for patient's age and vaccination history.

    Args:
        patient_key (str): Patient ICN
        age (int): Patient age in years

    Returns:
        dict: {
            "patient_key": str,
            "age": int,
            "compliance_summary": str,
            "missing_vaccines": [{"cvx_code", "vaccine_name", "reason", "priority"}],
            "incomplete_series": [{"cvx_code", "vaccine_name", "doses_received", "doses_required", "next_due_date"}]
        }
    """
    # Get patient's immunization history
    history = get_immunization_history(patient_key)
    cvx_received = {i["cvx_code"] for i in history["immunizations"]}

    missing_vaccines = []
    incomplete_series = []

    # Age-based recommendations (age >= 65)
    if age >= 65:
        # Pneumococcal PPSV23 (CVX 033)
        if "033" not in cvx_received:
            missing_vaccines.append({
                "cvx_code": "033",
                "vaccine_name": "Pneumococcal PPSV23",
                "reason": "Recommended for adults 65+",
                "priority": "HIGH"
            })

        # Shingrix (CVX 187) - 2-dose series
        shingrix_series = db_immunizations.get_vaccine_series_status(patient_key, "187")
        if shingrix_series["doses_received_count"] < 2:
            if shingrix_series["doses_received_count"] == 0:
                missing_vaccines.append({
                    "cvx_code": "187",
                    "vaccine_name": "Shingrix",
                    "reason": "Recommended for adults 50+ (2-dose series)",
                    "priority": "HIGH"
                })
            else:
                incomplete_series.append({
                    "cvx_code": "187",
                    "vaccine_name": "Shingrix",
                    "doses_received": shingrix_series["doses_received_count"],
                    "doses_required": 2,
                    "next_due_date": _calculate_next_due_date(shingrix_series, interval_months=2)
                })

    # Annual flu vaccine check
    flu_cvx_codes = ["088", "135", "140", "141", "144", "158", "161"]
    flu_vaccines = [i for i in history["immunizations"] if i["cvx_code"] in flu_cvx_codes]
    if flu_vaccines:
        most_recent_flu = max(flu_vaccines, key=lambda x: x["administered_datetime"])
        months_since = _months_since(most_recent_flu["administered_datetime"])
        if months_since >= 12:
            missing_vaccines.append({
                "cvx_code": "141",
                "vaccine_name": "Influenza, seasonal",
                "reason": f"Last flu vaccine was {months_since} months ago",
                "priority": "MEDIUM"
            })
    else:
        missing_vaccines.append({
            "cvx_code": "141",
            "vaccine_name": "Influenza, seasonal",
            "reason": "No flu vaccine on record (recommended annually)",
            "priority": "MEDIUM"
        })

    compliance_summary = _generate_compliance_summary(missing_vaccines, incomplete_series, age)

    return {
        "patient_key": patient_key,
        "age": age,
        "compliance_summary": compliance_summary,
        "missing_vaccines": missing_vaccines,
        "incomplete_series": incomplete_series
    }
```

**Helper Functions:**
```python
def _determine_age_group(age: int) -> str:
    if age < 2: return "infant"
    elif age < 18: return "child"
    elif age < 65: return "adult"
    else: return "older_adult"

def _calculate_next_due_date(series_status: dict, interval_months: int) -> str:
    if not series_status["doses_received"]:
        return "Now"
    last_dose = series_status["doses_received"][-1]
    last_date = datetime.fromisoformat(last_dose["administered_datetime"])
    next_due = last_date + timedelta(days=interval_months * 30)
    return next_due.strftime("%Y-%m-%d")

def _months_since(datetime_str: str) -> int:
    date = datetime.fromisoformat(datetime_str)
    now = datetime.now()
    return (now.year - date.year) * 12 + (now.month - date.month)

def _generate_compliance_summary(missing, incomplete, age) -> str:
    total_gaps = len(missing) + len(incomplete)
    if total_gaps == 0:
        return f"Patient (age {age}) appears up-to-date on age-appropriate vaccinations."
    summary_parts = []
    if missing: summary_parts.append(f"{len(missing)} missing vaccines")
    if incomplete: summary_parts.append(f"{len(incomplete)} incomplete series")
    return f"Patient (age {age}) has {' and '.join(summary_parts)}. Review recommended."
```

**Use Cases:**
- "Is the patient up to date on COVID-19 vaccinations?"
- "What immunizations are due based on CDC guidelines?"
- "Does this 68-year-old patient need pneumococcal vaccine?"

---

#### 6.6.3 Tool: forecast_next_dose

**Purpose:** Calculate next dose due date for multi-dose vaccine series

**Implementation:**
```python
@tool
def forecast_next_dose(patient_key: str, cvx_code: str) -> dict:
    """
    Calculate when next dose is due for a multi-dose vaccine series.

    Args:
        patient_key (str): Patient ICN
        cvx_code (str): CVX code for vaccine

    Returns:
        dict: {
            "cvx_code": str,
            "vaccine_name": str,
            "doses_received": int,
            "doses_required": int,
            "series_complete": bool,
            "next_due_date": str,
            "interval_description": str
        }
    """
    series_status = db_immunizations.get_vaccine_series_status(patient_key, cvx_code)
    ref_vaccine = _get_ref_vaccine(cvx_code)

    if not ref_vaccine:
        return {"error": f"Vaccine CVX {cvx_code} not found in reference table"}

    doses_required = _parse_doses_required(ref_vaccine.get("typical_series_pattern", ""))
    doses_received = series_status["doses_received_count"]
    series_complete = series_status["series_complete"]

    if series_complete or doses_received >= doses_required:
        next_due_date = "Series complete"
        interval_description = "No additional doses needed"
    else:
        # Standard intervals (MVP)
        interval_map = {
            "187": {"months": 2, "description": "2-6 months after first dose"},  # Shingrix
            "208": {"months": 1, "description": "3-8 weeks after first dose"},  # COVID-19 Pfizer
            "213": {"months": 1, "description": "4 weeks after first dose"},    # COVID-19 Moderna
            "043": {"months": 1, "description": "1-2 months after previous dose"}, # Hep B
        }
        interval = interval_map.get(cvx_code, {"months": 6, "description": "Standard interval"})

        if series_status["doses_received"]:
            last_dose = series_status["doses_received"][-1]
            last_date = datetime.fromisoformat(last_dose["administered_datetime"])
            next_due = last_date + timedelta(days=interval["months"] * 30)
            next_due_date = next_due.strftime("%Y-%m-%d")
        else:
            next_due_date = "Now"

        interval_description = interval["description"]

    return {
        "cvx_code": cvx_code,
        "vaccine_name": ref_vaccine["vaccine_name"],
        "doses_received": doses_received,
        "doses_required": doses_required,
        "series_complete": series_complete,
        "next_due_date": next_due_date,
        "interval_description": interval_description
    }
```

**Helper Functions:**
```python
def _get_ref_vaccine(cvx_code: str) -> dict:
    from app.db.connection import get_db_connection
    from sqlalchemy import text
    conn = get_db_connection()
    query = text("SELECT * FROM reference.vaccine WHERE cvx_code = :cvx_code")
    result = conn.execute(query, {"cvx_code": cvx_code})
    row = result.fetchone()
    if row:
        return {
            "cvx_code": row[0],
            "vaccine_name": row[1],
            "vaccine_short_name": row[2],
            "vaccine_group": row[3],
            "typical_series_pattern": row[4]
        }
    return None

def _parse_doses_required(pattern: str) -> int:
    if "2-dose" in pattern: return 2
    elif "3-dose" in pattern: return 3
    elif "4-dose" in pattern: return 4
    elif "5-dose" in pattern: return 5
    elif "Annual" in pattern or "Booster" in pattern or "Single" in pattern: return 1
    return 1
```

**Use Cases:**
- "When is the next Shingrix dose due?"
- "Has the patient completed the Shingrix series?"
- "Is the COVID-19 primary series complete?"

---

#### 6.6.4 System Prompts Integration

**File:** `ai/prompts/system_prompts.py`

Add immunization-specific context to the system prompt:

```python
IMMUNIZATION_CONTEXT = """
You have access to the patient's complete immunization history through the following tools:

1. **get_immunization_history**: Retrieve all vaccines the patient has received with CVX codes
2. **check_vaccine_compliance**: Check if patient is up-to-date based on CDC ACIP guidelines
3. **forecast_next_dose**: Calculate when the next dose of a multi-dose series is due

When discussing immunizations:
- Always reference CVX codes for precision
- Highlight incomplete vaccine series as they may require follow-up
- Note any adverse reactions for safety awareness
- Use CDC ACIP guidelines for age-appropriate recommendations
- Distinguish between routine vaccines (childhood, adult) and situational vaccines (travel, occupational)
- For multi-dose series (e.g., Shingrix, COVID-19, Hepatitis B), calculate and display due dates

Example response format:
"Based on the patient's immunization history, they have received [X] vaccines. The patient completed the COVID-19 primary series (CVX 208) with 2 doses, most recently on [date]. However, the Shingrix series (CVX 187) is incomplete with only 1 of 2 doses received. The second dose is due approximately [X months] after the first dose on [calculated date]."
"""
```

---

#### 6.6.5 RAG Enhancement (Future - Phase 7+)

**Deferred to Phase 7+:**
- Vector embeddings of CDC "Pink Book" ACIP schedules
- Semantic search for vaccine contraindications
- Entity extraction from clinical notes related to vaccinations
- Vaccine hesitancy pattern detection

**Why deferred:**
- MVP can use deterministic rules for common age-based vaccines
- RAG requires significant data preparation (CDC documents → chunks → embeddings)
- Clinical accuracy is critical; deterministic rules are more testable

---

**Integration with Existing Tools:**
- `get_patient_summary()` will automatically include recent immunizations (Phase 7 enhancement)
- Immunization-specific tools available for targeted queries
- Agent autonomously chooses appropriate tool based on query intent

**LangGraph Agent Integration:**
- User submits query via `/insight`
- Agent analyzes query and selects appropriate immunization tool(s)
- Tools execute and return structured data
- Agent synthesizes response with clinical context

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

### Phase 4: Clinical Notes Integration (Week 4) ✅ **COMPLETE**

**Prerequisites:**
- ✅ Clinical Notes domain fully implemented (106 notes in PostgreSQL)
- ✅ Clinical Notes UI complete (dashboard widget + full page)
- ✅ Query functions available in `app/db/notes.py`
- ✅ AI-ready schema columns present (embedding_vector, ai_summary, key_entities)
- ✅ LangGraph agent infrastructure operational (Phases 1-3 complete)

**Estimated Time:** 8-11 hours over 2 weeks (4-6 hours/week)

---

**Day 1-2: Enhance Patient Summary Tool with Clinical Notes** ✅ **COMPLETE**

**Tasks:**
1. ✅ Update `ai/services/patient_context.py` → `PatientContextBuilder`:
   - ✅ Add `get_notes_summary()` method
   - ✅ Call `app.db.notes.get_recent_notes_for_ai(icn, limit=3, preview_length=500)`
   - ✅ Format notes: `[Date] [Type] by [Author] ([Facility]): [Preview (500 chars)]...`
   - ✅ Add to existing `build_comprehensive_summary()` output (after Encounters section)

2. ✅ Update `ai/tools/patient_tools.py` → `get_patient_summary()`:
   - ✅ No code changes (PatientContextBuilder handles it)
   - ✅ Tool automatically includes notes in output

3. ✅ Test enhanced patient summary:
   - ✅ Verify notes appear in summary for patients with clinical notes
   - ✅ Verify graceful handling when no notes exist
   - ✅ Check token usage (< 2K tokens total with notes included)

**Deliverables:**
- [x] Updated `PatientContextBuilder.get_notes_summary()` method
- [x] Enhanced `get_patient_summary()` output includes recent notes
- [x] Manual testing with 3-5 patients (with/without notes)

**Estimated Time:** 2-3 hours

**Example Output (Enhanced):**
```
Recent Encounters:
- Observation on 2025-11-30 at VA Atlanta

Recent Clinical Notes (Last 3):
- 2025-12-28 Progress Note: "SUBJECTIVE: Patient presents for follow-up of hypertension and diabetes. Reports good medication compliance. Blood sugars running 120-140 mg/dL..."
- 2025-12-15 Cardiology Consult: "REASON FOR CONSULT: Evaluate for coronary artery disease. Patient with chest pain on exertion..."
- 2025-11-20 Discharge Summary: "ADMISSION DATE: 11/17/2025. DISCHARGE DATE: 11/20/2025. ADMITTING DIAGNOSIS: Acute exacerbation of COPD..."
```

---

**Day 3-4: Create get_clinical_notes_summary() Tool** ✅ **COMPLETE**

**Tasks:**
1. ✅ Create new file: `ai/tools/notes_tools.py`:
   - ✅ Implement `get_clinical_notes_summary()` tool (see Section 6.5 for full code)
   - ✅ Parameters: `patient_icn`, `note_type` (optional), `days` (default 90), `limit` (default 5)
   - ✅ Wraps `app.db.notes.get_all_notes()` with formatting
   - ✅ Include note type, date, title, author, cosigner, facility, status, preview text (500 chars)

2. ✅ Update `ai/tools/__init__.py`:
   - ✅ Import new tool: `from ai.tools.notes_tools import get_clinical_notes_summary`
   - ✅ Add to `ALL_TOOLS` list (4 tools total)
   - ✅ Update `__all__` exports

3. ✅ Test tool independently:
   - ✅ Test with `note_type` filter (Consults, Progress Notes, Discharge Summaries, Imaging)
   - ✅ Test date range parameter (30, 90, 180 days)
   - ✅ Test limit parameter (3, 5, 10 notes)
   - ✅ Verify performance (<200ms query time)

4. ✅ Test LangGraph agent integration:
   - ✅ Ask: "What did the cardiology consult say?"
   - ✅ Ask: "Show me recent progress notes"
   - ✅ Ask: "What imaging studies were done recently?"
   - ✅ Verify agent autonomously invokes correct tool with appropriate parameters

**Deliverables:**
- [x] New file `ai/tools/notes_tools.py` with `get_clinical_notes_summary()` tool
- [x] Updated `ai/tools/__init__.py` (ALL_TOOLS now has 4 tools)
- [x] LangGraph agent successfully invokes new tool for note-specific queries
- [x] Manual testing with 5-7 sample queries

**Estimated Time:** 3-4 hours

**Example Queries Enabled:**
- "What did the last cardiology consult recommend?"
- "Summarize the discharge summary from November"
- "What imaging studies were done in the last 6 months?"
- "Has the patient seen a specialist recently?"
- "Show me progress notes from the last month"

---

**Day 5: System Prompt Update + Testing** ✅ **COMPLETE**

**Tasks:**
1. ✅ Create `ai/prompts/system_prompts.py`:
   - ✅ Create centralized system prompts module (new architecture decision)
   - ✅ Add comprehensive clinical insights system prompt
   - ✅ Include clinical notes in available tools list (`get_clinical_notes_summary`)
   - ✅ Add guidance on when to use notes tool vs patient summary
   - ✅ Include safety & privacy guidelines, response formatting standards

2. ✅ Update suggested questions in `app/routes/insight.py`:
   - ✅ Replace one existing question with note-based query
   - ✅ New question: "What did recent clinical notes say about this patient?"

3. ✅ Comprehensive integration testing:
   - ✅ Test with 5-10 patients (variety of note types)
   - ✅ Test combined queries (e.g., "Check DDIs and summarize recent notes")
   - ✅ Test edge cases (no notes, single note, 10+ notes)
   - ✅ Verify performance (<5 sec p90 response time)
   - ✅ Check token usage and LLM costs

4. ✅ Documentation updates:
   - ✅ Update this document (mark Phase 4 complete)
   - ✅ Add Phase 4 notes to `app/README.md`
   - ✅ Update `CLAUDE.md` with new AI capabilities

**Deliverables:**
- [x] Created system prompts architecture (`ai/prompts/system_prompts.py`)
- [x] Updated system prompt includes clinical notes guidance
- [x] Updated suggested questions in UI
- [x] Comprehensive testing checklist completed
- [x] Documentation updated
- [x] Phase 4 marked complete ✅

**Estimated Time:** 3-4 hours

---

**Phase 4 Success Criteria:**
- [x] `get_patient_summary()` automatically includes recent clinical notes (last 3)
- [x] New `get_clinical_notes_summary()` tool available and functional
- [x] LangGraph agent autonomously invokes notes tool for relevant queries
- [x] Response time < 5 seconds for note-based queries (p90)
- [x] Token usage remains reasonable (< 2K tokens for summaries, < 5K for targeted queries)
- [x] Manual testing with 10+ patients confirms accurate note retrieval
- [x] UI suggested questions include at least one note-based query

---

**Phase 4 Deliverables Summary:**
- ✅ Created system prompts architecture (`ai/prompts/system_prompts.py`)
- ✅ Added AI notes configuration to `config.py` (5 configurable parameters)
- ✅ Created `get_recent_notes_for_ai()` with 500-char previews
- ✅ Enhanced `PatientContextBuilder` with notes integration (2-3 hours)
- ✅ New `get_clinical_notes_summary()` tool (3-4 hours)
- ✅ Updated system prompts and UI (1-2 hours)
- ✅ Comprehensive testing and documentation (2-2 hours)
- ✅ **Total: 8-11 hours completed successfully**

---

### Post-Phase 4 UX & Configuration Enhancements ✅ **COMPLETE**

**Completion Date:** 2026-01-03
**Total Time:** 4-5 hours

Following Phase 4 completion, several UX improvements and configuration enhancements were implemented to improve usability, maintainability, and clinical data completeness.

---

#### **Enhancement 1: Suggested Questions Modal Refactoring** ✅ **COMPLETE**

**Problem:** Suggested question chips consumed vertical space on initial page load and were no longer visible after first message submission.

**Solution:** Replaced static chips with modal-based suggested questions accessible anytime during conversation.

**Implementation:**

1. **Created Suggested Questions Modal** (1 hour)
   - Location: `app/templates/partials/suggested_questions_modal.html`
   - Pattern: Follows existing `patient_flags_modal.html` structure
   - Features:
     - Scrollable list of suggested questions (max-height: 60vh)
     - Each question is a clickable button
     - Clicking a question populates textarea (does not auto-submit)
     - User can edit question before submitting
   - Integration: Uses existing app.js modal handlers (data-modal-open/close)

2. **Added Sparkle Icon Button** (30 min)
   - Location: Left of "Ask a question..." textarea in `app/templates/insight.html`
   - Icon: `fa-solid fa-sparkles` (Font Awesome)
   - Styling: 36px × 36px, gradient background (cyan to purple), gold icon
   - Tooltip: "Suggested questions"
   - Layout: `[Sparkle Icon] [spacing] [Textarea] [Submit Button]`
   - Opens modal via `data-modal-open="suggested-questions-modal"`

3. **Removed Suggested Question Chips** (15 min)
   - Deleted chips section from `insight.html` (lines 78-99)
   - Removed chip CSS (retain for potential future use)
   - Simplified page layout

4. **Updated JavaScript** (30 min)
   - Created `selectSuggestedQuestion(question)` function
   - Populates textarea with selected question
   - Closes modal
   - Focuses textarea for editing
   - Retained `hideSuggestions()` as no-op for HTMX compatibility

**Benefits:**
- ✅ Cleaner initial page layout (no chips cluttering interface)
- ✅ Suggested questions accessible anytime (not just on initial load)
- ✅ User control: populate textarea but don't auto-submit
- ✅ Consistent with modal patterns across med-z1

**Files Modified:**
- `app/templates/insight.html` - Removed chips, added sparkle button, included modal
- `app/templates/partials/suggested_questions_modal.html` (NEW) - Modal structure
- `app/static/styles.css` - Added sparkle button and modal list styles

---

#### **Enhancement 2: Suggested Questions Configuration Refactoring** ✅ **COMPLETE**

**Problem:** Suggested questions were hardcoded in `app/routes/insight.py`, making them difficult to maintain and update.

**Solution:** Centralized suggested questions in dedicated module following system prompts pattern.

**Implementation:**

1. **Created Suggested Questions Module** (45 min)
   - Location: `ai/prompts/suggested_questions.py`
   - Pattern: Matches `ai/prompts/system_prompts.py` architecture
   - Content:
     - `SUGGESTED_QUESTIONS` list (simple Python list)
     - Design principles documented in docstring
     - Clear instructions for modifying questions

2. **Simplified from Initial Over-Engineering** (15 min)
   - Initially implemented with function wrapper and future-proofing
   - User feedback: "Remove future scope, keep it simple"
   - Refactored to single list constant (no function wrapper)
   - Removed category support, rotation, A/B testing complexity

3. **Updated Imports** (15 min)
   - Updated `ai/prompts/__init__.py` to export `SUGGESTED_QUESTIONS`
   - Updated `app/routes/insight.py` to import constant directly
   - Simplified usage: `suggested_questions = SUGGESTED_QUESTIONS`

**Current Questions (as of 2026-01-03):**
```python
SUGGESTED_QUESTIONS = [
    "What are the key clinical risks for this patient?",
    "Are there any drug-drug interaction concerns?",
    "Summarize this patient's recent clinical activity.",
    "What did recent clinical notes say about this patient?",
    "Has the patient seen cardiology?",
    "What imaging studies were done recently?",
]
```

**Benefits:**
- ✅ Single source of truth for suggested questions
- ✅ Easy to modify (edit one file)
- ✅ Follows established pattern (system_prompts.py)
- ✅ Simple architecture (no over-engineering)
- ✅ AI content separated from technical config

**Files Modified:**
- `ai/prompts/suggested_questions.py` (NEW) - Question list
- `ai/prompts/__init__.py` - Export SUGGESTED_QUESTIONS
- `app/routes/insight.py` - Import and use constant
- `app/README.md` - Documented pattern

---

#### **Enhancement 3: Chat Button Styling Consistency** ✅ **COMPLETE**

**Problem:** Submit button (paper plane) had default primary button styling, inconsistent with new sparkle button.

**Solution:** Unified button styling using Insights branding colors (matches active sidebar menu).

**Implementation:**

1. **Sparkle Button Styling** (15 min)
   - Size: 36px × 36px (matches chat avatar icons)
   - Background: `linear-gradient(135deg, #06b6d4, #4f46e5)` (cyan to purple)
   - Icon Color: `gold` (yellow sparkles)
   - Hover: Opacity + subtle scale effect
   - Vertical alignment with chat robot avatars

2. **Submit Button Styling** (15 min)
   - Updated to match sparkle button
   - Added `chat-submit-btn` class
   - Size: 36px × 36px (was 48px, now consistent)
   - Background: Same gradient as sparkle button
   - Icon Color: `gold` (yellow paper plane)
   - Tooltip: "Submit question"

**Visual Result:**
```
Chat Avatar (36px)     Sparkle (36px)    [Textarea]    Submit (36px)
     🤖                     ✨                              ✈️
  (robot icon)         (gold sparkles)                (gold plane)
   Gradient               Gradient                      Gradient
```

**Benefits:**
- ✅ Consistent visual language across all chat interface buttons
- ✅ Insights branding throughout (matches active sidebar menu colors)
- ✅ Perfect vertical alignment with chat avatars
- ✅ Professional, cohesive appearance

**Files Modified:**
- `app/static/styles.css` - Added `.chat-sparkle-btn` and `.chat-submit-btn` styles
- `app/templates/insight.html` - Added tooltip to submit button

---

#### **Enhancement 4: Patient Demographics - Date of Birth Integration** ✅ **COMPLETE**

**Problem:** AI agent could not answer "What is the patient's date of birth?" despite DOB being available in database.

**Root Cause:** `PatientContextBuilder.get_demographics_summary()` used calculated age but ignored `dob` field from `get_patient_demographics()`.

**Solution:** Enhanced demographics summary to include both age and date of birth.

**Implementation:**

1. **Updated Demographics Summary** (15 min)
   - Location: `ai/services/patient_context.py`
   - Method: `get_demographics_summary()`
   - Change: Added DOB field extraction and formatting
   - Format: `"45-year-old male veteran (DOB: 1979-05-15), service-connected..."`

2. **Updated Documentation** (10 min)
   - Updated method docstring examples
   - Updated class-level examples

**Before:**
```
Date of Birth/Age: The patient is 45 years old. The exact date of birth is not provided in the summary.
```

**After:**
```
Date of Birth: 1979-05-15
Age: 45 years old
Gender: Male
```

**Benefits:**
- ✅ Complete demographic information available to AI
- ✅ Answers DOB queries accurately
- ✅ Graceful fallback if DOB missing

**Files Modified:**
- `ai/services/patient_context.py` - Enhanced `get_demographics_summary()`

---

**Post-Phase 4 Enhancement Summary:**

**Total Enhancements:** 4 completed
**Total Time:** 4-5 hours
**Completion Date:** 2026-01-03

**Deliverables:**
1. ✅ Suggested questions modal with sparkle icon button
2. ✅ Centralized suggested questions configuration module
3. ✅ Unified chat button styling (sparkle + submit)
4. ✅ Enhanced demographics with date of birth

**Impact:**
- Improved UX: Cleaner interface, persistent access to suggested questions
- Improved maintainability: Centralized configuration, clear patterns
- Improved visual consistency: Unified branding across all buttons
- Improved data completeness: AI can now answer DOB queries

---

**Post-Phase 4 Opportunities (Phase 5+):**
Once Phase 4 is stable, consider these advanced enhancements:
1. **Care Gap Analysis Tool** - Extract unfulfilled recommendations from notes
2. **Clinical Timeline Generator** - Chronological patient story from notes + structured data
3. **Semantic Note Search** - Vector embeddings for similarity search (use `embedding_vector` column)
4. **AI-Generated Note Summaries** - Populate `ai_summary` column via ETL
5. **Entity Extraction** - Extract medications, diagnoses, procedures from narrative text

See **Clinical Notes Enhancement Opportunities Assessment** (Section 14.3) for detailed specifications.

---

### Phase 5: Conversation Transcript Download (MVP) ✅ **COMPLETE**

**Prerequisites:**
- ✅ Clinical Insights chat interface operational (Phase 2 complete)
- ✅ Chat messages rendered in DOM via HTMX
- ✅ Patient context available on page
- ✅ Existing modal patterns established (Patient Flags modal)

**Estimated Time:** 3-4 hours

**Overview:**
Enable clinicians to download AI Clinical Insights conversation transcripts to their local computer for clinical documentation, reference, or record-keeping purposes. This MVP implements client-side file generation (no server storage) in two formats: plaintext (.txt) and markdown (.md).

**Design Philosophy:**
- **Privacy-First:** Files generated client-side (never touches server), minimizing PHI exposure
- **Simple & Practical:** Text-based formats (no PDF/Word complexity in MVP)
- **User Control:** Explicit download action with PHI warning
- **Session-Only:** Captures current page session (lost on refresh - acceptable for MVP)

---

#### **Day 1: PHI Warning Modal + Download Button (1.5 hours)** ✅ **COMPLETE**

**Tasks:**

1. **Create PHI Warning Modal** ✅ (45 min)
   - Location: `app/templates/partials/transcript_download_modal.html`
   - Pattern: Follow existing `patient_flags_modal.html` structure
   - Content: PHI/HIPAA handling warning with 5 acknowledgment items
   - Actions: [Cancel] [Download Plain Text (.txt)] [Download Markdown (.md)]
   - **Implementation Notes:**
     - Used standard black bullet points (`fa-circle`, 0.4rem) instead of green checkmarks
     - Reduced vertical spacing (`line-height: 1.5`, `margin-bottom: 0.25rem`) to eliminate scrolling
     - Shortened disclaimer text: "All AI-generated insights must be verified before making clinical decisions."

2. **Add Download Button to Insights Page** ✅ (30 min)
   - Location: `app/templates/insight.html` (lines 135-146)
   - Position: Below chat form, above AI disclaimer
   - **Final Design Decision:** Single "Download Transcript" button (UX improvement)
     - Initial spec called for two buttons (Text and Markdown)
     - User feedback: Modal already offers both formats → consolidate to one button
     - Button aligned with textarea (same width, left/right alignment)
     - Reduced vertical spacing (`margin-top: 0.5rem`)

   ```html
   <!-- Transcript Download Actions -->
   <div class="transcript-download-actions">
       <button
           type="button"
           class="btn btn--secondary"
           data-modal-open="transcript-download-modal"
           title="Download conversation transcript"
       >
           <i class="fa-solid fa-download"></i>
           Download Transcript
       </button>
   </div>
   ```

   **CSS Styling** (`app/static/styles.css` lines 5105-5126):
   ```css
   /* Transcript Download Actions */
   .transcript-download-actions {
       margin-top: 0.5rem;
       margin-bottom: 1rem;
       padding-left: calc(36px + 0.75rem);  /* Sparkle button width + gap */
       padding-right: calc(36px + 0.75rem); /* Submit button width + gap */
   }

   .transcript-download-actions .btn {
       width: 100%;
   }

   @media (max-width: 768px) {
       .transcript-download-actions {
           padding-left: 0;
           padding-right: 0;
       }

       .transcript-download-actions .btn {
           width: 100%;
       }
   }
   ```

3. **Include Modal in Page** ✅ (15 min)
   - Added `{% include "partials/transcript_download_modal.html" %}` to `insight.html` (line 172)
   - Modal open/close behavior working using existing app.js handlers

**Deliverables:**
- ✅ `app/templates/partials/transcript_download_modal.html` created with optimized formatting
- ✅ Single download button added to Insights page (aligned with textarea)
- ✅ Modal opens on button click, offers both format options
- ✅ Responsive CSS styling for mobile and desktop

**Actual Time:** ~1.5 hours (including UX refinements)

---

#### **Day 2: JavaScript Transcript Generation (2-2.5 hours)** ✅ **COMPLETE**

**Tasks:**

1. **Create Transcript JavaScript Module** (2 hours)
   - Location: `app/static/transcript.js`
   - Functions:
     - `prepareTranscriptDownload(format)` - Sets download format, opens modal
     - `generatePlaintextTranscript()` - Formats chat as plaintext
     - `generateMarkdownTranscript()` - Formats chat as markdown
     - `collectChatMessages()` - Extracts messages from DOM
     - `downloadFile(content, mimeType, extension)` - Triggers browser download
     - `generateMetadata()` - Collects patient/user/timestamp data
     - `generateDisclaimer()` - Adds AI disclaimer footer

2. **Add Script to Insights Page** (15 min)
   - Include `<script src="{{ url_for('static', path='/transcript.js') }}"></script>` in `insight.html`

3. **Wire Up Modal Buttons** (30 min)
   - Connect "Download Text" button to `downloadTranscript('text')`
   - Connect "Download Markdown" button to `downloadTranscript('markdown')`
   - Close modal after download initiated

**Deliverables:**
- ✅ `app/static/transcript.js` created (~350 lines)
- ✅ Plaintext and markdown generation functional
- ✅ Browser download triggered with proper filenames
- ✅ Script integrated into `insight.html`
- ✅ Modal buttons wired to `downloadTranscript()` function

**Actual Time:** ~2 hours

**Implementation Notes:**
- Comprehensive transcript.js module with 7 core functions
- Extracts messages, metadata, and timestamps from DOM
- Generates formatted plaintext with headers and disclaimers
- Generates formatted markdown with emoji icons and structured sections
- Client-side file generation using Blob API
- Automatic modal close after download initiated

---

#### **Technical Specifications**

##### **5.1 Plaintext Format (.txt)**

**File Naming Convention:**
```
clinical_insights_ICN{patient_icn}_{timestamp}.txt
Example: clinical_insights_ICN100001_20260103_143205.txt
```

**Format Structure:**
```
========================================
AI CLINICAL INSIGHTS TRANSCRIPT
========================================

Generated: January 3, 2026 2:32:05 PM
Patient: MOORE, ROBERT (ICN: ICN100001)
Clinician: clinician.alpha@va.gov
Session ID: {browser_session_id}

========================================

[14:25:12] USER:
What are the key clinical risks for this patient?

[14:25:18] AI:
Based on the patient's clinical data, here are the key risks:

1. Drug-Drug Interactions:
   - GABAPENTIN + HYDROCODONE: Moderate severity
   - Recommendation: Monitor for increased CNS depression

2. Blood Pressure Control:
   - Recent BP: 145/92 mmHg (Stage 1 Hypertension)
   - Trend: Increasing over last 30 days
   - Recommendation: Consider medication adjustment

3. Medication Adherence:
   - 7 active prescriptions
   - Last refill gap: GABAPENTIN (14 days overdue)

Sources Checked: get_patient_summary, check_ddi_risks, analyze_vitals_trends

========================================

[14:28:45] USER:
What did recent clinical notes say about this patient?

[14:28:51] AI:
Based on recent clinical notes (last 90 days):

**Progress Note (2025-12-28)**
Author: Dr. Smith, Alexandria VAMC
Key Points:
- Patient presents for HTN/DM follow-up
- Reports good medication compliance
- Blood sugars: 120-140 mg/dL
- BP today: 145/92 (elevated)
- Plan: Increase lisinopril to 20mg daily

**Cardiology Consult (2025-12-15)**
Author: Dr. Johnson, Alexandria VAMC
Reason: Evaluate for coronary artery disease
Findings:
- Stress test: Negative for ischemia
- EKG: Normal sinus rhythm
- Recommendation: Continue current cardiac medications

Sources Checked: get_clinical_notes_summary

========================================

DISCLAIMER:
This transcript contains AI-generated clinical insights. All information
must be independently verified by qualified healthcare professionals before
making clinical decisions. This tool provides decision support, not medical
advice.

Protected Health Information (PHI):
This document contains sensitive patient information protected under HIPAA.
Handle according to VA/HIPAA data security policies. Store on encrypted
devices only. Do not transmit via unsecured channels (email, SMS).

Generated by: Med-Z1 AI Clinical Insights v1.0
https://github.com/department-of-veterans-affairs/med-z1
```

**Key Features:**
- ✅ Clear section delimiters (========)
- ✅ Timestamps for each message
- ✅ USER vs AI attribution
- ✅ Preserves multi-paragraph formatting
- ✅ Lists tools/sources checked
- ✅ Comprehensive metadata header
- ✅ PHI/HIPAA disclaimer footer

---

##### **5.2 Markdown Format (.md)**

**File Naming Convention:**
```
clinical_insights_ICN{patient_icn}_{timestamp}.md
Example: clinical_insights_ICN100001_20260103_143205.md
```

**Format Structure:**
```markdown
# AI Clinical Insights Transcript

**Generated:** January 3, 2026 2:32:05 PM
**Patient:** MOORE, ROBERT (ICN: ICN100001)
**Clinician:** clinician.alpha@va.gov
**Session ID:** {browser_session_id}

---

## [14:25:12] User Question
What are the key clinical risks for this patient?

## [14:25:18] AI Response
Based on the patient's clinical data, here are the key risks:

### 1. Drug-Drug Interactions
- **GABAPENTIN + HYDROCODONE:** Moderate severity
- **Recommendation:** Monitor for increased CNS depression

### 2. Blood Pressure Control
- **Recent BP:** 145/92 mmHg (Stage 1 Hypertension)
- **Trend:** Increasing over last 30 days
- **Recommendation:** Consider medication adjustment

### 3. Medication Adherence
- 7 active prescriptions
- Last refill gap: GABAPENTIN (14 days overdue)

*Sources Checked: get_patient_summary, check_ddi_risks, analyze_vitals_trends*

---

## [14:28:45] User Question
What did recent clinical notes say about this patient?

## [14:28:51] AI Response
Based on recent clinical notes (last 90 days):

### Progress Note (2025-12-28)
**Author:** Dr. Smith, Alexandria VAMC
**Key Points:**
- Patient presents for HTN/DM follow-up
- Reports good medication compliance
- Blood sugars: 120-140 mg/dL
- BP today: 145/92 (elevated)
- **Plan:** Increase lisinopril to 20mg daily

### Cardiology Consult (2025-12-15)
**Author:** Dr. Johnson, Alexandria VAMC
**Reason:** Evaluate for coronary artery disease
**Findings:**
- Stress test: Negative for ischemia
- EKG: Normal sinus rhythm
- **Recommendation:** Continue current cardiac medications

*Sources Checked: get_clinical_notes_summary*

---

## Disclaimer

⚠️ **AI-Generated Clinical Insights**

This transcript contains AI-generated clinical insights. All information must be independently verified by qualified healthcare professionals before making clinical decisions. This tool provides decision support, not medical advice.

### Protected Health Information (PHI)

This document contains sensitive patient information protected under HIPAA. Handle according to VA/HIPAA data security policies:
- Store on encrypted devices only
- Do not transmit via unsecured channels (email, SMS)
- Delete when no longer clinically necessary

---

*Generated by: Med-Z1 AI Clinical Insights v1.0*
*https://github.com/department-of-veterans-affairs/med-z1*
```

**Key Features:**
- ✅ Structured headings (H1/H2/H3)
- ✅ **Bold** for emphasis on key clinical terms
- ✅ *Italic* for tool attribution
- ✅ Horizontal rules (---) between sections
- ✅ Bulleted lists for clinical data
- ✅ Preserves markdown from AI responses (tables, code blocks)
- ✅ Human-readable as plain text
- ✅ Can be rendered as HTML in markdown viewers

---

##### **5.3 PHI Warning Modal Content**

**Modal Title:** ⚠️ Protected Health Information Warning

**Body Content:**
```
You are about to download a transcript containing Protected Health
Information (PHI).

By downloading this file, you acknowledge and agree to:

✓ Store the file on an encrypted, VA-approved device only
✓ NOT share via unsecured channels (email, text message, cloud storage)
✓ Delete the file when it is no longer clinically necessary
✓ Follow all VA and HIPAA data handling policies
✓ Take full responsibility for the security of this file

This transcript is for clinical reference and documentation purposes only.
All AI-generated insights must be independently verified before making
clinical decisions.

Which format would you like to download?
```

**Buttons:**
- `[Cancel]` - Close modal, no download
- `[Download Plain Text (.txt)]` - Download plaintext format
- `[Download Markdown (.md)]` - Download markdown format

---

##### **5.4 JavaScript Implementation Details**

**Core Functions:**

```javascript
// app/static/transcript.js

let pendingDownloadFormat = null;

/**
 * Prepare transcript download by setting format and opening PHI warning modal
 * @param {string} format - 'text' or 'markdown'
 */
function prepareTranscriptDownload(format) {
    pendingDownloadFormat = format;
    // Modal opens automatically via data-modal-open attribute
}

/**
 * Execute transcript download after user acknowledges PHI warning
 * Called by modal button click
 */
function downloadTranscript(format) {
    const downloadFormat = format || pendingDownloadFormat;

    if (!downloadFormat) {
        console.error('No download format specified');
        return;
    }

    let content, mimeType, extension;

    if (downloadFormat === 'text') {
        content = generatePlaintextTranscript();
        mimeType = 'text/plain';
        extension = 'txt';
    } else if (downloadFormat === 'markdown') {
        content = generateMarkdownTranscript();
        mimeType = 'text/markdown';
        extension = 'md';
    } else {
        console.error('Unknown format:', downloadFormat);
        return;
    }

    // Generate filename: clinical_insights_ICN{icn}_{timestamp}.{ext}
    const patientICN = getPatientICN();
    const timestamp = formatTimestamp(new Date());
    const filename = `clinical_insights_${patientICN}_${timestamp}.${extension}`;

    // Trigger download
    downloadFile(content, mimeType, filename);

    // Close modal
    closeModal('transcript-download-modal');

    // Reset pending format
    pendingDownloadFormat = null;
}

/**
 * Collect all chat messages from DOM
 * @returns {Array} Array of message objects {type: 'user'|'ai', text: string, timestamp: string, tools: array}
 */
function collectChatMessages() {
    const messages = [];
    const chatHistory = document.getElementById('chat-history');

    if (!chatHistory) {
        return messages;
    }

    const messageElements = chatHistory.querySelectorAll('.chat-message');

    messageElements.forEach(msgEl => {
        const isUser = msgEl.classList.contains('chat-message--user');
        const type = isUser ? 'user' : 'ai';

        // Extract message text
        const contentEl = msgEl.querySelector('.chat-message__content');
        const text = contentEl ? contentEl.textContent.trim() : '';

        // Extract timestamp (if available)
        const timestampEl = msgEl.querySelector('.chat-message__timestamp');
        const timestamp = timestampEl ? timestampEl.textContent.trim() : 'Just now';

        // Extract tools used (AI messages only)
        let tools = [];
        if (!isUser) {
            const toolsEl = msgEl.querySelector('.chat-message__tools');
            if (toolsEl) {
                const toolsText = toolsEl.textContent;
                // Parse "Sources checked: tool1, tool2, tool3"
                const match = toolsText.match(/Sources checked:\s*(.+)/);
                if (match) {
                    tools = match[1].split(',').map(t => t.trim());
                }
            }
        }

        messages.push({type, text, timestamp, tools});
    });

    return messages;
}

/**
 * Generate plaintext transcript
 * @returns {string} Formatted plaintext transcript
 */
function generatePlaintextTranscript() {
    const metadata = generateMetadata();
    const messages = collectChatMessages();
    const disclaimer = generateDisclaimer();

    let transcript = '';

    // Header
    transcript += '========================================\n';
    transcript += 'AI CLINICAL INSIGHTS TRANSCRIPT\n';
    transcript += '========================================\n\n';

    // Metadata
    transcript += `Generated: ${metadata.generated}\n`;
    transcript += `Patient: ${metadata.patientName} (ICN: ${metadata.patientICN})\n`;
    transcript += `Clinician: ${metadata.clinicianEmail}\n`;
    transcript += `Session ID: ${metadata.sessionId}\n\n`;
    transcript += '========================================\n\n';

    // Messages
    messages.forEach(msg => {
        const label = msg.type === 'user' ? 'USER' : 'AI';
        transcript += `[${msg.timestamp}] ${label}:\n`;
        transcript += `${msg.text}\n\n`;

        if (msg.tools && msg.tools.length > 0) {
            transcript += `Sources Checked: ${msg.tools.join(', ')}\n\n`;
        }

        transcript += '========================================\n\n';
    });

    // Disclaimer
    transcript += disclaimer;

    return transcript;
}

/**
 * Generate markdown transcript
 * @returns {string} Formatted markdown transcript
 */
function generateMarkdownTranscript() {
    const metadata = generateMetadata();
    const messages = collectChatMessages();
    const disclaimer = generateDisclaimer('markdown');

    let transcript = '';

    // Header
    transcript += '# AI Clinical Insights Transcript\n\n';

    // Metadata
    transcript += `**Generated:** ${metadata.generated}  \n`;
    transcript += `**Patient:** ${metadata.patientName} (ICN: ${metadata.patientICN})  \n`;
    transcript += `**Clinician:** ${metadata.clinicianEmail}  \n`;
    transcript += `**Session ID:** ${metadata.sessionId}\n\n`;
    transcript += '---\n\n';

    // Messages
    messages.forEach(msg => {
        const label = msg.type === 'user' ? 'User Question' : 'AI Response';
        transcript += `## [${msg.timestamp}] ${label}\n`;
        transcript += `${msg.text}\n\n`;

        if (msg.tools && msg.tools.length > 0) {
            transcript += `*Sources Checked: ${msg.tools.join(', ')}*\n\n`;
        }

        transcript += '---\n\n';
    });

    // Disclaimer
    transcript += disclaimer;

    return transcript;
}

/**
 * Generate metadata object from page context
 * @returns {object} Metadata {generated, patientName, patientICN, clinicianEmail, sessionId}
 */
function generateMetadata() {
    const now = new Date();

    // Extract patient info from page
    const patientNameEl = document.querySelector('.patient-header__name');
    const patientName = patientNameEl ? patientNameEl.textContent.trim() : 'Unknown Patient';

    const patientICN = getPatientICN();

    // Extract clinician from user context (if available)
    const clinicianEmail = getUserEmail() || 'unknown@va.gov';

    // Generate session ID (browser-generated unique ID)
    const sessionId = generateSessionId();

    return {
        generated: formatDateTimeLong(now),
        patientName,
        patientICN,
        clinicianEmail,
        sessionId
    };
}

/**
 * Generate disclaimer text
 * @param {string} format - 'text' or 'markdown'
 * @returns {string} Formatted disclaimer
 */
function generateDisclaimer(format = 'text') {
    if (format === 'markdown') {
        return `## Disclaimer

⚠️ **AI-Generated Clinical Insights**

This transcript contains AI-generated clinical insights. All information must be independently verified by qualified healthcare professionals before making clinical decisions. This tool provides decision support, not medical advice.

### Protected Health Information (PHI)

This document contains sensitive patient information protected under HIPAA. Handle according to VA/HIPAA data security policies:
- Store on encrypted devices only
- Do not transmit via unsecured channels (email, SMS)
- Delete when no longer clinically necessary

---

*Generated by: Med-Z1 AI Clinical Insights v1.0*
*https://github.com/department-of-veterans-affairs/med-z1*
`;
    } else {
        return `DISCLAIMER:
This transcript contains AI-generated clinical insights. All information
must be independently verified by qualified healthcare professionals before
making clinical decisions. This tool provides decision support, not medical
advice.

Protected Health Information (PHI):
This document contains sensitive patient information protected under HIPAA.
Handle according to VA/HIPAA data security policies. Store on encrypted
devices only. Do not transmit via unsecured channels (email, SMS).

Generated by: Med-Z1 AI Clinical Insights v1.0
https://github.com/department-of-veterans-affairs/med-z1
`;
    }
}

/**
 * Trigger browser download
 * @param {string} content - File content
 * @param {string} mimeType - MIME type (text/plain, text/markdown)
 * @param {string} filename - Filename with extension
 */
function downloadFile(content, mimeType, filename) {
    const blob = new Blob([content], {type: mimeType});
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    // Cleanup
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Helper functions (implement as needed)
function getPatientICN() {
    // Extract from page context or hidden form field
    const icnInput = document.querySelector('input[name="icn"]');
    return icnInput ? icnInput.value : 'UNKNOWN';
}

function getUserEmail() {
    // Extract from session/page if available
    // For MVP, may return null
    return null;
}

function generateSessionId() {
    // Simple browser-generated ID
    return 'SESSION_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function formatTimestamp(date) {
    // Format: YYYYMMDD_HHMMSS
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    const hh = String(date.getHours()).padStart(2, '0');
    const min = String(date.getMinutes()).padStart(2, '0');
    const ss = String(date.getSeconds()).padStart(2, '0');
    return `${yyyy}${mm}${dd}_${hh}${min}${ss}`;
}

function formatDateTimeLong(date) {
    // Format: "January 3, 2026 2:32:05 PM"
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = '';
    }
}
```

**Lines of Code:** ~200 lines (including comments)

---

##### **5.5 CSS Styling (Optional)**

Add minimal styling for download buttons if needed:

```css
/* app/static/styles.css */

.transcript-download-actions {
    margin-top: 1rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.transcript-download-actions .btn {
    flex: 1 1 auto;
    min-width: 200px;
}

@media (max-width: 768px) {
    .transcript-download-actions {
        flex-direction: column;
    }

    .transcript-download-actions .btn {
        width: 100%;
    }
}
```

---

#### **Phase 5 Success Criteria:**

- [ ] PHI warning modal displays before download
- [ ] User must acknowledge warning to proceed
- [ ] Plaintext transcript (.txt) downloads correctly
- [ ] Markdown transcript (.md) downloads correctly
- [ ] Filenames include patient ICN and timestamp
- [ ] Transcripts include all messages from current session
- [ ] Metadata (patient, clinician, timestamp) included in header
- [ ] PHI/HIPAA disclaimer included in footer
- [ ] Tools/sources attribution preserved in transcripts
- [ ] Download buttons disabled when no messages present
- [ ] Manual testing with 5+ conversation scenarios

---

#### **Phase 5 Deliverables:**

**Day 1 - Complete ✅:**
1. ✅ `app/templates/partials/transcript_download_modal.html` - PHI warning modal with optimized formatting
2. ✅ Single download button added to `app/templates/insight.html` (aligned with textarea)
3. ✅ CSS styling in `app/static/styles.css` for responsive button layout
4. ✅ Modal integration with existing app.js handlers
5. ✅ UX refinements (single button, black bullets, reduced spacing, shortened disclaimer)

**Day 2 - Complete ✅:**
1. ✅ `app/static/transcript.js` - Client-side transcript generation (~350 lines)
2. ✅ Both plaintext and markdown formats functional
3. ✅ Browser download triggered with proper filenames
4. ✅ Script integrated into `insight.html`
5. ✅ Modal buttons wired to download functions
6. ✅ Comprehensive testing with sample conversations

**Additional Enhancements:**
1. ✅ Real timestamp implementation in `app/routes/insight.py`
   - Replaced hardcoded "Just now" with actual datetime
   - Format: "2:45:32 PM" (12-hour with seconds)
   - Timestamps automatically included in downloaded transcripts
2. ✅ Markdown formatting improvements
   - Removed green checkmarks from Security Requirements
   - Clean bullet points for professional appearance

**Total Actual Time:** 3.5 hours (Day 1: 1.5 hours, Day 2: 2 hours)

---

#### **Phase 5 Completion Summary** ✅

**Completion Date:** January 4, 2026

**What Was Built:**
Phase 5 delivered a complete conversation transcript download system for AI Clinical Insights, enabling clinicians to save chat conversations to their local computers for clinical documentation and reference.

**Key Features Delivered:**
1. **PHI Warning Modal** - Comprehensive warning with 5 security acknowledgment items before download
2. **Dual Format Support** - Both plaintext (.txt) and markdown (.md) export formats
3. **Smart Filenames** - Auto-generated with patient ICN and timestamp: `clinical_insights_ICN100001_20260104_143205.txt`
4. **Real Timestamps** - Actual datetime display (e.g., "2:45:32 PM") instead of "Just now"
5. **Metadata Headers** - Patient name, ICN, clinician, session ID, generation timestamp
6. **Tools Attribution** - "Sources checked" preserved in transcripts
7. **Clinical Disclaimers** - PHI/HIPAA warnings and AI verification notices
8. **Client-Side Generation** - Privacy-first approach (no server storage)
9. **Responsive Design** - Mobile-friendly button layout and modal
10. **Browser Compatibility** - Works across Chrome, Edge, Firefox, Safari

**Technical Implementation:**
- **Backend:** `app/routes/insight.py` - Real timestamp generation
- **Frontend:** `app/static/transcript.js` - Client-side transcript generation (~350 lines)
- **Templates:** Modal, button, and styling updates
- **Architecture:** Blob API for file download, DOM extraction for conversation data

**User Workflow:**
1. User engages in AI conversation (asks questions, receives insights)
2. Clicks "Download Transcript" button below chat interface
3. PHI warning modal appears with security requirements
4. User selects format: "Download Plain Text (.txt)" or "Download Markdown (.md)"
5. File downloads to browser's default Downloads folder
6. User can reference transcript for clinical documentation

**Success Criteria Met:**
- ✅ PHI warning modal displays before download
- ✅ User must acknowledge warning to proceed
- ✅ Plaintext transcript (.txt) downloads correctly
- ✅ Markdown transcript (.md) downloads correctly
- ✅ Filenames include patient ICN and timestamp
- ✅ Transcripts include all messages from current session
- ✅ Metadata (patient, clinician, timestamp) included in header
- ✅ PHI/HIPAA disclaimer included in footer
- ✅ Tools/sources attribution preserved in transcripts
- ✅ Real timestamps (not "Just now") included throughout
- ✅ Manual testing with multiple conversation scenarios

**Folder Selection Decision:**
After evaluating File System Access API (Option 1), user elected to keep current implementation with default Downloads folder. This provides:
- Simple, reliable cross-browser experience
- No additional complexity or browser compatibility concerns
- Users can move files to preferred locations using OS file manager

**Phase 5 Complete - Ready for Production Use** 🎉

---

### Post-Phase 5 Data Quality & UX Enhancements ✅ **COMPLETE**

**Completion Date:** January 4, 2026

Following Phase 5 completion and initial user testing, several data quality issues and UX improvements were identified and resolved to ensure accurate clinical information display and optimal user experience.

---

#### **Enhancement 1: Real Timestamps Implementation**

**Problem:** Chat messages displayed hardcoded "Just now" timestamp instead of actual datetime.

**Impact:**
- No temporal context for conversation history
- Inability to determine when messages were sent
- Downloaded transcripts showed "Just now" for all messages

**Solution Implemented:**

1. **Backend Timestamp Generation** (`app/routes/insight.py` lines 162-164):
   ```python
   # Generate timestamp for this message exchange
   # Format: "2:45:32 PM" (12-hour format with seconds for precision)
   message_timestamp = datetime.now().strftime('%I:%M:%S %p')
   ```

2. **Updated Message Rendering** (lines 224, 230):
   - Replaced hardcoded `"Just now"` with `message_timestamp`
   - Applied to both user and AI messages
   - Applied to error messages (line 244)

3. **Added Import** (line 13):
   ```python
   from datetime import datetime
   ```

**Result:**
- ✅ Chat displays actual time: "2:45:32 PM"
- ✅ Clear temporal context during conversation
- ✅ Accurate timestamps in downloaded transcripts
- ✅ 12-hour format with seconds for clinical precision

**Files Modified:**
- `app/routes/insight.py`

---

#### **Enhancement 2: Clinician Email in Transcripts**

**Problem:** Downloaded transcripts showed incorrect clinician email "clinician@va.gov" instead of authenticated user's full email (e.g., "clinician.alpha@va.gov").

**Root Cause:** JavaScript had hardcoded placeholder email, no access to authenticated user data.

**Solution Implemented:**

1. **Added Hidden Field** (`app/templates/insight.html` line 96):
   ```html
   <input type="hidden" id="clinician-email" value="{{ user.email if user else 'unknown@va.gov' }}">
   ```
   - Extracts authenticated user email from session
   - Makes email available to client-side JavaScript

2. **Updated JavaScript Extraction** (`app/static/transcript.js` lines 124-130):
   ```javascript
   // Clinician email (from authenticated user session)
   const clinicianEmailInput = document.getElementById('clinician-email');
   if (clinicianEmailInput) {
       metadata.clinician = clinicianEmailInput.value;
   } else {
       metadata.clinician = 'unknown@va.gov';  // Fallback if not found
   }
   ```
   - Replaced hardcoded `'clinician@va.gov'` placeholder
   - Extracts real email from DOM

**Result:**
- ✅ Transcripts show correct authenticated user email
- ✅ Full email address preserved (e.g., "clinician.alpha@va.gov")
- ✅ Proper attribution for clinical documentation

**Files Modified:**
- `app/templates/insight.html`
- `app/static/transcript.js`

---

#### **Enhancement 3: Patient Name Display Fixes (Three Bugs)**

**Problem:** When asking "What is the patient's name?", AI responded "The patient's name is Unknown Patient" instead of the actual patient name.

**Root Cause:** Three separate bugs affecting patient name availability:

---

##### **Bug 1: Name Missing from Demographics Tool**

**Issue:** `get_demographics_summary()` in PatientContextBuilder did not include patient name in returned summary.

**Solution** (`ai/services/patient_context.py` lines 82-84):
```python
# Patient name (first line)
name = demo.get('name_display', 'Unknown Patient')
text = f"Patient Name: {name}\n"
```

**Result:**
- Demographics summary now starts with: `"Patient Name: MOORE, ROBERT"`
- Tool provides complete demographic information
- AI can answer name-based queries from tool results

---

##### **Bug 2: AI Privacy Overcaution**

**Issue:** AI refused to share patient name citing "privacy regulations" even though user is authenticated clinician in secure VA system.

**Root Cause:** System prompt said "Respect data sensitivity: All patient data is protected health information (PHI)" without clarifying that sharing with authenticated clinicians is authorized.

**Solution** (`ai/prompts/system_prompts.py` lines 84-90):

**Before:**
```
Safety & Privacy:
- Respect data sensitivity: All patient data is protected health information (PHI)
```

**After:**
```
Safety & Privacy:
- **Authorized clinical system**: You are operating within a secure VA clinical system.
  The user is an authenticated VA healthcare provider authorized to access all patient
  information including identifiers (name, ICN, SSN, DOB, etc.)
- **Share patient information freely**: When asked for patient identifiers or
  demographic details, provide them directly. There is no privacy restriction on
  sharing patient data with authorized clinicians in this clinical context
```

**Result:**
- AI understands this is authorized clinical use
- No privacy objections when sharing patient identifiers
- Proper balance: protect from external disclosure, enable internal clinical use

---

##### **Bug 3: Wrong Dictionary Field Name**

**Issue:** System prompt context showed "Unknown Patient" because route handler used wrong dictionary key.

**Root Cause** (`app/routes/insight.py` line 158):
```python
patient_name = patient.get("name", "Unknown Patient")  # Wrong key!
```

Database field is `name_display`, not `name`.

**Solution:**
```python
patient_name = patient.get("name_display", "Unknown Patient")
```

**Result:**
- System prompt now contains correct patient name
- Consistency between system prompt and tool results
- AI has patient name available from multiple sources

---

**Files Modified:**
- `ai/services/patient_context.py`
- `ai/prompts/system_prompts.py`
- `app/routes/insight.py`

---

#### **Post-Phase 5 Enhancements Summary**

**Total Bugs Fixed:** 4 (1 timestamp, 1 email, 3 patient name)

**User Experience Improvements:**
- ✅ Accurate timestamps for clinical documentation
- ✅ Proper clinician attribution in transcripts
- ✅ AI correctly answers "What is the patient's name?"
- ✅ Complete demographic information in tool results
- ✅ Proper authorization context for PHI sharing

**Testing Verification:**
- Tested with multiple patients (ICN100010, etc.)
- Verified database queries return correct data
- Confirmed AI responses include patient name
- Validated transcript metadata accuracy

**Impact:**
These enhancements ensure the AI Clinical Insights system provides accurate, complete clinical information with proper attribution, ready for production clinical use.

---

#### **Future Enhancements (Post-MVP):**

**Phase 5.1: Server-Side Session Storage** (6-8 hours)
- Store chat history in server session
- Enable download of conversations after page refresh
- Add "Download Previous Transcript" option

**Phase 5.2: PDF Export** (4-6 hours)
- Add PDF format using jsPDF library (client-side) or reportlab (server-side)
- Professional formatting with headers, footers, page numbers
- VA branding/logo

**Phase 5.3: Persistent Transcript History** (2-3 days)
- Database table: `clinical_insights_transcripts`
- Transcript management UI (view past conversations)
- Search/filter old transcripts
- Retention policies (auto-delete after 90 days)

**Phase 5.4: Advanced Features** (Future)
- Email transcript (encrypted, VA-approved channels only)
- Copy-to-clipboard option
- Print-friendly view
- Transcript annotations (clinician notes)
- Audit logging (who downloaded what, when)

---

#### **Security & Compliance Considerations:**

**PHI Handling:**
- ✅ Transcripts generated client-side (minimize server exposure)
- ✅ Explicit user acknowledgment required before download
- ✅ Clear PHI/HIPAA warnings in modal and file footer
- ✅ Filenames sanitized (avoid patient names, use ICN only)
- ✅ User responsible for file security post-download

**Audit Logging (Future):**
- Consider logging download events (who, what patient, when) for compliance
- Store in separate audit table, not in transcript content

**Data Retention:**
- MVP: No server storage (client-side only)
- Future: Define retention policy for persistent transcripts (e.g., 90-day auto-delete)

**Access Control:**
- Only authenticated clinicians can access Insights page
- Download buttons only visible to logged-in users
- Future: Role-based permissions for transcript management

---

### Phase 6: Conversation Memory (PostgreSQL Checkpointer) (Week 6) **✅ COMPLETE**

**Status:** ✅ Complete (2026-01-20)
**Priority:** High (Critical UX Enhancement)
**Actual Time:** ~6 hours (implementation + debugging)
**Completion Date:** 2026-01-20  

**Prerequisites:**
- LangGraph agent infrastructure operational (Phases 1-5 complete)
- PostgreSQL serving database running (port 5432)
- FastAPI application with SessionMiddleware configured
- CCOW patient context management operational

**Objective:** Implement persistent conversation memory using LangGraph's PostgreSQL checkpointer to enable follow-up questions, maintain chat history across page refreshes, and provide session-based persistence with automatic clearing on patient changes.

---

#### **Problem Statement**

**Current Limitation:**
The AI chatbot currently has **zero conversation memory** between user prompts. Each chat message creates a completely fresh agent state with no history of previous questions, answers, or tool calls.

**Impact on User Experience:**
- User asks: "What is the patient's birth date?" → Agent responds: "Born on May 15, 1965"
- User asks follow-up: "How old is the patient?" → Agent has **NO MEMORY** (re-calls tool or says "no information")

**Root Cause:**
- Each chat invocation passes only current message (`app/routes/insight.py:190-197`)
- Agent compiled without checkpointer (`ai/agents/insight_agent.py:168`)
- No state persistence between invocations

---

#### **Solution: PostgreSQL Checkpointer**

**Technology:** LangGraph's `langgraph-checkpoint-postgres` package

**Key Benefits:**
- **Follow-up questions work** - "What was that birth date?" resolves correctly
- **Persists across page refreshes** - Conversation survives navigation
- **Session-scoped memory** - History maintained for 25-minute login session
- **Patient-specific isolation** - Each ICN gets its own thread per user
- **Automatic clearing on patient change** - Different ICN = new conversation
- **Production-ready** - Uses existing PostgreSQL infrastructure

---

#### **Technical Requirements**

1. ✅ Chat history persists across page refreshes and navigation
2. ✅ Chat history persists for duration of user login session (25 minutes)
3. ✅ Chat history specific to selected patient (ICN)
4. ✅ Chat history clears automatically when patient changes (CCOW context change)
5. ✅ Chat history maintained if same patient used for entire session
6. ✅ Chat history deleted immediately when session expires
7. ✅ Optional "Clear Chat History" button for manual reset

---

#### **thread_id Strategy**

**Format:** `thread_id = f"{user_id}_{patient_icn}"` ⭐ **UPDATED (user-scoped, not session-scoped)**

**Behavior:**
- Same user + same patient = Same thread_id → History restored (persists across login sessions)
- Same user + different patient = Different thread_id → Fresh conversation
- Different user = Different user_id → Completely isolated conversations

**Example:** `45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc_ICN100001`

**Architectural Decision:**
Changed from session-scoped (`session_id`) to user-scoped (`user_id`) to enable conversation persistence across login sessions. This provides better clinical continuity - clinicians can log out/in and resume conversations with the same patients.

---

#### **Implementation Plan** (4-6 hours total)

**Task 1: Install Package** (5 min)
```bash
pip install langgraph-checkpoint-postgres
```

**Task 2: Update config.py** (2 min)
```python
LANGGRAPH_CHECKPOINT_URL = DATABASE_URL  # Reuse PostgreSQL
```

**Task 3: Create Database Tables** (10 min)
- Run DDL script: `db/ddl/create_ai_checkpoints_tables.sql`
- Creates `ai.checkpoints` and `ai.checkpoint_writes` tables
- See developer setup guide for detailed instructions

**Task 4: Add FastAPI Lifespan Handler** (30 min)
- Initialize AsyncPostgresSaver at startup with `ai` schema
- Configure connection string with `search_path=ai,public`
- Store checkpointer in app.state
- Recreate agent with checkpointer enabled

**Task 5: Update Agent Creation** (15 min)
- Add `checkpointer` parameter to `create_insight_agent()`
- Pass to `workflow.compile(checkpointer=checkpointer)`

**Task 6: Update Chat Route** (2-3 hours)
- Generate thread_id: `f"{session}_{icn}"`
- Switch to async (`await agent.ainvoke()`)
- Pass `config={"configurable": {"thread_id": thread_id}}`
- Get patient from CCOW (not form parameter)

**Task 7: Update UI Template** (30 min)
- Add hidden thread_id field
- Add JavaScript to persist thread_id across messages
- Add "Clear Chat History" button

**Task 8: Implement History Loading** (1 hour)
- Load checkpoint on GET `/insight/{icn}`
- Extract messages from checkpoint state
- Format for UI (skip system messages)
- Pre-populate chat history div

**Task 9: Implement Clear History** (30 min)
- POST endpoint to generate new thread_id with UUID suffix
- Clear chat history div via HTMX

---

#### **Database Schema**

**Schema:** `public` (LangGraph default, auto-created at app startup)

**Tables Created by:** `AsyncPostgresSaver.setup()` during application startup

```sql
-- LangGraph v3.x creates 4 tables in public schema:

-- 1. Main checkpoints table (conversation state metadata)
CREATE TABLE public.checkpoints (
    thread_id       TEXT NOT NULL,
    checkpoint_id   TEXT NOT NULL,
    parent_id       TEXT,
    checkpoint      BYTEA,           -- May be NULL if data in checkpoint_blobs
    metadata        BYTEA NOT NULL,
    PRIMARY KEY (thread_id, checkpoint_id)
);

-- 2. Checkpoint writes table (transactional updates)
CREATE TABLE public.checkpoint_writes (
    thread_id       TEXT NOT NULL,
    checkpoint_id   TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    idx             INTEGER NOT NULL,
    channel         TEXT NOT NULL,
    value           BYTEA,
    PRIMARY KEY (thread_id, checkpoint_id, task_id, idx)
);

-- 3. Checkpoint blobs table (large data storage)
CREATE TABLE public.checkpoint_blobs (
    thread_id       TEXT NOT NULL,
    checkpoint_id   TEXT NOT NULL,
    channel         TEXT NOT NULL,
    type            TEXT NOT NULL,
    blob            BYTEA NOT NULL,
    PRIMARY KEY (thread_id, checkpoint_id, channel, type)
);

-- 4. Checkpoint migrations table (schema versioning)
CREATE TABLE public.checkpoint_migrations (
    v               INTEGER PRIMARY KEY
);
```

**Key Design Decisions:**
- **Schema:** `public` schema (LangGraph default, avoids connection string complexity)
- **Auto-Creation:** Tables created by `AsyncPostgresSaver.setup()` at app startup (no manual DDL needed)
- **Version:** LangGraph checkpoint schema v3.x (4 tables, blob optimization)
- **Storage:** ~50KB per conversation thread (typical, stored in checkpoint_blobs)
- **Thread ID Format:** `{session_id}_{patient_icn}` for isolation
- **Migration Safety:** checkpoint_migrations tracks schema version for future LangGraph upgrades

**See Also:** `app/main.py` lifespan handler, LangGraph AsyncPostgresSaver documentation

---

#### **Success Criteria**

- [x] Follow-up questions work without re-calling tools ✅
- [x] History persists across page refresh ✅
- [x] History clears when patient changes ✅
- [x] History resumes when returning to same patient ✅
- [x] "Clear Chat History" button works ✅
- [x] Conversation persists across login sessions (user-scoped) ✅
- [x] No blank AI messages in history display ✅
- [x] All manual tests pass ✅

---

#### **Testing**

**Test 1: Conversation Memory**
- Ask: "What is the patient's birth date?"
- Follow-up: "How old is the patient?"
- **Verify:** Agent uses memory (no re-call of get_patient_summary)

**Test 2: Thread Isolation**
- Create conversation with Patient A
- Switch to Patient B
- **Verify:** Fresh conversation (no contamination)

**Test 3: History Loading**
- Create conversation (3 messages)
- Refresh browser (F5)
- **Verify:** All 3 messages restored

---

#### **Deliverables**

**Code:**
1. `db/ddl/create_ai_checkpoints_tables.sql` - DDL script for `ai` schema tables ⭐ **NEW**
2. `requirements.txt` - Add `langgraph-checkpoint-postgres`
3. `config.py` - Add `LANGGRAPH_CHECKPOINT_URL`
4. `app/main.py` - Lifespan handler with `ai` schema configuration
5. `ai/agents/insight_agent.py` - Checkpointer parameter
6. `app/routes/insight.py` - Async chat route + history loading
7. `app/templates/insight.html` - thread_id field + Clear button
8. `app/templates/partials/chat_message.html` - data-thread-id attribute

**Documentation:**
- `db/ddl/create_ai_checkpoints_tables.sql` - Comprehensive DDL with helper functions ⭐ **NEW**
- `docs/guide/developer-setup-guide.md` - Checkpoint table setup instructions ⭐ **NEW**
- Phase 6 spec updated in this document
- `config.py` updated (SESSION_TIMEOUT_MINUTES default = 25)
- Testing scripts created

**Full Specification:** See `docs/spec/phase6-conversation-memory-spec.md` for complete implementation details (~1700 lines including code examples, testing plan, and architecture decisions).

---

### Phase 7: Immunizations Integration (Week 7) **_PLANNED_**

**Prerequisites:**
- ✅ Immunizations ETL pipeline complete (PostgreSQL data available)
- ✅ Immunizations UI complete (dashboard widget + full page)
- ✅ Query functions available in `app/db/patient_immunizations.py`
- ✅ LangGraph agent infrastructure operational (Phases 1-6 complete)

**Estimated Time:** 5-7 days

**Objective:** Add immunization history and CDC compliance checking to AI Clinical Insights

---

#### **Days 1-3: Implement Immunization-Specific Tools (3-4 hours/day)**

**Tasks:**

1. **Create `ai/tools/immunization_tools.py`** (Day 1: 3-4 hours)
   - Implement `get_immunization_history()` tool
     - Wraps `app/db/patient_immunizations.get_patient_immunizations()`
     - Returns formatted text with vaccine names, dates, CVX codes, series status
     - Flags adverse reactions for safety awareness
   - Add tool to `ai/tools/__init__.py` (export in `ALL_TOOLS`)

2. **Implement `check_vaccine_compliance()` tool** (Day 2: 3-4 hours)
   - Age-based CDC ACIP guideline logic:
     - Adults 65+: Pneumococcal PPSV23, Shingrix (2-dose series)
     - All adults: Annual influenza, COVID-19 boosters
   - Return missing vaccines and incomplete series
   - Query patient age from demographics
   - Phase 7 MVP: Deterministic rules (no RAG)

3. **Implement `forecast_next_dose()` tool** (Day 3: 2-3 hours)
   - Calculate due dates for multi-dose series
   - Standard intervals: Shingrix (2 months), COVID-19 (1 month), Hepatitis B (1-2 months)
   - Query `get_vaccine_series_status()` from database layer
   - Return formatted due date and series progress

4. **Unit Testing** (Day 3: 1 hour)
   - Test each tool independently with mock data
   - Test with patients of different ages (18, 50, 68, 75)
   - Verify incomplete series detection
   - Test adverse reaction flagging

**Deliverables:**
- [ ] `ai/tools/immunization_tools.py` with 3 new tools
- [ ] Updated `ai/tools/__init__.py` (ALL_TOOLS now has 7 tools)
- [ ] Unit tests for immunization tools
- [ ] Manual testing with 5+ patients

**Estimated Time:** Days 1-3 (9-11 hours total)

**Design Reference:** `immunizations-design.md` Section 9.2 (detailed tool specifications)

---

#### **Day 4: Enhance PatientContextBuilder Service (2-3 hours)**

**Tasks:**

1. **Add `get_immunizations_summary()` method** (1.5 hours)
   - Location: `ai/services/patient_context.py`
   - Query `get_patient_immunizations(icn, limit=10)`
   - Format as natural language:
     ```
     Recent Immunizations (Last 10):
     - INFLUENZA, HIGH DOSE SEASONAL (2024-10-05), series complete
     - COVID-19, MRNA (2021-04-12), 2 of 2 doses complete
     - SHINGRIX (2021-02-10), 1 of 2 doses (INCOMPLETE) ⚠️
     ```
   - Flag incomplete series and adverse reactions
   - Graceful handling when no immunizations on record

2. **Update `build_comprehensive_summary()`** (30 min)
   - Add immunizations query: `immunizations = self.get_immunizations_summary()`
   - Insert into summary output (after ALLERGIES, before ENCOUNTERS)
   - Update data sources footer to include immunizations

3. **Update Documentation** (30 min)
   - Update method docstrings
   - Update class-level examples
   - Document in `app/README.md`

**Deliverables:**
- [ ] Enhanced `PatientContextBuilder` with immunizations integration
- [ ] `get_patient_summary()` now includes immunization history automatically
- [ ] Updated documentation

**Estimated Time:** Day 4 (2-3 hours)

**Impact:** When users ask "Summarize this patient's chart", immunization status is automatically included. Critical for elderly patients where vaccines are preventive care priorities.

---

#### **Day 5: System Prompts and Testing (2-3 hours)**

**Tasks:**

1. **Update System Prompts** (1 hour)
   - Location: `ai/prompts/system_prompts.py`
   - Add immunization context to agent prompts:
     ```python
     IMMUNIZATION_CONTEXT = """
     You have access to the patient's complete immunization history through these tools:

     1. **get_immunization_history**: Retrieve all vaccines with CVX codes
     2. **check_vaccine_compliance**: Check CDC ACIP guideline compliance
     3. **forecast_next_dose**: Calculate next dose due dates

     When discussing immunizations:
     - Always reference CVX codes for precision
     - Highlight incomplete vaccine series (require follow-up)
     - Note adverse reactions for safety awareness
     - Use CDC ACIP guidelines for age-appropriate recommendations
     - Calculate and display due dates for multi-dose series
     """
     ```

2. **Integration Testing** (1.5 hours)
   - Test immunization-specific tools via `/insight` interface
   - Test queries:
     - "What vaccines has this patient received?"
     - "Is patient up-to-date on vaccinations?"
     - "What immunizations are due?"
     - "When is next Shingrix dose due?"
   - Verify immunizations appear in comprehensive patient summaries
   - Test with patients of different ages (18, 50, 68, 75)

3. **Update Suggested Questions** (30 min)
   - Location: `ai/prompts/suggested_questions.py`
   - Add immunization-related question:
     - "What immunizations are due for this patient?"
     - OR "Is the patient up to date on vaccinations?"

**Deliverables:**
- [ ] Updated system prompts with immunization guidance
- [ ] Updated suggested questions
- [ ] Comprehensive integration testing completed
- [ ] End-to-end testing with 10+ patients

**Estimated Time:** Day 5 (2-3 hours)

---

#### **Days 6-7: Documentation and Final Testing (2-3 hours)**

**Tasks:**

1. **Documentation Updates** (1 hour)
   - Mark Phase 7 complete in this document
   - Update tool registry (Section 6.6) with final implementation notes
   - Document usage examples and performance metrics
   - Update `CLAUDE.md` with new AI capabilities

2. **Final QA Testing** (1 hour)
   - Test all immunization queries end-to-end
   - Verify CDC compliance checking accuracy
   - Check token usage and LLM costs
   - Performance testing (< 5 sec p90 response time)
   - Edge cases: no immunizations, incomplete series, adverse reactions

3. **Production Cleanup** (30 min)
   - Remove any debug logging
   - Verify error handling
   - Confirm graceful handling of missing data

**Deliverables:**
- [ ] Phase 7 marked complete
- [ ] All documentation updated
- [ ] Final QA checklist completed
- [ ] Ready for production use

**Estimated Time:** Days 6-7 (2-3 hours)

---

#### **Phase 7 Success Criteria:**
- [ ] `get_patient_summary()` automatically includes recent immunizations (last 10)
- [ ] 3 new immunization-specific tools available and functional:
  - `get_immunization_history`
  - `check_vaccine_compliance`
  - `forecast_next_dose`
- [ ] LangGraph agent autonomously invokes immunization tools for relevant queries
- [ ] CDC ACIP compliance checking works for common age-based vaccines
- [ ] Multi-dose series due dates calculated correctly
- [ ] Response time < 5 seconds for immunization queries (p90)
- [ ] Token usage remains reasonable (< 2K tokens for summaries)
- [ ] Manual testing with 10+ patients confirms accurate immunization retrieval
- [ ] Incomplete series and adverse reactions properly flagged
- [ ] UI suggested questions include immunization query

---

#### **Phase 7 Dependencies:**
- **Immunizations ETL Pipeline:** Must be complete with data in PostgreSQL
- **Immunizations UI:** Full page and widget operational for cross-referencing
- **Database Functions:** `app/db/patient_immunizations.py` with query functions
- **LangGraph Agent:** Phases 1-5 complete and operational

---

#### **Phase 7 Clinical Impact:**

**Care Gap Identification:**
- 68-year-old patient without pneumococcal vaccine → AI flags as care gap
- Incomplete Shingrix series → AI calculates next due date
- Overdue flu shot → AI recommends based on last vaccination date

**Preventive Care:**
- Immunizations are critical preventive care, especially for elderly patients
- AI can proactively identify missed vaccines during chart review
- Reduces cognitive load on clinicians for vaccine schedule tracking

**Safety:**
- Adverse reaction history surfaced automatically
- Helps clinicians make informed decisions about future vaccinations
- CVX code precision prevents confusion between similar vaccines

---

#### **Phase 7 Future Enhancements (Phase 8+):**
- **RAG Integration:** Vector embeddings of CDC "Pink Book" ACIP schedules
- **Contraindication Checking:** Semantic search for vaccine contraindications
- **Travel Medicine:** Destination-specific vaccine recommendations
- **Occupational Health:** Job-based vaccine requirements (healthcare workers, etc.)
- **Pediatric Schedules:** CDC childhood immunization schedule integration

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
1. Clear "AI-generated" disclaimer on every page
2. Show which tools/data sources were queried
3. Timestamp for when data was retrieved
4. Indication of data freshness (T-0 vs T-1)

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
- All patient data stays within VA network (no external API calls with PHI)
- OpenAI API: Send only de-identified summaries, NOT raw PHI
- No logging of patient-specific queries to external services
- Comply with VHA Directive 6500 (Information Security Program)

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

---

### 14.1.1 Port MCP Server Tools to LangGraph (2-4 weeks, 8-12 hours)

**Context:** During MCP learning path implementation (Sections 5-6), clinical decision support tools were built for **external MCP clients** (Claude Desktop, etc.). These tools wrap existing med-z1 business logic but are **not yet available** in the web UI's LangGraph agent.

**Opportunity:** Reuse the same clinical algorithms by creating LangGraph `@tool` wrappers that share the underlying services.

**Candidate Tools from MCP Server #2 (Clinical Decision Support):**

1. **`assess_fall_risk(patient_icn: str)`**
   - **MCP Implementation:** `mcpsvr/clinical_decision_support_server.py:_assess_fall_risk()`
   - **Algorithm:** Age (≥65 = +2), polypharmacy (≥5 meds = +1), high-risk medication classes (+1 each)
   - **Output:** Risk level (Low/Moderate/High) + contributing factors + recommendations
   - **Clinical Value:** Geriatric safety assessment for inpatient safety planning
   - **Effort:** 2-3 hours (extract logic to `ai/services/fall_risk_analyzer.py`, create `@tool` wrapper)

2. **`calculate_ckd_egfr(creatinine: float, age: int, sex: str, race_black: bool = False)`**
   - **MCP Implementation:** `mcpsvr/clinical_decision_support_server.py:_calculate_ckd_egfr()`
   - **Algorithm:** CKD-EPI 2021 equation (race-neutral)
   - **Output:** eGFR value + CKD stage (G1-G5) + clinical recommendations
   - **Clinical Value:** Essential for medication dosing adjustments (many drugs renally cleared)
   - **Effort:** 2-3 hours (pure calculation function, easy to extract and wrap)

3. **`recommend_cancer_screening(patient_icn: str)`**
   - **MCP Implementation:** `mcpsvr/clinical_decision_support_server.py:_recommend_cancer_screening()`
   - **Algorithm:** USPSTF guideline-based (colorectal, breast, cervical, lung, prostate)
   - **Output:** Age/sex-stratified screening recommendations with evidence grades (A/B/C)
   - **Clinical Value:** Preventive care planning, gap analysis
   - **Effort:** 3-4 hours (guideline logic extraction, may need update mechanism for guideline changes)

**Implementation Pattern:**

```python
# Step 1: Extract business logic to ai/services/ (if needed)
# ai/services/fall_risk_analyzer.py
class FallRiskAnalyzer:
    def assess_risk(self, patient_icn: str) -> dict:
        """Reusable fall risk assessment logic"""
        # Logic from MCP server
        pass

# Step 2: Create LangGraph tool wrapper
# ai/tools/clinical_tools.py (new file)
from langchain_core.tools import tool
from ai.services.fall_risk_analyzer import FallRiskAnalyzer

@tool
def assess_fall_risk(patient_icn: str) -> str:
    """Assess patient fall risk based on age, medications, and polypharmacy.

    Returns risk level (Low/Moderate/High) with contributing factors.
    Useful for geriatric and inpatient safety planning.
    """
    analyzer = FallRiskAnalyzer()
    result = analyzer.assess_risk(patient_icn)
    return format_fall_risk_result(result)

# Step 3: Add to ALL_TOOLS in ai/tools/__init__.py
from ai.tools.clinical_tools import assess_fall_risk, calculate_egfr, recommend_cancer_screening

ALL_TOOLS = [
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
    get_clinical_notes_summary,
    assess_fall_risk,           # NEW
    calculate_egfr,             # NEW
    recommend_cancer_screening, # NEW
]
```

**Benefits:**
- ✅ Expands web UI capabilities without new logic development
- ✅ Reuses thoroughly tested MCP server algorithms
- ✅ Single source of truth (services shared by both MCP and LangGraph)
- ✅ Quick implementation (logic already exists, just needs wrapper)

**Dependencies:**
- MCP Server #2 implementation (Section 6) - ✅ Complete as of 2026-02-02

**Priority:** Medium (enhances web UI, but MCP servers already provide access via Claude Desktop)

---

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

### 14.3 Clinical Notes Enhancement Opportunities (Phase 5+)

**Background:**
With Phase 4 complete, the AI system will have access to 106 clinical notes containing rich narrative data (SOAP documentation, consultant recommendations, discharge summaries, imaging reports). These notes represent the highest-value unstructured data for AI-powered clinical insights. The following enhancements build on Phase 4's foundation.

---

**Priority 1: Care Gap Analysis Tool (2-4 weeks, 8-12 hours)**

**Purpose:** Extract action items, follow-ups, and recommendations from clinical notes to identify care plan items that may not have been completed.

**Implementation:**
- LLM-based extraction from note text (focus on PLAN sections of SOAP notes)
- Pattern matching for keywords: "follow-up", "schedule", "refer to", "order", "recheck", "monitor"
- Cross-reference with subsequent notes and orders to identify gaps
- Report unfulfilled items with original date and clinician

**Example Output:**
```
⚠️ **Care Gaps Identified:**

1. Cardiology follow-up recommended on 12/15/2025
   - Source: Cardiology consult by Dr. Emily Johnson
   - Recommendation: "Return to cardiology in 2 weeks after stress test results"
   - Status: No cardiology encounter found in subsequent 30 days
   - Action needed: Schedule cardiology follow-up

2. Stress test ordered on 12/15/2025
   - Source: Cardiology consult
   - Recommendation: "Schedule exercise stress test"
   - Status: No imaging report found for stress test
   - Action needed: Verify if test was scheduled/completed

3. HbA1c check recommended on 12/28/2025
   - Source: Progress note by Dr. Jonathan Smith
   - Recommendation: "Check HbA1c at next visit"
   - Status: No lab result found in last 30 days
   - Action needed: Order HbA1c
```

**Technical Approach:**
- Use LLM to extract recommendations from each note (focus on PLAN section)
- Store extracted actions with source note ID and date
- Query subsequent notes/orders/labs for evidence of follow-through
- Flag items with no evidence of completion

---

**Priority 2: Clinical Timeline Generator (2-4 weeks, 10-15 hours)**

**Purpose:** Build chronological patient story combining clinical notes and structured data to understand disease progression and treatment response.

**Implementation:**
- Merge notes, encounters, medications, vitals, labs by date
- LLM summarization of key events at each timepoint
- Identify turning points: admissions, new diagnoses, treatment changes, significant test results

**Example Output:**
```
**Clinical Timeline for Patient ICN100001**

📅 **2025-11-17** - Hospital Admission
   - Event: Admitted for COPD exacerbation (Discharge Summary)
   - Vitals: BP 152/92, HR 94, O2 sat 88% on room air
   - Treatment: Started on prednisone and nebulizers
   - Outcome: Discharged 11/20 after 3-day stay

📅 **2025-11-30** - Follow-up Visit
   - Event: Post-discharge observation visit (Encounter)
   - Vitals: BP 142/88, HR 76 (improved from admission)
   - Assessment: COPD stable, recovering well
   - Plan: Continue medications, return PRN

📅 **2025-12-15** - Specialty Consultation
   - Event: Cardiology consult for chest pain (Consult Note)
   - New symptoms: Exertional chest pain concerning for CAD
   - Risk factors: HTN, DM, hyperlipidemia, age 68
   - Diagnostic plan: Stress test + echo ordered
   - Medication change: Started metoprolol 25mg BID

📅 **2025-12-28** - Routine Follow-up
   - Event: Primary care visit (Progress Note)
   - Diabetes control: Blood sugars 120-140 mg/dL (good)
   - Hypertension: BP well-controlled on current regimen
   - Plan: Continue current meds, RTC 3 months
```

**Technical Approach:**
- Query all notes and structured data for date range
- Sort chronologically
- Use LLM to identify significant events and transitions
- Format as narrative timeline with clinical context

---

**Priority 3: Semantic Note Search with Vector Embeddings (4-6 weeks, 15-20 hours)**

**Purpose:** Enable natural language search across all clinical notes without requiring exact keyword matching.

**Implementation:**
- Generate embeddings for all note text using OpenAI text-embedding-ada-002 (or similar)
- Populate `embedding_vector` column in PostgreSQL (pgvector extension already installed!)
- Create `search_clinical_notes(query, patient_icn, top_k=5)` tool
- Use cosine similarity for retrieval

**Example Queries:**
- "Find notes mentioning heart failure symptoms" (without saying "heart failure")
- "Show me when the patient complained of shortness of breath"
- "What notes discuss kidney function?"
- "Search for medication compliance issues"

**Technical Details:**
- **ETL Addition:** Add embedding generation step to Silver or Gold layer
- **Storage:** VECTOR(1536) column in PostgreSQL (OpenAI ada-002 embeddings)
- **Query:** pgvector cosine similarity search (`<=>` operator)
- **Performance:** <500ms for top-5 search with proper indexes

**Example Tool:**
```python
@tool
def search_clinical_notes(
    query: str,
    patient_icn: str,
    top_k: int = 5
) -> str:
    """Search clinical notes using semantic similarity."""
    # Generate query embedding
    query_embedding = openai.Embedding.create(input=query, model="text-embedding-ada-002")

    # Search using pgvector
    results = db.query("""
        SELECT document_title, document_class, reference_datetime, text_preview,
               1 - (embedding_vector <=> :query_emb) as similarity
        FROM patient_clinical_notes
        WHERE patient_icn = :icn
        ORDER BY embedding_vector <=> :query_emb
        LIMIT :top_k
    """, query_emb=query_embedding, icn=patient_icn, top_k=top_k)

    return format_search_results(results)
```

---

**Priority 4: AI-Generated Note Summaries (3-5 weeks, 12-18 hours)**

**Purpose:** Populate `ai_summary` column with LLM-generated 2-3 sentence abstracts for faster note scanning.

**Implementation:**
- Background ETL job: Generate summaries for each note using GPT-3.5-turbo (cheaper for bulk)
- Store in `ai_summary` column (TEXT)
- Use in widgets, AI tool responses, and search results
- Regenerate when notes are amended

**Example Summaries:**
```
Progress Note (2025-12-28):
AI Summary: "68yo male veteran with routine follow-up for HTN and DM. Blood sugars well-controlled (120-140 mg/dL). No new complaints. Continue current medications."

Cardiology Consult (2025-12-15):
AI Summary: "Evaluated for exertional chest pain concerning for CAD. Multiple cardiac risk factors present. Stress test and echo ordered. Started beta-blocker therapy."
```

**ETL Integration:**
```python
# etl/generate_note_summaries.py

def generate_summary(note_text: str) -> str:
    prompt = f"""Summarize this clinical note in 2-3 sentences. Focus on:
    1. Patient presentation/reason for visit
    2. Key findings or assessments
    3. Plan or recommendations

    Note:
    {note_text[:2000]}  # Truncate long notes

    Summary:"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=100
    )

    return response.choices[0].message.content

# Run for all notes, update ai_summary column
```

---

**Priority 5: Clinical Entity Extraction (NER) (6-8 weeks, 20-30 hours)**

**Purpose:** Extract structured entities from narrative text (medications, diagnoses, procedures, lab values) and populate `key_entities` JSONB column.

**Implementation:**
- Use LLM or specialized NER model (spaCy ScispaCy, BioBERT, or GPT-4)
- Extract: medications, diseases/diagnoses, procedures, labs, body sites, symptoms
- Store in `key_entities` column as JSON
- Enable entity-based search and cross-referencing with structured data

**Example Extracted Entities:**
```json
{
  "medications": ["lisinopril", "metformin", "atorvastatin", "aspirin"],
  "diagnoses": ["hypertension", "diabetes mellitus type 2", "hyperlipidemia", "CAD"],
  "procedures": ["stress test", "echocardiogram"],
  "labs": {
    "blood sugar": "120-140 mg/dL",
    "HbA1c": "6.8%",
    "blood pressure": "142/88 mmHg"
  },
  "symptoms": ["chest pain", "exertional dyspnea"],
  "body_sites": ["chest", "cardiac"]
}
```

**Use Cases:**
- "Find all notes that mention chest pain" → Search key_entities.symptoms
- "What diagnoses are documented in notes?" → Extract key_entities.diagnoses
- "Reconcile medications in notes vs med list" → Compare key_entities.medications with patient_medications table

---

**Summary of Phase 5+ Enhancements:**

| Enhancement | Effort | Impact | Dependencies |
|-------------|--------|--------|--------------|
| Care Gap Analysis | 8-12 hours | VERY HIGH | Phase 4 complete |
| Clinical Timeline | 10-15 hours | HIGH | Phase 4 complete |
| Semantic Search | 15-20 hours | VERY HIGH | Phase 4 + embeddings ETL |
| AI Note Summaries | 12-18 hours | HIGH | Phase 4 + ETL pipeline |
| Entity Extraction | 20-30 hours | VERY HIGH | Phase 4 + NER model |

**Recommended Implementation Order:**
1. **Phase 4** - Basic notes integration (current focus)
2. **Care Gap Analysis** - Immediate clinical value
3. **Clinical Timeline** - Builds on gap analysis
4. **AI Summaries** - Improves UX, enables next features
5. **Semantic Search** - Requires embeddings infrastructure
6. **Entity Extraction** - Advanced feature, highest complexity

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
| v1.5 | 2025-12-30 | **Phase 1-3 Complete**. Marked all Phase 1-3 tasks complete. Added implementation notes for Phase 2 (Web UI Integration) and Phase 3 (Vital Trends + Vista Session Caching). | Claude + User |
| v1.6 | 2026-01-02 | Added Phase 4 specification (Clinical Notes Integration). Documented Days 1-5 implementation plan with detailed tasks, deliverables, and success criteria. | Claude + User |
| v1.7 | 2026-01-03 | **Phase 4 Complete**. Marked all Phase 4 tasks complete. Added implementation notes for system prompts architecture, clinical notes tool, enhanced patient summary, and testing results. | Claude + User |
| v1.8 | 2026-01-03 | **Post-Phase 4 UX Enhancements Complete**. Added new section documenting 4 completed enhancements: (1) Suggested questions modal refactoring with sparkle icon button, (2) Centralized suggested questions configuration module, (3) Unified chat button styling (sparkle + submit buttons), (4) Enhanced demographics with date of birth. Added Phase 5 specification (Conversation Transcript Download MVP). Updated document status. | Claude + User |
| v1.9 | 2026-01-03 | **Phase 5 Day 1 Complete**. Updated Phase 5 specification with actual implementation details: (1) Single "Download Transcript" button (UX improvement from initial two-button spec), (2) Button aligned with textarea using calc() padding, (3) PHI warning modal with black bullet points and reduced spacing, (4) Shortened disclaimer text to eliminate vertical scrolling. Marked Day 1 deliverables complete, Day 2 ready for implementation. Updated document status to reflect progress. | Claude + User |
| v2.0 | 2026-01-04 | **Phase 5 Complete - Conversation Transcript Download MVP**. Marked all Phase 5 deliverables complete. Day 2 implementation: (1) Complete transcript.js module (~350 lines) with client-side plaintext and markdown generation, (2) Browser download with formatted filenames, (3) Script integration and modal button wiring. Additional enhancements: (1) Real timestamp implementation replacing hardcoded "Just now" with actual datetime (format: "2:45:32 PM"), (2) Markdown formatting improvements removing green checkmarks from Security Requirements. Total implementation time: 3.5 hours. All success criteria met. **Major milestone: Phase 1-5 complete.** | Claude + User |
| v2.1 | 2026-01-04 | **Post-Phase 5 Data Quality & UX Enhancements Complete**. Fixed 4 bugs identified during user testing: (1) Real timestamps - replaced hardcoded "Just now" with actual datetime in chat messages (backend datetime generation), (2) Clinician email - fixed transcript metadata to show full authenticated user email instead of placeholder, (3) Patient name fixes - three separate bugs: added name to demographics tool output, updated system prompt to authorize sharing patient identifiers with clinicians, fixed dictionary field name from "name" to "name_display" in route handler. All enhancements verified working. AI now correctly answers "What is the patient's name?" System ready for production clinical use. | Claude + User |
| v2.2 | 2026-01-15 | **Phase 6 Detailed Specifications - Immunizations Integration (Consolidated)**. Expanded Section 6.6 with full implementation details for 3 immunization tools (get_immunization_history, check_vaccine_compliance, forecast_next_dose) including complete Python code, helper functions, and use cases (~250 lines). Added Section 4.6: Use Case 6 "Vaccination Compliance and Gap Analysis" with detailed agent flow and example response for 68-year-old patient compliance check (~70 lines). Section 6.6 now contains 5 subsections (6.6.1-6.6.5) with comprehensive tool specifications, system prompts integration, and RAG enhancement roadmap. **Architectural decision:** Consolidated all AI integration design from `immunizations-design.md` Section 9 into this document per "single source of truth" principle. `immunizations-design.md` Section 9 now contains concise pointer to this document (Sections 4.6, 6.6, and 10 Phase 6). Phase 6 already detailed in Section 10 (no changes needed - already comprehensive 5-7 day plan). Ready for Phase 6 implementation. | Claude + User |
| v2.3 | 2026-01-19 | **Phase 6 Conversation Memory Specification (PostgreSQL Checkpointer)**. Inserted new Phase 6 before Immunizations (renumbered to Phase 7). Added comprehensive specification for persistent conversation memory using LangGraph PostgreSQL checkpointer (~200 lines in main doc, full 1700-line spec in `phase6-conversation-memory-spec.md`). **Key features:** Follow-up questions work (no re-calling tools), history persists across page refreshes, session-scoped persistence (25 minutes), automatic clearing on patient change, patient-specific thread isolation, "Clear Chat History" button. **Implementation:** 8 tasks, 4-6 hours total. **thread_id strategy:** `f"{user_session_id}_{patient_icn}"` enables automatic patient-based clearing. **Technical updates:** Updated `config.py` SESSION_TIMEOUT_MINUTES default from 15 to 25 minutes (aligns with clinical workflow). Database schema: Auto-created `checkpoints` and `checkpoint_writes` tables (~50KB per thread). Ready for immediate implementation. | Claude + User |
| v2.4 | 2026-01-20 | **Phase 6 Complete - Conversation Memory with PostgreSQL Checkpointer**. Implemented full conversation persistence across page refreshes and login sessions. **Key implementation details:** (1) User-scoped thread_id (`{user_id}_{patient_icn}`) instead of session-scoped for cross-session persistence, (2) Fixed history loading with proper Jinja2 template variable passing, (3) Filtered blank AI messages (tool-only messages), (4) Clear Chat History button using psycopg v3 syntax (`%s` placeholders, tuple parameters), (5) LangGraph v3.x checkpoint schema (4 tables: checkpoints, checkpoint_writes, checkpoint_blobs, checkpoint_migrations in `public` schema). **Bugs fixed:** Template rendering issue, psycopg v3 API differences, connection lifetime management. **Testing:** All success criteria met - follow-up questions work, history persists across refresh/login, patient isolation verified, clear button functional. Total time: ~6 hours. Ready for Phase 7 (Immunizations Integration). | Claude + User |

---

**Next Steps:**
1. ✅ Phases 1-6 Complete - AI Clinical Insights fully operational with conversation memory
2. ⏳ **Phase 7: Immunizations Integration** (5-7 days, 16-20 hours) - Next priority
3. ⏳ Phase 8+: Advanced features (RAG, semantic search, care gap analysis)

**Questions or Feedback:** Phase 6 complete and tested. Review implementation in `app/main.py` (lifespan handler), `app/routes/insight.py` (history loading + clear button), and `app/templates/insight.html` (UI updates).
