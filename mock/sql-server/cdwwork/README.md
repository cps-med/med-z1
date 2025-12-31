# CDWWork - VistA Mock Database

**Purpose:** Simulate VistA (Veterans Health Information Systems and Technology Architecture) data from the VA Corporate Data Warehouse for local development and testing.

**Status:** ✅ Production - Fully populated with 4 patients across 7 clinical domains

---

## Overview

CDWWork is the primary mock database for the med-z1 project, simulating data from VA medical centers running the legacy VistA EHR system. It contains comprehensive patient data across multiple clinical domains, mirroring the structure and content of the real VA Corporate Data Warehouse.

**Key Characteristics:**
- **Patient-centric data model** - Data organized primarily by patient (PatientSID)
- **Rich dimension tables** - Separate tables for each code set (Dim.VitalType, Dim.Allergen, etc.)
- **Multiple schemas** - Domain-specific schemas (SPatient, Vital, Allergy, RxOut, etc.)
- **Production-ready** - 4 fully populated demo patients with realistic clinical scenarios

---

## Database Schema

### Schemas

| Schema | Purpose | Tables | Rows (Approx) |
|--------|---------|--------|---------------|
| **Dim** | Dimension/reference tables | 15+ | 500+ |
| **SPatient** | Patient demographics and administrative data | 5 | 20+ |
| **SStaff** | Staff and provider data | 2 | 10+ |
| **Inpat** | Inpatient encounters and admissions | 3 | 15+ |
| **RxOut** | Outpatient pharmacy (prescriptions) | 4 | 100+ |
| **BCMA** | Bar Code Medication Administration | 4 | 50+ |
| **Allergy** | Allergies and adverse reactions | 2 | 15+ |
| **Vital** | Vital signs measurements | 3 | 50+ |
| **Chem** | Laboratory chemistry results | 1 | 60+ |

### Key Tables

#### Demographics
- **SPatient.SPatient** - Patient master (4 patients)
- **SPatient.SPatientAddress** - Patient addresses
- **SPatient.SPatientInsurance** - Insurance coverage
- **SPatient.SPatientDisability** - Disability ratings

#### Patient Flags
- **Dim.PatientRecordFlag** - Flag definitions (National Cat I, Local Cat II)
- **SPatient.PatientRecordFlagAssignment** - Patient → Flag assignments
- **SPatient.PatientRecordFlagHistory** - Audit trail with narrative notes

#### Vitals
- **Dim.VitalType** - Vital sign types (Blood Pressure, Pulse, Temperature, etc.)
- **Dim.VitalQualifier** - Qualifiers (Standing, Sitting, Lying)
- **Vital.VitalSign** - Vital measurements (40+ readings)
- **Vital.VitalSignQualifier** - Vital → Qualifier link

#### Allergies
- **Dim.Allergen** - Allergen definitions (Penicillin, Aspirin, etc.)
- **Dim.Reaction** - Reaction types (Rash, Hives, Anaphylaxis, etc.)
- **Dim.AllergySeverity** - Severity levels (Mild, Moderate, Severe)
- **Allergy.PatientAllergy** - Patient allergy assignments (10+ allergies)
- **Allergy.PatientAllergyReaction** - Specific reactions per allergy

#### Medications
- **Dim.LocalDrug** - VA formulary drugs
- **Dim.NationalDrug** - National drug file
- **RxOut.RxOutpat** - Outpatient prescriptions (50+ prescriptions)
- **RxOut.RxOutpatFill** - Prescription fills
- **RxOut.RxOutpatSig** - Prescription instructions
- **RxOut.RxOutpatMedInstructions** - Medication instructions
- **BCMA.BCMAMedicationLog** - Medication administration records (30+ administrations)
- **BCMA.BCMADispensedDrug** - Dispensed medications
- **BCMA.BCMAAdditive** - Medication additives
- **BCMA.BCMASolution** - IV solutions

#### Laboratory Results
- **Dim.LabTest** - Lab test definitions (HbA1c, Glucose, Creatinine, etc.)
- **Chem.LabChem** - Lab chemistry results (58 results for 2 patients)

#### Inpatient Encounters
- **Inpat.Inpatient** - Inpatient admissions (4 admissions)
- **Inpat.PatientTransfer** - Ward transfers
- **Inpat.ProvisionalMovement** - Provisional bed assignments

