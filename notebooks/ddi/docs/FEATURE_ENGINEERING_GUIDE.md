# Feature Engineering Guide
## Understanding Features in AI/ML for DDI Risk Analysis

---

## What Are Features?

In machine learning and AI, **features** are measurable properties or characteristics of the data that you use to train models and make predictions. Think of features as the "inputs" or "variables" that help a machine learning algorithm understand patterns and make decisions.

### Analogy: Features as Clues
Imagine you're a detective trying to determine if a patient is at high risk for drug-drug interactions (DDI):

- **Raw data** is like having access to all police reports, witness statements, and evidence
- **Features** are like extracting the key clues: "patient takes 8 medications", "has 3 high-severity DDI pairs", "medications from 2 different care systems"
- **Model** is like the detective's reasoning process that uses these clues to reach a conclusion

### Examples from Everyday ML

**Email Spam Detection:**
- Raw data: Email text
- Features: Number of words, presence of "FREE!!!", sender domain, number of links
- Model uses features to classify: spam or not spam

**Credit Card Fraud:**
- Raw data: Transaction records
- Features: Transaction amount, time of day, location, distance from last transaction
- Model uses features to predict: fraudulent or legitimate

**Medical Diagnosis:**
- Raw data: Patient medical records
- Features: Age, blood pressure, cholesterol level, family history
- Model uses features to predict: disease risk

---

## Why Feature Engineering Matters

Feature engineering is often considered the **most important step** in the ML workflow because:

### 1. **Models Learn from Features, Not Raw Data**
Machine learning algorithms can't directly understand raw text, dates, or complex relationships. You must transform raw data into numerical features the model can process.

### 2. **Better Features = Better Models**
A simple model with great features often outperforms a complex model with poor features. The saying goes:
> "Garbage in, garbage out" - but also "Gold in, gold out"

### 3. **Features Encode Domain Knowledge**
Good feature engineering captures what domain experts (like clinicians) know matters. For DDI analysis, we know that:
- Number of medications matters (polypharmacy)
- Severity of interactions matters
- Temporal overlap matters (are drugs taken concurrently?)

### 4. **Features Make Patterns Visible**
Raw medication records don't reveal patterns. But features like "DDI density" (proportion of drug pairs that interact) make risk patterns obvious.

---

## Our DDI Project: Two Feature Engineering Datasets

For our drug-drug interaction risk analysis project, we created **two complementary feature datasets**. Each serves a different purpose in the ML workflow.

### Dataset 1: Patient-Level Features
**File:** `v3_features/ddi/patients_features.parquet`
**Structure:** One row per patient
**Purpose:** Clustering, risk scoring, population health analysis

### Dataset 2: DDI Pair-Level Features
**File:** `v3_features/ddi/ddi_pairs_features.parquet`
**Structure:** One row per patient DDI pair
**Purpose:** Detailed interaction analysis, prediction modeling

---

## Patient-Level Features: Detailed Breakdown

These features aggregate each patient's medication profile into a single row, creating a "patient risk fingerprint."

### Why Patient-Level?
When clustering patients or assessing overall risk, you need **one comprehensive record per patient** that captures their entire medication profile and DDI risk.

### Feature Categories

#### 1. Demographic Features
**What they measure:** Patient demographic characteristics that influence medication response and DDI risk

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `Age` | Patient age in years | 72 | Age affects drug metabolism, clearance, and DDI sensitivity |
| `AgeGroup` | Age category | "65-79" | Enables age-stratified analysis and clustering |
| `IsElderly` | Elderly flag (65+) | 1 (yes) | Elderly patients have higher DDI risk (polypharmacy, altered pharmacokinetics) |
| `Gender` | Gender code | "M" | Gender affects drug metabolism and certain DDI risks |

**Clinical Insight:** Age is one of the strongest predictors of DDI risk. Elderly patients (65+) often have multiple chronic conditions (polypharmacy), altered drug metabolism (slower clearance), and increased sensitivity to adverse drug interactions. Gender can also influence drug metabolism through differences in body composition and enzyme activity.

#### 2. Medication Profile Features
**What they measure:** The patient's medication burden and complexity

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `medication_count` | Total medication records | 15 | More records = more opportunities for DDI |
| `unique_medications` | Distinct drugs | 8 | Polypharmacy indicator |
| `medication_diversity` | Shannon entropy | 2.1 | Higher = more varied drug types |
| `avg_medications_per_day` | Daily medication burden | 3.5 | Measures sustained medication load |

