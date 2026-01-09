# CDWWork2 - Oracle Health (Cerner Millennium) Mock Database

**Purpose:** Simulate Oracle Health (Cerner) data structure to demonstrate med-z1's dual-source data integration capability (VistA + Cerner).

**Status:** ✅ Phase 1 (Foundation) Complete - 2025-12-30

---

## Overview

CDWWork2 is the second mock Corporate Data Warehouse database for the med-z1 project. It simulates data from VA medical centers that have transitioned to Oracle Health (formerly Cerner Millennium) EHR system.

**Key Differences from CDWWork (VistA):**
- **Encounter-centric** vs patient-centric data model
- **Consolidated code sets** (NDimMill.CodeValue) vs many dimension tables
- **Person** terminology vs Patient
- **Different internal IDs** (PersonSID vs PatientSID), but shared **PatientICN** for identity resolution

---

## Database Schema

### Schemas Created

| Schema | Purpose | Tables Created (Phase 1) |
|--------|---------|---------------------------|
| **NDimMill** | Normalized dimensions (consolidated code values) | CodeValue |
| **VeteranMill** | Patient demographics | SPerson |
| **EncMill** | Encounters (core of Cerner's data model) | Encounter |
| **VitalMill** | Vital signs results | VitalResult |
| **AllergyMill** | Allergy and reaction data | PersonAllergy, AdverseReaction |

### Key Tables

**NDimMill.CodeValue** (Consolidated Code Sets)
- Replaces VistA's many dimension tables (Dim.VitalType, Dim.Allergen, etc.)
- All code sets stored in single table with `CodeSet` field
- Phase 1 code sets: VITAL_TYPE, UNIT, ALLERGEN, REACTION, SEVERITY
- **48 total codes** populated

**VeteranMill.SPerson** (Patient Demographics)
- Cerner's patient master table (corresponds to CDWWork SPatient.SPatient)
- Key fields: PersonSID (Cerner-specific), PatientICN (shared identity key)
- **2 demo patients** populated

**EncMill.Encounter** (Encounters)
- Core table for Cerner's encounter-centric model
- All clinical data (vitals, allergies, labs, etc.) linked to encounters
- **16 encounters** populated (8 per patient)

---

## Demo Patients

| PatientICN | Name | CDWWork (VistA) | CDWWork2 (Cerner) |
|-----------|------|-----------------|-------------------|
| ICN100001 | Adam Dooree | PatientSID 1001<br>Atlanta VAMC (508) | PersonSID 2001<br>Portland VAMC (648)<br>**8 encounters** |
| ICN100010 | Alexander Aminor | PatientSID 1010<br>Dayton VAMC (552) | PersonSID 2010<br>Seattle VAMC (663)<br>**8 encounters** |

**Demo Narrative:**
> These patients received historical care at VistA sites (Atlanta, Dayton) and then relocated to Cerner sites (Portland, Seattle) after the sites migrated to Oracle Health. Med-z1's Silver layer will merge data from both systems to show complete longitudinal patient records.

---

## Sites

**Cerner Sites (Phase 1):**
- **648** - Portland VAMC (Oregon)
- **663** - Seattle VAMC (Washington)

*These sites represent real VA medical centers that have transitioned or will transition to Oracle Health.*

---

## Setup Instructions

### 1. Create Database and Schema

```bash
cd mock/sql-server/cdwwork2/create
./_master.sh
```

**Creates:**
- CDWWork2 database
- 5 schemas (NDimMill, VeteranMill, EncMill, VitalMill, AllergyMill)
- 6 tables (CodeValue, SPerson, Encounter, VitalResult, PersonAllergy, AdverseReaction)

### 2. Populate Demo Data

```bash
cd ../insert
./_master.sh
```

**Populates:**
- 48 code values (5 code sets)
- 2 patients (Adam Dooree, Alexander Aminor)
- 16 encounters (8 per patient at Portland and Seattle)

### 3. Verify Cross-Database Identity Resolution

```bash
cd /Users/chuck/swdev/med/med-z1
source .env
sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -i scripts/test_cdwwork2_identity.sql
```

**Tests:**
- PatientICN matching across CDWWork and CDWWork2
- Encounter count comparison
- Site distribution (VistA vs Cerner)

**Expected Result:** All tests pass, confirming ICN-based identity resolution works.

---

## Implementation Status

### ✅ Phase 1: Foundation (Days 1-2) - **COMPLETE**

**Deliverables:**
- [x] Database and schema structure
- [x] Consolidated code value system (NDimMill.CodeValue)
- [x] Patient demographics (2 demo patients)
- [x] Encounters (16 encounters across 2 sites)
- [x] Clinical domain schemas (Vitals, Allergies)
- [x] Cross-database identity resolution test

**Success Criteria Met:**
- ✅ Can query patients from both CDWWork and CDWWork2 using ICN
- ✅ Encounter data exists for both patients at Cerner sites
- ✅ Code value system supports vitals and allergies domains

---

### 🚧 Phase 2: Vitals Domain (Days 3-5) - **PENDING**

**Tasks:**
- [ ] Populate VitalMill.VitalResult with 5-10 vitals per patient
- [ ] Create `etl/bronze_cdwwork2_vitals.py` (extract from CDWWork2)
- [ ] Enhance `etl/silver_vitals.py` (merge CDWWork + CDWWork2)
- [ ] Enhance `etl/gold_vitals.py` (add `data_source` column)
- [ ] Update `db/ddl/patient_vitals.sql` (add `data_source VARCHAR(20)`)
- [ ] Update `app/db/vitals.py` (SELECT `data_source`)
- [ ] Update vitals UI (add source badges: "V" for VistA, "C" for Cerner)
- [ ] Test: View Adam Dooree vitals page, verify 20+ VistA + 10 Cerner vitals

**Success Criteria:**
- Unified vitals timeline with source indicators
- No duplicate vitals
- ETL runtime < 5 seconds

---

### 🚧 Phase 3: Allergies Domain (Days 6-8) - **PENDING**

**Tasks:**
- [ ] Populate AllergyMill.PersonAllergy with 2-3 allergies per patient
- [ ] Populate AllergyMill.AdverseReaction with 1-3 reactions per allergy
- [ ] Create `etl/bronze_cdwwork2_allergies.py`
- [ ] Enhance `etl/silver_allergies.py` (merge + deduplicate)
- [ ] Enhance `etl/gold_patient_allergies.py` (add `data_source`)
- [ ] Update `db/ddl/patient_allergies.sql` (add `data_source`)
- [ ] Update `app/db/allergies.py` (SELECT `data_source`)
- [ ] Update allergies UI (add source badges)
- [ ] Test: Verify deduplication (same allergy in both systems shows once)

**Success Criteria:**
- Combined allergy list with proper deduplication
- Reactions correctly linked to parent allergies
- Source lineage tracked for all records

---

### 🚧 Phase 4: Demo Polish (Days 9-10) - **PENDING**

**Tasks:**
- [ ] End-to-end workflow test (both patients, both domains)
- [ ] Performance validation (ETL < 5s total)
- [ ] UI consistency check (source badges, tooltips)
- [ ] Demo script preparation
- [ ] Documentation updates

**Demo Date Target:** January 6-10, 2026

---

## Architecture Decisions

### 1. Identity Resolution Strategy
- **Shared Key:** PatientICN (Integrated Care Number)
- **Internal IDs:** Differ by system (CDWWork PatientSID ≠ CDWWork2 PersonSID)
- **Join Pattern:** Always join on PatientICN, never on internal SIDs

### 2. Code Value Consolidation
- **Design:** Single NDimMill.CodeValue table replaces many Dim tables
- **Rationale:** Matches real Cerner data warehouse pattern
- **Benefit:** Simpler schema, easier to extend with new code sets

### 3. Encounter-Centric Model
- **Design:** All clinical data (vitals, allergies) linked to encounters
- **Rationale:** Reflects Cerner's architecture (vs VistA's patient-centric model)
- **Impact:** Silver layer must handle different join patterns during merge

