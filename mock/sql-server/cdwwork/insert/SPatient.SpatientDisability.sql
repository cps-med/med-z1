/*
|--------------------------------------------------------------------------------
| Insert: SPatient.SPatientDisability.sql
|--------------------------------------------------------------------------------
| Expanded test data with realistic service-connected percentages and exposures
| Version: v2.0 (2026-02-07) - Military History Enhancement
|
| SPatientDisabilitySID => 1001-1028 series (original records, corrected)
|                       => 1121-1129 series (new records for 30+ coverage)
|
| Environmental Exposure Codes:
| - AgentOrangeExposureCode: Y=Yes, N=No, U=Unknown
| - IonizingRadiationCode: Y=Yes, N=No, U=Unknown
| - POWStatusCode: Y=Yes, N=No, U=Unknown
| - SHADFlag: Y=Yes, N=No, U=Unknown (Shipboard Hazard and Defense)
| - SWAsiaCode: Y=Yes, N=No, U=Unknown (Southwest Asia/Gulf War)
| - CampLejeuneFlag: Y=Yes, N=No
|
| Target Distribution (30 records, 79% of 38 test patients):
| - 0%: 6 records (20%) - Evaluated but not service-connected
| - 10-30%: 10 records (33%) - Low disability
| - 40-60%: 7 records (23%) - Moderate disability
| - 70-90%: 5 records (17%) - High disability
| - 100%: 1 record (3%) - Total & Permanent Disability
|
| Environmental Exposures (realistic distribution):
| - Agent Orange: 3 records (Vietnam veterans)
| - Ionizing Radiation: 2 records (rare exposure)
| - POW Status: 2 records (Former Prisoners of War)
| - Camp Lejeune: 2 records (Water contamination 1953-1987)
| - Gulf War: 7 records (OIF/OEF/Desert Storm)
|--------------------------------------------------------------------------------
*/

-- Set the active database
USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Clear existing data
DELETE FROM SPatient.SPatientDisability;
GO

-- Insert expanded disability records
INSERT INTO SPatient.SPatientDisability
(
    SPatientDisabilitySID, PatientSID, PatientIEN, Sta3n, ClaimFolderInstitutionSID,
    ServiceConnectedFlag, ServiceConnectedPercent, AgentOrangeExposureCode, IonizingRadiationCode,
    POWStatusCode, SHADFlag, AgentOrangeLocation, POWLocation, SWAsiaCode, CampLejeuneFlag
)
VALUES
-- =============================================
-- Existing Records (Corrected for Data Quality)
-- =============================================

-- Patient 1001: Adam Dooree - Vietnam veteran, Agent Orange exposure, high disability
(1001, 1001, 'PtIEN15401', 508, 11001, 'Y', 90.0, 'Y', 'N', 'N', 'N', 'VIETNAM', NULL, 'N', 'N'),

