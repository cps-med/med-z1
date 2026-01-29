# med-z1 SQL Server Mock CDW Database Reference

**Document Version:** v1.0
**Last Updated:** 2026-01-29
**Databases:** `CDWWork`, `CDWWork2`
**SQL Server Version:** Microsoft SQL Server 2019

---

## Table of Contents

1. [Overview](#overview)
2. [Database Organization](#database-organization)
3. [Identity and Key Patterns](#identity-and-key-patterns)
4. [CDWWork Database (VistA)](#cdwwork-database-vista)
   - [Schema: Dim (Dimensions)](#schema-dim-dimensions)
   - [Schema: SPatient (Patient Demographics)](#schema-spatient-patient-demographics)
   - [Schema: SStaff (Staff/Providers)](#schema-sstaff-staffproviders)
   - [Schema: Vital](#schema-vital)
   - [Schema: Allergy](#schema-allergy)
   - [Schema: RxOut (Outpatient Pharmacy)](#schema-rxout-outpatient-pharmacy)
   - [Schema: BCMA (Medication Administration)](#schema-bcma-medication-administration)
   - [Schema: Inpat (Inpatient Encounters)](#schema-inpat-inpatient-encounters)
   - [Schema: Chem (Laboratory)](#schema-chem-laboratory)
   - [Schema: TIU (Clinical Notes)](#schema-tiu-clinical-notes)
   - [Schema: Immunization](#schema-immunization)
5. [CDWWork2 Database (Cerner/Oracle Health)](#cdwwork2-database-cerneroracle-health)
   - [Schema: VeteranMill](#schema-veteranmill)
   - [Schema: VitalMill](#schema-vitalmill)
   - [Schema: ImmunizationMill](#schema-immunizationmill)
   - [Schema: AllergyMill](#schema-allergymill)
   - [Schema: EncMill](#schema-encmill)
   - [Schema: NDimMill](#schema-ndimmill)
6. [Cross-Database Harmonization](#cross-database-harmonization)
7. [Common Query Patterns](#common-query-patterns)

---

## Overview

The **med-z1 SQL Server Mock CDW databases** simulate the VA Corporate Data Warehouse (CDW) as the source system for the med-z1 application's ETL pipelines. These databases contain **synthetic, non-PHI/PII data** for development and testing purposes.

**Key Characteristics:**
- **Purpose:** Source system for ETL Bronze layer extraction
- **Two Databases:**
  - **CDWWork**: Simulates VistA-based CDW data (primary VA EHR system)
  - **CDWWork2**: Simulates Cerner/Oracle Health-based CDW data (community care/DoD integration)
- **Data Type:** Mock synthetic data only (safe for version control and public repositories)
- **Access Pattern:** Read-only for ETL processes; populated via SQL INSERT scripts
- **Identity Model:** SID-based surrogate keys with ICN for cross-database patient identity

**Role in med-z1 Architecture:**
```
SQL Server (CDW Mock)
  ├─ CDWWork (VistA)      ──┐
  └─ CDWWork2 (Cerner)    ──┼─→ ETL Bronze Layer ──→ Silver Layer ──→ Gold Layer ──→ PostgreSQL (medz1)
                            │   (Parquet/MinIO)      (Harmonized)     (Query-ready)   (Serving DB)
```

---

## Database Organization

### CDWWork (VistA-based)

**Total Tables:** ~51 tables across 10 schemas

| Schema | Purpose | Tables | Key Tables |
|--------|---------|--------|------------|
| `Dim` | Dimensions and reference data | ~15 | Location, Sta3n, PatientRecordFlag, TIUDocumentDefinition, VitalType, Allergen, LocalDrug, NationalDrug, LabTest, Vaccine |
| `SPatient` | Patient demographics and administrative | 6 | SPatient, SPatientAddress, SPatientInsurance, SPatientDisability, PatientRecordFlagAssignment, PatientRecordFlagHistory |
| `SStaff` | Staff and providers | 2 | SStaff, RadiologyNuclearMedicineReport |
| `Vital` | Vital signs | 2 | VitalSign, VitalSignQualifier |
| `Allergy` | Patient allergies | 2 | PatientAllergy, PatientAllergyReaction |
| `RxOut` | Outpatient pharmacy | 4 | RxOutpat, RxOutpatFill, RxOutpatSig, RxOutpatMedInstructions |
| `BCMA` | Medication administration | 4 | BCMAMedicationLog, BCMADispensedDrug, BCMAAdditive, BCMASolution |
| `Inpat` | Inpatient encounters | 3 | Inpatient, PatientTransfer, ProvisionalMovement |
| `Chem` | Laboratory results | 1 | LabChem |
| `TIU` | Clinical notes | 2 | TIUDocument_8925, TIUDocumentText |
| `Immunization` | Immunizations | 1 | PatientImmunization |

### CDWWork2 (Cerner/Oracle Health-based)

**Total Tables:** ~10 tables across 5 schemas

| Schema | Purpose | Tables | Key Tables |
|--------|---------|--------|------------|
| `VeteranMill` | Veteran/patient demographics | 1 | SPerson |
| `VitalMill` | Vital signs | 1 | VitalResult |
| `ImmunizationMill` | Immunizations | 2 | VaccineAdmin, VaccineCode |
| `AllergyMill` | Allergies | 2 | PersonAllergy, AdverseReaction |
| `EncMill` | Encounters | 1 | Encounter |
| `NDimMill` | Normalized dimensions | 1 | CodeValue |

**Naming Convention Note:** CDWWork2 uses "Mill" suffix (e.g., VeteranMill, VitalMill) and different terminology (Person vs Patient, VitalResult vs VitalSign) to simulate Cerner's distinct data model.

---

## Identity and Key Patterns

**Critical Concept:** SQL Server CDW databases use **surrogate keys (SIDs)** for internal relationships, while the med-z1 PostgreSQL serving database uses **ICN (Integrated Care Number)** as the primary patient identifier.

### SID-Based Identity (CDW Pattern)

| Key Type | Example | Purpose | Scope |
|----------|---------|---------|-------|
| **PatientSID** | `123456789` | Surrogate key for patient records in CDWWork | Unique per row in SPatient.SPatient |
| **PersonSID** | `987654321` | Surrogate key for patient records in CDWWork2 | Unique per row in VeteranMill.SPerson |
| **VitalSignSID** | `555123456` | Surrogate key for vital sign records | Unique per vital measurement |
| **RxOutpatSID** | `444789012` | Surrogate key for outpatient prescriptions | Unique per prescription |
| **InpatientSID** | `333456789` | Surrogate key for inpatient encounters | Unique per admission |

**Important:** SID values are **auto-incrementing IDENTITY columns** and may differ across databases even for the same logical entity. Do not use SIDs for cross-database joins.

### ICN-Based Identity (Cross-Database Pattern)

| Key Type | Example | Purpose | Scope |
|----------|---------|---------|-------|
| **PatientICN** | `ICN100001` | Integrated Care Number (business key) | **Unique across both CDWWork and CDWWork2** |

**ICN as the Universal Patient Identifier:**
- **CDWWork:** `SPatient.SPatient.PatientICN` (VARCHAR(50))
- **CDWWork2:** `VeteranMill.SPerson.PatientICN` (VARCHAR(50))
- **PostgreSQL:** `clinical.patient_demographics.patient_key` (TEXT)

**ETL Pattern:**
1. **Bronze Layer:** Extracts data with SIDs from CDWWork/CDWWork2
2. **Silver Layer:** Resolves PatientSID/PersonSID → PatientICN via lookup tables
3. **Gold Layer:** Uses PatientICN as primary patient identifier
4. **PostgreSQL Load:** Renames PatientICN → patient_key

### Sta3n (Facility Identifier)

| Field | Type | Purpose | Example Values |
|-------|------|---------|----------------|
| **Sta3n** | SMALLINT | VA station/facility code | `508` (Atlanta), `200` (Alexandria), `630` (Palo Alto) |

**Used for:**
- Multi-facility patient data (same patient, different sites)
- Location-based filtering in ETL
- Facility name lookup via `Dim.Sta3n` table

---

## CDWWork Database (VistA)

### Schema: Dim (Dimensions)

**Purpose:** Reference data and lookup tables for all clinical domains.

**Key Dimension Tables:**

| Table Name | Purpose | Row Count (Typical) | Key Columns |
|------------|---------|---------------------|-------------|
| `Dim.Location` | Hospital locations (clinics, wards) | 20-50 | LocationSID, LocationName, LocationType |
| `Dim.Sta3n` | VA facility/station codes | 10-20 | Sta3n, Sta3nName, Active |
| `Dim.State` | US states | 50 | StateSID, StateAbbr, StateName |
| `Dim.PatientRecordFlag` | Flag definitions (safety alerts) | 10-20 | PatientRecordFlagSID, FlagName, FlagCategory |
| `Dim.TIUDocumentDefinition` | Clinical note types | 10-15 | TIUDocumentDefinitionSID, Title, DocumentClass |
| `Dim.VitalType` | Vital sign types (BP, pulse, temp) | 10-15 | VitalTypeSID, VitalType, VitalAbbreviation |
| `Dim.Allergen` | Standardized allergen names | 20-50 | AllergenSID, AllergenName, AllergenType |
| `Dim.AllergySeverity` | Allergy severity levels | 3-5 | AllergySeveritySID, Severity, SeverityRank |
| `Dim.LocalDrug` | Local drug formulary | 50-100 | LocalDrugSID, DrugNameWithDose, DrugClass |
| `Dim.NationalDrug` | National drug formulary | 50-100 | NationalDrugSID, NationalDrugName, GenericName |
| `Dim.LabTest` | Laboratory test definitions | 20-50 | LabTestSID, LabTestName, LabTestCode, LOINCCode |
| `Dim.Vaccine` | Vaccine definitions (CVX codes) | 30-50 | VaccineSID, VaccineCVXCode, VaccineName |

**Dimension Table Pattern:**
- Surrogate key: `*SID` (INT or BIGINT, IDENTITY)
- Active flag: `Active` (CHAR(1), 'Y'/'N') or `IsActive` (BIT)
- Descriptive fields: Names, codes, categories
- Minimal change over time (static reference data)

---

### Schema: SPatient (Patient Demographics)

#### Table: `SPatient.SPatient`

**Purpose:** Patient demographic and administrative data (core patient record).

**Primary Key:** `PatientSID` (INT, IDENTITY)

**VistA Alignment:** File #2 (PATIENT)

##### Columns (Selected Key Fields)

**Note:** This table has 139 columns in CDW. Only key fields used by ETL are documented here.

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientSID` | INT | NOT NULL | **Surrogate key (primary key)** | `123456789` |
| `PatientIEN` | VARCHAR(50) | NOT NULL | VistA Internal Entry Number | `1001` |
| `Sta3n` | SMALLINT | NOT NULL | Home VA station | `508`, `200` |
| `PatientICN` | VARCHAR(50) | NULL | **Integrated Care Number (business key)** | `ICN100001` |
| `PatientName` | VARCHAR(30) | NULL | Full name (LAST,FIRST) | `DOOREE,ADAM` |
| `PatientLastName` | VARCHAR(30) | NULL | Last name | `DOOREE` |
| `PatientFirstName` | VARCHAR(30) | NULL | First name | `ADAM` |
| `ScrSSN` | VARCHAR(20) | NULL | Scrambled SSN (masked) | `XXX-XX-6789` |
| `PatientSSN` | VARCHAR(20) | NULL | Full SSN (encrypted in production) | `123-45-6789` |
| `BirthDateTime` | DATETIME | NULL | Date of birth | `1956-03-15 00:00:00` |
| `Age` | NUMERIC(9) | NULL | Current age | `68` |
| `Gender` | CHAR(1) | NULL | Biological sex | `M`, `F` |
| `SelfIdentifiedGender` | VARCHAR(20) | NULL | Gender identity | `Male`, `Female`, `Non-binary` |
| `MaritalStatus` | VARCHAR(25) | NULL | Marital status | `Married`, `Single`, `Divorced` |
| `Religion` | VARCHAR(20) | NULL | Religion | `Catholic`, `Baptist` |
| `DeceasedFlag` | CHAR(1) | NULL | Deceased indicator | `Y`, `N` |
| `DeathDateTime` | DATETIME | NULL | Date of death | `2023-05-20 00:00:00` |
| `ServiceConnectedFlag` | CHAR(1) | NULL | Service-connected disability indicator | `Y`, `N` |
| `VeteranFlag` | CHAR(1) | NULL | Veteran status | `Y`, `N` |
| `TestPatientFlag` | CHAR(1) | NULL | Test patient indicator | `Y`, `N` |
| `SensitiveFlag` | CHAR(1) | NULL | Sensitive record flag | `Y`, `N` |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_SPatient` | `PatientSID` | Primary Key | Auto-created |
| `IX_SPatient_ICN` | `PatientICN` | B-tree | Critical for ETL joins |
| `IX_SPatient_SSN` | `PatientSSN` | B-tree | Patient lookups |
| `IX_SPatient_Sta3n` | `Sta3n` | B-tree | Facility filtering |

---

#### Table: `SPatient.SPatientAddress`

**Purpose:** Patient address history (one-to-many relationship with SPatient).

**Primary Key:** `PatientAddressSID` (BIGINT, IDENTITY)

##### Columns (Key Fields)

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientAddressSID` | BIGINT | NOT NULL | Surrogate key | `987654321` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `AddressType` | VARCHAR(30) | NULL | Address type | `PERMANENT`, `TEMPORARY`, `CONFIDENTIAL` |
| `StreetLine1` | VARCHAR(50) | NULL | Street address line 1 | `123 Main St` |
| `StreetLine2` | VARCHAR(50) | NULL | Street address line 2 | `Apt 4B` |
| `City` | VARCHAR(30) | NULL | City | `Atlanta` |
| `StateSID` | INT | NULL | FK to Dim.State | `13` (Georgia) |
| `State` | VARCHAR(30) | NULL | State name | `GEORGIA` |
| `ZipCode` | VARCHAR(15) | NULL | ZIP code | `30303`, `30303-1234` |
| `Country` | VARCHAR(30) | NULL | Country | `USA` |
| `IsPrimaryAddress` | CHAR(1) | NULL | Primary address flag | `Y`, `N` |

---

#### Table: `SPatient.PatientRecordFlagAssignment`

**Purpose:** Patient safety flags (behavioral flags, clinical alerts) - current assignments.

**Primary Key:** `PatientRecordFlagAssignmentSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #26.13 (PATIENT RECORD FLAG)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientRecordFlagAssignmentSID` | BIGINT | NOT NULL | Surrogate key | `789456123` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `PatientRecordFlagSID` | INT | NOT NULL | FK to Dim.PatientRecordFlag | `5` |
| `AssignmentStatus` | VARCHAR(20) | NOT NULL | Current status | `ACTIVE`, `INACTIVE` |
| `AssignmentDateTime` | DATETIME2(3) | NOT NULL | Date flag was assigned | `2024-01-15 09:00:00` |
| `InactivationDateTime` | DATETIME2(3) | NULL | Date flag was inactivated | `2024-06-20 14:30:00` |
| `OwnerSiteSta3n` | SMALLINT | NULL | Owning facility | `508` |
| `ReviewFrequencyDays` | INT | NULL | Required review frequency | `90`, `180`, `365` |
| `NextReviewDate` | DATETIME2(3) | NULL | Next required review date | `2025-03-15 00:00:00` |
| `LastActionDateTime` | DATETIME2(3) | NULL | Date of last action | `2024-12-10 11:15:00` |
| `LastActionType` | VARCHAR(50) | NULL | Last action taken | `ASSIGNMENT`, `REVIEW`, `INACTIVATE` |
| `Sta3n` | SMALLINT | NULL | Home station | `508` |

---

#### Table: `SPatient.PatientRecordFlagHistory`

**Purpose:** Audit trail for patient flag actions with sensitive narrative text.

**Primary Key:** `PatientRecordFlagHistorySID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientRecordFlagHistorySID` | BIGINT | NOT NULL | Surrogate key | `555123789` |
| `PatientRecordFlagAssignmentSID` | BIGINT | NOT NULL | FK to PatientRecordFlagAssignment | `789456123` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `HistoryDateTime` | DATETIME2(3) | NOT NULL | Date of historical action | `2024-01-15 09:00:00` |
| `ActionCode` | SMALLINT | NOT NULL | Action code (1-5) | `1` (ASSIGNMENT), `3` (INACTIVATE) |
| `ActionName` | VARCHAR(50) | NOT NULL | Action name | `ASSIGNMENT`, `REVIEW`, `INACTIVATE` |
| `EnteredByDUZ` | INT | NOT NULL | Staff DUZ (VistA user ID) | `10958` |
| `ApprovedByDUZ` | INT | NOT NULL | Approver DUZ | `10958` |
| `TIUDocumentIEN` | INT | NULL | TIU document IEN (note reference) | `123456` |
| `Comments` | NVARCHAR(MAX) | NULL | **SENSITIVE** - Narrative comments | `"Patient exhibits high-risk behavior..."` |

**⚠️ Security Note:** The `Comments` column contains **sensitive clinical narrative text** and must be protected with appropriate access controls.

---

### Schema: SStaff (Staff/Providers)

#### Table: `SStaff.SStaff`

**Purpose:** Healthcare provider and staff information.

**Primary Key:** `StaffSID` (BIGINT, IDENTITY)

##### Columns (Key Fields)

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `StaffSID` | BIGINT | NOT NULL | Surrogate key | `10958` |
| `StaffIEN` | VARCHAR(50) | NULL | VistA Staff IEN | `10958` |
| `StaffName` | VARCHAR(100) | NULL | Full name | `DOCTOR, JANE` |
| `StaffTitle` | VARCHAR(50) | NULL | Professional title | `MD`, `RN`, `PA` |
| `Sta3n` | SMALLINT | NULL | Home station | `508` |

---

### Schema: Vital

#### Table: `Vital.VitalSign`

**Purpose:** Patient vital signs measurements.

**Primary Key:** `VitalSignSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #120.5 (GMRV VITAL MEASUREMENT)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `VitalSignSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `555123456` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `VitalTypeSID` | INT | NOT NULL | FK to Dim.VitalType | `3` (Blood Pressure) |
| `VitalSignTakenDateTime` | DATETIME2(3) | NOT NULL | When vital was taken | `2025-12-10 08:30:00` |
| `VitalSignEnteredDateTime` | DATETIME2(3) | NULL | When entered into VistA | `2025-12-10 08:35:00` |
| `ResultValue` | VARCHAR(50) | NULL | Display value | `"120/80"`, `"98.6"`, `"180"` |
| `NumericValue` | DECIMAL(10,2) | NULL | Numeric value for single-value vitals | `98.6`, `180` |
| `Systolic` | INT | NULL | BP systolic (BP only) | `120` |
| `Diastolic` | INT | NULL | BP diastolic (BP only) | `80` |
| `MetricValue` | DECIMAL(10,2) | NULL | Converted metric value | `37.0` (temp in C), `81.6` (weight in kg) |
| `LocationSID` | INT | NULL | FK to Dim.Location | `456` |
| `EnteredByStaffSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `IsInvalid` | CHAR(1) | NULL | Soft delete flag | `Y`, `N` |
| `EnteredInError` | CHAR(1) | NULL | Entered in error flag | `Y`, `N` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |
| `CreatedDateTimeUTC` | DATETIME2(3) | NULL | Record created timestamp | `2025-12-10 08:35:00` |
| `UpdatedDateTimeUTC` | DATETIME2(3) | NULL | Record updated timestamp | `2025-12-10 09:00:00` |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_VitalSign` | `VitalSignSID` | Primary Key | Auto-created |
| `IX_VitalSign_Patient_Date` | `PatientSID`, `VitalSignTakenDateTime DESC` | B-tree | Primary ETL query pattern |
| `IX_VitalSign_Type_Date` | `VitalTypeSID`, `VitalSignTakenDateTime DESC` | B-tree | Type filtering |
| `IX_VitalSign_Patient_Type_Recent` | `PatientSID`, `VitalTypeSID`, `VitalSignTakenDateTime DESC` | Filtered | WHERE IsInvalid = 'N' |

**⚠️ QUOTED_IDENTIFIER Note:** Filtered indexes require `SET QUOTED_IDENTIFIER ON;` before creation.

---

#### Table: `Vital.VitalSignQualifier`

**Purpose:** Qualifiers for vital signs (position, site, method) - one-to-many relationship with VitalSign.

**Primary Key:** `VitalSignQualifierSID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `VitalSignQualifierSID` | BIGINT | NOT NULL | Surrogate key | `777888999` |
| `VitalSignSID` | BIGINT | NOT NULL | FK to Vital.VitalSign | `555123456` |
| `VitalQualifierSID` | INT | NOT NULL | FK to Dim.VitalQualifier | `10` |
| `QualifierText` | VARCHAR(100) | NULL | Qualifier description | `"Sitting"`, `"Right Arm"`, `"Oral"` |

---

### Schema: Allergy

#### Table: `Allergy.PatientAllergy`

**Purpose:** Patient allergy records.

**Primary Key:** `PatientAllergySID` (BIGINT, IDENTITY)

**VistA Alignment:** File #120.8 (PATIENT ALLERGIES)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientAllergySID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `456789123` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `AllergenSID` | INT | NOT NULL | FK to Dim.Allergen (standardized) | `25` |
| `AllergySeveritySID` | INT | NULL | FK to Dim.AllergySeverity | `3` (SEVERE) |
| `LocalAllergenName` | VARCHAR(255) | NOT NULL | What clinician typed | `"PENICILLIN VK 500MG"`, `"SHELLFISH"` |
| `OriginationDateTime` | DATETIME2(3) | NOT NULL | When allergy was recorded | `2020-05-10 10:30:00` |
| `ObservedDateTime` | DATETIME2(3) | NULL | When reaction was observed | `2020-05-10 10:30:00` |
| `OriginatingStaffSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `OriginatingSiteSta3n` | SMALLINT | NULL | Facility where entered | `508` |
| `Comment` | NVARCHAR(MAX) | NULL | **SENSITIVE** - Free-text narrative | `"Patient reports anaphylaxis in 2019..."` |
| `HistoricalOrObserved` | VARCHAR(20) | NULL | Allergy type | `HISTORICAL`, `OBSERVED` |
| `IsActive` | BIT | NULL | Active allergy | `1` (true), `0` (false) |
| `VerificationStatus` | VARCHAR(30) | NULL | Verification status | `VERIFIED`, `UNVERIFIED` |
| `Sta3n` | SMALLINT | NULL | Home station | `508` |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_PatientAllergy` | `PatientAllergySID` | Primary Key | Auto-created |
| `IX_PatientAllergy_Patient` | `PatientSID`, `IsActive`, `OriginationDateTime DESC` | B-tree | Primary ETL query pattern |
| `IX_PatientAllergy_Allergen` | `AllergenSID` | B-tree | Allergen filtering |

---

#### Table: `Allergy.PatientAllergyReaction`

**Purpose:** Specific reactions for each allergy (one-to-many relationship with PatientAllergy).

**Primary Key:** `PatientAllergyReactionSID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientAllergyReactionSID` | BIGINT | NOT NULL | Surrogate key | `888999000` |
| `PatientAllergySID` | BIGINT | NOT NULL | FK to Allergy.PatientAllergy | `456789123` |
| `ReactionSID` | INT | NOT NULL | FK to Dim.Reaction | `15` |
| `ReactionText` | VARCHAR(100) | NULL | Reaction name | `"Hives"`, `"Itching"`, `"Anaphylaxis"` |

---

### Schema: RxOut (Outpatient Pharmacy)

#### Table: `RxOut.RxOutpat`

**Purpose:** Outpatient prescriptions (pharmacy orders).

**Primary Key:** `RxOutpatSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #52 (PRESCRIPTION)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `RxOutpatSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `444789012` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `LocalDrugSID` | BIGINT | NULL | FK to Dim.LocalDrug | `10001` |
| `NationalDrugSID` | BIGINT | NULL | FK to Dim.NationalDrug | `50001` |
| `PrescriptionNumber` | VARCHAR(50) | NULL | Prescription number | `"RX-2024-001234"` |
| `IssueDateTime` | DATETIME2(3) | NULL | Date prescription was issued | `2024-11-15 10:30:00` |
| `RxStatus` | VARCHAR(30) | NULL | Prescription status | `ACTIVE`, `EXPIRED`, `DISCONTINUED` |
| `RxType` | VARCHAR(30) | NULL | Prescription type | `PRESCRIPTION`, `REFILL` |
| `QuantityOrdered` | DECIMAL(12,4) | NULL | Quantity ordered | `90.0000`, `30.0000` |
| `DaysSupply` | INT | NULL | Days supply | `90`, `30` |
| `RefillsAllowed` | INT | NULL | Total refills allowed | `5`, `3` |
| `RefillsRemaining` | INT | NULL | Refills remaining | `3`, `0` |
| `SigText` | NVARCHAR(MAX) | NULL | Complete signature/directions | `"TAKE ONE TABLET BY MOUTH TWICE DAILY WITH MEALS"` |
| `ExpirationDateTime` | DATETIME2(3) | NULL | Prescription expiration date | `2025-11-15 00:00:00` |
| `DiscontinuedDateTime` | DATETIME2(3) | NULL | Date prescription was discontinued | `2025-03-20 09:00:00` |
| `DiscontinueReason` | VARCHAR(100) | NULL | Reason for discontinuation | `"NO LONGER CLINICALLY INDICATED"` |
| `ProviderSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_RxOutpat` | `RxOutpatSID` | Primary Key | Auto-created |
| `IX_RxOutpat_Patient_Date` | `PatientSID`, `IssueDateTime DESC` | B-tree | Primary ETL query pattern |
| `IX_RxOutpat_Status` | `RxStatus`, `IssueDateTime DESC` | B-tree | Status filtering |

---

#### Table: `RxOut.RxOutpatFill`

**Purpose:** Prescription fill history (one-to-many relationship with RxOutpat).

**Primary Key:** `RxOutpatFillSID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `RxOutpatFillSID` | BIGINT | NOT NULL | Surrogate key | `555666777` |
| `RxOutpatSID` | BIGINT | NOT NULL | FK to RxOut.RxOutpat | `444789012` |
| `FillNumber` | INT | NULL | Fill number | `0` (original), `1`, `2`, `3` |
| `FillDateTime` | DATETIME2(3) | NULL | Date filled | `2025-01-15 14:00:00` |
| `FillStatus` | VARCHAR(30) | NULL | Fill status | `FILLED`, `PARTIALLY FILLED` |
| `QuantityDispensed` | DECIMAL(12,4) | NULL | Quantity dispensed | `90.0000` |
| `DaysSupplyDispensed` | INT | NULL | Days supply dispensed | `90` |

---

### Schema: BCMA (Medication Administration)

#### Table: `BCMA.BCMAMedicationLog`

**Purpose:** Inpatient medication administration records (bar code medication administration).

**Primary Key:** `BCMAMedicationLogSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #53.79 (BCMA MEDICATION LOG)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `BCMAMedicationLogSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `987654321` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `InpatientSID` | BIGINT | NULL | FK to Inpat.Inpatient | `555123` |
| `LocalDrugSID` | BIGINT | NULL | FK to Dim.LocalDrug | `10001` |
| `NationalDrugSID` | BIGINT | NULL | FK to Dim.NationalDrug | `50001` |
| `ActionType` | VARCHAR(30) | NULL | Administration action | `GIVEN`, `HELD`, `REFUSED`, `MISSING DOSE` |
| `ActionStatus` | VARCHAR(30) | NULL | Action status | `COMPLETED`, `INCOMPLETE` |
| `ActionDateTime` | DATETIME2(3) | NULL | When action occurred | `2025-01-10 08:00:00` |
| `ScheduledDateTime` | DATETIME2(3) | NULL | When scheduled | `2025-01-10 08:00:00` |
| `OrderedDateTime` | DATETIME2(3) | NULL | When ordered | `2025-01-09 18:00:00` |
| `DosageOrdered` | VARCHAR(100) | NULL | Dosage ordered | `"10 UNITS"` |
| `DosageGiven` | VARCHAR(100) | NULL | Dosage given | `"10 UNITS"` |
| `Route` | VARCHAR(50) | NULL | Administration route | `PO`, `IV`, `IM`, `SC` |
| `ScheduleType` | VARCHAR(30) | NULL | Schedule type | `SCHEDULED`, `PRN` |
| `AdministeredByStaffSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

---

### Schema: Inpat (Inpatient Encounters)

#### Table: `Inpat.Inpatient`

**Purpose:** Inpatient admissions and stays.

**Primary Key:** `InpatientSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #405 (PATIENT MOVEMENT)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `InpatientSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `555123456` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `AdmitDateTime` | DATETIME2(3) | NOT NULL | Admission date/time | `2024-12-01 14:30:00` |
| `DischargeDateTime` | DATETIME2(3) | NULL | Discharge date/time (NULL if active) | `2024-12-05 10:00:00`, `NULL` |
| `AdmitLocationSID` | INT | NULL | FK to Dim.Location (admission ward) | `123` |
| `DischargeLocationSID` | INT | NULL | FK to Dim.Location (discharge ward) | `456` |
| `AdmitDiagnosisICD10Code` | VARCHAR(20) | NULL | ICD-10 admission diagnosis | `I21.9`, `J44.1` |
| `DischargeDiagnosisICD10Code` | VARCHAR(20) | NULL | ICD-10 discharge diagnosis | `I21.9` |
| `DischargeDisposition` | VARCHAR(50) | NULL | Discharge disposition | `Home`, `SNF`, `Rehab`, `AMA`, `Deceased` |
| `LengthOfStay` | INT | NULL | LOS in days | `4`, `7`, `15` |
| `AttendingPhysicianStaffSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

---

### Schema: Chem (Laboratory)

#### Table: `Chem.LabChem`

**Purpose:** Laboratory chemistry test results.

**Primary Key:** `LabChemSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #63 (LABORATORY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `LabChemSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `123456789` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `LabTestSID` | INT | NOT NULL | FK to Dim.LabTest | `1001` |
| `AccessionNumber` | VARCHAR(50) | NOT NULL | Accession number | `"CH 20251211-001"` |
| `ResultValue` | VARCHAR(100) | NULL | Display result value | `"142"`, `"Positive"`, `"6.5"` |
| `ResultNumeric` | DECIMAL(18,6) | NULL | Numeric result for trending | `142.000000`, `6.500000` |
| `ResultUnit` | VARCHAR(50) | NULL | Result unit | `mmol/L`, `mg/dL`, `%` |
| `AbnormalFlag` | VARCHAR(10) | NULL | Abnormal flag | `H`, `L`, `H*`, `L*`, `PANIC` |
| `ReferenceRange` | VARCHAR(100) | NULL | Reference range text | `"135 - 145"`, `"Negative"`, `"<5.7"` |
| `CollectionDateTime` | DATETIME2(3) | NOT NULL | When specimen was collected | `2025-12-11 08:00:00` |
| `ResultDateTime` | DATETIME2(3) | NOT NULL | When result became available | `2025-12-11 10:30:00` |
| `LocationSID` | INT | NULL | FK to Dim.Location | `789` |
| `SpecimenType` | VARCHAR(50) | NULL | Specimen type | `Serum`, `Whole Blood`, `Plasma` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

---

### Schema: TIU (Clinical Notes)

#### Table: `TIU.TIUDocument_8925`

**Purpose:** Clinical note metadata (corresponds to VistA File #8925).

**Primary Key:** `TIUDocumentSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #8925 (TIU DOCUMENT)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `TIUDocumentSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `987654321` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `TIUDocumentDefinitionSID` | INT | NOT NULL | FK to Dim.TIUDocumentDefinition | `3` |
| `TIUDocumentIEN` | VARCHAR(50) | NULL | VistA Document IEN | `12345` |
| `Status` | VARCHAR(50) | NOT NULL | Document status | `COMPLETED`, `UNSIGNED`, `AMENDED` |
| `ReferenceDateTime` | DATETIME2(3) | NOT NULL | Clinical date of note (primary sort key) | `2025-11-20 10:00:00` |
| `EntryDateTime` | DATETIME2(3) | NOT NULL | Date note was authored/entered | `2025-11-20 10:30:00` |
| `AuthorStaffSID` | BIGINT | NULL | FK to SStaff.SStaff | `10958` |
| `CosignerStaffSID` | BIGINT | NULL | FK to SStaff.SStaff (if applicable) | `10959` |
| `VisitSID` | BIGINT | NULL | Associated visit/encounter | `555123` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

---

#### Table: `TIU.TIUDocumentText`

**Purpose:** Full narrative text of clinical notes (one-to-one relationship with TIUDocument_8925).

**Primary Key:** `TIUDocumentTextSID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `TIUDocumentTextSID` | BIGINT | NOT NULL | Surrogate key | `888999111` |
| `TIUDocumentSID` | BIGINT | NOT NULL | FK to TIU.TIUDocument_8925 | `987654321` |
| `DocumentText` | NVARCHAR(MAX) | NULL | **SENSITIVE** - Full narrative text (SOAP format) | `"SUBJECTIVE: Patient reports..."` |
| `TextLength` | INT | NULL | Character count | `1250`, `3500` |

**⚠️ Security Note:** The `DocumentText` column contains **sensitive clinical narrative text** and must be protected with appropriate access controls.

---

### Schema: Immunization

#### Table: `Immunization.PatientImmunization`

**Purpose:** Patient immunization records.

**Primary Key:** `PatientImmunizationSID` (BIGINT, IDENTITY)

**VistA Alignment:** File #9000010.11 (V IMMUNIZATION)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PatientImmunizationSID` | BIGINT | NOT NULL | **Surrogate key (primary key)** | `123456789` |
| `PatientSID` | BIGINT | NOT NULL | FK to SPatient.SPatient | `123456789` |
| `VaccineSID` | INT | NULL | FK to Dim.Vaccine | `15` |
| `VaccineCVXCode` | VARCHAR(10) | NULL | CDC CVX code | `"208"` (COVID-19 Pfizer), `"141"` (Flu) |
| `VaccineName` | VARCHAR(255) | NULL | Vaccine name (UPPERCASE) | `"COVID-19, MRNA, LNP-S, PF, 30 MCG/0.3 ML DOSE"` |
| `AdministeredDateTime` | DATETIME2(3) | NOT NULL | When vaccine was administered | `2024-09-15 10:00:00` |
| `Series` | VARCHAR(50) | NULL | Series tracking | `"1 of 2"`, `"BOOSTER"`, `"ANNUAL 2024"` |
| `Dose` | VARCHAR(50) | NULL | Dose amount | `"0.5 ML"`, `"0.3 ML"` |
| `Route` | VARCHAR(50) | NULL | Administration route | `IM`, `SC`, `PO`, `Intranasal` |
| `SiteOfAdministration` | VARCHAR(100) | NULL | Anatomical site | `Left Deltoid`, `Right Thigh` |
| `AdverseReaction` | VARCHAR(255) | NULL | Adverse reaction description | `"Soreness at injection site"`, `"Fever, chills"` |
| `ProviderStaffSID` | INT | NULL | FK to SStaff.SStaff | `10958` |
| `LocationSID` | INT | NULL | FK to Dim.Location | `456` |
| `Sta3n` | SMALLINT | NULL | Facility | `508` |

---

## CDWWork2 Database (Cerner/Oracle Health)

**Purpose:** Simulates Cerner/Oracle Health-based data from community care sites and DoD integration points. This database uses different naming conventions and schemas to represent the distinct data model of non-VistA EHR systems.

**Key Differences from CDWWork:**
- **Terminology:** "Person" instead of "Patient", "VitalResult" instead of "VitalSign"
- **Schema Naming:** "Mill" suffix (VeteranMill, VitalMill, ImmunizationMill, AllergyMill, EncMill)
- **Encounter-Centric:** Cerner data is often encounter-linked vs VistA patient-linked
- **Denormalization:** More denormalized fields (e.g., PatientICN duplicated in many tables)

---

### Schema: VeteranMill

#### Table: `VeteranMill.SPerson`

**Purpose:** Veteran/patient demographics (equivalent to CDWWork's SPatient.SPatient).

**Primary Key:** `PersonSID` (BIGINT, IDENTITY)

**Harmonizes With:** `CDWWork.SPatient.SPatient`

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PersonSID` | BIGINT | NOT NULL | **Surrogate key (Cerner-specific)** | `987654321` |
| `PatientICN` | VARCHAR(50) | NOT NULL | **Shared ICN (cross-database identity)** | `ICN100001` |
| `LastName` | VARCHAR(100) | NOT NULL | Last name | `DOOREE` |
| `FirstName` | VARCHAR(100) | NOT NULL | First name | `ADAM` |
| `MiddleName` | VARCHAR(100) | NULL | Middle name | `M` |
| `BirthDate` | DATE | NOT NULL | Date of birth | `1956-03-15` |
| `Gender` | CHAR(1) | NOT NULL | Biological sex | `M`, `F` |
| `SSN` | VARCHAR(11) | NULL | SSN (format: XXX-XX-XXXX) | `123-45-6789` |
| `StreetAddress` | VARCHAR(200) | NULL | Street address | `123 Main St` |
| `City` | VARCHAR(100) | NULL | City | `Atlanta` |
| `State` | CHAR(2) | NULL | State abbreviation | `GA` |
| `ZipCode` | VARCHAR(10) | NULL | ZIP code | `30303` |
| `IsActive` | BIT | NOT NULL | Active record | `1` (true), `0` (false) |
| `CreatedDate` | DATETIME | NOT NULL | Record created | `2024-01-01 00:00:00` |
| `LastUpdatedDate` | DATETIME | NOT NULL | Record updated | `2025-12-30 15:00:00` |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_SPerson` | `PersonSID` | Primary Key | Auto-created |
| `UQ_SPerson_ICN` | `PatientICN` | Unique | **Critical for cross-database joins** |
| `IX_SPerson_ICN` | `PatientICN` | B-tree | ETL performance |
| `IX_SPerson_Name` | `LastName`, `FirstName` | B-tree | Name searches |

---

### Schema: VitalMill

#### Table: `VitalMill.VitalResult`

**Purpose:** Vital signs results (equivalent to CDWWork's Vital.VitalSign).

**Primary Key:** `VitalResultSID` (BIGINT, IDENTITY)

**Harmonizes With:** `CDWWork.Vital.VitalSign`

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `VitalResultSID` | BIGINT | NOT NULL | **Surrogate key (Cerner-specific)** | `555666777` |
| `EncounterSID` | BIGINT | NOT NULL | FK to EncMill.Encounter | `111222333` |
| `PersonSID` | BIGINT | NOT NULL | FK to VeteranMill.SPerson | `987654321` |
| `PatientICN` | VARCHAR(50) | NOT NULL | **Denormalized ICN for performance** | `ICN100001` |
| `VitalTypeCodeSID` | BIGINT | NOT NULL | FK to NDimMill.CodeValue (vital type) | `5001` |
| `VitalTypeName` | VARCHAR(200) | NULL | Denormalized vital type name | `Blood Pressure`, `Pulse`, `Temperature` |
| `ResultValue` | VARCHAR(200) | NOT NULL | Text representation | `"120/80"`, `"72"`, `"98.6"` |
| `NumericValue` | DECIMAL(10,2) | NULL | Numeric value for single-value vitals | `72`, `98.6` |
| `Systolic` | INT | NULL | BP systolic | `120` |
| `Diastolic` | INT | NULL | BP diastolic | `80` |
| `UnitCodeSID` | BIGINT | NULL | FK to NDimMill.CodeValue (unit) | `6001` |
| `UnitName` | VARCHAR(50) | NULL | Denormalized unit name | `mmHg`, `bpm`, `°F` |
| `TakenDateTime` | DATETIME | NOT NULL | When vital was measured | `2025-12-30 08:00:00` |
| `EnteredDateTime` | DATETIME | NOT NULL | When recorded in system | `2025-12-30 08:05:00` |
| `LocationName` | VARCHAR(200) | NULL | Where vital was taken | `Primary Care Clinic` |
| `Sta3n` | VARCHAR(10) | NULL | Site/facility (denormalized) | `648`, `663` |
| `IsActive` | BIT | NOT NULL | Active record | `1` (true), `0` (false) |

##### Indexes

| Index Name | Columns | Type | Notes |
|------------|---------|------|-------|
| `PK_VitalResult` | `VitalResultSID` | Primary Key | Auto-created |
| `IX_VitalResult_Person` | `PersonSID`, `TakenDateTime DESC` | B-tree | Patient vital lookups |
| `IX_VitalResult_ICN` | `PatientICN`, `TakenDateTime DESC` | B-tree | **Cross-database queries** |
| `IX_VitalResult_Encounter` | `EncounterSID`, `TakenDateTime DESC` | B-tree | Encounter-based lookups (Cerner pattern) |
| `IX_VitalResult_VitalType` | `VitalTypeCodeSID`, `TakenDateTime DESC` | B-tree | Vital type filtering |

---

### Schema: ImmunizationMill

#### Table: `ImmunizationMill.VaccineAdmin`

**Purpose:** Vaccine administration records (equivalent to CDWWork's Immunization.PatientImmunization).

**Primary Key:** `VaccineAdminSID` (BIGINT, IDENTITY)

**Harmonizes With:** `CDWWork.Immunization.PatientImmunization`

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `VaccineAdminSID` | BIGINT | NOT NULL | **Surrogate key (Cerner-specific)** | `777888999` |
| `PersonSID` | BIGINT | NOT NULL | FK to VeteranMill.SPerson | `987654321` |
| `PatientICN` | VARCHAR(50) | NOT NULL | **Denormalized ICN for performance** | `ICN100001` |
| `VaccineCodeSID` | BIGINT | NOT NULL | FK to ImmunizationMill.VaccineCode | `100` |
| `VaccineCVXCode` | VARCHAR(10) | NULL | CDC CVX code | `"208"`, `"141"` |
| `VaccineName` | VARCHAR(255) | NOT NULL | Vaccine name | `COVID-19 mRNA Pfizer`, `Influenza Quadrivalent` |
| `AdministeredDateTime` | DATETIME | NOT NULL | When administered | `2024-09-15 10:00:00` |
| `DoseSequence` | VARCHAR(50) | NULL | Dose sequence | `"1 of 2"`, `"Booster"` |
| `Route` | VARCHAR(50) | NULL | Route | `IM`, `SC`, `PO` |
| `BodySite` | VARCHAR(100) | NULL | Anatomical site | `Left Deltoid`, `Right Arm` |
| `AdverseReaction` | VARCHAR(255) | NULL | Adverse reaction | `"Soreness"`, `"None"` |
| `Sta3n` | VARCHAR(10) | NULL | Site/facility | `648`, `663` |
| `IsActive` | BIT | NOT NULL | Active record | `1` (true), `0` (false) |

---

### Schema: AllergyMill

#### Table: `AllergyMill.PersonAllergy`

**Purpose:** Patient allergy records (equivalent to CDWWork's Allergy.PatientAllergy).

**Primary Key:** `PersonAllergySID` (BIGINT, IDENTITY)

**Harmonizes With:** `CDWWork.Allergy.PatientAllergy`

##### Columns (Key Fields)

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `PersonAllergySID` | BIGINT | NOT NULL | **Surrogate key (Cerner-specific)** | `444555666` |
| `PersonSID` | BIGINT | NOT NULL | FK to VeteranMill.SPerson | `987654321` |
| `PatientICN` | VARCHAR(50) | NOT NULL | **Denormalized ICN for performance** | `ICN100001` |
| `AllergenName` | VARCHAR(255) | NOT NULL | Allergen name | `Penicillin`, `Shellfish` |
| `AllergenType` | VARCHAR(50) | NULL | Allergen type | `DRUG`, `FOOD`, `ENVIRONMENTAL` |
| `Severity` | VARCHAR(50) | NULL | Severity | `MILD`, `MODERATE`, `SEVERE` |
| `RecordedDateTime` | DATETIME | NOT NULL | When recorded | `2020-05-10 10:30:00` |
| `IsActive` | BIT | NOT NULL | Active allergy | `1` (true), `0` (false) |

---

### Schema: EncMill

#### Table: `EncMill.Encounter`

**Purpose:** Patient encounters (visits, admissions) - supports vital and procedure linkage.

**Primary Key:** `EncounterSID` (BIGINT, IDENTITY)

##### Columns (Key Fields)

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `EncounterSID` | BIGINT | NOT NULL | **Surrogate key (Cerner-specific)** | `111222333` |
| `PersonSID` | BIGINT | NOT NULL | FK to VeteranMill.SPerson | `987654321` |
| `PatientICN` | VARCHAR(50) | NOT NULL | **Denormalized ICN for performance** | `ICN100001` |
| `EncounterDateTime` | DATETIME | NOT NULL | Encounter start date/time | `2025-12-30 08:00:00` |
| `EncounterType` | VARCHAR(50) | NULL | Encounter type | `OUTPATIENT`, `INPATIENT`, `EMERGENCY` |
| `LocationName` | VARCHAR(200) | NULL | Encounter location | `Primary Care Clinic`, `Emergency Department` |
| `Sta3n` | VARCHAR(10) | NULL | Site/facility | `648`, `663` |

---

### Schema: NDimMill

#### Table: `NDimMill.CodeValue`

**Purpose:** Normalized code values for Cerner's multi-purpose code system (vital types, units, etc.).

**Primary Key:** `CodeValueSID` (BIGINT, IDENTITY)

##### Columns

| Column Name | Data Type | Nullable | Description | Example Values |
|-------------|-----------|----------|-------------|----------------|
| `CodeValueSID` | BIGINT | NOT NULL | Surrogate key | `5001`, `6001` |
| `CodeSet` | VARCHAR(100) | NOT NULL | Code set name | `VITAL_TYPE`, `UNIT`, `ALLERGEN_TYPE` |
| `CodeValue` | VARCHAR(100) | NOT NULL | Code value | `BP`, `PULSE`, `TEMP`, `mmHg`, `bpm` |
| `CodeDisplay` | VARCHAR(200) | NULL | Display text | `Blood Pressure`, `Pulse`, `Temperature` |
| `IsActive` | BIT | NOT NULL | Active code | `1` (true), `0` (false) |

**Usage Pattern:** Many Cerner tables use `CodeValueSID` foreign keys instead of dedicated dimension tables (flexible but less normalized than VistA pattern).

---

## Cross-Database Harmonization

**Purpose:** The Silver layer ETL process harmonizes data from CDWWork (VistA) and CDWWork2 (Cerner) into a unified schema for Gold layer consumption.

### Harmonization Strategy

**Key Principles:**
1. **ICN as Universal Identifier:** All CDWWork2 tables include `PatientICN` (denormalized) to enable joins with CDWWork data after ICN resolution
2. **Schema Mapping:** Silver layer maps equivalent fields across different naming conventions
3. **Data Source Tracking:** `data_source` column added during Silver transformation (`"CDWWork"` or `"CDWWork2"`)
4. **Merge and Deduplicate:** Same clinical events from both sources are deduplicated (prefer CDWWork2 as most recent)
5. **Unified Output:** Single Parquet file per domain (e.g., `vitals_merged.parquet`)

### Table Equivalents

| CDWWork Table | CDWWork2 Table | Silver Output | Key Mapping Notes |
|---------------|----------------|---------------|-------------------|
| `SPatient.SPatient` | `VeteranMill.SPerson` | `patient_cleaned.parquet` | PatientSID/PersonSID → PatientICN |
| `Vital.VitalSign` | `VitalMill.VitalResult` | `vitals_merged.parquet` | VitalSignSID/VitalResultSID → unique event ID, VitalTypeSID → standardized type |
| `Immunization.PatientImmunization` | `ImmunizationMill.VaccineAdmin` | `immunizations_merged.parquet` | CVX code standardization, dose sequence parsing |
| `Allergy.PatientAllergy` | `AllergyMill.PersonAllergy` | `allergies_merged.parquet` | AllergenSID → standardized allergen name |
| `Inpat.Inpatient` | `EncMill.Encounter` | (Future) | Encounter type filtering (inpatient only) |

### Field Name Harmonization Examples

**Vitals Domain:**

| CDWWork Field | CDWWork2 Field | Silver Field | Notes |
|---------------|----------------|--------------|-------|
| `VitalSignSID` | `VitalResultSID` | `vital_sign_id` | Unique across sources (prefixed or offset) |
| `VitalSignTakenDateTime` | `TakenDateTime` | `taken_datetime` | Standardized timestamp |
| `VitalTypeSID` → Dim lookup | `VitalTypeName` (denormalized) | `vital_type` | Text type ("BLOOD PRESSURE", "PULSE") |
| `LocationSID` → Dim lookup | `LocationName` (denormalized) | `location_name` | Text location name |

**Immunizations Domain:**

| CDWWork Field | CDWWork2 Field | Silver Field | Notes |
|---------------|----------------|--------------|-------|
| `PatientImmunizationSID` | `VaccineAdminSID` | `immunization_sid` | Unique across sources |
| `VaccineCVXCode` | `VaccineCVXCode` | `cvx_code` | Direct mapping (standardized) |
| `VaccineName` | `VaccineName` | `vaccine_name` | Uppercase standardization |
| `AdministeredDateTime` | `AdministeredDateTime` | `administered_datetime` | Standardized timestamp |
| `Series` | `DoseSequence` | `series` | Parsed to `dose_number` / `total_doses` |

### ICN Resolution Process

**CDWWork Pattern (SID → ICN):**
```sql
-- ETL lookup to resolve PatientSID → PatientICN
SELECT
    PatientSID,
    PatientICN
FROM SPatient.SPatient
WHERE PatientICN IS NOT NULL
```

**CDWWork2 Pattern (ICN embedded):**
```sql
-- ICN already denormalized in most tables
SELECT
    PersonSID,
    PatientICN,  -- Already present
    ...
FROM VitalMill.VitalResult
```

**Silver Layer Join:**
```python
# Polars example from silver_vitals.py
df_cdwwork = df_cdwwork.join(
    patient_icn_df,
    left_on="PatientSID",
    right_on="PatientSID",
    how="left"
)

df_cdwwork2 = df_cdwwork2.rename({"PatientICN": "patient_icn"})

# Now both have patient_icn for merging
df_merged = pl.concat([df_cdwwork, df_cdwwork2])
```

### Deduplication Logic

**Example: Vitals Domain**

When the same vital measurement appears in both CDWWork and CDWWork2:
1. **Canonical Event Key:** `(PatientICN, VitalType, TakenDateTime)` rounded to minute
2. **Preference:** CDWWork2 (most recent/current system)
3. **Merge:** Single row with `data_source = "CDWWork2"`

**Example: Immunizations Domain**

When the same immunization appears in both sources:
1. **Canonical Event Key:** `(PatientICN, CVXCode, AdministeredDate)`
2. **Preference:** CDWWork2
3. **Audit:** Track which source contributed each field in metadata

---

## Common Query Patterns

### Pattern 1: Find Patient by ICN

**CDWWork:**
```sql
SELECT *
FROM SPatient.SPatient
WHERE PatientICN = 'ICN100001';
```

**CDWWork2:**
```sql
SELECT *
FROM VeteranMill.SPerson
WHERE PatientICN = 'ICN100001';
```

---

### Pattern 2: Get Patient Vitals with Dimension Lookups

**CDWWork (Join Pattern):**
```sql
SELECT
    v.VitalSignSID,
    v.PatientSID,
    p.PatientICN,
    vt.VitalType,
    vt.VitalAbbreviation,
    v.VitalSignTakenDateTime,
    v.ResultValue,
    v.NumericValue,
    v.Systolic,
    v.Diastolic,
    l.LocationName,
    l.LocationType,
    s.Sta3nName
FROM Vital.VitalSign v
INNER JOIN SPatient.SPatient p ON v.PatientSID = p.PatientSID
INNER JOIN Dim.VitalType vt ON v.VitalTypeSID = vt.VitalTypeSID
LEFT JOIN Dim.Location l ON v.LocationSID = l.LocationSID
LEFT JOIN Dim.Sta3n s ON v.Sta3n = s.Sta3n
WHERE p.PatientICN = 'ICN100001'
  AND v.IsInvalid = 'N'
ORDER BY v.VitalSignTakenDateTime DESC;
```

**CDWWork2 (Denormalized Pattern):**
```sql
SELECT
    VitalResultSID,
    PersonSID,
    PatientICN,           -- Already denormalized
    VitalTypeName,        -- Already denormalized
    TakenDateTime,
    ResultValue,
    NumericValue,
    Systolic,
    Diastolic,
    LocationName,         -- Already denormalized
    Sta3n
FROM VitalMill.VitalResult
WHERE PatientICN = 'ICN100001'
  AND IsActive = 1
ORDER BY TakenDateTime DESC;
```

---

### Pattern 3: Get Active Patient Allergies with Reactions

**CDWWork:**
```sql
SELECT
    pa.PatientAllergySID,
    p.PatientICN,
    a.AllergenName AS AllergenStandardized,
    pa.LocalAllergenName,
    s.Severity,
    s.SeverityRank,
    pa.OriginationDateTime,
    STRING_AGG(r.ReactionText, ', ') AS Reactions
FROM Allergy.PatientAllergy pa
INNER JOIN SPatient.SPatient p ON pa.PatientSID = p.PatientSID
INNER JOIN Dim.Allergen a ON pa.AllergenSID = a.AllergenSID
LEFT JOIN Dim.AllergySeverity s ON pa.AllergySeveritySID = s.AllergySeveritySID
LEFT JOIN Allergy.PatientAllergyReaction par ON pa.PatientAllergySID = par.PatientAllergySID
LEFT JOIN Dim.Reaction r ON par.ReactionSID = r.ReactionSID
WHERE p.PatientICN = 'ICN100001'
  AND pa.IsActive = 1
GROUP BY
    pa.PatientAllergySID,
    p.PatientICN,
    a.AllergenName,
    pa.LocalAllergenName,
    s.Severity,
    s.SeverityRank,
    pa.OriginationDateTime
ORDER BY s.SeverityRank DESC, pa.OriginationDateTime DESC;
```

---

### Pattern 4: Get Patient Medications (Outpatient Active)

**CDWWork:**
```sql
SELECT
    r.RxOutpatSID,
    p.PatientICN,
    ld.DrugNameWithDose AS LocalDrugName,
    nd.GenericName,
    nd.TradeName,
    r.IssueDateTime,
    r.RxStatus,
    r.QuantityOrdered,
    r.DaysSupply,
    r.RefillsRemaining,
    r.SigText,
    r.ExpirationDateTime,
    s.StaffName AS ProviderName,
    st.Sta3nName AS FacilityName
FROM RxOut.RxOutpat r
INNER JOIN SPatient.SPatient p ON r.PatientSID = p.PatientSID
LEFT JOIN Dim.LocalDrug ld ON r.LocalDrugSID = ld.LocalDrugSID
LEFT JOIN Dim.NationalDrug nd ON r.NationalDrugSID = nd.NationalDrugSID
LEFT JOIN SStaff.SStaff s ON r.ProviderSID = s.StaffSID
LEFT JOIN Dim.Sta3n st ON r.Sta3n = st.Sta3n
WHERE p.PatientICN = 'ICN100001'
  AND r.RxStatus = 'ACTIVE'
  AND (r.ExpirationDateTime IS NULL OR r.ExpirationDateTime >= GETDATE())
ORDER BY r.IssueDateTime DESC;
```

---

### Pattern 5: Get Patient Clinical Notes with Metadata

**CDWWork:**
```sql
SELECT
    td.TIUDocumentSID,
    p.PatientICN,
    d.Title AS DocumentTitle,
    d.DocumentClass,
    td.Status,
    td.ReferenceDateTime,
    td.EntryDateTime,
    a.StaffName AS AuthorName,
    c.StaffName AS CosignerName,
    t.DocumentText,
    LEN(t.DocumentText) AS TextLength,
    st.Sta3nName AS FacilityName
FROM TIU.TIUDocument_8925 td
INNER JOIN SPatient.SPatient p ON td.PatientSID = p.PatientSID
INNER JOIN Dim.TIUDocumentDefinition d ON td.TIUDocumentDefinitionSID = d.TIUDocumentDefinitionSID
LEFT JOIN SStaff.SStaff a ON td.AuthorStaffSID = a.StaffSID
LEFT JOIN SStaff.SStaff c ON td.CosignerStaffSID = c.StaffSID
LEFT JOIN TIU.TIUDocumentText t ON td.TIUDocumentSID = t.TIUDocumentSID
LEFT JOIN Dim.Sta3n st ON td.Sta3n = st.Sta3n
WHERE p.PatientICN = 'ICN100001'
  AND td.Status = 'COMPLETED'
ORDER BY td.ReferenceDateTime DESC;
```

---

### Pattern 6: ETL Bronze Layer Extraction (Vitals Example)

**CDWWork Bronze Extraction:**
```python
# From etl/bronze_vitals.py
query = """
SELECT
    v.VitalSignSID,
    v.PatientSID,
    v.VitalTypeSID,
    v.VitalSignTakenDateTime,
    v.VitalSignEnteredDateTime,
    v.ResultValue,
    v.NumericValue,
    v.Systolic,
    v.Diastolic,
    v.MetricValue,
    v.LocationSID,
    v.EnteredByStaffSID,
    v.IsInvalid,
    v.Sta3n
FROM Vital.VitalSign v
WHERE v.IsInvalid = 'N'
ORDER BY v.VitalSignSID
"""
```

**CDWWork2 Bronze Extraction:**
```python
# From etl/bronze_cdwwork2_vitals.py
query = """
SELECT
    VitalResultSID,
    PersonSID,
    PatientICN,          -- ICN already present
    VitalTypeName,       -- Denormalized
    ResultValue,
    NumericValue,
    Systolic,
    Diastolic,
    UnitName,            -- Denormalized
    TakenDateTime,
    EnteredDateTime,
    LocationName,        -- Denormalized
    Sta3n
FROM VitalMill.VitalResult
WHERE IsActive = 1
ORDER BY VitalResultSID
"""
```

---

## Revision History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| v1.0 | 2026-01-29 | Claude Code | Initial SQL Server Mock CDW database reference documentation covering CDWWork (VistA) and CDWWork2 (Cerner/Oracle Health) with comprehensive table schemas, identity patterns, and cross-database harmonization strategy |

---

**End of Document**
