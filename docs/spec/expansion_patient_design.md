# Patient Expansion Design Document
## CDWWork Database - 10 New Patients (PatientSIDs 1016-1025)

**Purpose:** Expand patient cohort from 15 to 25 patients with balanced age/complexity distribution

**Design Criteria:**
- Age groups: 3 younger (25-45), 4 middle-aged (46-64), 3 elderly (65+)
- Mental health emphasis (7/10 patients)
- Mixed data sources (RxOut, BCMA, both)
- 5 designed DDI scenarios, 5 natural DDIs
- Temporal complexity: 2-3 medication dates per patient (30-90 day span)
- Geographic: 4 facilities (Sta3n 508, 516, 552, 688-DC)

---

## YOUNGER PATIENTS (Ages 25-45)

### Patient 1016: Combat Veteran with PTSD
**Demographics:**
- PatientSID: 1016
- PatientICN: 1016V123456
- Age: 28
- DOB: 1996-03-15
- Gender: M
- Sta3n: 688 (Washington DC VAMC)

**Conditions:** PTSD, Major Depressive Disorder

**Medications (Natural DDI emergence):**
1. **Sertraline 100mg** (SSRI for PTSD/Depression)
2. **Prazosin 2mg** (Nightmares)
3. **Trazodone 50mg** (Sleep aid)

**Data Source:** RxOut + BCMA

**Medication Timeline:**
- Day 0 (2024-01-15): Sertraline started (RxOut)
- Day 30 (2024-02-14): Prazosin added for nightmares (RxOut), Sertraline (BCMA administration)
- Day 60 (2024-03-15): Trazodone added for insomnia (RxOut)

**Expected DDIs:**
- Sertraline + Trazodone: Moderate (Serotonin syndrome risk, CNS depression)
- Prazosin + Trazodone: Low (Additive hypotension)

**Clinical Rationale:** Common PTSD polypharmacy; DDIs emerge as treatments layered

---

### Patient 1017: Young Female with Anxiety and Chronic Pain
**Demographics:**
- PatientSID: 1017
- PatientICN: 1017V234567
- Age: 35
- DOB: 1989-07-22
- Gender: F
- Sta3n: 508 (Atlanta VAMC)

**Conditions:** Generalized Anxiety Disorder, Fibromyalgia, Chronic Pain

**Medications (DESIGNED DDI - SSRI + NSAID + Tramadol):**
1. **Escitalopram 10mg** (SSRI for anxiety)
2. **Ibuprofen 600mg** (NSAID for pain)
3. **Tramadol 50mg** (Pain management)
4. **Cyclobenzaprine 10mg** (Muscle relaxant)

**Data Source:** RxOut only

**Medication Timeline:**
- Day 0 (2024-02-01): Escitalopram, Cyclobenzaprine started (RxOut)
- Day 30 (2024-03-02): Ibuprofen added for pain flare (RxOut)
- Day 60 (2024-04-01): Tramadol added for inadequate pain control (RxOut)

**Expected DDIs:**
- Escitalopram + Tramadol: **Moderate** (Serotonin syndrome risk)
- Tramadol + Cyclobenzaprine: **Moderate** (CNS depression, respiratory depression)
- Escitalopram + Ibuprofen: Low (Increased bleeding risk)

**Clinical Rationale:** DESIGNED DDI scenario - common pain management adding opioid-like drug to SSRI

---

### Patient 1018: Young Male with Type 2 Diabetes
**Demographics:**
- PatientSID: 1018
- PatientICN: 1018V345678
- Age: 42
- DOB: 1982-11-08
- Gender: M
- Sta3n: 516 (Honolulu VAMC)

**Conditions:** Type 2 Diabetes Mellitus

**Medications (Natural DDI - minimal):**
1. **Metformin 1000mg** (First-line diabetes)
2. **Glipizide 5mg** (Sulfonylurea for glucose control)

**Data Source:** BCMA only

**Medication Timeline:**
- Day 0 (2024-01-20): Metformin started (BCMA)
- Day 45 (2024-03-05): Glipizide added for A1C control (BCMA)

**Expected DDIs:**
- Metformin + Glipizide: Low (Additive hypoglycemia - not typically flagged as DDI)

**Clinical Rationale:** Simple diabetes management, low complexity baseline patient

---

## MIDDLE-AGED PATIENTS (Ages 46-64)

### Patient 1019: Female with Depression and Hypertension
**Demographics:**
- PatientSID: 1019
- PatientICN: 1019V456789
- Age: 48
- DOB: 1976-05-14
- Gender: F
- Sta3n: 552 (Dayton VAMC)

