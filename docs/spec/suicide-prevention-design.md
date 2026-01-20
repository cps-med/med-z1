# Suicide Prevention AI Design Specification - med-z1

**Document Version:** 1.1
**Date:** 2026-01-20
**Status:** ✅ Specification Complete - ⏳ Implementation Pending
**Implementation Phase:** Phase 7 (Clinical Intelligence)
**Based on:** VA REACH VET 2.0 Architecture + VA/DoD CPG Suicide Risk Assessment (2024)

**Changelog:**

- **v1.1 (2026-01-20):**
  - **Section 3.3 added:** Data Freshness Requirements - Documents ETL pipeline limitation (T-1 data staleness creates 13-hour delay risk), dependency on clinical notes timeliness for safety override, and production requirement for real-time data access
  - **Section 3.4 added:** VistA Real-Time Integration Strategy - Documents TIU namespace RPC approach, site selection policy (3-5 sites for safety-critical domain), merge/deduplication strategy (canonical event keys), session caching pattern (30-min TTL), and 3-phase implementation timeline with trade-offs analysis
  - **Section 6.6 added:** Risk Model Configuration Management - Documents database-backed coefficient approach (Option A, recommended) vs JSON configuration (Option B, rejected), provides PostgreSQL schema design, operational workflow for model updates without code deployment, backward-compatible migration path, and clinical governance process for production model updates
  - **Section 13.5 updated:** Technical References - Added comprehensive references to Vista RPC Broker design specification (v2.0), implementation guide (vista/README.md), Vista client service (app/services/vista_client.py), and session cache service (app/services/vista_cache.py) with detailed relevance descriptions
- **v1.0 (2026-01-17):**
  - Initial design specification covering REACH VET 2.0 implementation, ETL pipeline, NLP processing, AI integration, and security considerations

**⚠️ TODO - Post-Implementation:**
- Update `docs/guide/developer-setup-guide.md` to reflect AI Suicide Prevention enhancement
- Add documentation for:
  - New Python dependencies (nltk, textblob)
  - New PostgreSQL tables (`clinical.clinical_risk_scores`, `clinical.clinical_risk_factors`)
  - New AI tool (`check_suicide_risk_factors`)
  - Suicide risk test patient data (ICN200000-200099)
  - ETL pipeline for suicide risk scoring

---

## Table of Contents

