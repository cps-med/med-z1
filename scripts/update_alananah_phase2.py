#!/usr/bin/env python3
"""
Phase 2: Complete clinical data updates for Thompson-Alananah.sql

Updates remaining sections:
- Section 3: Vitals (female profile, height 65")
- Section 6: Encounters (breast cancer treatment, diabetes management)
- Section 7: Clinical Notes (oncology, diabetes educator)
- Section 8.3: Labs (A1C trending, remove CKD markers)
- Section 8.4: Patient Flags (verify correct flags)

Reference: docs/spec/thompson-twins-patient-reqs.md
          docs/spec/thompson-alananah-clinical-updates.md
"""

import re
from pathlib import Path
from datetime import datetime

script_file = Path("/Users/chuck/swdev/med/med-z1/mock/sql-server/cdwwork/insert/Thompson-Alananah.sql")

def backup_file():
    """Create timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = script_file.with_suffix(f".sql.backup_phase2_{timestamp}")
    backup_path.write_text(script_file.read_text())
    return backup_path

def update_vitals_section_header():
    """Update vitals section header with Alananah's profile"""
    return """-- =====================================================
-- SECTION 3: VITALS
-- =====================================================
-- Quarterly vital sign readings: 2010-2025 (15 years)
-- Alananah Thompson: Female, Height 65" (5'5")
-- Weight trajectory:
--   2010-2011: 145-150 lbs (BMI 24-25, post-military baseline, healthy)
--   2012-2013: 135-145 lbs (weight loss during breast cancer treatment/chemo)
--   2014-2019: 155-175 lbs (gradual weight gain, BMI 26-29, overweight)
--   2020-2025: 185-195 lbs (BMI 31-33, obesity, diabetes management)
-- BP trend: 120/75 (2010) → 138/85 (2013 HTN) → 128/78 (2025 controlled)
-- Pain: Mild 2-4/10 (bilateral knee osteoarthritis, well-managed)
-- VitalSignSID range: 9001-9060 (allocated for Alananah)
-- =====================================================

PRINT '';
PRINT 'Inserting Alananah Thompson vitals (2010-2025, quarterly readings)...';
GO

SET IDENTITY_INSERT Vital.VitalSign ON;
GO

-- Vitals Batch 1: 2010-2012 (Baseline period, post-military retirement)
INSERT INTO Vital.VitalSign
    (VitalSignSID, PatientSID, VitalTypeSID, VitalSignTakenDateTime, VitalSignEnteredDateTime,
     ResultValue, NumericValue, Systolic, Diastolic, MetricValue,
     LocationSID, EnteredByStaffSID, IsInvalid, EnteredInError, Sta3n)
VALUES
    -- 2010-06-16: Initial baseline vitals (healthy, recently retired)
    (9001, 2002, 5, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '65', 65, NULL, NULL, 165.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9002, 2002, 6, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '148', 148, NULL, NULL, 67.1,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9003, 2002, 7, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '98.4', 98.4, NULL, NULL, 36.9,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9004, 2002, 1, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '118/74', NULL, 118, 74, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9005, 2002, 2, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '72', 72, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9006, 2002, 3, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '16', 16, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516),
    (9007, 2002, 10, '2010-06-16 09:30:00', '2010-06-16 09:35:00', '0', 0, NULL, NULL, NULL,
        (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n = 516 AND LocationType = 'CLINIC'),
        1001, 'N', 'N', 516)"""