### 4. Site Mutual Exclusivity
- **Rule:** Each Sta3n exists in either CDWWork OR CDWWork2, never both
- **Example:** Portland (648) is Cerner-only, Atlanta (508) is VistA-only
- **Rationale:** Simulates real VA migration pattern where sites transition fully

### 5. Data Source Lineage
- **Implementation:** Add `data_source VARCHAR(20)` to Gold/PostgreSQL tables
- **Values:** "CDWWork" or "CDWWork2"
- **Purpose:** Enable UI source badges, auditing, troubleshooting

---

## File Structure

```
mock/sql-server/cdwwork2/
├── README.md                          # This file
├── create/                            # CREATE TABLE scripts
│   ├── _master.sql                   # Master creation script
│   ├── _master.sh                    # Shell script to run master
│   ├── db_database.sql               # Drop/create CDWWork2 database
│   ├── db_schemas.sql                # Create all schemas
│   ├── NDimMill.CodeValue.sql        # Consolidated code values
│   ├── VeteranMill.SPerson.sql       # Patient demographics
│   ├── EncMill.Encounter.sql         # Encounters
│   ├── VitalMill.VitalResult.sql     # Vital signs
│   ├── AllergyMill.PersonAllergy.sql # Allergies
│   └── AllergyMill.AdverseReaction.sql # Adverse reactions
└── insert/                            # INSERT data scripts
    ├── _master.sql                    # Master insert script
    ├── _master.sh                     # Shell script to run master
    ├── NDimMill.CodeValue.sql         # Populate code sets (48 rows)
    ├── VeteranMill.SPerson.sql        # Populate patients (2 rows)
    └── EncMill.Encounter.sql          # Populate encounters (16 rows)
```

