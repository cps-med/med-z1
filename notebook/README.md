# med-ml

AI and Machine learning layer for Med-Insight

## Overview

**med-ml** is the artificial intelligence and machine learning engine of the Med-Insight application. It transforms cleaned and structured clinical data into predictive models, risk assessments, and data-driven insights using a traditional data science workflow with JupyterLab notebooks.

### Technology Stack

- **Python 3.11** - Core language
- **JupyterLab** - Interactive notebook environment
- **Pandas & NumPy** - Data manipulation
- **PyArrow** - Parquet file handling
- **scikit-learn** - Machine learning algorithms
- **SQL Server 2019** - Source database for patient medications and demographics (via pyodbc)
- **MinIO** - S3-compatible object storage for DDI reference data and processed datasets (via boto3 + s3fs)

## Project Structure

```
med-ml/
├── src/                                  # All code (notebooks + Python modules)
│   ├── config.py                         # Centralized configuration
│   ├── ddi_transforms.py                 # DDI-specific transformations
│   ├── 01a_dataprep_ddi.ipynb            # ✅ Data prep: DDI reference data
│   ├── 01b_dataprep_medications.ipynb    # ✅ Data prep: Patient medications
│   ├── 01c_dataprep_demographics.ipynb   # ✅ Data prep: Patient demographics
│   ├── 02_explore.ipynb                  # ✅ Exploratory data analysis
│   ├── 03_clean.ipynb                    # ✅ Data cleaning and validation
│   ├── 04_features.ipynb                 # ✅ Feature engineering
│   ├── 05_clustering.ipynb               # 🔜 Patient risk clustering (pending)
│   └── 06_analysis.ipynb                 # 🔜 Results analysis (pending)
├── docs/                                 # Methodology documentation
│   ├── FEATURE_ENGINEERING_GUIDE.md      # Feature engineering approach
│   ├── DEMOGRAPHICS_IMPLEMENTATION.md    # Demographics data implementation
│   ├── CLUSTERING_AND_ANALYSIS_GUIDE.md  # Clustering and analysis methodology
│   ├── PHYSIONET_INTEGRATION_GUIDE.md    # PhysioNet MIMIC-IV integration plan
│   └── PIPELINE_EXECUTION_GUIDE.md       # Step-by-step execution guide
└── README.md                             # This file
```

## Medallion Architecture

Data processing follows a versioned medallion architecture stored in MinIO:

| Tier | Prefix | Description | Location |
|------|--------|-------------|----------|
| **Raw** | `v1_raw` | Unmodified source data (Parquet) | `med-data/v1_raw/ddi/`, `med-data/v1_raw/medications/`, `med-data/v1_raw/demographics/` |
| **Clean** | `v2_clean` | Cleaned and validated data | `med-data/v2_clean/ddi/` |
| **Features** | `v3_features` | Feature-engineered datasets | `med-data/v3_features/ddi/` |
| **Models** | `v4_models` | Model outputs and predictions | `med-data/v4_models/ddi/` |

**Source data** originates from:
- **DDI reference data**: MinIO `med-sandbox/kaggle-data/ddi/` (CSV/Parquet)
- **Patient medications**: SQL Server CDWWork database (RxOut, BCMA schemas)
- **Patient demographics**: SQL Server CDWWork database (SPatient schema)

## Setup

### Prerequisites

Ensure you've completed the shared infrastructure setup from **med-data**:
- ✅ Docker Desktop running
- ✅ SQL Server 2019 container (`sqlserver2019`) running
- ✅ CDWWork database created and populated with sample data
- ✅ MinIO container (`med-insight-minio`) running
- ✅ Python 3.11 installed
- ✅ Root `.env` file configured

### Install ML Dependencies

```bash
cd ~/swdev/med/med-insight
source .venv/bin/activate

# Install Jupyter and ML packages
pip install jupyterlab ipykernel notebook matplotlib seaborn scikit-learn

# Update requirements
pip freeze > requirements.txt
```

### Prepare Source Data

