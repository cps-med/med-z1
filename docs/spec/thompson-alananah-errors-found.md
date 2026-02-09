# Thompson-Alananah.sql - Errors Found and Corrections Needed

**Date:** 2026-02-09
**Reviewed Against:** Thompson-Bailey.sql (working/correct version)
**Schema Reference:** `mock/sql-server/cdwwork/create/*.sql`

---

## Summary

The draft Thompson-Alananah.sql script contains **major structural errors** in the INSERT statements for multiple domains. The VALUES clauses do not match the column lists, and many field names/values are incorrect or in the wrong order.

---

## Section 14: Immunizations (Lines 1560-1589)

### Error Description
The INSERT statement has correct column names but the VALUES clause is completely wrong:

**Column List (CORRECT):**
```sql
INSERT INTO Immunization.PatientImmunization
(
    PatientSID,
    VaccineSID,
    AdministeredDateTime,
    Series,
    Dose,
    Route,
    SiteOfAdministration,
    Reaction,
    OrderingProviderSID,
    AdministeringProviderSID,
    LocationSID,
    Sta3n,
    LotNumber,
    IsActive
)
```

**VALUES Clause (INCORRECT - Line 1578-1582):**
```sql
VALUES
(NULL, 'Imm2002001', 516, 2002, 'PtIEN2002',
 (SELECT VaccineSID FROM Dim.Vaccine WHERE VaccineName LIKE '%DTAP%' AND Sta3n=516),
 'DTAP (DIPHTHERIA, TETANUS, PERTUSSIS)', '1963-06-15', '1 of 4',
 'N', NULL, '1963-06-15',
 (SELECT LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationName='Primary Care Clinic A' AND LocationType='Outpatient'), 516);
```

### Problems:
1. **Wrong number of values** - VALUES has ~13-14 items, but column list has 14 columns
2. **Wrong order** - Values don't align with column names
3. **Wrong data types** - String 'Imm2002001' where integer PatientSID expected
4. **Extraneous fields** - 'PtIEN2002' doesn't belong in this table
5. **Missing fields** - No Route, Dose, OrderingProviderSID, etc.

### Correct Pattern (from Bailey script):
```sql
VALUES
-- Column order: PatientSID, VaccineSID, AdministeredDateTime, Series, Dose, Route, SiteOfAdministration, Reaction, OrderingProviderSID, AdministeringProviderSID, LocationSID, Sta3n, LotNumber, IsActive
(2001, 18, '2010-10-15 14:00:00', 'ANNUAL 2010', '0.5 ML', 'IM', 'L DELTOID', NULL, 1001, 1002, (SELECT TOP 1 LocationSID FROM Dim.Location WHERE Sta3n=516 AND LocationType='Pharmacy' ORDER BY LocationSID), 516, 'FLU2010', 1)
```

### Action Required:
- Replace entire VALUES section with pattern from Bailey script
- Change PatientSID from 2001 → 2002
- Adjust vaccine series/dates for Alananah's timeline
- Total immunizations: 40 (per requirements doc)

---

## Section 15: Problems/Diagnoses (Lines 1601-1631)

### Error Description
Similar structural errors in the VALUES clause:

**Column List (CORRECT):**
```sql
INSERT INTO Outpat.ProblemList
(
    PatientSID,
    PatientICN,
    Sta3n,
    ProblemNumber,
    SNOMEDCode,
    SNOMEDDescription,
    ICD10Code,
    ICD10Description,
    ProblemStatus,
    OnsetDate,
    RecordedDate,
    LastModifiedDate,
    ResolvedDate,
    ProviderSID,
    ProviderName,
    Clinic,
    IsServiceConnected,
    IsAcuteCondition,
    IsChronicCondition,
    EnteredBy,
    EnteredDateTime
)
```

