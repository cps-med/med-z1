/*
|----------------------------------------------------------------------
| _add_expansion_patients.sql
|----------------------------------------------------------------------
| Phase 1 Expansion: Adds 10 patients with balanced age/complexity
| distribution expanding the total cohort from 15 to 25 patients.
|
| Patient Cohort Summary:
| - 10 patients: PatientSID 1016-1025
| - Age groups: 3 younger (25-45), 4 middle-aged (46-64), 3 elderly (65+)
| - Geographic area: Sta3n 508, 516, 552, 688 (new: Washington DC VAMC)
| - Total medications: ~62 prescriptions
| - Mental health emphasis: 7/10 patients have mental health conditions
| - Data sources: Mixed (RxOut, BCMA, both)
| - DDI scenarios: 5 designed, 5 natural emergence
| - Temporal complexity: 2-3 medication dates per patient (30-90 day span)
|
| Key DDI Scenarios Included:
| - SSRI + Tramadol (serotonin syndrome)
| - SSRI + NSAID + Antiplatelet (bleeding risk)
| - ACE inhibitor + Potassium-sparing + NSAID (hyperkalemia, renal)
| - ACE inhibitor + NSAID in CKD patient (acute renal failure risk)
| - Clopidogrel + Omeprazole (reduced antiplatelet effect)
| - Multiple mental health medication combinations
|
| Execution: Run this script after initial database setup
| sqlcmd -S 127.0.0.1,1433 -U sa -P "PASSWORD" -d CDWWork -i _add_expansion_patients.sql
|--------------------------------------------------------------------------------
*/

PRINT '================================================';
PRINT '=== ADD 10 EXPANSION PATIENTS (PHASE 1) ===';
PRINT '================================================';
GO

-- Set the active database
USE CDWWork;
GO

/*
|--------------------------------------------------------------------------------
| SECTION 1: Patient Demographics (SPatient.SPatient)
|--------------------------------------------------------------------------------
*/

PRINT '';
PRINT '==== SECTION 1: Adding 10 Expansion Patients ====';
GO

INSERT INTO SPatient.SPatient
(
 PatientSID, PatientIEN, Sta3n, PatientName, PatientLastName, PatientFirstName,
 TestPatientFlag, CDWPossibleTestPatientFlag, VeteranFlag, PatientType, PatientTypeSID,
 PatientICN, ScrSSN, PatientSSN, PseudoSSNReason, SSNVerificationStatus,
 GovernmentEmployeeFlag, SensitiveFlag, Age, BirthDateTime, BirthVistaErrorDate,
 BirthDateTimeTransformSID, DeceasedFlag, DeathDateTime, DeathVistaErrorDate,
 DeathDateTimeTransformSID, DeathEnteredByStaffSID, DeathNotificationSource,
 DeathDocumentationType, DeathModifiedDateTime, DeathModifiedVistaErrorDate,
 DeathModifiedDateTimeTransformSID, DeathLastUpdatedByStaffSID, Gender,
 SelfIdentifiedGender, Religion, ReligionSID, MaritalStatus, MaritalStatusSID,
 CollateralSponsorPatientSID, CurrentEnrollmentSID, MeansTestStatus, CurrentMeansTestStatusSID,
 PeriodOfService, PeriodOfServiceSID, OperationDesertShieldRank, ODSRankType,
 ODSRecalledCode, ODSTreatmentDateTime, ODSTreatmentVistaErrorDate, ODSTreatmentDateTimeTransformSID,
 FederalAgencySID, FilipinoVeteranCode, ServiceConnectedFlag, Eligibility, EligibilityVACode,
 EligibilitySID, EligibilityStatus, EligibilityStatusDateTime, EligibilityStatusVistaErrorDate,
 EligibilityStatusDateTimeTransformSID, EligibilityVerificationSource, EligibilityVerificationMethod,
 EligibilityInterimDateTime, EligibilityInterimVistaErrorDate, EligibilityInterimDateTimeTransformSID,
 EligibilityEnteredStaffSID, IneligibleReason, IneligibleVAROReason, IneligibleCity,
 IneligibleStateSID, IneligibleDateTime, IneligibleVistaErrorDate, IneligibleDateTimeTransformSID,
 IneligibleSource, PatientMissingSource, PatientMissingDateTime, PatientMissingVistaErrorDate,
 PatientMissingDateTimeTransformSID, PatientMissingCity, PatientMissingStateSID,
 FugitiveFelonFlag, FFFEnteredDateTime, FFFEnteredVistaErrorDate, FFFEnteredDateTimeTransformSID,
 FFFEnteredStaffSID, FFFRemovedReason, FFFRemovedDateTime, FFFRemovedVistaErrorDate,
 FFFRemovedDateTimeTransformSID, FFFRemovedStaffSID, PatientEnteredByStaffSID, PatientEnteredCode,
 PatientEnteredRemark, PatientEnteredDateTime, PatientEnteredVistaErrorDate, PatientEnteredDateTimeTransformSID,
 DuplicateRecordStatus, DestinationMergePatientSID, PreferredInstitutionSID, PreferredInstitutionSource,
 EmergencyResponseIndicator, InsuranceCoverageFlag, MedicaidEligibleFlag, MedicaidNumber,
 MedicaidInquireDateTime, MedicaidInquireVistaErrorDate, MedicaidInquireDateTimeTransformSID,
 VeteranTransportationProgramFlag
)
VALUES
-- ========== YOUNGER PATIENTS (Ages 25-45) ==========