**1. SQL Server CDWWork Database** (from med-data subsystem):
   - Ensure CDWWork database is created and populated
   - Verify patient data in SPatient.SPatient table (15 patients)
   - Verify medications in RxOut.RxOutpat and BCMA.BCMAMedicationLog tables
   - See **med-data** README for database setup instructions

**2. MinIO DDI Reference Data**:
   - Access MinIO Console: http://localhost:9001
   - Navigate to bucket: `med-sandbox`
   - Create folder path: `kaggle-data/ddi/`
   - Upload: `db_drug_interactions.csv`

**3. Create MinIO destination bucket structure**:
   - Bucket: `med-data` (create if doesn't exist)
   - Create folders: `v1_raw/ddi/`, `v1_raw/medications/`, `v1_raw/demographics/`
   - Create folders: `v2_clean/ddi/`, `v3_features/ddi/`, `v4_models/ddi/`

## Running Notebooks

### Using VS Code (Recommended)

1. Open project in VS Code
2. Navigate to: `med-ml/src/`
3. Open notebook: `01_dataprep.ipynb`
4. Select kernel: `.venv` (Python 3.11)
5. Run cells interactively

### Using JupyterLab

```bash
cd ~/swdev/med/med-insight/med-ml/src
source ../../.venv/bin/activate
jupyter lab
```

Access at: http://localhost:8888

## Workflow

### Phase 1: Data Preparation (✅ Complete)

#### 1a. DDI Reference Data (`01a_dataprep_ddi.ipynb`)
- Read DDI CSV from `med-sandbox/kaggle-data/ddi/`
- Write unmodified Parquet to `med-data/v1_raw/ddi/`
- 267,264 drug-drug interaction records

#### 1b. Patient Medications (`01b_dataprep_medications.ipynb`)
- Read medications from CDWWork SQL Server database (RxOut, BCMA schemas)
- Normalize drug names and create patient medication profiles
- Write to `med-data/v1_raw/medications/`
- Expanded cohort: 15 patients with realistic poly-pharmacy patterns
- Includes 5 elderly patients (ages 68-82) with DDI scenarios

#### 1c. Patient Demographics (`01c_dataprep_demographics.ipynb`)
- Read demographics from CDWWork SQL Server database (SPatient schema)
- Process age, gender, and comorbidities
- Write to `med-data/v1_raw/demographics/`
- Expanded cohort: 15 patients across 3 geographic locations (Sta3n 508, 516, 552)

### Phase 2: Exploration (✅ Complete)

#### 2. Exploratory Data Analysis (`02_explore.ipynb`)
- Load from v1_raw (DDI, medications, demographics)
- Examine schemas, distributions, missing values
- Identify data quality issues and relationship patterns
- 267K DDI pairs, 15 patients, 6-10 medications per patient
- Enhanced with elderly cohort featuring 18 clinically significant DDI scenarios

### Phase 3: Cleaning (✅ Complete)

#### 3. Data Cleaning (`03_clean.ipynb`)
- Apply standardization and validation rules
- Handle missing values and duplicates
- Normalize categorical variables
- Write to `med-data/v2_clean/`

### Phase 4: Feature Engineering (✅ Complete)

#### 4. Feature Engineering (`04_features.ipynb`)
- **Patient-level features** (19 features):
  - Demographics: age, gender, age groups
  - Medication burden: total medications, unique classes
  - DDI risk metrics: total interactions, severity distribution
  - Polypharmacy indicators
- **DDI pair-level features**:
  - Interaction characteristics with patient context
  - Severity, clinical significance, mechanism
- Write to `med-data/v3_features/`

### Phase 5: Clustering (🔜 Pending)

#### 5. Patient Risk Clustering (`05_clustering.ipynb`)
- Discover natural patient groupings based on risk profiles
- K-means, hierarchical, and DBSCAN clustering
- Identify high-risk, moderate-risk, and low-risk cohorts
- Write cluster assignments to `med-data/v3_features/`

### Phase 6: Analysis (🔜 Pending)

#### 6. Deep Analysis (`06_analysis.ipynb`)
- Analyze cluster characteristics and patterns
- Generate clinical insights and recommendations
- Prepare for predictive modeling
- Write reports to `med-data/v4_models/`

## Configuration

All configuration is centralized in `src/config.py`:

```python
# MinIO settings (loaded from root .env)
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "admin"
MINIO_SECRET_KEY = "<from .env>"

# Buckets
SOURCE_BUCKET = "med-sandbox"
DEST_BUCKET = "med-data"

# Data paths
SOURCE_DDI_PATH = "kaggle-data/ddi/"
V1_RAW_PREFIX = "v1_raw/ddi/"
V2_CLEAN_PREFIX = "v2_clean/ddi/"
V3_FEATURES_PREFIX = "v3_features/ddi/"
V4_MODELS_PREFIX = "v4_models/ddi/"
```

## Use Case: Drug-Drug Interaction (DDI) Risk Analysis

The initial use case identifies DDI risks from patient prescription data:

1. **Input Datasets**:
   - DDI reference data (267K drug-drug interactions from Kaggle)
   - Patient medication profiles (15 patients from CDWWork database)
   - Patient demographics and comorbidities (15 patients from CDWWork database)
   - Geographic data via Sta3n facility identifiers (3 VA locations)
2. **Goal**: Risk identification, patient clustering, and risk scoring for clinical decision support
3. **Current Status**: Feature engineering complete; ready for clustering and modeling
4. **Key Features**:
   - Elderly patient cohort (ages 68-82) with multiple comorbidities
   - 18 clinically significant DDI scenarios (Warfarin, NSAIDs, ACE inhibitors, statins, etc.)
   - Geographic distribution for location-based analysis
5. **Output**:
   - Patient risk profiles and cluster assignments
   - DDI risk scores with severity classification
   - Clinical recommendations for high-risk patients

## Development Notes

- Notebooks use standard Python logging (info level) to stdout
- Follow test-then-batch pattern: test with small samples before full processing
- Track metrics: row counts, processing time, data quality
- All imports use: `from config import *` for consistency
- Comprehensive guides available:
  - `FEATURE_ENGINEERING_GUIDE.md` - Feature engineering methodology
  - `DEMOGRAPHICS_IMPLEMENTATION.md` - Demographics integration approach
  - `CLUSTERING_AND_ANALYSIS_GUIDE.md` - Clustering and analysis strategy

## Current Status and Next Steps

**Completed Work (✅)**:
- ✅ All data preparation notebooks (DDI, medications, demographics)
- ✅ Exploratory data analysis across all datasets
- ✅ Data cleaning and validation
- ✅ Feature engineering (19 patient-level features + DDI pair features)
- ✅ Expanded CDWWork database with elderly patient cohort (5 patients, 18 DDI scenarios)

**In Progress (🔄)**:
- 🔄 Patient risk clustering implementation
- 🔄 Pattern analysis and insight generation

**Upcoming (🔜)**:
- 🔜 Predictive modeling (risk scores, classification)
- 🔜 Model evaluation and validation
- 🔜 PhysioNet MIMIC-IV integration for community care data (Phase 2)
- 🔜 Integration with med-view dashboard

## Additional Resources

- **MinIO Console**: http://localhost:9001 (login with credentials from .env)
- **Root .env**: `/Users/chuck/swdev/med/med-insight/.env` (shared configuration)

## Additional Documentation

Comprehensive guides are available for understanding the methodology and implementation approach:

- **[FEATURE_ENGINEERING_GUIDE.md](FEATURE_ENGINEERING_GUIDE.md)** - Detailed feature engineering methodology for DDI risk analysis
- **[DEMOGRAPHICS_IMPLEMENTATION.md](DEMOGRAPHICS_IMPLEMENTATION.md)** - Patient demographics data integration and processing details
- **[CLUSTERING_AND_ANALYSIS_GUIDE.md](CLUSTERING_AND_ANALYSIS_GUIDE.md)** - Strategy guide for patient risk clustering and pattern analysis
- **[PHYSIONET_INTEGRATION_GUIDE.md](PHYSIONET_INTEGRATION_GUIDE.md)** - PhysioNet MIMIC-IV community care data integration plan (Phase 2)