1. [Overview](#1-overview)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Prerequisites & Dependencies](#3-prerequisites--dependencies)
4. [Data Architecture](#4-data-architecture)
5. [Database Schema](#5-database-schema)
6. [ETL Pipeline Design](#6-etl-pipeline-design)
7. [AI Subsystem Integration (LangGraph)](#7-ai-subsystem-integration-langgraph)
8. [API Endpoints](#8-api-endpoints)
9. [Clinical Notes NLP Processing](#9-clinical-notes-nlp-processing)
10. [Implementation Roadmap](#10-implementation-roadmap)
11. [Testing Strategy](#11-testing-strategy)
12. [Security and Ethical Considerations](#12-security-and-ethical-considerations)
13. [Reference Documents](#13-reference-documents)

---

## 1. Overview

### 1.1 Purpose

The **Suicide Prevention AI** capability proactively identifies veterans at elevated risk for suicide by analyzing clinical and administrative data patterns. Modeled after the VA's **REACH VET 2.0** system (Recovery Engagement and Coordination for Health - Veterans Enhanced Treatment), this module leverages predictive analytics to flag high-risk individuals for early intervention by clinical teams.

Unlike standard clinical domains (e.g., Medications, Vitals), this is a **derived intelligence domain**. It does not merely display raw data; it synthesizes data from multiple sources (medications, encounters, demographics, flags, clinical notes) to calculate a probabilistic risk score and surface actionable insights via the `med-z1` AI Chatbot.

### 1.2 Scope

**In Scope for Initial Implementation (MVP - Days 1-15):**

* **Data Simulation:** Generating synthetic training/testing data for 100+ veterans mimicking REACH VET risk factors (missed appointments, chronic pain, specific medication combos, clinical note mentions of hopelessness/ideation)
* **ETL Pipeline:** Full Bronze → Silver → Gold pipeline to aggregate risk factors from `CDWWork` (VistA) and `CDWWork2` (Oracle Health/Cerner) schemas
* **Risk Engine (Python):** Calibrated logistic regression scoring engine implementing REACH VET 2.0 variables with published coefficient weights
* **Clinical Notes NLP:** Sentiment analysis and keyword extraction from clinical notes to identify psychosocial risk indicators (e.g., "suicidal ideation", "hopelessness", "access to firearms", "social isolation")
* **PostgreSQL Serving:** Dedicated `clinical_risk_scores` and `clinical_risk_factors` tables with audit trail
* **AI Agent Integration:** A new LangGraph tool (`check_suicide_risk_factors`) enabling the AI Chatbot to discuss risk factors with clinicians naturally and sensitively
* **Access Control:** Risk assessment accessible ONLY via AI Chatbot (no dashboard widgets, no dedicated pages)

**Out of Scope (Phase 2 - Deferred):**

* Deep learning models on unstructured clinical notes (vector embeddings, transformer models)
* Real-time integration with crisis response hotlines (e.g., Veterans Crisis Line API)
* Patient-facing alerts (clinician-facing only for safety)
* Dashboard widgets or dedicated risk assessment pages
* Integration with VA Safety Planning tools
* Automated care coordination workflows (e.g., automatic consult to Suicide Prevention Coordinator)
* Historical risk score trending (show risk trajectory over time)

### 1.3 Key Design Decisions

**ADR-SP-001: AI Chatbot Only Access Pattern**
- **Decision:** Suicide risk assessment accessible ONLY through AI Insights chatbot interface
- **Rationale:**
  - Reduces stigma (no visible "suicide risk" labels on dashboard)
  - Restricts access to clinical conversations (chatbot requires deliberate query)
  - Aligns with VA Mental Health Services guidance on sensitive information display
  - Minimizes risk of alarm/panic from clinicians or staff seeing "high risk" badges
- **Alternative Rejected:** Dashboard alert widget (too visible, potentially stigmatizing)

**ADR-SP-002: Calibrated Statistical Model vs. Simple Rules**
- **Decision:** Use logistic regression with published REACH VET 2.0 coefficient weights
- **Rationale:**
  - Published literature provides validated coefficients (McCarthy et al. 2015, Kessler et al. 2015)
  - Better clinical fidelity than arbitrary rule weights
  - Reproducible and auditable scoring methodology
  - Supports sensitivity/specificity claims aligned with VA standards
- **Alternative Rejected:** Simple weighted rules (less clinically validated), Deep learning (too complex for 15-day timeline)

**ADR-SP-003: Clinical Notes NLP Integration**
- **Decision:** Include narrative text analysis from clinical notes in initial implementation
- **Rationale:**
  - Many critical risk factors (hopelessness, suicidal ideation, social support) are documented only in narrative notes
  - Rule-based NLP (keyword extraction + sentiment analysis) is tractable in aggressive timeline
  - Significantly improves risk detection sensitivity vs. structured data alone
  - Aligns with VA/DoD CPG emphasis on comprehensive clinical assessment
- **Alternatives Considered:** Structured data only (misses narrative risk factors), Vector embeddings (too complex for MVP)

**ADR-SP-004: REACH VET 2.0 Variable Set Alignment**
- **Decision:** Implement REACH VET 2.0 variable set, including **Military Sexual Trauma (MST)** and excluding race/ethnicity
- **Rationale:**
  - REACH VET 2.0 is the VA's validated production system (alignment with VA standards)
  - MST is a significant risk factor for suicide in veteran populations
  - Removing race/ethnicity aligns with modern equity standards and reduces algorithmic bias
- **Alternative Rejected:** REACH VET 1.0 (outdated, omits MST)

**ADR-SP-005: Hybrid Data Source Strategy**
- **Decision:** Normalize data from both `Outpat.Visit` (VistA) and `Mill.ENCOUNTER` (Cerner) into unified "Utilization" feature set
- **Rationale:**
  - Demonstrates multi-source harmonization capability
  - Reflects real VA environment (VistA + Cerner sites)
  - Exercises Silver-layer transformation complexity
- **Alternative Rejected:** VistA-only (doesn't test cross-system harmonization)

**ADR-SP-006: Explainable AI (XAI) Requirement**
- **Decision:** AI Chatbot must cite specific factors driving risk score, not just "High Risk" label
- **Rationale:**
  - Clinician trust requires transparency in AI decision-making
  - VA Medical-Legal requirements for algorithmic transparency
  - Supports clinical decision-making (actionable insights vs. black box)
  - Aligns with VA/DoD CPG emphasis on individualized risk assessment
- **Implementation:** Store contributing factors in `clinical_risk_factors` table with weights and supporting data (JSONB)

---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

1. **Early Identification:** Successfully flag synthetic patients who exhibit known risk patterns (e.g., top 0.1% tier) before a crisis occurs
2. **Data Unification:** Demonstrate ability to compute complex risk scores across federated VistA and Oracle Health data models
3. **Clinician Support:** Provide AI Chatbot with ability to explain *why* a patient is flagged, aiding in care coordination
4. **Clinical Fidelity:** Achieve sensitivity/specificity metrics aligned with published REACH VET 2.0 performance (Sensitivity ~50% at 0.1% threshold)
5. **NLP Integration:** Successfully extract psychosocial risk factors from clinical notes narrative text

### 2.2 Success Criteria

**Data Pipeline:**
- [x] Mock CDW tables populated with 100+ synthetic patient records exhibiting REACH VET risk patterns
- [x] Bronze ETL extracts all required source tables to Parquet (Encounters, Medications, Demographics, Diagnoses, Clinical Notes)
- [x] Silver ETL harmonizes VistA and Cerner data, calculates derived features (e.g., No-Show Rate, Medication Classes)
- [x] NLP pipeline processes clinical notes and extracts risk keywords with sentiment scores
- [x] Gold ETL creates `gold_suicide_risk_features` with one row per patient per month
- [x] PostgreSQL serving DB loaded with `clinical_risk_scores` and `clinical_risk_factors` tables
- [x] Risk scores calculated for 100% of synthetic patients with explainability metadata

**Model Performance:**
- [x] Scoring engine correctly flags "High Risk" synthetic profiles (pre-seeded with REACH VET traits)
- [x] Scoring engine correctly assigns "Standard Risk" to low-risk profiles
- [x] Sensitivity ≥ 40% at top 0.1% threshold (aligned with REACH VET 2.0 published performance)
- [x] False positive rate < 5% for "High Risk" tier
- [x] Risk score calculation completes in < 200ms during patient load

**AI Chatbot Integration:**
- [x] New LangGraph tool `check_suicide_risk_factors` successfully queries risk assessment database
- [x] AI Chatbot can answer: *"Is this patient at risk for suicide?"* with nuanced, evidence-based response citing specific clinical factors
- [x] AI Chatbot displays appropriate clinical disclaimers and crisis protocol guidance
- [x] System prompts include safety guardrails to prevent harmful recommendations
- [x] Tool includes data source attribution (structured data vs. clinical notes)

**Quality & Documentation:**
- [x] Code follows established patterns from AI Insights (Phase 1-5)
- [x] Comprehensive logging for debugging and audit trail
- [x] Design specification complete with implementation roadmap
- [x] Test suite validates risk scoring logic against known patterns
- [x] Security review confirms access controls for sensitive risk data

---

## 3. Prerequisites & Dependencies

### 3.1 Completed Work

Before starting Suicide Prevention implementation, ensure:

- ✅ **AI Clinical Insights (Phases 1-5):** LangGraph agent infrastructure, system prompts, chatbot UI
- ✅ **Clinical Notes Domain:** PostgreSQL tables with clinical notes narrative text (TIU.TIUDocumentText)
- ✅ **Medications Domain:** Full implementation (outpatient + inpatient)
- ✅ **Encounters Domain:** Full implementation (inpatient admissions, outpatient visits)
- ✅ **Demographics Domain:** Full implementation
- ✅ **Patient Flags Domain:** Full implementation (includes MST flag support if implemented)
- ✅ **PostgreSQL Serving DB:** Operational with all prerequisite domains loaded
- ✅ **ETL Pipeline Patterns:** Bronze/Silver/Gold patterns established

### 3.2 New Dependencies

**Python Libraries:**
```bash
# Already in requirements.txt:
pandas>=2.1.0
polars>=0.19.0  # For ETL
scikit-learn>=1.3.0  # For logistic regression

# New additions needed:
nltk>=3.8.1  # For clinical notes NLP (tokenization, stopwords)
textblob>=0.17.1  # For sentiment analysis
scipy>=1.11.0  # For statistical functions (already likely present)
```

**Mock Data Generation:**
- `scripts/generate_suicide_risk_data.py` - Synthetic patient profiles with REACH VET patterns
- `scripts/generate_suicide_risk_notes.py` - Synthetic clinical notes with psychosocial risk language

**VA Reference Data:**
- ICD-10 codes for: Suicide attempt (T14.91, X71-X83, R45.851), TBI (S06.*, F07.81), PTSD (F43.1*), Chronic Pain (G89.*, M79.*)
- MST indicator (health factor or ICD: Z91.89 for personal history of trauma)
- DSM-5/ICD-10 codes for depression, anxiety, substance use disorders
- Medication classes: Opioids, Benzodiazepines, Antidepressants (from existing Dim.NationalDrug)

### 3.3 Data Freshness Requirements

**⚠️ Critical Safety Consideration:** Suicide risk factors can change rapidly, especially clinical documentation of suicidal ideation, hopelessness, or recent crisis events.

#### 3.3.1 ETL Pipeline Limitation

**Batch Processing Frequency:**
- **Current Pattern:** Nightly ETL runs (Bronze → Silver → Gold → PostgreSQL)
- **Data Currency:** T-1 (yesterday and earlier), always at least **1 day behind real-time**
- **Update Cadence:** Risk scores recalculated once per 24 hours

**High-Risk Scenario (Data Staleness):**

```
Timeline:
┌─────────────────────────────────────────────────────────────────┐
│ Day 1, 2:00 PM: Patient presents to clinic in distress         │
│                 Clinician documents in progress note:            │
│                 "Patient reports suicidal ideation with plan.   │
│                  Denies intent at this time. Safety plan        │
│                  reviewed. Will follow up in 48 hours."         │
├─────────────────────────────────────────────────────────────────┤
│ Day 1, 2:30 PM: Different clinician in another clinic queries  │
│                 med-z1 AI: "What is this patient's suicide     │
│                 risk?"                                          │
│                                                                 │
│ AI Response: Uses yesterday's ETL data (T-1)                   │
│              **MISSES TODAY'S NOTE WITH "SUICIDAL IDEATION"** │
│              Incorrectly assesses as "Standard Risk"           │
│              No safety override triggered                       │
├─────────────────────────────────────────────────────────────────┤
│ Day 2, 3:00 AM: ETL pipeline runs, processes Day 1 notes       │
│                 Risk score now reflects "High Risk" tier       │
│                 **But intervention opportunity delayed by 13hrs**│
└─────────────────────────────────────────────────────────────────┘
```

**Consequence:** Missed opportunity for immediate safety assessment and intervention during critical window.

#### 3.3.2 Dependency on Clinical Notes Timeliness

**Code-Level Impact:**

The risk scoring algorithm (Section 6.3, lines 929-935) includes a **safety override** that forces High Risk tier when recent suicidal ideation is detected:

```python
# Override: If current suicidal ideation detected in notes (< 30 days), force to High
features_df = features_df.with_columns([
    pl.when(pl.col('has_current_si_notes'))
      .then(pl.lit('High'))
      .otherwise(pl.col('risk_tier'))
      .alias('risk_tier')
])
```

**This safety mechanism depends on:**
- Clinical notes being processed through NLP pipeline (Section 9)
- `has_current_si_notes` flag calculated from narrative text keyword extraction
- Notes being available in PostgreSQL `clinical.clinical_notes` table

**If notes are T-1 stale:**
- ❌ Today's note with "suicidal ideation" **NOT PROCESSED**
- ❌ `has_current_si_notes` flag remains `FALSE`
- ❌ Safety override **WILL NOT TRIGGER**
- ❌ Patient incorrectly assessed as "Standard Risk" or "Moderate Risk"

#### 3.3.3 Production Deployment Requirement

**For ANY real-world pilot or production deployment:**

> **Real-time clinical notes access for suicide risk assessment is MANDATORY, not optional.**

**Rationale:**
1. **Patient Safety:** Cannot tolerate 13-hour delay in detecting documented crisis indicators
2. **Clinical Workflow:** Risk assessment often occurs during active clinical encounters (same-day)
3. **Liability:** Deploying a "suicide risk" tool with known T-1 data lag creates medico-legal exposure
4. **VA Standards:** Aligns with VA Mental Health Services emphasis on timely crisis identification

**Mitigation Strategy:** See Section 3.4 for VistA real-time integration approach.

### 3.4 VistA Real-Time Integration Strategy

**Status:** ⏳ **Design Required** - Not included in Phase 1 MVP (Days 1-15)

**Implementation Priority:**
- **Phase 1 (MVP):** ETL-only with prominent disclaimers (acceptable for development/testing with synthetic data)
- **Phase 2 (Pre-Production):** **MANDATORY** VistA TIU integration before any real-world pilot or deployment

#### 3.4.1 Existing Infrastructure (Reusable Pattern)

med-z1 has **operational VistA RPC Broker integration** (port 8003) with 4 clinical domains already implemented:

| Domain | RPC Handler | Status | Site Queries | Cache TTL |
|--------|-------------|--------|--------------|-----------|
| Vitals | `GMV LATEST VM` | ✅ Operational | 2 sites | 30 min |
| Encounters | `ORWCV ADMISSIONS` | ✅ Operational | 3 sites | 30 min |
| Allergies | `ORQQAL LIST` | ✅ Operational | 3-5 sites | 30 min |
| Medications | `ORWPS COVER` | ✅ Operational | 3 sites | 30 min |

**Established Pattern:**
1. User clicks "Refresh VistA" button in UI
2. HTTP POST request to Vista service (port 8003)
3. Vista service queries 2-5 VistA sites in parallel (simulated 1-3s latency per site)
4. Automatic ICN → DFN resolution (VistA uses local patient IDs, not ICN)
5. Merge/dedupe with PostgreSQL T-1 data using canonical event keys
6. Store merged result in session cache (30-minute TTL, server-side)
7. AI tools automatically access cached Vista data via `request.app.state.session`

**See:** `docs/spec/vista-rpc-broker-design.md` (v2.0) for complete technical specification

#### 3.4.2 Proposed Approach for Clinical Notes (TIU Namespace)

**VistA TIU (Text Integration Utilities) RPCs:**

```
RPC: TIU GET DOCUMENT TEXT
Namespace: TIU
Purpose: Retrieve full text of a clinical note by document IEN
Input: DFN (patient ID), Document IEN, Site Sta3n
Output: Multi-line note text (caret-delimited sections)

RPC: TIU DOCUMENTS BY CONTEXT
Purpose: List recent clinical note documents for a patient
Input: DFN, Date Range (e.g., T-30 to T-0), Note Type Filter
Output: Array of (IEN^Title^Author^Date^Status)
```

**Implementation Approach:**

```python
# vista/app/rpc_handlers/tiu_handlers.py

class TIUDocumentsByContextHandler(RPCHandler):
    """Retrieve recent clinical notes list for patient."""

    def handle(self, params: dict) -> str:
        dfn = params['dfn']
        sta3n = params['sta3n']
        lookback_days = params.get('lookback_days', 30)  # Default: last 30 days

        # Load mock data from vista/app/data/clinical_notes/
        # Filter to T-30 through T-0 (today) using T-notation dates
        # Return caret-delimited list of note metadata

        return self._format_vista_response(note_list)

class TIUGetDocumentTextHandler(RPCHandler):
    """Retrieve full note text for a specific document."""

    def handle(self, params: dict) -> str:
        dfn = params['dfn']
        sta3n = params['sta3n']
        document_ien = params['document_ien']

        # Load note text from JSON (mock) or query real VistA (future)
        # Return multi-line text in VistA format

        return note_text
```

**AI Tool Integration Workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│ User Query: "What is this patient's suicide risk?"         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 1: AI Tool checks session cache                       │
│   - Key: f"vista_clinical_notes_{user_id}_{icn}"           │
│   - Check age: < 30 minutes?                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────┴────────────────┐
        │ Cached?                         │
        └────────────────┬────────────────┘
                  Yes    │    No
                         ↓
         ┌───────────────────────────────┐
         │ Prompt user:                  │
         │ "For most current assessment, │
         │  refresh VistA data?"         │
         │ [Refresh Button]              │
         └───────────────┬───────────────┘
                         ↓
         ┌───────────────────────────────┐
         │ User clicks Refresh           │
         │ → Query 3-5 VistA sites       │
         │ → Retrieve notes (T-30 to T-0)│
         │ → Store in session cache      │
         └───────────────┬───────────────┘
                         ↓
         ┌───────────────────────────────┐
         │ Step 2: Merge PostgreSQL + Vista notes │
         │   - PostgreSQL: T-1 and earlier        │
         │   - Vista: T-0 (today) only            │
         │   - Dedupe by note_id + site           │
         └───────────────┬────────────────────────┘
                         ↓
         ┌───────────────────────────────────────┐
         │ Step 3: Run NLP on merged note corpus │
         │   - Keyword extraction (suicidal      │
         │     ideation, hopelessness, etc.)     │
         │   - Sentiment analysis                │
         │   - Generate `has_current_si_notes`   │
         └───────────────┬───────────────────────┘
                         ↓
         ┌───────────────────────────────────────┐
         │ Step 4: Recalculate risk score        │
         │   - Combine PostgreSQL features +     │
         │     fresh NLP flags                   │
         │   - Apply logistic regression         │
         │   - Check safety override (line 929)  │
         └───────────────┬───────────────────────┘
                         ↓
         ┌───────────────────────────────────────┐
         │ Step 5: Display risk assessment       │
         │   - Risk tier (High/Moderate/Standard)│
         │   - Contributing factors              │
         │   - ⚠️ Data timestamp:                │
         │     "Based on clinical notes as of    │
         │      2026-01-20 14:30 (T-0)"          │
         └───────────────────────────────────────┘
```

#### 3.4.3 Site Selection Policy for TIU Domain

**Safety-Critical Domain:** Clinical notes (like Allergies) require broader site coverage than non-critical domains.

**Recommendation:**
- **Default site queries:** 3-5 sites (top treating facilities by recent encounter count)
- **Rationale:** Patient may have documented crisis at non-primary site
- **Performance:** 3-5s total latency (1-3s per site × parallel queries)
- **Hard maximum:** 10 sites (architectural firebreak, user override required)

**See:** `docs/spec/vista-rpc-broker-design.md` Section 2.8 (Site Selection Policy)

#### 3.4.4 Merge/Deduplication Strategy

**Canonical Note Key:** `{site_sta3n}:{note_id}:{note_date}`

**Example:**
```python
# PostgreSQL T-1 note
pg_key = "500:12345678:2026-01-19"  # Anchorage, note ID 12345678, yesterday

# Vista T-0 note (today)
vista_key = "500:12345679:2026-01-20"  # Anchorage, note ID 12345679, today

# Different notes (different IDs, different dates) → Keep both
# Same note (same ID, same date) → Deduplicate, prefer Vista version
```

**See:** `docs/spec/vista-rpc-broker-design.md` Section 2.9.1 (Merge/Deduplication Rules)

#### 3.4.5 Implementation Phases & Timeline

| Phase | Scope | Data Freshness | Timeline | Risk Mitigation |
|-------|-------|----------------|----------|-----------------|
| **Phase 1 (MVP)** | ETL-only, no Vista | T-1 (stale) | Days 1-15 | ⚠️ **Prominent disclaimers in AI responses**<br>"Risk assessment based on data through [ETL date]. Clinical notes from today are not yet included. If patient presented today with concerning symptoms, verify with direct chart review." |
| **Phase 2 (Pre-Production)** | Vista TIU integration | T-0 (fresh) | +5-7 days | ✅ **MANDATORY before any real-world pilot**<br>Implement "Refresh VistA" button in AI chatbot UI<br>Session cache (30-min TTL) prevents repeated VistA queries |
| **Phase 3 (Enhancement)** | Auto-refresh on AI query | T-0 (fresh, transparent) | Future | ✅ Automatic background refresh when `check_suicide_risk_factors` tool invoked<br>No manual button required |

**Decision Guidance:**
- ✅ **Phase 1 acceptable for:** Development, testing with synthetic data, proof-of-concept demos
- ❌ **Phase 1 NOT acceptable for:** Real-world pilot, production deployment, any scenario with actual patients
- ✅ **Phase 2 required for:** Any deployment scenario involving real patient data and clinical decision-making

#### 3.4.6 Trade-offs Summary

| Approach | Data Freshness | Performance | Complexity | Production-Ready? |
|----------|----------------|-------------|------------|-------------------|
| **ETL-only (Phase 1)** | T-1 (stale, 13hr delay) | Fast (pre-computed, <50ms) | Low | ❌ No (safety risk) |
| **Vista + ETL (Phase 2)** | T-0 (fresh, includes today) | 3-5s latency on refresh | Medium | ✅ Yes |
| **Auto-refresh (Phase 3)** | T-0 (fresh, transparent UX) | 3-5s latency on every query | High | ✅ Yes (best UX) |

**Recommendation for Production Deployment:**
- Start with **Phase 2** (user-triggered "Refresh VistA")
- Monitor usage patterns and user feedback
- Evolve to **Phase 3** (auto-refresh) if latency acceptable and no performance degradation observed

---

## 4. Data Architecture

### 4.1 REACH VET 2.0 Risk Variables

The system aggregates data into a **Feature Vector** for each patient based on published REACH VET 2.0 methodology.

**What is a Feature Vector?**

A **Feature Vector** is a structured collection of measurable characteristics (features) about a patient that a statistical model uses to calculate risk. Think of it as a standardized patient profile with yes/no answers and counts for specific risk factors.

**Example Feature Vector for a patient:**
```
Patient ICN100001:
- has_prior_suicide_attempt: Yes (1)
- has_mst: Yes (1)
- no_show_count_12m: 4
- has_opioid_rx: Yes (1)
- has_concurrent_opioid_benzo: Yes (1)
- has_depression: Yes (1)
- has_hopelessness_notes: Yes (1)
- age_group_high_risk: No (0)
- is_male: Yes (1)
... (25-30 total features)
```

The statistical model multiplies each feature by its weight (e.g., prior attempt × 2.5, MST × 1.8) and sums the results to calculate an overall risk probability. This approach is called **logistic regression** and is widely used in medical risk prediction because it's transparent, reproducible, and clinically interpretable.

**Why Feature Vectors Matter:**
- **Standardization:** Every patient is evaluated using the same set of criteria
- **Explainability:** We can see exactly which factors contributed to the risk score
- **Reproducibility:** The same input data always produces the same risk score
- **Auditability:** Clinicians can review and validate the factors used in risk calculation

**Variable Categories (61 variables total in REACH VET 2.0, ~25-30 implemented in MVP):**

| Feature Category | Source Table (VistA/CDWWork) | Source Table (Oracle/CDWWork2) | Variable Logic | REACH VET Weight |
|---|---|---|---|---|
| **Prior Suicide Attempt** | `Outpat.VDiagnosis`, `TIU.TIUDocumentText` (NLP) | `Mill.DIAGNOSIS`, `Mill.CLINICAL_EVENT` | ICD-10: T14.91, X71-X83, R45.851 OR clinical note mention | **+2.5** (highest) |
| **Military Sexual Trauma (MST)** | `SPatient.HealthFactor`, `TIU.TIUDocumentText` (NLP) | `Mill.CLINICAL_EVENT` | Health Factor flag OR ICD-10: Z91.89 OR note mention | **+1.8** |
| **Missed Appointments (No-Show)** | `Outpat.Visit` | `Mill.ENCOUNTER` | Count of 'NO SHOW' status in last 12 months, ≥3 = positive | **+1.1** |
| **Active Opioid Prescription** | `RxOut.RxOutpatFill`, `Dim.NationalDrug` | `Mill.ORDERS`, `Mill.CLINICAL_EVENT` | Active Rx with NationalDrugClass = 'Opioid' | **+0.5** |
| **Active Benzodiazepine Prescription** | `RxOut.RxOutpatFill`, `Dim.NationalDrug` | `Mill.ORDERS` | Active Rx with NationalDrugClass = 'Benzodiazepine' | **+0.4** |
| **Concurrent Opioid + Benzo** | Combined medication check | Combined medication check | Both active simultaneously | **+0.8** |
| **Mental Health Diagnosis** | `Outpat.VDiagnosis` | `Mill.DIAGNOSIS` | ICD-10: F32.* (Depression), F43.1* (PTSD), F41.* (Anxiety) | **+0.6** |
| **Substance Use Disorder** | `Outpat.VDiagnosis`, `TIU.TIUDocumentText` (NLP) | `Mill.DIAGNOSIS` | ICD-10: F10-F19 (Substance Use) OR note mention | **+0.7** |
| **Traumatic Brain Injury (TBI)** | `Outpat.VDiagnosis`, `TIU.TIUDocumentText` | `Mill.DIAGNOSIS` | ICD-10: S06.*, F07.81 | **+0.5** |
| **Chronic Pain Diagnosis** | `Outpat.VDiagnosis` | `Mill.DIAGNOSIS` | ICD-10: G89.*, M79.* | **+0.3** |
| **Inpatient Psychiatric Admission** | `Inpat.Inpatient`, `Inpat.InpatientDiagnosis` | `Mill.ENCOUNTER` | Inpatient admission with psych diagnosis in last 2 years | **+1.2** |
| **Emergency Dept Utilization** | `Outpat.Visit` | `Mill.ENCOUNTER` | ≥3 ED visits in last 12 months | **+0.4** |
| **Homeless Status** | `SPatient.SPatient`, `TIU.TIUDocumentText` (NLP) | `Mill.PERSON` | Homeless indicator field OR note mention | **+0.6** |
| **Rural Residence** | `SPatient.SPatient`, `Dim.ZipCode` | `Mill.PERSON` | Derived from zip code RUCA classification | **+0.2** |
| **Age Group** | `SPatient.SPatient` | `Mill.PERSON` | Age 18-24 or 65+ (higher risk groups) | **+0.3** |
| **Male Gender** | `SPatient.SPatient` | `Mill.PERSON` | Gender = Male (higher completion rate) | **+0.2** |
| **Sleep Disorder** | `Outpat.VDiagnosis` | `Mill.DIAGNOSIS` | ICD-10: G47.* (Sleep Apnea, Insomnia) | **+0.3** |
| **Unemployment** | `TIU.TIUDocumentText` (NLP) | Social history notes | Note mentions of unemployment | **+0.4** |
| **Social Isolation** | `TIU.TIUDocumentText` (NLP) | Social history notes | Note mentions of "isolated", "alone", "no support" | **+0.5** |
| **Firearm Access** | `TIU.TIUDocumentText` (NLP) | Safety planning notes | Note mentions of firearm ownership/access | **+0.7** |
| **Recent Loss/Grief** | `TIU.TIUDocumentText` (NLP) | Progress notes | Note mentions of "loss", "death", "divorce" | **+0.4** |
| **Hopelessness Language** | `TIU.TIUDocumentText` (NLP) | Mental health notes | Sentiment analysis + keywords: "hopeless", "helpless", "no future" | **+0.9** |
| **Suicidal Ideation (Current)** | `TIU.TIUDocumentText` (NLP) | Mental health notes | Keywords: "SI", "suicidal thoughts", "wants to die" | **+3.0** (override to High) |

**Notes:**
- Weights are approximate based on published REACH VET 2.0 literature (McCarthy et al. 2015, Kessler et al. 2015)
- Actual implementation will use logistic regression coefficients (beta values) from published models
- Variables marked "NLP" require clinical notes narrative text processing
- **Suicidal Ideation (Current)** is a critical override: if detected in recent notes (< 30 days), automatically flag as High Risk regardless of score

### 4.2 Medallion Pipeline Flow

**Bronze Layer (Raw Ingestion):**
- `Outpat.Visit` → `bronze_outpat_visit.parquet`
- `RxOut.RxOutpat` + `RxOut.RxOutpatFill` → `bronze_rxout.parquet`
- `Dim.ICD10`, `Dim.NationalDrug` → `bronze_dimensions.parquet`
- `Mill.ENCOUNTER`, `Mill.DIAGNOSIS`, `Mill.ORDERS` → `bronze_mill.parquet`
- `TIU.TIUDocumentText` → `bronze_clinical_notes.parquet`

**Silver Layer (Harmonization + Feature Engineering):**
- **Utilization Harmonization:**
  - Map VistA "No Show" codes and Cerner "No Show" codes to single `visit_status` enum
  - Calculate: `no_show_count_12m`, `ed_visit_count_12m`, `last_visit_date`
- **Medication Harmonization:**
  - Map local drug names to NationalDrug classes ("Opioid", "Benzodiazepine", "Antidepressant")
  - Identify: `has_opioid_rx`, `has_benzo_rx`, `has_concurrent_opioid_benzo`
- **Diagnosis Harmonization:**
  - Standardize ICD-10 codes across VistA and Cerner
  - Boolean flags: `has_prior_attempt`, `has_tbi`, `has_ptsd`, `has_depression`, `has_chronic_pain`, `has_substance_use`
- **Clinical Notes NLP Processing:**
  - Extract: `note_mentions_hopelessness`, `note_mentions_si`, `note_mentions_firearm_access`, `note_mentions_social_isolation`
  - Sentiment scores: `mental_health_note_sentiment_avg` (0.0-1.0 scale)
- **Demographics:**
  - Calculate: `age_group`, `is_male`, `is_rural`, `is_homeless`

**Silver Output:**
- `silver_suicide_risk_features.parquet` - One row per patient with all calculated features

**Gold Layer (Feature Store + Risk Scoring):**
- **Input:** `silver_suicide_risk_features.parquet`
- **Processing:**
  - Apply logistic regression model with REACH VET 2.0 coefficients
  - Calculate: `risk_probability` (0.0-1.0), `risk_tier` (High/Moderate/Standard)
  - Generate explainability metadata (which features contributed most to score)
- **Output:**
  - `gold_suicide_risk_scores.parquet` - One row per patient with risk score and tier
  - `gold_suicide_risk_factors.parquet` - Multiple rows per patient (one per contributing factor) with weights

**Serving Layer (PostgreSQL):**
- **Load Tables:**
  - `clinical_risk_scores` - Top-level risk assessment per patient
  - `clinical_risk_factors` - Explainability factors (the "Why")
- **Performance:** Indexed on `patient_icn` for fast lookups during AI chatbot queries

---

## 5. Database Schema

### 5.1 PostgreSQL Serving Tables

**Schema: `clinical`** (follows existing pattern from `clinical.patient_vitals`, `clinical.patient_medications`)

#### Table: `clinical_risk_scores`
*Stores the top-level suicide risk assessment for a patient.*

```sql
CREATE TABLE clinical.clinical_risk_scores (
    id SERIAL PRIMARY KEY,
    patient_icn VARCHAR(50) NOT NULL,

    -- Model Metadata
    model_version VARCHAR(20) NOT NULL DEFAULT 'REACH_VET_2.0',
    model_run_date DATE NOT NULL DEFAULT CURRENT_DATE,

    -- Risk Assessment Results
    risk_probability DECIMAL(7, 6) NOT NULL,  -- e.g., 0.001500 (top 0.15%)
    risk_tier VARCHAR(20) NOT NULL,           -- 'High', 'Moderate', 'Standard'
    risk_percentile DECIMAL(5, 2),            -- e.g., 99.85 (top 0.15%)

    -- Data Sources Used
    used_structured_data BOOLEAN DEFAULT TRUE,
    used_nlp_data BOOLEAN DEFAULT FALSE,
    nlp_notes_analyzed INT DEFAULT 0,

    -- Temporal Metadata
    assessment_date DATE NOT NULL DEFAULT CURRENT_DATE,
    data_range_start DATE,  -- Lookback window start (e.g., 2 years prior)
    data_range_end DATE,    -- Lookback window end (typically 'today')

    -- Lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    calculated_at TIMESTAMP DEFAULT NOW(),

    -- Foreign Key
    CONSTRAINT fk_clinical_risk_scores_patient
        FOREIGN KEY (patient_icn)
        REFERENCES clinical.patient_demographics(icn)
);

CREATE INDEX idx_clinical_risk_scores_icn ON clinical.clinical_risk_scores(patient_icn);
CREATE INDEX idx_clinical_risk_scores_tier ON clinical.clinical_risk_scores(risk_tier);
CREATE INDEX idx_clinical_risk_scores_active ON clinical.clinical_risk_scores(is_active)
    WHERE is_active = TRUE;

COMMENT ON TABLE clinical.clinical_risk_scores IS 'Suicide risk assessment scores based on REACH VET 2.0 methodology';
COMMENT ON COLUMN clinical.clinical_risk_scores.risk_probability IS 'Estimated probability of suicide-related event (0.0-1.0)';
COMMENT ON COLUMN clinical.clinical_risk_scores.risk_tier IS 'Risk stratification: High (top 0.1%), Moderate (top 1%), Standard (all others)';
```

#### Table: `clinical_risk_factors`
*Stores the specific factors contributing to the risk score (explainability layer).*

```sql
CREATE TABLE clinical.clinical_risk_factors (
    id SERIAL PRIMARY KEY,
    score_id INTEGER NOT NULL,

    -- Factor Classification
    factor_category VARCHAR(50) NOT NULL,  -- 'Medication', 'Utilization', 'Diagnosis', 'Psychosocial', 'Demographics'
    factor_name VARCHAR(100) NOT NULL,     -- 'Missed 3+ Appointments', 'Active Opioid Rx', 'Prior Suicide Attempt'
    factor_source VARCHAR(20),             -- 'Structured', 'NLP', 'Hybrid'

    -- Contribution to Score
    factor_weight DECIMAL(5, 2) NOT NULL,  -- Beta coefficient from logistic regression (e.g., +2.5 for prior attempt)
    contribution_pct DECIMAL(5, 2),        -- Percentage of total risk score from this factor

    -- Supporting Evidence (JSONB for flexibility)
    supporting_data JSONB,
    -- Example: {"last_missed_appt": "2025-01-12", "no_show_count": 4, "timeframe": "12 months"}
    -- Example: {"medication": "Oxycodone 10mg", "start_date": "2024-06-01", "dea_schedule": "C-II"}
    -- Example: {"note_date": "2025-01-10", "note_type": "Mental Health Consult", "excerpt": "Patient reports feeling hopeless..."}

    -- Temporal
    observed_date DATE,  -- When this factor was observed (e.g., date of diagnosis, note date)

    -- Foreign Key
    CONSTRAINT fk_clinical_risk_factors_score
        FOREIGN KEY (score_id)
        REFERENCES clinical.clinical_risk_scores(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_clinical_risk_factors_score_id ON clinical.clinical_risk_factors(score_id);
CREATE INDEX idx_clinical_risk_factors_category ON clinical.clinical_risk_factors(factor_category);
CREATE INDEX idx_clinical_risk_factors_weight ON clinical.clinical_risk_factors(factor_weight DESC);

COMMENT ON TABLE clinical.clinical_risk_factors IS 'Explainability factors for suicide risk scores (the "Why")';
COMMENT ON COLUMN clinical.clinical_risk_factors.supporting_data IS 'JSONB field containing clinical evidence for this risk factor';
```

#### Example Data

**clinical_risk_scores:**
```sql
INSERT INTO clinical.clinical_risk_scores
(patient_icn, risk_probability, risk_tier, risk_percentile, used_nlp_data, nlp_notes_analyzed, data_range_start, data_range_end)
VALUES
('ICN100001', 0.002500, 'High', 99.75, TRUE, 8, '2023-01-17', '2026-01-17'),
('ICN100002', 0.000100, 'Standard', 50.25, FALSE, 0, '2024-01-17', '2026-01-17');
```

**clinical_risk_factors:**
```sql
INSERT INTO clinical.clinical_risk_factors
(score_id, factor_category, factor_name, factor_source, factor_weight, contribution_pct, supporting_data, observed_date)
VALUES
-- ICN100001 (High Risk Patient)
(1, 'Diagnosis', 'Prior Suicide Attempt', 'Structured', 2.50, 35.0,
 '{"icd10_code": "T14.91", "diagnosis_date": "2024-03-15", "source": "Outpat.VDiagnosis"}', '2024-03-15'),

(1, 'Psychosocial', 'Military Sexual Trauma (MST)', 'NLP', 1.80, 25.0,
 '{"note_date": "2024-11-20", "note_type": "Mental Health Consult", "excerpt": "Patient disclosed MST during OIF deployment..."}', '2024-11-20'),

(1, 'Utilization', 'Missed 3+ Appointments', 'Structured', 1.10, 15.0,
 '{"no_show_count": 4, "timeframe_months": 12, "last_missed": "2025-12-10"}', '2025-12-10'),

(1, 'Medication', 'Concurrent Opioid + Benzodiazepine', 'Structured', 0.80, 11.0,
 '{"opioid": "Oxycodone 10mg", "benzo": "Lorazepam 1mg", "overlap_days": 180}', '2025-01-15'),

(1, 'Psychosocial', 'Hopelessness Language in Notes', 'NLP', 0.90, 12.0,
 '{"note_date": "2025-01-05", "note_type": "Progress Note", "excerpt": "Patient states feels hopeless about recovery...", "sentiment_score": 0.15}', '2025-01-05');
```

### 5.2 Mock CDW Enhancements

**New Dimension Table: `Dim.ICD10DiagnosisCategory`** (Optional - for grouping related diagnoses)

```sql
CREATE TABLE CDWWork.Dim.ICD10DiagnosisCategory (
    CategoryID INT PRIMARY KEY,
    CategoryName VARCHAR(100),
    ICD10CodePattern VARCHAR(20),  -- e.g., 'F32.%' for Depression
    ClinicalDomain VARCHAR(50)     -- 'Mental Health', 'Trauma', 'Substance Use'
);

-- Example data
INSERT INTO CDWWork.Dim.ICD10DiagnosisCategory VALUES
(1, 'Depression', 'F32.%', 'Mental Health'),
(2, 'PTSD', 'F43.1%', 'Mental Health'),
(3, 'Suicide Attempt', 'T14.91%', 'Trauma'),
(4, 'Traumatic Brain Injury', 'S06.%', 'Trauma'),
(5, 'Opioid Use Disorder', 'F11.%', 'Substance Use');
```

**Enhancement to existing `SPatient.SPatient`:** Add `HomelessIndicator` field if not present.

**Enhancement to existing `TIU.TIUDocument_8925`:** Ensure coverage of Mental Health note types (Psychiatry Consult, Psychology Notes, Social Work Notes).

---

## 6. ETL Pipeline Design

### 6.1 Synthetic Data Generation (Pre-ETL)

**Location:** `scripts/generate_suicide_risk_data.py`

**Purpose:** Generate 100+ synthetic patient profiles exhibiting REACH VET 2.0 risk patterns for testing the suicide prevention risk assessment model.

**Patient Profile Types (Stratified Distribution):**

1. **High Risk Profiles (15 patients, top 0.1% simulation):**
   - Male, age 45-60
   - **3+ risk factors including:**
     - Prior suicide attempt (ICD-10: T14.91)
     - MST (ICD-10: Z91.89 or health factor)
     - 4+ missed appointments in last 12 months
     - Active opioid + benzodiazepine prescriptions
     - Clinical notes with hopelessness/suicidal ideation language
     - PTSD or major depression diagnosis
     - Recent psychiatric hospitalization
   - Clinical notes: 6-10 notes with psychosocial risk language

2. **Moderate Risk Profiles (25 patients, top 1% simulation):**
   - Age 25-40, mixed gender
   - **2-3 risk factors including:**
     - Chronic pain diagnosis (ICD-10: G89.29)
     - Active opioid OR benzodiazepine prescription
     - 2-3 missed appointments
     - Substance use disorder OR depression
     - Clinical notes with mild psychosocial stressors
   - Clinical notes: 4-6 notes with some risk language

3. **Standard Risk Profiles (60 patients, baseline):**
   - Age 30-70, mixed gender
   - **0-1 risk factors:**
     - No prior suicide attempts
     - No high-risk medications
     - ≤1 missed appointment
     - General medical visits only
     - Clinical notes with neutral language
   - Clinical notes: 2-4 notes, routine clinical documentation

**Data Generation Logic:**

```python
# Pseudo-code structure
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_high_risk_patient():
    """Generate a high-risk patient profile"""
    icn = f"ICN{random.randint(200000, 299999)}"

    # Demographics
    demographics = {
        'icn': icn,
        'gender': 'M',  # Higher risk
        'age': random.randint(45, 60),
        'is_homeless': random.choice([True, False]),
        'zip_rural': True if random.random() < 0.3 else False
    }

    # Diagnoses (guaranteed prior attempt + 2-3 others)
    diagnoses = [
        {'icd10': 'T14.91', 'description': 'Suicide attempt', 'date': fake.date_between('-2y', '-6m')},
        {'icd10': 'F43.12', 'description': 'PTSD, chronic', 'date': fake.date_between('-5y', '-1y')},
        {'icd10': 'F32.9', 'description': 'Major depressive disorder', 'date': fake.date_between('-3y', '-1y')},
        {'icd10': 'Z91.89', 'description': 'Military sexual trauma', 'date': fake.date_between('-10y', '-5y')}
    ]

    # Medications (opioid + benzo)
    medications = [
        {'drug_name': 'OXYCODONE HCL 10MG TAB', 'dea_schedule': 'C-II', 'start_date': fake.date_between('-180d', 'today')},
        {'drug_name': 'LORAZEPAM 1MG TAB', 'dea_schedule': 'C-IV', 'start_date': fake.date_between('-90d', 'today')}
    ]

    # Missed appointments (4-6)
    missed_appts = [
        {'date': fake.date_between('-60d', '-30d'), 'status': 'NO SHOW'},
        {'date': fake.date_between('-90d', '-61d'), 'status': 'NO SHOW'},
        {'date': fake.date_between('-120d', '-91d'), 'status': 'NO SHOW'},
        {'date': fake.date_between('-180d', '-121d'), 'status': 'NO SHOW'}
    ]

    # Clinical notes with psychosocial risk language
    clinical_notes = generate_high_risk_notes(icn, num_notes=8)

    return {
        'demographics': demographics,
        'diagnoses': diagnoses,
        'medications': medications,
        'missed_appointments': missed_appts,
        'clinical_notes': clinical_notes
    }

def generate_high_risk_notes(icn, num_notes=8):
    """Generate clinical notes with psychosocial risk language"""
    notes = []
    note_templates = [
        "Patient reports feeling hopeless about future prospects. Denies active suicidal ideation but states 'life has no meaning anymore.' Discussed safety planning.",
        "Patient disclosed history of MST during deployment to Iraq in 2005. Reports ongoing nightmares and hypervigilance. Currently engaged in CPT therapy.",
        "Patient states 'I don't see the point of continuing treatment.' Reports social isolation, estranged from family. Discussed support resources.",
        "Patient admits to having firearms at home. Discussed means restriction with patient and spouse. Patient agreed to temporary removal of firearms.",
        "Patient reports recent job loss and financial stress. States feels 'helpless to change situation.' Denies plan but admits to passive suicidal thoughts.",
        "Follow-up after no-show for last 2 appointments. Patient reports difficulty leaving house due to anxiety and depression. Re-engaged in care.",
        "Patient states chronic pain is 'unbearable' and medications not helping. Reports thoughts that 'everyone would be better off without me.' Suicide risk assessment completed - moderate risk.",
        "Patient reports recent death of close friend to suicide. States 'I understand why he did it.' Discussed grief, loss, and coping strategies."
    ]

    for i in range(num_notes):
        note_date = fake.date_between('-12m', '-7d')
        notes.append({
            'icn': icn,
            'note_date': note_date,
            'note_type': random.choice(['Mental Health Consult', 'Psychiatry Note', 'Social Work Note', 'Progress Note']),
            'note_text': random.choice(note_templates)
        })

    return notes
```

**Output Files (inserted into Mock CDW):**
- `mock/sql-server/cdwwork/insert/SPatient.SPatient_suicide_risk.sql` - 100+ patients
- `mock/sql-server/cdwwork/insert/Outpat.VDiagnosis_suicide_risk.sql` - Risk-related diagnoses
- `mock/sql-server/cdwwork/insert/TIU.TIUDocumentText_suicide_risk.sql` - Clinical notes with psychosocial language

### 6.2 Bronze ETL

**Location:** `etl/bronze/extract_suicide_risk_sources.py`

**Purpose:** Extract raw data from Mock CDW for suicide risk assessment.

**Source Tables:**
- `SPatient.SPatient` → Demographics, homeless status
- `Outpat.Visit` → Appointment utilization, no-shows, ED visits
- `Outpat.VDiagnosis` → Mental health diagnoses, suicide attempts, chronic pain
- `RxOut.RxOutpat` + `RxOut.RxOutpatFill` → Active medications (opioids, benzos)
- `Inpat.Inpatient` + `Inpat.InpatientDiagnosis` → Psychiatric admissions
- `TIU.TIUDocument_8925` + `TIU.TIUDocumentText` → Clinical notes
- `Dim.NationalDrug` → Medication classes
- `Dim.ICD10` → Diagnosis codes and descriptions

**Output Parquet Files:**
- `lake/bronze/suicide_risk/demographics.parquet`
- `lake/bronze/suicide_risk/visits.parquet`
- `lake/bronze/suicide_risk/diagnoses.parquet`
- `lake/bronze/suicide_risk/medications.parquet`
- `lake/bronze/suicide_risk/inpatient.parquet`
- `lake/bronze/suicide_risk/clinical_notes.parquet`
- `lake/bronze/suicide_risk/dim_drugs.parquet`
- `lake/bronze/suicide_risk/dim_icd10.parquet`

### 6.3 Silver ETL (Feature Engineering)

**Location:** `etl/silver/transform_suicide_risk_features.py`

**Purpose:** Harmonize data across VistA/Cerner sources, calculate derived features, perform clinical notes NLP.

**This is the Feature Engineering Layer:**

Feature engineering transforms raw clinical data into the calculated features (feature vector components) used by the risk scoring model. This is a critical AI/ML step that converts disparate data formats into standardized, quantifiable risk indicators.

**What Happens in Feature Engineering:**
- **Raw data** (individual appointment records, medication names, note text) → **Calculated features** (no-show counts, medication class flags, sentiment scores)
- Each subsection below shows a specific transformation: raw clinical data → engineered feature
- The output is a single row per patient with 25-30 numeric/boolean features ready for the logistic regression model

**Example Transformation:**
```
Raw data:       4 appointment records with "NO SHOW" status
                ↓ Feature Engineering ↓
Engineered feature:  no_show_count_12m = 4 (used by model with weight 1.1)
```

**Key Transformations:**

#### 6.3.1 Utilization Features

```python
def calculate_utilization_features(visits_df):
    """
    Calculate appointment utilization metrics from VistA and Cerner visits.

    Features:
    - no_show_count_12m: Count of missed appointments in last 12 months
    - ed_visit_count_12m: Count of ED visits in last 12 months
    - last_visit_date: Most recent visit date
    - total_visits_12m: Total visit count (for no-show rate calculation)
    """
    import polars as pl
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=365)

    # Harmonize VistA and Cerner visit status codes
    visits_df = visits_df.with_columns([
        pl.when(pl.col('VisitStatusCode').is_in(['NO SHOW', 'No-Show', 'NS']))
          .then(pl.lit('NO_SHOW'))
          .when(pl.col('LocationType') == 'Emergency Department')
          .then(pl.lit('ED_VISIT'))
          .otherwise(pl.lit('REGULAR'))
          .alias('visit_type_normalized')
    ])

    # Filter to last 12 months
    visits_12m = visits_df.filter(pl.col('VisitDateTime') >= cutoff_date)

    # Aggregate by patient
    utilization_features = visits_12m.group_by('PatientICN').agg([
        pl.col('visit_type_normalized').filter(pl.col('visit_type_normalized') == 'NO_SHOW')
          .count().alias('no_show_count_12m'),
        pl.col('visit_type_normalized').filter(pl.col('visit_type_normalized') == 'ED_VISIT')
          .count().alias('ed_visit_count_12m'),
        pl.col('VisitDateTime').max().alias('last_visit_date'),
        pl.col('visit_type_normalized').count().alias('total_visits_12m')
    ])

    # Calculate no-show rate
    utilization_features = utilization_features.with_columns([
        (pl.col('no_show_count_12m') / pl.col('total_visits_12m')).alias('no_show_rate')
    ])

    return utilization_features
```

#### 6.3.2 Medication Features

```python
def calculate_medication_features(medications_df, drug_dim_df):
    """
    Identify high-risk medication classes (opioids, benzodiazepines, antidepressants).

    Features:
    - has_opioid_rx: Boolean - Active opioid prescription
    - has_benzo_rx: Boolean - Active benzodiazepine prescription
    - has_concurrent_opioid_benzo: Boolean - Both active simultaneously
    - has_antidepressant_rx: Boolean - Active antidepressant
    """
    import polars as pl
    from datetime import datetime, timedelta

    # Join medications with drug dimension to get drug class
    meds_with_class = medications_df.join(
        drug_dim_df,
        left_on='NationalDrugSID',
        right_on='NationalDrugSID',
        how='left'
    )

    # Filter to active prescriptions (dispensed in last 90 days)
    active_cutoff = datetime.now() - timedelta(days=90)
    active_meds = meds_with_class.filter(
        pl.col('DispensedDate') >= active_cutoff
    )

    # Classify drug classes (based on NationalDrugClass or drug name patterns)
    active_meds = active_meds.with_columns([
        pl.when(pl.col('NationalDrugClass').str.contains('(?i)opioid|opiate|codeine|morphine|oxycodone|hydrocodone|fentanyl'))
          .then(pl.lit(True))
          .otherwise(pl.lit(False))
          .alias('is_opioid'),

        pl.when(pl.col('NationalDrugClass').str.contains('(?i)benzodiazepine|alprazolam|lorazepam|diazepam|clonazepam'))
          .then(pl.lit(True))
          .otherwise(pl.lit(False))
          .alias('is_benzo'),

        pl.when(pl.col('NationalDrugClass').str.contains('(?i)antidepressant|ssri|snri|sertraline|escitalopram|fluoxetine'))
          .then(pl.lit(True))
          .otherwise(pl.lit(False))
          .alias('is_antidepressant')
    ])

    # Aggregate by patient
    med_features = active_meds.group_by('PatientICN').agg([
        pl.col('is_opioid').any().alias('has_opioid_rx'),
        pl.col('is_benzo').any().alias('has_benzo_rx'),
        pl.col('is_antidepressant').any().alias('has_antidepressant_rx')
    ])

    # Calculate concurrent opioid + benzo
    med_features = med_features.with_columns([
        (pl.col('has_opioid_rx') & pl.col('has_benzo_rx')).alias('has_concurrent_opioid_benzo')
    ])

    return med_features
```

#### 6.3.3 Diagnosis Features

```python
def calculate_diagnosis_features(diagnoses_df, icd10_dim_df):
    """
    Identify mental health and trauma-related diagnoses from ICD-10 codes.

    Features:
    - has_prior_attempt: Prior suicide attempt (T14.91, X71-X83, R45.851)
    - has_ptsd: PTSD diagnosis (F43.1*)
    - has_depression: Depression diagnosis (F32.*, F33.*)
    - has_anxiety: Anxiety disorder (F41.*)
    - has_substance_use: Substance use disorder (F10-F19)
    - has_tbi: Traumatic brain injury (S06.*, F07.81)
    - has_chronic_pain: Chronic pain (G89.*, M79.*)
    - has_sleep_disorder: Sleep disorder (G47.*)
    - has_mst_icd: MST indicator via ICD code (Z91.89)
    """
    import polars as pl
    import re

    # Join with ICD10 dimension for code descriptions
    dx_with_codes = diagnoses_df.join(
        icd10_dim_df,
        left_on='ICD10SID',
        right_on='ICD10SID',
        how='left'
    )

    # Create boolean flags for each diagnosis category
    dx_with_codes = dx_with_codes.with_columns([
        # Suicide attempt codes
        pl.col('ICD10Code').str.contains(r'^(T14\.91|X7[1-9]|X8[0-3]|R45\.851)')
          .alias('is_prior_attempt'),

        # Mental health diagnoses
        pl.col('ICD10Code').str.contains(r'^F43\.1')
          .alias('is_ptsd'),
        pl.col('ICD10Code').str.contains(r'^F3[23]\.')
          .alias('is_depression'),
        pl.col('ICD10Code').str.contains(r'^F41\.')
          .alias('is_anxiety'),
        pl.col('ICD10Code').str.contains(r'^F1[0-9]\.')
          .alias('is_substance_use'),

        # Trauma and pain
        pl.col('ICD10Code').str.contains(r'^(S06\.|F07\.81)')
          .alias('is_tbi'),
        pl.col('ICD10Code').str.contains(r'^(G89\.|M79\.)')
          .alias('is_chronic_pain'),

        # Other risk factors
        pl.col('ICD10Code').str.contains(r'^G47\.')
          .alias('is_sleep_disorder'),
        pl.col('ICD10Code').str.contains(r'^Z91\.89')
          .alias('is_mst_icd')
    ])

    # Aggregate by patient (any diagnosis = True)
    dx_features = dx_with_codes.group_by('PatientICN').agg([
        pl.col('is_prior_attempt').any().alias('has_prior_attempt'),
        pl.col('is_ptsd').any().alias('has_ptsd'),
        pl.col('is_depression').any().alias('has_depression'),
        pl.col('is_anxiety').any().alias('has_anxiety'),
        pl.col('is_substance_use').any().alias('has_substance_use'),
        pl.col('is_tbi').any().alias('has_tbi'),
        pl.col('is_chronic_pain').any().alias('has_chronic_pain'),
        pl.col('is_sleep_disorder').any().alias('has_sleep_disorder'),
        pl.col('is_mst_icd').any().alias('has_mst_icd')
    ])

    return dx_features
```

#### 6.3.4 Clinical Notes NLP Features (See Section 9)

**Output Parquet File:**
- `lake/silver/suicide_risk/patient_risk_features.parquet` - One row per patient with all calculated features

### 6.4 Gold ETL (Risk Scoring)

**Location:** `etl/gold/calculate_suicide_risk_scores.py`

**Purpose:** Apply calibrated logistic regression model to calculate risk scores and generate explainability metadata.

**Risk Scoring Logic:**

```python
def calculate_reach_vet_score(features_df):
    """
    Apply REACH VET 2.0 logistic regression model to calculate risk scores.

    Model: log(p / (1 - p)) = β0 + Σ(βi * xi)
    Where:
    - p = probability of suicide-related event
    - β0 = intercept (calibrated to base rate)
    - βi = coefficient for feature i (from published literature)
    - xi = feature value (0 or 1 for binary features, continuous for some)
    """
    import polars as pl
    import numpy as np
    from scipy.special import expit  # Logistic sigmoid function

    # REACH VET 2.0 coefficients (from McCarthy et al. 2015, Kessler et al. 2015)
    # Note: These are approximate - actual implementation should use published values
    COEFFICIENTS = {
        'intercept': -7.5,  # Calibrated to ~0.1% base rate
        'has_prior_attempt': 2.50,
        'has_mst': 1.80,
        'has_psych_admission_2y': 1.20,
        'no_show_count_12m_ge3': 1.10,
        'has_hopelessness_notes': 0.90,
        'has_concurrent_opioid_benzo': 0.80,
        'has_firearm_access_notes': 0.70,
        'has_substance_use': 0.70,
        'has_depression': 0.60,
        'has_homeless': 0.60,
        'has_tbi': 0.50,
        'has_social_isolation_notes': 0.50,
        'has_opioid_rx': 0.50,
        'ed_visit_count_12m_ge3': 0.40,
        'has_benzo_rx': 0.40,
        'has_recent_loss_notes': 0.40,
        'has_unemployment_notes': 0.40,
        'has_chronic_pain': 0.30,
        'has_sleep_disorder': 0.30,
        'age_group_high_risk': 0.30,  # 18-24 or 65+
        'is_male': 0.20,
        'is_rural': 0.20
    }

    # Calculate linear combination (log-odds)
    features_df = features_df.with_columns([
        pl.lit(COEFFICIENTS['intercept']).alias('logit')
    ])

    # Add contribution from each feature
    for feature, coef in COEFFICIENTS.items():
        if feature == 'intercept':
            continue
        if feature in features_df.columns:
            features_df = features_df.with_columns([
                (pl.col('logit') + (pl.col(feature).cast(pl.Float64) * coef)).alias('logit')
            ])

    # Convert log-odds to probability using sigmoid
    features_df = features_df.with_columns([
        pl.col('logit').map_elements(lambda x: expit(x), return_dtype=pl.Float64).alias('risk_probability')
    ])

    # Assign risk tier based on probability percentiles
    # High: Top 0.1% (p >= 0.0015), Moderate: Top 1% (p >= 0.0003), Standard: All others
    features_df = features_df.with_columns([
        pl.when(pl.col('risk_probability') >= 0.0015)
          .then(pl.lit('High'))
          .when(pl.col('risk_probability') >= 0.0003)
          .then(pl.lit('Moderate'))
          .otherwise(pl.lit('Standard'))
          .alias('risk_tier')
    ])

    # Override: If current suicidal ideation detected in notes (< 30 days), force to High
    features_df = features_df.with_columns([
        pl.when(pl.col('has_current_si_notes'))
          .then(pl.lit('High'))
          .otherwise(pl.col('risk_tier'))
          .alias('risk_tier')
    ])

    return features_df

def generate_explainability_factors(features_df):
    """
    Generate risk factor contributions for explainability.

    Returns: DataFrame with one row per patient per contributing factor.
    """
    import polars as pl

    # Explode features into long format (patient_icn, feature_name, feature_value, coefficient)
    # Only include features that are True (contributing to risk)

    explainability_rows = []

    for row in features_df.iter_rows(named=True):
        icn = row['PatientICN']
        risk_prob = row['risk_probability']

        # Calculate total contribution (sum of all active features * coefficients)
        total_contribution = 0
        for feature, coef in COEFFICIENTS.items():
            if feature == 'intercept':
                continue
            if feature in row and row[feature]:
                total_contribution += coef

        # Generate factor rows
        for feature, coef in COEFFICIENTS.items():
            if feature == 'intercept':
                continue
            if feature in row and row[feature]:
                # Map feature name to human-readable factor name
                factor_name = FEATURE_NAME_MAPPING.get(feature, feature)
                factor_category = FEATURE_CATEGORY_MAPPING.get(feature, 'Other')
                factor_source = FEATURE_SOURCE_MAPPING.get(feature, 'Structured')

                contribution_pct = (coef / total_contribution) * 100 if total_contribution > 0 else 0

                explainability_rows.append({
                    'patient_icn': icn,
                    'factor_category': factor_category,
                    'factor_name': factor_name,
                    'factor_source': factor_source,
                    'factor_weight': coef,
                    'contribution_pct': contribution_pct
                })

    return pl.DataFrame(explainability_rows)

# Feature name mappings for human-readable output
FEATURE_NAME_MAPPING = {
    'has_prior_attempt': 'Prior Suicide Attempt',
    'has_mst': 'Military Sexual Trauma (MST)',
    'has_psych_admission_2y': 'Recent Psychiatric Hospitalization',
    'no_show_count_12m_ge3': 'Missed 3+ Appointments (12mo)',
    'has_hopelessness_notes': 'Hopelessness Language in Clinical Notes',
    'has_concurrent_opioid_benzo': 'Concurrent Opioid + Benzodiazepine',
    'has_firearm_access_notes': 'Firearm Access Mentioned in Notes',
    'has_substance_use': 'Substance Use Disorder',
    'has_depression': 'Major Depressive Disorder',
    'has_homeless': 'Homeless Status',
    'has_tbi': 'Traumatic Brain Injury',
    'has_social_isolation_notes': 'Social Isolation Mentioned in Notes',
    'has_opioid_rx': 'Active Opioid Prescription',
    'ed_visit_count_12m_ge3': '3+ Emergency Department Visits (12mo)',
    'has_benzo_rx': 'Active Benzodiazepine Prescription',
    'has_recent_loss_notes': 'Recent Loss/Grief Mentioned in Notes',
    'has_unemployment_notes': 'Unemployment Mentioned in Notes',
    'has_chronic_pain': 'Chronic Pain Diagnosis',
    'has_sleep_disorder': 'Sleep Disorder Diagnosis',
    'age_group_high_risk': 'High-Risk Age Group (18-24 or 65+)',
    'is_male': 'Male Gender',
    'is_rural': 'Rural Residence'
}

FEATURE_CATEGORY_MAPPING = {
    'has_prior_attempt': 'Diagnosis',
    'has_mst': 'Psychosocial',
    'has_psych_admission_2y': 'Utilization',
    'no_show_count_12m_ge3': 'Utilization',
    'has_hopelessness_notes': 'Psychosocial',
    'has_concurrent_opioid_benzo': 'Medication',
    'has_firearm_access_notes': 'Psychosocial',
    'has_substance_use': 'Diagnosis',
    'has_depression': 'Diagnosis',
    'has_homeless': 'Psychosocial',
    'has_tbi': 'Diagnosis',
    'has_social_isolation_notes': 'Psychosocial',
    'has_opioid_rx': 'Medication',
    'ed_visit_count_12m_ge3': 'Utilization',
    'has_benzo_rx': 'Medication',
    'has_recent_loss_notes': 'Psychosocial',
    'has_unemployment_notes': 'Psychosocial',
    'has_chronic_pain': 'Diagnosis',
    'has_sleep_disorder': 'Diagnosis',
    'age_group_high_risk': 'Demographics',
    'is_male': 'Demographics',
    'is_rural': 'Demographics'
}

FEATURE_SOURCE_MAPPING = {
    'has_hopelessness_notes': 'NLP',
    'has_firearm_access_notes': 'NLP',
    'has_social_isolation_notes': 'NLP',
    'has_recent_loss_notes': 'NLP',
    'has_unemployment_notes': 'NLP',
    # All others default to 'Structured'
}
```

**Output Parquet Files:**
- `lake/gold/suicide_risk/patient_risk_scores.parquet` - Risk scores and tiers
- `lake/gold/suicide_risk/patient_risk_factors.parquet` - Explainability factors

### 6.5 PostgreSQL Load

**Location:** `etl/load/load_suicide_risk_to_postgres.py`

**Purpose:** Load risk scores and factors from Gold Parquet to PostgreSQL serving database.

**Load Logic:**
```python
import polars as pl
import psycopg2
from config import POSTGRES_CONNECTION_STRING

def load_risk_scores_to_postgres():
    """Load risk scores and factors to PostgreSQL"""

    # Read Gold Parquet files
    scores_df = pl.read_parquet('lake/gold/suicide_risk/patient_risk_scores.parquet')
    factors_df = pl.read_parquet('lake/gold/suicide_risk/patient_risk_factors.parquet')

    # Connect to PostgreSQL
    conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
    cursor = conn.cursor()

    # Truncate existing data (development only)
    cursor.execute("TRUNCATE TABLE clinical.clinical_risk_scores CASCADE;")

    # Insert risk scores
    for row in scores_df.iter_rows(named=True):
        cursor.execute("""
            INSERT INTO clinical.clinical_risk_scores
            (patient_icn, risk_probability, risk_tier, risk_percentile,
             used_nlp_data, nlp_notes_analyzed, data_range_start, data_range_end)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            row['patient_icn'],
            row['risk_probability'],
            row['risk_tier'],
            row['risk_percentile'],
            row['used_nlp_data'],
            row['nlp_notes_analyzed'],
            row['data_range_start'],
            row['data_range_end']
        ))
        score_id = cursor.fetchone()[0]

        # Insert corresponding risk factors
        patient_factors = factors_df.filter(pl.col('patient_icn') == row['patient_icn'])
        for factor_row in patient_factors.iter_rows(named=True):
            cursor.execute("""
                INSERT INTO clinical.clinical_risk_factors
                (score_id, factor_category, factor_name, factor_source,
                 factor_weight, contribution_pct, supporting_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                score_id,
                factor_row['factor_category'],
                factor_row['factor_name'],
                factor_row['factor_source'],
                factor_row['factor_weight'],
                factor_row['contribution_pct'],
                '{}')  # Supporting data added in Phase 2
            ))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Loaded {len(scores_df)} risk scores and {len(factors_df)} risk factors to PostgreSQL")
```

### 6.6 Risk Model Configuration Management

**Problem Statement:**

The current REACH VET 2.0 logistic regression implementation (Section 8.3) hardcodes regression coefficients directly in Python code:

```python
# app/services/suicide_risk_scoring.py (lines 871-897)
COEFFICIENTS = {
    'prior_attempt': 2.5,         # Hardcoded β weight
    'prior_hospitalization': 1.8,
    'mst_exposure': 1.8,
    'recent_ed_visit': 1.2,
    'psychiatric_diagnosis': 1.5,
    # ... additional coefficients
}

def calculate_reach_vet_score(risk_factors: dict) -> float:
    """Calculate REACH VET 2.0 logistic regression score."""
    score = 0.0
    for factor, weight in COEFFICIENTS.items():
        if risk_factors.get(factor):
            score += weight
    return score
```

**Clinical Model Calibration Reality:**

- **Model drift:** Predictive models degrade over time as population characteristics change
- **Validation cycles:** VA periodically validates REACH VET against new cohort data (e.g., FY2024 vs FY2025)
- **Coefficient updates:** Clinical findings may indicate "Prior Attempt" weight should be 2.6 instead of 2.5
- **Deployment friction:** Hardcoded coefficients require:
  1. Code change in Python module
  2. Git commit/review
  3. Deployment pipeline (build, test, stage, prod)
  4. Potential rollback complexity if model performs poorly

**This friction discourages clinical model iteration and creates operational risk.**

---

#### 6.6.1 Recommended Approach: Database-Backed Configuration (Option A)

**Rationale:**

- **Clinical governance:** Model coefficients are clinical parameters, not application code
- **Hot-swappable:** Update coefficients without code deployment
- **Audit trail:** Track model version history and validation results
- **Multi-model support:** Enable A/B testing of model variants
- **Production-ready:** Standard pattern for ML model management

**Database Schema:**

```sql
-- PostgreSQL schema
CREATE TABLE reference.suicide_risk_model_coefficients (
    model_version VARCHAR(20) PRIMARY KEY,     -- e.g., 'REACH_VET_2.0_FY2024'
    is_active BOOLEAN NOT NULL DEFAULT FALSE,  -- Only one active model at a time
    effective_date DATE NOT NULL,              -- When this model version became active
    validation_data JSONB,                     -- Link to validation study results
    coefficients JSONB NOT NULL,               -- Risk factor weights (JSON object)
    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR(100),                   -- Who deployed this model
    notes TEXT                                 -- Clinical rationale for changes
);

-- Example row
INSERT INTO reference.suicide_risk_model_coefficients VALUES (
    'REACH_VET_2.0_FY2024',
    TRUE,                                      -- Active model
    '2024-10-01',
    '{"auc": 0.72, "sensitivity": 0.68, "specificity": 0.75}',
    '{
        "prior_attempt": 2.5,
        "prior_hospitalization": 1.8,
        "mst_exposure": 1.8,
        "recent_ed_visit": 1.2,
        "psychiatric_diagnosis": 1.5,
        "inpatient_mh_visit": 1.3,
        "poly_substance_abuse": 1.4,
        "high_risk_medications": 0.8,
        "sleep_disorders": 0.6,
        "chronic_pain": 0.7
    }'::JSONB,
    '2024-10-01 14:30:00',
    'clinical.research@va.gov',
    'FY2024 validation cohort (n=150,000). AUC improved from 0.70 to 0.72.'
);

-- Ensure only one active model
CREATE UNIQUE INDEX idx_active_model ON reference.suicide_risk_model_coefficients (is_active)
    WHERE is_active = TRUE;
```

**Application Code Changes:**

```python
# app/services/suicide_risk_scoring.py (updated implementation)
import psycopg2
from config import DATABASE_URL

def get_active_model_coefficients() -> dict:
    """
    Retrieve active REACH VET model coefficients from database.

    Returns:
        dict: Risk factor coefficients (e.g., {'prior_attempt': 2.5, ...})

    Raises:
        RuntimeError: If no active model is configured
    """
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_version, coefficients
        FROM reference.suicide_risk_model_coefficients
        WHERE is_active = TRUE
    """)

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise RuntimeError("No active suicide risk model configured in database")

    model_version, coefficients_json = row
    print(f"Loaded suicide risk model: {model_version}")

    return coefficients_json  # PostgreSQL JSONB returns as Python dict


def calculate_reach_vet_score(risk_factors: dict) -> float:
    """
    Calculate REACH VET 2.0 logistic regression score.

    Args:
        risk_factors: Boolean flags for each risk factor

    Returns:
        float: Raw logistic regression score (higher = higher risk)
    """
    coefficients = get_active_model_coefficients()  # Load from DB

    score = 0.0
    for factor, weight in coefficients.items():
        if risk_factors.get(factor):
            score += weight

    return score
```

**Operational Workflow:**

```bash
# Clinical team validates new model coefficients (off-platform)
# Research study shows "prior_attempt" should be 2.6 (was 2.5)

# Database administrator updates model (no code deployment)
psql -U postgres -d medzero <<EOF
BEGIN;

-- Mark old model inactive
UPDATE reference.suicide_risk_model_coefficients
SET is_active = FALSE
WHERE model_version = 'REACH_VET_2.0_FY2024';

-- Insert new model
INSERT INTO reference.suicide_risk_model_coefficients VALUES (
    'REACH_VET_2.0_FY2025',
    TRUE,
    '2025-02-01',
    '{"auc": 0.74, "sensitivity": 0.70, "specificity": 0.76}',
    '{
        "prior_attempt": 2.6,                  -- Updated coefficient
        "prior_hospitalization": 1.8,
        "mst_exposure": 1.8,
        "recent_ed_visit": 1.2,
        "psychiatric_diagnosis": 1.5,
        "inpatient_mh_visit": 1.3,
        "poly_substance_abuse": 1.4,
        "high_risk_medications": 0.8,
        "sleep_disorders": 0.6,
        "chronic_pain": 0.7
    }'::JSONB,
    NOW(),
    'clinical.research@va.gov',
    'FY2025 validation. Increased prior_attempt weight based on 200K patient cohort.'
);

COMMIT;
EOF

# Restart application to clear any cached coefficients (optional)
# Or: wait 30 minutes for cache TTL if caching is implemented

# New model takes effect immediately for all new risk calculations
```

**Benefits:**

| Benefit | Description |
|---------|-------------|
| **Rapid iteration** | Update coefficients in minutes, not days/weeks |
| **Clinical ownership** | Research team controls model parameters directly |
| **Audit trail** | Full history of model versions and justifications |
| **Rollback safety** | Revert to previous model with single UPDATE statement |
| **Multi-model testing** | Run A/B tests by switching active model per user cohort |
| **No deployment risk** | Zero code changes = zero regression risk |

---

#### 6.6.2 Alternative Approach: JSON Configuration File (Option B - Not Recommended)

**Approach:**

Store coefficients in a version-controlled JSON file (e.g., `config/reach_vet_coefficients.json`):

```json
{
    "model_version": "REACH_VET_2.0_FY2024",
    "effective_date": "2024-10-01",
    "coefficients": {
        "prior_attempt": 2.5,
        "prior_hospitalization": 1.8,
        "mst_exposure": 1.8,
        "recent_ed_visit": 1.2,
        "psychiatric_diagnosis": 1.5,
        "inpatient_mh_visit": 1.3,
        "poly_substance_abuse": 1.4,
        "high_risk_medications": 0.8,
        "sleep_disorders": 0.6,
        "chronic_pain": 0.7
    }
}
```

**Trade-offs:**

| Aspect | JSON File | Database Table |
|--------|-----------|----------------|
| **Ease of update** | Requires code deployment | No deployment needed |
| **Version control** | Git history ✅ | Database migrations |
| **Audit trail** | Git blame | Explicit audit columns ✅ |
| **Multi-model support** | Manual file swaps | Query-based switching ✅ |
| **Rollback** | Git revert + deploy | Single UPDATE statement ✅ |
| **Clinical governance** | Engineers involved ❌ | Clinical team owns ✅ |

**Verdict:** JSON configuration is better than hardcoded constants but still requires deployment friction. **Database approach (Option A) is strongly recommended for production.**

---

#### 6.6.3 Implementation Guidance

**Phase 1 (MVP - Hardcoded):**

- Use hardcoded `COEFFICIENTS` dictionary in `app/services/suicide_risk_scoring.py`
- **Rationale:** Faster initial development, deferred complexity
- **Risk:** Production deployment will require database migration before go-live

**Phase 2 (Database-Backed - Production Requirement):**

1. **Create reference table:**
   ```bash
   psql -U postgres -d medzero -f db/ddl/suicide_risk_model_coefficients.sql
   ```

2. **Seed initial model:**
   ```bash
   psql -U postgres -d medzero -f db/seeds/reach_vet_2.0_baseline.sql
   ```

3. **Update application code:**
   - Replace hardcoded `COEFFICIENTS` with `get_active_model_coefficients()` function
   - Add caching (30-minute TTL) to avoid per-request DB queries
   - Add fallback logic if DB query fails (return hardcoded defaults + log error)

4. **Test model switching:**
   ```bash
   pytest scripts/test_model_coefficient_switching.py
   ```

5. **Document operational procedures:**
   - How to validate new coefficients (clinical research workflow)
   - How to deploy new model (SQL script template)
   - How to rollback if model performs poorly (SQL revert script)

**Migration Path:**

```python
# Backward-compatible implementation (supports both hardcoded and DB-backed)
FALLBACK_COEFFICIENTS = {
    'prior_attempt': 2.5,
    'prior_hospitalization': 1.8,
    # ... hardcoded defaults
}

def get_active_model_coefficients() -> dict:
    """Load coefficients from DB, fallback to hardcoded if unavailable."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT coefficients FROM reference.suicide_risk_model_coefficients
            WHERE is_active = TRUE
        """)
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row:
            return row[0]  # Database coefficients
        else:
            logger.warning("No active model in DB, using fallback coefficients")
            return FALLBACK_COEFFICIENTS

    except Exception as e:
        logger.error(f"Failed to load model coefficients from DB: {e}")
        return FALLBACK_COEFFICIENTS  # Graceful degradation
```

---

#### 6.6.4 Clinical Governance Process (Future)

**Model Update Workflow (Production):**

1. **Validation Study:** Clinical research team validates new coefficients against holdout cohort
2. **Approval:** Clinical governance committee reviews validation metrics (AUC, sensitivity, specificity)
3. **Staging Deployment:** Database administrator inserts new model version with `is_active = FALSE`
4. **A/B Testing (Optional):** Split traffic 80/20 between old/new model, monitor outcomes for 2 weeks
5. **Production Cutover:** Set new model `is_active = TRUE`, old model `is_active = FALSE`
6. **Monitoring:** Track risk score distribution changes, alert on anomalies
7. **Rollback Plan:** Revert to previous model if clinical outcomes degrade

**Example Monitoring Query:**

```sql
-- Compare risk score distributions before/after model change
SELECT
    model_version,
    risk_tier,
    COUNT(*) as patient_count,
    ROUND(AVG(risk_score), 2) as avg_score
FROM clinical.suicide_risk_scores
WHERE calculation_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY model_version, risk_tier
ORDER BY model_version, risk_tier;
```

---



## 7. AI Subsystem Integration (LangGraph)

### 7.1 New AI Tool: `check_suicide_risk_factors`

**Location:** `ai/tools/risk_tools.py`

**Purpose:** Enables the AI agent to query and explain suicide risk assessments in a clinically appropriate manner.

**Tool Implementation:**

```python
from langchain.tools import tool
from typing import Optional
import psycopg2
from config import POSTGRES_CONNECTION_STRING
import json

@tool
def check_suicide_risk_factors(patient_icn: str) -> str:
    """
    Analyzes the patient's suicide risk profile based on REACH VET 2.0 predictive model.

    This tool queries the clinical risk assessment database to retrieve:
    - Overall risk tier (High, Moderate, Standard)
    - Specific contributing clinical factors
    - Data sources used (structured data, clinical notes NLP)

    Use this tool when clinicians ask about:
    - Suicide risk or safety concerns
    - Mental health risk assessment
    - REACH VET or predictive risk scores

    Args:
        patient_icn: Patient's Integrated Care Number (ICN)

    Returns:
        Formatted risk assessment with explainability factors and clinical guidance
    """

    conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
    cursor = conn.cursor()

    try:
        # Query latest active risk score
        cursor.execute("""
            SELECT
                id, risk_probability, risk_tier, risk_percentile,
                used_nlp_data, nlp_notes_analyzed,
                assessment_date, model_version
            FROM clinical.clinical_risk_scores
            WHERE patient_icn = %s AND is_active = TRUE
            ORDER BY calculated_at DESC
            LIMIT 1
        """, (patient_icn,))

        score_row = cursor.fetchone()

        if not score_row:
            return (
                "**No suicide risk assessment available for this patient.**\n\n"
                "No REACH VET risk score has been calculated. This may indicate:\n"
                "- Patient is new to the system\n"
                "- Insufficient data for risk modeling\n"
                "- Risk assessment pending (models run monthly)\n\n"
                "Consider conducting a clinical suicide risk assessment per VA/DoD CPG guidelines."
            )

        score_id, prob, tier, percentile, used_nlp, nlp_notes_count, assessment_date, model_version = score_row

        # If Standard risk, provide brief reassurance
        if tier == 'Standard':
            return (
                f"**Risk Assessment: Standard Risk** ({model_version})\n\n"
                f"This patient is in the standard risk category based on current data.\n"
                f"- **Risk Probability:** {prob:.4f} ({percentile:.1f}th percentile)\n"
                f"- **Assessment Date:** {assessment_date}\n\n"
                "While no elevated risk factors were identified by the predictive model, "
                "clinical judgment should always guide individual patient assessment. "
                "Consider screening for suicide risk if clinically indicated."
            )

        # For Moderate or High risk, retrieve contributing factors
        cursor.execute("""
            SELECT
                factor_category, factor_name, factor_source,
                factor_weight, contribution_pct, supporting_data
            FROM clinical.clinical_risk_factors
            WHERE score_id = %s
            ORDER BY factor_weight DESC
            LIMIT 8
        """, (score_id,))

        factors = cursor.fetchall()

        # Build response
        risk_emoji = "🔴" if tier == "High" else "🟡"
        response = f"{risk_emoji} **Risk Assessment: {tier} Risk** ({model_version})\n\n"
        response += f"**Risk Probability:** {prob:.4f} ({percentile:.1f}th percentile)\n"
        response += f"**Assessment Date:** {assessment_date}\n"

        if used_nlp:
            response += f"**Clinical Notes Analyzed:** {nlp_notes_count} notes\n"

        response += "\n**Key Contributing Factors:**\n"

        for factor in factors:
            category, name, source, weight, contrib_pct, supporting_json = factor
            source_badge = "📝 NLP" if source == "NLP" else "📊 Structured"
            response += f"{contrib_pct:.1f}% - **{name}** {source_badge}\n"

        # Add clinical guidance based on tier
        response += "\n**Clinical Guidance:**\n"
        if tier == "High":
            response += (
                "- **Immediate Action:** Conduct comprehensive suicide risk assessment using VA/DoD CPG protocol\n"
                "- **Consider:** Warm handoff to Suicide Prevention Coordinator (SPC) or Mental Health\n"
                "- **Review:** Patient's current safety plan; update as needed\n"
                "- **Means Restriction:** Discuss lethal means safety (firearms, medications)\n"
                "- **Follow-up:** Schedule close follow-up within 24-72 hours\n"
                "- **Crisis Resources:** Ensure patient has Veterans Crisis Line number (988, Press 1)"
            )
        else:  # Moderate
            response += (
                "- **Recommended:** Conduct suicide risk screening at next clinical encounter\n"
                "- **Monitor:** Trends in risk factors (medication changes, missed appointments)\n"
                "- **Engage:** Discuss coping strategies and support systems\n"
                "- **Document:** Risk assessment and patient's current level of functioning\n"
                "- **Resources:** Provide Veterans Crisis Line information (988, Press 1)"
            )

        response += "\n\n---\n"
        response += (
            "*This assessment is based on predictive analytics and should supplement, not replace, clinical judgment. "
            "Always conduct a thorough clinical evaluation for patients with concerning presentations.*"
        )

        return response

    except Exception as e:
        return f"Error retrieving suicide risk assessment: {str(e)}"
    finally:
        cursor.close()
        conn.close()
```

### 7.2 System Prompt Updates

**Location:** `ai/prompts/system_prompts.py`

**Add suicide risk assessment guidelines to system prompt:**

```python
SUICIDE_RISK_ASSESSMENT_GUIDELINES = """
## Suicide Risk Assessment Guidelines

When discussing suicide risk or responding to queries about patient safety:

1. **Always Use the Tool:**
   - If a user asks about suicide risk, mental health safety, or REACH VET scores, ALWAYS invoke the `check_suicide_risk_factors` tool
   - Never speculate about suicide risk without consulting the risk assessment database

2. **Sensitive Language:**
   - Use probabilistic, non-stigmatizing language ("elevated risk factors present" vs. "suicidal patient")
   - Avoid deterministic predictions ("will attempt suicide") - use risk stratification language
   - Frame risk as dynamic and changeable, not fixed

3. **Clinical Guidance Priority:**
   - For High Risk patients: ALWAYS recommend immediate clinical assessment and SPC consultation
   - For Moderate Risk: Recommend screening and monitoring
   - For Standard Risk: Still encourage clinical judgment and screening if indicated

4. **Explainability Required:**
   - Always cite specific contributing factors (e.g., "Risk elevated due to prior attempt + 4 missed appointments")
   - Distinguish between structured data and clinical notes NLP sources
   - Provide actionable context (e.g., "Last missed appointment: 2025-12-10")

5. **Crisis Protocol Override:**
   - If user describes IMMINENT danger (e.g., "Patient has gun and is threatening self NOW"):
     - Bypass tool, immediately output emergency protocol
     - Recommend: Call 988 Veterans Crisis Line, Call VA Police/911, Do not leave patient alone
     - State: "This is a psychiatric emergency requiring immediate intervention"

6. **Never:**
   - Predict specific suicide attempts or provide timelines
   - Minimize or dismiss risk factors present in the data
   - Suggest suicide prevention is solely the patient's responsibility
   - Provide firearm access information or means of self-harm

7. **Always:**
   - Display clinical disclaimers about predictive models
   - Emphasize that clinical judgment supersedes algorithmic assessment
   - Provide Veterans Crisis Line information (988, Press 1)
   - Document that risk assessment was discussed (in AI response)
"""

# Add to main system prompt
MAIN_SYSTEM_PROMPT = f"""
... (existing prompt content) ...

{SUICIDE_RISK_ASSESSMENT_GUIDELINES}

... (existing prompt content) ...
"""
```

### 7.3 Tool Registration

**Location:** `ai/agent/tools_registry.py`

**Add new tool to LangGraph agent:**

```python
from ai.tools.ddi_tools import check_ddi_risks
from ai.tools.patient_summary_tools import get_patient_summary
from ai.tools.vitals_tools import analyze_vitals_trends
from ai.tools.notes_tools import get_clinical_notes_summary
from ai.tools.risk_tools import check_suicide_risk_factors  # NEW

# Tool registry for LangGraph agent
AVAILABLE_TOOLS = [
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
    get_clinical_notes_summary,
    check_suicide_risk_factors  # NEW
]
```

### 7.4 Integration with Existing AI Chatbot UI

**No UI changes required** - Suicide risk assessment is invoked via natural language queries:

**Example User Queries:**
- "Is this patient at risk for suicide?"
- "What does the REACH VET score say?"
- "Are there any suicide risk factors I should know about?"
- "Show me the suicide risk assessment"
- "Is there anything concerning about this patient's mental health?"

**Suggested Questions Integration:**

To help clinicians discover the suicide risk assessment capability, update `ai/prompts/suggested_questions.py` to include one or more suicide prevention questions in the AI Insights page modal popup.

**Recommended additions:**
```python
# In ai/prompts/suggested_questions.py
SUGGESTED_QUESTIONS = [
    # ... existing questions ...

    # Suicide Prevention (new)
    "Is this patient at risk for suicide?",
    "What does the REACH VET assessment show?",
    # ... or choose the phrasing that best fits your clinical workflow
]
```

This makes the suicide risk assessment feature discoverable without requiring clinicians to know the exact phrasing.

**AI Agent Workflow:**
1. User submits query mentioning suicide/risk/safety
2. LangGraph agent selects `check_suicide_risk_factors` tool based on query intent
3. Tool queries PostgreSQL for risk score and factors
4. Tool formats response with explainability and clinical guidance
5. Response displayed in existing AI chatbot UI (`app/templates/insight/chat.html`)

---

## 8. API Endpoints

**No dedicated API endpoints required for MVP** - All access via AI Chatbot tool.

**Deferred to Phase 2 (if needed):**
- `GET /api/patient/{icn}/suicide-risk` - JSON API for programmatic access
- `GET /admin/suicide-risk/dashboard` - Aggregate population-level risk analytics (for Suicide Prevention Coordinators)

**Rationale:**
- Restricting access to AI Chatbot only reduces risk of inappropriate use
- No dashboard widgets or direct UI access per ADR-SP-001
- Future API endpoints would require additional RBAC and audit logging

---

## 9. Clinical Notes NLP Processing

### 9.1 Overview

Clinical notes contain critical psychosocial risk factors not captured in structured data (ICD codes, medications, demographics). This section details the NLP pipeline to extract risk indicators from narrative text.

**Approach:** Rule-based NLP with keyword matching and sentiment analysis (tractable for 15-day timeline, avoids complexity of transformer models).

**Target Note Types:**
- Mental Health Consult Notes
- Psychiatry Progress Notes
- Psychology Notes
- Social Work Notes
- Primary Care Progress Notes (when discussing mental health)
- Discharge Summaries (psychiatric admissions)

### 9.2 Risk Keywords and Patterns

**Location:** `ai/nlp/suicide_risk_keywords.py`

```python
# Suicide Risk NLP Keyword Taxonomy
# Based on VA/DoD CPG Suicide Risk Assessment Guidelines

# Critical Risk Indicators (Force to High Risk if found in recent notes < 30 days)
CRITICAL_KEYWORDS = {
    'suicidal_ideation': [
        r'\bsuicidal ideation\b',
        r'\bSI\b',
        r'\bwants to die\b',
        r'\bwishes.*dead\b',
        r'\bthoughts of suicide\b',
        r'\bthinking about suicide\b',
        r'\bsuicidal thoughts\b'
    ],
    'suicide_plan': [
        r'\bsuicide plan\b',
        r'\bplan to.*suicide\b',
        r'\bmethod.*suicide\b',
        r'\bhas a plan\b'
    ],
    'suicide_intent': [
        r'\bintent to.*suicide\b',
        r'\bintends to.*harm self\b',
        r'\bgoing to kill.*self\b'
    ]
}

# High-Weight Risk Indicators
HIGH_RISK_KEYWORDS = {
    'hopelessness': [
        r'\bhopeless\b',
        r'\bno hope\b',
        r'\bfeel.*hopeless\b',
        r'\blife.*no meaning\b',
        r'\bno future\b',
        r'\bno point.*living\b',
        r'\bnot worth living\b'
    ],
    'firearm_access': [
        r'\bfirearms?\b',
        r'\bguns?\b',
        r'\baccess to.*gun\b',
        r'\bown.*gun\b',
        r'\bpistol\b',
        r'\brifle\b'
    ],
    'mst': [
        r'\bMST\b',
        r'\bmilitary sexual trauma\b',
        r'\bsexual assault.*military\b',
        r'\bsexual harassment.*military\b',
        r'\bsexual trauma.*deployment\b'
    ]
}

# Moderate-Weight Risk Indicators
MODERATE_RISK_KEYWORDS = {
    'social_isolation': [
        r'\bisolated\b',
        r'\balone\b',
        r'\blonely\b',
        r'\bno.*support\b',
        r'\bno.*friends\b',
        r'\bno.*family\b',
        r'\bestranged\b'
    ],
    'recent_loss': [
        r'\bloss of\b',
        r'\bdeath of\b',
        r'\bdied\b',
        r'\bdivorce\b',
        r'\bseparation\b',
        r'\bgrief\b',
        r'\bmourning\b'
    ],
    'unemployment': [
        r'\bunemployed\b',
        r'\bjob loss\b',
        r'\blost.*job\b',
        r'\bcannot work\b',
        r'\bfinancial.*stress\b'
    ],
    'homelessness': [
        r'\bhomeless\b',
        r'\bunhoused\b',
        r'\bno.*housing\b',
        r'\bliving.*car\b',
        r'\bliving.*street\b'
    ],
    'substance_use_notes': [
        r'\bdrinking.*daily\b',
        r'\balcohol.*problem\b',
        r'\busing.*drugs\b',
        r'\brelapsed\b',
        r'\bintoxicated\b'
    ]
}

# Protective Factors (NEGATIVE weight - reduces risk)
PROTECTIVE_KEYWORDS = {
    'safety_plan': [
        r'\bsafety plan\b',
        r'\bcoping.*strategies\b',
        r'\breason.*living\b'
    ],
    'social_support': [
        r'\bsupportive.*family\b',
        r'\bclose.*friends\b',
        r'\bstrong.*support\b'
    ],
    'engagement_treatment': [
        r'\bengaged.*treatment\b',
        r'\bimprovement\b',
        r'\bprogress.*therapy\b'
    ]
}
```

### 9.3 NLP Processing Pipeline

**Location:** `etl/nlp/process_clinical_notes_for_risk.py`

```python
import polars as pl
import re
from textblob import TextBlob
import nltk
from nltk.tokenize import sent_tokenize
from datetime import datetime, timedelta
from ai.nlp.suicide_risk_keywords import (
    CRITICAL_KEYWORDS,
    HIGH_RISK_KEYWORDS,
    MODERATE_RISK_KEYWORDS,
    PROTECTIVE_KEYWORDS
)

# Download NLTK data (run once)
nltk.download('punkt', quiet=True)

def process_clinical_notes_for_risk(notes_df: pl.DataFrame) -> pl.DataFrame:
    """
    Extract suicide risk indicators from clinical notes narrative text.

    Args:
        notes_df: Polars DataFrame with columns: patient_icn, note_date, note_type, note_text

    Returns:
        Polars DataFrame with NLP-derived risk features per patient
    """

    # Filter to relevant note types (mental health notes primarily)
    relevant_note_types = [
        'Mental Health Consult',
        'Psychiatry Note',
        'Psychology Note',
        'Social Work Note',
        'Progress Note',  # May contain mental health content
        'Discharge Summary'
    ]

    notes_df = notes_df.filter(
        pl.col('note_type').is_in(relevant_note_types)
    )

    # Process each note
    note_features = []

    for row in notes_df.iter_rows(named=True):
        icn = row['patient_icn']
        note_date = row['note_date']
        note_type = row['note_type']
        note_text = row['note_text']

        # Calculate note recency
        days_ago = (datetime.now().date() - note_date).days

        # Extract features from this note
        features = extract_risk_features_from_note(note_text, note_date, note_type)
        features['patient_icn'] = icn
        features['days_ago'] = days_ago

        note_features.append(features)

    # Convert to DataFrame
    features_df = pl.DataFrame(note_features)

    # Aggregate features by patient
    patient_nlp_features = aggregate_note_features_by_patient(features_df)

    return patient_nlp_features


def extract_risk_features_from_note(note_text: str, note_date, note_type: str) -> dict:
    """
    Extract risk indicators from a single clinical note.

    Returns dict with boolean flags for each risk category.
    """
    note_text_lower = note_text.lower()

    features = {
        'note_date': note_date,
        'note_type': note_type,
        'note_length': len(note_text)
    }

    # Check for critical keywords (suicidal ideation, plan, intent)
    for category, patterns in CRITICAL_KEYWORDS.items():
        features[f'has_{category}'] = any(
            re.search(pattern, note_text, re.IGNORECASE)
            for pattern in patterns
        )

    # Check for high-risk keywords
    for category, patterns in HIGH_RISK_KEYWORDS.items():
        features[f'has_{category}'] = any(
            re.search(pattern, note_text, re.IGNORECASE)
            for pattern in patterns
        )

    # Check for moderate-risk keywords
    for category, patterns in MODERATE_RISK_KEYWORDS.items():
        features[f'has_{category}'] = any(
            re.search(pattern, note_text, re.IGNORECASE)
            for pattern in patterns
        )

    # Check for protective factors
    for category, patterns in PROTECTIVE_KEYWORDS.items():
        features[f'has_{category}'] = any(
            re.search(pattern, note_text, re.IGNORECASE)
            for pattern in patterns
        )

    # Sentiment analysis (using TextBlob)
    # Lower polarity (more negative) = higher risk
    try:
        sentiment = TextBlob(note_text).sentiment
        features['note_sentiment_polarity'] = sentiment.polarity  # -1.0 to 1.0
        features['note_sentiment_subjectivity'] = sentiment.subjectivity  # 0.0 to 1.0
    except:
        features['note_sentiment_polarity'] = 0.0
        features['note_sentiment_subjectivity'] = 0.5

    return features


def aggregate_note_features_by_patient(features_df: pl.DataFrame) -> pl.DataFrame:
    """
    Aggregate note-level features to patient-level risk indicators.

    Logic:
    - ANY critical keyword in last 30 days → High Risk Override
    - COUNT of notes with hopelessness language
    - AVERAGE sentiment of mental health notes
    - MOST RECENT mention of firearm access, social isolation, etc.
    """

    # Define recency windows
    RECENT_CUTOFF_DAYS = 30  # For critical override
    LOOKBACK_DAYS = 365  # For other features

    # Filter to lookback window
    features_df = features_df.filter(pl.col('days_ago') <= LOOKBACK_DAYS)

    # Patient-level aggregations
    patient_features = features_df.group_by('patient_icn').agg([
        # Critical flags (any in last 30 days)
        pl.col('has_suicidal_ideation').filter(pl.col('days_ago') <= RECENT_CUTOFF_DAYS).any()
          .alias('has_current_si_notes'),
        pl.col('has_suicide_plan').filter(pl.col('days_ago') <= RECENT_CUTOFF_DAYS).any()
          .alias('has_current_plan_notes'),

        # High-risk indicators (any in last 365 days)
        pl.col('has_hopelessness').any().alias('has_hopelessness_notes'),
        pl.col('has_firearm_access').any().alias('has_firearm_access_notes'),
        pl.col('has_mst').any().alias('has_mst_notes'),

        # Moderate-risk indicators
        pl.col('has_social_isolation').any().alias('has_social_isolation_notes'),
        pl.col('has_recent_loss').any().alias('has_recent_loss_notes'),
        pl.col('has_unemployment').any().alias('has_unemployment_notes'),
        pl.col('has_homelessness').any().alias('has_homeless_notes'),
        pl.col('has_substance_use_notes').any().alias('has_substance_use_notes_nlp'),

        # Protective factors
        pl.col('has_safety_plan').any().alias('has_safety_plan_notes'),
        pl.col('has_social_support').any().alias('has_social_support_notes'),

        # Sentiment averages (for mental health notes)
        pl.col('note_sentiment_polarity').mean().alias('mental_health_note_sentiment_avg'),

        # Count of notes analyzed
        pl.col('note_date').count().alias('nlp_notes_analyzed')
    ])

    return patient_features
```

### 9.4 Integration with Silver ETL

The NLP processing pipeline is invoked during Silver ETL transformation:

```python
# In etl/silver/transform_suicide_risk_features.py

from etl.nlp.process_clinical_notes_for_risk import process_clinical_notes_for_risk

def silver_transformation():
    """Silver ETL with NLP integration"""

    # Load Bronze clinical notes
    notes_df = pl.read_parquet('lake/bronze/suicide_risk/clinical_notes.parquet')

    # Process notes with NLP
    nlp_features_df = process_clinical_notes_for_risk(notes_df)

    # Load other structured features (utilization, medications, diagnoses)
    utilization_df = calculate_utilization_features(...)
    medication_df = calculate_medication_features(...)
    diagnosis_df = calculate_diagnosis_features(...)

    # Merge all features by patient_icn
    combined_features = utilization_df.join(
        medication_df, on='PatientICN', how='outer'
    ).join(
        diagnosis_df, on='PatientICN', how='outer'
    ).join(
        nlp_features_df, left_on='PatientICN', right_on='patient_icn', how='outer'
    )

    # Save to Silver
    combined_features.write_parquet('lake/silver/suicide_risk/patient_risk_features.parquet')
```

### 9.5 NLP Performance Considerations

**Processing Time:**
- ~100-200ms per note (keyword matching + sentiment analysis)
- Batch processing: ~10-20 notes/second
- For 100 patients × 6 notes average = 600 notes ≈ 30-60 seconds total

**Accuracy:**
- Rule-based keyword matching: High precision (~85%), moderate recall (~60%)
- Sentiment analysis: Directional indicator, not diagnostic
- False positives: Negation handling ("denies suicidal ideation" may trigger incorrectly)

**Future Enhancements (Phase 2):**
- Negation detection (e.g., NegEx algorithm)
- Contextual embeddings (transformer models)
- Named entity recognition (NER) for medications, diagnoses in notes
- Vector search for semantic similarity ("feeling hopeless" ≈ "no reason to live")

---

## 10. Implementation Roadmap

**Total Duration:** 12-15 days (aggressive timeline)

**Team Size Assumption:** 1-2 developers with AI/ML and clinical informatics experience

---

### **Day 1-2: Mock Data Generation & Database Schema**

**Day 1: Synthetic Patient Profiles**
- [ ] Create `scripts/generate_suicide_risk_data.py`
- [ ] Generate 100+ patient profiles:
  - 15 High Risk (3+ risk factors including prior attempt)
  - 25 Moderate Risk (2-3 risk factors)
  - 60 Standard Risk (0-1 risk factors)
- [ ] Generate demographic data (age, gender, homeless status, zip code)
- [ ] Generate diagnosis data (ICD-10 codes for suicide attempt, PTSD, depression, substance use, TBI, chronic pain)
- [ ] Generate medication data (opioids, benzodiazepines, antidepressants)
- [ ] Generate utilization data (missed appointments, ED visits, psychiatric admissions)
- [ ] Insert data into Mock CDW tables

**Day 2: Clinical Notes Generation & PostgreSQL Schema**
- [ ] Create `scripts/generate_suicide_risk_notes.py`
- [ ] Generate 400-600 synthetic clinical notes with psychosocial risk language:
  - High-risk patients: 6-10 notes each with hopelessness, SI mentions, firearm access
  - Moderate-risk patients: 4-6 notes with social isolation, unemployment, loss
  - Standard-risk patients: 2-4 notes with neutral language
- [ ] Insert notes into `TIU.TIUDocumentText`
- [ ] Create PostgreSQL schema:
  - Run DDL: `db/ddl/create_clinical_risk_tables.sql`
  - Create `clinical.clinical_risk_scores` table
  - Create `clinical.clinical_risk_factors` table
  - Verify indexes and foreign keys

**Deliverables:**
- ✅ Mock CDW populated with 100+ patients exhibiting REACH VET risk patterns
- ✅ PostgreSQL schema ready for risk scores
- ✅ Synthetic clinical notes with psychosocial risk language

---

### **Day 3-5: ETL Pipeline (Bronze → Silver → Gold)**

**Day 3: Bronze Extraction**
- [ ] Create `etl/bronze/extract_suicide_risk_sources.py`
- [ ] Extract source tables to Parquet:
  - Demographics, Visits, Diagnoses, Medications, Inpatient, Clinical Notes
  - Dimension tables (NationalDrug, ICD10)
- [ ] Verify Bronze Parquet files contain expected data
- [ ] Test Bronze extraction on all 100 patients

**Day 4: Silver Transformation (Structured Features)**
- [ ] Create `etl/silver/transform_suicide_risk_features.py`
- [ ] Implement utilization feature calculation:
  - `no_show_count_12m`, `ed_visit_count_12m`, `no_show_rate`
- [ ] Implement medication feature calculation:
  - `has_opioid_rx`, `has_benzo_rx`, `has_concurrent_opioid_benzo`
- [ ] Implement diagnosis feature calculation:
  - `has_prior_attempt`, `has_ptsd`, `has_depression`, `has_tbi`, `has_chronic_pain`, etc.
- [ ] Test Silver transformation output

**Day 5: Silver Transformation (NLP Features) + Gold Scoring**
- [ ] Create `etl/nlp/process_clinical_notes_for_risk.py`
- [ ] Implement NLP keyword extraction (see Section 9.3)
- [ ] Implement sentiment analysis
- [ ] Integrate NLP features into Silver output
- [ ] Create `etl/gold/calculate_suicide_risk_scores.py`
- [ ] Implement REACH VET 2.0 logistic regression scoring
- [ ] Generate explainability factors (top contributing features)
- [ ] Test Gold transformation output

**Deliverables:**
- ✅ Bronze Parquet files with raw data
- ✅ Silver Parquet with 100+ patients × 25-30 calculated features
- ✅ Gold Parquet with risk scores, tiers, and explainability factors

---

### **Day 6-7: PostgreSQL Load & AI Tool Development**

**Day 6: PostgreSQL Load**
- [ ] Create `etl/load/load_suicide_risk_to_postgres.py`
- [ ] Load risk scores from Gold to `clinical.clinical_risk_scores`
- [ ] Load risk factors from Gold to `clinical.clinical_risk_factors`
- [ ] Verify data integrity:
  - All 100 patients have risk scores
  - High-risk patients have 3+ contributing factors
  - Supporting data JSONB populated correctly
- [ ] Test query performance (should be < 100ms for single patient lookup)

**Day 7: AI Tool Implementation**
- [ ] Create `ai/tools/risk_tools.py`
- [ ] Implement `check_suicide_risk_factors` tool (see Section 7.1)
- [ ] Add tool to LangGraph agent registry
- [ ] Update system prompts with suicide risk guidelines (see Section 7.2)
- [ ] Test tool invocation:
  - Query for High Risk patient → should return detailed factors + clinical guidance
  - Query for Standard Risk patient → should return reassurance
  - Query for non-existent patient → should return "no assessment available"

**Deliverables:**
- ✅ PostgreSQL loaded with 100+ risk assessments
- ✅ AI tool functional and integrated with LangGraph agent
- ✅ System prompts updated with safety guardrails

---

### **Day 8-10: Testing & Validation**

**Day 8: Model Validation**
- [ ] Create `scripts/validate_suicide_risk_model.py`
- [ ] Calculate model performance metrics:
  - Sensitivity at top 0.1% threshold (should be ≥40%)
  - False positive rate for High Risk tier (should be <5%)
  - Verify all High Risk synthetic patients correctly flagged
  - Verify Standard Risk patients not incorrectly flagged as High
- [ ] Generate ROC curve (optional, for documentation)
- [ ] Document model coefficients and performance in design spec

**Day 9: End-to-End AI Chatbot Testing**
- [ ] Test AI Chatbot queries for all 100 patients:
  - "Is this patient at risk for suicide?"
  - "What does the REACH VET assessment say?"
  - "Are there any mental health concerns?"
- [ ] Verify responses include:
  - Correct risk tier
  - Top contributing factors (sorted by weight)
  - Clinical guidance appropriate to tier
  - Data source attribution (structured vs. NLP)
  - Crisis resources (Veterans Crisis Line)
- [ ] Test edge cases:
  - Patient with no assessment
  - Patient with critical SI mention in recent notes (should force High Risk)
  - Patient with protective factors (should be mentioned)

**Day 10: Security & Ethical Review**
- [ ] Verify access control: Risk assessment only accessible via AI Chatbot
- [ ] Verify no dashboard widgets or dedicated pages created
- [ ] Review AI responses for stigmatizing language
- [ ] Verify crisis protocol override works (imminent danger scenarios)
- [ ] Document audit trail capabilities (who accessed which risk assessments)
- [ ] Review compliance with VA Mental Health Services guidance

**Deliverables:**
- ✅ Model validation report with sensitivity/specificity metrics
- ✅ End-to-end test suite passing for 100 patients
- ✅ Security review complete

---

### **Day 11-12: Documentation & Refinement**

**Day 11: Documentation**
- [ ] Complete this design specification (Section 13 - Reference Documents)
- [ ] Create user guide for clinicians:
  - How to query suicide risk via AI Chatbot
  - How to interpret risk tier and contributing factors
  - Clinical workflow for High/Moderate/Standard risk patients
- [ ] Update `ai/README.md` with suicide risk tool documentation
- [ ] Create data dictionary for risk variables and ICD-10 codes

**Day 12: Refinement & Code Review**
- [ ] Code review of all ETL, NLP, and AI tool code
- [ ] Refactor for consistency with existing med-z1 patterns
- [ ] Add comprehensive logging and error handling
- [ ] Optimize query performance (ensure < 200ms for risk lookups)
- [ ] Final integration testing

**Deliverables:**
- ✅ Complete design specification
- ✅ Clinician user guide
- ✅ Code reviewed and optimized

---

### **Day 13-15: Buffer & Deployment Prep (Optional)**

**Day 13-14: Buffer for Unexpected Issues**
- Reserved for addressing implementation challenges
- NLP accuracy tuning if needed
- Additional test patient scenarios

**Day 15: Deployment Prep**
- [ ] Create deployment checklist
- [ ] Verify all dependencies installed (`requirements.txt` updated)
- [ ] Test on clean environment (Docker container rebuild)
- [ ] Create rollback plan
- [ ] Schedule stakeholder demo

**Deliverables:**
- ✅ Implementation complete and ready for demo
- ✅ Deployment documentation

---

## 11. Testing Strategy

### 11.1 Unit Tests

**Location:** `scripts/test_suicide_risk_*.py`

**Coverage:**

1. **NLP Keyword Extraction:**
   - Test each keyword category against sample notes
   - Verify true positives (keywords present → feature = True)
   - Verify true negatives (keywords absent → feature = False)
   - Test edge cases (negation, misspellings)

2. **Feature Engineering:**
   - Test utilization feature calculation with known inputs
   - Test medication classification (opioid/benzo detection)
   - Test diagnosis categorization (ICD-10 pattern matching)

3. **Risk Scoring:**
   - Test logistic regression calculation with known feature vectors
   - Verify risk tier assignment (probability thresholds)
   - Test critical override (current SI → High Risk)

4. **AI Tool:**
   - Test tool with mock PostgreSQL data
   - Verify response formatting
   - Test error handling (patient not found)

### 11.2 Integration Tests

**Test Scenarios:**

1. **End-to-End ETL Pipeline:**
   - Input: Mock CDW with 10 test patients (3 High, 3 Moderate, 4 Standard)
   - Run: Bronze → Silver → Gold → PostgreSQL Load
   - Verify: All 10 patients have risk scores in PostgreSQL
   - Assert: High-risk patients correctly flagged

2. **AI Chatbot Workflow:**
   - Input: User query "Is ICN100001 at risk for suicide?"
   - Expected: AI agent invokes `check_suicide_risk_factors` tool
   - Expected: Response includes risk tier + contributing factors + clinical guidance
   - Assert: Response contains at least 3 contributing factors for High Risk patient

3. **NLP Accuracy:**
   - Input: 20 clinical notes with known risk language
   - Run: NLP processing pipeline
   - Expected: ≥80% precision for hopelessness keyword detection
   - Expected: ≥60% recall for suicidal ideation mentions

### 11.3 Model Validation Tests

**Performance Metrics (Against Synthetic Data):**

1. **Sensitivity (True Positive Rate):**
   - Definition: % of true High Risk patients correctly identified
   - Target: ≥40% at top 0.1% threshold (aligned with REACH VET 2.0 published performance)
   - Test: Of 15 synthetic High Risk patients, ≥6 should be flagged as High tier

2. **False Positive Rate:**
   - Definition: % of Standard Risk patients incorrectly flagged as High
   - Target: <5%
   - Test: Of 60 synthetic Standard Risk patients, ≤3 should be flagged as High tier

3. **Risk Tier Distribution:**
   - Expected: ~0.1% High, ~1% Moderate, ~99% Standard (in real population)
   - Test: In synthetic population of 100:
     - 10-20 High Risk patients (we over-sample for testing)
     - 20-30 Moderate Risk patients
     - 50-70 Standard Risk patients

4. **Explainability Validation:**
   - For each High Risk patient, verify ≥3 contributing factors stored
   - Verify factor weights sorted descending (highest risk factors listed first)
   - Verify JSONB supporting data populated with clinical evidence

### 11.4 Security & Ethical Tests

1. **Access Control:**
   - Verify risk assessment not accessible via direct API endpoint
   - Verify no dashboard widgets displaying risk scores
   - Verify AI Chatbot is only access path

2. **Language Audit:**
   - Review AI responses for stigmatizing language (e.g., "suicidal patient" vs. "patient with elevated risk factors")
   - Verify probabilistic language used (not deterministic predictions)
   - Verify crisis resources included in all High/Moderate risk responses

3. **Crisis Protocol Override:**
   - Test: User query describing imminent danger ("Patient has gun and is threatening self")
   - Expected: AI bypasses tool, immediately outputs emergency protocol (988, VA Police, do not leave patient alone)
   - Assert: Response includes "This is a psychiatric emergency requiring immediate intervention"

---

## 12. Security and Ethical Considerations

### 12.1 Access Control & Privacy

**Principle:** Suicide risk assessments are highly sensitive clinical information requiring strict access controls.

**Implementation:**

1. **No Direct UI Access:**
   - No dashboard widgets displaying risk scores
   - No dedicated risk assessment pages
   - Access ONLY via AI Chatbot (deliberate query required)

2. **Role-Based Access Control (RBAC):**
   - Phase 1: AI Chatbot accessible to all authenticated clinicians (no additional RBAC)
   - Phase 2: Restrict `check_suicide_risk_factors` tool to specific roles:
     - Mental Health Providers
     - Primary Care Providers
     - Suicide Prevention Coordinators
     - Social Workers
   - Future: Integrate with VA SSO and RBAC system

3. **Audit Logging:**
   - Log all invocations of `check_suicide_risk_factors` tool:
     - User ID (who accessed)
     - Patient ICN (which patient)
     - Timestamp
     - Risk tier returned
   - Store audit logs in separate table: `audit.suicide_risk_access`
   - Retention: 7 years (VA medical record retention policy)

4. **Data Protection:**
   - Clinical notes contain PHI → Bronze/Silver/Gold Parquet files must be encrypted at rest
   - PostgreSQL connection strings must use SSL/TLS in production
   - Risk scores stored in `clinical` schema with same protections as other clinical data

### 12.2 Algorithmic Transparency & Explainability

**Principle:** Clinicians must understand WHY a patient is flagged, not just THAT they are flagged.

**Implementation:**

1. **Explainability Factors:**
   - Every risk score has corresponding rows in `clinical_risk_factors` table
   - Factors sorted by contribution percentage (most important first)
   - Supporting data (JSONB) provides clinical evidence (e.g., "Last missed appointment: 2025-12-10")

2. **Data Source Attribution:**
   - Distinguish structured data (ICD codes, medications) from NLP data (clinical notes)
   - Display source in AI response: "📊 Structured" vs. "📝 NLP"
   - Acknowledge limitations of NLP (keyword-based, not semantic understanding)

3. **Model Version Tracking:**
   - All risk scores tagged with `model_version` ('REACH_VET_2.0')
   - If model coefficients updated, increment version (e.g., 'REACH_VET_2.1')
   - Allows comparison of risk scores over time with consistent methodology

4. **Clinical Disclaimers:**
   - All AI responses include: "This assessment is based on predictive analytics and should supplement, not replace, clinical judgment."
   - Emphasize dynamic nature of risk (not fixed, changes with new data)

### 12.3 Ethical Safeguards

**Principle:** Predictive suicide risk models must not stigmatize patients or create self-fulfilling prophecies.

**Implementation:**

1. **Non-Stigmatizing Language:**
   - Avoid labels like "suicidal patient" → use "patient with elevated risk factors"
   - Use probabilistic language: "increased risk" vs. "will attempt suicide"
   - Frame risk as changeable: "current risk factors include..." (implies modifiable)

2. **Actionable Guidance:**
   - Every High/Moderate risk response includes specific clinical actions:
     - High Risk: Immediate assessment, SPC consult, safety planning, means restriction
     - Moderate Risk: Screening at next visit, monitor trends, engage coping strategies
   - Avoid "FYI only" alerts that create anxiety without actionable steps

3. **Patient-Facing Communication:**
   - **NEVER display risk scores or tiers to patients** (clinician-only tool)
   - Risk assessment is for care planning, not patient notification
   - Clinicians use assessment to guide conversations, not to inform patients "you are high risk"

4. **False Positive Acknowledgment:**
   - System prompts instruct AI to acknowledge: "While risk factors are present, this does not mean suicide is imminent or inevitable."
   - Emphasize individual variability: "Clinical judgment is essential for individualized assessment."

5. **Crisis Resources:**
   - All responses (High, Moderate, Standard) include Veterans Crisis Line: 988, Press 1
   - Emphasize help is available 24/7
   - Reduce perception that "high risk = hopeless"

### 12.4 Bias Mitigation

**Principle:** Algorithmic bias can perpetuate health disparities; mitigation is essential.

**Implementation:**

1. **No Race/Ethnicity Variables:**
   - REACH VET 2.0 explicitly excludes race/ethnicity from model
   - Aligns with modern equity standards
   - Prevents discriminatory profiling

2. **Balanced Synthetic Data:**
   - Generate test patients with diverse demographics (gender, age, geography)
   - Ensure algorithm performs equitably across subgroups
   - Test for differential false positive rates by gender/age

3. **NLP Bias Awareness:**
   - Keyword-based NLP may have cultural bias (e.g., "hopelessness" vs. other expressions of distress)
   - Clinical notes themselves may reflect provider bias (differential documentation by patient demographics)
   - Acknowledge limitations in documentation

4. **Continuous Monitoring (Phase 2):**
   - If deployed with real data, monitor model performance by demographic subgroups
   - Audit for disparate impact (e.g., higher false positive rate for specific populations)
   - Retrain/recalibrate if bias detected

### 12.5 Ethical Review Checklist

Before deployment, confirm:

- [ ] Risk assessment accessible only via AI Chatbot (no passive surveillance)
- [ ] AI responses use non-stigmatizing, probabilistic language
- [ ] Explainability factors provided for all risk scores
- [ ] Clinical disclaimers present in all responses
- [ ] Crisis protocol override functional (imminent danger scenarios)
- [ ] Audit logging enabled for all risk assessment queries
- [ ] No race/ethnicity variables included in model
- [ ] Synthetic test data balanced across demographics
- [ ] Documentation acknowledges model limitations (false positives, NLP bias)
- [ ] Clinician user guide includes ethical use guidelines

---

## 13. Reference Documents

### 13.1 VA/DoD Clinical Practice Guidelines

**VA/DoD Clinical Practice Guideline for Assessment and Management of Patients at Risk for Suicide (2024)**
- **Availability:** Publicly available from VA.gov and healthquality.va.gov
- **Relevance:** Authoritative clinical protocols for suicide risk assessment, safety planning, and crisis intervention. Defines standard of care for VA providers.
- **Key Sections:**
  - Section 3: Risk Assessment Strategies (Validated screening tools, clinical interview techniques)
  - Section 4: Safety Planning Intervention (Collaborative safety plan development)
  - Section 5: Lethal Means Counseling (Firearm access, medication disposal)
  - Appendix C: Veterans Crisis Line resources

**VA/DoD Clinical Practice Guideline for Management of Major Depressive Disorder (2022)**
- **Availability:** Publicly available from VA.gov and healthquality.va.gov
- **Relevance:** Depression is a major risk factor for suicide; provides context for diagnosis codes and treatment patterns.

**VA/DoD Clinical Practice Guideline for Management of PTSD (2023)**
- **Availability:** Publicly available from VA.gov and healthquality.va.gov
- **Relevance:** PTSD is a significant risk factor; discusses comorbidity with substance use and depression.

### 13.2 REACH VET Scientific Literature

**McCarthy, J. F., Bossarte, R. M., Katz, I. R., et al. (2015). Predictive Modeling and Concentration of the Risk of Suicide: Implications for Preventive Interventions in the US Department of Veterans Affairs. American Journal of Public Health, 105(9), 1935–1942.**
- **DOI:** 10.2105/AJPH.2015.302737
- **Availability:** Available via PubMed, AJPH journal website, or academic databases
- **Relevance:** Primary source for REACH VET 2.0 model design, variables, and performance metrics (sensitivity, specificity, PPV).
- **Key Findings:**
  - 61-variable logistic regression model
  - Sensitivity ~50% at top 0.1% threshold
  - Emphasis on administrative and clinical data integration

**Kessler, R. C., Warner, C. H., Ivany, C., et al. (2015). Predicting Suicides After Psychiatric Hospitalization in US Army Soldiers: The Army Study to Assess Risk and Resilience in Servicemembers (Army STARRS). JAMA Psychiatry, 72(1), 49–57.**
- **DOI:** 10.1001/jamapsychiatry.2014.1754
- **Availability:** Available via PubMed or JAMA Psychiatry journal website
- **Relevance:** Risk factor weights and statistical methodology applicable to veteran populations.

**Ribeiro, J. D., Franklin, J. C., Fox, K. R., et al. (2016). Self-injurious thoughts and behaviors as risk factors for future suicide ideation, attempts, and death: a meta-analysis of longitudinal studies. Psychological Medicine, 46(2), 225–236.**
- **DOI:** 10.1017/S0033291715001804
- **Availability:** Available via PubMed or Cambridge Core (Psychological Medicine journal)
- **Relevance:** Meta-analysis supporting prior suicide attempt as strongest predictor (2.5x coefficient).

### 13.3 VA Mental Health Services Guidelines

**VA Office of Mental Health and Suicide Prevention: REACH VET Program Overview**
- **Availability:** Internal VA documentation (not publicly available; accessible to VA staff via VA intranet)
- **Summary:** Operational guidelines for Suicide Prevention Coordinators (SPCs) on how to respond to REACH VET alerts, conduct follow-up assessments, and document interventions.

**VA National Strategy for Preventing Veteran Suicide (2024-2028)**
- **URL:** https://www.mentalhealth.va.gov/suicide_prevention/
- **Relevance:** Policy context for suicide prevention initiatives, including REACH VET 2.0 deployment.

### 13.4 Clinical Informatics & NLP References

**Natural Language Processing for Suicide Risk Identification (Literature Review)**
- **Relevance:** Techniques for extracting psychosocial risk factors from clinical notes (keyword extraction, sentiment analysis, negation detection).
- **Key Papers (available via PubMed/academic databases):**
  - McCoy, T. H., et al. (2016). Sentiment Measured in Hospital Discharge Notes Is Associated with Readmission and Mortality Risk. PLOS ONE.
  - Pestian, J. P., et al. (2017). A Machine Learning Approach to Identifying the Thought Markers of Suicidal Subjects: A Prospective Multicenter Trial. Suicide and Life-Threatening Behavior.

### 13.5 Technical References

**LangChain/LangGraph Documentation**
- **URL:** https://python.langchain.com/docs/langgraph
- **Relevance:** Agentic RAG architecture, tool design patterns, state management.

**scikit-learn Logistic Regression**
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
- **Relevance:** Statistical model implementation for risk scoring.

**NLTK (Natural Language Toolkit)**
- **URL:** https://www.nltk.org/
- **Relevance:** Tokenization, stopwords, sentiment analysis (TextBlob).

**VA CDW Data Model Documentation**
- **Location:** Internal VA documentation
- **Relevance:** Schema definitions for `Outpat.Visit`, `RxOut.RxOutpat`, `SPatient.SPatient`, `TIU.TIUDocumentText`.

**med-z1 VistA RPC Broker Design Specification**
- **Location:** `docs/spec/vista-rpc-broker-design.md` (v2.0, 2026-01-13)
- **Relevance:** Real-time VistA data integration architecture for T-0 clinical notes access (Section 3.4). Documents TIU namespace RPCs (`TIU GET DOCUMENT TEXT`, `TIU DOCUMENTS BY CONTEXT`), session caching pattern (30-minute TTL), site selection policy (3-5 sites for safety-critical domains), and merge/deduplication strategy.
- **Key Sections:**
  - Section 2.2: RPC Protocol and JSON Response Format
  - Section 4: Session-Based Caching (TTL, user-scoped isolation)
  - Section 5: Site Selection Policy (domain-specific limits)
  - Section 6.4: TIU Namespace RPCs (clinical notes retrieval)

**med-z1 VistA RPC Broker Implementation Guide**
- **Location:** `vista/README.md`
- **Relevance:** Practical guidance for integrating VistA real-time data into med-z1 services. Documents `vista/app/main.py` FastAPI service (port 8003), RPC handler registration patterns, and testing procedures with mock VistA sites (Alexandria 200, Anchorage 500, Palo Alto 630).
- **Key Endpoints:**
  - `POST /rpc/execute?site={sta3n}&icn={icn}` - Execute RPC with ICN-to-DFN resolution
  - `GET /sites` - Available VistA sites
  - `GET /health` - Service health check

**med-z1 Vista Client Service**
- **Location:** `app/services/vista_client.py`
- **Relevance:** HTTP client wrapper for VistA RPC Broker with intelligent site selection, timeout handling (25 seconds), and error recovery patterns. Used by suicide risk ETL pipeline for T-0 clinical notes retrieval.

**med-z1 Session Cache Service**
- **Location:** `app/services/vista_cache.py`
- **Relevance:** Server-side caching layer for VistA RPC responses (30-minute TTL, user-scoped via session ID). Reduces latency for repeated queries and protects VistA systems from excessive load during suicide risk assessment workflows.

### 13.6 Regulatory & Compliance

**21st Century Cures Act - Interoperability & Information Blocking**
- **Relevance:** Algorithmic transparency requirements for clinical decision support.

**VA Directive 6502: Privacy and Data Protection**
- **Relevance:** PHI handling, audit logging, access controls for sensitive clinical data.

**VA Handbook 5005: Staffing - Suicide Prevention Coordinator Role**
- **Relevance:** Workflow integration with SPC when High Risk patients identified.

---

## Appendices

### Appendix A: REACH VET 2.0 Variable Definitions (Detailed)

*This appendix would contain a comprehensive table of all 61 REACH VET 2.0 variables with ICD-10 code mappings, CPT codes, medication classes, and data sources. Deferred to separate reference document for brevity.*

### Appendix B: NLP Keyword Taxonomy (Full List)

*Complete list of all keyword patterns for critical, high-risk, moderate-risk, and protective factors. See `ai/nlp/suicide_risk_keywords.py` for implementation.*

### Appendix C: Glossary

**Agentic RAG:** Retrieval-Augmented Generation with autonomous agents that select tools to query data sources.

**CCOW:** Clinical Context Object Workgroup - Standard for patient context synchronization across applications.

**CPG:** Clinical Practice Guideline - Evidence-based recommendations for clinical care.

**ICD-10:** International Classification of Diseases, 10th Revision - Diagnosis coding system.

**MST:** Military Sexual Trauma - Sexual assault or harassment occurring during military service.

**NLP:** Natural Language Processing - Computational analysis of human language.

**REACH VET:** Recovery Engagement and Coordination for Health - Veterans Enhanced Treatment - VA's predictive suicide risk model.

**ROC Curve:** Receiver Operating Characteristic - Graph showing model performance across thresholds.

**SPC:** Suicide Prevention Coordinator - VA staff role responsible for high-risk patient outreach.

**XAI:** Explainable AI - Techniques to make AI decision-making transparent and interpretable.

### Appendix D: Sample AI Chatbot Conversation

**User:** Is this patient at risk for suicide?

**AI Agent:** [Invokes `check_suicide_risk_factors` tool for ICN100001]

**AI Response:**
```
🔴 **Risk Assessment: High Risk** (REACH_VET_2.0)

**Risk Probability:** 0.0025 (99.75th percentile)
**Assessment Date:** 2026-01-17
**Clinical Notes Analyzed:** 8 notes

**Key Contributing Factors:**
35.0% - **Prior Suicide Attempt** 📊 Structured
25.0% - **Military Sexual Trauma (MST)** 📝 NLP
15.0% - **Missed 3+ Appointments (12mo)** 📊 Structured
12.0% - **Hopelessness Language in Clinical Notes** 📝 NLP
11.0% - **Concurrent Opioid + Benzodiazepine** 📊 Structured

**Clinical Guidance:**
- **Immediate Action:** Conduct comprehensive suicide risk assessment using VA/DoD CPG protocol
- **Consider:** Warm handoff to Suicide Prevention Coordinator (SPC) or Mental Health
- **Review:** Patient's current safety plan; update as needed
- **Means Restriction:** Discuss lethal means safety (firearms, medications)
- **Follow-up:** Schedule close follow-up within 24-72 hours
- **Crisis Resources:** Ensure patient has Veterans Crisis Line number (988, Press 1)

---
*This assessment is based on predictive analytics and should supplement, not replace, clinical judgment. Always conduct a thorough clinical evaluation for patients with concerning presentations.*
```

---

**End of Design Specification**

**Document Status:** ✅ Complete
**Next Steps:** Review with stakeholders → Begin Day 1 implementation (Mock Data Generation)
**Questions/Feedback:** Contact development team or file issue in med-z1 repository