-- Patient 1016: Age 28, PTSD, Depression - Washington DC VAMC
(1016, 'PtIEN1016', 688, 'Marcus Johnson', 'Johnson', 'Marcus', 'N', 'N', 'Y', 'Regular', 101, '1016V123456', '777771016', '777771016', 'None', 'Verified', 'N', 'N', 28, '1996-03-15', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'M', 'Male', 'Christian', 1, 'SINGLE', 1, NULL, 1016, 'None', NULL, 'OIF/OEF', 12007, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-15', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1017: Age 35, Anxiety, Chronic Pain - Atlanta VAMC
(1017, 'PtIEN1017', 508, 'Sarah Williams', 'Williams', 'Sarah', 'N', 'N', 'Y', 'Regular', 101, '1017V234567', '888881017', '888881017', 'None', 'Verified', 'N', 'N', 35, '1989-07-22', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'F', 'Female', 'Protestant', 2, 'DIVORCED', 4, NULL, 1017, 'None', NULL, 'OIF/OEF', 12007, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-01', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1018: Age 42, Type 2 Diabetes - Honolulu VAMC
(1018, 'PtIEN1018', 516, 'David Chen', 'Chen', 'David', 'N', 'N', 'Y', 'Regular', 101, '1018V345678', '999991018', '999991018', 'None', 'Verified', 'N', 'N', 42, '1982-11-08', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'M', 'Male', 'Buddhist', 3, 'MARRIED', 2, NULL, 1018, 'None', NULL, 'PERSIAN GULF', 12005, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-20', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- ========== MIDDLE-AGED PATIENTS (Ages 46-64) ==========

-- Patient 1019: Age 48, Depression, Hypertension - Dayton VAMC
(1019, 'PtIEN1019', 552, 'Linda Rodriguez', 'Rodriguez', 'Linda', 'N', 'N', 'Y', 'Regular', 101, '1019V456789', '111101019', '111101019', 'None', 'Verified', 'N', 'N', 48, '1976-05-14', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'F', 'Female', 'Catholic', 2, 'MARRIED', 2, NULL, 1019, 'None', NULL, 'PERSIAN GULF', 12005, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-10', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1020: Age 53, COPD, Anxiety - Washington DC VAMC
(1020, 'PtIEN1020', 688, 'Robert Thompson', 'Thompson', 'Robert', 'N', 'N', 'Y', 'Regular', 101, '1020V567890', '222201020', '222201020', 'None', 'Verified', 'N', 'N', 53, '1971-09-30', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'M', 'Male', 'Christian', 1, 'MARRIED', 2, NULL, 1020, 'None', NULL, 'PERSIAN GULF', 12005, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-05', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1021: Age 58, Diabetes, CHF - Atlanta VAMC
(1021, 'PtIEN1021', 508, 'Patricia Garcia', 'Garcia', 'Patricia', 'N', 'N', 'Y', 'Regular', 101, '1021V678901', '333301021', '333301021', 'None', 'Verified', 'N', 'N', 58, '1966-12-03', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'F', 'Female', 'Catholic', 2, 'WIDOWED', 3, NULL, 1021, 'None', NULL, 'VIETNAM ERA', 12004, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-08', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1022: Age 61, CKD, Chronic Pain - Honolulu VAMC
(1022, 'PtIEN1022', 516, 'James Anderson', 'Anderson', 'James', 'N', 'N', 'Y', 'Regular', 101, '1022V789012', '444401022', '444401022', 'None', 'Verified', 'N', 'N', 61, '1963-04-17', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'M', 'Male', 'Protestant', 2, 'MARRIED', 2, NULL, 1022, 'None', NULL, 'VIETNAM ERA', 12004, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-12', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- ========== ELDERLY PATIENTS (Ages 65+) ==========

-- Patient 1023: Age 67, Depression, Diabetes, Hyperlipidemia - Dayton VAMC
(1023, 'PtIEN1023', 552, 'Barbara Lee', 'Lee', 'Barbara', 'N', 'N', 'Y', 'Regular', 101, '1023V890123', '555501023', '555501023', 'None', 'Verified', 'N', 'N', 67, '1957-08-25', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'F', 'Female', 'Methodist', 5, 'MARRIED', 2, NULL, 1023, 'None', NULL, 'VIETNAM ERA', 12004, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-05', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1024: Age 74, CHF, AFib, CKD - Washington DC VAMC
(1024, 'PtIEN1024', 688, 'Charles White', 'White', 'Charles', 'N', 'N', 'Y', 'Regular', 101, '1024V901234', '666601024', '666601024', 'None', 'Verified', 'N', 'N', 74, '1950-02-11', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'M', 'Male', 'Protestant', 2, 'WIDOWED', 3, NULL, 1024, 'None', NULL, 'VIETNAM ERA', 12004, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-12', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y'),

-- Patient 1025: Age 79, COPD, Diabetes, HTN, Depression - Honolulu VAMC
(1025, 'PtIEN1025', 516, 'Dorothy Martinez', 'Martinez', 'Dorothy', 'N', 'N', 'Y', 'Regular', 101, '1025V012345', '777701025', '777701025', 'None', 'Verified', 'N', 'N', 79, '1945-06-19', NULL, NULL, 'N', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'F', 'Female', 'Catholic', 2, 'WIDOWED', 3, NULL, 1025, 'None', NULL, 'WWII', 12003, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, 'VERIFIED', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-18', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Y');
GO

PRINT '  ✓ Added 10 expansion patients (PatientSID 1016-1025)';
PRINT '    - 3 younger (25-45): 1016, 1017, 1018';
PRINT '    - 4 middle-aged (46-64): 1019, 1020, 1021, 1022';
PRINT '    - 3 elderly (65+): 1023, 1024, 1025';
GO

/*
|--------------------------------------------------------------------------------
| SECTION 2: Patient Addresses with Geographic Location (SPatient.SPatientAddress)
|--------------------------------------------------------------------------------
*/

PRINT '';
PRINT '==== SECTION 2: Adding Patient Addresses ====';
GO

INSERT INTO SPatient.SPatientAddress
(
    SPatientAddressSID, PatientSID, PatientIEN, Sta3n, OrdinalNumber, AddressType,
    StreetAddress1, StreetAddress2, StreetAddress3, City, County,
    [State], StateSID, Zip, Zip4, PostalCode, Country, CountrySID, EmploymentStatus
)
VALUES
-- Sta3n 688: Washington DC VAMC (new facility)
(1016, 1016, 'PtIEN1016', 688, 1, 'HOME', '1234 Constitution Ave NW', 'Apt 5B', '', 'Washington', 'District of Columbia', 'DC', 3561, '20001', '200010016', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1020, 1020, 'PtIEN1020', 688, 1, 'HOME', '5678 Wisconsin Ave NW', '', '', 'Washington', 'District of Columbia', 'DC', 3561, '20016', '200160020', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1024, 1024, 'PtIEN1024', 688, 1, 'HOME', '910 Pennsylvania Ave SE', '', '', 'Washington', 'District of Columbia', 'DC', 3561, '20003', '200030024', '', 'UNITED STATES', 1200005271, 'RETIRED'),

-- Sta3n 508: Atlanta VAMC
(1017, 1017, 'PtIEN1017', 508, 1, 'HOME', '2468 Clairmont Rd', '', '', 'Decatur', 'DeKalb', 'GA', 415, '30033', '300330017', '', 'UNITED STATES', 1200005271, 'UNEMPLOYED'),
(1021, 1021, 'PtIEN1021', 508, 1, 'HOME', '1357 Memorial Dr SE', '', '', 'Atlanta', 'Fulton', 'GA', 415, '30312', '303120021', '', 'UNITED STATES', 1200005271, 'RETIRED'),

-- Sta3n 516: Honolulu VAMC
(1018, 1018, 'PtIEN1018', 516, 1, 'HOME', '753 Kapiolani Blvd', 'Unit 12', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96814', '968140018', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1022, 1022, 'PtIEN1022', 516, 1, 'HOME', '951 Ala Moana Blvd', '', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96814', '968140022', '', 'UNITED STATES', 1200005271, 'RETIRED'),
(1025, 1025, 'PtIEN1025', 516, 1, 'HOME', '357 King Street', 'Apt 8C', '', 'Honolulu', 'Honolulu', 'HI', 1792, '96813', '968130025', '', 'UNITED STATES', 1200005271, 'RETIRED'),

-- Sta3n 552: Dayton VAMC
(1019, 1019, 'PtIEN1019', 552, 1, 'HOME', '246 Oakwood Ave', '', '', 'Dayton', 'Montgomery', 'OH', 4963, '45419', '454190019', '', 'UNITED STATES', 1200005271, 'EMPLOYED'),
(1023, 1023, 'PtIEN1023', 552, 1, 'HOME', '159 Shiloh Springs Rd', '', '', 'Dayton', 'Montgomery', 'OH', 4963, '45415', '454150023', '', 'UNITED STATES', 1200005271, 'RETIRED');
GO

PRINT '  ✓ Added 10 patient addresses';
PRINT '    - Sta3n 508 (Atlanta): 2 patients';
PRINT '    - Sta3n 516 (Honolulu): 3 patients';
PRINT '    - Sta3n 552 (Dayton): 2 patients';
PRINT '    - Sta3n 688 (Washington DC): 3 patients';
GO

/*
|--------------------------------------------------------------------------------
| SECTION 3: Outpatient Prescriptions (RxOut.RxOutpat)
| Total: ~40 prescriptions with temporal patterns
| Mix of RxOut-only, RxOut+BCMA patients
|--------------------------------------------------------------------------------
*/

PRINT '';
PRINT '==== SECTION 3: Adding Outpatient Prescriptions ====';
GO

INSERT INTO RxOut.RxOutpat
(
  RxOutpatSID, RxOutpatIEN, Sta3n, PatientSID, PatientIEN, LocalDrugSID, LocalDrugIEN,
  NationalDrugSID, DrugNameWithoutDose, DrugNameWithDose, PrescriptionNumber,
  IssueDateTime, IssueVistaErrorDate, IssueDateTimeTransformSID, ProviderSID, ProviderIEN,
  OrderingProviderSID, OrderingProviderIEN, EnteredByStaffSID, EnteredByStaffIEN,
  PharmacySID, PharmacyIEN, PharmacyName, RxStatus, RxType, Quantity, DaysSupply,
  RefillsAllowed, RefillsRemaining, MaxRefills, UnitDose, ExpirationDateTime,
  ExpirationVistaErrorDate, ExpirationDateTimeTransformSID, DiscontinuedDateTime,
  DiscontinuedVistaErrorDate, DiscontinuedDateTimeTransformSID, DiscontinueReason,
  DiscontinuedByStaffSID, LoginDateTime, LoginVistaErrorDate, LoginDateTimeTransformSID,
  ClinicSID, ClinicIEN, ClinicName, DEASchedule, ControlledSubstanceFlag,
  CMOPIndicator, MailIndicator
)
VALUES
-- ========== PATIENT 1016: Marcus Johnson (3 meds, RxOut+BCMA) ==========
-- Day 0: Sertraline started
(5061, 'RxIEN5061', 688, 1016, 'PtIEN1016', 10027, 'DrugIEN10027', 20027, 'SERTRALINE HCL', 'SERTRALINE HCL 100MG TAB', '2024-016-0001', '2025-01-15 10:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-15 10:00:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: Prazosin added
(5062, 'RxIEN5062', 688, 1016, 'PtIEN1016', 10028, 'DrugIEN10028', 20028, 'PRAZOSIN HCL', 'PRAZOSIN HCL 2MG CAP', '2024-016-0002', '2025-02-14 09:30:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 4, 5, '1 CAP', '2025-08-14 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-14 09:30:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 60: Trazodone added
(5063, 'RxIEN5063', 688, 1016, 'PtIEN1016', 10029, 'DrugIEN10029', 20029, 'TRAZODONE HCL', 'TRAZODONE HCL 50MG TAB', '2024-016-0003', '2025-03-15 10:15:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-15 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-15 10:15:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),

-- ========== PATIENT 1017: Sarah Williams (4 meds, RxOut only) ==========
-- Day 0: Escitalopram, Cyclobenzaprine started
(5064, 'RxIEN5064', 508, 1017, 'PtIEN1017', 10030, 'DrugIEN10030', 20030, 'ESCITALOPRAM OXALATE', 'ESCITALOPRAM OXALATE 10MG TAB', '2024-017-0001', '2025-02-01 11:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-08-01 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-01 11:00:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
(5065, 'RxIEN5065', 508, 1017, 'PtIEN1017', 10031, 'DrugIEN10031', 20031, 'CYCLOBENZAPRINE HCL', 'CYCLOBENZAPRINE HCL 10MG TAB', '2024-017-0002', '2025-02-01 11:05:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 3, 3, 3, '1 TAB', '2025-08-01 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-01 11:05:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: Ibuprofen added
(5066, 'RxIEN5066', 508, 1017, 'PtIEN1017', 10013, 'DrugIEN10013', 20013, 'IBUPROFEN', 'IBUPROFEN 600MG TAB', '2024-017-0003', '2025-03-02 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'WINDOW', 120, 30, 3, 2, 3, '1 TAB', '2025-09-02 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-02 10:00:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),
-- Day 60: Tramadol added (creates DDI with Escitalopram)
(5067, 'RxIEN5067', 508, 1017, 'PtIEN1017', 10032, 'DrugIEN10032', 20032, 'TRAMADOL HCL', 'TRAMADOL HCL 50MG TAB', '2024-017-0004', '2025-04-01 09:45:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'WINDOW', 60, 30, 2, 2, 2, '1 TAB', '2025-10-01 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-04-01 09:45:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', 'IV', 'Y', 'N', 'N'),

-- ========== PATIENT 1019: Linda Rodriguez (5 meds, RxOut+BCMA) ==========
-- Day 0: Fluoxetine, Lisinopril, Aspirin started
(5068, 'RxIEN5068', 552, 1019, 'PtIEN1019', 10033, 'DrugIEN10033', 20033, 'FLUOXETINE HCL', 'FLUOXETINE HCL 40MG CAP', '2024-019-0001', '2025-01-10 10:00:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 CAP', '2025-07-10 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-10 10:00:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
(5069, 'RxIEN5069', 552, 1019, 'PtIEN1019', 10002, 'DrugIEN10002', 20002, 'LISINOPRIL', 'LISINOPRIL 10MG TAB', '2024-019-0002', '2025-01-10 10:05:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-10 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-10 10:05:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5070, 'RxIEN5070', 552, 1019, 'PtIEN1019', 10019, 'DrugIEN10019', 20019, 'ASPIRIN', 'ASPIRIN 81MG TAB EC', '2024-019-0003', '2025-01-10 10:10:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-10 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-10 10:10:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: HCTZ added
(5071, 'RxIEN5071', 552, 1019, 'PtIEN1019', 10034, 'DrugIEN10034', 20034, 'HYDROCHLOROTHIAZIDE', 'HYDROCHLOROTHIAZIDE 25MG TAB', '2024-019-0004', '2025-02-09 09:30:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 4, 5, '1 TAB', '2025-08-09 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-09 09:30:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 60: Ibuprofen added (creates triple DDI: SSRI+Aspirin+NSAID)
(5072, 'RxIEN5072', 552, 1019, 'PtIEN1019', 10026, 'DrugIEN10026', 20026, 'IBUPROFEN', 'IBUPROFEN 400MG TAB', '2024-019-0005', '2025-03-10 10:15:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'WINDOW', 120, 30, 3, 3, 3, '1 TAB', '2025-09-10 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-10 10:15:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),

-- ========== PATIENT 1020: Robert Thompson (5 meds, RxOut only) ==========
-- Day 0: Albuterol, Tiotropium, Advair started
(5073, 'RxIEN5073', 688, 1020, 'PtIEN1020', 10035, 'DrugIEN10035', 20035, 'ALBUTEROL SULFATE', 'ALBUTEROL SULFATE MDI', '2024-020-0001', '2025-02-05 11:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'WINDOW', 17, 90, 5, 5, 5, '2 PUFFS', '2025-08-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-05 11:00:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'N', 'N'),
(5074, 'RxIEN5074', 688, 1020, 'PtIEN1020', 10036, 'DrugIEN10036', 20036, 'TIOTROPIUM BROMIDE', 'TIOTROPIUM BROMIDE 18MCG INH', '2024-020-0002', '2025-02-05 11:05:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 INH', '2025-08-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-05 11:05:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'Y', 'Y'),
(5075, 'RxIEN5075', 688, 1020, 'PtIEN1020', 10037, 'DrugIEN10037', 20037, 'FLUTICASONE-SALMETEROL', 'FLUTICASONE-SALMETEROL 250-50MCG INH', '2024-020-0003', '2025-02-05 11:10:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 60, 60, 5, 4, 5, '2 PUFFS', '2025-08-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-05 11:10:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: Lorazepam added for anxiety
(5076, 'RxIEN5076', 688, 1020, 'PtIEN1020', 10038, 'DrugIEN10038', 20038, 'LORAZEPAM', 'LORAZEPAM 1MG TAB', '2024-020-0004', '2025-03-06 10:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'WINDOW', 60, 30, 2, 2, 2, '1 TAB', '2025-09-06 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-06 10:00:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', 'IV', 'Y', 'N', 'N'),
-- Day 60: Prednisone taper
(5077, 'RxIEN5077', 688, 1020, 'PtIEN1020', 10039, 'DrugIEN10039', 20039, 'PREDNISONE', 'PREDNISONE 10MG TAB', '2024-020-0005', '2025-04-05 09:45:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'WINDOW', 21, 21, 0, 0, 0, '1 TAB', '2025-10-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-04-05 09:45:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'N', 'N'),

-- ========== PATIENT 1021: Patricia Garcia (6 meds, RxOut+BCMA) ==========
-- Day 0: Metformin, Lisinopril, Carvedilol, Insulin started
(5078, 'RxIEN5078', 508, 1021, 'PtIEN1021', 10001, 'DrugIEN10001', 20001, 'METFORMIN HCL', 'METFORMIN HCL 1000MG TAB', '2024-021-0001', '2025-01-08 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 5, 5, '1 TAB', '2025-07-08 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-08 10:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5079, 'RxIEN5079', 508, 1021, 'PtIEN1021', 10002, 'DrugIEN10002', 20002, 'LISINOPRIL', 'LISINOPRIL 20MG TAB', '2024-021-0002', '2025-01-08 10:05:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-08 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-08 10:05:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5080, 'RxIEN5080', 508, 1021, 'PtIEN1021', 10040, 'DrugIEN10040', 20040, 'CARVEDILOL', 'CARVEDILOL 12.5MG TAB', '2024-021-0003', '2025-01-08 10:10:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 4, 5, '1 TAB', '2025-07-08 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-08 10:10:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5081, 'RxIEN5081', 508, 1021, 'PtIEN1021', 10041, 'DrugIEN10041', 20041, 'INSULIN GLARGINE', 'INSULIN GLARGINE 100 UNIT/ML INJ', '2024-021-0004', '2025-01-08 10:15:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'WINDOW', 10, 30, 5, 5, 5, '20 UNITS', '2025-07-08 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-08 10:15:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'N', 'N'),
-- Day 30: Spironolactone added for CHF (creates hyperkalemia risk with Lisinopril)
(5082, 'RxIEN5082', 508, 1021, 'PtIEN1021', 10024, 'DrugIEN10024', 20024, 'SPIRONOLACTONE', 'SPIRONOLACTONE 25MG TAB', '2024-021-0005', '2025-02-07 09:30:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-08-07 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-07 09:30:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 60: Naproxen added (creates triple DDI: ACE-I+K-sparing+NSAID)
(5083, 'RxIEN5083', 508, 1021, 'PtIEN1021', 10042, 'DrugIEN10042', 20042, 'NAPROXEN SODIUM', 'NAPROXEN SODIUM 500MG TAB', '2024-021-0006', '2025-03-08 10:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 5001, 'PharmIEN5001', 'VA ATLANTA MAIN PHARMACY', 'ACTIVE', 'WINDOW', 60, 30, 2, 2, 2, '1 TAB', '2025-09-08 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-08 10:00:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),

-- ========== PATIENT 1023: Barbara Lee (7 meds, RxOut+BCMA) ==========
-- Day 0: Metformin, Atorvastatin, Aspirin, Losartan started
(5084, 'RxIEN5084', 552, 1023, 'PtIEN1023', 10001, 'DrugIEN10001', 20001, 'METFORMIN HCL', 'METFORMIN HCL 850MG TAB', '2024-023-0001', '2025-01-05 10:00:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 5, 5, '1 TAB', '2025-07-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-05 10:00:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5085, 'RxIEN5085', 552, 1023, 'PtIEN1023', 10003, 'DrugIEN10003', 20003, 'ATORVASTATIN CALCIUM', 'ATORVASTATIN CALCIUM 40MG TAB', '2024-023-0002', '2025-01-05 10:05:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-05 10:05:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5086, 'RxIEN5086', 552, 1023, 'PtIEN1023', 10019, 'DrugIEN10019', 20019, 'ASPIRIN', 'ASPIRIN 81MG TAB EC', '2024-023-0003', '2025-01-05 10:10:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-05 10:10:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5087, 'RxIEN5087', 552, 1023, 'PtIEN1023', 10043, 'DrugIEN10043', 20043, 'LOSARTAN POTASSIUM', 'LOSARTAN POTASSIUM 50MG TAB', '2024-023-0004', '2025-01-05 10:15:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 4, 5, '1 TAB', '2025-07-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-05 10:15:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: Citalopram added for depression
(5088, 'RxIEN5088', 552, 1023, 'PtIEN1023', 10044, 'DrugIEN10044', 20044, 'CITALOPRAM HBR', 'CITALOPRAM HBR 20MG TAB', '2024-023-0005', '2025-02-04 09:30:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-08-04 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-04 09:30:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 60: Clopidogrel + Omeprazole added post-cardiac stent (creates DDI)
(5089, 'RxIEN5089', 552, 1023, 'PtIEN1023', 10022, 'DrugIEN10022', 20022, 'CLOPIDOGREL BISULFATE', 'CLOPIDOGREL BISULFATE 75MG TAB', '2024-023-0006', '2025-03-05 10:00:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-05 10:00:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5090, 'RxIEN5090', 552, 1023, 'PtIEN1023', 10014, 'DrugIEN10014', 20014, 'OMEPRAZOLE', 'OMEPRAZOLE 20MG CAP DR', '2024-023-0007', '2025-03-05 10:05:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 5003, 'PharmIEN5003', 'VA DAYTON MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 CAP', '2025-09-05 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-05 10:05:00', NULL, NULL, 8007, 'ClinicIEN8007', 'GASTROENTEROLOGY CLINIC', NULL, 'N', 'Y', 'Y'),

-- ========== PATIENT 1024: Charles White (8 meds, RxOut+BCMA) ==========
-- Day 0: Metoprolol, Apixaban, Furosemide, Lisinopril started
(5091, 'RxIEN5091', 688, 1024, 'PtIEN1024', 10011, 'DrugIEN10011', 20011, 'METOPROLOL TARTRATE', 'METOPROLOL TARTRATE 50MG TAB', '2024-024-0001', '2025-01-12 10:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 5, 5, '1 TAB', '2025-07-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-12 10:00:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5092, 'RxIEN5092', 688, 1024, 'PtIEN1024', 10045, 'DrugIEN10045', 20045, 'APIXABAN', 'APIXABAN 5MG TAB', '2024-024-0002', '2025-01-12 10:05:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 60, 60, 5, 5, 5, '1 TAB', '2025-07-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-12 10:05:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5093, 'RxIEN5093', 688, 1024, 'PtIEN1024', 10021, 'DrugIEN10021', 20021, 'FUROSEMIDE', 'FUROSEMIDE 40MG TAB', '2024-024-0003', '2025-01-12 10:10:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 4, 5, '1 TAB', '2025-07-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-12 10:10:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5094, 'RxIEN5094', 688, 1024, 'PtIEN1024', 10002, 'DrugIEN10002', 20002, 'LISINOPRIL', 'LISINOPRIL 10MG TAB', '2024-024-0004', '2025-01-12 10:15:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-12 10:15:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 30: Spironolactone, Digoxin added
(5095, 'RxIEN5095', 688, 1024, 'PtIEN1024', 10024, 'DrugIEN10024', 20024, 'SPIRONOLACTONE', 'SPIRONOLACTONE 25MG TAB', '2024-024-0005', '2025-02-11 09:30:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-08-11 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-11 09:30:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5096, 'RxIEN5096', 688, 1024, 'PtIEN1024', 10023, 'DrugIEN10023', 20023, 'DIGOXIN', 'DIGOXIN 0.125MG TAB', '2024-024-0006', '2025-02-11 09:35:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 4, 5, '1 TAB', '2025-08-11 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-02-11 09:35:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 60: Potassium supplement, Atorvastatin added
(5097, 'RxIEN5097', 688, 1024, 'PtIEN1024', 10046, 'DrugIEN10046', 20046, 'POTASSIUM CHLORIDE', 'POTASSIUM CHLORIDE 20MEQ TAB ER', '2024-024-0007', '2025-03-12 10:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-12 10:00:00', NULL, NULL, 8005, 'ClinicIEN8005', 'CARDIOLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5098, 'RxIEN5098', 688, 1024, 'PtIEN1024', 10003, 'DrugIEN10003', 20003, 'ATORVASTATIN CALCIUM', 'ATORVASTATIN CALCIUM 20MG TAB', '2024-024-0008', '2025-03-12 10:05:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 5004, 'PharmIEN5004', 'VA DC MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-12 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-12 10:05:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),

-- ========== PATIENT 1025: Dorothy Martinez (9 meds, RxOut only) ==========
-- Day 0: Tiotropium, Advair, Metformin, Amlodipine started
(5099, 'RxIEN5099', 516, 1025, 'PtIEN1025', 10036, 'DrugIEN10036', 20036, 'TIOTROPIUM BROMIDE', 'TIOTROPIUM BROMIDE 18MCG INH', '2024-025-0001', '2025-01-18 10:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 INH', '2025-07-18 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-18 10:00:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'Y', 'Y'),
(5100, 'RxIEN5100', 516, 1025, 'PtIEN1025', 10037, 'DrugIEN10037', 20037, 'FLUTICASONE-SALMETEROL', 'FLUTICASONE-SALMETEROL 250-50MCG INH', '2024-025-0002', '2025-01-18 10:05:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 60, 60, 5, 5, 5, '2 PUFFS', '2025-07-18 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-18 10:05:00', NULL, NULL, 8009, 'ClinicIEN8009', 'PULMONARY CLINIC', NULL, 'N', 'Y', 'Y'),
(5101, 'RxIEN5101', 516, 1025, 'PtIEN1025', 10047, 'DrugIEN10047', 20047, 'METFORMIN HCL', 'METFORMIN HCL 500MG TAB', '2024-025-0003', '2025-01-18 10:10:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 180, 90, 5, 4, 5, '1 TAB', '2025-07-18 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-18 10:10:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5102, 'RxIEN5102', 516, 1025, 'PtIEN1025', 10017, 'DrugIEN10017', 20017, 'AMLODIPINE BESYLATE', 'AMLODIPINE BESYLATE 5MG TAB', '2024-025-0004', '2025-01-18 10:15:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-07-18 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-01-18 10:15:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
-- Day 45: Glipizide, Sertraline, Acetaminophen added
(5103, 'RxIEN5103', 516, 1025, 'PtIEN1025', 10048, 'DrugIEN10048', 20048, 'GLIPIZIDE', 'GLIPIZIDE 10MG TAB', '2024-025-0005', '2025-03-03 09:30:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-03 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-03 09:30:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y'),
(5104, 'RxIEN5104', 516, 1025, 'PtIEN1025', 10049, 'DrugIEN10049', 20049, 'SERTRALINE HCL', 'SERTRALINE HCL 50MG TAB', '2024-025-0006', '2025-03-03 09:35:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-09-03 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-03 09:35:00', NULL, NULL, 8008, 'ClinicIEN8008', 'MENTAL HEALTH CLINIC', NULL, 'N', 'Y', 'Y'),
(5105, 'RxIEN5105', 516, 1025, 'PtIEN1025', 10050, 'DrugIEN10050', 20050, 'ACETAMINOPHEN', 'ACETAMINOPHEN 650MG TAB', '2024-025-0007', '2025-03-03 09:40:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'WINDOW', 200, 100, 3, 3, 3, '1 TAB', '2025-09-03 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-03-03 09:40:00', NULL, NULL, 8003, 'ClinicIEN8003', 'PAIN MANAGEMENT CLINIC', NULL, 'N', 'N', 'N'),
-- Day 75: Omeprazole, Multivitamin added
(5106, 'RxIEN5106', 516, 1025, 'PtIEN1025', 10014, 'DrugIEN10014', 20014, 'OMEPRAZOLE', 'OMEPRAZOLE 20MG CAP DR', '2024-025-0008', '2025-04-02 10:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 CAP', '2025-10-02 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-04-02 10:00:00', NULL, NULL, 8007, 'ClinicIEN8007', 'GASTROENTEROLOGY CLINIC', NULL, 'N', 'Y', 'Y'),
(5107, 'RxIEN5107', 516, 1025, 'PtIEN1025', 10051, 'DrugIEN10051', 20051, 'MULTIVITAMIN', 'MULTIVITAMIN TAB', '2024-025-0009', '2025-04-02 10:05:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 5002, 'PharmIEN5002', 'VA HONOLULU MAIN PHARMACY', 'ACTIVE', 'MAIL', 90, 90, 5, 5, 5, '1 TAB', '2025-10-02 00:00:00', NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-04-02 10:05:00', NULL, NULL, 8001, 'ClinicIEN8001', 'PRIMARY CARE CLINIC', NULL, 'N', 'Y', 'Y');
GO

PRINT '  ✓ Added 47 outpatient prescriptions';
PRINT '    - Patient 1016: 3 meds (RxOut)';
PRINT '    - Patient 1017: 4 meds (RxOut)';
PRINT '    - Patient 1019: 5 meds (RxOut)';
PRINT '    - Patient 1020: 5 meds (RxOut)';
PRINT '    - Patient 1021: 6 meds (RxOut)';
PRINT '    - Patient 1023: 7 meds (RxOut)';
PRINT '    - Patient 1024: 8 meds (RxOut)';
PRINT '    - Patient 1025: 9 meds (RxOut)';
PRINT '    - Note: Patients 1018, 1022 have BCMA-only (no RxOut)';
GO

/*
|--------------------------------------------------------------------------------
| SECTION 4: BCMA Medication Administration (BCMA.BCMAMedicationLog)
| For patients with BCMA data source: 1016, 1018, 1019, 1021, 1022, 1023, 1024
|--------------------------------------------------------------------------------
*/

PRINT '';
PRINT '==== SECTION 4: Adding BCMA Medication Administration Records ====';
GO

INSERT INTO BCMA.BCMAMedicationLog
(
  BCMAMedicationLogSID, BCMAMedicationLogIEN, Sta3n, PatientSID, PatientIEN, InpatientSID,
  InpatientIEN, ActionType, ActionStatus, ActionDateTime, ActionVistaErrorDate,
  ActionDateTimeTransformSID, ScheduledDateTime, ScheduledVistaErrorDate, ScheduledDateTimeTransformSID,
  OrderedDateTime, OrderedVistaErrorDate, OrderedDateTimeTransformSID, AdministeredByStaffSID,
  AdministeredByStaffIEN, OrderingProviderSID, OrderingProviderIEN, LocalDrugSID, LocalDrugIEN,
  NationalDrugSID, DrugNameWithoutDose, DrugNameWithDose, OrderNumber, DosageOrdered, DosageGiven,
  Route, RouteIEN, UnitOfAdministration, ScheduleType, Schedule, AdministrationUnit,
  WardLocationSID, WardLocationIEN, WardName, VarianceFlag, VarianceType, VarianceReason,
  VarianceComment, IVFlag, IVType, InfusionRate, TransactionDateTime, TransactionVistaErrorDate,
  TransactionDateTimeTransformSID
)
VALUES
-- Patient 1016: Sertraline BCMA administration
(6031, 'BCMALogIEN6031', 688, 1016, 'PtIEN1016', 1638016, 'PFIEN1016', 'GIVEN', 'COMPLETED', '2025-02-14 14:00:00', NULL, NULL, '2025-02-14 14:00:00', NULL, NULL, '2025-02-14 08:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 10027, 'DrugIEN10027', 20027, 'SERTRALINE HCL', 'SERTRALINE HCL 100MG TAB', 'IP-2024-016001', '100MG', '100MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2004, 'WardIEN2004', 'MENTAL HEALTH WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-14 14:00:00', NULL, NULL),

-- Patient 1018: Metformin, Glipizide BCMA administration (BCMA-only patient)
(6032, 'BCMALogIEN6032', 516, 1018, 'PtIEN1018', 1638018, 'PFIEN1018', 'GIVEN', 'COMPLETED', '2025-01-20 08:00:00', NULL, NULL, '2025-01-20 08:00:00', NULL, NULL, '2025-01-20 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10001, 'DrugIEN10001', 20001, 'METFORMIN HCL', 'METFORMIN HCL 1000MG TAB', 'IP-2024-018001', '1000MG', '1000MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'BID', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-01-20 08:00:00', NULL, NULL),
(6033, 'BCMALogIEN6033', 516, 1018, 'PtIEN1018', 1638018, 'PFIEN1018', 'GIVEN', 'COMPLETED', '2025-03-05 08:00:00', NULL, NULL, '2025-03-05 08:00:00', NULL, NULL, '2025-03-05 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10052, 'DrugIEN10052', 20052, 'GLIPIZIDE', 'GLIPIZIDE 5MG TAB', 'IP-2024-018002', '5MG', '5MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-03-05 08:00:00', NULL, NULL),

-- Patient 1019: Fluoxetine BCMA administration
(6034, 'BCMALogIEN6034', 552, 1019, 'PtIEN1019', 1638019, 'PFIEN1019', 'GIVEN', 'COMPLETED', '2025-02-09 12:00:00', NULL, NULL, '2025-02-09 12:00:00', NULL, NULL, '2025-02-09 08:00:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 10033, 'DrugIEN10033', 20033, 'FLUOXETINE HCL', 'FLUOXETINE HCL 40MG CAP', 'IP-2024-019001', '40MG', '40MG', 'PO', 'RouteIEN01', 'CAP', 'SCHEDULED', 'QD', 'CAP', 2004, 'WardIEN2004', 'MENTAL HEALTH WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-09 12:00:00', NULL, NULL),

-- Patient 1021: Lisinopril BCMA administration
(6035, 'BCMALogIEN6035', 508, 1021, 'PtIEN1021', 1638021, 'PFIEN1021', 'GIVEN', 'COMPLETED', '2025-02-07 14:00:00', NULL, NULL, '2025-02-07 14:00:00', NULL, NULL, '2025-02-07 08:00:00', NULL, NULL, 1001, 'StaffIEN1001', 1001, 'StaffIEN1001', 10002, 'DrugIEN10002', 20002, 'LISINOPRIL', 'LISINOPRIL 20MG TAB', 'IP-2024-021001', '20MG', '20MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2003, 'WardIEN2003', 'CARDIOLOGY WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-07 14:00:00', NULL, NULL),

-- Patient 1022: All meds via BCMA (BCMA-only patient)
(6036, 'BCMALogIEN6036', 516, 1022, 'PtIEN1022', 1638022, 'PFIEN1022', 'GIVEN', 'COMPLETED', '2025-02-12 08:00:00', NULL, NULL, '2025-02-12 08:00:00', NULL, NULL, '2025-02-12 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10017, 'DrugIEN10017', 20017, 'AMLODIPINE BESYLATE', 'AMLODIPINE BESYLATE 10MG TAB', 'IP-2024-022001', '10MG', '10MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-12 08:00:00', NULL, NULL),
(6037, 'BCMALogIEN6037', 516, 1022, 'PtIEN1022', 1638022, 'PFIEN1022', 'GIVEN', 'COMPLETED', '2025-02-12 08:15:00', NULL, NULL, '2025-02-12 08:15:00', NULL, NULL, '2025-02-12 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10002, 'DrugIEN10002', 20002, 'LISINOPRIL', 'LISINOPRIL 10MG TAB', 'IP-2024-022002', '10MG', '10MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-12 08:15:00', NULL, NULL),
(6038, 'BCMALogIEN6038', 516, 1022, 'PtIEN1022', 1638022, 'PFIEN1022', 'GIVEN', 'COMPLETED', '2025-02-12 08:30:00', NULL, NULL, '2025-02-12 08:30:00', NULL, NULL, '2025-02-12 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10016, 'DrugIEN10016', 20016, 'GABAPENTIN', 'GABAPENTIN 300MG CAP', 'IP-2024-022003', '300MG', '300MG', 'PO', 'RouteIEN01', 'CAP', 'SCHEDULED', 'TID', 'CAP', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-12 08:30:00', NULL, NULL),
(6039, 'BCMALogIEN6039', 516, 1022, 'PtIEN1022', 1638022, 'PFIEN1022', 'GIVEN', 'COMPLETED', '2025-03-13 08:00:00', NULL, NULL, '2025-03-13 08:00:00', NULL, NULL, '2025-03-13 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10053, 'DrugIEN10053', 20053, 'MELOXICAM', 'MELOXICAM 15MG TAB', 'IP-2024-022004', '15MG', '15MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'QD', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-03-13 08:00:00', NULL, NULL),
(6040, 'BCMALogIEN6040', 516, 1022, 'PtIEN1022', 1638022, 'PFIEN1022', 'GIVEN', 'COMPLETED', '2025-04-12 08:00:00', NULL, NULL, '2025-04-12 08:00:00', NULL, NULL, '2025-04-12 07:00:00', NULL, NULL, 1003, 'StaffIEN1003', 1003, 'StaffIEN1003', 10054, 'DrugIEN10054', 20054, 'OXYCODONE HCL', 'OXYCODONE HCL 5MG TAB', 'IP-2024-022005', '5MG', '5MG', 'PO', 'RouteIEN01', 'TAB', 'PRN', 'PRN', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-04-12 08:00:00', NULL, NULL),

-- Patient 1023: Metformin BCMA administration
(6041, 'BCMALogIEN6041', 552, 1023, 'PtIEN1023', 1638023, 'PFIEN1023', 'GIVEN', 'COMPLETED', '2025-02-04 13:00:00', NULL, NULL, '2025-02-04 13:00:00', NULL, NULL, '2025-02-04 08:00:00', NULL, NULL, 1004, 'StaffIEN1004', 1004, 'StaffIEN1004', 10001, 'DrugIEN10001', 20001, 'METFORMIN HCL', 'METFORMIN HCL 850MG TAB', 'IP-2024-023001', '850MG', '850MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'BID', 'TAB', 2002, 'WardIEN2002', 'MEDICAL WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-04 13:00:00', NULL, NULL),

-- Patient 1024: Metoprolol BCMA administration
(6042, 'BCMALogIEN6042', 688, 1024, 'PtIEN1024', 1638024, 'PFIEN1024', 'GIVEN', 'COMPLETED', '2025-02-11 14:00:00', NULL, NULL, '2025-02-11 14:00:00', NULL, NULL, '2025-02-11 08:00:00', NULL, NULL, 1005, 'StaffIEN1005', 1005, 'StaffIEN1005', 10011, 'DrugIEN10011', 20011, 'METOPROLOL TARTRATE', 'METOPROLOL TARTRATE 50MG TAB', 'IP-2024-024001', '50MG', '50MG', 'PO', 'RouteIEN01', 'TAB', 'SCHEDULED', 'BID', 'TAB', 2003, 'WardIEN2003', 'CARDIOLOGY WARD', 'N', NULL, NULL, NULL, 'N', NULL, NULL, '2025-02-11 14:00:00', NULL, NULL);
GO

PRINT '  ✓ Added 12 BCMA medication administration records';
PRINT '    - Patient 1016: 1 BCMA record (RxOut+BCMA)';
PRINT '    - Patient 1018: 2 BCMA records (BCMA-only)';
PRINT '    - Patient 1019: 1 BCMA record (RxOut+BCMA)';
PRINT '    - Patient 1021: 1 BCMA record (RxOut+BCMA)';
PRINT '    - Patient 1022: 5 BCMA records (BCMA-only)';
PRINT '    - Patient 1023: 1 BCMA record (RxOut+BCMA)';
PRINT '    - Patient 1024: 1 BCMA record (RxOut+BCMA)';
GO

/*
|--------------------------------------------------------------------------------
| VERIFICATION AND SUMMARY
|--------------------------------------------------------------------------------
*/

PRINT '';
PRINT '==== VERIFICATION SUMMARY ====';
GO

-- Verify patient counts
SELECT 'Total Patients' AS CheckType, COUNT(*) AS ActualCount, 25 AS ExpectedCount
FROM SPatient.SPatient
WHERE PatientSID BETWEEN 1001 AND 1025
UNION ALL
SELECT 'Expansion Patients', COUNT(*), 10
FROM SPatient.SPatient
WHERE PatientSID BETWEEN 1016 AND 1025;
GO

PRINT '';
PRINT '================================================';
PRINT '=== EXPANSION COMPLETE ===';
PRINT '================================================';
PRINT 'Total CDWWork patients: 25 (10 base + 5 elderly + 10 expansion)';
PRINT 'Ready for Phase 2: PhysioNet MIMIC-IV integration';
PRINT '================================================';
GO
