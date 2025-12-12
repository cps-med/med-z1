-- =============================================
-- Insert Data: Allergy.PatientAllergyReaction
-- Description: Bridge table linking allergies to reactions (1-3 reactions per allergy)
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Allergy.PatientAllergyReaction ON;
GO

-- Insert patient allergy reaction mappings
-- Each allergy (PatientAllergySID) can have multiple reactions (ReactionSID)
INSERT INTO Allergy.PatientAllergyReaction (PatientAllergyReactionSID, PatientAllergySID, ReactionSID)
VALUES
    -- Allergy 1: PENICILLIN (Patient 1001) - Hives, Itching
    (1, 1, 1),   -- HIVES
    (2, 1, 3),   -- ITCHING

    -- Allergy 2: SHELLFISH (Patient 1001) - Nausea, Vomiting, Hives
    (3, 2, 20),  -- NAUSEA
    (4, 2, 21),  -- VOMITING
    (5, 2, 1),   -- HIVES

    -- Allergy 3: LATEX (Patient 1001) - Rash, Swelling
    (6, 3, 2),   -- RASH
    (7, 3, 4),   -- SWELLING

    -- Allergy 4: SULFA (Patient 1002) - Rash, Fever, Blisters (Stevens-Johnson)
    (8, 4, 2),   -- RASH
    (9, 4, 50),  -- FEVER
    (10, 4, 7),  -- BLISTERS

    -- Allergy 5: CODEINE (Patient 1002) - Nausea, Vomiting
    (11, 5, 20), -- NAUSEA
    (12, 5, 21), -- VOMITING

    -- Allergy 6: ASPIRIN (Patient 1002) - Abdominal Pain
    (13, 6, 23), -- ABDOMINAL PAIN

    -- Allergy 7: PEANUTS (Patient 1002) - Throat Tightness, Difficulty Swallowing (similar to Difficulty Breathing)
    (14, 7, 14), -- THROAT TIGHTNESS
    (15, 7, 12), -- DIFFICULTY BREATHING

    -- Allergy 8: POLLEN (Patient 1002) - Sneezing, Nasal Congestion, Watery Eyes
    (16, 8, 18), -- SNEEZING
    (17, 8, 16), -- NASAL CONGESTION
    (18, 8, 56), -- WATERY EYES

    -- Allergy 9: AMOXICILLIN (Patient 1003) - Rash, Hives
    (19, 9, 2),  -- RASH
    (20, 9, 1),  -- HIVES

    -- Allergy 10: MORPHINE (Patient 1003) - Hypotension, Difficulty Breathing (respiratory depression)
    (21, 10, 32), -- HYPOTENSION
    (22, 10, 12), -- DIFFICULTY BREATHING

    -- Allergy 11: IBUPROFEN (Patient 1004) - Swelling, Hives
    (23, 11, 4),  -- SWELLING
    (24, 11, 1),  -- HIVES

    -- Allergy 12: IODINE CONTRAST (Patient 1004) - Anaphylaxis, Hypotension, Wheezing
    (25, 12, 30), -- ANAPHYLAXIS
    (26, 12, 32), -- HYPOTENSION
    (27, 12, 10), -- WHEEZING

    -- Allergy 13: EGGS (Patient 1004) - Nausea, Abdominal Pain
    (28, 13, 20), -- NAUSEA
    (29, 13, 23), -- ABDOMINAL PAIN

    -- Allergy 14: TREE NUTS (Patient 1004) - Itching, Throat Tightness
    (30, 14, 3),  -- ITCHING
    (31, 14, 14), -- THROAT TIGHTNESS

    -- Allergy 15: CEPHALEXIN (Patient 1005) - Diarrhea, Cramping
    (32, 15, 22), -- DIARRHEA
    (33, 15, 24), -- CRAMPING

    -- Allergy 16: TETRACYCLINE (Patient 1005) - Rash, Redness (photosensitivity)
    (34, 16, 2),  -- RASH
    (35, 16, 5),  -- REDNESS

    -- Allergy 17: ERYTHROMYCIN (Patient 1005) - Nausea, Abdominal Pain
    (36, 17, 20), -- NAUSEA
    (37, 17, 23), -- ABDOMINAL PAIN

    -- Allergy 18: FISH (Patient 1005) - Hives, Swelling
    (38, 18, 1),  -- HIVES
    (39, 18, 4),  -- SWELLING

    -- Allergy 19: MILK (Patient 1005) - Bloating, Diarrhea
    (40, 19, 25), -- BLOATING
    (41, 19, 22), -- DIARRHEA

    -- Allergy 20: DUST MITES (Patient 1005) - Sneezing, Nasal Congestion, Runny Nose
    (42, 20, 18), -- SNEEZING
    (43, 20, 16), -- NASAL CONGESTION
    (44, 20, 17), -- RUNNY NOSE

    -- Allergy 21: PENICILLIN G (Patient 1007) - Anaphylaxis, Wheezing, Swelling
    (45, 21, 30), -- ANAPHYLAXIS
    (46, 21, 10), -- WHEEZING
    (47, 21, 31), -- ANGIOEDEMA

    -- Allergy 22: SULFASALAZINE (Patient 1007) - Fever, Abdominal Pain (hepatitis symptoms)
    (48, 22, 50), -- FEVER
    (49, 22, 23), -- ABDOMINAL PAIN

    -- Allergy 23: LISINOPRIL (Patient 1007) - Cough
    (50, 23, 13), -- COUGH

    -- Allergy 24: SHELLFISH (Patient 1007) - Hives, Swelling
    (51, 24, 1),  -- HIVES
    (52, 24, 4),  -- SWELLING

    -- Allergy 25: SOY (Patient 1007) - Abdominal Pain, Nausea
    (53, 25, 23), -- ABDOMINAL PAIN
    (54, 25, 20), -- NAUSEA

    -- Allergy 26: MOLD (Patient 1007) - Sneezing, Cough
    (55, 26, 18), -- SNEEZING
    (56, 26, 13), -- COUGH

    -- Allergy 27: BEE STINGS (Patient 1007) - Anaphylaxis, Hives, Wheezing
    (57, 27, 30), -- ANAPHYLAXIS
    (58, 27, 1),  -- HIVES
    (59, 27, 10), -- WHEEZING

    -- Allergy 28: CODEINE (Patient 1008) - Nausea, Vomiting, Dizziness
    (60, 28, 20), -- NAUSEA
    (61, 28, 21), -- VOMITING
    (62, 28, 41), -- DIZZINESS

    -- Allergy 29: TRAMADOL (Patient 1008) - Itching, Confusion (agitation)
    (63, 29, 3),  -- ITCHING
    (64, 29, 42), -- CONFUSION

    -- Allergy 30: PEANUTS (Patient 1008) - Anaphylaxis, Throat Tightness
    (65, 30, 30), -- ANAPHYLAXIS
    (66, 30, 14), -- THROAT TIGHTNESS

    -- Allergy 31: ASPIRIN (Patient 1009) - Abdominal Pain (GI bleeding)
    (67, 31, 23), -- ABDOMINAL PAIN

    -- Allergy 32: SIMVASTATIN (Patient 1009) - Muscle Aches (rhabdomyolysis)
    (68, 32, 54), -- MUSCLE ACHES

    -- Allergy 33: EGGS (Patient 1009) - Hives
    (69, 33, 1),  -- HIVES

    -- Allergy 34: WHEAT (Patient 1009) - Bloating, Diarrhea
    (70, 34, 25), -- BLOATING
    (71, 34, 22), -- DIARRHEA

    -- Allergy 35: MORPHINE (Patient 1010) - Hypotension, Difficulty Breathing
    (72, 35, 32), -- HYPOTENSION
    (73, 35, 12), -- DIFFICULTY BREATHING

    -- Allergy 36: HYDROCODONE (Patient 1010) - Nausea, Vomiting
    (74, 36, 20), -- NAUSEA
    (75, 36, 21), -- VOMITING

    -- Allergy 37: AMOXICILLIN-CLAVULANATE (Patient 1011) - Diarrhea, Abdominal Pain
    (76, 37, 22), -- DIARRHEA
    (77, 37, 23), -- ABDOMINAL PAIN

    -- Allergy 38: LATEX (Patient 1011) - Rash, Hives
    (78, 38, 2),  -- RASH
    (79, 38, 1),  -- HIVES

    -- Allergy 39: SHELLFISH (Patient 1011) - Swelling, Throat Tightness
    (80, 39, 4),  -- SWELLING
    (81, 39, 14), -- THROAT TIGHTNESS

    -- Allergy 40: TREE NUTS (Patient 1011) - Itching
    (82, 40, 3),  -- ITCHING

    -- Allergy 41: PET DANDER (Patient 1011) - Sneezing, Watery Eyes, Runny Nose
    (83, 41, 18), -- SNEEZING
    (84, 41, 56), -- WATERY EYES
    (85, 41, 17), -- RUNNY NOSE

    -- Allergy 42-49: Patient 1013 (8 allergies)
    (86, 42, 1),  -- PENICILLIN: HIVES
    (87, 42, 3),  -- ITCHING
    (88, 43, 2),  -- SULFA: RASH
    (89, 43, 50), -- FEVER
    (90, 44, 23), -- IBUPROFEN: ABDOMINAL PAIN
    (91, 45, 30), -- CONTRAST: ANAPHYLAXIS
    (92, 45, 10), -- WHEEZING
    (93, 45, 32), -- HYPOTENSION
    (94, 46, 14), -- PEANUTS: THROAT TIGHTNESS
    (95, 46, 4),  -- SWELLING
    (96, 47, 1),  -- SHELLFISH: HIVES
    (97, 47, 20), -- NAUSEA
    (98, 48, 20), -- EGGS: NAUSEA
    (99, 49, 18), -- POLLEN: SNEEZING
    (100, 49, 16), -- NASAL CONGESTION

    -- Allergy 50-52: Patient 1014 (3 allergies)
    (101, 50, 4),  -- LISINOPRIL: SWELLING (angioedema)
    (102, 51, 22), -- METFORMIN: DIARRHEA
    (103, 52, 4),  -- INSECT BITES: SWELLING
    (104, 52, 5),  -- REDNESS

    -- Allergy 53-58: Patient 1015 (6 allergies)
    (105, 53, 2),  -- PENICILLIN: RASH
    (106, 53, 1),  -- HIVES
    (107, 54, 20), -- CODEINE: NAUSEA
    (108, 54, 21), -- VOMITING
    (109, 55, 23), -- ASPIRIN: ABDOMINAL PAIN
    (110, 56, 1),  -- FISH: HIVES
    (111, 56, 4),  -- SWELLING
    (112, 57, 25), -- MILK: BLOATING
    (113, 57, 22), -- DIARRHEA
    (114, 58, 3),  -- SESAME: ITCHING

    -- Allergy 59: Patient 1016 (1 allergy)
    (115, 59, 2),  -- PENICILLIN: RASH

    -- Allergy 60-63: Patient 1017 (4 allergies)
    (116, 60, 22), -- CEPHALEXIN: DIARRHEA
    (117, 61, 32), -- MORPHINE: HYPOTENSION
    (118, 61, 12), -- DIFFICULTY BREATHING
    (119, 62, 14), -- PEANUTS: THROAT TIGHTNESS
    (120, 63, 18), -- DUST MITES: SNEEZING
    (121, 63, 16), -- NASAL CONGESTION

    -- Allergy 64-68: Patient 1019 (5 allergies)
    (122, 64, 1),  -- AMOXICILLIN: HIVES
    (123, 65, 23), -- NAPROXEN: ABDOMINAL PAIN (GI bleeding)
    (124, 66, 3),  -- TRAMADOL: ITCHING
    (125, 67, 1),  -- SHELLFISH: HIVES
    (126, 68, 25), -- WHEAT: BLOATING

    -- Allergy 69-71: Patient 1020 (3 allergies)
    (127, 69, 2),  -- BACTRIM: RASH
    (128, 69, 50), -- FEVER
    (129, 69, 7),  -- BLISTERS
    (130, 70, 2),  -- LATEX: RASH
    (131, 71, 4),  -- TREE NUTS: SWELLING
    (132, 71, 3),  -- ITCHING

    -- Allergy 72-78: Patient 1022 (7 allergies)
    (133, 72, 1),  -- PENICILLIN: HIVES
    (134, 72, 3),  -- ITCHING
    (135, 73, 20), -- CODEINE: NAUSEA
    (136, 74, 2),  -- TETRACYCLINE: RASH (photosensitivity)
    (137, 74, 5),  -- REDNESS
    (138, 75, 30), -- PEANUTS: ANAPHYLAXIS
    (139, 76, 4),  -- SHELLFISH: SWELLING
    (140, 77, 25), -- MILK: BLOATING
    (141, 78, 18), -- PET DANDER: SNEEZING
    (142, 78, 56), -- WATERY EYES

    -- Allergy 79-80: Patient 1023 (2 allergies)
    (143, 79, 23), -- ASPIRIN: ABDOMINAL PAIN
    (144, 80, 54), -- ATORVASTATIN: MUSCLE ACHES

    -- Allergy 81-84: Patient 1024 (4 allergies)
    (145, 81, 2),  -- PENICILLIN: RASH
    (146, 82, 30), -- CONTRAST: ANAPHYLAXIS
    (147, 82, 10), -- WHEEZING
    (148, 83, 1),  -- FISH: HIVES
    (149, 84, 18), -- POLLEN: SNEEZING
    (150, 84, 17), -- RUNNY NOSE

    -- Allergy 85-87: Patient 1026 (3 allergies)
    (151, 85, 22), -- CEPHALOSPORINS: DIARRHEA
    (152, 86, 20), -- HYDROCODONE: NAUSEA
    (153, 87, 1),  -- EGGS: HIVES

    -- Allergy 88-92: Patient 1027 (5 allergies)
    (154, 88, 30), -- PENICILLIN: ANAPHYLAXIS
    (155, 88, 10), -- WHEEZING
    (156, 89, 32), -- MORPHINE: HYPOTENSION
    (157, 89, 12), -- DIFFICULTY BREATHING
    (158, 90, 14), -- PEANUTS: THROAT TIGHTNESS
    (159, 91, 4),  -- TREE NUTS: SWELLING
    (160, 92, 30), -- BEE STINGS: ANAPHYLAXIS
    (161, 92, 1),  -- HIVES

    -- Allergy 93: Patient 1028 (1 allergy)
    (162, 93, 23), -- IBUPROFEN: ABDOMINAL PAIN

    -- Allergy 94-99: Patient 1029 (6 allergies)
    (163, 94, 2),  -- AMOXICILLIN: RASH
    (164, 95, 2),  -- SULFA: RASH
    (165, 96, 20), -- ERYTHROMYCIN: NAUSEA
    (166, 97, 1),  -- SHELLFISH: HIVES
    (167, 98, 23), -- SOY: ABDOMINAL PAIN
    (168, 99, 18), -- MOLD: SNEEZING
    (169, 99, 13), -- COUGH

    -- Allergy 100-103: Patient 1031 (4 allergies)
    (170, 100, 20), -- CODEINE: NAUSEA
    (171, 101, 13), -- ACE INHIBITORS: COUGH
    (172, 102, 3),  -- TREE NUTS: ITCHING
    (173, 103, 25), -- WHEAT: BLOATING

    -- Allergy 104-105: Patient 1032 (2 allergies)
    (174, 104, 2),  -- LATEX: RASH
    (175, 105, 22), -- MILK: DIARRHEA

    -- Allergy 106-108: Patient 1033 (3 allergies)
    (176, 106, 1),  -- PENICILLIN: HIVES
    (177, 107, 3),  -- TRAMADOL: ITCHING
    (178, 108, 4),  -- FISH: SWELLING

    -- Allergy 109-113: Patient 1035 (5 allergies)
    (179, 109, 22), -- CEFTRIAXONE: DIARRHEA
    (180, 110, 23), -- ASPIRIN: ABDOMINAL PAIN
    (181, 111, 41), -- GABAPENTIN: DIZZINESS
    (182, 111, 43), -- DROWSINESS
    (183, 112, 20), -- EGGS: NAUSEA
    (184, 113, 18), -- DUST MITES: SNEEZING
    (185, 113, 16), -- NASAL CONGESTION

    -- Allergy 114-115: Patient 1036 (2 allergies)
    (186, 114, 2),  -- DOXYCYCLINE: RASH
    (187, 114, 5),  -- REDNESS
    (188, 115, 18), -- POLLEN: SNEEZING
    (189, 115, 56); -- WATERY EYES
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Allergy.PatientAllergyReaction OFF;
GO

PRINT '189 patient allergy reaction records inserted successfully';
PRINT 'Average reactions per allergy: ~1.6 reactions';
GO
