/*
|--------------------------------------------------------------------------------
| Insert: RxOut.RxOutpatMedInstructions.sql
|--------------------------------------------------------------------------------
| Insert additional patient instruction and provider comment data
| RxOutpatMedInstructionsSID => 8001 series
| Instructions linked to prescriptions and fills
| Contains free-text patient instructions, warnings, and provider comments
|--------------------------------------------------------------------------------
*/

PRINT '==== RxOut.RxOutpatMedInstructions ====';
GO

-- Set the active database
USE CDWWork;
GO

-- Insert instruction data into RxOut.RxOutpatMedInstructions table
INSERT INTO RxOut.RxOutpatMedInstructions
(
  RxOutpatMedInstructionsSID, RxOutpatMedInstructionsIEN, RxOutpatSID, RxOutpatFillSID, Sta3n, PatientSID, PatientIEN, InstructionType, InstructionSequence, InstructionText, SourceType, EnteredByStaffSID, EnteredByStaffIEN, EnteredDateTime, EnteredVistaErrorDate, EnteredDateTimeTransformSID, LocalDrugSID, NationalDrugSID
)
VALUES
-- RxOutpatSID 5001: METFORMIN - Multiple instructions
(8001, 'InstrIEN8001', 5001, 6001, 508, 1001, 'PtIEN1001', 'PATIENT', 1, 'Take with food to reduce stomach upset.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-15 10:30:00', NULL, NULL, 10001, 20001),
(8002, 'InstrIEN8002', 5001, 6001, 508, 1001, 'PtIEN1001', 'PATIENT', 2, 'May cause diarrhea. Contact provider if symptoms persist.', 'USER_ENTERED', 1001, 'StaffIEN1001', '2024-01-15 10:30:00', NULL, NULL, 10001, 20001),
(8003, 'InstrIEN8003', 5001, 6001, 508, 1001, 'PtIEN1001', 'WARNING', 3, 'Do not drink alcohol while taking this medication.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-15 10:30:00', NULL, NULL, 10001, 20001),

-- RxOutpatSID 5002: LISINOPRIL
(8004, 'InstrIEN8004', 5002, 6004, 508, 1001, 'PtIEN1001', 'PATIENT', 1, 'May cause dizziness. Use caution when standing up quickly.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-15 10:35:00', NULL, NULL, 10002, 20002),
(8005, 'InstrIEN8005', 5002, 6004, 508, 1001, 'PtIEN1001', 'WARNING', 2, 'Avoid salt substitutes containing potassium.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-15 10:35:00', NULL, NULL, 10002, 20002),
(8006, 'InstrIEN8006', 5002, 6004, 508, 1001, 'PtIEN1001', 'PROVIDER', 3, 'Monitor blood pressure weekly and report to clinic.', 'USER_ENTERED', 1001, 'StaffIEN1001', '2024-01-15 10:35:00', NULL, NULL, 10002, 20002),

-- RxOutpatSID 5003: ATORVASTATIN
(8007, 'InstrIEN8007', 5003, 6006, 508, 1001, 'PtIEN1001', 'PATIENT', 1, 'Take at bedtime for best effect.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-20 14:15:00', NULL, NULL, 10003, 20003),
(8008, 'InstrIEN8008', 5003, 6006, 508, 1001, 'PtIEN1001', 'WARNING', 2, 'Avoid grapefruit juice while taking this medication.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-20 14:15:00', NULL, NULL, 10003, 20003),
(8009, 'InstrIEN8009', 5003, 6006, 508, 1001, 'PtIEN1001', 'PATIENT', 3, 'Report any unexplained muscle pain, tenderness, or weakness.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-20 14:15:00', NULL, NULL, 10003, 20003),