**VALUES Clause (INCORRECT - Lines 1626-1631):**
```sql
VALUES
(NULL, 'Prob2002001', 516, 2002, 'PtIEN2002',
 '1', 'Prov1010', 'DR. ELIZABETH GARCIA', 'Prov1010', 'DR. ELIZABETH GARCIA',
 '2012-07-02', '2012-07-02', '2012-06-20', NULL,
 'ACTIVE', 'Z85.3', 'PERSONAL HISTORY OF MALIGNANT NEOPLASM OF BREAST', '429740004', 'HISTORY OF BREAST CANCER',
 'PERSONAL HISTORY OF STAGE IIA INVASIVE DUCTAL CARCINOMA RIGHT BREAST. S/P MASTECTOMY, CHEMO, ON TAMOXIFEN. IN REMISSION SINCE 2013.', 'Y', 50,
 'Y', 516);
```

### Problems:
1. **PatientSID = NULL** (should be 2002)
2. **Wrong field order** - ICD10 and SNOMED codes/descriptions are swapped
3. **Extraneous field** - 'PtIEN2002' doesn't belong
4. **Wrong data types** - String 'Prov1010' where integer ProviderSID expected
5. **Duplicate station** - Sta3n appears twice (516 at beginning and end)
6. **ProblemComment field missing** - Long description text should go in ProblemComment, not mixed into VALUES

### Correct Pattern (from Bailey script - Lines 2748-2749):
```sql
VALUES
(2001, 'ICN200001', 516, 'P2001-1', '47505003', 'Post-traumatic stress disorder', 'F43.10', 'Post-traumatic stress disorder, unspecified', 'ACTIVE', '2004-04-12', '2011-02-15', '2024-10-20', NULL, 1001, 'Mitchell, Sarah MD', 'Mental Health', 'Y', 'N', 'Y', 'Mitchell, Sarah MD', '2011-02-15 14:30:00')
```

### Action Required:
- Replace VALUES with correct field order
- Change PatientSID to 2002, PatientICN to 'ICN200002'
- Fix SNOMED/ICD10 code order: SNOMED first, then ICD10
- Use numeric ProviderSID (e.g., 1001)
- Total problems: 16 (per requirements doc)

---

## Additional Sections to Review

Based on the pattern of errors found, the following sections in Thompson-Alananah.sql likely have similar issues:

1. **Demographics** (SPatient.SPatient, Address, Phone, Insurance, Disability)
2. **Vitals** (Vital.VitalSign)
3. **Allergies** (Allergy.PatientAllergy)
4. **Medications** (RxOut.RxOutpat)
5. **Encounters** (Inpat.Inpatient)
6. **Clinical Notes** (TIU.TIUDocument_8925)
7. **Labs** (Chem.LabChem)
8. **Patient Flags** (SPatient.PatientRecordFlagAssignment)

**Recommendation:** Use Thompson-Bailey.sql as the authoritative template for all INSERT statement structures.

---

## Correct Schema References

For authoritative field names and data types, consult:

- `mock/sql-server/cdwwork/create/Immunization.PatientImmunization.sql`
- `mock/sql-server/cdwwork/create/Outpat.ProblemList.sql`
- `mock/sql-server/cdwwork/create/SPatient.SPatient.sql`
- `mock/sql-server/cdwwork/create/Vital.VitalSign.sql`
- `mock/sql-server/cdwwork/create/Allergy.PatientAllergy.sql`
- `mock/sql-server/cdwwork/create/RxOut.RxOutpat.sql`
- `mock/sql-server/cdwwork/create/Inpat.Inpatient.sql`
- `mock/sql-server/cdwwork/create/TIU.TIUDocument_8925.sql`
- `mock/sql-server/cdwwork/create/Chem.LabChem.sql`
- `mock/sql-server/cdwwork/create/SPatient.PatientRecordFlagAssignment.sql`

---

## Next Steps

1. ✅ Document errors (this file)
2. 🔲 Update specification documents with schema cross-references
3. 🔲 Rewrite Thompson-Alananah.sql using Bailey script as template
4. 🔲 Write Thompson-Joe.sql using same corrected template
5. 🔲 Test all three scripts in sequence
