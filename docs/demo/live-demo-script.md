# med-z1 Live Demo Script (90 Minutes)

**Audience:** Clinical + technical stakeholder (PharmD/PhD level)  
**Format:** Screen-share live demo (terminal + browser + selected code files)  
**Presenter Goal:** Balanced technical implementation and functional user value

---

## 1. Demo Outcomes

By the end of this session, the audience should understand:

1. How mock source data is prepared in `CDWWork` and `CDWWork2`.
2. How the medallion ETL pipeline moves data from SQL Server to MinIO to PostgreSQL.
3. Why PostgreSQL is the runtime serving foundation after ETL completion.
4. How the CCOW Vault service provides cross-application patient-context synchronization.
5. How the web UI modernizes JLV patterns with improved performance and modular domain views.
6. How AI Insights currently works (LangGraph + tools + DDI reference) and where clinical feedback is needed next.

---

## 2. 90-Minute Agenda

1. **0-5 min**: Context and architecture framing  
2. **5-30 min**: Part 1 Data prep + ETL + PostgreSQL serving model  
3. **30-55 min**: Part 2 Web UI walkthrough (dashboard + detail pages)  
4. **55-70 min**: CCOW Vault context synchronization (functional + technical)  
5. **70-90 min**: Part 3 AI Insights preview + collaborative workshop discussion

---

## 3. Pre-Demo Checklist (Run 10-15 min before meeting)

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate

# Start core data services
docker start sqlserver2019 postgres16 med-insight-minio

# Optional quick status checks
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

If needed, verify PostgreSQL access:

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT current_database();"
```

If needed, verify key tables:

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt clinical.*"
docker exec -it postgres16 psql -U postgres -d medz1 -c "\dt reference.*"
```

---

## 4. Opening Talk Track (0-5 min)

Use this framing statement:

> med-z1 modernizes JLV with a clean separation of concerns: historical serving data is loaded into PostgreSQL for fast access, optional real-time overlays come from VistA simulation, and AI tools run on top of prepared clinical datasets.

Show these files:

- `/Users/chuck/swdev/med/med-z1/README.md`
- `/Users/chuck/swdev/med/med-z1/docs/spec/med-z1-architecture.md`
- `/Users/chuck/swdev/med/med-z1/docs/spec/ai-insight-design.md`

Use this architecture sketch in your narration:

```text
Mock SQL Server (CDWWork + CDWWork2)
  -> ETL Bronze/Silver/Gold in MinIO (Parquet)
  -> Load to PostgreSQL serving DB
  <-> CCOW Vault (active patient context service)
  -> FastAPI UI (Dashboard + domain pages)
  -> AI Insights (LangGraph + tools + DDI reference)
```

---

## 5. Part 1: Data Prep + ETL + PostgreSQL (5-30 min)

### 5.1 Source Data Preparation Story

Narrative:

1. `CDWWork` simulates VistA-oriented source domains.
2. `CDWWork2` simulates Oracle Health/Cerner-oriented source structure.
3. Shared patient identity via ICN enables harmonization downstream.

Show source setup/readme files:

- `/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/README.md`
- `/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork2/README.md`
- `/Users/chuck/swdev/med/med-z1/docs/guide/med-z1-sqlserver-guide.md`

Optional source rebuild commands (only if you want to show creation flow):

```bash
cd /Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/create
./_master.sh
cd ../insert
./_master.sh

cd /Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork2/create
./_master.sh
cd ../insert
./_master.sh
```

### 5.2 ETL Medallion Pipeline Story

Show orchestrator:

- `/Users/chuck/swdev/med/med-z1/scripts/run_all_etl.sh`
- `/Users/chuck/swdev/med/med-z1/etl/README.md`

Explain layers:

1. Bronze: source extraction
2. Silver: cleanup/harmonization
3. Gold: curated query-ready structures
4. Load: PostgreSQL serving tables

Run full ETL (if time allows):

```bash
cd /Users/chuck/swdev/med/med-z1
./scripts/run_all_etl.sh
```

