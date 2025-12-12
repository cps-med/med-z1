#!/usr/bin/env python3
"""
Generate mock vitals data for CDWWork database
Generates 30-50 vital signs per patient over 12-18 months

Patient ID Strategy:
-------------------
This script uses PatientSID values 1-36 for simplicity, while SPatient.SPatient
uses PatientSID 1001-1036. This is intentional and acceptable because:

1. Different CDW tables can have different surrogate key ranges
2. Both resolve to the same ICN values using the pattern:
   ICN = "ICN" + str(100000 + patient_sid)
   - PatientSID 1  → ICN100001 (matches patient ICN)
   - PatientSID 2  → ICN100002 (matches patient ICN)
   - PatientSID 36 → ICN100036 (matches patient ICN)

3. The Gold ETL layer handles ICN resolution deterministically
4. This mimics real VA CDW where different tables have independent surrogate keys

For consistency in future mock data, consider using the same PatientSID range
(1001-1036), but this difference does not affect data quality or pipeline
correctness. The Gold layer properly resolves all vitals to the correct ICN.
"""

import random
from datetime import datetime, timedelta
from typing import List, Tuple

# Patient SIDs: Using 1-36 for simplicity (see module docstring for rationale)
# SPatient.SPatient uses 1001-1036, but both map to ICN100001-ICN100036
PATIENT_SIDS = list(range(1, 37))

# Vital types (from Dim.VitalType)
VITAL_TYPES = {
    1: {'name': 'BP', 'min': 90, 'max': 180},           # Blood Pressure
    2: {'name': 'T', 'min': 96.0, 'max': 103.0},        # Temperature
    3: {'name': 'P', 'min': 50, 'max': 130},             # Pulse
    4: {'name': 'R', 'min': 10, 'max': 28},              # Respiration
    5: {'name': 'HT', 'min': 60, 'max': 76},             # Height (inches)
    6: {'name': 'WT', 'min': 110, 'max': 300},           # Weight (lbs)
    7: {'name': 'PN', 'min': 0, 'max': 10},              # Pain
    8: {'name': 'POX', 'min': 88, 'max': 100},           # Pulse Oximetry
}

# Stations (facilities)
STATIONS = [518, 589, 528, 402]

# Staff SIDs (from SStaff.SStaff - using reasonable range)
STAFF_SIDS = list(range(1, 21))

def generate_bp_reading():
    """Generate realistic blood pressure reading"""
    # Bias towards normal range (90-140/60-90)
    if random.random() < 0.7:  # 70% normal
        systolic = random.randint(100, 135)
        diastolic = random.randint(60, 85)
    elif random.random() < 0.8:  # 20% slightly elevated
        systolic = random.randint(135, 150)
        diastolic = random.randint(85, 95)
    else:  # 10% high
        systolic = random.randint(150, 180)
        diastolic = random.randint(95, 115)

    return systolic, diastolic, f"{systolic}/{diastolic}"

def generate_temperature():
    """Generate realistic temperature reading (Fahrenheit)"""
    if random.random() < 0.85:  # 85% normal
        temp = round(random.uniform(97.5, 99.0), 1)
    elif random.random() < 0.9:  # 10% slightly elevated
        temp = round(random.uniform(99.1, 100.9), 1)
    else:  # 5% fever
        temp = round(random.uniform(101.0, 103.5), 1)

    # Convert to Celsius for metric value
    temp_c = round((temp - 32) * 5/9, 1)
    return temp, temp_c

def generate_pulse():
    """Generate realistic pulse reading"""
    if random.random() < 0.80:  # 80% normal
        pulse = random.randint(60, 90)
    elif random.random() < 0.9:  # 15% elevated
        pulse = random.randint(91, 110)
    else:  # 5% high
        pulse = random.randint(111, 130)
    return pulse

def generate_respiration():
    """Generate realistic respiration rate"""
    if random.random() < 0.90:  # 90% normal
        resp = random.randint(12, 20)
    else:  # 10% elevated
        resp = random.randint(21, 28)
    return resp