**Conditions:** Major Depressive Disorder, Hypertension

**Medications (DESIGNED DDI - SSRI + NSAIDs + Antiplatelet):**
1. **Fluoxetine 40mg** (SSRI for depression)
2. **Lisinopril 10mg** (ACE inhibitor for HTN)
3. **Aspirin 81mg** (Cardioprotection)
4. **Ibuprofen 400mg** (Headaches, arthritis)
5. **Hydrochlorothiazide 25mg** (Diuretic)

**Data Source:** RxOut + BCMA

**Medication Timeline:**
- Day 0 (2024-01-10): Fluoxetine, Lisinopril, Aspirin started (RxOut)
- Day 30 (2024-02-09): HCTZ added for BP control (RxOut), Fluoxetine (BCMA)
- Day 60 (2024-03-10): Ibuprofen added PRN for headaches (RxOut)

**Expected DDIs:**
- Fluoxetine + Aspirin + Ibuprofen: **Moderate** (Increased bleeding risk - triple combo)
- Lisinopril + Ibuprofen: **Moderate** (Reduced ACE inhibitor efficacy, renal risk)
- Ibuprofen + HCTZ: Low (Reduced diuretic effect)

**Clinical Rationale:** DESIGNED DDI - SSRI + antiplatelet + NSAID is clinically significant bleeding risk

---

### Patient 1020: Male with COPD and Anxiety
**Demographics:**
- PatientSID: 1020
- PatientICN: 1020V567890
- Age: 53
- DOB: 1971-09-30
- Gender: M
- Sta3n: 688 (Washington DC VAMC)

**Conditions:** COPD, Generalized Anxiety Disorder

**Medications (Natural DDI):**
1. **Albuterol MDI** (Bronchodilator)
2. **Tiotropium (Spiriva)** (Long-acting bronchodilator)
3. **Fluticasone/Salmeterol (Advair)** (Inhaled corticosteroid/LABA)
4. **Lorazepam 1mg** (Anxiety - PRN)
5. **Prednisone 10mg** (Maintenance for COPD exacerbations)

**Data Source:** RxOut only

**Medication Timeline:**
- Day 0 (2024-02-05): Albuterol, Tiotropium, Advair (RxOut)
- Day 30 (2024-03-06): Lorazepam added for anxiety (RxOut)
- Day 60 (2024-04-05): Prednisone taper started (RxOut)

**Expected DDIs:**
- Lorazepam + Inhaled medications: Low (Benzodiazepine with COPD - caution but not severe DDI)
- Prednisone + Fluticasone: Low (Additive corticosteroid effects)

**Clinical Rationale:** COPD + anxiety comorbidity; benzodiazepine use in COPD is caution but realistic

---

### Patient 1021: Female with Diabetes and Heart Failure
**Demographics:**
- PatientSID: 1021
- PatientICN: 1021V678901
- Age: 58
- DOB: 1966-12-03
- Gender: F
- Sta3n: 508 (Atlanta VAMC)

**Conditions:** Type 2 Diabetes, CHF (HFrEF), Hypertension

**Medications (DESIGNED DDI - ACE inhibitor + Potassium-sparing + NSAID):**
1. **Metformin 1000mg** (Diabetes)
2. **Lisinopril 20mg** (ACE inhibitor for CHF/HTN)
3. **Spironolactone 25mg** (Potassium-sparing diuretic for CHF)
4. **Carvedilol 12.5mg** (Beta-blocker for CHF)
5. **Naproxen 500mg** (Arthritis pain)
6. **Insulin Glargine 20 units** (Long-acting insulin)

**Data Source:** RxOut + BCMA

**Medication Timeline:**
- Day 0 (2024-01-08): Metformin, Lisinopril, Carvedilol, Insulin (RxOut)
- Day 30 (2024-02-07): Spironolactone added for CHF (RxOut), Lisinopril (BCMA)
- Day 60 (2024-03-08): Naproxen added for knee pain (RxOut)

**Expected DDIs:**
- Lisinopril + Spironolactone: **Moderate** (Hyperkalemia risk)
- Lisinopril + Naproxen: **Moderate** (Reduced ACE inhibitor effect, renal impairment)
- Spironolactone + Naproxen: **Moderate** (Hyperkalemia, renal impairment)

**Clinical Rationale:** DESIGNED DDI - Classic triple interaction (ACE-I + K-sparing + NSAID) = hyperkalemia + renal risk