If time-limited, run one domain end-to-end (vitals example):

```bash
python -m etl.bronze_vitals
python -m etl.silver_vitals
python -m etl.gold_vitals
python -m etl.load_vitals
```

### 5.3 Verify Serving Data in PostgreSQL

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_demographics;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_vitals;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_medications_outpatient;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_problems;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM reference.ddi;"
```

Reference files to show while explaining schemas/domains:

- `/Users/chuck/swdev/med/med-z1/docs/guide/med-z1-postgres-guide.md`
- `/Users/chuck/swdev/med/med-z1/db/ddl/create_reference_ddi_table.sql`

### 5.4 Key Message to Emphasize

Use this exact statement:

> Once data preparation and ETL loading are complete, med-z1 runtime serves historical domain data from PostgreSQL. SQL Server and MinIO are pipeline dependencies, not required for day-to-day historical query serving in the UI.

Code evidence (show quickly):

- `/Users/chuck/swdev/med/med-z1/app/db/patient.py`
- `/Users/chuck/swdev/med/med-z1/app/db/medications.py`

---

## 6. Part 2: Web UI Walkthrough (30-55 min)

### 6.1 Start Application Services

Open 3 terminals:

```bash
# Terminal 1
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn vista.app.main:app --reload --port 8003
```

```bash
# Terminal 2
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --reload --port 8001
```

```bash
# Terminal 3
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Open browser: `http://127.0.0.1:8000`

### 6.2 Suggested Live Click Path

1. Login (`clinician.alpha@va.gov` / `VaDemo2025!`)
2. Select a patient
3. Show dashboard composition and widget loading
4. Open detail pages:
   - Vitals
   - Medications
   - Problems (or Labs/Notes)
5. Return to dashboard and show persistent patient context

### 6.3 UI Architecture Talking Points

Show these files:

- `/Users/chuck/swdev/med/med-z1/app/templates/base.html`
- `/Users/chuck/swdev/med/med-z1/app/templates/dashboard.html`
- `/Users/chuck/swdev/med/med-z1/app/routes/dashboard.py`
- `/Users/chuck/swdev/med/med-z1/app/main.py`

Narration bullets:

1. Left navigation provides domain-level access and status (implemented vs coming soon).
2. Sticky top header provides patient context actions (select, refresh, flags).
3. Dashboard is widget-driven and HTMX-loaded for responsive interaction.
4. Domain pages provide deeper, focused data exploration while preserving shared context.
5. This pattern intentionally mirrors JLV usability goals but with modern performance/maintainability.

Optional visual references:

- `/Users/chuck/swdev/med/med-z1/docs/screenshot/02-dashboard.png`
- `/Users/chuck/swdev/med/med-z1/docs/screenshot/05-vitals.png`
- `/Users/chuck/swdev/med/med-z1/docs/screenshot/09-medications_new.png`
- `/Users/chuck/swdev/med/med-z1/docs/screenshot/14-insights.png`

---

## 7. CCOW Vault: Context Synchronization (55-70 min)

### 7.1 Why CCOW Matters

Use this line:

> CCOW Vault makes active-patient context explicit and shareable, so med-z1 and companion apps can stay synchronized on the same patient workflow.

Functional value to emphasize:

1. Reduces context switching risk.
2. Improves cross-app workflow continuity.
3. Provides a clear patient-context source of truth for the current session.

Technical value to emphasize:

1. Separate FastAPI service (`ccow`) on port `8001`.
2. App integration via CCOW client calls in UI routes.
3. Lightweight REST pattern that is easy to test and extend.

### 7.2 Show CCOW Files

- `/Users/chuck/swdev/med/med-z1/ccow/README.md`
- `/Users/chuck/swdev/med/med-z1/ccow/main.py`
- `/Users/chuck/swdev/med/med-z1/app/utils/ccow_client.py`
- `/Users/chuck/swdev/med/med-z1/app/routes/dashboard.py`

### 7.3 Live CCOW API Demo Commands

Keep `uvicorn ccow.main:app --reload --port 8001` running, then in another terminal:

```bash
# Health check
curl http://localhost:8001/ccow/health

# Read active patient (may be empty initially)
curl -i http://localhost:8001/ccow/active-patient

# Set active patient
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"ICN100001","set_by":"med-z1-demo"}'

# Confirm active patient and history
curl http://localhost:8001/ccow/active-patient
curl http://localhost:8001/ccow/history
```

Then in browser, click **Refresh Patient** in the top bar to show context pull from CCOW.

---

## 8. Part 3: AI Insights + Collaborative Workshop (70-90 min)

### 8.1 Position Current AI State Clearly

Use this statement:

> The current AI stack is productionized tool orchestration and clinical synthesis using LangGraph over prepared data. It is predictive/supportive in behavior, but not yet deployed as supervised ML scoring with scikit-learn models in runtime.

### 8.2 Show AI Implementation Footprint

- `/Users/chuck/swdev/med/med-z1/ai/agents/insight_agent.py`
- `/Users/chuck/swdev/med/med-z1/ai/tools/__init__.py`
- `/Users/chuck/swdev/med/med-z1/ai/services/ddi_analyzer.py`
- `/Users/chuck/swdev/med/med-z1/app/routes/insight.py`
- `/Users/chuck/swdev/med/med-z1/etl/load_ddi.py`

### 8.3 AI Architecture Sketch for Discussion

```text
User Question (/insight)
  -> LangGraph Agent (tool selection + response synthesis)
  -> Tools:
       - check_ddi_risks
       - get_patient_summary
       - get_family_history
       - analyze_vitals_trends
       - get_clinical_notes_summary
  -> Services/DB access
  -> Response with clinical context
```

### 8.4 Workshop Questions for Your Colleague

Use these to drive active discussion:

1. How should DDI severity be stratified clinically (major/moderate/minor + evidence grade)?
2. Should medication normalization be upgraded to RxNorm/ATC mapping before pair checks?
3. Which patient factors should modify interaction risk scoring first (age, renal function, hepatic function, dose, route)?
4. What reference data source should replace/augment current Kaggle/DrugBank-derived DDI coverage?
5. What alert-thresholding strategy would reduce alert fatigue while keeping safety high?

### 8.5 Suggested Follow-Up Scope (for dedicated Part 3 session)

1. DDI data quality and ontology gap assessment
2. Clinical validation rubric for high-risk interaction output
3. Prioritized roadmap for richer CDS logic and explainability

---

## 9. Demo Safety Net (If Something Breaks Live)

If ETL is too slow for live run:

1. Show `run_all_etl.sh` and explain domain sequence.
2. Show Postgres verification queries with current row counts.
3. Move to UI demo and mention ETL was completed pre-session.

If a service fails to start:

```bash
docker logs sqlserver2019 | tail -50
docker logs postgres16 | tail -50
docker logs med-insight-minio | tail -50
```

If app auth/session issues appear:

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT email, is_active FROM auth.users ORDER BY email;"
```

---

## 10. Overrun Strategy (If Meeting Runs Long)

If you are near time at minute ~75:

1. Complete CCOW segment and summarize AI architecture in 3-5 minutes.
2. Capture AI questions and schedule dedicated Part 3 follow-up.
3. Share this runbook and cheat sheet as pre-read for follow-up.

Use this line:

> We completed full data and workflow architecture today, including context synchronization; next session will focus deeply on AI safety, DDI reference expansion, and clinical validation.

---

## 11. Quick Command Sheet (Copy/Paste)

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
docker start sqlserver2019 postgres16 med-insight-minio
```

```bash
cd /Users/chuck/swdev/med/med-z1
./scripts/run_all_etl.sh
```

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_demographics;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_vitals;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM reference.ddi;"
```

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn vista.app.main:app --reload --port 8003
```

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --reload --port 8001
```

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

## 12. Optional Closing Statement

> med-z1 demonstrates a pragmatic modernization path: robust data engineering foundation, clinician-friendly UI, and extensible AI tooling. The next major value gain comes from clinically guided improvement of the DDI and AI decision-support layer.
