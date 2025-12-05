/*
|--------------------------------------------------------------------------------
| Insert: BCMA.BCMAAdditive.sql
|--------------------------------------------------------------------------------
| Insert additive data for IV medications
| BCMAAdditiveSID => 11001 series
| Linked to BCMA.BCMAMedicationLog and BCMA.BCMADispensedDrug
| Includes medications/electrolytes added to IV solutions
|--------------------------------------------------------------------------------
*/

PRINT '==== BCMA.BCMAAdditive ====';
GO

-- Set the active database
USE CDWWork;
GO

-- Insert additive data
INSERT INTO BCMA.BCMAAdditive
(
  BCMAAdditiveSID, BCMAAdditiveIEN, BCMAMedicationLogSID, BCMADispensedDrugSID, Sta3n, PatientSID, PatientIEN, InpatientSID, InpatientIEN, AdditiveName, AdditiveStrength, AdditiveAmount, AdditiveUnit, AdditiveSequence, LocalDrugSID, LocalDrugIEN, NationalDrugSID, AdditiveType, OrderNumber
)
VALUES
-- BCMAMedicationLogSID 9018: POTASSIUM CHLORIDE in D5W - Potassium is the additive
(11001, 'AdditiveIEN11001', 9018, 10015, 508, 1004, 'PtIEN1004', 1638004, 'PFIEN004', 'POTASSIUM CHLORIDE', '2MEQ/ML', 20, 'MEQ', 1, 16001, 'DrugIEN16001', 26001, 'ELECTROLYTE', 'IP-2025-004002');
GO