---

### Patient 1022: Male with Chronic Kidney Disease and Pain
**Demographics:**
- PatientSID: 1022
- PatientICN: 1022V789012
- Age: 61
- DOB: 1963-04-17
- Gender: M
- Sta3n: 516 (Honolulu VAMC)

**Conditions:** CKD Stage 3, Chronic Lower Back Pain, Hypertension

**Medications (DESIGNED DDI - CKD + NSAIDs + ACE inhibitor):**
1. **Amlodipine 10mg** (Calcium channel blocker for HTN)
2. **Gabapentin 300mg** (Neuropathic pain)
3. **Meloxicam 15mg** (NSAID for pain)
4. **Lisinopril 10mg** (ACE inhibitor for renal protection/HTN)
5. **Oxycodone 5mg** (Pain - PRN)

**Data Source:** BCMA only

**Medication Timeline:**
- Day 0 (2024-02-12): Amlodipine, Lisinopril, Gabapentin (BCMA)
- Day 30 (2024-03-13): Meloxicam added for back pain (BCMA)
- Day 60 (2024-04-12): Oxycodone added for breakthrough pain (BCMA)

**Expected DDIs:**
- Lisinopril + Meloxicam: **Moderate** (Acute renal failure risk in CKD patient)
- Gabapentin + Oxycodone: **Moderate** (CNS depression, respiratory depression)
- Meloxicam + Oxycodone: Low (Additive GI effects)

**Clinical Rationale:** DESIGNED DDI - NSAID use in CKD patient on ACE inhibitor is high-risk scenario

---

## ELDERLY PATIENTS (Ages 65+)

### Patient 1023: Elderly Female with Depression and Metabolic Syndrome
**Demographics:**
- PatientSID: 1023
- PatientICN: 1023V890123
- Age: 67
- DOB: 1957-08-25
- Gender: F
- Sta3n: 552 (Dayton VAMC)

**Conditions:** Major Depressive Disorder, Type 2 Diabetes, Hyperlipidemia, Hypertension

**Medications (DESIGNED DDI - SSRI + Antiplatelet + Anticoagulant):**
1. **Citalopram 20mg** (SSRI for depression)
2. **Metformin 850mg** (Diabetes)
3. **Atorvastatin 40mg** (Statin for hyperlipidemia)
4. **Aspirin 81mg** (Cardioprotection)
5. **Clopidogrel 75mg** (Antiplatelet - post-stent)
6. **Losartan 50mg** (ARB for HTN)
7. **Omeprazole 20mg** (PPI for GI protection)

**Data Source:** RxOut + BCMA

**Medication Timeline:**
- Day 0 (2024-01-05): Metformin, Atorvastatin, Aspirin, Losartan (RxOut)
- Day 30 (2024-02-04): Citalopram added for depression (RxOut), Metformin (BCMA)
- Day 60 (2024-03-05): Clopidogrel + Omeprazole added post-cardiac stent (RxOut)

**Expected DDIs:**
- Citalopram + Aspirin + Clopidogrel: **Moderate** (Triple bleeding risk)
- Clopidogrel + Omeprazole: **Moderate** (Reduced clopidogrel effectiveness)
- Aspirin + Clopidogrel: **Moderate** (Dual antiplatelet bleeding risk)

**Clinical Rationale:** DESIGNED DDI - Post-cardiac intervention patient with depression; complex bleeding risk management

---

### Patient 1024: Elderly Male with Heart Failure and AFib
**Demographics:**
- PatientSID: 1024
- PatientICN: 1024V901234
- Age: 74
- DOB: 1950-02-11
- Gender: M
- Sta3n: 688 (Washington DC VAMC)

**Conditions:** CHF (HFrEF), Atrial Fibrillation, CKD Stage 3, Hypertension

**Medications (Natural DDI):**
1. **Metoprolol 50mg** (Beta-blocker for CHF/AFib)
2. **Apixaban 5mg** (Anticoagulant for AFib)
3. **Furosemide 40mg** (Loop diuretic for CHF)
4. **Spironolactone 25mg** (Potassium-sparing for CHF)
5. **Digoxin 0.125mg** (Rate control for AFib)
6. **Lisinopril 10mg** (ACE inhibitor for CHF)
7. **Potassium Chloride 20mEq** (Supplement)
8. **Atorvastatin 20mg** (Statin)

**Data Source:** RxOut + BCMA

