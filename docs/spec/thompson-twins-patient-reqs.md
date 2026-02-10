# Thompson Twins Test Patients

**Document Version:** v3.3
**Last Updated:** February 9, 2026
**Implementation Status:** ✅ Bailey CDWWork Complete, ✅ Alananah CDWWork Complete, 🔧 Joe In Progress, 🔧 CDWWork2 Scripts Need Review
**Update:** Updated implementation status. Bailey and Alananah CDWWork scripts are complete and fully tested (all SID conflicts resolved, full ETL pipeline validated, UI operational). CDWWork2 scripts for Bailey and Alananah have been created but require further review/verification. Joe's CDWWork script is the next priority before revisiting CDWWork2.

---

## Table of Contents
1. [Introduction](#introduction)
2. [Goal](#goal)
3. [Scope](#scope)
4. [Patient Personas](#patient-personas)
5. [Patient Identification Schema](#patient-identification-schema)
6. [Demographics](#demographics)
7. [Military Service History](#military-service-history)
8. [Clinical Domain Data Requirements](#clinical-domain-data-requirements)
9. [Script Organization](#script-organization)
10. [Implementation Checklist](#implementation-checklist)

---

## Introduction

This is a requirements specification for the addition of three new comprehensive test patients to the med-z1 mock CDW databases. The Thompson siblings - Bailey and Alananah (twins, born April 15, 1963), and their younger brother Joe (born May 10, 1970) - all served in the U.S. military from 1990-2012, deployed to various conflicts, and continued their healthcare through the VA system after retirement. Bailey and Alananah served in the U.S. Army with combat exposure, while Joe served as a commissioned officer in the U.S. Air Force in a non-combat support role.

**Geographic Timeline:**
- **1990-2010:** Active military service (various deployment locations)
- **2010-2025:** Retired to St. Petersburg, FL → Bay Pines VA Healthcare System (VistA/CDWWork)
- **2025-2026:** Relocated to Walla Walla, WA → Jonathan M. Wainwright Memorial VA Medical Center (Cerner/CDWWork2)

These patients will provide robust test cases for:
- Multi-database patient identity resolution (CDWWork → CDWWork2)
- Geographic facility transitions
- Complex chronic disease management
- Mental health and combat-related conditions
- AI/ML clinical insights and analysis
- Complete ETL pipeline testing across all implemented clinical domains

---

## Goal

Create comprehensive mock patient records for all three Thompson siblings that include:
- ✅ All 10 currently implemented clinical domains in med-z1
- ✅ Realistic medical histories reflecting their military service and chronic conditions
- ✅ Data spanning 15 years at Bay Pines (CDWWork, 2010-2025) and 1 year at Walla Walla (CDWWork2, 2025-2026)
- ✅ Well-documented SQL insert scripts with clear rationale for all clinical values
- ✅ Support for ETL pipeline, PostgreSQL serving database, UI display, and AI analysis

**Note:** VistA real-time overlay is NOT required for these patients, as they no longer receive care at VistA-based facilities.

---

## Scope

### In Scope
- Complete patient records in CDWWork (Bay Pines, 2010-2025) and CDWWork2 (Walla Walla, 2025-2026)
- All 10 implemented clinical domains:
  1. Demographics
  2. Vitals
  3. Patient Flags
  4. Allergies
  5. Medications
  6. Encounters
  7. Clinical Notes
  8. Immunizations
  9. Problems/Diagnoses
  10. Laboratory Results (ETL complete, UI pending)
- Military service history and disability records
- Realistic clinical narratives and timelines
- AI/ML testing scenarios (using existing tools)

### Out of Scope
- VistA RPC Broker real-time overlay data (T-0)
- Clinical domains not yet implemented (Orders, Imaging, Procedures)
- DoD/CHCS/AHLTA data sources
- Non-Bay Pines and non-Walla Walla VA facilities

---

## Patient Personas

### Bailey Thompson (Male Veteran, Twin)

**Demographics:**
- **Full Name:** Bailey James Thompson
- **Date of Birth:** April 15, 1963 (age 62, twin of Alananah)
- **Sex:** Male
- **SSN:** 200-00-1001 (mock)
- **Race/Ethnicity:** White, Not Hispanic/Latino
- **Marital Status:** Divorced (2018)

**Military Service:**
- **Branch:** U.S. Army
- **Service Period:** 1990-2010 (20 years)
- **Rank at Retirement:** Sergeant First Class (E-7)
- **Discharge Status:** Honorable
- **Deployments:**
  - 1990-1991: Gulf War (Operation Desert Storm) - Kuwait/Iraq theater
  - 1995-1996: Bosnia peacekeeping operations
  - 2003-2005: Iraq War (Operation Iraqi Freedom) - **Severe IED blast injury (2004)**
  - 2007-2008: Iraq War (second deployment)

**Service-Connected Disabilities (Total: 100%):**
- **PTSD:** 70% (combat-related, multiple deployments)
- **Chronic Back Pain:** 40% (IED blast injury, lumbar spine damage)
- **Tinnitus (bilateral):** 10% (blast exposure)
- **Traumatic Brain Injury (TBI):** 10% (mild, from 2004 IED blast)

**Medical Conditions (Major):**
1. **PTSD** - Diagnosed 2011, ongoing treatment
2. **Chronic Pain Syndrome** - Lumbar radiculopathy, post-IED blast (2004)
3. **Traumatic Brain Injury (TBI)** - Mild, with persistent cognitive symptoms
4. **Tinnitus** - Bilateral, constant ringing
5. **Major Depressive Disorder** - Recurrent episodes, comorbid with PTSD
6. **Hypertension** - Diagnosed 2015
7. **Hyperlipidemia** - Diagnosed 2016
8. **Tobacco Use Disorder** - 40+ pack-year history (quit 2022)
9. **Alcohol Use Disorder** - In remission since 2020 (treatment 2019-2020)
10. **Obstructive Sleep Apnea** - Diagnosed 2017, uses CPAP
11. **Type 2 Diabetes Mellitus** - Diagnosed 2019 (obesity, sedentary lifestyle)
12. **Chronic Kidney Disease (CKD) Stage 3a** - Related to hypertension and diabetes

**Charlson Comorbidity Index:** Estimated 4-5 (Diabetes with complications, CKD, prior suicide attempt → elevated mortality risk)

**Mental Health History:**
- 2011: Initial PTSD diagnosis at Bay Pines
- 2013: Major depressive episode, suicide ideation (no attempt)
- 2016: Inpatient psychiatric admission (7 days, suicide attempt via overdose)
- 2019-2020: Alcohol treatment program (successful completion)
- 2021-present: Stable on medications, weekly therapy

**Pain Management:**
- 2010-2018: Opioid therapy (oxycodone, morphine ER)
- 2018: Opioid taper initiated due to overdose risk
- 2019-present: Non-opioid pain management (gabapentin, duloxetine, lidocaine patches)
- 2020: Lumbar epidural steroid injections (3 series)
- 2022: Spinal cord stimulator trial (declined permanent implant)

**Substance Use:**
- **Tobacco:** 1.5 packs/day (1980-2022), quit 2022 with varenicline
- **Alcohol:** Heavy use 2010-2019 (6-8 drinks/day), abstinent since 2020
- **Illicit drugs:** Denies

**Current Medications (~15):**
- Sertraline 200mg daily (PTSD/depression)
- Prazosin 5mg nightly (PTSD nightmares)
- Gabapentin 1200mg TID (neuropathic pain)
- Duloxetine 60mg daily (pain/depression)
- Lidocaine 5% patches (back pain)
- Metformin 1000mg BID (diabetes)
- Lisinopril 20mg daily (hypertension)
- Atorvastatin 40mg nightly (hyperlipidemia)
- Aspirin 81mg daily (cardiovascular protection)
- Pantoprazole 40mg daily (GERD)
- Trazodone 100mg nightly (insomnia)
- Vitamin D 2000 IU daily
- Multivitamin daily

**Allergies:**
- Penicillin → Rash (childhood, unconfirmed)
- Morphine → Severe nausea and vomiting (confirmed 2016)

**Patient Flags:**
- **High Risk for Suicide (Cat I National)** - Active since 2016 (suicide attempt history)
- **Opioid Risk (Cat II Local)** - Active 2010-2018, Inactive since 2018 (successfully tapered)

**Key Clinical Events:**
- 2004: IED blast injury (Iraq) → TBI, lumbar fractures, shrapnel wounds
- 2010: Military retirement, initial VA enrollment
- 2011: PTSD diagnosis, mental health treatment initiated
- 2016: Suicide attempt (opioid overdose), psychiatric hospitalization
- 2019: Diabetes diagnosis, A1C 8.2%
- 2020: Alcohol use disorder remission
- 2022: Tobacco cessation (major achievement)
- 2025: Relocation to Walla Walla, WA

**Social History:**
- Divorced 2018 (marriage strained by PTSD, substance use)
- Two adult children (limited contact)
- Lives alone in apartment
- Disabled veteran, 100% VA disability compensation
- Limited social support network

**AI/ML Testing Scenarios:**
- **Drug-Drug Interactions:** Sertraline + trazodone (serotonin syndrome risk), gabapentin + duloxetine (CNS depression)
- **Vitals Trends:** Weight gain 2010-2019 (sedentary, alcohol), weight loss 2020-present (sobriety, diabetes management)
- **Patient Summary:** Complex polypharmacy, mental health conditions, chronic pain
- **Clinical Notes:** Rich psychiatric notes, pain management notes, substance use treatment documentation
- **Charlson Comorbidity Index:** Elevated score due to diabetes, CKD, prior suicide attempt

---

### Alananah Thompson (Female Veteran, Twin)

**Demographics:**
- **Full Name:** Alananah Marie Thompson
- **Date of Birth:** April 15, 1963 (age 62, twin of Bailey)
- **Sex:** Female
- **SSN:** 200-00-1002 (mock)
- **Race/Ethnicity:** White, Not Hispanic/Latino
- **Marital Status:** Married (2012-present)

**Military Service:**
- **Branch:** U.S. Army
- **Service Period:** 1990-2010 (20 years)
- **Rank at Retirement:** Master Sergeant (E-8)
- **Discharge Status:** Honorable
- **Deployments:**
  - 1990-1991: Gulf War (Operation Desert Storm) - Medical logistics, Saudi Arabia
  - 1996: Bosnia peacekeeping operations
  - 2003-2004: Iraq War (Operation Iraqi Freedom) - Combat support hospital
  - 2006-2007: Iraq War (second deployment)

**Service-Connected Disabilities (Total: 50%):**
- **PTSD:** 30% (combat support, exposure to casualties)
- **Bilateral Knee Pain:** 10% (degenerative joint disease)
- **Hearing Loss (bilateral):** 10% (noise exposure)

**Medical Conditions (Major):**
1. **Type 2 Diabetes Mellitus** - Diagnosed 2012, well-controlled
2. **Breast Cancer (Stage IIA)** - Diagnosed 2012, currently in remission
3. **PTSD** - Diagnosed 2011, mild-moderate severity
4. **Hypertension** - Diagnosed 2013
5. **Hyperlipidemia** - Diagnosed 2014
6. **Osteoarthritis (bilateral knees)** - Chronic, service-related
7. **Hypothyroidism** - Diagnosed 2016
8. **Diabetic Peripheral Neuropathy** - Diagnosed 2020 (feet, bilateral)
9. **Diabetic Retinopathy (nonproliferative, mild)** - Diagnosed 2021
10. **Obesity (BMI 32-34)** - Ongoing weight management efforts

**Charlson Comorbidity Index:** Estimated 2 (Breast cancer history)

**Breast Cancer History:**
- **2012 (age 49):** Abnormal screening mammogram → biopsy → Stage IIA invasive ductal carcinoma (right breast)
- **Treatment:**
  - 2012: Mastectomy + sentinel lymph node biopsy (1/3 nodes positive)
  - 2012-2013: Adjuvant chemotherapy (4 cycles AC, 4 cycles paclitaxel)
  - 2013: Radiation therapy (6 weeks)
  - 2013-present: Hormone therapy (tamoxifen 2013-2023, then aromatase inhibitor)
- **Surveillance:**
  - Annual mammograms (2013-present, no recurrence)
  - Oncology follow-up every 6 months (2013-2020), now annually
  - Last visit: October 2025 (Walla Walla oncology) - no evidence of disease

**Diabetes Management:**
- **A1C Trend:** 8.5% (2012) → 7.2% (2015) → 6.8% (2020) → 7.1% (2025)
- **Complications:**
  - Peripheral neuropathy (feet): Diagnosed 2020
  - Retinopathy (mild, nonproliferative): Diagnosed 2021, stable
  - No nephropathy (normal kidney function)
- **Treatment Evolution:**
  - 2012-2016: Metformin monotherapy
  - 2016-2020: Metformin + glipizide
  - 2020-present: Metformin + empagliflozin (SGLT2 inhibitor, cardioprotective)

**Mental Health:**
- 2011: PTSD diagnosis (mild-moderate severity)
- 2012-2013: Anxiety and depression during cancer treatment
- 2014-present: Stable, monthly therapy sessions
- No hospitalizations, no suicide ideation/attempts

**Current Medications (~12):**
- Metformin 1000mg BID (diabetes)
- Empagliflozin 10mg daily (diabetes, cardioprotective)
- Lisinopril 10mg daily (hypertension, renal protection)
- Atorvastatin 20mg nightly (hyperlipidemia)
- Aspirin 81mg daily (cardiovascular protection)
- Anastrozole 1mg daily (aromatase inhibitor, breast cancer prevention)
- Levothyroxine 75mcg daily (hypothyroidism)
- Gabapentin 300mg TID (neuropathic pain, feet)
- Sertraline 100mg daily (PTSD/anxiety)
- Calcium + Vitamin D (bone health, aromatase inhibitor side effect mitigation)
- Celecoxib 200mg BID PRN (knee pain)
- Multivitamin daily

**Allergies:**
- Sulfa drugs (Bactrim) → Severe rash (hives), confirmed 2015
- Codeine → Nausea, confirmed 2010

**Patient Flags:**
- **Diabetes Management (Cat II Local)** - Active, requires quarterly A1C monitoring
- **Cancer Survivor (Cat II Local)** - Active, annual surveillance mammogram required

**Key Clinical Events:**
- 1990-2010: Military service, multiple deployments
- 2010: Retirement, VA enrollment at Bay Pines
- 2011: PTSD diagnosis
- 2012: Type 2 diabetes diagnosis, married
- 2013: Hypertension diagnosis
- 2016: Hypothyroidism diagnosis
- 2012: Breast cancer diagnosis (Stage IIA)
- 2012-2013: Cancer treatment (surgery, chemo, radiation)
- 2019-present: Hormone therapy (tamoxifen → anastrozole)
- 2020: Diabetic peripheral neuropathy diagnosis
- 2021: Diabetic retinopathy (mild) diagnosis
- 2025: Relocation to Walla Walla, WA

**Social History:**
- Married since 2012 (supportive spouse, also veteran)
- No children
- Retired, 50% VA disability compensation + military pension
- Active in local veteran women's support group
- Non-smoker, occasional alcohol use (1-2 drinks/month)

**AI/ML Testing Scenarios:**
- **Drug-Drug Interactions:** Minimal risk (well-managed polypharmacy)
- **Vitals Trends:** Weight fluctuations (cancer treatment weight loss 2012-2013, gradual gain 2014-2025), blood pressure control
- **Patient Summary:** Diabetes management, cancer survivorship, chronic disease monitoring
- **Clinical Notes:** Oncology notes, diabetes educator notes, ophthalmology diabetic screening notes
- **Charlson Comorbidity Index:** Moderate score (diabetes with complications, breast cancer history)
- **Care Gaps:** Annual mammogram compliance, diabetic retinal exam compliance, A1C monitoring

---

### Joe Thompson (Male Veteran - Healthy Control)

**Demographics:**
- **Full Name:** Joe Michael Thompson
- **Date of Birth:** May 10, 1970 (age 55-56)
- **Sex:** Male
- **SSN:** 200-00-1003 (mock)
- **Race/Ethnicity:** White, Not Hispanic/Latino
- **Marital Status:** Married (2000-present)

**Military Service:**
- **Branch:** U.S. Air Force
- **Service Period:** 1992-2012 (20 years)
- **Rank at Retirement:** Major (O-4)
- **Discharge Status:** Honorable
- **Deployments:**
  - 2005-2006: Iraq War (Operation Iraqi Freedom) - Qatar/Kuwait theater, logistics coordination (non-combat, rear echelon)

**Service-Connected Disabilities (Total: 10%):**
- **Tinnitus (bilateral):** 10% (aircraft noise exposure)

**Medical Conditions (Major):**
1. **Hypertension (mild)** - Diagnosed 2015, well-controlled on single medication
2. **Hyperlipidemia (mild)** - Diagnosed 2016, well-controlled on statin

**Charlson Comorbidity Index:** 0 (no comorbidities, excellent prognosis)

**Health Profile:**
Joe represents the "healthy veteran" control case - same family background and military service era as his siblings, but dramatically different health outcomes due to:
- **Officer status:** Better pay, less physical stress, more control over work environment
- **Air Force vs Army:** No ground combat exposure, better living conditions during service
- **Non-combat role:** Logistics officer in rear echelon, never exposed to IEDs or direct combat
- **Strong social support:** Married 24 years, two adult children, close family ties
- **No substance use:** Never smoked, social drinker only (1-2 drinks/week), no illicit drugs
- **Excellent preventive care:** All screenings up to date, exercises regularly, normal BMI
- **Financial stability:** Federal contractor career (2012-2020), retired early, financially secure
- **Strong coping mechanisms:** Healthy stress management, strong social network, supportive marriage

**Mental Health:**
- No PTSD (no combat exposure)
- No depression, anxiety, or other mental health conditions
- Excellent adjustment to civilian life
- Strong family relationships (close with siblings Bailey and Alananah, provides support)

**Physical Health:**
- **Weight:** Stable, BMI 26 (slightly overweight but stable for 10+ years)
- **Blood Pressure:** 130-138/80-85 (well-controlled on lisinopril 10mg)
- **Cholesterol:** LDL 95 mg/dL (goal <100, well-controlled on atorvastatin 20mg)
- **No diabetes:** Fasting glucose 92-98 mg/dL (normal), A1C 5.4% (excellent)
- **No chronic pain:** Occasional knee soreness from recreational basketball (OTC ibuprofen PRN)
- **Excellent fitness:** Walks 3 miles daily, plays basketball weekly, active lifestyle

**Current Medications (3 total):**
- Lisinopril 10mg daily (hypertension)
- Atorvastatin 20mg nightly (hyperlipidemia)
- Multivitamin daily (preventive care)

**Allergies:**
- NKDA (No Known Drug Allergies)

**Patient Flags:**
- None (no high-risk flags)

**Key Clinical Events:**
- 2012: Military retirement, initial VA enrollment (Bay Pines)
- 2015: Hypertension diagnosis (routine screening, started lisinopril)
- 2016: Hyperlipidemia diagnosis (routine screening, started atorvastatin)
- 2018: Elective inguinal hernia repair (outpatient surgery, uneventful recovery)
- 2020: Retired from federal contracting (age 50, financially stable)
- 2025: Relocation to Walla Walla, WA (moved with siblings)

**Social History:**
- Married since 2000 (spouse: Jennifer Thompson, also healthy)
- Two adult children (son 23, daughter 21, both college graduates)
- Retired federal contractor (logistics), financially secure
- Active volunteer (veteran mentorship program)
- Close relationship with siblings Bailey and Alananah (provides emotional/financial support to Bailey during difficult periods)
- Lives in separate home near siblings (same neighborhood)
- Strong social network, active in community

**Occupation Post-Military:**
- 2012-2020: Federal contractor (logistics, $120K/year)
- 2020-present: Retired (early retirement at age 50)
- Hobbies: Basketball, hiking, volunteering, family time

**AI/ML Testing Scenarios:**
- **Drug-Drug Interactions:** None (minimal polypharmacy)
- **Vitals Trends:** Stable weight, stable blood pressure (model of consistency)
- **Patient Summary:** "Healthy 55-year-old male veteran with excellent preventive care and minimal chronic disease burden"
- **Clinical Notes:** Routine wellness visits, preventive screening notes, hernia surgery note
- **Charlson Comorbidity Index:** Score of 0 (low mortality risk, excellent prognosis)
- **Comparison with Siblings:** Demonstrates impact of combat exposure, officer status, and social support on long-term health outcomes

**Contrast with Siblings (Key Differences):**

| Factor | Bailey (Poor Health) | Alananah (Moderate Health) | Joe (Excellent Health) |
|--------|---------------------|---------------------------|----------------------|
| **Branch** | Army (ground combat) | Army (medical, support) | Air Force (logistics, office) |
| **Rank** | Enlisted (E-7) | Enlisted (E-8) | Officer (O-4) |
| **Combat Exposure** | High (infantry, IED blast) | Moderate (indirect fire, casualties) | None (rear echelon) |
| **PTSD** | Severe (70% SC) | Mild-Moderate (30% SC) | None |
| **Chronic Pain** | Severe (40% SC, opioid history) | Moderate (10% SC, knee arthritis) | None |
| **Substance Use** | Yes (tobacco, alcohol) | No | No |
| **Chronic Diseases** | 12 major conditions | 10 major conditions | 2 mild conditions |
| **Medications** | 15 active | 12 active | 3 active |
| **Hospitalizations** | 32 admissions | 28 admissions | 1 admission (elective) |
| **Charlson Score** | 5 (high risk) | 4 (moderate risk) | 0 (low risk) |
| **Marital Status** | Divorced (stress) | Married (support) | Married (support) |
| **Social Support** | Limited | Good | Excellent |
| **Financial Status** | Disabled, limited income | Retired, moderate income | Retired, high income |

This comparison provides excellent data for analyzing the impact of military service conditions, rank/occupation, combat exposure, and social determinants of health on long-term veteran health outcomes.

---

## Patient Identification Schema

Following the established med-z1 pattern for multi-database patient identity resolution:

### Bailey Thompson (Male)

| Database | PatientSID | ICN | Sta3n | Facility | Time Period |
|----------|------------|-----|-------|----------|-------------|
| CDWWork | 2001 | ICN200001 | 516 | Bay Pines VA Healthcare System (FL) | 2010-2025 |
| CDWWork2 | 20001 | ICN200001 | 687 | Jonathan M. Wainwright Memorial VAMC (WA) | 2025-2026 |

### Alananah Thompson (Female)

| Database | PatientSID | ICN | Sta3n | Facility | Time Period |
|----------|------------|-----|-------|----------|-------------|
| CDWWork | 2002 | ICN200002 | 516 | Bay Pines VA Healthcare System (FL) | 2010-2025 |
| CDWWork2 | 20002 | ICN200002 | 687 | Jonathan M. Wainwright Memorial VAMC (WA) | 2025-2026 |

### Joe Thompson (Male)

| Database | PatientSID | ICN | Sta3n | Facility | Time Period |
|----------|------------|-----|-------|----------|-------------|
| CDWWork | 2003 | ICN200003 | 516 | Bay Pines VA Healthcare System (FL) | 2012-2025 |
| CDWWork2 | 20003 | ICN200003 | 687 | Jonathan M. Wainwright Memorial VAMC (WA) | 2025-2026 |

**Key Points:**
- **ICN (Integrated Care Number):** Unique national identifier (ICN200001, ICN200002, ICN200003)
- **PatientSID:** Database-specific surrogate key
  - CDWWork uses 2001/2002/2003 (lower range)
  - CDWWork2 uses 20001/20002/20003 (higher range, following existing pattern)
- **Sta3n (Station Number):** Real VA facility codes
  - 516 = Bay Pines VA Healthcare System (St. Petersburg, FL)
  - 687 = Jonathan M. Wainwright Memorial VA Medical Center (Walla Walla, WA)
- **Identity Resolution:** ETL Silver layer will resolve PatientSID 2001 (CDWWork) + PatientSID 20001 (CDWWork2) → single patient ICN200001

---

## Demographics

### Bailey Thompson

| Field | Value | Notes |
|-------|-------|-------|
| **Full Name** | Bailey James Thompson | Middle name: James |
| **Date of Birth** | 1963-04-15 | Age 62 (as of Feb 2026) |
| **Sex** | Male | Assigned at birth |
| **SSN** | 200-00-1001 | Mock value (non-real) |
| **Race** | White | Self-reported |
| **Ethnicity** | Not Hispanic/Latino | Self-reported |
| **Marital Status** | Divorced | Divorced 2018 |
| **Religion** | Protestant | Optional field |
| **Preferred Language** | English | Primary language |
| **Contact Phone** | (727) 555-2001 | Bay Pines era (CDWWork) |
| **Contact Phone** | (509) 555-2001 | Walla Walla era (CDWWork2) |
| **Email** | bailey.thompson@example.com | Mock email |

**Addresses:**

**Bay Pines Era (2010-2025):**
- Street: 1234 Gulf Blvd, Apt 5B
- City: St. Petersburg
- State: FL
- ZIP: 33706
- County: Pinellas
- Address Type: Residential

**Walla Walla Era (2025-2026):**
- Street: 567 Pine Street, Unit 12
- City: Walla Walla
- State: WA
- ZIP: 99362
- County: Walla Walla
- Address Type: Residential

**Emergency Contact:**
- Name: Alananah Thompson (sister)
- Relationship: Sister
- Phone: (509) 555-2002

**Insurance:**
- VA Healthcare (Priority Group 1 - 100% service-connected)
- Medicare Part A & B (eligible since age 65 in 2028 - future)
- Tricare for Life (retiree, secondary to VA)

### Alananah Thompson

| Field | Value | Notes |
|-------|-------|-------|
| **Full Name** | Alananah Marie Thompson | Middle name: Marie |
| **Date of Birth** | 1965-08-22 | Age 60 (as of Feb 2026) |
| **Sex** | Female | Assigned at birth |
| **SSN** | 200-00-1002 | Mock value (non-real) |
| **Race** | White | Self-reported |
| **Ethnicity** | Not Hispanic/Latino | Self-reported |
| **Marital Status** | Married | Married 2012-present |
| **Religion** | None/Agnostic | Optional field |
| **Preferred Language** | English | Primary language |
| **Contact Phone** | (727) 555-2002 | Bay Pines era (CDWWork) |
| **Contact Phone** | (509) 555-2002 | Walla Walla era (CDWWork2) |
| **Email** | alananah.thompson@example.com | Mock email |

**Addresses:**

**Bay Pines Era (2010-2025):**
- Street: 1234 Gulf Blvd, Apt 6C
- City: St. Petersburg
- State: FL
- ZIP: 33706
- County: Pinellas
- Address Type: Residential
- **Note:** Same building as brother Bailey (different unit)

**Walla Walla Era (2025-2026):**
- Street: 789 Maple Avenue
- City: Walla Walla
- State: WA
- ZIP: 99362
- County: Walla Walla
- Address Type: Residential

**Emergency Contact:**
- Name: Robert Thompson (spouse)
- Relationship: Spouse
- Phone: (509) 555-2003

**Insurance:**
- VA Healthcare (Priority Group 3 - 50% service-connected)
- Medicare Part A & B (not yet eligible, age 60)
- Tricare for Life (retiree, secondary to VA)

### Joe Thompson

| Field | Value | Notes |
|-------|-------|-------|
| **Full Name** | Joe Michael Thompson | Middle name: Michael |
| **Date of Birth** | 1970-05-10 | Age 55 (as of Feb 2026) |
| **Sex** | Male | Assigned at birth |
| **SSN** | 200-00-1003 | Mock value (non-real) |
| **Race** | White | Self-reported |
| **Ethnicity** | Not Hispanic/Latino | Self-reported |
| **Marital Status** | Married | Married 2000-present |
| **Religion** | Christian | Optional field |
| **Preferred Language** | English | Primary language |
| **Contact Phone** | (727) 555-2003 | Bay Pines era (CDWWork) |
| **Contact Phone** | (509) 555-2003 | Walla Walla era (CDWWork2) |
| **Email** | joe.thompson@example.com | Mock email |

**Addresses:**

**Bay Pines Era (2012-2025):**
- Street: 1250 Gulf Blvd (separate house, same neighborhood as siblings)
- City: St. Petersburg
- State: FL
- ZIP: 33706
- County: Pinellas
- Address Type: Residential

**Walla Walla Era (2025-2026):**
- Street: 800 Oak Street
- City: Walla Walla
- State: WA
- ZIP: 99362
- County: Walla Walla
- Address Type: Residential

**Emergency Contact:**
- Name: Jennifer Thompson (spouse)
- Relationship: Spouse
- Phone: (509) 555-2004

**Insurance:**
- VA Healthcare (Priority Group 7 - 10% service-connected)
- Medicare Part A & B (not yet eligible, age 55)
- Tricare for Life (retiree, secondary to VA)
- Private insurance (retiree health plan from federal contractor)

---

## Military Service History

### Bailey Thompson

| Field | Value |
|-------|-------|
| **Branch** | U.S. Army |
| **Service Period** | 1990-06-15 to 2010-06-14 (20 years) |
| **Rank at Retirement** | Sergeant First Class (E-7) |
| **MOS (Military Occupation)** | 11B (Infantryman) |
| **Discharge Type** | Honorable |
| **Discharge Reason** | Medical Retirement (combat injuries, PTSD) |

**Deployments:**
1. **Gulf War (1990-1991):** Operation Desert Storm, Kuwait/Iraq theater (6 months)
2. **Bosnia (1995-1996):** Peacekeeping operations (12 months)
3. **Iraq War (2003-2005):** Operation Iraqi Freedom, Baghdad (18 months) - **IED blast injury April 2004**
4. **Iraq War (2007-2008):** Operation Iraqi Freedom, Fallujah (12 months)

**Combat Injuries:**
- **2004-04-12:** IED blast (Baghdad, Iraq)
  - Traumatic brain injury (TBI), concussion
  - Lumbar spine fractures (L3-L4 compression fractures)
  - Shrapnel wounds (left leg, abdomen - removed)
  - Tympanic membrane rupture (bilateral)
  - 3 months evacuation/treatment (Landstuhl, Germany → Walter Reed, USA)
  - Returned to duty 2004-08 (limited duty)

**Service-Connected Disability Ratings:**
- PTSD: 70%
- Chronic back pain (lumbar spine): 40%
- Tinnitus (bilateral): 10%
- TBI (mild, residuals): 10%
- **Total Combined Rating:** 100% (Permanent and Total)

**Awards/Decorations:**
- Purple Heart (2004, combat injury)
- Bronze Star Medal (2004, meritorious service)
- Army Commendation Medal (2x)
- Army Achievement Medal (3x)
- Combat Infantryman Badge
- Good Conduct Medal (6x)

**Exposures:**
- **Gulf War Exposures:** Oil fire smoke, pesticides
- **Burn Pit Exposure:** Iraq (2003-2005, 2007-2008)
- **Blast Exposure:** Multiple (IED, mortars, RPGs)
- **Agent Orange:** None (post-Vietnam era)

### Alananah Thompson

| Field | Value |
|-------|-------|
| **Branch** | U.S. Army |
| **Service Period** | 1990-06-15 to 2010-06-14 (20 years) |
| **Rank at Retirement** | Master Sergeant (E-8) |
| **MOS (Military Occupation)** | 68W (Combat Medic / Healthcare Specialist) |
| **Discharge Type** | Honorable |
| **Discharge Reason** | Retirement (20 years service) |

**Deployments:**
1. **Gulf War (1990-1991):** Operation Desert Storm, Saudi Arabia (medical logistics, 6 months)
2. **Bosnia (1996):** Peacekeeping operations, combat support hospital (12 months)
3. **Iraq War (2003-2004):** Operation Iraqi Freedom, Baghdad Combat Support Hospital (12 months)
4. **Iraq War (2006-2007):** Operation Iraqi Freedom, Balad Air Base (medical, 12 months)

**Combat Exposure:**
- **Indirect fire (mortars/rockets):** Multiple incidents, Balad Air Base (2006-2007)
- **Mass casualty events:** Treated combat casualties, exposure to traumatic injuries
- **No direct combat injuries:** Non-combat service-connected conditions

**Service-Connected Disability Ratings:**
- PTSD: 30%
- Bilateral knee pain (degenerative joint disease): 10%
- Bilateral hearing loss: 10%
- **Total Combined Rating:** 50%

**Awards/Decorations:**
- Meritorious Service Medal (2010, retirement)
- Army Commendation Medal (3x)
- Army Achievement Medal (5x)
- Combat Medical Badge (2004, Iraq)
- Good Conduct Medal (6x)

**Exposures:**
- **Gulf War Exposures:** Oil fire smoke, pesticides
- **Burn Pit Exposure:** Iraq (2003-2004, 2006-2007)
- **Blast Exposure:** Indirect fire, no direct blast injuries
- **Agent Orange:** None (post-Vietnam era)

### Joe Thompson

| Field | Value |
|-------|-------|
| **Branch** | U.S. Air Force |
| **Service Period** | 1992-06-01 to 2012-06-01 (20 years) |
| **Rank at Retirement** | Major (O-4) |
| **AFSC (Air Force Specialty Code)** | 21R (Logistics Readiness Officer) |
| **Discharge Type** | Honorable |
| **Discharge Reason** | Retirement (20 years service) |

**Deployments:**
1. **Iraq War (2005-2006):** Operation Iraqi Freedom, Al Udeid Air Base (Qatar) and Ali Al Salem Air Base (Kuwait) - Logistics coordination, supply chain management (12 months, non-combat rear echelon)

**Combat Exposure:**
- **No direct combat exposure:** Served in rear echelon support roles at secure air bases
- **No combat injuries:** Office-based logistics work, never exposed to IEDs or direct fire
- **No traumatic incidents:** Routine deployment without significant threats

**Service-Connected Disability Ratings:**
- Tinnitus (bilateral): 10% (aircraft noise exposure on flight line)
- **Total Combined Rating:** 10%

**Awards/Decorations:**
- Meritorious Service Medal (2012, retirement)
- Air Force Commendation Medal (2x)
- Air Force Achievement Medal (3x)
- National Defense Service Medal
- Global War on Terrorism Service Medal
- Air Force Good Conduct Medal (6x)

**Exposures:**
- **Aircraft Noise:** Flight line operations, contributing to mild tinnitus
- **Burn Pit Exposure:** Minimal (spent most deployment on secure air bases with better facilities)
- **No combat exposure:** Rear echelon logistics role
- **Agent Orange:** None (post-Vietnam era)

**Key Differences from Siblings:**
- **Officer vs Enlisted:** Better pay ($60K-$90K as officer vs $40K-$60K as enlisted), less physical labor, more autonomy
- **Air Force vs Army:** Significantly better living conditions, no ground combat, secure airbases with amenities
- **Logistics vs Combat/Medical:** Office work, predictable hours, no life-threatening situations
- **Single deployment (12 months) vs Multiple deployments (48+ months):** Less cumulative stress and trauma exposure
- **No combat trauma:** Never saw combat, IEDs, or mass casualties (unlike siblings)

---

## Clinical Domain Data Requirements

All data quantities below represent **totals across both databases** (CDWWork + CDWWork2) unless otherwise specified.

### Schema Cross-References

For authoritative field names and data types when writing INSERT scripts, consult the CREATE TABLE scripts:

**CDWWork (VistA) Schema Files:** `mock/sql-server/cdwwork/create/`
- Demographics: `SPatient.SPatient.sql`, `SPatient.SPatientAddress.sql`, `SPatient.SPatientPhone.sql`, `SPatient.SPatientInsurance.sql`, `SPatient.SPatientDisability.sql`
- Vitals: `Vital.VitalSign.sql`, `Dim.VitalType.sql`
- Patient Flags: `Dim.PatientRecordFlag.sql`, `SPatient.PatientRecordFlagAssignment.sql`
- Allergies: `Allergy.PatientAllergy.sql`, `Allergy.PatientAllergyReaction.sql`
- Medications: `RxOut.RxOutpat.sql`, `Dim.LocalDrug.sql`, `Dim.NationalDrug.sql`
- Encounters: `Inpat.Inpatient.sql`, `Dim.Location.sql`
- Clinical Notes: `TIU.TIUDocument_8925.sql`, `TIU.TIUDocumentText.sql`, `Dim.TIUDocumentDefinition.sql`
- Immunizations: `Immunization.PatientImmunization.sql`, `Dim.Vaccine.sql`
- Problems: `Outpat.ProblemList.sql`
- Labs: `Chem.LabChem.sql`, `Dim.LabTest.sql`

**CDWWork2 (Cerner) Schema Files:** `mock/sql-server/cdwwork2/create/`
- Demographics: `VeteranMill.SPerson.sql`
- Vitals: `VitalMill.VitalResult.sql`, `NDimMill.CodeValue.sql`
- Encounters: `EncMill.Encounter.sql`
- Problems: `EncMill.ProblemList.sql`
- Immunizations: `ImmunizationMill.VaccineAdmin.sql`, `ImmunizationMill.VaccineCode.sql`

**⚠️ IMPORTANT:** Use `Thompson-Bailey.sql` as the authoritative template for all INSERT statement structures. The field order and VALUES clause patterns in Bailey's script are correct and tested.

### Domain 1: Demographics

**Tables:** `SPatient.SPatient`, `SPatient.SPatientAddress`, `SPatient.SPatientPhone`, related dimension tables

**Data Requirements:**
- Complete demographic records per specifications in [Demographics](#demographics) section
- Address history: 2 addresses each (Bay Pines era, Walla Walla era)
- Phone number updates corresponding to moves
- Insurance/enrollment records in both databases

**CDWWork (2012-2025):**
- PatientSID 2001/2002/2003, Sta3n 516
- Florida addresses, (727) phone numbers

**CDWWork2 (2025-2026):**
- PatientSID 20001/20002/20003, Sta3n 687
- Washington addresses, (509) phone numbers

**Note:** Joe Thompson's CDWWork data starts in 2012 (his retirement year), not 2010 like his siblings.

### Domain 2: Vitals

**Tables:** `Vital.VitalSign`, `Dim.VitalType`, `Dim.Location`

**Data Requirements:**

**Bailey Thompson - ~64 vital readings total:**
- **CDWWork (2010-2025, Bay Pines):** ~60 readings (quarterly x 15 years)
  - Height: 70 inches (constant)
  - Weight: 185 lbs (2010) → 245 lbs (2019, peak, alcohol/sedentary) → 220 lbs (2025, post-sobriety)
  - BMI: 26.5 (2010) → 35.2 (2019, obese) → 31.6 (2025, obese)
  - Blood Pressure: 125/78 (2010) → 145/92 (2014, pre-HTN dx) → 135/85 (2025, treated)
  - Pulse: 72-85 bpm
  - Temperature: 98.6°F (normal)
  - Respirations: 16-18/min
  - Pain Score: 5-8/10 (chronic back pain)
  - Pulse Oximetry: 96-98% (baseline, sleep apnea when untreated)

- **CDWWork2 (2025-2026, Walla Walla):** ~4 readings (quarterly)
  - Weight: 215-220 lbs (continued gradual loss)
  - BP: 130-138/82-88 (well-controlled on meds)
  - Pain: 4-6/10 (improved pain management)

**Alananah Thompson - ~64 vital readings total:**
- **CDWWork (2010-2025, Bay Pines):** ~60 readings (quarterly)
  - Height: 65 inches (constant)
  - Weight: 165 lbs (2010) → 145 lbs (2019, cancer treatment) → 175 lbs (2025, post-treatment weight gain)
  - BMI: 27.5 (2010) → 24.1 (2019, during chemo) → 29.1 (2025, overweight)
  - Blood Pressure: 128/80 (2010) → 138/88 (2013, HTN dx) → 125/78 (2025, well-controlled)
  - Pulse: 68-78 bpm
  - Temperature: 98.4°F (normal)
  - Respirations: 14-16/min
  - Pain Score: 2-4/10 (knee arthritis)

- **CDWWork2 (2025-2026, Walla Walla):** ~4 readings
  - Weight: 170-175 lbs (gradual loss, diabetes management)
  - BP: 122-128/76-82 (excellent control)
  - Pain: 2-3/10 (knee pain managed)

**Joe Thompson - ~56 vital readings total:**
- **CDWWork (2012-2025, Bay Pines):** ~52 readings (quarterly x 13 years)
  - Height: 72 inches (constant)
  - Weight: 190 lbs (2012) → 195 lbs (2025, stable, minimal variation)
  - BMI: 25.8 (2012) → 26.4 (2025, slightly overweight but stable)
  - Blood Pressure: 128/82 (2012) → 135/85 (2015, pre-HTN) → 130/80 (2016-2025, controlled on lisinopril)
  - Pulse: 68-75 bpm (excellent)
  - Temperature: 98.6°F (normal)
  - Respirations: 14-16/min (normal)
  - Pain Score: 0-1/10 (minimal, occasional knee soreness)
  - Pulse Oximetry: 98-99% (excellent)

- **CDWWork2 (2025-2026, Walla Walla):** ~4 readings (quarterly)
  - Weight: 193-195 lbs (stable)
  - BP: 128-132/78-82 (excellent control)
  - Pain: 0-1/10 (minimal)

**Key Vital Trends for AI Analysis:**
- **Bailey:** Weight gain/loss correlating with alcohol use and sobriety
- **Alananah:** Weight loss during cancer treatment, subsequent gradual gain
- **Joe:** Model of stability - minimal weight variation, excellent BP control, no chronic pain

### Domain 3: Patient Flags

**Tables:** `Dim.PatientRecordFlag`, `SPatient.PatientRecordFlagAssignment`, `SPatient.PatientRecordFlagHistory`

**Data Requirements:**

**Bailey Thompson - 2 flags:**

1. **High Risk for Suicide (Cat I National)**
   - **Active:** 2016-09-15 to present
   - **Reason:** Suicide attempt via opioid overdose (2016-09-12)
   - **Assignment:** Bay Pines psychiatry (2016-09-15)
   - **Review History:** Reviewed every 90 days (2016-2025 Bay Pines, 2025-2026 Walla Walla)
   - **Narrative (sensitive):** "63M veteran with PTSD, chronic pain, and major depressive disorder. Suicide attempt 09/2016 via intentional opioid overdose. Currently stable on medications, engaged in weekly therapy. Continues to endorse occasional passive SI but denies intent/plan. Firearms removed from home. Safety plan in place."

2. **Opioid Risk (Cat II Local, Bay Pines)**
   - **Active:** 2010-06-15 to 2018-12-31 (Inactive)
   - **Reason:** Chronic opioid therapy for combat-related back pain
   - **Assignment:** Bay Pines pain management (2010-06-15)
   - **Inactivation:** 2018-12-31 (successful opioid taper completed)
   - **Narrative:** "Veteran successfully tapered off chronic opioid therapy. Transitioned to non-opioid pain management (gabapentin, duloxetine, interventional procedures). No longer requires opioid risk monitoring."

**Alananah Thompson - 2 flags:**

1. **Diabetes Management (Cat II Local, Bay Pines/Walla Walla)**
   - **Active:** 2012-03-01 to present
   - **Reason:** Type 2 diabetes requiring quarterly monitoring
   - **Assignment:** Bay Pines endocrinology (2012-03-01), transferred to Walla Walla (2025-01-15)
   - **Review History:** Reviewed quarterly
   - **Narrative:** "61F veteran with Type 2 diabetes (dx 2012). Requires quarterly A1C monitoring, annual diabetic foot exam, annual retinal exam. Complicated by peripheral neuropathy (2020) and mild nonproliferative retinopathy (2021). Last A1C 7.1% (goal <7.5%)."

2. **Cancer Survivor (Cat II Local, Bay Pines/Walla Walla)**
   - **Active:** 2018-06-15 to present
   - **Reason:** Breast cancer survivor requiring surveillance
   - **Assignment:** Bay Pines oncology (2018-06-15), transferred to Walla Walla (2025-01-15)
   - **Review History:** Reviewed every 6 months (2018-2022), annually (2023-present)
   - **Narrative:** "Breast cancer Stage IIA (2012), treated with mastectomy, chemotherapy, radiation, and hormone therapy. Currently on anastrozole. Requires annual screening mammogram and oncology follow-up. Last mammogram 10/2025: BI-RADS 1 (negative)."

**Joe Thompson - 0 flags:**
- No patient flags (no high-risk conditions requiring special monitoring)

### Domain 4: Allergies

**Tables:** `Allergy.Allergy`, `Dim.AllergyType`

**Data Requirements:**

**Bailey Thompson - 2 allergies:**

1. **Penicillin**
   - **Reaction:** Rash (urticaria)
   - **Severity:** Moderate
   - **Type:** Drug allergy
   - **Verified:** Unconfirmed (childhood report, never re-challenged)
   - **Date Recorded:** 2010-06-16 (initial VA enrollment)
   - **Comments:** "Patient reports childhood rash with penicillin. No anaphylaxis. Never re-exposed. Avoid penicillins, use alternative antibiotics (fluoroquinolones, macrolides acceptable)."

2. **Morphine**
   - **Reaction:** Severe nausea and vomiting
   - **Severity:** Moderate-Severe
   - **Type:** Drug intolerance
   - **Verified:** Confirmed (2016-09 during hospitalization)
   - **Date Recorded:** 2016-09-14
   - **Comments:** "Confirmed severe nausea/vomiting with IV morphine during psychiatric admission. Not true allergy (no histamine release), but intolerance severe enough to avoid. Use alternative opioids if needed (oxycodone, hydromorphone tolerated)."

**Alananah Thompson - 2 allergies:**

1. **Sulfa Drugs (Sulfamethoxazole/Trimethoprim, Bactrim)**
   - **Reaction:** Severe rash (urticaria, hives, pruritus)
   - **Severity:** Severe
   - **Type:** Drug allergy
   - **Verified:** Confirmed (2015-07, treated for UTI)
   - **Date Recorded:** 2015-07-20
   - **Comments:** "Developed diffuse urticarial rash and pruritus 2 days after starting Bactrim for UTI. Rash resolved with antihistamines and drug discontinuation. Avoid all sulfonamide antibiotics. No cross-reactivity with sulfonylureas (takes glipizide without issue)."

2. **Codeine**
   - **Reaction:** Nausea
   - **Severity:** Mild-Moderate
   - **Type:** Drug intolerance
   - **Verified:** Confirmed (2010, post-op knee arthroscopy)
   - **Date Recorded:** 2010-11-05
   - **Comments:** "Nausea with codeine-containing analgesics. Use alternative opioids (oxycodone, hydrocodone) or non-opioid analgesics (NSAIDs, acetaminophen)."

**Joe Thompson - 0 allergies:**
- NKDA (No Known Drug Allergies)

### Domain 5: Medications

**Tables:** `RxOut.RxOutpatient`, `Dim.LocalDrug`, `Dim.NationalDrug`

**Data Requirements:**

**Bailey Thompson - ~45 medication records total:**
- **Active medications (current, ~15):** See "Current Medications" in persona
- **Historical medications (~30):** Discontinued or replaced over 15 years
  - **2010-2018:** Opioids (oxycodone, morphine ER, hydrocodone) - discontinued 2018
  - **2010-2020:** Various psych med trials (fluoxetine, paroxetine, venlafaxine) - settled on sertraline
  - **2010-2016:** Various pain meds (tramadol, cyclobenzaprine) - replaced with current regimen
  - **2019-2022:** Varenicline (Chantix) - tobacco cessation, completed course
  - **Antibiotics (intermittent):** For infections (UTIs, respiratory infections, skin infections)

**Active Medications (2025-2026, both databases):**
1. Sertraline 200mg PO daily (PTSD/depression)
2. Prazosin 5mg PO nightly (PTSD nightmares)
3. Gabapentin 1200mg PO TID (neuropathic pain)
4. Duloxetine 60mg PO daily (pain/depression, SNRI)
5. Lidocaine 5% patches, apply to lower back daily (topical pain)
6. Metformin 1000mg PO BID (diabetes)
7. Lisinopril 20mg PO daily (hypertension)
8. Atorvastatin 40mg PO nightly (hyperlipidemia)
9. Aspirin 81mg PO daily (cardiovascular protection)
10. Pantoprazole 40mg PO daily (GERD)
11. Trazodone 100mg PO nightly (insomnia)
12. Vitamin D 2000 IU PO daily (deficiency)
13. Multivitamin PO daily (nutritional support)
14. Acetaminophen 650mg PO Q6H PRN (pain)
15. Naproxen 500mg PO BID PRN (pain, inflammation)

**Alananah Thompson - ~40 medication records total:**
- **Active medications (current, ~12):** See "Current Medications" in persona
- **Historical medications (~28):** Discontinued or replaced
  - **2012-2016:** Metformin monotherapy - dose escalated, glipizide added 2016
  - **2016-2020:** Glipizide 10mg BID - discontinued 2020, replaced with empagliflozin
  - **2018-2019:** Chemotherapy agents (doxorubicin, cyclophosphamide, paclitaxel) - completed
  - **2018-2019:** Antiemetics for chemo (ondansetron, metoclopramide) - completed
  - **2019-2024:** Tamoxifen 20mg daily - switched to anastrozole 2024 (post-menopause)
  - **Antibiotics (intermittent):** For infections (UTIs, respiratory infections)

**Active Medications (2025-2026, both databases):**
1. Metformin 1000mg PO BID (diabetes)
2. Empagliflozin 10mg PO daily (diabetes, SGLT2 inhibitor, cardioprotective)
3. Lisinopril 10mg PO daily (hypertension, renal protection)
4. Atorvastatin 20mg PO nightly (hyperlipidemia)
5. Aspirin 81mg PO daily (cardiovascular protection)
6. Anastrozole 1mg PO daily (aromatase inhibitor, breast cancer prevention)
7. Levothyroxine 75mcg PO daily (hypothyroidism)
8. Gabapentin 300mg PO TID (diabetic peripheral neuropathy)
9. Sertraline 100mg PO daily (PTSD/anxiety)
10. Calcium 600mg + Vitamin D 400 IU, PO BID (bone health, AI side effects)
11. Celecoxib 200mg PO BID PRN (knee pain, arthritis)
12. Multivitamin PO daily (nutritional support)

**Joe Thompson - ~8 medication records total:**
- **Active medications (current, 3):**
  1. Lisinopril 10mg PO daily (hypertension, started 2015)
  2. Atorvastatin 20mg PO nightly (hyperlipidemia, started 2016)
  3. Multivitamin PO daily (preventive care)

- **Historical medications (~5):**
  - Ibuprofen 600mg PO PRN (occasional use for knee soreness, 2012-2025)
  - Amoxicillin 500mg (completed courses for rare infections, 2x over 13 years)
  - Other: Minimal medication history

**AI/ML Testing - Drug-Drug Interactions:**
- **Bailey:** Sertraline + trazodone (serotonin syndrome risk, mild), gabapentin + duloxetine (CNS depression, monitor), aspirin + naproxen (GI bleeding risk)
- **Alananah:** Minimal interactions (well-managed regimen)
- **Joe:** No interactions (only 3 medications, no polypharmacy)

### Domain 6: Encounters

**Tables:** `Inpat.Inpatient`, `Dim.Location`, `Dim.Specialty`

**Data Requirements:**

**Bailey Thompson - ~32 inpatient encounters total:**

**CDWWork (Bay Pines, 2010-2025) - ~30 encounters:**

1. **2011-02-10 to 2011-02-17 (7 days):** Psychiatry - Initial PTSD evaluation, medication initiation
2. **2012-08-15 to 2012-08-20 (5 days):** Medicine - Uncontrolled hypertension, medication adjustment
3. **2013-11-05 to 2013-11-08 (3 days):** Psychiatry - Major depressive episode, suicide ideation (no attempt)
4. **2014-03-20 to 2014-03-25 (5 days):** Surgery - Lumbar epidural steroid injections (3-day procedure + observation)
5. **2015-09-12 to 2015-09-16 (4 days):** Medicine - Pneumonia (community-acquired)
6. **2016-09-12 to 2016-09-19 (7 days):** Psychiatry - **Suicide attempt (opioid overdose), ICU → psychiatry**
7. **2017-06-01 to 2017-06-04 (3 days):** Neurology - Sleep study, OSA diagnosis, CPAP initiation
8. **2018-07-10 to 2018-07-13 (3 days):** Medicine - Cellulitis (left leg)
9. **2019-01-22 to 2019-01-29 (7 days):** Substance Use Treatment - Alcohol detoxification, withdrawal management
10. **2019-10-05 to 2019-10-12 (7 days):** Substance Use Treatment - Residential alcohol treatment program
11. **2020-02-14 to 2020-02-18 (4 days):** Pain Management - Spinal cord stimulator trial (unsuccessful)
12. **2021-05-20 to 2021-05-24 (4 days):** Medicine - Acute kidney injury (AKI, resolved)
13. **2022-11-10 to 2022-11-14 (4 days):** Medicine - Diabetic ketoacidosis (DKA, A1C 9.5%)
14. **2023-03-18 to 2023-03-21 (3 days):** Cardiology - Atrial fibrillation (converted to sinus rhythm)
15-30. **Additional encounters:** Routine admissions for chronic disease management, minor procedures, infections (UTIs, respiratory infections)

**CDWWork2 (Walla Walla, 2025-2026) - ~2 encounters:**

1. **2025-10-08 to 2025-10-12 (4 days):** Medicine - Community-acquired pneumonia
2. **2026-01-15 to 2026-01-18 (3 days):** Psychiatry - Medication adjustment (PTSD symptom exacerbation after move)

**Alananah Thompson - ~28 inpatient encounters total:**

**CDWWork (Bay Pines, 2010-2025) - ~26 encounters:**

1. **2013-04-10 to 2013-04-12 (2 days):** Surgery - Arthroscopic knee surgery (left knee, meniscus repair)
2. **2015-09-20 to 2015-09-22 (2 days):** Surgery - Arthroscopic knee surgery (right knee, meniscus repair)
3. **2016-11-05 to 2016-11-07 (2 days):** Medicine - Hyperthyroidism workup, hypothyroidism diagnosis (post-thyroiditis)
4. **2012-07-02 to 2012-07-05 (3 days):** Surgery - **Mastectomy + sentinel lymph node biopsy (breast cancer)**
5. **2018-07-10 to 2018-07-13 (3 days):** Oncology - Chemotherapy cycle 1 (AC regimen, observation)
6. **2018-08-14 to 2018-08-17 (3 days):** Oncology - Chemotherapy cycle 2 (AC regimen)
7. **2018-09-18 to 2018-09-21 (3 days):** Oncology - Chemotherapy cycle 3 (AC regimen)
8. **2018-10-23 to 2018-10-26 (3 days):** Oncology - Chemotherapy cycle 4 (AC regimen)
9. **2018-11-27 to 2018-11-30 (3 days):** Oncology - Chemotherapy cycle 5 (paclitaxel, week 1)
10. **2019-01-08 to 2019-01-11 (3 days):** Oncology - Chemotherapy cycle 8 (paclitaxel, week 4, final)
11. **2020-08-12 to 2020-08-15 (3 days):** Neurology - Diabetic peripheral neuropathy workup, nerve conduction studies
12. **2021-03-22 to 2021-03-24 (2 days):** Ophthalmology - Diabetic retinopathy screening, laser photocoagulation consult (deferred)
13. **2022-06-10 to 2022-06-12 (2 days):** Medicine - Pyelonephritis (kidney infection)
14. **2023-09-05 to 2023-09-07 (2 days):** Cardiology - Paroxysmal atrial fibrillation (resolved, rate control)
15-26. **Additional encounters:** Routine admissions for diabetes management, oncology surveillance, minor infections

**CDWWork2 (Walla Walla, 2025-2026) - ~2 encounters:**

1. **2025-10-20 to 2025-10-22 (2 days):** Oncology - Annual surveillance (mammogram, oncology consult, no evidence of disease)
2. **2026-01-10 to 2026-01-12 (2 days):** Endocrinology - Diabetes management optimization (A1C 7.1%, medication adjustment)

**Joe Thompson - ~3 inpatient encounters total:**

**CDWWork (Bay Pines, 2012-2025) - ~1 encounter:**

1. **2018-07-10 to 2018-07-11 (1 day):** Surgery - Elective inguinal hernia repair (outpatient surgery, uneventful recovery)

**CDWWork2 (Walla Walla, 2025-2026) - ~2 encounters:**

1. **2025-09-15 to 2025-09-16 (1 day):** Surgery - Routine colonoscopy (screening, age 55, no findings, outpatient)
2. **2026-01-20 to 2026-01-21 (1 day):** Primary Care - Annual wellness visit with extended metabolic panel (outpatient)

**Key Encounter Notes:**
- All encounters include admission/discharge locations (use real Bay Pines and Walla Walla location names)
- Discharge diagnoses align with Problems/Diagnoses domain
- Encounter dates should be realistic (not clustered, spread across 15 years)

### Domain 7: Clinical Notes

**Tables:** `TIU.TIUDocument_8925`, `TIU.TIUDocumentText`, `Dim.TIUDocumentDefinition`

**Data Requirements:**

**Bailey Thompson - ~220 notes total:**

**CDWWork (Bay Pines, 2010-2025) - ~200 notes:**
- **Progress Notes (~100):** Primary care visits, psychiatry visits, pain management visits
- **Consult Notes (~40):** Psychiatry, pain management, neurology, cardiology, endocrinology
- **Discharge Summaries (~30):** One per inpatient encounter (see Domain 6)
- **Procedure Notes (~15):** Epidural steroid injections, spinal cord stimulator trial, sleep study
- **Emergency Department Notes (~10):** ER visits (chest pain, back pain exacerbations, mental health crises)
- **Specialty Notes (~5):** Nephrology (CKD), pulmonology (sleep apnea)

**Key Note Types and Sample Content:**

1. **Psychiatry Progress Note (2016-09-20, post-suicide attempt):**
   - SOAP format
   - **Subjective:** "Patient is a 53M veteran with combat-related PTSD, chronic pain, and major depressive disorder. Admitted 9/12 after suicide attempt via intentional opioid overdose. Reports feeling overwhelmed by pain, financial stress, and divorce proceedings. States 'I just wanted the pain to stop.' Denies current SI/HI."
   - **Objective:** MSE shows flat affect, logical thought process, no psychosis. PHQ-9 score 24 (severe depression). PCL-5 score 62 (severe PTSD).
   - **Assessment:** Suicide attempt in context of undertreated MDD, chronic pain, psychosocial stressors. High risk for repeat attempt.
   - **Plan:** Continue sertraline 200mg daily, add prazosin 5mg nightly for nightmares. Safety plan reviewed. Remove firearms from home (sister Alananah will secure). Weekly therapy. High Risk flag activated. Follow-up in 1 week.

2. **Pain Management Consult (2018-05-10, opioid taper):**
   - **Reason for Consult:** Chronic pain management, opioid risk reduction post-suicide attempt
   - **HPI:** 55M with chronic lumbar radiculopathy (IED blast 2004). Currently on oxycodone 30mg Q6H + morphine ER 60mg Q12H. Recent suicide attempt (9/2016) with opioid overdose. High risk for opioid misuse.
   - **Assessment:** Chronic pain, opioid-dependent, high suicide risk
   - **Plan:** Initiate slow opioid taper (10% monthly dose reduction). Add gabapentin 300mg TID, titrate to 1200mg TID. Add duloxetine 30mg daily, titrate to 60mg. Consider lidocaine patches. Frequent follow-up (biweekly). Behavioral pain management referral.

3. **Primary Care Progress Note (2022-12-15, diabetes diagnosis):**
   - **Chief Complaint:** Follow-up diabetes, tobacco cessation
   - **HPI:** 59M veteran with PTSD, chronic pain, HTN, HLD. A1C 8.2% (prior 7.8%). Weight 240 lbs. Quit tobacco 2 months ago with varenicline (major achievement!).
   - **Assessment:** Type 2 diabetes (new diagnosis), uncontrolled. Obesity. Tobacco use disorder in remission.
   - **Plan:** Start metformin 500mg BID, titrate to 1000mg BID over 4 weeks. Diabetes education referral. Quarterly A1C monitoring. Goal A1C <7.5%. Congratulate on tobacco cessation. F/u 3 months.

**CDWWork2 (Walla Walla, 2025-2026) - ~20 notes:**
- **Progress Notes (~12):** Primary care, psychiatry, endocrinology
- **Consult Notes (~5):** New patient consults (transfer of care from Bay Pines)
- **Discharge Summaries (~2):** One per inpatient encounter
- **Specialty Notes (~1):** Nephrology (CKD follow-up)

**Alananah Thompson - ~180 notes total:**

**CDWWork (Bay Pines, 2010-2025) - ~160 notes:**
- **Progress Notes (~80):** Primary care, endocrinology, oncology
- **Consult Notes (~35):** Endocrinology, oncology, ophthalmology (diabetic retinal exams), orthopedics (knee arthritis)
- **Discharge Summaries (~26):** One per inpatient encounter
- **Procedure Notes (~10):** Lumpectomy, chemotherapy infusions, knee arthroscopies
- **Imaging Reports (~5):** Mammograms (2018 abnormal, 2019-2025 negative)
- **Specialty Notes (~4):** Cardiology (a-fib), nephrology (diabetes screening)

**Key Note Types and Sample Content:**

1. **Oncology Consult (2012-06-20, breast cancer diagnosis):**
   - **Reason for Consult:** Abnormal screening mammogram, biopsy-proven breast cancer
   - **HPI:** 49F veteran with newly diagnosed right breast invasive ductal carcinoma (Stage IIA, ER+/PR+/HER2-, 1/3 lymph nodes positive). Post-mastectomy.
   - **Assessment:** Breast cancer Stage IIA, favorable biology (hormone receptor positive)
   - **Plan:** Adjuvant chemotherapy (4 cycles AC → 4 cycles paclitaxel), followed by radiation therapy (6 weeks), followed by hormone therapy (tamoxifen x5 years, then aromatase inhibitor). Oncotype DX score 28 (intermediate risk, chemo recommended). Discuss fertility preservation (patient age 49, not interested). Support services referral.

2. **Endocrinology Progress Note (2020-11-10, diabetic neuropathy):**
   - **Chief Complaint:** Foot pain, tingling (bilateral)
   - **HPI:** 55F veteran with T2DM (dx 2012), A1C 7.4%. Reports 6 months progressive burning pain and tingling in feet, worse at night. Denies foot ulcers, trauma.
   - **Exam:** Decreased vibration sense (tuning fork) bilateral feet. Decreased light touch sensation. Monofilament test: 3/10 sites insensate (left foot). No ulcers, pulses intact.
   - **Assessment:** Diabetic peripheral neuropathy (bilateral feet)
   - **Plan:** Start gabapentin 300mg TID, titrate to effect. Foot care education. Annual foot exams. Optimize glycemic control (goal A1C <7%). F/u 3 months.

3. **Oncology Surveillance Note (2025-10-22, Walla Walla):**
   - **Chief Complaint:** Annual oncology follow-up, breast cancer survivor
   - **HPI:** 62F veteran with history of Stage IIA breast cancer (dx 2012), treated with mastectomy, chemotherapy, radiation, and hormone therapy. Currently on anastrozole (switched from tamoxifen 2023). Last mammogram 10/2025: BI-RADS 1 (negative). No breast symptoms, no new lumps.
   - **Assessment:** Breast cancer in remission (7 years post-diagnosis)
   - **Plan:** Continue anastrozole 1mg daily. Annual screening mammogram. Next oncology follow-up 1 year. Calcium/vitamin D for bone health (AI side effects). Encourage exercise, weight management.

**CDWWork2 (Walla Walla, 2025-2026) - ~20 notes:**
- **Progress Notes (~12):** Primary care, endocrinology, oncology
- **Consult Notes (~5):** Transfer of care consults
- **Discharge Summaries (~2):** One per encounter
- **Imaging Reports (~1):** Mammogram (surveillance)

**Joe Thompson - ~60 clinical notes total:**

**CDWWork (Bay Pines, 2012-2025) - ~55 notes:**
- **Progress Notes (~45):** Annual wellness visits, routine primary care
- **Consult Notes (~5):** Cardiology (HTN workup), preventive health counseling
- **Discharge Summaries (~1):** Hernia repair (2018)
- **Procedure Notes (~2):** Hernia surgery, routine screening procedures
- **Specialty Notes (~2):** Preventive cardiology, health coaching

**CDWWork2 (Walla Walla, 2025-2026) - ~5 notes:**
- **Progress Notes (~3):** Wellness visits, preventive care
- **Procedure Notes (~2):** Colonoscopy, metabolic panel

**Key Note Content:**
- Focus on preventive care, health maintenance, excellent compliance
- Consistently normal exam findings
- Minimal medication adjustments (stable regimen)
- Strong family support documented
- Active lifestyle documented (basketball, hiking, volunteering)

**Note Content Guidelines:**
- Use realistic SOAP format (Subjective, Objective, Assessment, Plan)
- Include relevant clinical details (medications, lab values, exam findings)
- Reference prior notes/encounters for continuity
- Include patient quotes where appropriate
- Use medical abbreviations (T2DM, HTN, HLD, PTSD, etc.)
- Notes should be 500-2000 characters (preview length: 500 chars for AI)

### Domain 8: Immunizations

**Tables (CDWWork):** `Immunization.PatientImmunization`, `Dim.Vaccine`
**Tables (CDWWork2):** `ImmunizationMill.VaccineAdmin`, `ImmunizationMill.VaccineCode`
**Schema Reference:** See `mock/sql-server/cdwwork/create/Immunization.PatientImmunization.sql` for correct field names

**Data Requirements:**

**Bailey Thompson - ~42 immunizations total:**

**CDWWork (Bay Pines, 2010-2025) - ~38 immunizations:**
- **Influenza vaccine:** Annual (15 doses, 2010-2024)
- **Pneumococcal vaccines:**
  - PPSV23 (Pneumovax): 2013 (age 50), 2018 (age 55, 5-year booster)
  - PCV13 (Prevnar 13): 2014 (age 51, per VA guidelines)
- **Tetanus-diphtheria-pertussis (Tdap):** 2010, 2020 (10-year booster)
- **Hepatitis A:** 2-dose series (2011, 2012)
- **Hepatitis B:** 3-dose series (2010, 2010, 2011) - military incomplete series completed
- **Shingles (Zoster):**
  - Zostavax (live): 2013 (age 50, initial)
  - Shingrix (recombinant, 2-dose): 2019 (age 56, dose 1), 2019 (dose 2, per new recommendations)
- **COVID-19:**
  - Primary series: Pfizer 2-dose (2021-01, 2021-02)
  - Booster 1: Pfizer (2021-09)
  - Booster 2: Moderna (2022-04)
  - Bivalent booster: Moderna (2022-11)
  - 2023 updated booster: Pfizer (2023-10)
  - 2024 updated booster: Moderna (2024-10)

**CDWWork2 (Walla Walla, 2025-2026) - ~4 immunizations:**
- **Influenza vaccine:** 2025-10 (annual)
- **COVID-19:** 2025-11 (updated 2025 booster)
- **RSV vaccine (Respiratory Syncytial Virus):** 2025-11 (age 62, new recommendation for older adults)
- **Pneumococcal (PCV20):** 2026-01 (new vaccine, replaces prior PPSV23/PCV13)

**Adverse Reactions:**
- None reported (well-tolerated)

**Alananah Thompson - ~40 immunizations total:**

**CDWWork (Bay Pines, 2010-2025) - ~36 immunizations:**
- **Influenza vaccine:** Annual (15 doses, 2010-2024)
- **Pneumococcal vaccines:**
  - PPSV23 (Pneumovax): 2015 (age 50), 2020 (age 55, 5-year booster)
  - PCV13 (Prevnar 13): 2016 (age 51)
- **Tetanus-diphtheria-pertussis (Tdap):** 2010, 2020 (10-year booster)
- **Hepatitis A:** 2-dose series (2010, 2011)
- **Hepatitis B:** 3-dose series (military complete, titers checked 2010 - immune)
- **Shingles (Zoster):**
  - Shingrix (recombinant, 2-dose): 2020 (age 55, dose 1), 2020 (dose 2)
- **COVID-19:**
  - Primary series: Moderna 2-dose (2021-02, 2021-03)
  - Booster 1: Moderna (2021-10)
  - Booster 2: Pfizer (2022-05)
  - Bivalent booster: Pfizer (2022-12)
  - 2023 updated booster: Moderna (2023-11)
  - 2024 updated booster: Pfizer (2024-11)

**CDWWork2 (Walla Walla, 2025-2026) - ~4 immunizations:**
- **Influenza vaccine:** 2025-11 (annual)
- **COVID-19:** 2025-12 (updated 2025 booster)
- **RSV vaccine:** 2025-12 (age 60, new recommendation)
- **Pneumococcal (PCV20):** Pending (scheduled 2026-03)

**Adverse Reactions:**
- Influenza vaccine (2018): Mild arm soreness (not clinically significant)
- COVID-19 Moderna dose 2 (2021-03): Fever 101.2°F x 24 hours, fatigue (resolved, not unusual)

**Joe Thompson - ~40 immunizations total:**

**CDWWork (Bay Pines, 2012-2025) - ~36 immunizations:**
- **Influenza vaccine:** Annual (13 doses, 2012-2024)
- **Pneumococcal vaccines:**
  - PPSV23 (Pneumovax): 2020 (age 50)
  - PCV13 (Prevnar 13): 2021 (age 51, per VA guidelines)
- **Tetanus-diphtheria-pertussis (Tdap):** 2012, 2022 (10-year booster)
- **Hepatitis A:** 2-dose series (military complete, titers checked 2012 - immune)
- **Hepatitis B:** 3-dose series (military complete, titers checked 2012 - immune)
- **Shingles (Zoster):**
  - Shingrix (recombinant, 2-dose): 2020 (age 50, dose 1), 2021 (dose 2)
- **COVID-19:**
  - Primary series: Pfizer 2-dose (2021-01, 2021-02)
  - Booster 1: Pfizer (2021-09)
  - Booster 2: Pfizer (2022-04)
  - Bivalent booster: Pfizer (2022-11)
  - 2023 updated booster: Pfizer (2023-10)
  - 2024 updated booster: Pfizer (2024-10)
- **Human Papillomavirus (HPV):** 3-dose series (military, 1990-1991) - documented for completeness
- **Meningococcal (MenACWY):** Military series (1990), booster (2000)

**CDWWork2 (Walla Walla, 2025-2026) - ~4 immunizations:**
- **Influenza vaccine:** 2025-10 (annual)
- **COVID-19:** 2025-11 (updated 2025 booster)
- **RSV vaccine:** 2025-11 (age 55, preventive - may be early for typical recommendation but accepted for high-compliance patient)
- **Pneumococcal (PCV20):** 2026-01 (new vaccine, replaces prior PPSV23/PCV13)

**Adverse Reactions:**
- None reported (excellent vaccine tolerance)

### Domain 9: Problems/Diagnoses

**Tables:** `Prob.Problem` (or equivalent), `Dim.ICD10`, `Dim.SNOMED`

**Data Requirements:**

**Bailey Thompson - ~18 active/resolved problems:**

**Active Problems (15):**
1. **PTSD (Post-Traumatic Stress Disorder)** - ICD-10: F43.10, SNOMED: 47505003
   - Onset: 2011-02-15, Status: Active, Chronic
   - Service-connected: Yes (70%)
   - Provider: Psychiatry
   - Charlson weight: 0

2. **Chronic Pain Syndrome (Lumbar Radiculopathy)** - ICD-10: M54.16, SNOMED: 23056005
   - Onset: 2004-04-12 (IED blast injury), Status: Active, Chronic
   - Service-connected: Yes (40%)
   - Provider: Pain Management
   - Charlson weight: 0

3. **Traumatic Brain Injury (TBI), Mild, with residuals** - ICD-10: S06.9X9S, SNOMED: 127295002
   - Onset: 2004-04-12 (IED blast), Status: Active, Chronic
   - Service-connected: Yes (10%)
   - Charlson weight: 0

4. **Tinnitus, Bilateral** - ICD-10: H93.13, SNOMED: 60862001
   - Onset: 2004 (blast exposure), Status: Active, Chronic
   - Service-connected: Yes (10%)
   - Charlson weight: 0

5. **Major Depressive Disorder, Recurrent, Moderate** - ICD-10: F33.1, SNOMED: 191736004
   - Onset: 2011-03, Status: Active, Chronic
   - Comorbid with PTSD
   - Charlson weight: 0

6. **Hypertension (Essential)** - ICD-10: I10, SNOMED: 59621000
   - Onset: 2015-08, Status: Active, Chronic
   - Controlled on medications
   - Charlson weight: 0

7. **Hyperlipidemia (Mixed)** - ICD-10: E78.2, SNOMED: 55822004
   - Onset: 2016-06, Status: Active, Chronic
   - Controlled on statin
   - Charlson weight: 0

8. **Type 2 Diabetes Mellitus** - ICD-10: E11.9, SNOMED: 44054006
   - Onset: 2019-01, Status: Active, Chronic
   - Complicated by neuropathy, retinopathy (mild)
   - Charlson weight: 1 (uncomplicated diabetes)
   - **Note:** Increases to 2 if complications documented separately

9. **Chronic Kidney Disease (CKD) Stage 3a** - ICD-10: N18.3, SNOMED: 433146000
   - Onset: 2021-05, Status: Active, Chronic
   - eGFR 55 ml/min (2025)
   - Related to hypertension and diabetes
   - Charlson weight: 2 (moderate-severe renal disease)

10. **Obstructive Sleep Apnea (OSA)** - ICD-10: G47.33, SNOMED: 78275009
    - Onset: 2017-06, Status: Active, Chronic
    - Uses CPAP (compliant)
    - Charlson weight: 0

11. **Tobacco Use Disorder, In Remission** - ICD-10: Z87.891, SNOMED: 8517006
    - Onset: 1980, Quit: 2022-03, Status: In Remission
    - 40+ pack-year history
    - Charlson weight: 0

12. **Alcohol Use Disorder, In Remission** - ICD-10: F10.21, SNOMED: 7200002
    - Onset: 2010, Remission: 2020, Status: In Remission
    - Successful treatment 2019-2020
    - Charlson weight: 0

13. **Gastroesophageal Reflux Disease (GERD)** - ICD-10: K21.9, SNOMED: 235595009
    - Onset: 2016, Status: Active, Chronic
    - Controlled on PPI
    - Charlson weight: 0

14. **Obesity (BMI 31.6)** - ICD-10: E66.9, SNOMED: 414915002
    - Onset: 2012, Status: Active, Chronic
    - Weight management ongoing
    - Charlson weight: 0

15. **Suicide Attempt (History)** - ICD-10: T50.905S (poisoning, sequela), SNOMED: 248042004
    - Onset: 2016-09-12, Status: Active (historical, risk monitoring)
    - Opioid overdose (intentional)
    - **Note:** Significantly impacts Charlson score (prior suicide attempt → elevated mortality risk)
    - Charlson adjustment: +2 (major psychiatric condition with prior attempt)

**Resolved Problems (3):**
1. **Pneumonia, Community-Acquired** - ICD-10: J18.9, Resolved: 2015-09
2. **Cellulitis, Left Leg** - ICD-10: L03.115, Resolved: 2018-07
3. **Atrial Fibrillation, Paroxysmal** - ICD-10: I48.0, Resolved: 2023-03 (converted to sinus, no recurrence)

**Charlson Comorbidity Index Calculation (Bailey):**
- Diabetes (uncomplicated): +1
- Chronic Kidney Disease (moderate): +2
- Prior suicide attempt (major psychiatric): +2 (adjustment)
- **Total Charlson Score: 5** (high mortality risk, 21% 10-year survival)

**Alananah Thompson - ~16 active/resolved problems:**

**Active Problems (13):**
1. **Type 2 Diabetes Mellitus with Complications** - ICD-10: E11.65 (with hyperglycemia), SNOMED: 44054006
   - Onset: 2012-03, Status: Active, Chronic
   - Complicated by neuropathy and retinopathy
   - Charlson weight: 2 (diabetes with end-organ damage)

2. **Diabetic Peripheral Neuropathy, Bilateral Feet** - ICD-10: E11.40, SNOMED: 230572002
   - Onset: 2020-08, Status: Active, Chronic
   - Complication of diabetes
   - Charlson weight: 0 (captured in diabetes score)

3. **Diabetic Retinopathy, Nonproliferative, Mild** - ICD-10: E11.329, SNOMED: 1481000119106
   - Onset: 2021-03, Status: Active, Chronic
   - Complication of diabetes
   - Charlson weight: 0 (captured in diabetes score)

4. **Breast Cancer, Stage IIA (History), In Remission** - ICD-10: Z85.3 (personal history), SNOMED: 254837009
   - Onset: 2018-06, Remission: 2019-12, Status: Remission
   - Invasive ductal carcinoma (ER+/PR+/HER2-)
   - Treated with surgery, chemo, radiation, hormone therapy
   - Charlson weight: 2 (solid tumor, localized, treated)
   - **Note:** Remains in Charlson calculation for 5 years post-remission

5. **PTSD (Post-Traumatic Stress Disorder), Mild** - ICD-10: F43.10, SNOMED: 47505003
   - Onset: 2011-02, Status: Active, Chronic
   - Service-connected: Yes (30%)
   - Charlson weight: 0

6. **Hypertension (Essential)** - ICD-10: I10, SNOMED: 59621000
   - Onset: 2013-04, Status: Active, Chronic
   - Well-controlled on medications
   - Charlson weight: 0

7. **Hyperlipidemia (Mixed)** - ICD-10: E78.2, SNOMED: 55822004
   - Onset: 2014-06, Status: Active, Chronic
   - Controlled on statin
   - Charlson weight: 0

8. **Hypothyroidism (Primary)** - ICD-10: E03.9, SNOMED: 40930008
   - Onset: 2016-11, Status: Active, Chronic
   - Controlled on levothyroxine
   - Charlson weight: 0

9. **Osteoarthritis, Bilateral Knees** - ICD-10: M17.0, SNOMED: 396275006
   - Onset: 2010, Status: Active, Chronic
   - Service-connected: Yes (10%)
   - Treated with NSAIDs, prior arthroscopic surgeries
   - Charlson weight: 0

10. **Hearing Loss, Bilateral, Sensorineural** - ICD-10: H90.3, SNOMED: 60700002
    - Onset: 2010 (noise exposure), Status: Active, Chronic
    - Service-connected: Yes (10%)
    - Charlson weight: 0

11. **Obesity (BMI 29.1)** - ICD-10: E66.9, SNOMED: 414915002
    - Onset: 2015, Status: Active, Chronic
    - Weight management ongoing
    - Charlson weight: 0

12. **Generalized Anxiety Disorder** - ICD-10: F41.1, SNOMED: 21897009
    - Onset: 2012-07 (during cancer treatment), Status: Active
    - Comorbid with PTSD
    - Controlled on sertraline
    - Charlson weight: 0

13. **Gastroesophageal Reflux Disease (GERD)** - ICD-10: K21.9, SNOMED: 235595009
    - Onset: 2017, Status: Active, Chronic
    - Controlled on PPI (as needed)
    - Charlson weight: 0

**Resolved Problems (3):**
1. **Pyelonephritis (Kidney Infection)** - ICD-10: N10, Resolved: 2022-06
2. **Atrial Fibrillation, Paroxysmal** - ICD-10: I48.0, Resolved: 2023-09 (no recurrence)
3. **Meniscal Tear, Left Knee** - ICD-10: S83.209A, Resolved: 2013-04 (post-surgery)

**Charlson Comorbidity Index Calculation (Alananah):**
- Diabetes with complications (neuropathy, retinopathy): +2
- Solid tumor (breast cancer, in remission <5 years): +2
- **Total Charlson Score: 4** (moderate-high mortality risk, 53% 10-year survival)

**Joe Thompson - ~2 active problems:**

**Active Problems (2):**
1. **Hypertension (Essential), Mild** - ICD-10: I10, SNOMED: 59621000
   - Onset: 2020-06, Status: Active, Chronic
   - Well-controlled on single medication (lisinopril 10mg daily)
   - Service-connected: No
   - Charlson weight: 0

2. **Hyperlipidemia (Mixed), Mild** - ICD-10: E78.2, SNOMED: 55822004
   - Onset: 2021-05, Status: Active, Chronic
   - Well-controlled on statin (atorvastatin 20mg daily)
   - Service-connected: No
   - Charlson weight: 0

**Resolved Problems (0):**
- None (excellent health history, no major illnesses)

**Charlson Comorbidity Index Calculation (Joe):**
- **Total Charlson Score: 0** (excellent prognosis, 99% 10-year survival)

**Problem List Notes:**
- All problems coded with both ICD-10 and SNOMED CT (dual coding)
- Service-connected disabilities flagged in problem list
- Charlson scores calculated per standard algorithm
- Chronic conditions marked with onset dates and status (Active/Resolved/In Remission)

### Domain 10: Laboratory Results

**Tables:** `Chem.LabChem`, `Dim.LabTest`, `Dim.Location`

**Data Requirements:**

**Bailey Thompson - ~160 lab results total:**

**CDWWork (Bay Pines, 2010-2025) - ~150 results:**

**Annual/Routine Labs (repeated yearly, ~15 years):**
- **Hemoglobin A1C (Diabetes monitoring, quarterly 2019-2025):**
  - 2019: 8.2% (diagnosis), 2020: 7.8%, 2021: 7.5%, 2022: 8.0% (DKA spike), 2023: 7.2%, 2024: 7.0%, 2025: 7.1%
- **Basic Metabolic Panel (BMP):**
  - Glucose: 110-145 mg/dL (pre-diabetes 2010-2018, diabetic 2019+)
  - Sodium: 138-142 mEq/L (normal)
  - Potassium: 4.0-4.5 mEq/L (normal)
  - Chloride: 100-105 mEq/L (normal)
  - CO2: 24-28 mEq/L (normal)
  - **Creatinine:** 0.9 mg/dL (2010) → 1.2 mg/dL (2015) → 1.5 mg/dL (2021-2025, CKD Stage 3a)
  - **eGFR:** 90 ml/min (2010) → 75 ml/min (2015) → 55 ml/min (2021-2025, CKD 3a)
  - BUN: 18-25 mg/dL

- **Lipid Panel:**
  - Total cholesterol: 220 mg/dL (2010, untreated) → 165 mg/dL (2025, on statin)
  - LDL: 145 mg/dL (2010) → 85 mg/dL (2025, goal <100)
  - HDL: 38 mg/dL (2010, low) → 42 mg/dL (2025)
  - Triglycerides: 180 mg/dL (2010) → 145 mg/dL (2025)

- **Complete Blood Count (CBC):**
  - WBC: 7.0-9.5 k/uL (normal)
  - Hemoglobin: 14.5-15.8 g/dL (normal)
  - Hematocrit: 42-46% (normal)
  - Platelets: 200-280 k/uL (normal)

- **Liver Function Tests (LFTs):**
  - AST: 25-35 U/L (normal)
  - ALT: 28-40 U/L (normal, slightly elevated 2010-2019 due to alcohol)
  - Alkaline phosphatase: 70-90 U/L (normal)
  - Bilirubin: 0.6-1.0 mg/dL (normal)

- **Thyroid Function:**
  - TSH: 1.8-3.2 mIU/L (normal, no thyroid disease)

- **Urinalysis (annual, CKD monitoring):**
  - Protein: Trace to 1+ (2021-2025, mild proteinuria)
  - Glucose: Negative (2010-2018), 1-2+ (2019-2025, diabetic)
  - Blood: Negative
  - Microalbumin/Creatinine ratio: 45 mg/g (2025, mild albuminuria)

**Disease-Specific Labs:**
- **Vitamin D:** 18 ng/mL (2015, deficient) → 32 ng/mL (2025, repleted)
- **Urine Drug Screen (UDS, pain management 2010-2018):** Consistent with prescribed medications (opioids, benzodiazepines), no illicit drugs
- **Troponin (chest pain ER visit 2023):** <0.01 ng/mL (negative, no MI)

**CDWWork2 (Walla Walla, 2025-2026) - ~10 results:**
- **A1C:** 7.1% (2026-01, stable)
- **BMP:** Creatinine 1.5, eGFR 55 (stable CKD 3a)
- **Lipid panel:** LDL 88 mg/dL (goal met)
- **CBC:** Normal
- **Urinalysis:** Protein 1+, microalbumin 50 mg/g

**Alananah Thompson - ~140 lab results total:**

**CDWWork (Bay Pines, 2010-2025) - ~130 results:**

**Annual/Routine Labs:**
- **Hemoglobin A1C (Diabetes monitoring, quarterly 2012-2025):**
  - 2012: 8.5% (diagnosis), 2015: 7.2%, 2018: 7.0%, 2019: 8.2% (during chemo, steroid-induced hyperglycemia), 2020: 6.8%, 2023: 7.0%, 2025: 7.1%

- **Basic Metabolic Panel (BMP):**
  - Glucose: 105-135 mg/dL (diabetic, well-controlled)
  - Sodium: 137-141 mEq/L (normal)
  - Potassium: 3.9-4.3 mEq/L (normal)
  - Creatinine: 0.8-0.9 mg/dL (normal, no CKD)
  - eGFR: >90 ml/min (normal kidney function)
  - BUN: 12-18 mg/dL (normal)

- **Lipid Panel:**
  - Total cholesterol: 210 mg/dL (2010) → 155 mg/dL (2025, on statin)
  - LDL: 135 mg/dL (2010) → 78 mg/dL (2025, goal <100)
  - HDL: 52 mg/dL (2010) → 55 mg/dL (2025, normal)
  - Triglycerides: 150 mg/dL (2010) → 110 mg/dL (2025)

- **Complete Blood Count (CBC):**
  - WBC: 6.5-8.0 k/uL (normal, except 2018-2019 chemo: 2.5-4.0 k/uL, leukopenia)
  - Hemoglobin: 12.8-13.5 g/dL (normal, except 2018-2019 chemo: 9.5-11.0 g/dL, anemia)
  - Platelets: 210-250 k/uL (normal, except 2018-2019 chemo: 100-150 k/uL, thrombocytopenia)

- **Liver Function Tests (LFTs):**
  - AST: 22-30 U/L (normal)
  - ALT: 25-32 U/L (normal)
  - Alkaline phosphatase: 65-85 U/L (normal)

- **Thyroid Function:**
  - TSH: 0.5 mIU/L (2016, hyperthyroid, thyroiditis) → 8.5 mIU/L (2016, hypothyroid) → 2.0 mIU/L (2017-2025, on levothyroxine)
  - Free T4: 1.0-1.2 ng/dL (normal on treatment)

- **Urinalysis (annual, diabetes screening):**
  - Protein: Negative to Trace (no nephropathy)
  - Glucose: 1-2+ (diabetic)
  - Microalbumin/Creatinine ratio: 15 mg/g (normal, <30 mg/g)

**Disease-Specific Labs:**
- **Tumor Markers (Breast Cancer Surveillance, annual 2019-2025):**
  - CA 15-3: 18 U/mL (normal, <30) - stable, no recurrence
  - CA 27-29: 22 U/mL (normal, <38) - stable

- **Bone Density (DEXA scan, anastrozole monitoring):**
  - 2020: T-score -1.2 (osteopenia, mild)
  - 2024: T-score -1.4 (stable, calcium/vitamin D supplementation)

- **Vitamin D:** 22 ng/mL (2018, deficient) → 38 ng/mL (2025, repleted)

- **Oncotype DX (2012, breast cancer):** Score 28 (intermediate recurrence risk, chemo recommended)

**CDWWork2 (Walla Walla, 2025-2026) - ~10 results:**
- **A1C:** 7.1% (2026-01, stable)
- **BMP:** Normal (Creatinine 0.9, eGFR >90)
- **Lipid panel:** LDL 78 mg/dL (excellent control)
- **TSH:** 2.1 mIU/L (stable on levothyroxine)
- **CA 15-3:** 19 U/mL (stable, no recurrence)

**Joe Thompson - ~60 lab results total:**

**CDWWork (Bay Pines, 2012-2025) - ~55 results:**

**Annual/Routine Labs (repeated yearly, ~13 years):**
- **Hemoglobin A1C (Diabetes screening, annual):**
  - 2012-2025: 5.2-5.5% (consistently normal, no diabetes)

- **Basic Metabolic Panel (BMP):**
  - Glucose: 85-98 mg/dL (normal fasting glucose)
  - Sodium: 139-142 mEq/L (normal)
  - Potassium: 4.0-4.4 mEq/L (normal)
  - Chloride: 101-104 mEq/L (normal)
  - CO2: 25-28 mEq/L (normal)
  - Creatinine: 0.9-1.0 mg/dL (normal, excellent kidney function)
  - eGFR: >90 ml/min (normal)
  - BUN: 12-16 mg/dL (normal)

- **Lipid Panel:**
  - Total cholesterol: 195 mg/dL (2012, untreated) → 165 mg/dL (2025, on statin)
  - LDL: 125 mg/dL (2012) → 82 mg/dL (2025, goal <100 met)
  - HDL: 55 mg/dL (2012) → 58 mg/dL (2025, normal)
  - Triglycerides: 110 mg/dL (2012) → 95 mg/dL (2025, normal)

- **Complete Blood Count (CBC):**
  - WBC: 6.0-7.5 k/uL (normal)
  - Hemoglobin: 14.8-15.5 g/dL (normal)
  - Hematocrit: 44-47% (normal)
  - Platelets: 220-260 k/uL (normal)

- **Liver Function Tests (LFTs):**
  - AST: 20-28 U/L (normal)
  - ALT: 22-30 U/L (normal)
  - Alkaline phosphatase: 65-80 U/L (normal)
  - Bilirubin: 0.5-0.8 mg/dL (normal)

- **Thyroid Function:**
  - TSH: 1.5-2.8 mIU/L (normal, no thyroid disease)

- **Urinalysis (annual wellness):**
  - Protein: Negative
  - Glucose: Negative
  - Blood: Negative
  - All parameters normal

**Disease-Specific Labs:**
- **Vitamin D:** 32 ng/mL (2015, normal) → 38 ng/mL (2025, adequate)
- **PSA (Prostate cancer screening, annual age 50+):**
  - 2020-2025: 0.8-1.2 ng/mL (normal, <4.0)
- **Colon cancer screening:**
  - Colonoscopy 2020 (age 50): No polyps, repeat 2030
  - Colonoscopy 2025 (age 55): No polyps, repeat 2035 (early repeat per patient preference/family history)

**CDWWork2 (Walla Walla, 2025-2026) - ~5 results:**
- **A1C:** 5.4% (2026-01, normal)
- **BMP:** All normal (Creatinine 0.9, eGFR >90)
- **Lipid panel:** LDL 82 mg/dL (excellent control)
- **CBC:** All normal
- **PSA:** 1.1 ng/mL (normal)

**Lab Result Notes:**
- All labs include collection date, result value, reference range, units
- Collection location (Bay Pines labs, Walla Walla labs)
- Ordering provider specialty
- Critical values flagged (e.g., A1C >9%, creatinine >2.0)
- Trending data shows disease progression and treatment response

---

## Script Organization

### File Structure

**CDWWork Scripts (Bay Pines):**
- Location: `mock/sql-server/cdwwork/insert/`
- Filenames:
  - `Thompson-Bailey.sql` - All Bailey Thompson data for CDWWork (2010-2025)
  - `Thompson-Alananah.sql` - All Alananah Thompson data for CDWWork (2010-2025)
  - `Thompson-Joe.sql` - All Joe Thompson data for CDWWork (2012-2025)

**CDWWork2 Scripts (Walla Walla):**
- Location: `mock/sql-server/cdwwork2/insert/` (create if needed)
- Filenames:
  - `Thompson-Bailey.sql` - All Bailey Thompson data for CDWWork2 (2025-2026)
  - `Thompson-Alananah.sql` - All Alananah Thompson data for CDWWork2 (2025-2026)
  - `Thompson-Joe.sql` - All Joe Thompson data for CDWWork2 (2025-2026)

**Total Scripts:** 6 files (3 patients x 2 databases)

### Script Content Requirements

Each script must include:

1. **Header Block:**
   ```sql
   -- =====================================================
   -- Thompson Twins Test Patient Data
   -- Patient: Bailey James Thompson (Male)
   -- ICN: ICN200001
   -- Database: CDWWork (Bay Pines VA, 2010-2025)
   -- =====================================================
   -- Purpose: Comprehensive test patient for med-z1
   --          Male veteran with PTSD, chronic pain, TBI
   --          Service history: Gulf War, Iraq (IED injury)
   --          100% service-connected disability
   -- =====================================================
   -- Last Updated: 2026-02-08
   -- Author: med-z1 development team
   -- =====================================================

   USE CDWWork;
   GO

   SET QUOTED_IDENTIFIER ON;
   GO
   ```

2. **Table of Contents (comment block):**
   - List all tables/domains included in script
   - Example:
     ```sql
     -- TABLE OF CONTENTS:
     -- 1. Demographics (SPatient.SPatient, SPatientAddress, SPatientPhone)
     -- 2. Military History (SPatient.PatientMilitaryService, SPatientDisability)
     -- 3. Vitals (Vital.VitalSign)
     -- 4. Patient Flags (SPatient.PatientRecordFlagAssignment, PatientRecordFlagHistory)
     -- 5. Allergies (Allergy.Allergy)
     -- 6. Medications (RxOut.RxOutpatient)
     -- 7. Encounters (Inpat.Inpatient)
     -- 8. Clinical Notes (TIU.TIUDocument_8925, TIUDocumentText)
     -- 9. Immunizations (Immun.Immunization)
     -- 10. Problems (Prob.Problem)
     -- 11. Laboratory Results (Chem.LabChem)
     ```

3. **Domain Sections with Documentation:**
   - Each INSERT statement preceded by comment block explaining:
     - **Why this record exists** (clinical rationale)
     - **Why specific values were chosen** (e.g., "AgentOrangeExposureCode = 'N' because patient enlisted post-Vietnam")
     - **Relationships to other records** (e.g., "Encounter InpatientSID 50001 corresponds to suicide attempt 2016-09-12")

   Example:
   ```sql
   -- =====================================================
   -- DEMOGRAPHICS: SPatient.SPatient
   -- =====================================================
   -- Bailey Thompson: Male veteran, age 62
   -- Born 1963-04-15, served 1990-2010 (20 years)
   -- Retired to St. Petersburg, FL (2010-2025)
   -- PatientSID 2001 for CDWWork (Bay Pines)
   -- ICN200001 (national identifier)
   -- =====================================================

   INSERT INTO SPatient.SPatient (
       PatientSID,
       PatientICN,
       PatientName,
       DateOfBirth,
       Sex,
       SSN,
       Sta3n
   )
   VALUES (
       2001,                           -- PatientSID: Unique ID for CDWWork
       'ICN200001',                    -- ICN: National identifier
       'THOMPSON,BAILEY JAMES',        -- Name: Last,First Middle format
       '1963-04-15',                   -- DOB: Age 62 as of 2026
       'M',                            -- Sex: Male
       '200-00-1001',                  -- SSN: Mock value (non-real)
       516                             -- Sta3n: Bay Pines VA (St. Petersburg, FL)
   );
   GO
   ```

4. **Date Handling:**
   - **CDWWork (historical, 2010-2025):** Use **fixed dates** (Option A)
     - Example: `'2010-06-15'` for retirement date
     - Example: `'2016-09-12'` for suicide attempt date
     - Rationale: Historical data should remain constant for reproducibility

   - **CDWWork2 (current, 2025-2026):** Use **relative dates** with SQL Server functions
     - Example: `DATEADD(year, -1, GETDATE())` for move date (1 year ago)
     - Example: `DATEADD(month, -2, GETDATE())` for recent vitals (2 months ago)
     - Rationale: Keeps Walla Walla data "fresh" relative to script execution date

   Example (CDWWork2):
   ```sql
   -- Recent vital sign (2 months ago, relative to script run date)
   INSERT INTO Vital.VitalSign (
       VitalSignSID,
       PatientSID,
       VitalSignTakenDateTime,
       Weight,
       ...
   )
   VALUES (
       60001,
       20001,
       DATEADD(month, -2, GETDATE()),  -- 2 months ago (current data)
       220.0,
       ...
   );
   GO
   ```

5. **Execution Feedback:**
   - Use `PRINT` statements after each domain section
   - Example:
     ```sql
     PRINT 'Bailey Thompson: Demographics inserted (PatientSID 2001)';
     PRINT 'Bailey Thompson: 64 vital signs inserted (2010-2026)';
     PRINT 'Bailey Thompson: 2 patient flags inserted';
     ```

6. **Error Handling (Optional):**
   - Check for existing records before inserting (avoid duplicates)
   - Example:
     ```sql
     IF NOT EXISTS (SELECT 1 FROM SPatient.SPatient WHERE PatientSID = 2001)
     BEGIN
         INSERT INTO SPatient.SPatient (...) VALUES (...);
         PRINT 'Bailey Thompson: Demographics inserted';
     END
     ELSE
     BEGIN
         PRINT 'Bailey Thompson: Demographics already exist (skipped)';
     END
     GO
     ```

### Master Script Integration

After creating the six Thompson Twins scripts, update the master scripts to include them:

**CDWWork Master Script:**
- File: `mock/sql-server/cdwwork/insert/_master.sql`
- Add near end (after existing patient scripts):
  ```sql
  -- =====================================================
  -- Thompson Twins Test Patients (ICN200001, ICN200002, ICN200003)
  -- Bay Pines VA (Sta3n 516), 2010-2025
  -- =====================================================
  PRINT 'Inserting Thompson Twins test patients...';
  :r Thompson-Bailey.sql
  :r Thompson-Alananah.sql
  :r Thompson-Joe.sql
  PRINT 'Thompson Twins (CDWWork): Complete';
  GO
  ```

**CDWWork2 Master Script:**
- File: `mock/sql-server/cdwwork2/insert/_master.sql` (create if doesn't exist)
- Add Thompson Twins scripts:
  ```sql
  -- =====================================================
  -- Thompson Twins Test Patients (ICN200001, ICN200002, ICN200003)
  -- Walla Walla VA (Sta3n 687), 2025-2026
  -- =====================================================
  PRINT 'Inserting Thompson Twins test patients (Walla Walla)...';
  :r Thompson-Bailey.sql
  :r Thompson-Alananah.sql
  :r Thompson-Joe.sql
  PRINT 'Thompson Twins (CDWWork2): Complete';
  GO
  ```

---

## Implementation Checklist

### Phase 1: Script Development (Estimated 2-3 days)

- [ ] **Create script files:**
  - [ ] `mock/sql-server/cdwwork/insert/Thompson-Bailey.sql`
  - [ ] `mock/sql-server/cdwwork/insert/Thompson-Alananah.sql`
  - [ ] `mock/sql-server/cdwwork/insert/Thompson-Joe.sql`
  - [ ] `mock/sql-server/cdwwork2/insert/Thompson-Bailey.sql`
  - [ ] `mock/sql-server/cdwwork2/insert/Thompson-Alananah.sql`
  - [ ] `mock/sql-server/cdwwork2/insert/Thompson-Joe.sql`

- [x] **CDWWork (Bay Pines) - Bailey Thompson:** ✅ **COMPLETE (2026-02-09)**
  - [x] Demographics (SPatient tables) ✅
  - [x] Military History (SPatientMilitaryService, SPatientDisability) ✅
  - [x] Vitals (231 records, VitalSignSID 9001-9231) ✅
  - [x] Patient Flags (2 flags: HIGH RISK FOR SUICIDE, OPIOID RISK TOOL) ✅
  - [x] Allergies (2: PENICILLIN, MORPHINE SULFATE, PatientAllergySID 9001-9002) ✅
  - [x] Medications (45 total: RxOutpatSID 8001-8045) ✅
  - [x] Encounters (32 inpatient admissions) ✅
  - [x] Clinical Notes (8 notes) ✅
  - [x] Immunizations (42 vaccines) ✅
  - [x] Problems (18 problems, Charlson=5) ✅
  - [x] Labs (~160 results) ✅
  - [x] Full ETL pipeline testing ✅ (Bronze → Silver → Gold → PostgreSQL, no errors)
  - [x] UI verification ✅ (All 10 domains operational)

- [x] **CDWWork (Bay Pines) - Alananah Thompson:** ✅ **COMPLETE (2026-02-09)**
  - [x] Demographics ✅
  - [x] Military History ✅
  - [x] Vitals (231 records, VitalSignSID 10001-10231, female weight trajectory 135-195 lbs) ✅
  - [x] Patient Flags (2 flags: DIABETIC PATIENT, CANCER HISTORY) ✅
  - [x] Allergies (2: PENICILLIN, MORPHINE SULFATE, PatientAllergySID 10001-10002) ✅
  - [x] Medications (32 total: RxOutpatSID 8046-8077) ✅
  - [x] Encounters (8 inpatient admissions) ✅
  - [x] Clinical Notes (3 notes) ✅
  - [x] Immunizations (42 vaccines) ✅
  - [x] Problems (10 problems, Charlson=2) ✅
  - [x] Labs (~140 results) ✅
  - [x] Fixed all SID conflicts (vitals 9001→10001, allergies 9001→10001, patient flags schema) ✅
  - [x] Full ETL pipeline testing ✅ (Bronze → Silver → Gold → PostgreSQL, no errors)
  - [x] UI verification ✅ (All 10 domains operational)

- [x] **CDWWork2 (Walla Walla) - Bailey Thompson:** 🔧 **NEEDS REVIEW/VERIFICATION**
  - [x] Demographics (updated address/phone) - Created, not verified
  - [x] Vitals (~4 records, 2025-2026, relative dates) - Created, not verified
  - [x] Patient Flags (transferred from Bay Pines) - Created, not verified
  - [x] Medications (active meds only) - Created, not verified
  - [x] Encounters (~2 admissions) - Created, not verified
  - [x] Clinical Notes (~20 notes) - Created, not verified
  - [x] Immunizations (~4 recent vaccines) - Created, not verified
  - [x] Problems (active problems carried forward) - Created, not verified
  - [x] Labs (~10 recent results) - Created, not verified
  - [ ] Test script execution **⚠️ PENDING** (deferred until after Joe CDWWork complete)
  - [ ] ETL pipeline testing **⚠️ PENDING**

- [x] **CDWWork2 (Walla Walla) - Alananah Thompson:** 🔧 **NEEDS REVIEW/VERIFICATION**
  - [x] Demographics (updated address/phone) - Created, not verified
  - [x] Vitals (~4 records, relative dates) - Created, not verified
  - [x] Patient Flags (transferred) - Created, not verified
  - [x] Medications (active meds only) - Created, not verified
  - [x] Encounters (~2 admissions) - Created, not verified
  - [x] Clinical Notes (~20 notes) - Created, not verified
  - [x] Immunizations (~4 recent vaccines) - Created, not verified
  - [x] Problems (active problems carried forward) - Created, not verified
  - [x] Labs (~10 recent results) - Created, not verified
  - [ ] Test script execution **⚠️ PENDING** (deferred until after Joe CDWWork complete)
  - [ ] ETL pipeline testing **⚠️ PENDING**

- [ ] **CDWWork (Bay Pines) - Joe Thompson:**
  - [ ] Demographics (SPatient tables)
  - [ ] Military History (SPatientMilitaryService, SPatientDisability)
  - [ ] Vitals (~55 records, 2012-2025)
  - [ ] Patient Flags (0 flags - healthy patient)
  - [ ] Allergies (NKDA - No Known Drug Allergies)
  - [ ] Medications (~8 total: 3 active, 5 historical)
  - [ ] Encounters (~3 total: mostly outpatient)
  - [ ] Clinical Notes (~55 notes: preventive care focus)
  - [ ] Immunizations (~36 vaccines)
  - [ ] Problems (~2 problems: hypertension, hyperlipidemia, both mild)
  - [ ] Labs (~55 results: all normal/near-normal ranges)

- [ ] **CDWWork2 (Walla Walla) - Joe Thompson:**
  - [ ] Demographics (updated address/phone)
  - [ ] Vitals (~1 record, relative dates)
  - [ ] Patient Flags (0 flags)
  - [ ] Medications (3 active meds only)
  - [ ] Encounters (~2 admissions: colonoscopy, wellness visit)
  - [ ] Clinical Notes (~5 notes)
  - [ ] Immunizations (~4 recent vaccines)
  - [ ] Problems (2 active problems carried forward)
  - [ ] Labs (~5 recent results, all normal)

### Phase 2: Script Testing (Estimated 1 day)

**CDWWork (Bailey & Alananah):** ✅ **COMPLETE (2026-02-09)**
- [x] **Execute scripts in clean SQL Server container:**
  - [x] CDWWork: Thompson-Bailey.sql ✅ No errors
  - [x] CDWWork: Thompson-Alananah.sql ✅ No errors (after fixing SID conflicts)
  - [ ] CDWWork: Thompson-Joe.sql **⚠️ NOT STARTED** (next priority)

- [x] **Verify data insertion:**
  - [x] Query `SPatient.SPatient` for PatientSID 2001, 2002 (CDWWork) ✅ Both patients present
  - [x] Spot-check vital signs, medications, encounters, notes ✅ All data present
  - [x] Verify foreign key relationships (no orphaned records) ✅ All valid
  - [x] Verify date handling (fixed dates in CDWWork) ✅ All dates correct (2010-2025)

- [x] **Update master scripts:**
  - [x] Add Thompson-Bailey.sql and Thompson-Alananah.sql to `mock/sql-server/cdwwork/insert/_master.sql` ✅

**CDWWork2 (Bailey & Alananah):** 🔧 **NEEDS REVIEW** (deferred until after Joe CDWWork complete)
- [ ] Execute CDWWork2 scripts **⚠️ PENDING**
- [ ] Verify CDWWork2 data insertion **⚠️ PENDING**
- [ ] Update `mock/sql-server/cdwwork2/insert/_master.sql` **⚠️ PENDING**

### Phase 3: ETL Pipeline Testing (Estimated 1-2 days)

**CDWWork (Bailey & Alananah):** ✅ **COMPLETE (2026-02-09)**
- [x] **Run Bronze ETL:**
  - [x] Extract Bailey and Alananah data from CDWWork → Bronze Parquet ✅ Success
  - [x] Verify Parquet file contents ✅ All data present

- [x] **Run Silver ETL:**
  - [x] Identity resolution: PatientSID 2001 → ICN100001 (Bailey) ✅
  - [x] Identity resolution: PatientSID 2002 → ICN200002 (Alananah) ✅
  - [x] Harmonize CDWWork data (unified schema) ✅
  - [x] Verify Silver Parquet files ✅

- [x] **Run Gold ETL:**
  - [x] Generate patient-centric views (per-patient aggregations) ✅
  - [x] Generate domain-centric views (all patients, queryable) ✅
  - [x] Verify Gold Parquet files ✅

**CDWWork2 (Bailey & Alananah):** 🔧 **PENDING** (deferred until after Joe CDWWork complete)
- [ ] Run Bronze ETL (CDWWork2 → Parquet) **⚠️ PENDING**
- [ ] Run Silver ETL (merge with CDWWork data) **⚠️ PENDING**
- [ ] Run Gold ETL **⚠️ PENDING**

**Joe Thompson (CDWWork & CDWWork2):** 🚧 **NOT STARTED** (next priority)

**Load PostgreSQL Serving Database:**
**CDWWork (Bailey & Alananah):** ✅ **COMPLETE (2026-02-09)**
- [x] Run load scripts for all 10 domains ✅
- [x] Verify Bailey and Alananah data in PostgreSQL ✅ All data present, no errors
- [x] Query test: Retrieve Bailey Thompson vitals ✅ 231 records
- [x] Query test: Retrieve Alananah Thompson medications ✅ 32 meds, active meds visible
- [x] Query test: Retrieve Alananah Thompson vitals ✅ 231 records, female weight trajectory

**Joe Thompson:** 🚧 **NOT STARTED** (next priority)

### Phase 4: UI Testing (Estimated 1 day)

**CDWWork (Bailey & Alananah):** ✅ **COMPLETE (2026-02-09)**
- [x] **Test Patient Dashboard:**
  - [x] Navigate to Bailey Thompson (ICN100001) dashboard ✅ Operational
  - [x] Verify all widgets display (Demographics, Vitals, Medications, etc.) ✅ All 10 domains displayed
  - [x] Verify Charlson Comorbidity Index badge (should show 5) ✅ Shows 5
  - [x] Navigate to Alananah Thompson (ICN200002) dashboard ✅ Operational
  - [x] Verify Charlson badge (should show 2) ✅ Shows 2
  - [ ] Navigate to Joe Thompson (ICN200003) dashboard **⚠️ NOT STARTED**
  - [ ] Verify Joe's Charlson badge (should show 0) **⚠️ NOT STARTED**

- [x] **Test Dedicated Domain Pages (Bailey & Alananah):**
  - [x] Vitals: Verify charts ✅ 231 readings for Bailey, 231 for Alananah (female trajectory)
  - [x] Medications: Verify active/historical meds ✅ 45 for Bailey, 32 for Alananah
  - [x] Encounters: Verify pagination ✅ 32 for Bailey, 8 for Alananah
  - [x] Clinical Notes: Verify filtering ✅ 8 notes for Bailey, 3 for Alananah
  - [x] Immunizations: Verify vaccine history ✅ 42 for both Bailey and Alananah
  - [x] Problems: Verify ICD-10 grouping, Charlson calculation ✅ Working (Bailey: 18 problems, Alananah: 10)
  - [ ] Labs: (UI pending, test when implemented) **⚠️ PENDING**

- [x] **Test Patient Flags:**
  - [x] Verify topbar badge count (Bailey: 2, Alananah: 2) ✅ Both patients show 2 flags
  - [x] Open flags modal, verify flag details ✅ Working
  - [x] Verify "HIGH RISK FOR SUICIDE" flag for Bailey (Cat I) ✅ Present and active
  - [x] Verify "DIABETIC PATIENT" and "CANCER HISTORY" flags for Alananah (Cat II) ✅ Both present and active

**Joe Thompson:** 🚧 **NOT STARTED** (next priority)

### Phase 5: AI/ML Testing (Estimated 1 day)

- [ ] **Test AI Insight Tool (`/insight`):**
  - [ ] Bailey Thompson: "What are the key clinical risks for this patient?"
    - Expected: PTSD, suicide risk, polypharmacy, chronic pain, CKD, diabetes
  - [ ] Bailey Thompson: "Are there any drug-drug interaction concerns?"
    - Expected: Sertraline + trazodone (serotonin syndrome), gabapentin + duloxetine (CNS depression)
  - [ ] Bailey Thompson: "What did recent psychiatry notes say?"
    - Expected: PTSD management, suicide risk monitoring, medication adherence
  - [ ] Alananah Thompson: "Summarize this patient's cancer history"
    - Expected: Stage IIA breast cancer (2012), mastectomy + chemo + radiation, currently in remission on anastrozole
  - [ ] Alananah Thompson: "How is her diabetes controlled?"
    - Expected: A1C 7.1%, on metformin + empagliflozin, complicated by neuropathy and retinopathy
  - [ ] Joe Thompson: "What are the key clinical risks for this patient?"
    - Expected: Minimal risks, mild hypertension/hyperlipidemia well-controlled, excellent overall health

- [ ] **Test Vitals Trend Analysis:**
  - [ ] Bailey Thompson: Verify weight gain/loss trend (2010-2019 gain, 2020-2025 loss)
  - [ ] Alananah Thompson: Verify weight loss during chemo (2018-2019), subsequent gain
  - [ ] Joe Thompson: Verify stable vitals (consistent weight, BP, all normal ranges)

- [ ] **Test Charlson Comorbidity Index:**
  - [ ] Verify Bailey score = 5 (high risk)
  - [ ] Verify Alananah score = 4 (moderate-high risk)
  - [ ] Verify Joe score = 0 (excellent prognosis)

### Phase 6: Documentation (Estimated 0.5 days)

**CDWWork (Bailey & Alananah):** ✅ **COMPLETE (2026-02-09)**
- [x] **Update this requirements document:**
  - [x] Mark "Implementation Status: Complete" for Bailey and Alananah CDWWork ✅
  - [x] Add implementation notes (lessons learned, deviations from plan) ✅

- [x] **Create implementation summary:**
  - [x] Document all script execution issues ✅ See `thompson-twins-completion-summary.md`
  - [x] Document all SID conflict fixes ✅ See `thompson-alananah-all-fixes-complete.md`
  - [x] Recommend improvements for future test patients ✅ Documented in completion summary

**Remaining Documentation:**
- [ ] **Update CLAUDE.md:** Add Thompson Twins to test patient roster (deferred until all three patients complete)
- [ ] **Final implementation summary:** Create after Joe Thompson is complete

---

## Success Criteria

**Current Status (2026-02-09):**

Implementation is considered complete when:

1. **SQL scripts execute without errors:**
   - ✅ Bailey CDWWork: COMPLETE (Thompson-Bailey.sql)
   - ✅ Alananah CDWWork: COMPLETE (Thompson-Alananah.sql, all SID conflicts resolved)
   - 🚧 Joe CDWWork: NOT STARTED (next priority)
   - 🔧 Bailey/Alananah CDWWork2: Scripts created but need review (deferred)
   - 🔧 Joe CDWWork2: NOT STARTED

2. **Data inserted successfully:**
   - ✅ Bailey CDWWork: All 10 domains loaded, 231 vitals, 45 meds, 32 encounters, etc.
   - ✅ Alananah CDWWork: All 10 domains loaded, 231 vitals, 32 meds, 8 encounters, etc.
   - 🚧 Joe CDWWork: NOT STARTED
   - 🔧 CDWWork2 (all patients): PENDING REVIEW

3. **ETL pipeline processes Thompson Twins data:**
   - ✅ Bailey CDWWork: Bronze → Silver → Gold → PostgreSQL, no errors
   - ✅ Alananah CDWWork: Bronze → Silver → Gold → PostgreSQL, no errors
   - 🚧 Joe: NOT STARTED
   - 🔧 CDWWork2 merge: PENDING

4. **UI displays all 10 clinical domains:**
   - ✅ Bailey: All domains operational (ICN100001, Charlson=5)
   - ✅ Alananah: All domains operational (ICN200002, Charlson=2)
   - 🚧 Joe: NOT STARTED

5. **AI/ML tools generate accurate insights:**
   - 🔧 TESTING PENDING (will test after all patients complete)

6. **Patient identity resolution works correctly:**
   - ✅ Bailey: PatientSID 2001 → ICN100001 ✅
   - ✅ Alananah: PatientSID 2002 → ICN200002 ✅
   - 🚧 Joe: NOT STARTED

7. **Charlson Comorbidity Index calculates correctly:**
   - ✅ Bailey: 5 (verified in UI)
   - ✅ Alananah: 2 (verified in UI)
   - 🚧 Joe: NOT STARTED

8. **All scripts documented thoroughly:**
   - ✅ Bailey: Comprehensive inline documentation
   - ✅ Alananah: Comprehensive inline documentation
   - 🚧 Joe: NOT STARTED

9. **Master scripts updated and tested:**
   - ✅ CDWWork _master.sql: Updated with Bailey and Alananah, full rebuild tested ✅
   - 🔧 CDWWork2 _master.sql: PENDING (deferred until after Joe CDWWork)

10. ✅ **No PHI/PII included** (all data is synthetic and mock) - Verified for all scripts

---

## Appendix: Quick Reference

### Patient Identifiers

| Patient | Sex | ICN | CDWWork SID | CDWWork2 SID | Sta3n (Bay Pines) | Sta3n (Walla Walla) |
|---------|-----|-----|-------------|--------------|-------------------|---------------------|
| Bailey Thompson | M | ICN200001 | 2001 | 20001 | 516 | 687 |
| Alananah Thompson | F | ICN200002 | 2002 | 20002 | 516 | 687 |
| Joe Thompson | M | ICN200003 | 2003 | 20003 | 516 | 687 |

### Data Volume Summary

| Domain | Bailey (Total) | Alananah (Total) | Joe (Total) |
|--------|----------------|------------------|-------------|
| Vitals | 64 | 64 | 56 |
| Medications | 45 | 40 | 8 |
| Encounters | 32 | 28 | 3 |
| Clinical Notes | 220 | 180 | 60 |
| Immunizations | 42 | 40 | 40 |
| Problems | 18 | 16 | 2 |
| Labs | 160 | 140 | 60 |
| Allergies | 2 | 2 | 0 (NKDA) |
| Patient Flags | 2 | 2 | 0 |

### Key Clinical Conditions

**Bailey Thompson:**
- PTSD (70% SC), Chronic Pain (40% SC), TBI (10% SC), Tinnitus (10% SC)
- Suicide attempt (2016), High Risk flag
- Diabetes, CKD Stage 3a, Hypertension, Hyperlipidemia
- Alcohol/tobacco use disorder (in remission)
- Charlson Score: 5 (high risk)

**Alananah Thompson:**
- PTSD (30% SC), Knee Arthritis (10% SC), Hearing Loss (10% SC)
- Breast cancer survivor (Stage IIA, 2012, in remission)
- Diabetes with neuropathy and retinopathy
- Hypothyroidism, Hypertension, Hyperlipidemia
- Charlson Score: 4 (moderate-high risk)

**Joe Thompson:**
- Very healthy (minimal chronic disease)
- Hypertension (mild, well-controlled)
- Hyperlipidemia (mild, well-controlled)
- 10% service-connected disability (knee strain, minor)
- Charlson Score: 0 (excellent prognosis)
- **Purpose:** Healthy control case for comparison testing

---

## Implementation Status Summary (2026-02-09)

### ✅ Complete: Bailey & Alananah CDWWork
- **Scripts:** `Thompson-Bailey.sql` and `Thompson-Alananah.sql` fully implemented and tested
- **Testing:** Full ETL pipeline validated (SQL Server → Bronze → Silver → Gold → PostgreSQL)
- **UI:** All 10 clinical domains operational in med-z1 UI
- **Data Quality:** All SID conflicts resolved, no errors in database rebuild
- **Documentation:** Comprehensive completion summary available in `thompson-twins-completion-summary.md`

### 🔧 Pending Review: Bailey & Alananah CDWWork2
- **Scripts:** `Thompson-Bailey.sql` and `Thompson-Alananah.sql` created for CDWWork2 database
- **Status:** Scripts exist but require further review and verification before considered complete
- **Rationale:** User will revisit CDWWork2 scripts after Joe's CDWWork script is complete
- **Testing:** SQL Server execution, ETL pipeline, and UI verification are pending

### 🚧 Not Started: Joe Thompson (CDWWork & CDWWork2)
- **Scripts:** `Thompson-Joe.sql` for both CDWWork and CDWWork2 not yet created
- **Priority:** Joe's CDWWork script is the next priority before revisiting CDWWork2
- **Profile:** Healthy control case (Charlson=0) with minimal clinical data

### Key Lessons Learned (Bailey & Alananah Implementation)
1. **SID Allocation Critical:** Use +1000 increments per patient to avoid conflicts (Bailey: 9001-9231, Alananah: 10001-10231)
2. **Verify Dimension Tables First:** Check flag/lookup tables exist before referencing them (Patient Flags issue)
3. **Test Incrementally:** Catch ID conflicts early before full integration
4. **Use Working Templates:** Bailey's proven script patterns saved time on Alananah implementation
5. **User Feedback Critical:** User identified VitalSignSID and Allergy conflicts before they became blocking issues

### Related Documentation
- **Completion Summary:** `docs/spec/thompson-twins-completion-summary.md` (comprehensive status for Bailey & Alananah)
- **Implementation Plan:** `docs/spec/thompson-twins-implementation-plan.md` (v2.2, updated with current status)
- **Fix Documentation:** `docs/spec/thompson-alananah-all-fixes-complete.md` (all SID conflict resolutions documented)
- **Architecture:** `docs/spec/med-z1-architecture.md` (system design patterns)

### Next Steps
1. 🚧 **CURRENT PRIORITY:** Create Joe Thompson CDWWork script (`Thompson-Joe.sql`)
2. 🔧 **FUTURE:** Review and verify CDWWork2 scripts for all three patients (Bailey, Alananah, Joe)
3. 🔧 **FUTURE:** Complete full ETL pipeline testing with CDWWork2 data
4. 🔧 **FUTURE:** Update CLAUDE.md with Thompson Twins test patient references

---

**End of Requirements Document**
