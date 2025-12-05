/*
|--------------------------------------------------------------------------------
| Insert: BCMA.BCMASolution.sql
|--------------------------------------------------------------------------------
| Insert solution data for IV medications
| BCMASolutionSID => 12001 series
| Linked to BCMA.BCMAMedicationLog
| Includes IV solution bags/containers (Normal Saline, D5W, LR, etc.)
|--------------------------------------------------------------------------------
*/

PRINT '==== BCMA.BCMASolution ====';
GO

-- Set the active database
USE CDWWork;
GO

-- Insert solution data
INSERT INTO BCMA.BCMASolution
(
  BCMASolutionSID, BCMASolutionIEN, BCMAMedicationLogSID, Sta3n, PatientSID, PatientIEN, InpatientSID, InpatientIEN, SolutionName, SolutionVolume, SolutionUnit, SolutionStrength, InfusionRate, InfusionRateUnit, FlowRate, FlowRateUnit, InfusionDuration, InfusionDurationUnit, LocalDrugSID, LocalDrugIEN, NationalDrugSID, SolutionType, IVType, OrderNumber, SolutionSequence
)
VALUES
-- BCMAMedicationLogSID 9008: CEFTRIAXONE in NS 100ML (IVPB)
(12001, 'SolutionIEN12001', 9008, 508, 1004, 'PtIEN1004', 1638004, 'PFIEN004', 'SODIUM CHLORIDE 0.9%', 100, 'ML', '0.9%', '100ML/30MIN', 'ML/MIN', 3.33, 'ML/MIN', 30, 'MINUTES', 17001, 'DrugIEN17001', 27001, 'NORMAL SALINE', 'IVPB', 'IP-2025-004001', 1),

-- BCMAMedicationLogSID 9009: CEFTRIAXONE in NS 100ML (IVPB)
(12002, 'SolutionIEN12002', 9009, 508, 1004, 'PtIEN1004', 1638004, 'PFIEN004', 'SODIUM CHLORIDE 0.9%', 100, 'ML', '0.9%', '100ML/30MIN', 'ML/MIN', 3.33, 'ML/MIN', 30, 'MINUTES', 17001, 'DrugIEN17001', 27001, 'NORMAL SALINE', 'IVPB', 'IP-2025-004001', 1),

-- BCMAMedicationLogSID 9016: NORMAL SALINE continuous infusion
(12003, 'SolutionIEN12003', 9016, 516, 1008, 'PtIEN1008', 1638008, 'PFIEN008', 'SODIUM CHLORIDE 0.9%', 1000, 'ML', '0.9%', '125ML/HR', 'ML/HR', 125, 'ML/HR', 8, 'HOURS', 15002, 'DrugIEN15002', 25002, 'NORMAL SALINE', 'CONTINUOUS', 'IP-2025-008001', 1),

-- BCMAMedicationLogSID 9018: POTASSIUM CHLORIDE in D5W 1000ML
(12004, 'SolutionIEN12004', 9018, 508, 1004, 'PtIEN1004', 1638004, 'PFIEN004', 'DEXTROSE 5% IN WATER', 1000, 'ML', '5%', '100ML/HR', 'ML/HR', 100, 'ML/HR', 10, 'HOURS', 17002, 'DrugIEN17002', 27002, 'DEXTROSE 5%', 'IVPB', 'IP-2025-004002', 1);
GO