#### Location & Site Data
- **Dim.Sta3n** - VA medical centers/stations (Atlanta, Dayton, etc.)
- **Dim.Location** - Clinical locations (clinics, wards)
- **Dim.WardLocation** - Inpatient ward locations
- **Dim.Division** - Facility divisions
- **Dim.VistASite** - VistA site information

---

## Demo Patients

### Patient 1001: Adam Dooree (ICN100001)

**Demographics:**
- **Name:** Dooree, Adam James
- **DOB:** 1980-01-02 (Age 45)
- **Gender:** Male
- **SSN:** 123-45-1001
- **Primary Site:** Atlanta VAMC (Sta3n 508)

**Clinical Conditions:**
- Type 2 Diabetes Mellitus
- Hypertension
- Hyperlipidemia

**Data Populated:**
- **Vitals:** 20+ readings (BP, Pulse, Temp, Weight) from 2020-2024
- **Allergies:** 2 drug allergies (Penicillin with Rash/Hives, Aspirin with GI upset)
- **Medications:** 5+ chronic medications (Metformin, Lisinopril, Atorvastatin)
- **Labs:** 15+ results (HbA1c, Glucose, Creatinine, Lipid panel)
- **Inpatient:** 1 admission (diabetic management)
- **Flags:** 2 patient flags (High Risk for Suicide Cat I, Behavioral Cat II)

**Demo Use:** Primary dual-source demo patient (also in CDWWork2 at Portland)

### Patient 1010: Alexander Aminor (ICN100010)

**Demographics:**
- **Name:** Aminor, Alexander Lee
- **DOB:** 1965-07-15 (Age 59)
- **Gender:** Male
- **SSN:** 234-56-1010
- **Primary Site:** Dayton VAMC (Sta3n 552)

**Clinical Conditions:**
- Post-Vietnam veteran
- Cardiac history
- General health monitoring

**Data Populated:**
- **Vitals:** Multiple readings across all vital types
- **Allergies:** Drug and environmental allergies
- **Medications:** Multiple prescriptions
- **Labs:** Comprehensive lab panel
- **Inpatient:** 1 admission (cardiac workup)
- **Flags:** 1 patient flag (Combat Veteran Cat I)

**Demo Use:** Secondary dual-source demo patient (also in CDWWork2 at Seattle)

### Patient 1012: Helen Martinez (ICN100012)

**Demographics:**
- **Name:** Martinez, Helen
- **DOB:** 1975-05-20 (Age 50)
- **Gender:** Female
- **SSN:** 345-67-1012
- **Primary Site:** Multiple sites

**Clinical Conditions:**
- Comprehensive VistA data across all domains

**Data Populated:**
- **Vitals:** Full vital signs history
- **Allergies:** Multiple allergies with reactions
- **Medications:** Active prescriptions
- **Labs:** Lab results available
- **Inpatient:** Encounter history
- **Flags:** Patient flags assigned

**Demo Use:** VistA-only patient for control scenarios

### Patient 1025: Dorothy Martinez (1025V012345)

**Demographics:**
- **Name:** Martinez, Dorothy
- **DOB:** 1950-10-10 (Age 75)
- **Gender:** Female
- **SSN:** 456-78-1025
- **ICN Format:** 1025V012345 (alternate format)
- **Primary Site:** Multiple sites

**Clinical Conditions:**
- Elderly veteran with complex care needs

**Data Populated:**
- **Vitals:** Vital signs monitoring
- **Allergies:** Documented allergies
- **Medications:** Medication regimen
- **Labs:** Laboratory monitoring
- **Inpatient:** Admission history
- **Flags:** Patient record flags

**Demo Use:** Alternate ICN format testing and VistA-only scenarios

---

## VistA Data Model Patterns

### Patient-Centric Design

VistA organizes data primarily around patients:

```
SPatient.SPatient (PatientSID)
    ├─→ Vital.VitalSign (links to PatientSID)
    ├─→ Allergy.PatientAllergy (links to PatientSID)
    ├─→ RxOut.RxOutpat (links to PatientSID)
    ├─→ Chem.LabChem (links to PatientSID)
    └─→ Inpat.Inpatient (links to PatientSID)
```

### Dimension Table Pattern

