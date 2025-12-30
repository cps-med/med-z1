#!/usr/bin/env python3
"""
Analyze RxOutpatSig coverage for target patients.
"""

import re

# Read RxOutpat file
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpat.sql', 'r') as f:
    rxout_content = f.read()

# Read RxOutpatSig file
with open('/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/RxOut.RxOutpatSig.sql', 'r') as f:
    sig_content = f.read()

# Extract RxOutpat records for target patients
target_patients = [1001, 1002, 1009, 1010]
rxout_pattern = r'^\((\d+),.*?(\d+),.*?\'([^\']+)\'.*?\'([^\']+)\'.*$'

prescriptions = {}
for patient_sid in target_patients:
    prescriptions[patient_sid] = []

for line in rxout_content.split('\n'):
    if line.strip().startswith('(50'):
        match = re.search(r'^\((\d+),[^,]+,[^,]+,\s*(\d+),[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,\s*\'([^\']+)\',\s*\'([^\']+)\'', line)
        if match:
            rx_sid = int(match.group(1))
            patient_sid = int(match.group(2))
            drug_wo_dose = match.group(3)
            drug_w_dose = match.group(4)

            if patient_sid in target_patients:
                prescriptions[patient_sid].append({
                    'RxOutpatSID': rx_sid,
                    'DrugNameWithoutDose': drug_wo_dose,
                    'DrugNameWithDose': drug_w_dose
                })

# Extract existing sig records
sig_pattern = r'^\((\d+),[^,]+,\s*(\d+),'
existing_sigs = set()

for line in sig_content.split('\n'):
    if line.strip().startswith('(70'):
        match = re.search(r'^\((\d+),[^,]+,\s*(\d+),', line)
        if match:
            rx_outpat_sid = int(match.group(2))
            existing_sigs.add(rx_outpat_sid)

# Analyze coverage
print("=" * 80)
print("RxOutpatSig Coverage Analysis for Target Patients")
print("=" * 80)

total_rx = 0
total_with_sig = 0
total_missing_sig = 0

for patient_sid in target_patients:
    icn = f"ICN{100000 + patient_sid}"
    rx_list = prescriptions[patient_sid]

    with_sig = [rx for rx in rx_list if rx['RxOutpatSID'] in existing_sigs]
    missing_sig = [rx for rx in rx_list if rx['RxOutpatSID'] not in existing_sigs]

    coverage_pct = (len(with_sig) / len(rx_list) * 100) if rx_list else 0

    print(f"\nPatient {patient_sid} ({icn}):")
    print(f"  Total Prescriptions: {len(rx_list)}")
    print(f"  With Sig Data: {len(with_sig)} ({coverage_pct:.1f}%)")
    print(f"  Missing Sig Data: {len(missing_sig)}")

    if missing_sig:
        print(f"  \nMissing Sig for:")
        for rx in missing_sig[:10]:  # Show first 10
            print(f"    - RxSID {rx['RxOutpatSID']}: {rx['DrugNameWithDose']}")
        if len(missing_sig) > 10:
            print(f"    ... and {len(missing_sig) - 10} more")

    total_rx += len(rx_list)
    total_with_sig += len(with_sig)
    total_missing_sig += len(missing_sig)

print("\n" + "=" * 80)
print(f"TOTAL SUMMARY:")
print(f"  Total Prescriptions: {total_rx}")
print(f"  With Sig Data: {total_with_sig} ({total_with_sig/total_rx*100:.1f}%)")
print(f"  Missing Sig Data: {total_missing_sig}")
print("=" * 80)