**Medication Timeline:**
- Day 0 (2024-01-12): Metoprolol, Apixaban, Furosemide, Lisinopril (RxOut)
- Day 30 (2024-02-11): Spironolactone, Digoxin added (RxOut), Metoprolol (BCMA)
- Day 60 (2024-03-12): K+ supplement, Atorvastatin added (RxOut)

**Expected DDIs:**
- Lisinopril + Spironolactone + K+ supplement: **Moderate** (Hyperkalemia risk)
- Digoxin + Furosemide: **Moderate** (Hypokalemia increases digoxin toxicity)
- Multiple drug-drug interactions in complex CHF/AFib management

**Clinical Rationale:** Natural DDI emergence - complex cardiac patient with multiple necessary medications

---

### Patient 1025: Elderly Female with Multi-Morbidity
**Demographics:**
- PatientSID: 1025
- PatientICN: 1025V012345
- Age: 79
- DOB: 1945-06-19
- Gender: F
- Sta3n: 516 (Honolulu VAMC)

**Conditions:** COPD, Type 2 Diabetes, Hypertension, Major Depressive Disorder, Osteoarthritis

**Medications (Natural DDI - Polypharmacy):**
1. **Tiotropium (Spiriva)** (Long-acting bronchodilator)
2. **Fluticasone/Salmeterol (Advair)** (Inhaled corticosteroid/LABA)
3. **Metformin 500mg** (Diabetes)
4. **Glipizide 10mg** (Sulfonylurea)
5. **Amlodipine 5mg** (Calcium channel blocker for HTN)
6. **Sertraline 50mg** (SSRI for depression)
7. **Acetaminophen 650mg** (Pain management)
8. **Omeprazole 20mg** (GERD/GI protection)
9. **Multivitamin** (Nutritional support)

**Data Source:** RxOut only

**Medication Timeline:**
- Day 0 (2024-01-18): Spiriva, Advair, Metformin, Amlodipine (RxOut)
- Day 45 (2024-03-03): Glipizide, Sertraline, Acetaminophen added (RxOut)
- Day 75 (2024-04-02): Omeprazole, Multivitamin added (RxOut)

**Expected DDIs:**
- Sertraline + multiple medications: Low-Moderate (Serotonin, bleeding with antiplatelet if added)
- Glipizide + Metformin: Low (Hypoglycemia)
- Generally lower severity DDIs due to careful prescribing in elderly

**Clinical Rationale:** Natural polypharmacy in elderly multi-morbid patient; high medication burden but managed carefully

---

## SUMMARY STATISTICS

**Total New Patients:** 10 (PatientSIDs 1016-1025)

**Age Distribution:**
- Younger (25-45): 3 patients (1016, 1017, 1018)
- Middle-aged (46-64): 4 patients (1019, 1020, 1021, 1022)
- Elderly (65+): 3 patients (1023, 1024, 1025)

**Geographic Distribution:**
- Sta3n 508 (Atlanta): 2 patients (1017, 1021)
- Sta3n 516 (Honolulu): 3 patients (1018, 1022, 1025)
- Sta3n 552 (Dayton): 2 patients (1019, 1023)
- Sta3n 688 (Washington DC): 3 patients (1016, 1020, 1024)

**Data Source Distribution:**
- RxOut + BCMA: 5 patients (1016, 1019, 1021, 1023, 1024)
- RxOut only: 3 patients (1017, 1020, 1025)
- BCMA only: 2 patients (1018, 1022)

**DDI Design:**
- Designed DDI scenarios: 5 patients (1017, 1019, 1021, 1022, 1023)
- Natural DDI emergence: 5 patients (1016, 1018, 1020, 1024, 1025)

**Mental Health Conditions:** 7 patients (1016, 1017, 1019, 1020, 1023, 1025, and 1022 with pain-related depression potential)

**Total Medications:** 62 new medication records across all patients

**Expected DDI Pairs:**
- Moderate severity: ~15-20 pairs
- Low severity: ~10-15 pairs
- Total: ~25-35 DDI pairs

**Medication Classes Represented:**
- SSRIs/Antidepressants: 6 patients
- Antihypertensives (ACE-I, ARB, CCB, BB): 7 patients
- NSAIDs: 5 patients
- Diabetes medications: 5 patients
- Respiratory medications: 3 patients
- Anticoagulants/Antiplatelets: 3 patients
- Pain medications: 4 patients
- GI medications: 3 patients

---

**Design Date:** 2024-11-29
**Purpose:** Phase 1 expansion (15 → 25 patients) before PhysioNet integration
**Next Phase:** PhysioNet MIMIC-IV integration for care coordination analysis