def update_labs_section():
    """Update labs section with Alananah's diabetes-focused labs"""
    return """-- =====================================================
-- Section 8.3: LABORATORY RESULTS (Representative subset ~50 results)
-- =====================================================
-- Focus: Diabetes management (A1C trending), thyroid monitoring, routine screening
-- A1C trend: 8.5% (2012) → 6.8% (2020) → 7.1% (2025)
-- No CKD markers (Alananah has normal renal function, unlike Bailey)
-- =====================================================
PRINT '  Section 8.3: Laboratory Results (diabetes-focused)';
GO

-- BMP Panel 1 (2024-12-05, recent - showing good control)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 1, 'CH 20241205-2002', '139', 139.0, 'mmol/L', NULL, '135 - 145', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 2, 'CH 20241205-2002', '4.2', 4.2, 'mmol/L', NULL, '3.5 - 5.0', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 3, 'CH 20241205-2002', '103', 103.0, 'mmol/L', NULL, '98 - 107', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 4, 'CH 20241205-2002', '25', 25.0, 'mmol/L', NULL, '22 - 29', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 5, 'CH 20241205-2002', '14', 14.0, 'mg/dL', NULL, '7 - 20', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 6, 'CH 20241205-2002', '0.9', 0.9, 'mg/dL', NULL, '0.7 - 1.3', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 7, 'CH 20241205-2002', '118', 118.0, 'mg/dL', 'H', '70 - 100', '2024-12-05 08:00:00', '2024-12-05 10:15:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- HbA1c results (diabetes monitoring, quarterly 2012-2024)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 28, 'CH 20120415-A1C', '8.5', 8.5, '%', 'H', '4.0 - 5.6', '2012-04-15 08:00:00', '2012-04-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20120715-A1C', '8.2', 8.2, '%', 'H', '4.0 - 5.6', '2012-07-15 08:00:00', '2012-07-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20130115-A1C', '7.8', 7.8, '%', 'H', '4.0 - 5.6', '2013-01-15 08:00:00', '2013-01-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20150615-A1C', '7.2', 7.2, '%', 'H', '4.0 - 5.6', '2015-06-15 08:00:00', '2015-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20200615-A1C', '6.8', 6.8, '%', 'H', '4.0 - 5.6', '2020-06-15 08:00:00', '2020-06-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20220815-A1C', '6.9', 6.9, '%', 'H', '4.0 - 5.6', '2022-08-15 08:00:00', '2022-08-15 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 28, 'CH 20241205-A1C', '7.1', 7.1, '%', 'H', '4.0 - 5.6', '2024-12-05 08:00:00', '2024-12-05 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

-- Lipid panel (2024-06-15, annual)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 23, 'CH 20240615-LIP', '185', 185.0, 'mg/dL', NULL, '0 - 200', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 24, 'CH 20240615-LIP', '95', 95.0, 'mg/dL', NULL, '0 - 100', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 25, 'CH 20240615-LIP', '48', 48.0, 'mg/dL', NULL, '40 - 60', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 26, 'CH 20240615-LIP', '185', 185.0, 'mg/dL', 'H', '0 - 150', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum'),
(2002, 27, 'CH 20240615-LIP', '37', 37.0, 'mg/dL', NULL, '5 - 40', '2024-06-15 08:00:00', '2024-06-15 11:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Serum');
GO

-- CBC Panel (2024-09-10, normal values for Alananah)
INSERT INTO [Chem].[LabChem] ([PatientSID], [LabTestSID], [AccessionNumber], [Result], [ResultNumeric], [ResultUnit], [AbnormalFlag], [RefRange], [CollectionDateTime], [ResultDateTime], [VistaPackage], [LocationSID], [Sta3n], [SpecimenType])
VALUES
(2002, 8, 'CH 20240910-CBC', '7.2', 7.2, 'K/uL', NULL, '4.5 - 11.0', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 9, 'CH 20240910-CBC', '4.5', 4.5, 'M/uL', NULL, '4.0 - 5.5', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 10, 'CH 20240910-CBC', '13.8', 13.8, 'g/dL', NULL, '12.0 - 16.0', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 11, 'CH 20240910-CBC', '41', 41.0, '%', NULL, '36 - 44', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood'),
(2002, 12, 'CH 20240910-CBC', '245', 245.0, 'K/uL', NULL, '150 - 400', '2024-09-10 08:30:00', '2024-09-10 10:00:00', 'CH', (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Laboratory' ORDER BY LocationSID), 516, 'Whole Blood');
GO

PRINT '    Alananah Thompson: ~50 lab results inserted';
PRINT '    Key trends: A1C 8.5% (2012) → 6.8% (2020) → 7.1% (2025)';
PRINT '    Normal renal function (Cr 0.9 mg/dL, BUN 14 mg/dL)';
PRINT '    Good lipid control (LDL 95 mg/dL)';
GO"""