Each clinical domain has dedicated dimension tables:

```
Vital Signs:
    Dim.VitalType (Blood Pressure, Pulse, etc.)
    Dim.VitalQualifier (Standing, Sitting, etc.)

Allergies:
    Dim.Allergen (Penicillin, Aspirin, etc.)
    Dim.Reaction (Rash, Hives, etc.)
    Dim.AllergySeverity (Mild, Moderate, Severe)

Labs:
    Dim.LabTest (HbA1c, Glucose, etc.)
```

### Identity and Linking

- **PatientSID:** Internal VistA patient ID (e.g., 1001, 1010)
- **PatientICN:** Shared enterprise patient ID (e.g., ICN100001)
- **Sta3n:** Site/facility identifier (e.g., 508 for Atlanta)

---

## Setup Instructions

### 1. Create Database Structure

```bash
cd mock/sql-server/cdwwork/create
./_master.sh
```

**Output:**
```
Creating CDWWork database...
Creating schemas: Dim, SPatient, SStaff, Inpat, RxOut, BCMA, Allergy, Vital, Chem
Creating 50+ tables...
All tables created successfully.
```

**What this creates:**
- CDWWork database
- 8 schemas
- 50+ dimension and clinical tables with indexes and constraints

### 2. Populate Demo Data

```bash
cd ../insert
./_master.sh
```

**Output:**
```
Populating dimension tables...
Populating patient data...
Populating clinical domains...
Total: 4 patients, 7 domains, 300+ total records
```

**What this populates:**
- Dimension tables (locations, drugs, allergens, vital types, etc.)
- 4 patients (Adam, Alexander, Helen, Dorothy)
- 40+ vitals, 10+ allergies, 50+ medications, 58 labs, 4 inpatient encounters

### 3. Verify Data

```bash
# Quick verification
sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -Q \
    "SELECT COUNT(*) AS PatientCount FROM CDWWork.SPatient.SPatient"
# Expected: 4

sqlcmd -S 127.0.0.1,1433 -U sa -P "${CDWWORK_DB_PASSWORD}" -C -Q \
    "SELECT COUNT(*) AS VitalCount FROM CDWWork.Vital.VitalSign"
# Expected: 40+
```

---

## File Structure

```
cdwwork/
├── README.md                           # This file
├── create/                             # CREATE TABLE scripts
│   ├── _master.sql                    # Master creation script
│   ├── _master.sh                     # Shell wrapper
│   ├── db_database.sql                # Database creation
│   ├── db_schemas.sql                 # Schema creation
│   │
│   ├── Dim.Country.sql                # Geographic dimensions
│   ├── Dim.State.sql
│   ├── Dim.Sta3n.sql                  # VA sites
│   ├── Dim.VistASite.sql
│   ├── Dim.Location.sql               # Clinical locations
│   ├── Dim.WardLocation.sql
│   ├── Dim.Division.sql
│   │
│   ├── Dim.VitalType.sql              # Vitals dimensions
│   ├── Dim.VitalQualifier.sql
│   │
│   ├── Dim.Allergen.sql               # Allergy dimensions
│   ├── Dim.Reaction.sql
│   ├── Dim.AllergySeverity.sql
│   │
│   ├── Dim.LocalDrug.sql              # Medication dimensions
│   ├── Dim.NationalDrug.sql
│   │
│   ├── Dim.LabTest.sql                # Lab dimensions
│   │
│   ├── Dim.PatientRecordFlag.sql      # Flag dimensions
│   ├── Dim.PeriodOfService.sql
│   ├── Dim.InsuranceCompany.sql
│   │
│   ├── SPatient.SPatient.sql          # Patient tables
│   ├── SPatient.SPatientAddress.sql
│   ├── SPatient.SPatientInsurance.sql
│   ├── SPatient.SPatientDisability.sql
│   ├── SPatient.PatientRecordFlagAssignment.sql
│   ├── SPatient.PatientRecordFlagHistory.sql
│   │
│   ├── SStaff.SStaff.sql              # Staff tables
│   ├── SStaff.RadiologyNuclearMedicineReport.sql
│   │
│   ├── Vital.VitalSign.sql            # Vitals tables
│   ├── Vital.VitalSignQualifier.sql
│   │
│   ├── Allergy.PatientAllergy.sql     # Allergy tables
│   ├── Allergy.PatientAllergyReaction.sql
│   │
│   ├── RxOut.RxOutpat.sql             # Medication tables
│   ├── RxOut.RxOutpatFill.sql
│   ├── RxOut.RxOutpatSig.sql
│   ├── RxOut.RxOutpatMedInstructions.sql
│   │
│   ├── BCMA.BCMAMedicationLog.sql     # Med administration
│   ├── BCMA.BCMADispensedDrug.sql
│   ├── BCMA.BCMAAdditive.sql
│   ├── BCMA.BCMASolution.sql
│   │
│   ├── Inpat.Inpatient.sql            # Inpatient tables
│   ├── Inpat.PatientTransfer.sql
│   ├── Inpat.ProvisionalMovement.sql
│   │
│   └── Chem.LabChem.sql               # Laboratory tables
│
└── insert/                             # INSERT data scripts
    ├── _master.sql                    # Master insert script
    ├── _master.sh                     # Shell wrapper
    └── [matching INSERT scripts for each table above]
```