-- RxOutpatSID 5004: ALBUTEROL
(8010, 'InstrIEN8010', 5004, 6007, 508, 1002, 'PtIEN1002', 'PATIENT', 1, 'Shake inhaler well before each use.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-01-22 09:15:00', NULL, NULL, 10004, 20004),
(8011, 'InstrIEN8011', 5004, 6007, 508, 1002, 'PtIEN1002', 'PATIENT', 2, 'Rinse mouth after use to prevent dry mouth.', 'USER_ENTERED', 1002, 'StaffIEN1002', '2024-01-22 09:15:00', NULL, NULL, 10004, 20004),
(8012, 'InstrIEN8012', 5004, 6007, 508, 1002, 'PtIEN1002', 'PROVIDER', 3, 'If using more than 2-3 times per week, contact pulmonary clinic.', 'USER_ENTERED', 1002, 'StaffIEN1002', '2024-01-22 09:15:00', NULL, NULL, 10004, 20004),

-- RxOutpatSID 5005: TRAMADOL
(8013, 'InstrIEN8013', 5005, 6011, 508, 1002, 'PtIEN1002', 'PATIENT', 1, 'May cause drowsiness. Do not drive or operate machinery until you know how this medication affects you.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-03-10 11:45:00', NULL, NULL, 10005, 20005),
(8014, 'InstrIEN8014', 5005, 6011, 508, 1002, 'PtIEN1002', 'WARNING', 2, 'Do not drink alcohol while taking this medication.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-03-10 11:45:00', NULL, NULL, 10005, 20005),
(8015, 'InstrIEN8015', 5005, 6011, 508, 1002, 'PtIEN1002', 'WARNING', 3, 'May be habit forming. Take only as prescribed.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-03-10 11:45:00', NULL, NULL, 10005, 20005),

-- RxOutpatSID 5006: SERTRALINE
(8016, 'InstrIEN8016', 5006, 6013, 508, 1003, 'PtIEN1003', 'PATIENT', 1, 'May take 4-6 weeks to see full benefit. Continue taking as directed.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-05 13:20:00', NULL, NULL, 10006, 20006),
(8017, 'InstrIEN8017', 5006, 6013, 508, 1003, 'PtIEN1003', 'WARNING', 2, 'Do not stop taking suddenly. Contact provider before discontinuing.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-05 13:20:00', NULL, NULL, 10006, 20006),
(8018, 'InstrIEN8018', 5006, 6013, 508, 1003, 'PtIEN1003', 'PROVIDER', 3, 'Follow up in mental health clinic in 4 weeks.', 'USER_ENTERED', 1001, 'StaffIEN1001', '2024-02-05 13:20:00', NULL, NULL, 10006, 20006),

-- RxOutpatSID 5007: ALPRAZOLAM (Discontinued)
(8019, 'InstrIEN8019', 5007, 6014, 508, 1003, 'PtIEN1003', 'WARNING', 1, 'May cause drowsiness. Do not drive or operate machinery.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-05 13:25:00', NULL, NULL, 10007, 20007),
(8020, 'InstrIEN8020', 5007, 6014, 508, 1003, 'PtIEN1003', 'WARNING', 2, 'Do not drink alcohol while taking this medication.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-02-05 13:25:00', NULL, NULL, 10007, 20007),
(8021, 'InstrIEN8021', 5007, 6014, 508, 1003, 'PtIEN1003', 'PROVIDER', 3, 'Transitioning to buspirone - follow taper schedule provided.', 'USER_ENTERED', 1001, 'StaffIEN1001', '2024-06-15 00:00:00', NULL, NULL, 10007, 20007),

-- RxOutpatSID 5008: AMOXICILLIN
(8022, 'InstrIEN8022', 5008, 6015, 508, 1004, 'PtIEN1004', 'PATIENT', 1, 'Take until all medication is gone, even if you feel better.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-03-12 15:30:00', NULL, NULL, 10008, 20008),
(8023, 'InstrIEN8023', 5008, 6015, 508, 1004, 'PtIEN1004', 'PATIENT', 2, 'May be taken with or without food.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-03-12 15:30:00', NULL, NULL, 10008, 20008),