---

## Testing

### Manual Testing

**Cross-Database Patient Query:**
```sql
-- Verify patients exist in both databases
SELECT
    cdw.PatientSID AS VistA_PatientSID,
    cdw.PatientICN,
    cdw.PatientName AS VistA_Name,
    cerner.PersonSID AS Cerner_PersonSID,
    cerner.LastName + ', ' + cerner.FirstName AS Cerner_Name
FROM CDWWork.SPatient.SPatient cdw
FULL OUTER JOIN CDWWork2.VeteranMill.SPerson cerner
    ON cdw.PatientICN = cerner.PatientICN
WHERE cdw.PatientICN IN ('ICN100001', 'ICN100010')
ORDER BY cdw.PatientICN;
```

**Expected Result:** 2 rows, both with matching PatientICN values.

### Automated Testing

Run comprehensive test suite:
```bash
sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -i scripts/test_cdwwork2_identity.sql
```

---

## Next Steps

After Phase 1 completion, proceed with:

1. **Phase 2 (Days 3-5): Vitals Domain**
   - Populate VitalMill.VitalResult with demo vitals data
   - Implement Bronze ETL for CDWWork2 vitals
   - Enhance Silver layer to merge CDWWork + CDWWork2 vitals
   - Update Gold layer and PostgreSQL schema with `data_source` column
   - Add source badges to vitals UI

2. **Phase 3 (Days 6-8): Allergies Domain**
   - Populate AllergyMill tables with demo allergy data
   - Implement Bronze ETL for CDWWork2 allergies
   - Enhance Silver layer to merge and deduplicate allergies
   - Update Gold layer and PostgreSQL with `data_source`
   - Add source badges to allergies UI

3. **Phase 4 (Days 9-10): Demo Polish**
   - End-to-end testing
   - Demo script preparation
   - Performance optimization

---

## References

- **Design Document:** `/docs/spec/cdwwork2-design.md` (v1.3)
- **Architecture:** `/docs/spec/med-z1-architecture.md`
- **Main Application:** `/app/README.md`
- **ETL Patterns:** `/etl/README.md`

---

**Last Updated:** 2025-12-30
**Phase 1 Status:** ✅ Complete
**Next Milestone:** Phase 2 - Vitals Domain (3 days)