**Clinical Insight:** A patient taking 10 different medications has exponentially more DDI risk than one taking 2 medications.

#### 3. Temporal Features
**What they measure:** Duration and patterns of medication use over time

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `first_medication_date` | Earliest medication | 2024-01-15 | Start of medication history |
| `last_medication_date` | Most recent medication | 2024-11-27 | End of observation period |
| `medication_timespan_days` | Duration of med history | 316 days | Longer history = more chronic conditions |

**Clinical Insight:** Patients with longer medication histories often have chronic conditions requiring careful DDI monitoring.

#### 4. Source System Features
**What they measure:** Where medications are prescribed/administered

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `rxout_count` | Outpatient prescriptions | 8 | Community pharmacy fills |
| `bcma_count` | Inpatient administrations | 12 | Hospital-administered meds |
| `source_diversity` | Number of care settings | 2 | Higher = fragmented care risk |

**Clinical Insight:** Patients receiving care in multiple settings (VA + non-VA) have higher risk of DDI because providers may not see the complete medication list.

#### 5. DDI Risk Features
**What they measure:** The patient's actual DDI burden

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `ddi_pair_count` | Number of interacting drug pairs | 5 | Direct measure of DDI exposure |
| `ddi_severity_High` | Count of high-severity DDIs | 1 | Most critical interactions |
| `ddi_severity_Moderate` | Count of moderate DDIs | 3 | Clinically significant |
| `ddi_severity_Low` | Count of low-severity DDIs | 1 | Minor interactions |
| `total_ddi_risk_score` | Weighted sum (H=3, M=2, L=1) | 10 | Overall risk magnitude |
| `max_severity_level` | Worst interaction (0-3) | 3 | Highest risk present |
| `ddi_density` | DDI pairs / possible pairs | 0.18 | 18% of possible pairs interact |

**Clinical Insight:** A patient with `ddi_density=0.5` has DDI in half of all possible drug combinations - extremely high risk!

#### 6. Clinical Indicators (Binary Flags)
**What they measure:** Clinical decision thresholds

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `is_polypharmacy` | 5+ medications | 1 (yes) | Standard polypharmacy definition |
| `is_high_ddi_risk` | Moderate+ severity DDI | 1 (yes) | Needs medication review |

**Clinical Insight:** These binary flags make it easy to identify patients needing intervention.

### Example Patient Record

```
PatientSID: 1005
Age: 72
AgeGroup: "65-79"
IsElderly: 1
Gender: "M"
unique_medications: 3
medication_count: 8
ddi_pair_count: 1
ddi_severity_High: 0
ddi_severity_Moderate: 1
total_ddi_risk_score: 2
max_severity_level: 2
ddi_density: 0.33
is_polypharmacy: 0
is_high_ddi_risk: 1
```

**Interpretation:** This is a 72-year-old male patient (elderly) who takes 3 different medications, has 1 DDI pair of moderate severity, and is flagged for high DDI risk despite not meeting polypharmacy criteria (5+ meds). The `ddi_density` of 0.33 means one-third of possible drug pairs interact. Being elderly (IsElderly=1) increases his vulnerability to adverse effects from this DDI.

---

## DDI Pair-Level Features: Detailed Breakdown

These features describe each specific drug-drug interaction within each patient's medication list.

### Why Pair-Level?
When analyzing specific interactions or building prediction models (e.g., "will adding Drug X to this patient create a DDI?"), you need **detailed information about each drug pair**.

### Feature Categories

#### 1. Identification Features
**What they identify:** Which patient and which drug pair

| Feature | Description | Example Value |
|---------|-------------|---------------|
| `PatientSID` | Patient identifier | 1005 |
| `Drug1` | First drug (normalized) | WARFARIN |
| `Drug2` | Second drug (normalized) | ACETYLSALICYLIC ACID |

#### 2. Interaction Characteristics
**What they describe:** The nature and severity of the interaction

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `Severity` | High/Moderate/Low | Moderate | Risk level classification |
| `interaction_type` | Mechanism category | Bleeding Risk | Clinical mechanism |
| `Interaction` | Full description | "Warfarin may increase..." | Complete clinical details |

