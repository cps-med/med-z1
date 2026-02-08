#!/bin/bash
# Run all ETL pipelines for med-z1
# Command: ./scripts/run_all_etl.sh

set -e  # Exit on error

echo "═══════════════════════════"
echo "  Starting ETL pipelines..."
echo "═══════════════════════════"
sleep 2

# Patient Demographics
echo "══════════════════════════════════════════════════"
echo ">>> Running Patient Demographics pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_patient
python -m etl.bronze_patient_address
python -m etl.bronze_patient_disability
python -m etl.bronze_patient_insurance
python -m etl.bronze_insurance_company
python -m etl.silver_patient
python -m etl.gold_patient
python -m etl.load_postgres_patient

# Patient Military History
echo "══════════════════════════════════════════════════"
echo ">>> Running Patient Military History pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.silver_patient_military_history
python -m etl.gold_patient_military_history
python -m etl.load_military_history

# Vitals
echo "══════════════════════════════════════════════════"
echo ">>> Running Vitals pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_vitals
python -m etl.bronze_cdwwork2_vitals
python -m etl.silver_vitals
python -m etl.gold_vitals
python -m etl.load_vitals

# Allergies
echo "══════════════════════════════════════════════════"
echo ">>> Running Allergies pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_allergen
python -m etl.bronze_reaction
python -m etl.bronze_allergy_severity
python -m etl.bronze_patient_allergy
python -m etl.bronze_patient_allergy_reaction
python -m etl.silver_patient_allergies
python -m etl.gold_patient_allergies
python -m etl.load_patient_allergies

# Medications
echo "══════════════════════════════════════════════════"
echo ">>> Running Medications pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_medications
python -m etl.silver_medications
python -m etl.gold_patient_medications
python -m etl.load_medications

# Patient Flags
echo "══════════════════════════════════════════════════"
echo ">>> Running Patient Flags pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_patient_flags
python -m etl.silver_patient_flags
python -m etl.gold_patient_flags
python -m etl.load_patient_flags

# Encounters
echo "══════════════════════════════════════════════════"
echo ">>> Running Encounters pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_inpatient
python -m etl.silver_inpatient
python -m etl.gold_inpatient
python -m etl.load_encounters

# Laboratory Results
echo "══════════════════════════════════════════════════"
echo ">>> Running Laboratory Results pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_labs
python -m etl.silver_labs
python -m etl.gold_labs
python -m etl.load_labs

# Clinical Notes
echo "══════════════════════════════════════════════════"
echo ">>> Running Clinical Notes pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_clinical_notes_vista
python -m etl.silver_clinical_notes
python -m etl.gold_clinical_notes
python -m etl.load_clinical_notes

# Immunizations
echo "══════════════════════════════════════════════════"
echo ">>> Running Immunizations pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_immunizations
python -m etl.bronze_cdwwork2_immunizations
python -m etl.silver_immunizations
python -m etl.gold_immunizations
python -m etl.load_immunizations

# Problems/Diagnoses
echo "══════════════════════════════════════════════════"
echo ">>> Running Problems/Diagnoses pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_problems
python -m etl.silver_problems
python -m etl.gold_problems
python -m etl.load_problems

# Drug-Drug Interaction Reference Data
echo "══════════════════════════════════════════════════"
echo ">>> Running DDI Reference Data pipeline..."
echo "══════════════════════════════════════════════════"
sleep 2
python -m etl.bronze_ddi
python -m etl.silver_ddi
python -m etl.gold_ddi

echo "══════════════════════════════════════════"
echo "All ETL pipelines completed successfully!"
echo "══════════════════════════════════════════"
sleep 1