# med-z1 Live Demo Cheat Sheet (1 Page)

**Use case:** Second-screen quick reference during 90-minute demo

## 1. Time Plan

1. **0-5 min**: Architecture framing
2. **5-30 min**: Part 1 Data prep + ETL + PostgreSQL
3. **30-55 min**: Part 2 UI walkthrough
4. **55-70 min**: CCOW Vault context sync
5. **70-90 min**: Part 3 AI Insights + workshop questions

## 2. Core Message

`med-z1 modernizes JLV with PostgreSQL serving for historical data, CCOW context synchronization, optional real-time VistA overlays, and LangGraph-based AI tools.`

## 3. Start Commands

```bash
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
docker start sqlserver2019 postgres16 med-insight-minio
```

## 4. Part 1 (Data/ETL) Commands

Full ETL:

```bash
./scripts/run_all_etl.sh
```

Fast fallback (single domain):

```bash
python -m etl.bronze_vitals
python -m etl.silver_vitals
python -m etl.gold_vitals
python -m etl.load_vitals
```

Verify serving DB:

```bash
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_demographics;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM clinical.patient_vitals;"
docker exec -it postgres16 psql -U postgres -d medz1 -c "SELECT COUNT(*) FROM reference.ddi;"
```

Key line to say:

`After ETL load, historical runtime reads are from PostgreSQL; SQL Server + MinIO are ETL-time dependencies.`

## 5. Part 2 (UI) Commands

Terminal 1:

```bash
uvicorn vista.app.main:app --reload --port 8003
```

Terminal 2:

```bash
uvicorn ccow.main:app --reload --port 8001
```

Terminal 3:

```bash
uvicorn app.main:app --reload --port 8000
```

Open:

`http://127.0.0.1:8000`

Demo click flow:

1. Login
2. Select patient
3. Dashboard scan
4. Vitals detail page
5. Medications detail page
6. Problems (or Labs/Notes)
7. Back to dashboard

## 6. Part 3 (AI) Positioning

Say this clearly:

`Current AI is tool-orchestrated predictive support (LangGraph + tools), not production supervised ML scoring with scikit-learn in runtime.`

## 7. CCOW Vault Quick Demo

Say this:

`CCOW Vault keeps active patient context synchronized across apps and reduces patient-context switching risk.`

CCOW API checks:

```bash
curl http://localhost:8001/ccow/health
curl -i http://localhost:8001/ccow/active-patient
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "Content-Type: application/json" \
  -d '{"patient_id":"ICN100001","set_by":"med-z1-demo"}'
curl http://localhost:8001/ccow/history
```

Then in browser: click `Refresh Patient`.

## 8. Workshop Questions (Pharmacist Colleague)

1. How should DDI severity be stratified clinically?
2. Should we normalize meds using RxNorm/ATC?
3. Which factors should modify risk first (dose, age, renal/hepatic, route)?
4. Which data source should replace/augment current DDI dataset?
5. How should alerts be prioritized to reduce fatigue?

## 9. Architecture Sketch (Read Aloud)

```text
CDWWork + CDWWork2 (SQL Server mock)
  -> Bronze/Silver/Gold ETL in MinIO
  -> PostgreSQL serving DB
  <-> CCOW Vault context service
  -> FastAPI UI + domain pages
  -> LangGraph AI Insights tools
```

## 10. Overrun Fallback

If time runs long:

`Complete Part 1 + Part 2 + CCOW today, then schedule Part 3 AI deep-dive as follow-up.`

## 11. File Pointers to Show Quickly

- `/Users/chuck/swdev/med/med-z1/docs/guide/med-z1-live-demo-script.md`
- `/Users/chuck/swdev/med/med-z1/scripts/run_all_etl.sh`
- `/Users/chuck/swdev/med/med-z1/app/templates/base.html`
- `/Users/chuck/swdev/med/med-z1/app/templates/dashboard.html`
- `/Users/chuck/swdev/med/med-z1/ccow/README.md`
- `/Users/chuck/swdev/med/med-z1/ai/agents/insight_agent.py`