def generate_weight():
    """Generate realistic weight reading"""
    # Weight should be relatively stable for a patient
    base_weight = random.randint(120, 280)
    # Add small variation (+/- 5 lbs)
    variation = random.uniform(-5, 5)
    weight_lb = round(base_weight + variation, 1)
    weight_kg = round(weight_lb * 0.453592, 1)
    return weight_lb, weight_kg

def generate_height():
    """Generate height (fairly constant for adults)"""
    height_in = random.randint(60, 76)
    height_cm = round(height_in * 2.54, 1)
    return height_in, height_cm

def generate_pain():
    """Generate pain scale reading"""
    if random.random() < 0.60:  # 60% minimal/no pain
        pain = random.randint(0, 3)
    elif random.random() < 0.85:  # 25% moderate pain
        pain = random.randint(4, 7)
    else:  # 15% severe pain
        pain = random.randint(8, 10)
    return pain

def generate_pox():
    """Generate pulse oximetry reading"""
    if random.random() < 0.92:  # 92% normal
        pox = random.randint(95, 100)
    else:  # 8% low
        pox = random.randint(88, 94)
    return pox

def generate_vital_measurement(patient_sid: int, vital_type_sid: int, taken_datetime: datetime, sta3n: int) -> Tuple:
    """Generate a single vital measurement"""

    entered_datetime = taken_datetime + timedelta(minutes=random.randint(1, 30))
    staff_sid = random.choice(STAFF_SIDS)
    is_invalid = 'N'
    entered_in_error = 'N'

    # Generate type-specific values
    if vital_type_sid == 1:  # BP
        systolic, diastolic, result = generate_bp_reading()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                result, None, systolic, diastolic, None, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 2:  # Temperature
        temp_f, temp_c = generate_temperature()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{temp_f}", temp_f, None, None, temp_c, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 3:  # Pulse
        pulse = generate_pulse()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{pulse}", pulse, None, None, None, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 4:  # Respiration
        resp = generate_respiration()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{resp}", resp, None, None, None, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 5:  # Height
        height_in, height_cm = generate_height()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{height_in}", height_in, None, None, height_cm, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 6:  # Weight
        weight_lb, weight_kg = generate_weight()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{weight_lb}", weight_lb, None, None, weight_kg, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 7:  # Pain
        pain = generate_pain()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{pain}", pain, None, None, None, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

    elif vital_type_sid == 8:  # Pulse Oximetry
        pox = generate_pox()
        return (patient_sid, vital_type_sid, taken_datetime, entered_datetime,
                f"{pox}", pox, None, None, None, None, staff_sid,
                is_invalid, entered_in_error, sta3n)

def generate_vitals_for_patient(patient_sid: int) -> List[Tuple]:
    """Generate 30-50 vitals for a single patient over 12-18 months"""
    vitals = []
    num_measurements = random.randint(30, 50)

    # Start date: 18 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=random.randint(365, 548))  # 12-18 months

    # Generate timestamps evenly distributed
    time_increment = (end_date - start_date) / num_measurements

    # Patient's primary station
    primary_sta3n = random.choice(STATIONS)

    # Height is measured infrequently (1-2 times)
    height_measurements = random.randint(1, 2)

    for i in range(num_measurements):
        taken_datetime = start_date + (time_increment * i)

        # Standard vitals at most visits (BP, T, P, R)
        if random.random() < 0.95:  # 95% of visits have BP
            vitals.append(generate_vital_measurement(patient_sid, 1, taken_datetime, primary_sta3n))

        if random.random() < 0.90:  # 90% have temperature
            vitals.append(generate_vital_measurement(patient_sid, 2, taken_datetime, primary_sta3n))

        if random.random() < 0.95:  # 95% have pulse
            vitals.append(generate_vital_measurement(patient_sid, 3, taken_datetime, primary_sta3n))

        if random.random() < 0.85:  # 85% have respiration
            vitals.append(generate_vital_measurement(patient_sid, 4, taken_datetime, primary_sta3n))

        # Height - only occasionally
        if height_measurements > 0 and random.random() < 0.05:
            vitals.append(generate_vital_measurement(patient_sid, 5, taken_datetime, primary_sta3n))
            height_measurements -= 1

        # Weight - tracked regularly
        if random.random() < 0.70:  # 70% of visits
            vitals.append(generate_vital_measurement(patient_sid, 6, taken_datetime, primary_sta3n))

        # Pain - sometimes
        if random.random() < 0.40:  # 40% of visits
            vitals.append(generate_vital_measurement(patient_sid, 7, taken_datetime, primary_sta3n))

        # Pulse Ox - sometimes
        if random.random() < 0.50:  # 50% of visits
            vitals.append(generate_vital_measurement(patient_sid, 8, taken_datetime, primary_sta3n))

    return vitals

