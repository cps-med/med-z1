# Problems / Diagnoses / Problem List - Design Specification

**Document Version:** v1.1
**Created:** 2026-02-07
**Last Updated:** 2026-02-07
**Status:** Phase 1-2 Complete (ETL Pipeline Operational)
**Clinical Domain:** Problem List, Diagnoses, Chronic Conditions
**Priority:** HIGH - Critical for readmission ML model and clinical decision support

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Clinical Context](#2-clinical-context)
3. [Data Sources & Architecture](#3-data-sources--architecture)
4. [Mock Data Design](#4-mock-data-design)
5. [ETL Pipeline Design](#5-etl-pipeline-design)
6. [PostgreSQL Schema](#6-postgresql-schema)
7. [VistA RPC Integration](#7-vista-rpc-integration)
8. [UI Design](#8-ui-design)
9. [API Endpoints](#9-api-endpoints)
10. [AI Integration](#10-ai-integration)
11. [Implementation Roadmap](#11-implementation-roadmap)
12. [Appendices](#12-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

The Problems/Diagnoses domain is **the most critical data element** for clinical decision support and machine learning applications in med-z1. This design implements a comprehensive problem list and diagnosis tracking system that:

- Provides clinicians with a **unified view** of patient conditions (active, inactive, resolved)
- Enables **machine learning readmission prediction** through comorbidity indices
- Supports **AI clinical insights** with disease burden assessment
- Harmonizes **VistA and Cerner** data sources for enterprise-wide visibility

### 1.2 Key Features

**Clinical Features:**
- ✅ Problem List (longitudinal tracking of chronic conditions)
- ✅ Encounter Diagnoses (episodic billing diagnoses)
- ✅ Dual Coding (SNOMED CT + ICD-10)
- ✅ Charlson Comorbidity Index (automated scoring)
- ✅ Problem status lifecycle (Active → Inactive → Resolved)
- ✅ Service-connected condition tracking

**Technical Features:**
- ✅ Multi-source data (CDWWork VistA + CDWWork2 Cerner)
- ✅ Real-time VistA overlay (T-0 problem updates)
- ✅ ICD-10 code categorization (Cardiovascular, Respiratory, etc.)
- ✅ Temporal tracking (onset, entered, modified, resolved dates)

### 1.3 Expected Impact

**Machine Learning Value:**
- **AUC Improvement:** +0.05-0.08 for readmission prediction (CRITICAL)
- **Feature Richness:** 30+ new ML features (chronic condition flags, CCI score, disease counts)
- **Subgroup Analysis:** Disease-specific models (CHF, COPD, diabetes cohorts)

**Clinical Value:**
- **Care Coordination:** Identify complex patients (Charlson ≥6, polypharmacy + multi-morbidity)
- **Clinical Insights:** AI-powered disease burden assessment and care gap analysis
- **Continuity of Care:** Complete problem history across VA facilities

---

## 2. Clinical Context

### 2.1 Problem List vs. Diagnoses

**Critical Distinction:**

| Aspect | Problem List | Encounter Diagnoses |
|--------|-------------|-------------------|
| **Purpose** | Long-term chronic condition tracking | Episodic billing/administrative |
| **Coding** | SNOMED CT (clinical terminology) | ICD-10-CM (billing) |
| **Scope** | Persistent across encounters | Tied to specific visit |
| **Example** | "Diabetes Type 2" (active for years) | "Hyperglycemia" (today's visit) |
| **Clinical Use** | Care planning, medication management | Billing, documentation |

**Implementation Approach:** Unified view merging both problem list and encounter diagnoses.

### 2.2 VA-Specific Considerations

**Dual Coding System:**
- **VistA Historical:** ICD-9 → ICD-10 transition (October 2015)
- **Current State:** SNOMED CT (clinical) + ICD-10 (billing)
- **Display:** Both codes shown to clinicians

**Service-Connected Conditions:**
- Flag problems related to military service
- Impacts care priority and benefits eligibility
- Critical for VA-specific workflows

### 2.3 Charlson Comorbidity Index (CCI)

**Clinical Significance:**
- **Mortality Predictor:** 10-year mortality risk based on 19 conditions
- **Complexity Indicator:** Helps identify high-risk patients
- **Readmission Risk:** Strong correlation with 30-day readmissions

**Scoring:**
- 1 point: MI, CHF, PVD, CVD, dementia, COPD, connective tissue disease, PUD, mild liver disease, diabetes (uncomplicated)
- 2 points: Hemiplegia, moderate/severe renal disease, diabetes with complications, malignancy, leukemia, lymphoma
- 3 points: Moderate/severe liver disease
- 6 points: Metastatic cancer, AIDS

**Interpretation:**
- 0-1: Low burden (12% 1-year mortality)
- 2-3: Moderate burden (26% 1-year mortality)
- 4-5: High burden (52% 1-year mortality)
- ≥6: Very high burden (85% 1-year mortality)

### 2.4 Clinical Use Cases

**Primary Use Cases:**
1. **Chronic Disease Management:** Track diabetes, CHF, COPD control
2. **Medication Reconciliation:** Ensure meds align with diagnoses
3. **Care Gaps:** Identify missing screenings (HbA1c for diabetics)
4. **Risk Stratification:** CCI score for care coordination prioritization
5. **Readmission Prevention:** High CCI + recent admission = intervention target

---

## 3. Data Sources & Architecture

### 3.1 Source Systems

**CDWWork (VistA-Based):**
- `Outpat.ProblemList` - Long-term problem tracking
- `Outpat.VDiagnosis` - Outpatient encounter diagnoses
- `Inpat.InpatientDischargeDiagnosis` - Inpatient discharge diagnoses
- `Dim.ICD10`, `Dim.ICD9`, `Dim.SNOMED` - Code definitions

**CDWWork2 (Cerner-Based):**
- `EncMill.ProblemList` - Chronic problem list
- `EncMill.Diagnosis` - Encounter diagnoses
- Uses SNOMED CT + ICD-10 (no ICD-9 legacy)

**VistA Real-Time (T-0):**
- RPC: `ORQQPL LIST` - Get active problem list
- RPC: `ORQQPL DETAIL` - Get problem details
- Returns: All active problems with "updated today" flag

### 3.2 Data Architecture

**Medallion Pipeline:**

```
┌─────────────────────────────────────────────────────────────┐
│ BRONZE LAYER                                                │
├─────────────────────────────────────────────────────────────┤
│ CDWWork:                                                    │
│ - problem_list_raw.parquet (VistA problem list)           │
│ - v_diagnosis_raw.parquet (VistA encounter diagnoses)     │
│ - icd10_codes.parquet (code definitions)                  │
│                                                             │
│ CDWWork2:                                                   │
│ - cerner_problem_list_raw.parquet                          │
│ - cerner_diagnosis_raw.parquet                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SILVER LAYER                                                │
├─────────────────────────────────────────────────────────────┤
│ - problems_cleaned.parquet                                  │
│   • Harmonize VistA + Cerner schemas                       │
│   • Resolve patient identity (ICN)                         │
│   • Join code descriptions                                 │
│   • Deduplicate problems                                   │
│   • Calculate ICD-10 categories                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ GOLD LAYER                                                  │
├─────────────────────────────────────────────────────────────┤
│ - patient_problems.parquet                                  │
│   • Patient-centric view                                   │
│   • Calculate Charlson Index per patient                   │
│   • Flag chronic conditions (diabetes, CHF, CKD, COPD)     │
│   • Active problem count aggregation                       │
│   • Category grouping (Cardiovascular, Respiratory, etc.)  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ POSTGRESQL (Serving DB)                                     │
├─────────────────────────────────────────────────────────────┤
│ clinical.patient_problems                                   │
│ - Problem list + encounter diagnoses merged                │
│ - Active/inactive/resolved status                          │
│ - Charlson score per patient                               │
│ - Chronic condition flags                                  │
└─────────────────────────────────────────────────────────────┘
```

### 3.3 Data Harmonization Strategy

**VistA vs. Cerner Differences:**

| Field | VistA (CDWWork) | Cerner (CDWWork2) | Harmonization |
|-------|----------------|-------------------|---------------|
| Patient ID | PatientSID | PersonSID | Map to ICN |
| Coding | SNOMED + ICD-10 + ICD-9 | SNOMED + ICD-10 | Keep all codes |
| Problem Text | Free-text common | Structured | Preserve both |
| Status | Active/Inactive/Resolved | Active/Resolved | Map to 3-state |
| Date Fields | Onset, Entered, Modified, Resolved | Onset, Documented, Resolved | Standardize names |

**Deduplication Logic:**
- Same ICN + Same ICD-10 Code + Same Onset Date = Duplicate
- Prefer VistA for active problems (authoritative source)
- Preserve Cerner if unique facility data

---

## 4. Mock Data Design

### 4.1 Test Patient Distribution

**38 Test Patients → Problem List Coverage:**

| Patient Age Group | Avg Problems | Charlson Score | Example Patients |
|------------------|-------------|----------------|------------------|
| Young (30-40) | 3-5 | 0-2 | ICN100005, ICN100009 |
| Middle (50-60) | 6-10 | 2-4 | ICN100002, ICN100010 |
| Elderly (70+) | 10-15 | 4-8 | ICN100001, ICN100007 |

**Total Mock Records:** ~400 problem/diagnosis records

### 4.2 Top 50 ICD-10 Codes (High-Value Conditions)

**Cardiovascular (I00-I99):**
- `I50.9` - Heart failure, unspecified (CHF)
- `I10` - Essential (primary) hypertension
- `I25.10` - Atherosclerotic heart disease (CAD)
- `I48.91` - Atrial fibrillation
- `I50.23` - Acute on chronic systolic heart failure

**Respiratory (J00-J99):**
- `J44.9` - Chronic obstructive pulmonary disease (COPD)
- `J45.909` - Asthma, unspecified, uncomplicated
- `J18.9` - Pneumonia, unspecified

**Endocrine/Metabolic (E00-E89):**
- `E11.9` - Type 2 diabetes mellitus without complications
- `E11.65` - Type 2 diabetes with hyperglycemia
- `E11.22` - Type 2 diabetes with diabetic chronic kidney disease
- `E78.5` - Hyperlipidemia, unspecified
- `E66.9` - Obesity, unspecified

**Renal (N00-N99):**
- `N18.3` - Chronic kidney disease, stage 3
- `N18.4` - Chronic kidney disease, stage 4
- `N18.5` - Chronic kidney disease, stage 5

**Mental Health (F00-F99):**
- `F32.9` - Major depressive disorder, single episode
- `F33.1` - Major depressive disorder, recurrent, moderate
- `F41.1` - Generalized anxiety disorder
- `F10.20` - Alcohol dependence, uncomplicated
- `F43.10` - Post-traumatic stress disorder (PTSD)

**Musculoskeletal (M00-M99):**
- `M15.9` - Osteoarthritis, unspecified
- `M81.0` - Osteoporosis without current pathological fracture
- `M54.5` - Low back pain

**Neoplasms (C00-D49):**
- `C61` - Malignant neoplasm of prostate
- `C34.90` - Malignant neoplasm of bronchus and lung
- `C18.9` - Malignant neoplasm of colon, unspecified

**Charlson Condition Coverage (All 19):**
- MI: `I21.9`, `I22.9`, `I25.2`
- CHF: `I50.9`, `I50.23`
- PVD: `I70.209`, `I73.9`
- CVD: `I63.9`, `G45.9`
- Dementia: `F03.90`, `G30.9`
- COPD: `J44.9`, `J43.9`
- Connective Tissue: `M05.9`, `M32.9`
- PUD: `K27.9`
- Mild Liver: `K74.60`
- Diabetes (uncomp): `E11.9`
- Hemiplegia: `G81.90`
- Renal (moderate/severe): `N18.4`, `N18.5`
- Diabetes (comp): `E11.22`, `E11.51`
- Malignancy: `C61`, `C34.90`
- Leukemia: `C91.10`
- Lymphoma: `C85.90`
- Liver (severe): `K72.90`
- Metastatic cancer: `C79.9`
- AIDS: `B20`

### 4.3 CDWWork Mock Schema

#### 4.3.1 Outpat.ProblemList

```sql
CREATE TABLE [Outpat].[ProblemList] (
    [ProblemListSID] BIGINT IDENTITY(10001,1) PRIMARY KEY,
    [PatientSID] INT NOT NULL,
    [Sta3n] SMALLINT NOT NULL,

    -- Dual coding
    [SNOMEDCode] VARCHAR(50) NULL,           -- e.g., '44054006' (Diabetes Type 2)
    [ICD10Code] VARCHAR(20) NULL,            -- e.g., 'E11.9'
    [ICD9Code] VARCHAR(20) NULL,             -- Legacy (pre-2015)

    -- Problem details
    [ProblemText] VARCHAR(200) NOT NULL,     -- 'Diabetes mellitus type 2'
    [ProblemStatus] VARCHAR(20) NOT NULL,    -- 'Active', 'Inactive', 'Resolved'

    -- Temporal tracking
    [OnsetDate] DATE NULL,                   -- When problem started
    [EnteredDateTime] DATETIME2(0) NULL,     -- When added to system
    [ModifiedDateTime] DATETIME2(0) NULL,    -- Last update
    [ResolvedDate] DATE NULL,                -- When resolved (if applicable)

    -- Clinical metadata
    [EnteringProviderSID] INT NULL,
    [ResponsibleProviderSID] INT NULL,
    [ClinicSID] INT NULL,

    -- VA-specific
    [ServiceConnected] BIT NULL,             -- SC condition flag
    [Priority] VARCHAR(20) NULL,             -- 'Chronic', 'Acute'
    [Comments] VARCHAR(500) NULL,            -- Clinical notes

    -- Audit
    [SourceSystem] VARCHAR(20) DEFAULT 'CDWWork',
    [LoadDateTime] DATETIME2(0) DEFAULT GETDATE()
);

CREATE INDEX IX_ProblemList_Patient ON Outpat.ProblemList(PatientSID);
CREATE INDEX IX_ProblemList_Status ON Outpat.ProblemList(ProblemStatus) WHERE ProblemStatus = 'Active';
CREATE INDEX IX_ProblemList_ICD10 ON Outpat.ProblemList(ICD10Code);
```

#### 4.3.2 Dim.ICD10

```sql
CREATE TABLE [Dim].[ICD10] (
    [ICD10SID] INT IDENTITY(1,1) PRIMARY KEY,
    [ICD10Code] VARCHAR(20) NOT NULL UNIQUE,  -- 'I50.9', 'E11.9'
    [ICD10Name] VARCHAR(200) NOT NULL,        -- 'Heart failure, unspecified'
    [ICD10Category] VARCHAR(100) NULL,        -- 'Cardiovascular'
    [ICD10Chapter] VARCHAR(100) NULL,         -- 'Diseases of circulatory system (I00-I99)'
    [ICD10ChapterCode] VARCHAR(10) NULL,      -- 'IX'
    [IsActive] BIT NOT NULL DEFAULT 1,
    [EffectiveDate] DATE NULL,
    [TerminationDate] DATE NULL
);

CREATE INDEX IX_ICD10_Code ON Dim.ICD10(ICD10Code);
CREATE INDEX IX_ICD10_Category ON Dim.ICD10(ICD10Category);
```

#### 4.3.3 Dim.CharlsonMapping

```sql
CREATE TABLE [Dim].[CharlsonMapping] (
    [CharlsonMappingSID] INT IDENTITY(1,1) PRIMARY KEY,
    [ICD10Code] VARCHAR(20) NOT NULL,
    [ConditionCategory] VARCHAR(100) NOT NULL,  -- 'Myocardial Infarction', 'CHF', 'COPD', etc.
    [PointValue] TINYINT NOT NULL,              -- 1, 2, 3, or 6
    [ConditionDescription] VARCHAR(200) NULL    -- Detailed explanation
);

CREATE INDEX IX_CharlsonMapping_ICD10 ON Dim.CharlsonMapping(ICD10Code);
CREATE INDEX IX_CharlsonMapping_Condition ON Dim.CharlsonMapping(ConditionCategory);
```

### 4.4 CDWWork2 Mock Schema

#### 4.4.1 EncMill.ProblemList

```sql
CREATE TABLE [EncMill].[ProblemList] (
    [ProblemListSID] BIGINT IDENTITY(20001,1) PRIMARY KEY,
    [PersonSID] INT NOT NULL,  -- Cerner uses PersonSID

    -- Coding (ICD-10 + SNOMED, no ICD-9)
    [SNOMEDCode] VARCHAR(50) NULL,
    [ICD10Code] VARCHAR(20) NULL,

    -- Problem details
    [ProblemDescription] VARCHAR(200) NOT NULL,
    [ProblemStatus] VARCHAR(20) NOT NULL,        -- 'Active', 'Resolved'
    [ProblemClass] VARCHAR(50) NULL,             -- 'Diagnosis', 'Symptom', 'Finding'

    -- Temporal
    [OnsetDate] DATE NULL,
    [DocumentedDateTime] DATETIME2(0) NULL,
    [ResolvedDate] DATE NULL,

    -- Clinical metadata
    [EnteringProviderSID] INT NULL,
    [Severity] VARCHAR(20) NULL,                 -- 'Mild', 'Moderate', 'Severe'
    [Comments] VARCHAR(500) NULL,

    -- Audit
    [SourceSystem] VARCHAR(20) DEFAULT 'CDWWork2',
    [LoadDateTime] DATETIME2(0) DEFAULT GETDATE()
);

CREATE INDEX IX_ProblemList_Cerner_Person ON EncMill.ProblemList(PersonSID);
CREATE INDEX IX_ProblemList_Cerner_Status ON EncMill.ProblemList(ProblemStatus) WHERE ProblemStatus = 'Active';
```

### 4.5 Mock Data Scenarios

**Scenario 1: Young Veteran (ICN100005, Age 35)**
```sql
-- Simple case: 3 active problems
INSERT INTO Outpat.ProblemList VALUES
(1005, 508, '38341003', 'I10', NULL, 'Essential hypertension', 'Active', '2022-03-15', '2022-03-20', NULL, NULL, ...),
(1005, 508, '44054006', 'E11.9', NULL, 'Type 2 diabetes mellitus', 'Active', '2023-01-10', '2023-01-15', NULL, NULL, ...),
(1005, 508, NULL, 'M54.5', NULL, 'Low back pain', 'Active', '2024-06-01', '2024-06-05', NULL, NULL, ...);

-- Charlson Score: 1 (diabetes uncomp)
```

**Scenario 2: Complex Elderly Veteran (ICN100001, Age 89)**
```sql
-- Complex case: 12 active problems, Charlson = 7
INSERT INTO Outpat.ProblemList VALUES
-- Cardiovascular (3 points total)
(1001, 508, '42343007', 'I50.23', NULL, 'Acute on chronic systolic heart failure', 'Active', '2018-05-10', ...),  -- CHF (1pt)
(1001, 508, '22298006', 'I21.9', NULL, 'Acute myocardial infarction', 'Resolved', '2017-03-15', ..., '2017-05-01'),  -- MI (1pt)
(1001, 508, '49601007', 'I48.91', NULL, 'Atrial fibrillation', 'Active', '2019-02-20', ...),  -- 0pt (not in CCI)

-- Respiratory (1 point)
(1001, 508, '13645005', 'J44.9', NULL, 'Chronic obstructive pulmonary disease', 'Active', '2015-08-01', ...),  -- COPD (1pt)

-- Renal (2 points)
(1001, 508, '431855005', 'N18.4', NULL, 'Chronic kidney disease stage 4', 'Active', '2020-11-12', ...),  -- CKD (2pt)

-- Diabetes with complications (2 points)
(1001, 508, '44054006', 'E11.22', NULL, 'Type 2 diabetes with CKD', 'Active', '2016-01-05', ...),  -- DM comp (2pt)

-- Mental health (0 points, not in CCI)
(1001, 508, '33449004', 'F32.9', NULL, 'Major depressive disorder', 'Active', '2019-06-15', ...),
(1001, 508, '371631005', 'F43.10', NULL, 'Post-traumatic stress disorder', 'Active', '2018-09-20', ...),

-- Musculoskeletal (0 points)
(1001, 508, '396275006', 'M15.9', NULL, 'Osteoarthritis', 'Active', '2014-03-10', ...),

-- Other chronic (0 points)
(1001, 508, '38341003', 'I10', NULL, 'Essential hypertension', 'Active', '2010-01-15', ...),
(1001, 508, '55822004', 'E78.5', NULL, 'Hyperlipidemia', 'Active', '2012-07-20', ...),
(1001, 508, '414916001', 'E66.9', NULL, 'Obesity', 'Active', '2013-11-05', ...);

-- Charlson Score: 1 (CHF) + 1 (MI, resolved) + 1 (COPD) + 2 (CKD stage 4) + 2 (DM w/ comp) = 7
-- High complexity patient → High readmission risk
```

**Scenario 3: Service-Connected Conditions (ICN100007)**
```sql
-- Former POW with service-connected conditions
INSERT INTO Outpat.ProblemList VALUES
(1007, 516, '371631005', 'F43.10', NULL, 'Post-traumatic stress disorder', 'Active', '2015-01-01', ..., ServiceConnected = 1),
(1007, 516, '35489007', 'F33.1', NULL, 'Major depressive disorder, recurrent', 'Active', '2016-03-15', ..., ServiceConnected = 1),
(1007, 516, '22298006', 'I25.2', NULL, 'Old myocardial infarction', 'Active', '2018-08-20', ..., ServiceConnected = 1);

-- All flagged as service-connected (POW status from military_history table)
```

### 4.6 Dimension Data Population

**Dim.ICD10 - Top 50 Codes:**
```sql
INSERT INTO Dim.ICD10 (ICD10Code, ICD10Name, ICD10Category, ICD10Chapter) VALUES
-- Cardiovascular
('I50.9', 'Heart failure, unspecified', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I50.23', 'Acute on chronic systolic heart failure', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I10', 'Essential (primary) hypertension', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I25.10', 'Atherosclerotic heart disease', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I48.91', 'Atrial fibrillation', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I21.9', 'Acute myocardial infarction', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),
('I25.2', 'Old myocardial infarction', 'Cardiovascular', 'Diseases of circulatory system (I00-I99)'),

-- Respiratory
('J44.9', 'Chronic obstructive pulmonary disease', 'Respiratory', 'Diseases of respiratory system (J00-J99)'),
('J45.909', 'Asthma, unspecified, uncomplicated', 'Respiratory', 'Diseases of respiratory system (J00-J99)'),
('J18.9', 'Pneumonia, unspecified', 'Respiratory', 'Diseases of respiratory system (J00-J99)'),

-- Endocrine/Metabolic
('E11.9', 'Type 2 diabetes mellitus without complications', 'Endocrine', 'Endocrine/metabolic diseases (E00-E89)'),
('E11.65', 'Type 2 diabetes with hyperglycemia', 'Endocrine', 'Endocrine/metabolic diseases (E00-E89)'),
('E11.22', 'Type 2 diabetes with chronic kidney disease', 'Endocrine', 'Endocrine/metabolic diseases (E00-E89)'),
('E78.5', 'Hyperlipidemia, unspecified', 'Endocrine', 'Endocrine/metabolic diseases (E00-E89)'),
('E66.9', 'Obesity, unspecified', 'Endocrine', 'Endocrine/metabolic diseases (E00-E89)'),

-- Renal
('N18.3', 'Chronic kidney disease, stage 3', 'Renal', 'Diseases of genitourinary system (N00-N99)'),
('N18.4', 'Chronic kidney disease, stage 4', 'Renal', 'Diseases of genitourinary system (N00-N99)'),
('N18.5', 'Chronic kidney disease, stage 5', 'Renal', 'Diseases of genitourinary system (N00-N99)'),

-- Mental Health
('F32.9', 'Major depressive disorder, single episode', 'Mental Health', 'Mental/behavioral disorders (F00-F99)'),
('F33.1', 'Major depressive disorder, recurrent, moderate', 'Mental Health', 'Mental/behavioral disorders (F00-F99)'),
('F41.1', 'Generalized anxiety disorder', 'Mental Health', 'Mental/behavioral disorders (F00-F99)'),
('F10.20', 'Alcohol dependence, uncomplicated', 'Mental Health', 'Mental/behavioral disorders (F00-F99)'),
('F43.10', 'Post-traumatic stress disorder', 'Mental Health', 'Mental/behavioral disorders (F00-F99)'),

-- Musculoskeletal
('M15.9', 'Osteoarthritis, unspecified', 'Musculoskeletal', 'Diseases of musculoskeletal system (M00-M99)'),
('M81.0', 'Osteoporosis without fracture', 'Musculoskeletal', 'Diseases of musculoskeletal system (M00-M99)'),
('M54.5', 'Low back pain', 'Musculoskeletal', 'Diseases of musculoskeletal system (M00-M99)'),

-- Neoplasms
('C61', 'Malignant neoplasm of prostate', 'Neoplasm', 'Neoplasms (C00-D49)'),
('C34.90', 'Malignant neoplasm of bronchus and lung', 'Neoplasm', 'Neoplasms (C00-D49)'),
('C18.9', 'Malignant neoplasm of colon', 'Neoplasm', 'Neoplasms (C00-D49)');

-- [Continue for all 50+ codes...]
```

**Dim.CharlsonMapping - All 19 Conditions:**
```sql
INSERT INTO Dim.CharlsonMapping (ICD10Code, ConditionCategory, PointValue, ConditionDescription) VALUES
-- 1 Point Conditions
('I21%', 'Myocardial Infarction', 1, 'Acute MI'),
('I22%', 'Myocardial Infarction', 1, 'Subsequent MI'),
('I25.2', 'Myocardial Infarction', 1, 'Old MI'),
('I50%', 'Congestive Heart Failure', 1, 'Heart failure'),
('I09.9', 'Congestive Heart Failure', 1, 'Rheumatic heart disease'),
-- [Continue for all CHF codes]

('I70%', 'Peripheral Vascular Disease', 1, 'Atherosclerosis'),
-- [All PVD codes]

('G45%', 'Cerebrovascular Disease', 1, 'TIA'),
('I60%', 'Cerebrovascular Disease', 1, 'Subarachnoid hemorrhage'),
-- [All CVD codes]

('F00%', 'Dementia', 1, 'Alzheimer disease'),
('F03%', 'Dementia', 1, 'Unspecified dementia'),
('G30%', 'Dementia', 1, 'Alzheimer disease'),

('J40%', 'Chronic Pulmonary Disease', 1, 'Bronchitis'),
('J44%', 'Chronic Pulmonary Disease', 1, 'COPD'),
('J45%', 'Chronic Pulmonary Disease', 1, 'Asthma'),
-- [All COPD codes]

('M05%', 'Rheumatologic Disease', 1, 'Rheumatoid arthritis'),
('M06%', 'Rheumatologic Disease', 1, 'Rheumatoid arthritis'),
-- [All connective tissue codes]

('K25%', 'Peptic Ulcer Disease', 1, 'Gastric ulcer'),
('K26%', 'Peptic Ulcer Disease', 1, 'Duodenal ulcer'),

('K70.0', 'Mild Liver Disease', 1, 'Alcoholic fatty liver'),
('K70.3', 'Mild Liver Disease', 1, 'Alcoholic cirrhosis'),
-- [All mild liver codes]

('E08.0', 'Diabetes Uncomplicated', 1, 'Diabetes due to underlying condition without complications'),
('E10.0', 'Diabetes Uncomplicated', 1, 'Type 1 diabetes without complications'),
('E11.0', 'Diabetes Uncomplicated', 1, 'Type 2 diabetes without complications'),
('E11.9', 'Diabetes Uncomplicated', 1, 'Type 2 diabetes without complications'),

-- 2 Point Conditions
('G81%', 'Hemiplegia', 2, 'Hemiplegia and hemiparesis'),
('G82%', 'Hemiplegia', 2, 'Paraplegia'),

('I12.0', 'Moderate/Severe Renal Disease', 2, 'Hypertensive CKD with stage 5 or ESRD'),
('N18.3', 'Moderate/Severe Renal Disease', 2, 'CKD stage 3'),
('N18.4', 'Moderate/Severe Renal Disease', 2, 'CKD stage 4'),
('N18.5', 'Moderate/Severe Renal Disease', 2, 'CKD stage 5'),

('E08.2', 'Diabetes Complicated', 2, 'Diabetes with kidney complications'),
('E10.2', 'Diabetes Complicated', 2, 'Type 1 diabetes with kidney complications'),
('E11.2', 'Diabetes Complicated', 2, 'Type 2 diabetes with kidney complications'),
('E11.22', 'Diabetes Complicated', 2, 'Type 2 diabetes with CKD'),

('C00%', 'Malignancy', 2, 'Malignant neoplasm of lip'),
('C61', 'Malignancy', 2, 'Malignant neoplasm of prostate'),
-- [All malignancy codes C00-C76, C81-C97]

('C91%', 'Leukemia', 2, 'Lymphoid leukemia'),
('C92%', 'Leukemia', 2, 'Myeloid leukemia'),

('C81%', 'Lymphoma', 2, 'Hodgkin lymphoma'),
('C85%', 'Lymphoma', 2, 'Non-Hodgkin lymphoma'),

-- 3 Point Conditions
('K70.4', 'Moderate/Severe Liver Disease', 3, 'Alcoholic hepatic failure'),
('K72.1', 'Moderate/Severe Liver Disease', 3, 'Chronic hepatic failure'),

-- 6 Point Conditions
('C77%', 'Metastatic Solid Tumor', 6, 'Secondary malignant neoplasm of lymph nodes'),
('C78%', 'Metastatic Solid Tumor', 6, 'Secondary malignant neoplasm of respiratory/digestive organs'),
('C79%', 'Metastatic Solid Tumor', 6, 'Secondary malignant neoplasm of other sites'),

('B20%', 'AIDS', 6, 'HIV disease'),
('B24', 'AIDS', 6, 'Unspecified HIV disease');
```

---

## 5. ETL Pipeline Design

### 5.1 Bronze Layer: Extraction

**Script:** `etl/bronze_problems.py`

**Extraction Queries:**

**CDWWork - Problem List:**
```sql
SELECT
    ProblemListSID,
    PatientSID,
    Sta3n,
    SNOMEDCode,
    ICD10Code,
    ICD9Code,
    ProblemText,
    ProblemStatus,
    OnsetDate,
    EnteredDateTime,
    ModifiedDateTime,
    ResolvedDate,
    EnteringProviderSID,
    ResponsibleProviderSID,
    ClinicSID,
    ServiceConnected,
    Priority,
    Comments
FROM Outpat.ProblemList
```

**CDWWork - ICD-10 Codes:**
```sql
SELECT
    ICD10SID,
    ICD10Code,
    ICD10Name,
    ICD10Category,
    ICD10Chapter
FROM Dim.ICD10
WHERE IsActive = 1
```

**CDWWork - Charlson Mapping:**
```sql
SELECT
    CharlsonMappingSID,
    ICD10Code,
    ConditionCategory,
    PointValue,
    ConditionDescription
FROM Dim.CharlsonMapping
```

**CDWWork2 - Problem List:**
```sql
SELECT
    ProblemListSID,
    PersonSID,
    SNOMEDCode,
    ICD10Code,
    ProblemDescription,
    ProblemStatus,
    ProblemClass,
    OnsetDate,
    DocumentedDateTime,
    ResolvedDate,
    EnteringProviderSID,
    Severity,
    Comments
FROM EncMill.ProblemList
```

**Output Files:**
- `bronze/cdwwork/problems/problem_list_raw.parquet`
- `bronze/cdwwork/problems/icd10_codes.parquet`
- `bronze/cdwwork/problems/charlson_mapping.parquet`
- `bronze/cdwwork2/problems/cerner_problem_list_raw.parquet`

### 5.2 Silver Layer: Harmonization

**Script:** `etl/silver_problems.py`

**Transformation Logic:**

```python
import polars as pl
from datetime import datetime, timezone

def transform_problems_silver():
    """Transform Bronze problems to Silver layer."""

    # Read Bronze files
    df_vista = minio_client.read_parquet("bronze/cdwwork/problems/problem_list_raw.parquet")
    df_cerner = minio_client.read_parquet("bronze/cdwwork2/problems/cerner_problem_list_raw.parquet")
    df_patient = minio_client.read_parquet("bronze/cdwwork/patient/patient_raw.parquet")
    df_icd10 = minio_client.read_parquet("bronze/cdwwork/problems/icd10_codes.parquet")

    # Harmonize VistA schema
    df_vista_cleaned = df_vista.with_columns([
        pl.col("PatientSID").alias("patient_sid"),
        pl.col("ICD10Code").str.strip_chars().alias("icd10_code"),
        pl.col("SNOMEDCode").str.strip_chars().alias("snomed_code"),
        pl.col("ICD9Code").str.strip_chars().alias("icd9_code"),
        pl.col("ProblemText").alias("problem_text"),
        pl.col("ProblemStatus").str.strip_chars().alias("problem_status"),  # Active/Inactive/Resolved
        pl.col("OnsetDate").alias("onset_date"),
        pl.col("EnteredDateTime").alias("entered_datetime"),
        pl.col("ModifiedDateTime").alias("modified_datetime"),
        pl.col("ResolvedDate").alias("resolved_date"),
        pl.col("ServiceConnected").cast(pl.Boolean).alias("service_connected"),
        pl.lit("VistA").alias("source_system"),
        pl.col("Sta3n").alias("facility_id"),
    ])

    # Harmonize Cerner schema
    df_cerner_cleaned = df_cerner.with_columns([
        pl.col("PersonSID").alias("patient_sid"),  # Cerner uses PersonSID
        pl.col("ICD10Code").str.strip_chars().alias("icd10_code"),
        pl.col("SNOMEDCode").str.strip_chars().alias("snomed_code"),
        pl.lit(None).alias("icd9_code"),  # Cerner has no ICD-9
        pl.col("ProblemDescription").alias("problem_text"),
        pl.col("ProblemStatus").str.strip_chars().alias("problem_status"),  # Active/Resolved only
        pl.col("OnsetDate").alias("onset_date"),
        pl.col("DocumentedDateTime").alias("entered_datetime"),
        pl.lit(None).alias("modified_datetime"),  # Not tracked in Cerner
        pl.col("ResolvedDate").alias("resolved_date"),
        pl.lit(None).cast(pl.Boolean).alias("service_connected"),  # Not in Cerner
        pl.lit("Cerner").alias("source_system"),
        pl.lit(None).alias("facility_id"),  # Cerner doesn't use Sta3n
    ])

    # Union VistA + Cerner
    df_combined = pl.concat([df_vista_cleaned, df_cerner_cleaned])

    # Join with patient data to get ICN
    df_patient_icn = df_patient.select([
        pl.col("PatientSID"),
        pl.col("PatientICN").alias("icn"),
    ])

    df = df_combined.join(
        df_patient_icn,
        left_on="patient_sid",
        right_on="PatientSID",
        how="inner"
    )

    # Join with ICD-10 codes to get category
    df_icd10_lookup = df_icd10.select([
        pl.col("ICD10Code").alias("icd10_code"),
        pl.col("ICD10Name").alias("icd10_description"),
        pl.col("ICD10Category").alias("icd10_category"),
    ])

    df = df.join(
        df_icd10_lookup,
        on="icd10_code",
        how="left"  # Left join to preserve problems without ICD-10
    )

    # Deduplicate: Same ICN + ICD-10 + Onset Date = Duplicate
    # Prefer VistA for active problems
    df = df.sort(["icn", "icd10_code", "onset_date", "source_system"])  # VistA sorts before Cerner
    df = df.unique(subset=["icn", "icd10_code", "onset_date"], keep="first")

    logger.info(f"After deduplication: {len(df)} problems")

    # Add timestamp
    df = df.with_columns([
        pl.lit(datetime.now(timezone.utc)).alias("last_updated"),
    ])

    # Write to Silver
    silver_path = build_silver_path("problems", "problems_cleaned.parquet")
    minio_client.write_parquet(df, silver_path)

    return df
```

**Output:** `silver/problems/problems_cleaned.parquet`

### 5.3 Gold Layer: Aggregation & Charlson Calculation

**Script:** `etl/gold_problems.py`

**Transformation Logic:**

```python
def create_gold_problems():
    """Create Gold layer with Charlson Index."""

    # Read Silver
    df_problems = minio_client.read_parquet("silver/problems/problems_cleaned.parquet")
    df_charlson = minio_client.read_parquet("bronze/cdwwork/problems/charlson_mapping.parquet")

    # Create patient_key
    df_problems = df_problems.with_columns([
        pl.col("icn").alias("patient_key")
    ])

    # Calculate Charlson Index per patient
    # Step 1: Join problems with Charlson mapping
    df_with_charlson = df_problems.join(
        df_charlson.select([
            pl.col("ICD10Code").alias("icd10_code"),
            pl.col("ConditionCategory").alias("charlson_condition"),
            pl.col("PointValue").alias("charlson_points"),
        ]),
        on="icd10_code",
        how="left"
    ).filter(
        pl.col("problem_status") == "Active"  # Only count active problems
    )

    # Step 2: Aggregate by patient and condition (max points if multiple codes map to same condition)
    df_patient_conditions = (
        df_with_charlson
        .filter(pl.col("charlson_condition").is_not_null())
        .group_by(["patient_key", "charlson_condition"])
        .agg([
            pl.col("charlson_points").max().alias("condition_points")
        ])
    )

    # Step 3: Sum points per patient
    df_charlson_scores = (
        df_patient_conditions
        .group_by("patient_key")
        .agg([
            pl.col("condition_points").sum().alias("charlson_index"),
            pl.col("charlson_condition").n_unique().alias("charlson_condition_count"),
        ])
    )

    # Calculate active problem counts per patient
    df_active_counts = (
        df_problems
        .filter(pl.col("problem_status") == "Active")
        .group_by("patient_key")
        .agg([
            pl.count().alias("active_problem_count"),
        ])
    )

    # Flag specific chronic conditions (for ML features)
    df_chronic_flags = (
        df_problems
        .filter(pl.col("problem_status") == "Active")
        .group_by("patient_key")
        .agg([
            pl.col("icd10_code").str.contains("^I50").any().alias("has_chf"),
            pl.col("icd10_code").str.contains("^J44").any().alias("has_copd"),
            pl.col("icd10_code").str.contains("^E11").any().alias("has_diabetes"),
            pl.col("icd10_code").str.contains("^N18").any().alias("has_ckd"),
            pl.col("icd10_code").str.contains("^F32|^F33").any().alias("has_depression"),
            pl.col("icd10_code").str.contains("^F43\\.10").any().alias("has_ptsd"),
        ])
    )

    # Join all patient-level aggregations
    df_gold = df_problems.join(df_charlson_scores, on="patient_key", how="left")
    df_gold = df_gold.join(df_active_counts, on="patient_key", how="left")
    df_gold = df_gold.join(df_chronic_flags, on="patient_key", how="left")

    # Fill nulls for patients without Charlson conditions
    df_gold = df_gold.with_columns([
        pl.col("charlson_index").fill_null(0),
        pl.col("active_problem_count").fill_null(0),
    ])

    # Write to Gold
    gold_path = build_gold_path("problems", "patient_problems.parquet")
    minio_client.write_parquet(df_gold, gold_path)

    return df_gold
```

**Output:** `gold/problems/patient_problems.parquet`

### 5.4 Load to PostgreSQL

**Script:** `etl/load_problems.py`

**Load Logic:**

```python
def load_problems_to_postgres():
    """Load Gold problems to PostgreSQL."""

    # Read Gold
    df = minio_client.read_parquet("gold/problems/patient_problems.parquet")

    logger.info(f"Read {len(df)} problem records from Gold layer")

    # Convert to Pandas
    df_pandas = df.to_pandas()

    # Create SQLAlchemy engine
    engine = create_engine(DATABASE_URL)

    # Load to PostgreSQL (truncate and reload)
    df_pandas.to_sql(
        "patient_problems",
        engine,
        schema="clinical",
        if_exists="replace",
        index=False,
        method="multi",
    )

    logger.info(f"Loaded {len(df)} problem records to PostgreSQL")

    # Verification queries
    with engine.connect() as conn:
        # Total records
        result = conn.execute(text("SELECT COUNT(*) FROM clinical.patient_problems")).fetchone()
        logger.info(f"Verification: {result[0]} rows in patient_problems table")

        # Active problems summary
        result = conn.execute(text("""
            SELECT
                COUNT(DISTINCT patient_key) as patients_with_problems,
                AVG(active_problem_count) as avg_active_problems,
                AVG(charlson_index) as avg_charlson_score,
                SUM(CASE WHEN has_chf THEN 1 ELSE 0 END) as chf_count,
                SUM(CASE WHEN has_diabetes THEN 1 ELSE 0 END) as diabetes_count,
                SUM(CASE WHEN has_copd THEN 1 ELSE 0 END) as copd_count
            FROM clinical.patient_problems
            WHERE active_problem_count > 0
        """)).fetchone()

        logger.info(f"Patients with problems: {result[0]}")
        logger.info(f"Avg active problems: {result[1]:.1f}")
        logger.info(f"Avg Charlson score: {result[2]:.1f}")
        logger.info(f"CHF patients: {result[3]}, Diabetes: {result[4]}, COPD: {result[5]}")
```

---

## 6. PostgreSQL Schema

### 6.1 Clinical Schema Table

**Table:** `clinical.patient_problems`

```sql
-- Drop table if exists (for development)
DROP TABLE IF EXISTS clinical.patient_problems CASCADE;

-- Create patient problems table
CREATE TABLE clinical.patient_problems (
    -- Primary keys
    problem_id SERIAL PRIMARY KEY,
    patient_key VARCHAR(50) NOT NULL,
    icn VARCHAR(50) NOT NULL,

    -- Problem codes (dual coding)
    icd10_code VARCHAR(20),
    icd10_description VARCHAR(200),
    icd10_category VARCHAR(100),
    snomed_code VARCHAR(50),
    icd9_code VARCHAR(20),  -- Legacy

    -- Problem details
    problem_text VARCHAR(200) NOT NULL,
    problem_status VARCHAR(20) NOT NULL,  -- Active, Inactive, Resolved

    -- Temporal tracking
    onset_date DATE,
    entered_datetime TIMESTAMP,
    modified_datetime TIMESTAMP,
    resolved_date DATE,

    -- Clinical metadata
    service_connected BOOLEAN,
    priority VARCHAR(20),
    comments TEXT,

    -- Source tracking
    source_system VARCHAR(20),  -- VistA, Cerner
    facility_id SMALLINT,

    -- Patient-level aggregations (denormalized for performance)
    charlson_index INT DEFAULT 0,
    charlson_condition_count INT DEFAULT 0,
    active_problem_count INT DEFAULT 0,

    -- Chronic condition flags (ML features)
    has_chf BOOLEAN DEFAULT FALSE,
    has_copd BOOLEAN DEFAULT FALSE,
    has_diabetes BOOLEAN DEFAULT FALSE,
    has_ckd BOOLEAN DEFAULT FALSE,
    has_depression BOOLEAN DEFAULT FALSE,
    has_ptsd BOOLEAN DEFAULT FALSE,

    -- Audit
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX idx_problems_patient_key ON clinical.patient_problems(patient_key);
CREATE INDEX idx_problems_icn ON clinical.patient_problems(icn);
CREATE INDEX idx_problems_status ON clinical.patient_problems(problem_status) WHERE problem_status = 'Active';
CREATE INDEX idx_problems_icd10 ON clinical.patient_problems(icd10_code);
CREATE INDEX idx_problems_category ON clinical.patient_problems(icd10_category);
CREATE INDEX idx_problems_charlson ON clinical.patient_problems(charlson_index);
CREATE INDEX idx_problems_onset ON clinical.patient_problems(onset_date);

-- Composite index for filtered queries
CREATE INDEX idx_problems_patient_active ON clinical.patient_problems(patient_key, problem_status) WHERE problem_status = 'Active';

-- Comments for documentation
COMMENT ON TABLE clinical.patient_problems IS 'Patient problem list and diagnoses from VistA and Cerner sources';
COMMENT ON COLUMN clinical.patient_problems.icd10_code IS 'ICD-10-CM diagnosis code (e.g., I50.9, E11.9)';
COMMENT ON COLUMN clinical.patient_problems.snomed_code IS 'SNOMED CT concept code (clinical terminology)';
COMMENT ON COLUMN clinical.patient_problems.problem_status IS 'Active, Inactive, or Resolved';
COMMENT ON COLUMN clinical.patient_problems.charlson_index IS 'Charlson Comorbidity Index score (0-37, higher = more complex)';
COMMENT ON COLUMN clinical.patient_problems.service_connected IS 'Problem related to military service (VA compensation)';
```

### 6.2 Reference Schema Table

**Table:** `reference.charlson_mapping`

```sql
CREATE SCHEMA IF NOT EXISTS reference;

-- Charlson Comorbidity Index mapping table
CREATE TABLE reference.charlson_mapping (
    mapping_id SERIAL PRIMARY KEY,
    icd10_code VARCHAR(20) NOT NULL,
    condition_category VARCHAR(100) NOT NULL,  -- 'Myocardial Infarction', 'CHF', etc.
    point_value SMALLINT NOT NULL,  -- 1, 2, 3, or 6
    condition_description VARCHAR(200),

    UNIQUE(icd10_code, condition_category)
);

CREATE INDEX idx_charlson_icd10 ON reference.charlson_mapping(icd10_code);
CREATE INDEX idx_charlson_condition ON reference.charlson_mapping(condition_category);

COMMENT ON TABLE reference.charlson_mapping IS 'ICD-10 to Charlson Comorbidity Index condition mapping';
```

---

## 7. VistA RPC Integration

### 7.1 RPC Specification

**RPC Name:** `ORQQPL LIST`
**Purpose:** Get patient problem list with real-time updates

**Parameters:**
- `site` (int): VistA site number (Sta3n)
- `icn` (str): Patient ICN (resolves to DFN internally)

**Return Format:** JSON array of problems

```json
{
  "site": 200,
  "icn": "ICN100001",
  "dfn": "DFN1001",
  "problems": [
    {
      "problem_ien": "123",
      "problem_text": "Diabetes mellitus type 2",
      "icd10_code": "E11.9",
      "snomed_code": "44054006",
      "problem_status": "Active",
      "onset_date": "2023-01-15",
      "service_connected": true,
      "updated_today": false
    },
    {
      "problem_ien": "456",
      "problem_text": "Acute exacerbation of COPD",
      "icd10_code": "J44.1",
      "snomed_code": "195951007",
      "problem_status": "Active",
      "onset_date": "2026-02-07",
      "service_connected": false,
      "updated_today": true  // This problem was added/updated today (T-0)
    }
  ],
  "total_active_problems": 12,
  "last_updated": "2026-02-07T14:30:00Z"
}
```

### 7.2 Mock Data Files

**Location:** `vista/data/problems/`

**File Structure:**
```
vista/data/problems/
├── site_200_ICN100001.json
├── site_200_ICN100002.json
├── site_500_ICN100001.json
└── ...
```

**Example File:** `site_200_ICN100001.json`

```json
{
  "site": 200,
  "icn": "ICN100001",
  "dfn": "DFN1001",
  "problems": [
    {
      "problem_ien": "1001-1",
      "problem_text": "Acute on chronic systolic heart failure",
      "icd10_code": "I50.23",
      "snomed_code": "42343007",
      "problem_status": "Active",
      "onset_date": "T-2920",
      "entered_date": "T-2910",
      "modified_date": "T-0",
      "service_connected": false,
      "updated_today": true,
      "priority": "Chronic",
      "comments": "Recent decompensation, seen in ED today"
    },
    {
      "problem_ien": "1001-2",
      "problem_text": "Type 2 diabetes mellitus with chronic kidney disease",
      "icd10_code": "E11.22",
      "snomed_code": "44054006",
      "problem_status": "Active",
      "onset_date": "T-3650",
      "entered_date": "T-3640",
      "modified_date": "T-30",
      "service_connected": true,
      "updated_today": false,
      "priority": "Chronic",
      "comments": "CKD stage 3, on metformin"
    }
  ],
  "total_active_problems": 12,
  "cache_ttl_minutes": 30
}
```

**T-Notation:**
- `T-0`: Today
- `T-1`: Yesterday
- `T-30`: 30 days ago
- `T-365`: 1 year ago

### 7.3 Implementation

**File:** `vista/app/rpcs/problems.py`

```python
from fastapi import HTTPException
from datetime import datetime, timedelta
import json
from pathlib import Path
import random

def execute_orqqpl_list(site: int, icn: str) -> dict:
    """
    Execute ORQQPL LIST RPC - Get patient problem list.

    Returns all active problems with "updated today" flag for newly added/modified problems.
    """
    # Resolve ICN to site-specific DFN
    dfn = resolve_icn_to_dfn(icn, site)
    if not dfn:
        raise HTTPException(status_code=404, detail=f"Patient {icn} not found at site {site}")

    # Load mock data
    data_file = Path(f"vista/data/problems/site_{site}_{icn}.json")

    if not data_file.exists():
        return {
            "site": site,
            "icn": icn,
            "dfn": dfn,
            "problems": [],
            "total_active_problems": 0,
            "message": "No problem list data for this patient at this site"
        }

    with open(data_file, 'r') as f:
        data = json.load(f)

    # Convert T-notation dates to actual dates
    today = datetime.now().date()

    for problem in data["problems"]:
        problem["onset_date"] = convert_t_notation(problem["onset_date"], today)
        problem["entered_date"] = convert_t_notation(problem.get("entered_date"), today)
        problem["modified_date"] = convert_t_notation(problem.get("modified_date"), today)

    # Simulate network latency (1-3 seconds)
    simulate_latency()

    return data

def convert_t_notation(t_string: str, reference_date: datetime.date) -> str:
    """Convert T-notation (T-30) to actual date."""
    if not t_string or not t_string.startswith("T-"):
        return t_string

    days_ago = int(t_string.replace("T-", ""))
    actual_date = reference_date - timedelta(days=days_ago)
    return actual_date.strftime("%Y-%m-%d")

def simulate_latency():
    """Simulate VistA RPC network latency (1-3 seconds)."""
    import time
    time.sleep(random.uniform(1.0, 3.0))
```

### 7.4 Merge/Dedupe Strategy

**Merge Logic:** `app/services/realtime_overlay.py`

```python
def merge_problems_with_vista(icn: str, postgres_problems: list, vista_problems: list) -> list:
    """
    Merge PostgreSQL historical problems with VistA real-time problems.

    Strategy:
    - VistA problems with "updated_today" = True take precedence (T-0 data)
    - For active problems, prefer VistA if present (authoritative source)
    - Keep historical/resolved problems from PostgreSQL
    - Deduplicate by ICN + ICD-10 + Onset Date
    """
    merged = []
    vista_keys = set()

    # Add VistA problems first (priority)
    for vista_prob in vista_problems:
        key = (icn, vista_prob["icd10_code"], vista_prob["onset_date"])
        vista_keys.add(key)

        merged.append({
            **vista_prob,
            "data_source": "VistA (Real-Time)" if vista_prob["updated_today"] else "VistA",
            "is_real_time": vista_prob["updated_today"]
        })

    # Add PostgreSQL problems not in VistA
    for pg_prob in postgres_problems:
        key = (icn, pg_prob["icd10_code"], pg_prob["onset_date"])

        if key not in vista_keys:
            merged.append({
                **pg_prob,
                "data_source": "PostgreSQL (Historical)",
                "is_real_time": False
            })

    # Sort by onset date (most recent first), then by updated_today
    merged.sort(key=lambda x: (x.get("updated_today", False), x.get("onset_date", "")), reverse=True)

    return merged
```

---

## 8. UI Design

### 8.1 Dashboard Widget (2x1)

**Widget Size:** 2 columns × 1 row (half-width)

**Widget Content:**

```
┌────────────────────────────────────────────────────┐
│ 🩺 Problems (12 Active) | Charlson: 7 (Very High)  │
├────────────────────────────────────────────────────┤
│ 🫀 CHF - Acute on Chronic Systolic (I50.23)        │
│    • Onset: 2018-05-10 • Service Connected         │
│                                                     │
│ 🫁 COPD - Severe (J44.9)                           │
│    • Onset: 2015-08-01                             │
│                                                     │
│ 💉 Type 2 Diabetes with CKD (E11.22)               │
│    • Onset: 2016-01-05 • Service Connected         │
│                                                     │
│ 🧠 Major Depression, Recurrent (F33.1)             │
│    • Onset: 2019-06-15 • Service Connected         │
│                                                     │
│ 🦴 Osteoarthritis (M15.9)                          │
│    • Onset: 2014-03-10                             │
│                                                     │
│ [View All 12 Problems →]                           │
└────────────────────────────────────────────────────┘
```

**Features:**
- Shows top 5 active problems (by onset date, most recent first)
- Charlson Index badge (color-coded: 0-1=green, 2-3=yellow, 4-5=orange, 6+=red)
- Service-connected indicator
- Icons by category (Cardiovascular, Respiratory, Endocrine, Mental Health, Musculoskeletal)
- "View All" link to full page

### 8.2 Full Page View

**Route:** `/patient/{icn}/problems`

**Page Layout:**

```
┌──────────────────────────────────────────────────────────────────────┐
│ Patient: Dooree, Adam (ICN100001) | DOB: 1935-05-15 | Age: 89       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│ ┌─────────────────────────────────────────────────────────────┐     │
│ │ SUMMARY                                                      │     │
│ ├─────────────────────────────────────────────────────────────┤     │
│ │ Active Problems: 12  │  Resolved: 3  │  Inactive: 0         │     │
│ │ Charlson Index: 7 (Very High Risk)                          │     │
│ │                                                              │     │
│ │ Chronic Conditions:                                          │     │
│ │ ✓ CHF   ✓ COPD   ✓ CKD Stage 4   ✓ Diabetes (complicated)  │     │
│ │ ✓ Depression   ✓ PTSD   ✓ Osteoarthritis                   │     │
│ └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│ ┌─────────────────────────────────────────────────────────────┐     │
│ │ FILTERS & ACTIONS                                            │     │
│ ├─────────────────────────────────────────────────────────────┤     │
│ │ Status: [Active ▼] [Inactive] [Resolved]                    │     │
│ │ Category: [All Categories ▼]                                 │     │
│ │ Service Connected: [All] [SC Only]                           │     │
│ │ [🔄 Refresh VistA (Real-Time)]                              │     │
│ └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│ ┌─────────────────────────────────────────────────────────────┐     │
│ │ CARDIOVASCULAR (3 problems)                                  │     │
│ ├─────────────────────────────────────────────────────────────┤     │
│ │ 🫀 Acute on chronic systolic heart failure                  │     │
│ │    ICD-10: I50.23 | SNOMED: 42343007 | Status: Active       │     │
│ │    Onset: 2018-05-10 | Entered: 2018-05-15 | VistA          │     │
│ │    Charlson: CHF (1 point)                                   │     │
│ │    [View Details] [View Related Meds]                        │     │
│ │                                                              │     │
│ │ 🫀 Atrial fibrillation                                       │     │
│ │    ICD-10: I48.91 | SNOMED: 49601007 | Status: Active       │     │
│ │    Onset: 2019-02-20 | Entered: 2019-02-25 | VistA          │     │
│ │    [View Details] [View Related Meds]                        │     │
│ │                                                              │     │
│ │ 🫀 Old myocardial infarction  🏷️ Service Connected          │     │
│ │    ICD-10: I25.2 | SNOMED: 22298006 | Status: Resolved      │     │
│ │    Onset: 2017-03-15 | Resolved: 2017-05-01 | VistA         │     │
│ │    Charlson: MI (1 point)                                    │     │
│ │    [View Details]                                            │     │
│ └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│ ┌─────────────────────────────────────────────────────────────┐     │
│ │ RESPIRATORY (1 problem)                                      │     │
│ ├─────────────────────────────────────────────────────────────┤     │
│ │ 🫁 Chronic obstructive pulmonary disease                     │     │
│ │    ICD-10: J44.9 | SNOMED: 13645005 | Status: Active        │     │
│ │    Onset: 2015-08-01 | Entered: 2015-08-10 | VistA          │     │
│ │    Charlson: COPD (1 point)                                  │     │
│ │    [View Details] [View Related Meds]                        │     │
│ └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
│ [Continue for: ENDOCRINE, RENAL, MENTAL HEALTH, MUSCULOSKELETAL...] │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Features:**
- Summary card with active/resolved counts and Charlson Index
- Chronic condition badges (visual indicators)
- Grouped by ICD-10 category (Cardiovascular, Respiratory, etc.)
- Collapsible sections
- Service-connected indicator
- Charlson condition mapping shown
- "Refresh VistA" button for real-time overlay
- Filter by status, category, service-connected
- Links to related medications (future enhancement)

### 8.3 Problem Detail Modal

**Triggered by:** Clicking "View Details" on any problem

**Modal Content:**

```
┌──────────────────────────────────────────────────────┐
│ Problem Details: Acute on Chronic Systolic CHF       │
├──────────────────────────────────────────────────────┤
│                                                       │
│ CODING INFORMATION                                    │
│ • ICD-10: I50.23 (Acute on chronic systolic HF)      │
│ • SNOMED CT: 42343007 (Heart failure)                │
│ • ICD-9 (Legacy): 428.23                             │
│ • Category: Cardiovascular                           │
│                                                       │
│ STATUS & TIMELINE                                     │
│ • Status: Active                                      │
│ • Onset Date: 2018-05-10 (8 years ago)               │
│ • Entered: 2018-05-15 by Dr. Smith, John             │
│ • Last Modified: 2026-02-07 (today)                  │
│ • Never resolved                                      │
│                                                       │
│ CLINICAL SIGNIFICANCE                                 │
│ • Charlson Condition: Congestive Heart Failure       │
│ • Charlson Points: 1                                  │
│ • Priority: Chronic                                   │
│                                                       │
│ VA-SPECIFIC                                           │
│ • Service Connected: No                               │
│ • Facility: Alexandria VA Medical Center (508)       │
│                                                       │
│ COMMENTS                                              │
│ "Recent decompensation, seen in ED today. Patient    │
│  admitted for IV diuresis. EF 25% on last echo."     │
│                                                       │
│ DATA SOURCE                                           │
│ • System: VistA (Real-Time)                          │
│ • Last Updated: 2026-02-07 14:30:00                  │
│                                                       │
│ [Close]                                               │
└──────────────────────────────────────────────────────┘
```

---

## 9. API Endpoints

### 9.1 FastAPI Route Structure

**Router:** `app/routes/problems.py` (Pattern B - Dedicated router)

**Endpoints:**

#### 9.1.1 Widget API

```python
@router.get("/api/patient/{icn}/problems/widget")
async def get_problems_widget(icn: str, use_vista: bool = False):
    """
    Get top 5 active problems for dashboard widget.

    Query Parameters:
    - use_vista: If true, merge with VistA real-time data

    Returns:
    - Top 5 active problems
    - Charlson Index
    - Active problem count
    """
```

**Response:**
```json
{
  "icn": "ICN100001",
  "active_count": 12,
  "charlson_index": 7,
  "charlson_risk": "Very High",
  "problems": [
    {
      "problem_text": "Acute on chronic systolic heart failure",
      "icd10_code": "I50.23",
      "icd10_category": "Cardiovascular",
      "onset_date": "2018-05-10",
      "service_connected": false,
      "charlson_condition": "CHF",
      "charlson_points": 1,
      "is_real_time": false
    }
  ]
}
```

#### 9.1.2 Full Problem List API

```python
@router.get("/api/patient/{icn}/problems")
async def get_patient_problems(
    icn: str,
    status: str = "Active",  # Active, Inactive, Resolved, All
    category: str = None,  # Cardiovascular, Respiratory, etc.
    service_connected_only: bool = False,
    use_vista: bool = False
):
    """
    Get complete problem list with filtering.

    Query Parameters:
    - status: Filter by problem status
    - category: Filter by ICD-10 category
    - service_connected_only: Show only SC conditions
    - use_vista: Merge with VistA real-time data
    """
```

**Response:**
```json
{
  "icn": "ICN100001",
  "summary": {
    "active_count": 12,
    "inactive_count": 0,
    "resolved_count": 3,
    "charlson_index": 7,
    "charlson_risk": "Very High",
    "chronic_conditions": {
      "has_chf": true,
      "has_copd": true,
      "has_diabetes": true,
      "has_ckd": true,
      "has_depression": true,
      "has_ptsd": true
    }
  },
  "problems_by_category": {
    "Cardiovascular": [
      {
        "problem_id": 1001,
        "problem_text": "Acute on chronic systolic heart failure",
        "icd10_code": "I50.23",
        "icd10_description": "Acute on chronic systolic heart failure",
        "snomed_code": "42343007",
        "problem_status": "Active",
        "onset_date": "2018-05-10",
        "entered_datetime": "2018-05-15T10:30:00",
        "modified_datetime": "2026-02-07T14:30:00",
        "service_connected": false,
        "charlson_condition": "CHF",
        "charlson_points": 1,
        "source_system": "VistA",
        "is_real_time": true
      }
    ],
    "Respiratory": [...],
    "Endocrine": [...]
  }
}
```

#### 9.1.3 HTML Widget Endpoint

```python
@router.get("/patient/{icn}/problems/widget")
async def get_problems_widget_html(request: Request, icn: str):
    """Render HTML widget for HTMX insertion."""
    problems_data = get_problems_widget_data(icn)
    return templates.TemplateResponse(
        "widgets/problems_widget.html",
        {"request": request, "problems": problems_data}
    )
```

#### 9.1.4 Full Page Endpoint

```python
@router.get("/patient/{icn}/problems")
async def get_problems_page(request: Request, icn: str):
    """Render full problems page."""
    problems_data = get_patient_problems_grouped(icn)
    return templates.TemplateResponse(
        "patient_problems.html",
        get_base_context(request, problems=problems_data, active_page="problems")
    )
```

#### 9.1.5 VistA Refresh Endpoint (HTMX)

```python
@router.get("/patient/{icn}/problems/refresh-vista")
async def refresh_problems_vista(request: Request, icn: str):
    """
    Refresh problems with VistA real-time data.

    Returns: HTML fragment for HTMX OOB swap
    """
    # Get PostgreSQL problems
    pg_problems = get_patient_problems_db(icn)

    # Get VistA problems (multi-site query)
    vista_problems = get_vista_problems_multi_site(icn)

    # Merge/dedupe
    merged_problems = merge_problems_with_vista(icn, pg_problems, vista_problems)

    return templates.TemplateResponse(
        "partials/problems_list.html",
        {"request": request, "problems": merged_problems}
    )
```

---

## 10. AI Integration

### 10.1 AI Context Builder Updates

**File:** `ai/services/patient_context.py`

**New Method:**

```python
def get_problems_summary(self) -> str:
    """
    Get patient problems formatted as natural language text.

    Returns:
        Natural language problems summary with Charlson Index

    Example:
        "Active Problems (12):
         - Congestive Heart Failure (I50.23, onset 2018)
         - COPD (J44.9, onset 2015)
         - Diabetes Type 2 with CKD (E11.22, onset 2016, service-connected)
         - Major Depression (F33.1, onset 2019, service-connected)

         Charlson Comorbidity Index: 7 (Very High Risk)

         Chronic Conditions: CHF, COPD, CKD Stage 4, Diabetes with complications, Depression, PTSD"
    """
    from app.db.problems import get_patient_problems

    problems = get_patient_problems(self.icn)

    if not problems:
        return "No problem list on record"

    # Get active problems
    active = [p for p in problems if p['problem_status'] == 'Active']

    if not active:
        return "No active problems on record"

    text = f"Active Problems ({len(active)}):\n"

    # List top 10 active problems (sorted by onset, most recent first)
    for prob in sorted(active, key=lambda x: x.get('onset_date', ''), reverse=True)[:10]:
        prob_text = prob.get('problem_text', 'Unknown problem')
        icd10 = prob.get('icd10_code', '')
        onset = prob.get('onset_date', 'unknown')
        onset_year = onset[:4] if onset and onset != 'unknown' else 'unknown'

        text += f"- {prob_text}"
        if icd10:
            text += f" ({icd10}, onset {onset_year})"

        # Add service-connected indicator
        if prob.get('service_connected'):
            text += ", service-connected"

        text += "\n"

    # Add Charlson Index
    charlson = problems[0].get('charlson_index', 0) if problems else 0
    if charlson > 0:
        risk_level = "Very High Risk" if charlson >= 6 else "High Risk" if charlson >= 4 else "Moderate Risk"
        text += f"\nCharlson Comorbidity Index: {charlson} ({risk_level})"

    # Add chronic condition summary
    chronic_conditions = []
    if problems[0].get('has_chf'): chronic_conditions.append("CHF")
    if problems[0].get('has_copd'): chronic_conditions.append("COPD")
    if problems[0].get('has_ckd'): chronic_conditions.append("CKD")
    if problems[0].get('has_diabetes'): chronic_conditions.append("Diabetes")
    if problems[0].get('has_depression'): chronic_conditions.append("Depression")
    if problems[0].get('has_ptsd'): chronic_conditions.append("PTSD")

    if chronic_conditions:
        text += f"\n\nChronic Conditions: {', '.join(chronic_conditions)}"

    return text.strip()
```

**Update `build_comprehensive_summary()`:**

```python
def build_comprehensive_summary(self) -> str:
    """Build comprehensive patient summary including problems."""

    demographics = self.get_demographics_summary()
    problems = self.get_problems_summary()  # NEW
    medications = self.get_medication_summary()
    vitals = self.get_vitals_summary()
    allergies = self.get_allergies_summary()
    encounters = self.get_encounters_summary()
    notes = self.get_notes_summary()

    summary = f"""PATIENT DEMOGRAPHICS
{demographics}

ACTIVE PROBLEMS & CHRONIC CONDITIONS
{problems}

CURRENT MEDICATIONS
{medications}

RECENT VITALS (last 7 days)
{vitals}

ALLERGIES
{allergies}

RECENT ENCOUNTERS (last 90 days)
{encounters}

RECENT CLINICAL NOTES (last 90 days)
{notes}

Data sources: PostgreSQL (demographics, problems, medications, vitals, allergies, encounters, clinical_notes)"""

    return summary
```

### 10.2 AI Tool: Disease Burden Assessment

**New LangGraph Tool:**

```python
@tool
def assess_disease_burden(patient_icn: str) -> str:
    """
    Assess patient's disease burden based on problem list and comorbidities.

    Analyzes:
    - Charlson Comorbidity Index
    - Number of active problems
    - Chronic condition complexity
    - Service-connected conditions

    Args:
        patient_icn: Patient ICN

    Returns:
        Natural language disease burden assessment
    """
    from app.db.problems import get_patient_problems

    problems = get_patient_problems(patient_icn)

    if not problems:
        return "No problem list available for disease burden assessment"

    # Extract key metrics
    active_count = sum(1 for p in problems if p['problem_status'] == 'Active')
    charlson = problems[0].get('charlson_index', 0)

    # Assess complexity
    if charlson >= 6 and active_count >= 10:
        burden = "Very High - Patient has severe multi-morbidity with significant mortality risk"
    elif charlson >= 4 or active_count >= 8:
        burden = "High - Multiple chronic conditions requiring coordinated care"
    elif charlson >= 2 or active_count >= 5:
        burden = "Moderate - Several chronic conditions, manageable with good care coordination"
    else:
        burden = "Low - Limited comorbidity burden"

    # Build detailed assessment
    assessment = f"""Disease Burden Assessment:

Overall Burden: {burden}

Key Metrics:
- Active Problems: {active_count}
- Charlson Index: {charlson} (mortality predictor)

Clinical Implications:
"""

    # Add specific clinical implications
    if problems[0].get('has_chf') and problems[0].get('has_ckd'):
        assessment += "- Cardiorenal syndrome risk: CHF + CKD requires careful fluid/medication management\n"

    if problems[0].get('has_diabetes') and problems[0].get('has_ckd'):
        assessment += "- Diabetic nephropathy: Close glucose control and nephroprotection critical\n"

    if problems[0].get('has_copd') and problems[0].get('has_chf'):
        assessment += "- Respiratory-cardiac interaction: Dyspnea management challenging, exacerbation risk\n"

    if problems[0].get('has_ptsd') or problems[0].get('has_depression'):
        assessment += "- Mental health comorbidity: May affect medication adherence and self-care\n"

    # Service-connected conditions
    sc_count = sum(1 for p in problems if p.get('service_connected') and p['problem_status'] == 'Active')
    if sc_count > 0:
        assessment += f"\n{sc_count} active service-connected conditions - Eligible for VA benefits and care coordination\n"

    return assessment.strip()
```

### 10.3 System Prompt Updates

**File:** `ai/prompts/system_prompts.py`

**Update Tool Description:**

```python
1. **get_patient_summary** - Retrieve comprehensive patient clinical summary
   - Returns: Demographics (including SC%, environmental exposures), **active problems/diagnoses**, Charlson Index, medications, vitals, allergies, encounters, recent clinical notes (last 3)
   - Problem list includes: ICD-10 codes, chronic conditions (CHF, COPD, diabetes, CKD), comorbidity burden
   - Use for: General overview questions, "tell me about this patient", initial context, disease burden assessment
   - Example queries: "What conditions does this patient have?", "What's the Charlson score?", "What chronic diseases?"

2. **assess_disease_burden** - Analyze patient comorbidity complexity
   - Parameters: patient_icn
   - Returns: Disease burden assessment (low/moderate/high/very high), clinical implications, Charlson Index interpretation
   - Use for: Risk stratification, care coordination prioritization, readmission risk assessment
   - Example queries: "How complex is this patient?", "What's the disease burden?", "Is this a high-risk patient?"
```

**Add Clinical Safety Priority:**

```python
Clinical Safety Priorities:
1. **Drug interactions**: Always flag Major/Severe DDI risks prominently
2. **Vital sign abnormalities**: Note critical values (e.g., BP >180/110, HR >120 or <50)
3. **Allergy conflicts**: Mention if medications conflict with documented allergies
4. **Environmental exposures**: Consider exposure-related health risks
5. **Disease burden**: High Charlson score (≥6) + polypharmacy = readmission risk
6. **Chronic disease management**: Flag gaps in care (no HbA1c for diabetics, no echo for CHF)
7. **Care gaps**: Identify missing screenings, overdue follow-ups
8. **Polypharmacy**: Note if patient on 10+ medications
```

---

## 11. Implementation Roadmap

### Progress Summary (as of 2026-02-07)

**✅ Completed Phases:**
- **Phase 1:** Mock Data & Schema (3 tables in CDWWork, 1 in CDWWork2, 50 ICD-10 codes, 63 Charlson mappings, 73 problem records)
- **Phase 2:** ETL Pipeline (Bronze → Silver → Gold → PostgreSQL, Charlson Index calculation, 15 chronic condition flags)

**🔄 Next Phase:**
- **Phase 3:** VistA RPC Integration (ORQQPL LIST mock data with T-notation dates)

**📊 Current Status:**
- **PostgreSQL:** 72 problems loaded, 7 patients, Charlson Index operational
- **Multi-Source:** VistA (55) + Cerner (17) harmonized successfully
- **Chronic Conditions:** 15 boolean flags populated (CHF, diabetes, COPD, CKD, hypertension, PTSD, etc.)
- **Data Quality:** 1 duplicate removed, all deduplication rules working
- **Metadata:** Audit trail timestamps (silver_load_datetime, gold_load_datetime) in place

**🔧 Implementation Notes:**
- **Schema Alignment:** ETL scripts required updates to match actual SQL Server schema (not all designed columns were implemented)
- **Charlson Weights:** Loaded from separate `Dim.CharlsonMapping` table in Gold layer (not included in ICD-10 dimension)
- **Cerner Naming:** `DiagnosisSID` used instead of `ProblemSID`, status codes are single characters (A/I/R) instead of full words
- **Deduplication Rule:** Same ICN + Same ICD-10 Code + Same Onset Date = Duplicate (VistA preferred when conflict)
- **Documentation Updated:** Both PostgreSQL and SQL Server reference guides updated to reflect new tables

**⏱️ Time Estimate for Remaining Work:**
- Phase 3 (VistA RPC): 2 days
- Phase 4 (Database Query Layer): 1 day
- Phase 5 (UI Implementation): 4 days
- Phase 6 (AI Integration): 2 days
- Phase 7 (Documentation & Testing): 1 day
- **Total Remaining:** ~10 days

---

### 11.1 Phase 1: Mock Data & Schema (Days 1-3) ✅ **COMPLETE**

**Day 1: CDW Schema Design** ✅
- [x] Create `Outpat.ProblemList` table in CDWWork
- [x] Create `Dim.ICD10`, `Dim.CharlsonMapping` tables (ICD9 deferred)
- [x] Create `EncMill.ProblemList` table in CDWWork2
- [x] Write CREATE scripts in `mock/sql-server/cdwwork/create/`

**Day 2: Dimension Data Population** ✅
- [x] Populate `Dim.ICD10` with 50 common ICD-10 codes
- [x] Populate `Dim.CharlsonMapping` with 19 CCI conditions (63 ICD-10 mappings)
- [x] Write INSERT scripts in `mock/sql-server/cdwwork/insert/`

**Day 3: Test Patient Problem Lists** ✅
- [x] Generated 73 problem records across 7 test patients (focused dataset)
- [x] Age-stratified distribution with diverse diagnoses
- [x] Multiple Charlson conditions represented (CHF, diabetes, COPD, CKD, PTSD, etc.)
- [x] Included active (67), inactive (2), and resolved (3) problems
- [x] Write INSERT scripts for `Outpat.ProblemList` (55 records) and `EncMill.ProblemList` (18 records)
- [x] Update `_master.sql` scripts

**Verification:** ✅ **PASSED**
```bash
# Actual Results (2026-02-07):
# - Outpat.ProblemList: 55 records
# - EncMill.ProblemList: 18 records
# - Dim.ICD10: 50 codes
# - Dim.CharlsonMapping: 63 mappings
# - All tables populated successfully
```

---

### 11.2 Phase 2: ETL Pipeline (Days 4-7) ✅ **COMPLETE**

**Day 4: Bronze Extraction** ✅
- [x] Create `etl/bronze_problems.py`
- [x] Extract `Outpat.ProblemList` → `bronze/cdwwork/outpat_problemlist/outpat_problemlist_raw.parquet`
- [x] Extract `Dim.ICD10` → `bronze/cdwwork/icd10_dim/icd10_dim_raw.parquet`
- [x] Extract `Dim.CharlsonMapping` → `bronze/cdwwork/charlson_mapping/charlson_mapping_raw.parquet`
- [x] Extract `EncMill.ProblemList` → `bronze/cdwwork2/encmill_problemlist/encmill_problemlist_raw.parquet`
- [x] Test extraction: `python -m etl.bronze_problems` ✅ **PASSED**

**Day 5: Silver Harmonization** ✅
- [x] Create `etl/silver_problems.py`
- [x] Harmonize VistA + Cerner schemas (ProblemSID/DiagnosisSID → problem_id)
- [x] Schema harmonization: status codes (ACTIVE/A → Active), boolean flags (Y/N → True/False)
- [x] Join with ICD-10 codes for descriptions and categories
- [x] Deduplicate (ICN + ICD-10 + Onset Date) - Removed 1 duplicate, retained 72 unique
- [x] Test: `python -m etl.silver_problems` ✅ **PASSED**

**Day 6: Gold Transformation & Charlson Calculation** ✅
- [x] Create `etl/gold_problems.py`
- [x] Calculate Charlson Index per patient (join with `Dim.CharlsonMapping`)
- [x] Flag 15 chronic conditions (CHF, CAD, AFib, hypertension, COPD, asthma, diabetes, hyperlipidemia, CKD, depression, PTSD, anxiety, cancer, osteoarthritis, back pain)
- [x] Calculate patient-level aggregations (active/inactive/resolved counts, chronic problem count, service-connected count)
- [x] Add metadata timestamps (silver_load_datetime, gold_load_datetime, schema versions)
- [x] Test: `python -m etl.gold_problems` ✅ **PASSED**
  - **Results:** Charlson Index distribution: Min=0, Max=7, Mean=3.14, Median=1.0
  - **Patients:** 3 with no comorbidities, 1 low (1-2), 3 high (5+)

**Day 7: PostgreSQL Load** ✅
- [x] Create `db/ddl/create_patient_problems_table.sql`
- [x] Run DDL script to create tables
- [x] Create `etl/load_problems.py`
- [x] Load Gold data to PostgreSQL
- [x] Write verification queries (counts, Charlson distribution, chronic condition flags)
- [x] Test: `python -m etl.load_problems` ✅ **PASSED**
  - **Loaded:** 72 problem records, 7 patients
  - **Status:** 67 active, 2 inactive, 3 resolved
  - **Chronic Conditions:** CHF=2, Diabetes=4, COPD=3, CKD=3, Hypertension=6, PTSD=4
- [x] Update `scripts/run_all_etl.sh`

**Verification:** ✅ **PASSED**
```bash
# Actual Results (2026-02-07):
# - Total problems: 72
# - Patients with problems: 7
# - Active problems: 67, Inactive: 2, Resolved: 3
# - Charlson Index: Min=0, Max=7, Mean=3.14, Median=1.0
# - Top ICD-10 categories: Cardiovascular (18), Endocrine (12), Respiratory (6)
# - Chronic conditions: CHF=2, Diabetes=4, COPD=3, CKD=3, Hypertension=6, PTSD=4
# - Service-connected problems: 25
# - Multi-source: VistA=55, Cerner=17 (1 duplicate removed)
# - All 15 chronic condition flags operational
# - Metadata timestamps: silver_load_datetime, gold_load_datetime populated
```

---

### 11.3 Phase 3: VistA RPC Integration (Days 8-9) 🔄 **NEXT PHASE**

**Day 8: Mock VistA Data**
- [ ] Create `vista/data/problems/` directory
- [ ] Generate JSON files for 10 test patients (3 sites each = 30 files)
- [ ] Include "updated_today" flags for T-0 problems
- [ ] Use T-notation for dates (T-0, T-30, T-365, etc.)

**Day 9: RPC Implementation**
- [ ] Create `vista/app/rpcs/problems.py`
- [ ] Implement `execute_orqqpl_list(site, icn)`
- [ ] Add RPC route in `vista/app/main.py`
- [ ] Test RPC: `curl http://localhost:8003/rpc/execute?site=200&icn=ICN100001 -d '{"rpc_name": "ORQQPL LIST"}'`
- [ ] Create `app/services/vista_client.py::get_vista_problems_multi_site(icn)`
- [ ] Implement merge/dedupe in `app/services/realtime_overlay.py::merge_problems_with_vista()`
- [ ] Test multi-site merge logic

**Verification:**
```bash
# Test VistA RPC
curl -X POST http://localhost:8003/rpc/execute \
  -H "Content-Type: application/json" \
  -d '{
    "rpc_name": "ORQQPL LIST",
    "parameters": {"site": 200, "icn": "ICN100001"}
  }'

# Expect JSON response with 12 problems, some with "updated_today": true
```

---

### 11.4 Phase 4: Database Query Layer (Day 10)

**Day 10: Query Functions**
- [ ] Create `app/db/problems.py`
- [ ] Implement `get_patient_problems(icn, status='Active', category=None)`
- [ ] Implement `get_problems_summary(icn)` (widget data)
- [ ] Implement `get_problems_grouped_by_category(icn)`
- [ ] Implement `get_charlson_score(icn)`
- [ ] Test all functions with test patients
- [ ] Create `scripts/test_problems_queries.py` (verification script)

**Verification:**
```python
# scripts/test_problems_queries.py
from app.db.problems import get_patient_problems, get_charlson_score

# Test patient with high Charlson score
problems = get_patient_problems("ICN100001")
assert len(problems) >= 10, "Expected 10+ problems for ICN100001"

charlson = get_charlson_score("ICN100001")
assert charlson >= 6, f"Expected Charlson ≥6, got {charlson}"
```

---

### 11.5 Phase 5: UI Implementation (Days 11-14)

**Day 11: Dashboard Widget**
- [ ] Create `app/templates/widgets/problems_widget.html`
- [ ] Implement widget API endpoint in `app/routes/problems.py`
- [ ] Add widget to dashboard grid in `app/templates/patient_dashboard.html`
- [ ] Test widget display with test patients
- [ ] Verify Charlson badge color-coding (green/yellow/orange/red)

**Day 12: Full Page View**
- [ ] Create `app/templates/patient_problems.html`
- [ ] Implement grouped display (Cardiovascular, Respiratory, etc.)
- [ ] Add filters (status, category, service-connected)
- [ ] Implement collapsible sections
- [ ] Add "View Details" modal trigger
- [ ] Test full page with test patients

**Day 13: Problem Detail Modal & VistA Refresh**
- [ ] Create `app/templates/modals/problem_detail_modal.html`
- [ ] Implement modal API endpoint
- [ ] Add "Refresh VistA" button (HTMX)
- [ ] Implement VistA refresh endpoint (merge/dedupe + OOB swap)
- [ ] Test real-time overlay functionality

**Day 14: CSS & Polish**
- [ ] Add category icons (🫀 🫁 💉 🧠 🦴)
- [ ] Style Charlson badge (color-coded by risk)
- [ ] Add service-connected indicator styling
- [ ] Test responsive design
- [ ] Test accessibility (keyboard navigation, screen readers)

**Verification:**
```bash
# Start app
uvicorn app.main:app --reload

# Test URLs
http://localhost:8000/patient/ICN100001/problems  # Full page
http://localhost:8000/  # Dashboard with widget

# Test "Refresh VistA" button (inspect network tab for HTMX request)
```

---

### 11.6 Phase 6: AI Integration (Days 15-16)

**Day 15: Context Builder**
- [ ] Update `ai/services/patient_context.py`
- [ ] Add `get_problems_summary()` method
- [ ] Update `build_comprehensive_summary()` to include problems
- [ ] Test with AI Insight page: "What conditions does this patient have?"

**Day 16: Disease Burden Tool**
- [ ] Create `ai/tools/disease_burden.py`
- [ ] Implement `assess_disease_burden(icn)` tool
- [ ] Register tool with LangGraph agent
- [ ] Update system prompt in `ai/prompts/system_prompts.py`
- [ ] Test queries: "How complex is this patient?", "What's the disease burden?"

**Verification:**
```bash
# Test AI queries
http://localhost:8000/insight

# Select patient ICN100001 (Charlson 7, high complexity)
# Ask: "What conditions does this patient have?"
# Expected: List of 12 active problems with Charlson Index 7

# Ask: "Assess the disease burden for this patient"
# Expected: Very High burden assessment with clinical implications
```

---

### 11.7 Phase 7: Documentation & Testing (Day 17)

**Day 17: Final Documentation**
- [ ] Update `docs/guide/developer-setup-guide.md` with Problems pipeline
- [ ] Update `app/README.md` with Problems API patterns
- [ ] Create `docs/spec/problems-implementation-summary.md`
- [ ] Update `docs/spec/med-z1-implementation-roadmap.md` (mark Problems as complete)
- [ ] Write unit tests for Charlson calculation logic
- [ ] Write integration tests for ETL pipeline
- [ ] Create demo video/screenshots

**Final Verification:**
```bash
# Run complete pipeline
./scripts/run_all_etl.sh

# Verify all components
1. SQL Server: ~400 problems in CDWWork
2. MinIO: Bronze/Silver/Gold Parquet files exist
3. PostgreSQL: ~400 problems in clinical.patient_problems
4. VistA: RPC returns problems with T-0 data
5. UI: Dashboard widget shows top 5 problems
6. UI: Full page displays grouped problems
7. UI: "Refresh VistA" merges real-time data
8. AI: "What conditions does this patient have?" returns problem list
9. AI: "Assess disease burden" returns complexity analysis
```

---

## 12. Appendices

### 12.1 ICD-10 Chapter Mapping

**Complete ICD-10 Chapter List:**

| Chapter | Code Range | Category Name |
|---------|-----------|---------------|
| I | A00-B99 | Infectious diseases |
| II | C00-D49 | Neoplasms |
| III | D50-D89 | Blood/immune disorders |
| IV | E00-E89 | Endocrine/metabolic |
| V | F00-F99 | Mental/behavioral |
| VI | G00-G99 | Nervous system |
| VII | H00-H59 | Eye diseases |
| VIII | H60-H95 | Ear diseases |
| IX | I00-I99 | Cardiovascular |
| X | J00-J99 | Respiratory |
| XI | K00-K95 | Digestive |
| XII | L00-L99 | Skin diseases |
| XIII | M00-M99 | Musculoskeletal |
| XIV | N00-N99 | Genitourinary |
| XV | O00-O9A | Pregnancy/childbirth |
| XVI | P00-P96 | Perinatal conditions |
| XVII | Q00-Q99 | Congenital abnormalities |
| XVIII | R00-R99 | Symptoms/signs |
| XIX | S00-T88 | Injury/poisoning |
| XX | V00-Y99 | External causes |
| XXI | Z00-Z99 | Health services contact |

### 12.2 Charlson Condition Reference

**Quick Reference Card for CCI:**

```
1 POINT (10 conditions):
- Myocardial Infarction (I21, I22, I25.2)
- Congestive Heart Failure (I50, I09.9, I11.0, I13.0, I42, I43)
- Peripheral Vascular Disease (I70, I71, I73, I77.1, K55)
- Cerebrovascular Disease (G45, G46, I60-I69)
- Dementia (F00-F03, G30, G31.1)
- COPD (J40-J47, J60-J67, J68.4, J70)
- Connective Tissue Disease (M05, M06, M31.5, M32-M35)
- Peptic Ulcer Disease (K25-K28)
- Mild Liver Disease (B18, K70, K73, K74, K76)
- Diabetes Uncomplicated (E08-E13 without end-organ damage)

2 POINTS (6 conditions):
- Hemiplegia/Paraplegia (G04.1, G11.4, G80-G83)
- Moderate/Severe Renal Disease (I12.0, N18.3-N18.5, N19, Z94.0)
- Diabetes Complicated (E08-E13 with end-organ damage: .2-.5)
- Malignancy (C00-C76, C81-C85, C88, C90-C97)
- Leukemia (C91-C95)
- Lymphoma (C81-C85, C88, C96)

3 POINTS (1 condition):
- Moderate/Severe Liver Disease (I85, K70.4, K71.1, K72, K76.5-K76.7)

6 POINTS (2 conditions):
- Metastatic Solid Tumor (C77-C80)
- AIDS (B20-B24)

INTERPRETATION:
0-1 = Low burden (12% 1-year mortality)
2-3 = Moderate burden (26% 1-year mortality)
4-5 = High burden (52% 1-year mortality)
≥6 = Very high burden (85% 1-year mortality)
```

### 12.3 Test Patient Reference

**Key Test Patients for Problems Domain:**

| ICN | Name | Age | Active Problems | Charlson | Key Conditions |
|-----|------|-----|----------------|----------|----------------|
| ICN100001 | Dooree, Adam | 89 | 12 | 7 | CHF, COPD, CKD-4, DM w/ CKD, PTSD, depression |
| ICN100007 | Amajor, Adam | 75 | 8 | 5 | POW, PTSD, depression (all SC), MI, HTN |
| ICN100010 | Aminor, Alexander | 68 | 10 | 6 | DM, CKD-4, HTN, Gulf War exposure |
| ICN100002 | Miifaa, Barry | 55 | 7 | 3 | Gulf War, DM, HTN, OSA |
| ICN100005 | Dooree, Edward | 35 | 3 | 1 | HTN, DM, low back pain (simple case) |

**Use Cases:**
- **High Complexity:** ICN100001 (Charlson 7, 12 problems) - Test disease burden assessment, readmission risk
- **Service-Connected:** ICN100007 (POW, all problems SC) - Test SC filtering, military history integration
- **Simple Case:** ICN100005 (Charlson 1, 3 problems) - Test low-complexity patient display

### 12.4 SQL Verification Queries

**Useful Queries for Testing:**

```sql
-- 1. Charlson Distribution
SELECT
    charlson_index,
    COUNT(*) as patient_count,
    ROUND(AVG(active_problem_count), 1) as avg_problems
FROM clinical.patient_problems
WHERE charlson_index IS NOT NULL
GROUP BY charlson_index
ORDER BY charlson_index;

-- 2. Top 10 Most Common Problems
SELECT
    icd10_code,
    icd10_description,
    COUNT(*) as patient_count
FROM clinical.patient_problems
WHERE problem_status = 'Active'
GROUP BY icd10_code, icd10_description
ORDER BY patient_count DESC
LIMIT 10;

-- 3. Service-Connected Conditions
SELECT
    icd10_category,
    COUNT(*) as sc_problem_count
FROM clinical.patient_problems
WHERE service_connected = TRUE AND problem_status = 'Active'
GROUP BY icd10_category
ORDER BY sc_problem_count DESC;

-- 4. Chronic Condition Prevalence
SELECT
    'CHF' as condition, SUM(CASE WHEN has_chf THEN 1 ELSE 0 END) as count
FROM clinical.patient_problems
WHERE active_problem_count > 0
UNION ALL
SELECT 'COPD', SUM(CASE WHEN has_copd THEN 1 ELSE 0 END)
FROM clinical.patient_problems
WHERE active_problem_count > 0
UNION ALL
SELECT 'Diabetes', SUM(CASE WHEN has_diabetes THEN 1 ELSE 0 END)
FROM clinical.patient_problems
WHERE active_problem_count > 0
UNION ALL
SELECT 'CKD', SUM(CASE WHEN has_ckd THEN 1 ELSE 0 END)
FROM clinical.patient_problems
WHERE active_problem_count > 0
UNION ALL
SELECT 'Depression', SUM(CASE WHEN has_depression THEN 1 ELSE 0 END)
FROM clinical.patient_problems
WHERE active_problem_count > 0
UNION ALL
SELECT 'PTSD', SUM(CASE WHEN has_ptsd THEN 1 ELSE 0 END)
FROM clinical.patient_problems
WHERE active_problem_count > 0;

-- 5. Problems by Category
SELECT
    icd10_category,
    COUNT(*) as problem_count,
    COUNT(DISTINCT patient_key) as patient_count
FROM clinical.patient_problems
WHERE problem_status = 'Active'
GROUP BY icd10_category
ORDER BY problem_count DESC;
```

---

## Document End

**Version History:**
- v1.0 (2026-02-07): Initial design specification

**Next Steps:**
1. Review and approve design
2. Begin Phase 1 implementation (Mock Data & Schema)
3. Proceed through implementation roadmap sequentially

**Questions or Clarifications:**
Contact: med-z1 development team