-- RxOutpatSID 5009: LEVOTHYROXINE
(8024, 'InstrIEN8024', 5009, 6016, 508, 1004, 'PtIEN1004', 'PATIENT', 1, 'Take on empty stomach, 30-60 minutes before breakfast.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-01-18 10:00:00', NULL, NULL, 10009, 20009),
(8025, 'InstrIEN8025', 5009, 6016, 508, 1004, 'PtIEN1004', 'PATIENT', 2, 'Wait at least 4 hours before taking calcium or iron supplements.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-01-18 10:00:00', NULL, NULL, 10009, 20009),
(8026, 'InstrIEN8026', 5009, 6016, 508, 1004, 'PtIEN1004', 'PROVIDER', 3, 'Recheck TSH in 6 weeks.', 'USER_ENTERED', 1002, 'StaffIEN1002', '2024-01-18 10:00:00', NULL, NULL, 10009, 20009),

-- RxOutpatSID 5010: WARFARIN
(8027, 'InstrIEN8027', 5010, 6018, 508, 1005, 'PtIEN1005', 'PATIENT', 1, 'Take at the same time every day.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-25 09:30:00', NULL, NULL, 10010, 20010),
(8028, 'InstrIEN8028', 5010, 6018, 508, 1005, 'PtIEN1005', 'WARNING', 2, 'Avoid large changes in diet, especially foods high in vitamin K.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-25 09:30:00', NULL, NULL, 10010, 20010),
(8029, 'InstrIEN8029', 5010, 6018, 508, 1005, 'PtIEN1005', 'PROVIDER', 3, 'INR monitoring required weekly. Schedule with anticoagulation clinic.', 'USER_ENTERED', 1001, 'StaffIEN1001', '2024-01-25 09:30:00', NULL, NULL, 10010, 20010),
(8030, 'InstrIEN8030', 5010, 6018, 508, 1005, 'PtIEN1005', 'WARNING', 4, 'Report any unusual bleeding or bruising immediately.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-25 09:30:00', NULL, NULL, 10010, 20010),

-- RxOutpatSID 5011: METOPROLOL
(8031, 'InstrIEN8031', 5011, 6019, 508, 1005, 'PtIEN1005', 'PATIENT', 1, 'Do not stop taking suddenly. Contact provider before discontinuing.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-25 09:35:00', NULL, NULL, 10011, 20011),
(8032, 'InstrIEN8032', 5011, 6019, 508, 1005, 'PtIEN1005', 'PATIENT', 2, 'May cause dizziness. Rise slowly from sitting or lying position.', 'ORDERABLE_ITEM', 1001, 'StaffIEN1001', '2024-01-25 09:35:00', NULL, NULL, 10011, 20011),

-- RxOutpatSID 5012: HYDROCODONE-ACETAMINOPHEN
(8033, 'InstrIEN8033', 5012, 6020, 508, 1006, 'PtIEN1006', 'WARNING', 1, 'May cause drowsiness. Do not drive or operate machinery.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-04-10 14:20:00', NULL, NULL, 10012, 20012),
(8034, 'InstrIEN8034', 5012, 6020, 508, 1006, 'PtIEN1006', 'WARNING', 2, 'Do not drink alcohol or take other sedating medications.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-04-10 14:20:00', NULL, NULL, 10012, 20012),
(8035, 'InstrIEN8035', 5012, 6020, 508, 1006, 'PtIEN1006', 'WARNING', 3, 'May cause constipation. Increase water and fiber intake.', 'ORDERABLE_ITEM', 1002, 'StaffIEN1002', '2024-04-10 14:20:00', NULL, NULL, 10012, 20012),
(8036, 'InstrIEN8036', 5012, 6020, 508, 1006, 'PtIEN1006', 'PROVIDER', 4, 'For post-operative pain only. Follow up in 10 days.', 'USER_ENTERED', 1002, 'StaffIEN1002', '2024-04-10 14:20:00', NULL, NULL, 10012, 20012),