-- Patient 1002: Barry Miifaa - Gulf War veteran, moderate disability
(1002, 1002, 'PtIEN15402', 508, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1003: Carol Soola - Evaluated but not service-connected
(1003, 1003, 'PtIEN15403', 508, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1004: Debby Tiidoo - Low service-connected percentage
(1004, 1004, 'PtIEN15404', 508, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1005: Edward Dooree - Gulf War veteran, low disability
(1005, 1005, 'PtIEN15405', 508, 11001, 'Y', 20.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1006: Francine Miifaa - Moderate disability
(1006, 1006, 'PtIEN15406', 516, 11001, 'Y', 60.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1007: Adam Amajor - Former POW, Total & Permanent Disability
(1007, 1007, 'PtIEN15407', 516, 11001, 'Y', 100.0, 'N', 'N', 'Y', 'N', NULL, 'VIETNAM', 'N', 'N'),

-- Patient 1008: Barry Bmajor - Moderate disability
(1008, 1008, 'PtIEN15408', 516, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1606021: ZZDUCK, DONN - Evaluated but not service-connected, Former POW (unique case)
(1021, 1606021, 'PtIEN887021', 508, 11001, 'N', 0.0, 'N', 'N', 'Y', 'N', NULL, 'KOREA', 'N', 'N'),

-- Patient 1606026: ZZZ, TEST - Moderate disability
(1026, 1606026, 'PtIEN887026', 516, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1026: Margaret E Wilson - DECEASED - WWII era veteran with radiation exposure
(1027, 1026, 'PtIEN1026', 508, 11001, 'Y', 50.0, 'N', 'Y', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1027: Robert J Anderson - DECEASED - OIF/OEF combat veteran, Camp Lejeune exposure
(1028, 1027, 'PtIEN1027', 528, 11001, 'Y', 70.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'Y'),

-- Patient 1009: Claire Cmajor - Gulf War veteran, low disability
(1109, 1009, 'PtIEN15409', 552, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1010: Alexander Aminor - Gulf War veteran with radiation exposure, high disability
(1110, 1010, 'PtIEN15410', 688, 11001, 'Y', 90.0, 'N', 'Y', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1011: George Harris - Evaluated but not service-connected
(1111, 1011, 'PtIEN15411', 508, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1012: Helen Martinez - Gulf War veteran, high disability
(1112, 1012, 'PtIEN15412', 688, 11001, 'Y', 80.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1013: Irving Thompson - Gulf War veteran, moderate disability
(1113, 1013, 'PtIEN15413', 552, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1014: Joyce Kim - Vietnam veteran, Agent Orange exposure
(1114, 1014, 'PtIEN15414', 508, 11001, 'Y', 20.0, 'Y', 'N', 'N', 'N', 'VIETNAM', NULL, 'N', 'N'),

-- Patient 1015: Kenneth Wilson - Low disability
(1115, 1015, 'PtIEN15415', 552, 11001, 'Y', 30.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1018: David Chen - Gulf War veteran, moderate disability
(1118, 1018, 'PtIEN15418', 668, 11001, 'Y', 50.0, 'N', 'N', 'N', 'N', NULL, NULL, 'Y', 'N'),

-- Patient 1019: Linda Rodriguez - Evaluated but not service-connected
(1119, 1019, 'PtIEN15419', 508, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1020: Robert Thompson - High disability
(1120, 1020, 'PtIEN15420', 516, 11001, 'Y', 80.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- ===========================================
-- New Records (Expanded Coverage - 30+ total)
-- ===========================================

-- Patient 1016: Marcus Johnson - Vietnam veteran, Agent Orange exposure
(1121, 1016, 'PtIEN15416', 516, 11001, 'Y', 30.0, 'Y', 'N', 'N', 'N', 'VIETNAM', NULL, 'N', 'N'),

-- Patient 1017: Sarah Williams - Low disability
(1122, 1017, 'PtIEN15417', 552, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1022: James Anderson - Camp Lejeune exposure, moderate disability
(1123, 1022, 'PtIEN15422', 688, 11001, 'Y', 40.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'Y'),

-- Patient 1023: Barbara Lee - Low disability
(1124, 1023, 'PtIEN15423', 508, 11001, 'Y', 20.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1024: Charles White - Low disability
(1125, 1024, 'PtIEN15424', 516, 11001, 'Y', 30.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1025: Dorothy Martinez - Low disability
(1126, 1025, 'PtIEN15425', 552, 11001, 'Y', 10.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1011533925: ZZTEST, DONNA R - Evaluated but not service-connected
(1127, 1011533925, 'PtIEN533925', 508, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1051720886: ZZTEST, APPLE - High disability
(1128, 1051720886, 'PtIEN720886', 516, 11001, 'Y', 70.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N'),

-- Patient 1060349008: ZZTEST, ABC - Evaluated but not service-connected
(1129, 1060349008, 'PtIEN349008', 552, 11001, 'N', 0.0, 'N', 'N', 'N', 'N', NULL, NULL, 'N', 'N');

GO

-- ========================================
-- Verification Queries
-- ========================================

PRINT 'Total disability records inserted:';
SELECT COUNT(*) AS TotalRecords FROM SPatient.SPatientDisability;

PRINT '';
PRINT 'Distribution by service-connected percentage:';
SELECT
    CASE
        WHEN ServiceConnectedPercent = 0 THEN '0% (Not SC)'
        WHEN ServiceConnectedPercent BETWEEN 1 AND 30 THEN '10-30%'
        WHEN ServiceConnectedPercent BETWEEN 31 AND 60 THEN '40-60%'
        WHEN ServiceConnectedPercent BETWEEN 61 AND 90 THEN '70-90%'
        WHEN ServiceConnectedPercent > 90 THEN '100% (T&P)'
    END AS PercentageRange,
    COUNT(*) AS RecordCount,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM SPatient.SPatientDisability) AS DECIMAL(5,1)) AS Percentage
FROM SPatient.SPatientDisability
GROUP BY
    CASE
        WHEN ServiceConnectedPercent = 0 THEN '0% (Not SC)'
        WHEN ServiceConnectedPercent BETWEEN 1 AND 30 THEN '10-30%'
        WHEN ServiceConnectedPercent BETWEEN 31 AND 60 THEN '40-60%'
        WHEN ServiceConnectedPercent BETWEEN 61 AND 90 THEN '70-90%'
        WHEN ServiceConnectedPercent > 90 THEN '100% (T&P)'
    END
ORDER BY PercentageRange;

PRINT '';
PRINT 'Environmental exposure summary:';
SELECT
    SUM(CASE WHEN AgentOrangeExposureCode = 'Y' THEN 1 ELSE 0 END) AS AgentOrange,
    SUM(CASE WHEN IonizingRadiationCode = 'Y' THEN 1 ELSE 0 END) AS Radiation,
    SUM(CASE WHEN POWStatusCode = 'Y' THEN 1 ELSE 0 END) AS POW,
    SUM(CASE WHEN CampLejeuneFlag = 'Y' THEN 1 ELSE 0 END) AS CampLejeune,
    SUM(CASE WHEN SWAsiaCode = 'Y' THEN 1 ELSE 0 END) AS GulfWar
FROM SPatient.SPatientDisability;

PRINT '';
PRINT 'Service-connected flag distribution:';
SELECT
    ServiceConnectedFlag,
    CASE
        WHEN ServiceConnectedFlag = 'Y' THEN 'Service Connected'
        WHEN ServiceConnectedFlag = 'N' THEN 'Not Service Connected'
        ELSE 'Unknown'
    END AS Description,
    COUNT(*) AS RecordCount
FROM SPatient.SPatientDisability
GROUP BY ServiceConnectedFlag
ORDER BY ServiceConnectedFlag;

GO