**Clinical Insight:** Knowing the `interaction_type` allows grouping similar interactions (e.g., all bleeding risks) for systematic review.

#### 3. Temporal Features
**What they measure:** Timing of concurrent medication use

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `temporal_overlap` | Are both drugs active? | 1 (yes) | DDI only matters if concurrent |
| `first_occurrence_date` | When DDI first appeared | 2024-02-01 | Start of risk period |
| `drug1_first_date` | When Drug1 started | 2024-01-15 | Drug1 timeline |
| `drug2_first_date` | When Drug2 started | 2024-02-01 | Drug2 timeline |
| `days_between_drug_starts` | Time lag between drugs | 17 days | How quickly DDI emerged |

**Clinical Insight:** A `temporal_overlap=0` means the drugs were never taken concurrently - the DDI risk may not apply. This is crucial for accurate risk assessment!

#### 4. Patient Context Features
**What they provide:** Background about the patient

| Feature | Description | Example Value | Why It Matters |
|---------|-------------|---------------|----------------|
| `patient_age` | Patient's age | 72 | Age affects DDI vulnerability |
| `patient_is_elderly` | Elderly flag | 1 | Elderly patients more sensitive to DDIs |
| `patient_medication_count` | Patient's total meds | 8 | Polypharmacy context |
| `patient_total_risk_score` | Patient's overall DDI risk | 10 | Cumulative risk context |
| `patient_is_polypharmacy` | Polypharmacy flag | 1 | Patient complexity |

**Clinical Insight:** A single moderate DDI in a patient with `patient_total_risk_score=15` is different than in a patient with `score=2`. Context matters! Age is particularly important - the same DDI can be benign in a young patient but dangerous in an elderly patient with reduced drug clearance.

### Example DDI Pair Record

```
PatientSID: 1005
Drug1: WARFARIN
Drug2: ACETYLSALICYLIC ACID
Severity: Moderate
interaction_type: Bleeding Risk
temporal_overlap: 1
first_occurrence_date: 2024-02-01
days_between_drug_starts: 17
patient_age: 72
patient_is_elderly: 1
patient_medication_count: 3
patient_total_risk_score: 2
patient_is_polypharmacy: 0
```

**Interpretation:** Patient 1005 has a moderate bleeding risk from WARFARIN + ACETYLSALICYLIC ACID. Both drugs are currently active (temporal_overlap=1), and this DDI first appeared 17 days after starting WARFARIN. The patient is a 72-year-old (elderly), which increases bleeding risk sensitivity. Despite not meeting polypharmacy criteria, this elderly patient has clinically significant DDI risk requiring careful monitoring.

---

## How These Features Will Be Used

### Immediate Use: Patient Clustering (05_clustering.ipynb)

**Goal:** Group patients by DDI risk profile
**Uses:** Patient-level features
**Algorithm:** K-means, hierarchical clustering, or DBSCAN

**Example Clusters:**
1. **Low-risk young**: Few medications, no DDIs, younger patients, stable over time
2. **Elderly high-risk polypharmacy**: 8+ medications, multiple DDIs, age 65+, fragmented care
3. **Middle-age moderate complexity**: Moderate medication load, some DDIs, 40-64 age group
4. **Acute care spike**: Short medication bursts (hospitalizations), BCMA-heavy, all age groups

**Why It Matters:** Clustering reveals patient subgroups needing different interventions. Age-stratified clusters help tailor interventions to life stage and physiological vulnerability.

### Near-Term Use: DDI Risk Analysis (06_analysis.ipynb)

**Goal:** Understand DDI patterns and high-risk scenarios
**Uses:** Both feature sets

**Analyses:**
- Which drug pairs are most common in high-risk patients?
- What's the distribution of DDI severity across the population?
- Which patients need immediate medication review?
- Are elderly patients at higher DDI risk than younger patients?
- Do DDI patterns differ by age group or gender?
- Are there geographic or temporal patterns?

### Future Use: Predictive Modeling

**Scenario 1: DDI Prediction**
- **Question:** "If we add Drug X to this patient, will it create a DDI?"
- **Input:** Patient-level features + proposed drug
- **Model:** Classification (Yes/No DDI)
- **Output:** Risk warning before prescribing

