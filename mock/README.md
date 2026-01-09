# Mock Data Subsystem

**Mock Data Service for VA Healthcare Analytics and JLV Viewer Development**

---

## Overview

The **mock** subsystem provides synthetic patient data that simulates the VA Corporate Data Warehouse (CDW) environment for local development, testing, and demonstration of the med-z1 application. All data is **synthetic** and contains **no PHI or PII**.

**Key Features:**
- ✅ Dual-source data architecture (VistA + Oracle Health/Cerner)
- ✅ 4 demo patients with comprehensive clinical data
- ✅ 7+ clinical domains (Demographics, Vitals, Allergies, Meds, Labs, Encounters, Flags)
- ✅ Shared patient identity (ICN) enabling cross-database queries
- ✅ Real VA site mappings (Atlanta, Dayton, Portland, Seattle)

---

## Data Sources

### CDWWork (VistA-Based Mock Database)

**Purpose:** Simulates legacy VistA data from the VA Corporate Data Warehouse

| Attribute | Details |
|-----------|---------|
| **Database** | CDWWork (Microsoft SQL Server 2019) |
| **EHR System** | VistA (Veterans Health Information Systems and Technology Architecture) |
| **Data Model** | Patient-centric (data organized by patient) |
| **Sites** | Atlanta (508), Dayton (552), + others |
| **Schemas** | Dim, SPatient, SStaff, Inpat, RxOut, BCMA, Allergy, Vital, Chem |
| **Status** | ✅ Production - Fully populated with 4 patients across 7 domains |
| **Directory** | `mock/sql-server/cdwwork/` |

**Populated Domains:**
- Demographics (SPatient.SPatient)
- Vitals (Vital.VitalSign)
- Allergies (Allergy.PatientAllergy)
- Medications - Outpatient (RxOut.RxOutpat) + Administration (BCMA.BCMAMedicationLog)
- Laboratory Results (Chem.LabChem)
- Inpatient Encounters (Inpat.Inpatient)
- Patient Flags (SPatient.PatientRecordFlagAssignment)

### CDWWork2 (Oracle Health/Cerner Mock Database)

**Purpose:** Simulates new Oracle Health (Cerner) data from sites that have migrated

| Attribute | Details |
|-----------|---------|
| **Database** | CDWWork2 (Microsoft SQL Server 2019) |
| **EHR System** | Oracle Health (formerly Cerner Millennium) |
| **Data Model** | Encounter-centric (data organized by encounters) |
| **Sites** | Portland (648), Seattle (663) |
| **Schemas** | NDimMill, VeteranMill, EncMill, VitalMill, AllergyMill |
| **Status** | 🚧 Phase 1 Complete - Foundation ready, clinical data pending |
| **Directory** | `mock/sql-server/cdwwork2/` |

**Populated (Phase 1):**
- Code Value System (NDimMill.CodeValue) - 48 codes across 5 code sets
- Patient Demographics (VeteranMill.SPerson) - 2 patients
- Encounters (EncMill.Encounter) - 16 encounters

**Pending (Phase 2-3):**
- Vitals (VitalMill.VitalResult) - TBD
- Allergies (AllergyMill.PersonAllergy, AdverseReaction) - TBD

---

## Side-by-Side Comparison: VistA vs Oracle Health