-- RxOutpatSID 5014: OMEPRAZOLE (Sta3n 516)
(8037, 'InstrIEN8037', 5014, 6022, 516, 1007, 'PtIEN1007', 'PATIENT', 1, 'Take before first meal of the day for best results.', 'ORDERABLE_ITEM', 1003, 'StaffIEN1003', '2024-02-08 11:15:00', NULL, NULL, 10014, 20014),
(8038, 'InstrIEN8038', 5014, 6022, 516, 1007, 'PtIEN1007', 'PATIENT', 2, 'Swallow capsule whole. Do not crush or chew.', 'ORDERABLE_ITEM', 1003, 'StaffIEN1003', '2024-02-08 11:15:00', NULL, NULL, 10014, 20014),

-- RxOutpatSID 5016: GABAPENTIN (Sta3n 516)
(8039, 'InstrIEN8039', 5016, 6025, 516, 1008, 'PtIEN1008', 'PATIENT', 1, 'May cause dizziness or drowsiness. Use caution with activities requiring alertness.', 'ORDERABLE_ITEM', 1004, 'StaffIEN1004', '2024-03-15 10:45:00', NULL, NULL, 10016, 20016),
(8040, 'InstrIEN8040', 5016, 6025, 516, 1008, 'PtIEN1008', 'PATIENT', 2, 'Do not stop taking suddenly. Contact provider before discontinuing.', 'ORDERABLE_ITEM', 1004, 'StaffIEN1004', '2024-03-15 10:45:00', NULL, NULL, 10016, 20016),

-- RxOutpatSID 5019: INSULIN (Sta3n 552)
(8041, 'InstrIEN8041', 5019, 6029, 552, 1010, 'PtIEN1010', 'PATIENT', 1, 'Inject subcutaneously in abdomen, thigh, or upper arm. Rotate injection sites.', 'ORDERABLE_ITEM', 1005, 'StaffIEN1005', '2024-02-12 09:00:00', NULL, NULL, 10019, 20019),
(8042, 'InstrIEN8042', 5019, 6029, 552, 1010, 'PtIEN1010', 'PATIENT', 2, 'Store unused vials in refrigerator. In-use vial may be kept at room temperature.', 'ORDERABLE_ITEM', 1005, 'StaffIEN1005', '2024-02-12 09:00:00', NULL, NULL, 10019, 20019),
(8043, 'InstrIEN8043', 5019, 6029, 552, 1010, 'PtIEN1010', 'WARNING', 3, 'Always carry fast-acting sugar in case of low blood sugar.', 'ORDERABLE_ITEM', 1005, 'StaffIEN1005', '2024-02-12 09:00:00', NULL, NULL, 10019, 20019),
(8044, 'InstrIEN8044', 5019, 6029, 552, 1010, 'PtIEN1010', 'PROVIDER', 4, 'Check blood sugar before meals and at bedtime. Log results.', 'USER_ENTERED', 1005, 'StaffIEN1005', '2024-02-12 09:00:00', NULL, NULL, 10019, 20019),

-- RxOutpatSID 5020: METFORMIN 1000MG (Sta3n 552)
(8045, 'InstrIEN8045', 5020, 6031, 552, 1010, 'PtIEN1010', 'PATIENT', 1, 'Take with meals to reduce stomach upset.', 'ORDERABLE_ITEM', 1005, 'StaffIEN1005', '2024-02-12 09:05:00', NULL, NULL, 10020, 20020),
(8046, 'InstrIEN8046', 5020, 6031, 552, 1010, 'PtIEN1010', 'WARNING', 2, 'Do not drink alcohol while taking this medication.', 'ORDERABLE_ITEM', 1005, 'StaffIEN1005', '2024-02-12 09:05:00', NULL, NULL, 10020, 20020);
GO