---

## Testing & Validation

### Basic Queries

**Patient List:**
```sql
SELECT PatientSID, PatientICN, PatientName, BirthDateTime, Gender, SSN
FROM CDWWork.SPatient.SPatient
ORDER BY PatientSID;
```

**Vitals for Adam Dooree:**
```sql
SELECT
    v.VitalSignTakenDateTime,
    vt.VitalType,
    v.VitalResultNumeric,
    v.VitalResult
FROM CDWWork.Vital.VitalSign v
JOIN CDWWork.SPatient.SPatient p ON v.PatientSID = p.PatientSID
JOIN CDWWork.Dim.VitalType vt ON v.VitalTypeSID = vt.VitalTypeSID
WHERE p.PatientICN = 'ICN100001'
ORDER BY v.VitalSignTakenDateTime DESC;
```

**Allergies for Alexander Aminor:**
```sql
SELECT
    a.AllergenName,
    s.AllergySeverity,
    pa.ObservedDateTime,
    pa.VerifiedDateTime
FROM CDWWork.Allergy.PatientAllergy pa
JOIN CDWWork.Dim.Allergen a ON pa.AllergenSID = a.AllergenSID
LEFT JOIN CDWWork.Dim.AllergySeverity s ON pa.AllergySeveritySID = s.AllergySeveritySID
JOIN CDWWork.SPatient.SPatient p ON pa.PatientSID = p.PatientSID
WHERE p.PatientICN = 'ICN100010';
```

**Lab Results:**
```sql
SELECT
    p.PatientName,
    lt.LabTestName,
    lc.LabChemResultValue,
    lc.LabChemResultNumericValue,
    lc.Units,
    lc.LabChemSpecimenDateTime
FROM CDWWork.Chem.LabChem lc
JOIN CDWWork.SPatient.SPatient p ON lc.PatientSID = p.PatientSID
JOIN CDWWork.Dim.LabTest lt ON lc.LabTestSID = lt.LabTestSID
WHERE p.PatientICN IN ('ICN100001', 'ICN100010')
ORDER BY p.PatientName, lc.LabChemSpecimenDateTime DESC;
```

### Data Completeness Check

```sql
-- Data coverage by patient and domain
SELECT
    p.PatientName,
    p.PatientICN,
    COUNT(DISTINCT v.VitalSignSID) AS VitalCount,
    COUNT(DISTINCT pa.PatientAllergySID) AS AllergyCount,
    COUNT(DISTINCT rx.RxOutpatSID) AS MedicationCount,
    COUNT(DISTINCT lc.LabChemSID) AS LabCount,
    COUNT(DISTINCT i.InpatientSID) AS InpatientCount
FROM CDWWork.SPatient.SPatient p
LEFT JOIN CDWWork.Vital.VitalSign v ON p.PatientSID = v.PatientSID
LEFT JOIN CDWWork.Allergy.PatientAllergy pa ON p.PatientSID = pa.PatientSID
LEFT JOIN CDWWork.RxOut.RxOutpat rx ON p.PatientSID = rx.PatientSID
LEFT JOIN CDWWork.Chem.LabChem lc ON p.PatientSID = lc.PatientSID
LEFT JOIN CDWWork.Inpat.Inpatient i ON p.PatientSID = i.PatientSID
GROUP BY p.PatientName, p.PatientICN
ORDER BY p.PatientName;
```