def format_sql_datetime(dt: datetime) -> str:
    """Format datetime for SQL Server"""
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

def generate_insert_statement(vital_sign_sid: int, vital_data: Tuple) -> str:
    """Generate SQL INSERT statement for a single vital"""
    (patient_sid, vital_type_sid, taken_dt, entered_dt, result_value,
     numeric_value, systolic, diastolic, metric_value, location_sid, staff_sid,
     is_invalid, entered_in_error, sta3n) = vital_data

    # Format values, handling NULL
    result_value_str = f"'{result_value}'" if result_value else "NULL"
    numeric_value_str = f"{numeric_value}" if numeric_value is not None else "NULL"
    systolic_str = f"{systolic}" if systolic else "NULL"
    diastolic_str = f"{diastolic}" if diastolic else "NULL"
    metric_value_str = f"{metric_value}" if metric_value is not None else "NULL"
    location_sid_str = f"{location_sid}" if location_sid else "NULL"
    staff_sid_str = f"{staff_sid}" if staff_sid else "NULL"

    sql = f"""    ({vital_sign_sid}, {patient_sid}, {vital_type_sid}, '{format_sql_datetime(taken_dt)}', '{format_sql_datetime(entered_dt)}',
        {result_value_str}, {numeric_value_str}, {systolic_str}, {diastolic_str}, {metric_value_str},
        {location_sid_str}, {staff_sid_str}, '{is_invalid}', '{entered_in_error}', {sta3n})"""

    return sql

def main():
    """Generate SQL INSERT script for all patients"""
    print("-- Insert seed data: Vital.VitalSign")
    print("-- Generated mock vitals data (30-50 measurements per patient)")
    print("-- Covers 12-18 months of historical data")
    print("")
    print("USE CDWWork;")
    print("GO")
    print("")
    print("SET QUOTED_IDENTIFIER ON;")
    print("GO")
    print("")
    print("SET IDENTITY_INSERT Vital.VitalSign ON;")
    print("GO")
    print("")

    all_vitals = []
    vital_sign_sid = 1

    for patient_sid in PATIENT_SIDS:
        patient_vitals = generate_vitals_for_patient(patient_sid)
        all_vitals.extend(patient_vitals)

    # Generate INSERT statements in batches of 500
    batch_size = 500
    total_vitals = len(all_vitals)

    for batch_start in range(0, total_vitals, batch_size):
        batch_end = min(batch_start + batch_size, total_vitals)
        batch = all_vitals[batch_start:batch_end]

        print(f"-- Batch {batch_start // batch_size + 1} (vitals {batch_start + 1} - {batch_end})")
        print("INSERT INTO Vital.VitalSign")
        print("    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,")
        print("     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,")
        print("     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)")
        print("VALUES")

        for i, vital in enumerate(batch):
            insert_sql = generate_insert_statement(vital_sign_sid, vital)
            vital_sign_sid += 1
            if i < len(batch) - 1:
                print(insert_sql + ",")
            else:
                print(insert_sql + ";")

        print("GO")
        print("")

    print("SET IDENTITY_INSERT Vital.VitalSign OFF;")
    print("GO")
    print("")
    print(f"PRINT 'Inserted {total_vitals} vital signs for {len(PATIENT_SIDS)} patients';")
    print("GO")
    print("")
    print("-- Verify")
    print("SELECT VitalTypeSID, COUNT(*) as VitalCount")
    print("FROM Vital.VitalSign")
    print("GROUP BY VitalTypeSID")
    print("ORDER BY VitalTypeSID;")
    print("GO")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