**Scenario 2: Severity Prediction**
- **Question:** "How severe will this DDI be?"
- **Input:** DDI pair-level features
- **Model:** Multi-class classification (High/Moderate/Low)
- **Output:** Triage priority

**Scenario 3: Care Coordination (After PhysioNet)**
- **Question:** "Are VA+non-VA patients at higher DDI risk?"
- **Input:** Patient-level features with source_diversity
- **Model:** Risk scoring
- **Output:** Identify fragmented care risks

---

## Feature Engineering Best Practices (Applied to Our Project)

### 1. **Domain Knowledge Integration**
We didn't just calculate statistics - we encoded clinical knowledge:
- Polypharmacy threshold (5+ medications)
- DDI severity weighting (High=3, Moderate=2, Low=1)
- Temporal overlap (concurrent use matters)
- Elderly threshold (65+ years) for age-related vulnerability
- Age groups aligned with clinical pharmacokinetic changes

### 2. **Multiple Granularities**
We created features at different levels:
- Patient-level: For clustering and overall risk
- Pair-level: For detailed interaction analysis

This gives flexibility for different ML tasks.

### 3. **Derived Features**
We created features that aren't in the raw data:
- `ddi_density` = calculated from counts
- `medication_diversity` = Shannon entropy
- `interaction_type` = extracted from text descriptions
- `Age` = calculated from DateOfBirth
- `AgeGroup` = binned age categories
- `IsElderly` = binary threshold flag

These capture insights that raw data doesn't reveal.

### 4. **Temporal Awareness**
We preserved time information:
- Date ranges
- Temporal overlap
- Days between events

This enables time-series analysis and tracking risk over time.

### 5. **Validation and Quality Checks**
We validated features:
- No missing critical values
- No infinite values
- Correlations checked (avoid redundancy)
- Distributions examined

---

## The Feature Engineering Process: Our Approach

### Step 1: Understand the ML Goal
**Our Goal:** Identify high-risk DDI patients and understand interaction patterns

### Step 2: Identify What Matters Clinically
**Clinical Knowledge:**
- Age increases risk (elderly have altered pharmacokinetics)
- Polypharmacy increases risk
- Severity matters (High > Moderate > Low)
- Concurrent use matters (temporal overlap)
- Fragmented care matters (multiple systems)
- Gender influences drug metabolism

### Step 3: Transform Raw Data → Features
**Raw Data:**
- Patient demographics (DateOfBirth, Gender) from SPatient.SPatient
- Medication records with dates, drug names, source systems
- DDI reference data with drug pairs and descriptions

**Features Created:**
- Demographics (age calculation, age groups, elderly flags, gender standardization)
- Aggregations (counts, sums, averages)
- Calculations (density, diversity, scores)
- Extractions (interaction types from text)
- Binary flags (polypharmacy, high risk, elderly)

### Step 4: Create Multiple Feature Sets
**Two datasets** for different use cases:
- Patient-level: Clustering, population health
- Pair-level: Detailed analysis, prediction

### Step 5: Validate
- Check data quality
- Examine distributions
- Look for correlations
- Verify clinical sensibility

---

## Key Takeaways

1. **Features are the bridge** between raw data and machine learning models

2. **Good feature engineering requires domain knowledge** - we encoded clinical expertise about age-related vulnerability, polypharmacy, DDI severity, and temporal patterns

3. **Different ML tasks need different feature granularities** - that's why we created both patient-level and pair-level features

4. **Feature engineering is iterative** - as we learn from clustering and analysis, we may create new features or refine existing ones

5. **Features should tell a story** - each feature in our datasets has a clinical rationale and helps answer specific questions about DDI risk

---

## Next Steps in Your ML Journey

Now that you have engineered features, you're ready for:

1. **Clustering (05_clustering.ipynb):** Use patient-level features to discover risk groups
2. **Analysis (06_analysis.ipynb):** Use both feature sets to understand DDI patterns
3. **Modeling (future):** Use features to build predictive models

Remember: The quality of your features determines the quality of your insights and predictions. By thoughtfully engineering features that capture clinical knowledge about DDI risk, you've set yourself up for success in the next steps!

---

*Generated for the med-ml DDI Risk Analysis Project*
*Date: 2025-11-27*