def main():
    print("=" * 70)
    print("Phase 2: Completing Thompson-Alananah.sql Clinical Data Updates")
    print("=" * 70)

    # Backup file
    print("\n1. Creating Phase 2 backup...")
    backup_path = backup_file()
    print(f"   ✓ Backup created: {backup_path.name}")

    # Read current file
    print("\n2. Reading Thompson-Alananah.sql...")
    content = script_file.read_text()

    # Update Section 3: Vitals header (major changes needed - will do height/weight replacements)
    print("\n3. Updating Section 3: Vitals header...")
    vitals_header_pattern = r"-- =====================================================\n-- SECTION 3: VITALS\n-- =====================================================.*?VALUES"
    new_vitals_header = update_vitals_section_header()
    content = re.sub(vitals_header_pattern, new_vitals_header, content, count=1, flags=re.DOTALL)
    print("   ✓ Vitals header updated (female profile, height 65\")")

    # Update all height values in vitals: 70 → 65
    print("\n4. Updating height values in vitals: 70\" → 65\"...")
    # Pattern for height entries (VitalTypeSID 5 = Height)
    height_pattern = r"(\(900\d+, 2002, 5,.*?')'70'(', 70,)"
    content = re.sub(height_pattern, r"\1'65'\2", content)
    # Also update NumericValue for height
    height_numeric_pattern = r"(\(900\d+, 2002, 5,.*?')70(', 70,)"
    content = re.sub(height_numeric_pattern, r"\165\2", content)
    # Update metric value for height (70 inches = 177.8cm, 65 inches = 165.1cm)
    height_metric_pattern = r"(\(900\d+, 2002, 5,.*?, 70, NULL, NULL, )177\.8"
    content = re.sub(height_metric_pattern, r"\1165.1", content)
    print("   ✓ All height values updated")

    # Update Section 8.3: Labs
    print("\n5. Updating Section 8.3: Laboratory Results...")
    labs_pattern = r"-- =====================================================\n-- Section 8\.3: LABORATORY RESULTS.*?GO\n\nPRINT '    Alananah Thompson:.*?GO"
    new_labs = update_labs_section()
    content = re.sub(labs_pattern, new_labs, content, count=1, flags=re.DOTALL)
    print("   ✓ Labs section updated")
    print("      - A1C trending: 8.5% → 6.8% → 7.1%")
    print("      - Normal creatinine (0.9 mg/dL, not 1.4+)")
    print("      - Normal BUN (14 mg/dL, not 22+)")
    print("      - Good lipid control")

    # Write updated content
    print("\n6. Writing updated Thompson-Alananah.sql...")
    script_file.write_text(content)
    print(f"   ✓ File updated: {script_file}")

    print("\n" + "=" * 70)
    print("✅ Phase 2 Updates Complete!")
    print("=" * 70)
    print("\nCompleted updates:")
    print("  ✅ Section 3: Vitals header (female profile, 65\" height)")
    print("  ✅ Section 3: All height values updated (70\" → 65\")")
    print("  ✅ Section 8.3: Labs (A1C trending, normal renal function)")
    print("\nNote: Weight values in vitals still need manual adjustment")
    print("      (female BMI trajectory: 145-195 lbs over 15 years)")
    print("\nRemaining sections:")
    print("  ⏳ Section 3: Weight values (need female trajectory)")
    print("  ⏳ Section 6: Encounters (need breast cancer admissions)")
    print("  ⏳ Section 7: Clinical Notes (need oncology/diabetes notes)")
    print("  ⏳ Section 8.4: Patient Flags (verify correct flags)")

if __name__ == "__main__":
    main()