| Aspect | CDWWork (VistA) | CDWWork2 (Oracle Health) |
|--------|-----------------|--------------------------|
| **Data Organization** | Patient-centric | Encounter-centric |
| **Code Sets** | Many Dim tables (VitalType, Allergen, etc.) | Single consolidated table (NDimMill.CodeValue) |
| **Patient Table** | SPatient.SPatient | VeteranMill.SPerson |
| **Internal ID** | PatientSID | PersonSID |
| **Shared Identity** | PatientICN | PatientICN ✅ (same) |
| **Encounter Linking** | Optional (some domains don't require it) | Required (all clinical data links to encounters) |
| **Example Domain** | Vital.VitalSign → links to PatientSID | VitalMill.VitalResult → links to EncounterSID + PersonSID |

**Key Insight:** Despite architectural differences, both databases share **PatientICN** as the common identity key, enabling med-z1's Silver layer to merge data seamlessly.

---

## Demo Patients (Unified Registry)

### Patient Identity Mapping

| PatientICN | Name | CDWWork (VistA) | CDWWork2 (Cerner) | Demo Use |
|-----------|------|-----------------|-------------------|----------|
| **ICN100001** | Adam Dooree | PatientSID 1001<br>Atlanta (508) | PersonSID 2001<br>Portland (648) | ✅ Primary dual-source demo |
| **ICN100010** | Alexander Aminor | PatientSID 1010<br>Dayton (552) | PersonSID 2010<br>Seattle (663) | ✅ Secondary dual-source demo |
| **ICN100012** | Helen Martinez | PatientSID 1012<br>Multiple sites | N/A | VistA-only patient |
| **1025V012345** | Dorothy Martinez | PatientSID 1025<br>Multiple sites | N/A | VistA-only patient |

### Data Coverage Matrix

| Domain | Adam Dooree | Alexander Aminor | Helen Martinez | Dorothy Martinez |
|--------|-------------|------------------|----------------|------------------|
| **Demographics** | ✅ VistA + Cerner | ✅ VistA + Cerner | ✅ VistA | ✅ VistA |
| **Vitals** | ✅ VistA (20+)<br>🚧 Cerner (pending) | ✅ VistA<br>🚧 Cerner (pending) | ✅ VistA | ✅ VistA |
| **Allergies** | ✅ VistA (2)<br>🚧 Cerner (pending) | ✅ VistA<br>🚧 Cerner (pending) | ✅ VistA | ✅ VistA |
| **Medications** | ✅ VistA | ✅ VistA | ✅ VistA | ✅ VistA |
| **Labs** | ✅ VistA (15+) | ✅ VistA | ✅ VistA | ✅ VistA |
| **Inpatient** | ✅ VistA (1) | ✅ VistA (1) | ✅ VistA | ✅ VistA |
| **Flags** | ✅ VistA (2) | ✅ VistA (1) | ✅ VistA | ✅ VistA |
| **Encounters (Cerner)** | ✅ Cerner (8) | ✅ Cerner (8) | N/A | N/A |

**Legend:**
- ✅ Data populated and available
- 🚧 Schema ready, data pending (Phase 2-3)
- N/A Not applicable (patient not in this system)

---

## Demo Narratives

### Adam Dooree (ICN100001) - Primary Dual-Source Demo

**Background:**
- 45-year-old male veteran with Type 2 Diabetes and Hypertension
- **Historical Care:** Atlanta VAMC (Sta3n 508, VistA) - 2020-2024
- **Current Care:** Portland VAMC (Sta3n 648, Oracle Health) - June 2024-present
- **Relocation Reason:** Moved to Portland for employment in mid-2024

**Clinical Data:**
- VistA: 20+ vital signs, 2 drug allergies, chronic medications, 15+ lab results, 1 inpatient admission, 2 patient flags
- Cerner: 8 encounters at Portland (including 1 inpatient admission for diabetic management)

**Demo Value:** Shows complete longitudinal record spanning VistA and Cerner systems after site migration.

### Alexander Aminor (ICN100010) - Secondary Dual-Source Demo

**Background:**
- 59-year-old male veteran, post-Vietnam service
- **Historical Care:** Dayton VAMC (Sta3n 552, VistA) - Historical
- **Current Care:** Seattle VAMC (Sta3n 663, Oracle Health) - September 2024-present
- **Relocation Reason:** Moved to Seattle in late 2024

**Clinical Data:**
- VistA: Comprehensive vitals, allergies, medications, labs, 1 inpatient encounter, 1 patient flag
- Cerner: 8 encounters at Seattle (including 1 inpatient admission for chest pain evaluation)

**Demo Value:** Demonstrates patient mobility and dual-source data merge for cardiac care continuity.

### Helen Martinez (ICN100012) - VistA-Only Patient

**Background:**
- Female veteran with comprehensive VistA data across multiple domains
- Remains at VistA site (has not relocated to Cerner site)

**Demo Value:** Control patient for VistA-only workflows and data completeness testing.

### Dorothy Martinez (1025V012345) - VistA-Only Patient

**Background:**
- Female veteran with VistA data
- Uses alternate ICN format (1025V012345)

**Demo Value:** Tests alternate ICN format handling and VistA-only patient scenarios.

---

## Quick Setup Guide

### Prerequisites

- Docker or Podman running SQL Server 2019 container
- sqlcmd CLI tool installed
- Environment variables configured in `.env` file

### 1. Create CDWWork (VistA) Database

```bash
cd mock/sql-server/cdwwork/create
./_master.sh
```

**Creates:**
- CDWWork database
- 8 schemas (Dim, SPatient, SStaff, Inpat, RxOut, BCMA, Allergy, Vital, Chem)
- 50+ dimension and clinical tables

### 2. Populate CDWWork Data

```bash
cd ../insert
./_master.sh
```

**Populates:**
- 4 patients (Adam, Alexander, Helen, Dorothy)
- 7 clinical domains with comprehensive data
- Dimension tables (locations, drugs, allergens, etc.)

### 3. Create CDWWork2 (Cerner) Database

```bash
cd ../../cdwwork2/create
./_master.sh
```

**Creates:**
- CDWWork2 database
- 5 schemas (NDimMill, VeteranMill, EncMill, VitalMill, AllergyMill)
- 6 tables (consolidated code sets, demographics, encounters, vitals, allergies)

### 4. Populate CDWWork2 Data (Phase 1)

```bash
cd ../insert
./_master.sh
```

**Populates:**
- 48 code values (5 code sets)
- 2 patients (Adam, Alexander)
- 16 encounters at Portland and Seattle

### 5. Verify Cross-Database Identity Resolution

```bash
cd /Users/chuck/swdev/med/med-z1
source .env
sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -i scripts/test_cdwwork2_identity.sql
```

**Expected:** All tests pass, confirming PatientICN-based identity resolution works.

---

## Directory Structure

```
mock/
├── README.md                           # This file (comprehensive overview)
├── shared/                             # Shared resources (future)
│   └── patient-registry.csv           # Future: unified patient registry
└── sql-server/                         # Microsoft SQL Server mock databases
    ├── cdwwork/                        # VistA-based mock CDW
    │   ├── README.md                   # Detailed VistA implementation guide
    │   ├── create/                     # CREATE TABLE scripts
    │   │   ├── _master.sql            # Master creation script
    │   │   ├── _master.sh             # Shell wrapper
    │   │   ├── db_database.sql        # Database creation
    │   │   ├── db_schemas.sql         # Schema creation
    │   │   ├── Dim.*.sql              # Dimension tables (15+)
    │   │   ├── SPatient.*.sql         # Patient tables (5+)
    │   │   ├── Allergy.*.sql          # Allergy tables (2)
    │   │   ├── Vital.*.sql            # Vital signs tables (3)
    │   │   ├── RxOut.*.sql            # Medications tables (4)
    │   │   ├── BCMA.*.sql             # Med administration (4)
    │   │   ├── Inpat.*.sql            # Inpatient tables (3)
    │   │   └── Chem.*.sql             # Laboratory tables (1)
    │   └── insert/                     # INSERT data scripts
    │       ├── _master.sql            # Master insert script
    │       ├── _master.sh             # Shell wrapper
    │       └── [matching table inserts]
    │
    └── cdwwork2/                       # Oracle Health/Cerner mock CDW
        ├── README.md                   # Detailed Cerner implementation guide
        ├── create/                     # CREATE TABLE scripts
        │   ├── _master.sql            # Master creation script
        │   ├── _master.sh             # Shell wrapper
        │   ├── db_database.sql        # Database creation
        │   ├── db_schemas.sql         # Schema creation
        │   ├── NDimMill.CodeValue.sql # Consolidated code sets
        │   ├── VeteranMill.SPerson.sql # Patient demographics
        │   ├── EncMill.Encounter.sql  # Encounters
        │   ├── VitalMill.VitalResult.sql # Vitals
        │   └── AllergyMill.*.sql      # Allergies (2 tables)
        └── insert/                     # INSERT data scripts
            ├── _master.sql            # Master insert script
            ├── _master.sh             # Shell wrapper
            └── [matching table inserts]
```

---

## Testing & Validation

### Verify CDWWork Data

```sql
-- Check patient count
SELECT COUNT(*) FROM CDWWork.SPatient.SPatient;  -- Expected: 4

-- Check vitals count
SELECT COUNT(*) FROM CDWWork.Vital.VitalSign;     -- Expected: 40+

-- Check Adam Dooree data
SELECT * FROM CDWWork.SPatient.SPatient WHERE PatientICN = 'ICN100001';
```

### Verify CDWWork2 Data

```sql
-- Check patient count
SELECT COUNT(*) FROM CDWWork2.VeteranMill.SPerson;  -- Expected: 2

-- Check code values
SELECT CodeSet, COUNT(*)
FROM CDWWork2.NDimMill.CodeValue
GROUP BY CodeSet;  -- Expected: 5 code sets

-- Check encounters
SELECT COUNT(*) FROM CDWWork2.EncMill.Encounter;  -- Expected: 16
```

### Cross-Database Identity Resolution

```sql
-- Verify PatientICN matching
SELECT
    cdw.PatientICN,
    cdw.PatientName AS VistA_Name,
    cerner.LastName + ', ' + cerner.FirstName AS Cerner_Name
FROM CDWWork.SPatient.SPatient cdw
JOIN CDWWork2.VeteranMill.SPerson cerner
    ON cdw.PatientICN = cerner.PatientICN
ORDER BY cdw.PatientICN;
-- Expected: 2 rows (Adam, Alexander)
```

---

## Integration with med-z1 ETL Pipeline

### Bronze Layer
- **Purpose:** Extract raw data from CDWWork and CDWWork2
- **Files:** `etl/bronze_*.py` scripts
- **Output:** Bronze Parquet files in MinIO (`bronze/vitals/`, `bronze/allergies/`, etc.)

### Silver Layer
- **Purpose:** Harmonize and merge data from both sources
- **Files:** `etl/silver_*.py` scripts
- **Identity Resolution:** JOIN on PatientICN
- **Output:** Silver Parquet files with unified patient records

### Gold Layer
- **Purpose:** Create curated, query-optimized views
- **Files:** `etl/gold_*.py` scripts
- **Data Source Tracking:** Add `data_source` column ("CDWWork" or "CDWWork2")
- **Output:** Gold Parquet files ready for PostgreSQL loading

### PostgreSQL Serving Database
- **Purpose:** Low-latency queries for med-z1 UI
- **Files:** `etl/load_*.py` scripts
- **Tables:** `clinical.patient_vitals`, `clinical.patient_allergies`, etc.
- **Source Badges:** UI displays "V" (VistA) or "C" (Cerner) based on `data_source` column

---

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| **CDWWork (VistA)** | ✅ Production | 4 patients, 7 domains, fully populated |
| **CDWWork2 (Cerner) - Phase 1** | ✅ Complete | Foundation ready (code sets, patients, encounters) |
| **CDWWork2 (Cerner) - Phase 2** | 🚧 Pending | Vitals domain (Days 3-5) |
| **CDWWork2 (Cerner) - Phase 3** | 🚧 Pending | Allergies domain (Days 6-8) |
| **Dual-Source ETL** | 🚧 Pending | Bronze/Silver/Gold enhancements (Phase 2-3) |
| **UI Source Badges** | 🚧 Pending | Display VistA vs Cerner indicators (Phase 2-3) |

---

## Future Enhancements

**Additional Clinical Domains (CDWWork2):**
- Labs (LabMill.LabResult)
- Medications (PharmMill.MedicationOrder)
- Imaging (RadMill.ImagingExam)
- Notes (DocMill.ClinicalDocument)

**Additional Patients:**
- Expand to 6-8 demo patients with varied care patterns
- Add patients with DoD/CHCS data (non-VA care)

**Shared Patient Registry:**
- Create `mock/shared/patient-registry.csv` with unified patient metadata
- Single source of truth for all ICNs across databases

**Data Quality Scenarios:**
- Duplicate records (same data in both VistA and Cerner)
- Conflicting data (different values for same clinical observation)
- Missing data (gaps in one system but not the other)

---

## Key Design Decisions

### 1. Shared Identity (PatientICN)
- **Decision:** Use PatientICN as primary identity key across all databases
- **Rationale:** Mirrors real VA CDW where ICN is the enterprise patient identifier
- **Impact:** Enables seamless cross-database JOINs without complex identity resolution logic

### 2. Site Mutual Exclusivity
- **Decision:** Each Sta3n exists in either CDWWork OR CDWWork2, never both
- **Rationale:** Simulates real VA migration pattern where sites fully transition
- **Example:** Portland (648) is Cerner-only, Atlanta (508) is VistA-only

### 3. Dual-Source Patients
- **Decision:** Adam and Alexander exist in both CDWWork and CDWWork2
- **Rationale:** Demonstrates patient mobility and dual-source merge capability
- **Demo Value:** Shows complete longitudinal records spanning both systems

### 4. Data Source Lineage
- **Decision:** Track data origin with `data_source` column in Gold/PostgreSQL
- **Rationale:** Enables UI source badges, auditing, and troubleshooting
- **Values:** "CDWWork" or "CDWWork2"

---

## Related Documentation

- **CDWWork (VistA) Details:** `mock/sql-server/cdwwork/README.md`
- **CDWWork2 (Cerner) Details:** `mock/sql-server/cdwwork2/README.md`
- **Design Specification:** `docs/spec/cdwwork2-design.md` (v1.3)
- **Architecture Decisions:** `docs/spec/med-z1-architecture.md`
- **ETL Pipeline:** `etl/README.md`

---

## Support & Troubleshooting

### Common Issues

**Issue:** "CDWWork database does not exist"
- **Solution:** Run `cd mock/sql-server/cdwwork/create && ./_master.sh`

**Issue:** "No data returned for patient ICN100001"
- **Solution:** Run `cd mock/sql-server/cdwwork/insert && ./_master.sh`

**Issue:** "Cross-database query fails"
- **Solution:** Verify both CDWWork and CDWWork2 exist: `sqlcmd -Q "SELECT name FROM sys.databases"`

**Issue:** "Permission denied on _master.sh"
- **Solution:** Make executable: `chmod +x _master.sh`

### Rebuild Databases

To completely rebuild both mock databases:

```bash
# Rebuild CDWWork (VistA)
cd mock/sql-server/cdwwork/create
./_master.sh
cd ../insert
./_master.sh

# Rebuild CDWWork2 (Cerner)
cd ../../cdwwork2/create
./_master.sh
cd ../insert
./_master.sh

# Verify
cd /Users/chuck/swdev/med/med-z1
sqlcmd -Q "SELECT name FROM sys.databases WHERE name LIKE 'CDW%'"
```

---

**Last Updated:** 2025-12-30
**CDWWork Status:** ✅ Production (4 patients, 7 domains)
**CDWWork2 Status:** ✅ Phase 1 Complete, 🚧 Phase 2-3 Pending
**Demo Target:** January 6-10, 2026
