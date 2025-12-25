#!/bin/bash
# Run all ETL pipelines for med-z1
# Command: ./scripts/run_all_etl.sh

set -e  # Exit on error

echo "Starting ETL pipelines..."

# Patient Demographics
echo ">>> Running Patient Demographics pipeline..."
python -m etl.bronze_patient
python -m etl.bronze_patient_address
python -m etl.bronze_patient_disability
python -m etl.bronze_patient_insurance
python -m etl.bronze_insurance_company
python -m etl.silver_patient
python -m etl.gold_patient
python -m etl.load_postgres_patient

# Vitals
echo ">>> Running Vitals pipeline..."
python -m etl.bronze_vitals
python -m etl.silver_vitals
python -m etl.gold_vitals
python -m etl.load_vitals

# Allergies
echo ">>> Running Allergies pipeline..."
python -m etl.bronze_allergen
python -m etl.bronze_reaction
python -m etl.bronze_allergy_severity
python -m etl.bronze_patient_allergy
python -m etl.bronze_patient_allergy_reaction
python -m etl.silver_patient_allergies
python -m etl.gold_patient_allergies
python -m etl.load_patient_allergies

# Medications
echo ">>> Running Medications pipeline..."
python -m etl.bronze_medications
python -m etl.silver_medications
python -m etl.gold_patient_medications
python -m etl.load_medications

# Patient Flags
echo ">>> Running Patient Flags pipeline..."
python -m etl.bronze_patient_flags
python -m etl.silver_patient_flags
python -m etl.gold_patient_flags
python -m etl.load_patient_flags

# Encounters
echo ">>> Running Encounters pipeline..."
python -m etl.bronze_inpatient
python -m etl.silver_inpatient
python -m etl.gold_inpatient
python -m etl.load_encounters

# Laboratory Results
echo ">>> Running Laboratory Results pipeline..."
python -m etl.bronze_labs
python -m etl.silver_labs
python -m etl.gold_labs
python -m etl.load_labs

echo "All ETL pipelines completed successfully!"