---

## Integration with ETL Pipeline

### Bronze Layer Extraction

CDWWork is the primary data source for Bronze layer ETL scripts:

```python
# Example: etl/bronze_vitals.py
from sqlalchemy import create_engine

# Connect to CDWWork
engine = create_engine(cdwwork_connection_string)

# Extract vitals
query = """
SELECT
    vs.VitalSignSID,
    vs.PatientSID,
    p.PatientICN,
    vt.VitalType,
    vs.VitalResultNumeric,
    vs.VitalSignTakenDateTime,
    vs.Sta3n
FROM CDWWork.Vital.VitalSign vs
JOIN CDWWork.SPatient.SPatient p ON vs.PatientSID = p.PatientSID
JOIN CDWWork.Dim.VitalType vt ON vs.VitalTypeSID = vt.VitalTypeSID
"""

# Write to Bronze Parquet
df = pl.read_database(query, engine)
write_parquet(df, "bronze/vitals/vitals_cdwwork.parquet")
```

### Silver Layer Harmonization

Silver layer merges CDWWork (VistA) data with CDWWork2 (Cerner) data:

```python
# Example: etl/silver_vitals.py

# Read both sources
cdwwork_vitals = read_parquet("bronze/vitals/vitals_cdwwork.parquet")
cdwwork2_vitals = read_parquet("bronze/vitals/vitals_cdwwork2.parquet")

# Harmonize schemas (different column names)
cdwwork_harmonized = harmonize_vista_vitals(cdwwork_vitals)
cdwwork2_harmonized = harmonize_cerner_vitals(cdwwork2_vitals)

# Merge on PatientICN + TakenDateTime
merged = merge_vitals(cdwwork_harmonized, cdwwork2_harmonized)

# Write to Silver
write_parquet(merged, "silver/vitals/vitals_merged.parquet")
```

---

## Comparison to CDWWork2 (Cerner)

| Aspect | CDWWork (VistA) | CDWWork2 (Cerner) |
|--------|-----------------|-------------------|
| **Patients** | 4 (all 4 patients) | 2 (Adam, Alexander only) |
| **Data Model** | Patient-centric | Encounter-centric |
| **Vitals Storage** | Vital.VitalSign → PatientSID | VitalMill.VitalResult → EncounterSID |
| **Code Sets** | Dim.VitalType, Dim.Allergen, etc. | NDimMill.CodeValue (consolidated) |
| **Sites** | 508, 552, others | 648, 663 only |
| **Maturity** | ✅ Production (complete) | 🚧 Phase 1 (foundation only) |

**Key Insight:** CDWWork is the mature, production-ready database with comprehensive data. CDWWork2 is being built incrementally to demonstrate dual-source capability.

---

## Troubleshooting

**Issue:** "Invalid object name 'CDWWork.SPatient.SPatient'"
- **Cause:** Database or table doesn't exist
- **Solution:** Run `cd create && ./_master.sh`

**Issue:** "No rows returned for patient ICN100001"
- **Cause:** Data not populated
- **Solution:** Run `cd insert && ./_master.sh`

**Issue:** "Login failed for user 'sa'"
- **Cause:** Incorrect password or SQL Server not running
- **Solution:** Check `.env` file and verify SQL Server container: `docker ps`

**Issue:** "Permission denied: ./_master.sh"
- **Cause:** Script not executable
- **Solution:** `chmod +x _master.sh`

---

## Related Documentation

- **Parent README:** `/mock/README.md` (comprehensive overview of both databases)
- **CDWWork2 README:** `/mock/sql-server/cdwwork2/README.md` (Cerner implementation)
- **Design Spec:** `/docs/spec/cdwwork2-design.md` (dual-source architecture)
- **ETL Pipeline:** `/etl/README.md` (Bronze/Silver/Gold transformations)

---

**Last Updated:** 2025-12-30
**Status:** ✅ Production - Fully Populated
**Patients:** 4 (Adam, Alexander, Helen, Dorothy)
**Domains:** 7 (Demographics, Vitals, Allergies, Meds, Labs, Inpatient, Flags)
**Total Records:** 300+
