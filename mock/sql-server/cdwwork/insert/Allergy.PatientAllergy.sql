-- =============================================
-- Insert Data: Allergy.PatientAllergy
-- Description: Patient allergy records (5-15 allergies per patient, realistic distribution)
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Allergy.PatientAllergy ON;
GO

-- Insert patient allergy data
-- Distribution: 60-70% drug allergies, 20-25% food allergies, 5-15% environmental
-- Severity: 40% MILD, 40% MODERATE, 20% SEVERE
-- HistoricalOrObserved: 70% HISTORICAL, 30% OBSERVED
INSERT INTO Allergy.PatientAllergy (
    PatientAllergySID, PatientSID, AllergenSID, AllergySeveritySID, LocalAllergenName,
    OriginationDateTime, ObservedDateTime, OriginatingSiteSta3n,
    Comment, HistoricalOrObserved, IsActive, VerificationStatus, Sta3n
)
VALUES
    -- Patient 1001 (3 allergies: PENICILLIN, SHELLFISH, LATEX)
    (1, 1001, 1, 2, 'PENICILLIN VK 500MG', '2015-03-12 10:30:00', NULL, 518,
        'Patient reports developing hives and itching within 2 hours of taking penicillin VK 500mg for strep throat in 2015. Rash resolved after stopping medication and taking Benadryl. No respiratory symptoms. Patient instructed to avoid all penicillin antibiotics.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (2, 1001, 22, 3, 'SHELLFISH', '2010-07-22 14:15:00', '2010-07-22 12:00:00', 518,
        'Patient experienced severe reaction to shrimp at family gathering. Symptoms included nausea, vomiting, hives covering torso and arms. Required ER visit and epinephrine administration. Carries EpiPen. Avoids all shellfish.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (3, 1001, 8, 1, 'LATEX GLOVES', '2018-11-05 09:00:00', '2018-11-05 09:00:00', 518,
        'Developed contact dermatitis and mild swelling when wearing latex gloves during dental appointment. Switched to nitrile gloves without issue.',
        'OBSERVED', 1, 'VERIFIED', 518),

    -- Patient 1002 (5 allergies: SULFA, CODEINE, ASPIRIN, PEANUTS, POLLEN)
    (4, 1002, 3, 3, 'SULFAMETHOXAZOLE-TRIMETHOPRIM', '2012-05-18 11:20:00', NULL, 442,
        'Patient developed severe Stevens-Johnson syndrome reaction to Bactrim (sulfamethoxazole-trimethoprim) in 2012. Required hospitalization for extensive blistering rash, fever, and mucosal involvement. Permanent contraindication to all sulfa-containing medications. Patient carries medical alert bracelet.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (5, 1002, 6, 2, 'CODEINE 30MG', '2016-09-10 14:30:00', NULL, 442,
        'Patient reports severe nausea and vomiting when taking codeine for post-surgical pain. Symptoms resolved when switched to non-opioid pain management.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (6, 1002, 4, 1, 'ASPIRIN', '2019-02-14 10:00:00', NULL, 442,
        'Mild gastric upset and heartburn when taking aspirin 325mg daily for cardioprotection. Switched to low-dose aspirin with enteric coating with improvement.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (7, 1002, 20, 2, 'PEANUTS', '2005-11-20 16:45:00', '2005-11-20 15:30:00', 442,
        'Throat tightness and difficulty swallowing after eating peanut butter sandwich. Required treatment with antihistamines in urgent care. Avoids all peanut products.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (8, 1002, 30, 1, 'POLLEN', '2020-04-05 08:00:00', NULL, 442,
        'Seasonal allergic rhinitis with sneezing, nasal congestion, and watery eyes during spring pollen season. Managed with antihistamines.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),

    -- Patient 1003 (2 allergies: PENICILLIN, MORPHINE)
    (9, 1003, 1, 2, 'AMOXICILLIN', '2017-08-15 09:30:00', '2017-08-15 09:00:00', 589,
        'Developed widespread urticarial rash after 3 days of amoxicillin therapy for sinusitis. Rash resolved with antihistamines and cessation of antibiotic. Cross-reactivity concern with all penicillins.',
        'OBSERVED', 1, 'VERIFIED', 589),
    (10, 1003, 7, 3, 'MORPHINE SULFATE', '2014-06-22 13:45:00', '2014-06-22 10:30:00', 589,
        'Severe hypotension and respiratory depression following IV morphine administration post-operatively. Required naloxone reversal and ICU monitoring. Contraindicated for all morphine use.',
        'OBSERVED', 1, 'VERIFIED', 589),

    -- Patient 1004 (4 allergies: NSAIDS, IODINE CONTRAST, EGGS, TREE NUTS)
    (11, 1004, 5, 2, 'IBUPROFEN', '2013-03-10 11:00:00', NULL, 640,
        'Patient reports facial swelling and hives after taking ibuprofen 400mg for headache. Similar reaction with naproxen. Tolerates acetaminophen without issue.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (12, 1004, 9, 3, 'IODINE CONTRAST DYE', '2011-09-28 14:20:00', '2011-09-28 14:00:00', 640,
        'Anaphylactic reaction during CT scan with IV contrast. Experienced severe hypotension, bronchospasm, and angioedema. Required epinephrine, steroids, and ICU admission. Pre-medication protocol required for any future contrast studies.',
        'OBSERVED', 1, 'VERIFIED', 640),
    (13, 1004, 24, 1, 'EGGS', '2008-05-15 07:30:00', NULL, 640,
        'Mild nausea and stomach upset after eating eggs. Tolerates eggs in baked goods. Avoids whole eggs.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),
    (14, 1004, 21, 2, 'TREE NUTS', '2019-12-03 18:00:00', '2019-12-03 17:30:00', 640,
        'Oral itching and throat tightness after eating walnuts in salad. Avoids all tree nuts including almonds, cashews, pecans, walnuts.',
        'OBSERVED', 1, 'VERIFIED', 640),

    -- Patient 1005 (6 allergies: CEPHALOSPORINS, TETRACYCLINE, ERYTHROMYCIN, FISH, MILK, DUST MITES)
    (15, 1005, 2, 2, 'CEPHALEXIN', '2016-04-20 10:15:00', NULL, 518,
        'Severe diarrhea and abdominal cramping after starting cephalexin for skin infection. Symptoms resolved after stopping antibiotic. Concern for cross-reactivity with all cephalosporins.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (16, 1005, 10, 1, 'TETRACYCLINE', '2009-07-12 14:00:00', NULL, 518,
        'Photosensitivity reaction with severe sunburn after minimal sun exposure while taking tetracycline for acne. Rash resolved after discontinuation.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (17, 1005, 11, 1, 'ERYTHROMYCIN', '2012-11-08 09:30:00', NULL, 518,
        'Nausea and stomach upset with erythromycin. Unable to complete course of therapy.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),
    (18, 1005, 23, 2, 'FISH', '2018-03-25 19:00:00', '2018-03-25 18:30:00', 518,
        'Hives and lip swelling after eating salmon. Similar reaction with tuna. Avoids all fish.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (19, 1005, 25, 1, 'MILK', '2015-09-14 08:00:00', NULL, 518,
        'Bloating and diarrhea after drinking milk. Likely lactose intolerance. Uses lactose-free dairy products.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),
    (20, 1005, 31, 1, 'DUST MITES', '2020-01-10 10:00:00', NULL, 518,
        'Year-round allergic rhinitis and sneezing, worse in bedroom. Positive skin testing for dust mite allergy. Uses allergen-proof bedding covers.',
        'HISTORICAL', 1, 'VERIFIED', 518),

    -- Patient 1006 (0 allergies - testing empty state)

    -- Patient 1007 (7 allergies: PENICILLIN, SULFA, LISINOPRIL, SHELLFISH, SOY, MOLD, BEE STINGS)
    (21, 1007, 1, 3, 'PENICILLIN G', '2010-02-18 11:30:00', '2010-02-18 10:00:00', 442,
        'Anaphylaxis with penicillin G injection. Severe bronchospasm, angioedema, hypotension. Required epinephrine and emergency treatment. Carries EpiPen. Avoid all penicillin and cephalosporin antibiotics.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (22, 1007, 3, 2, 'SULFASALAZINE', '2013-06-05 14:00:00', NULL, 442,
        'Developed drug-induced hepatitis with sulfasalazine for inflammatory bowel disease. Elevated liver enzymes, jaundice. Resolved after medication discontinuation.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (23, 1007, 17, 2, 'LISINOPRIL', '2017-09-12 09:00:00', NULL, 442,
        'Persistent dry cough and throat irritation on lisinopril for hypertension. Switched to ARB without issue.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (24, 1007, 22, 2, 'SHELLFISH', '2014-11-20 18:30:00', '2014-11-20 17:45:00', 442,
        'Hives and facial swelling after eating lobster. Required ER visit and treatment with steroids and antihistamines. Avoids all shellfish.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (25, 1007, 26, 1, 'SOY', '2019-05-08 12:00:00', NULL, 442,
        'Mild GI upset with soy milk. Tolerates small amounts in processed foods. Prefers to avoid.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),
    (26, 1007, 32, 1, 'MOLD', '2018-08-22 10:00:00', NULL, 442,
        'Seasonal allergic symptoms worse in damp environments. Positive skin testing for mold allergy.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),
    (27, 1007, 34, 3, 'BEE STINGS', '2011-07-04 15:00:00', '2011-07-04 14:30:00', 442,
        'Severe systemic reaction to bee sting with generalized urticaria, angioedema, and wheezing. Required epinephrine and hospital observation. Carries EpiPen. Completed venom immunotherapy.',
        'OBSERVED', 1, 'VERIFIED', 442),

    -- Patient 1008 (3 allergies: CODEINE, TRAMADOL, PEANUTS)
    (28, 1008, 6, 2, 'CODEINE', '2015-11-18 10:30:00', NULL, 589,
        'Severe nausea, vomiting, and dizziness with codeine for dental pain. Unable to tolerate even small doses.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (29, 1008, 15, 2, 'TRAMADOL', '2018-04-22 14:00:00', NULL, 589,
        'Severe itching and agitation with tramadol. Discontinued after 2 doses.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (30, 1008, 20, 3, 'PEANUTS', '2006-09-15 12:30:00', '2006-09-15 12:00:00', 589,
        'History of anaphylaxis to peanuts as child. Confirmed with skin testing. Strict avoidance. Carries EpiPen.',
        'OBSERVED', 1, 'VERIFIED', 589),

    -- Patient 1009 (4 allergies: ASPIRIN, STATINS, EGGS, WHEAT)
    (31, 1009, 4, 2, 'ASPIRIN', '2016-06-10 09:00:00', NULL, 640,
        'Gastric bleeding and severe heartburn with aspirin therapy. Switched to clopidogrel for antiplatelet therapy.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (32, 1009, 13, 2, 'SIMVASTATIN', '2017-03-15 10:30:00', NULL, 640,
        'Severe muscle aches and weakness (rhabdomyolysis) with simvastatin. CK elevated to 5000. Resolved after stopping medication. Concern for all statins.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (33, 1009, 24, 1, 'EGGS', '2010-05-20 08:00:00', NULL, 640,
        'Mild hives after eating eggs. Tolerates eggs in baked goods.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),
    (34, 1009, 27, 1, 'WHEAT', '2019-08-12 12:00:00', NULL, 640,
        'Bloating and diarrhea after eating wheat products. Possible gluten sensitivity. Follows gluten-free diet.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),

    -- Patient 1010 (2 allergies: MORPHINE, HYDROCODONE)
    (35, 1010, 7, 3, 'MORPHINE', '2013-10-05 11:00:00', '2013-10-05 10:00:00', 518,
        'Severe respiratory depression and hypotension with IV morphine post-operatively. Required naloxone reversal.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (36, 1010, 14, 2, 'HYDROCODONE', '2016-12-08 15:00:00', NULL, 518,
        'Severe nausea and vomiting with hydrocodone. Unable to tolerate for pain management.',
        'HISTORICAL', 1, 'VERIFIED', 518),

    -- Patient 1011 (5 allergies: PENICILLIN, LATEX, SHELLFISH, TREE NUTS, PET DANDER)
    (37, 1011, 1, 2, 'AMOXICILLIN-CLAVULANATE', '2014-09-20 10:00:00', NULL, 442,
        'Severe diarrhea and C. difficile colitis after taking Augmentin for sinus infection. Hospitalized for treatment. Avoids all penicillins.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (38, 1011, 8, 2, 'LATEX', '2017-05-15 14:30:00', '2017-05-15 14:00:00', 442,
        'Contact dermatitis and hives from latex gloves at work. Uses powder-free nitrile gloves. Also reacts to latex balloons.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (39, 1011, 22, 2, 'SHELLFISH', '2012-07-04 19:00:00', '2012-07-04 18:00:00', 442,
        'Lip swelling and throat tightness after eating crab. Treated with antihistamines. Avoids all shellfish.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (40, 1011, 21, 1, 'TREE NUTS', '2018-11-22 12:00:00', NULL, 442,
        'Mild oral itching with almonds and cashews. Avoids tree nuts.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),
    (41, 1011, 33, 1, 'PET DANDER', '2020-02-10 09:00:00', NULL, 442,
        'Allergic rhinitis and watery eyes around cats and dogs. Managed with antihistamines.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),

    -- Patient 1012 (0 allergies - testing empty state)

    -- Patient 1013 (8 allergies - moderate allergy burden)
    (42, 1013, 1, 2, 'PENICILLIN', '2011-04-10 10:00:00', NULL, 589,
        'Hives and itching after penicillin treatment. Confirmed penicillin allergy.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (43, 1013, 3, 2, 'SULFA', '2013-08-15 11:30:00', NULL, 589,
        'Rash and fever with Bactrim. Avoids sulfa medications.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (44, 1013, 5, 1, 'IBUPROFEN', '2016-02-20 09:00:00', NULL, 589,
        'Stomach upset and heartburn with ibuprofen. Uses acetaminophen instead.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (45, 1013, 9, 3, 'CONTRAST DYE', '2015-06-18 14:00:00', '2015-06-18 13:30:00', 589,
        'Severe allergic reaction to IV contrast during CT scan. Bronchospasm and hypotension. Requires pre-medication protocol.',
        'OBSERVED', 1, 'VERIFIED', 589),
    (46, 1013, 20, 2, 'PEANUTS', '2008-09-12 16:00:00', NULL, 589,
        'Throat swelling and difficulty breathing after peanut exposure. Carries EpiPen.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (47, 1013, 22, 2, 'SHELLFISH', '2010-12-25 18:00:00', '2010-12-25 17:00:00', 589,
        'Hives and nausea after eating shrimp. Avoids all shellfish.',
        'OBSERVED', 1, 'VERIFIED', 589),
    (48, 1013, 24, 1, 'EGGS', '2012-03-08 08:00:00', NULL, 589,
        'Mild GI upset with eggs. Avoids whole eggs.',
        'HISTORICAL', 1, 'UNVERIFIED', 589),
    (49, 1013, 30, 1, 'POLLEN', '2019-04-15 10:00:00', NULL, 589,
        'Seasonal allergies with pollen. Managed with antihistamines.',
        'HISTORICAL', 1, 'UNVERIFIED', 589),

    -- Patient 1014 (3 allergies: ACE INHIBITORS, METFORMIN, INSECT BITES)
    (50, 1014, 12, 2, 'LISINOPRIL', '2017-07-10 09:30:00', NULL, 640,
        'Angioedema of lips and tongue with lisinopril. Discontinued immediately. Avoids all ACE inhibitors.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (51, 1014, 18, 1, 'METFORMIN', '2018-09-22 10:00:00', NULL, 640,
        'Severe diarrhea and GI upset with metformin. Unable to tolerate even extended-release formulation.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (52, 1014, 35, 2, 'INSECT BITES', '2016-06-30 15:00:00', '2016-06-30 14:00:00', 640,
        'Large local reaction to mosquito bites with significant swelling and redness. Lasts several days.',
        'OBSERVED', 1, 'UNVERIFIED', 640),

    -- Patient 1015 (6 allergies: PENICILLIN, CODEINE, ASPIRIN, FISH, MILK, SESAME)
    (53, 1015, 1, 2, 'PENICILLIN', '2012-05-15 11:00:00', NULL, 518,
        'Rash and hives with penicillin. Confirmed allergy.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (54, 1015, 6, 2, 'CODEINE', '2014-08-20 14:30:00', NULL, 518,
        'Severe nausea and vomiting with codeine.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (55, 1015, 4, 1, 'ASPIRIN', '2016-11-10 09:00:00', NULL, 518,
        'Gastric upset with aspirin. Switched to enteric-coated formulation.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (56, 1015, 23, 2, 'FISH', '2013-07-22 19:00:00', '2013-07-22 18:30:00', 518,
        'Hives and lip swelling after eating fish. Avoids all fish.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (57, 1015, 25, 1, 'MILK', '2018-03-15 08:00:00', NULL, 518,
        'Lactose intolerance with bloating and diarrhea. Uses lactose-free products.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),
    (58, 1015, 28, 1, 'SESAME', '2019-09-08 12:00:00', NULL, 518,
        'Mild oral itching with tahini. Avoids sesame products.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),

    -- Remaining patients (1016-1036) - varied allergy profiles
    -- Patient 1016 (1 allergy: PENICILLIN only)
    (59, 1016, 1, 1, 'PENICILLIN', '2018-02-10 10:00:00', NULL, 442,
        'Mild rash with penicillin treatment.',
        'HISTORICAL', 1, 'VERIFIED', 442),

    -- Patient 1017 (4 allergies)
    (60, 1017, 2, 2, 'CEPHALEXIN', '2015-09-12 11:00:00', NULL, 589,
        'Severe diarrhea with cephalexin. Avoid cephalosporins.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (61, 1017, 7, 3, 'MORPHINE', '2012-06-18 14:00:00', '2012-06-18 12:00:00', 589,
        'Respiratory depression with morphine. Required naloxone.',
        'OBSERVED', 1, 'VERIFIED', 589),
    (62, 1017, 20, 2, 'PEANUTS', '2010-03-22 16:00:00', NULL, 589,
        'Throat tightness with peanut butter. Avoids peanuts.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (63, 1017, 31, 1, 'DUST MITES', '2019-11-05 09:00:00', NULL, 589,
        'Year-round allergic rhinitis from dust mites.',
        'HISTORICAL', 1, 'UNVERIFIED', 589),

    -- Patient 1018 (0 allergies)

    -- Patient 1019 (5 allergies)
    (64, 1019, 1, 2, 'AMOXICILLIN', '2016-07-20 10:30:00', NULL, 640,
        'Hives with amoxicillin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (65, 1019, 5, 2, 'NAPROXEN', '2017-04-15 09:00:00', NULL, 640,
        'GI bleeding with naproxen.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (66, 1019, 15, 1, 'TRAMADOL', '2018-10-08 14:00:00', NULL, 640,
        'Severe itching with tramadol.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (67, 1019, 22, 2, 'SHELLFISH', '2014-12-20 18:00:00', '2014-12-20 17:00:00', 640,
        'Hives after eating shrimp.',
        'OBSERVED', 1, 'VERIFIED', 640),
    (68, 1019, 27, 1, 'WHEAT', '2020-05-12 12:00:00', NULL, 640,
        'Bloating with wheat. Follows gluten-free diet.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),

    -- Patient 1020 (3 allergies)
    (69, 1020, 3, 3, 'BACTRIM', '2011-08-15 10:00:00', '2011-08-15 09:00:00', 518,
        'Stevens-Johnson syndrome with Bactrim. Severe reaction. Avoid all sulfa drugs.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (70, 1020, 8, 2, 'LATEX', '2015-03-22 14:00:00', '2015-03-22 13:30:00', 518,
        'Contact dermatitis from latex gloves.',
        'OBSERVED', 1, 'VERIFIED', 518),
    (71, 1020, 21, 2, 'TREE NUTS', '2017-11-10 12:00:00', NULL, 518,
        'Oral swelling with almonds. Avoids all tree nuts.',
        'HISTORICAL', 1, 'VERIFIED', 518),

    -- Patient 1021 (0 allergies)

    -- Patient 1022 (7 allergies)
    (72, 1022, 1, 2, 'PENICILLIN', '2013-06-10 10:00:00', NULL, 442,
        'Hives and itching with penicillin.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (73, 1022, 6, 2, 'CODEINE', '2015-09-18 14:00:00', NULL, 442,
        'Severe nausea with codeine.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (74, 1022, 10, 1, 'TETRACYCLINE', '2017-02-22 11:00:00', NULL, 442,
        'Photosensitivity reaction with tetracycline.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (75, 1022, 20, 3, 'PEANUTS', '2009-05-15 16:00:00', '2009-05-15 15:00:00', 442,
        'Anaphylaxis to peanuts. Carries EpiPen.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (76, 1022, 22, 2, 'SHELLFISH', '2012-08-20 18:00:00', NULL, 442,
        'Lip swelling with shrimp.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (77, 1022, 25, 1, 'MILK', '2018-11-05 08:00:00', NULL, 442,
        'Lactose intolerance.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),
    (78, 1022, 33, 1, 'PET DANDER', '2020-03-12 09:00:00', NULL, 442,
        'Allergic rhinitis around pets.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),

    -- Patient 1023 (2 allergies)
    (79, 1023, 4, 2, 'ASPIRIN', '2016-04-10 09:30:00', NULL, 589,
        'GI bleeding with aspirin.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (80, 1023, 13, 2, 'ATORVASTATIN', '2018-07-22 10:00:00', NULL, 589,
        'Muscle aches with atorvastatin.',
        'HISTORICAL', 1, 'VERIFIED', 589),

    -- Patient 1024 (4 allergies)
    (81, 1024, 1, 2, 'PENICILLIN', '2014-11-15 10:00:00', NULL, 640,
        'Rash with penicillin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (82, 1024, 9, 3, 'CONTRAST DYE', '2016-05-20 14:00:00', '2016-05-20 13:00:00', 640,
        'Anaphylaxis with IV contrast. Requires pre-medication.',
        'OBSERVED', 1, 'VERIFIED', 640),
    (83, 1024, 23, 2, 'FISH', '2015-08-12 19:00:00', NULL, 640,
        'Hives after eating fish.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (84, 1024, 30, 1, 'POLLEN', '2019-04-20 10:00:00', NULL, 640,
        'Seasonal allergies.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),

    -- Patient 1025 (0 allergies)

    -- Patient 1026 (3 allergies)
    (85, 1026, 2, 2, 'CEPHALOSPORINS', '2017-03-15 11:00:00', NULL, 518,
        'Diarrhea with cephalosporins.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (86, 1026, 14, 2, 'HYDROCODONE', '2018-09-20 14:00:00', NULL, 518,
        'Nausea with hydrocodone.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (87, 1026, 24, 1, 'EGGS', '2016-05-10 08:00:00', NULL, 518,
        'Mild hives with eggs.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),

    -- Patient 1027 (5 allergies)
    (88, 1027, 1, 3, 'PENICILLIN', '2010-07-18 11:00:00', '2010-07-18 10:00:00', 442,
        'Anaphylaxis with penicillin. Carries EpiPen.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (89, 1027, 7, 2, 'MORPHINE', '2013-12-10 14:00:00', NULL, 442,
        'Respiratory depression with morphine.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (90, 1027, 20, 2, 'PEANUTS', '2008-04-22 16:00:00', NULL, 442,
        'Throat tightness with peanuts.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (91, 1027, 21, 2, 'TREE NUTS', '2011-09-15 12:00:00', NULL, 442,
        'Oral swelling with walnuts.',
        'HISTORICAL', 1, 'VERIFIED', 442),
    (92, 1027, 34, 3, 'BEE STINGS', '2015-06-30 15:00:00', '2015-06-30 14:00:00', 442,
        'Anaphylaxis to bee sting. Carries EpiPen.',
        'OBSERVED', 1, 'VERIFIED', 442),

    -- Patient 1028 (1 allergy)
    (93, 1028, 5, 1, 'IBUPROFEN', '2019-02-10 09:00:00', NULL, 589,
        'Stomach upset with ibuprofen.',
        'HISTORICAL', 1, 'VERIFIED', 589),

    -- Patient 1029 (6 allergies)
    (94, 1029, 1, 2, 'AMOXICILLIN', '2015-05-12 10:30:00', NULL, 640,
        'Rash with amoxicillin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (95, 1029, 3, 2, 'SULFA', '2017-08-18 11:00:00', NULL, 640,
        'Rash with sulfa drugs.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (96, 1029, 11, 1, 'ERYTHROMYCIN', '2018-11-22 09:00:00', NULL, 640,
        'GI upset with erythromycin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (97, 1029, 22, 2, 'SHELLFISH', '2014-07-04 18:00:00', '2014-07-04 17:00:00', 640,
        'Hives with lobster.',
        'OBSERVED', 1, 'VERIFIED', 640),
    (98, 1029, 26, 1, 'SOY', '2019-03-15 12:00:00', NULL, 640,
        'GI upset with soy.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),
    (99, 1029, 32, 1, 'MOLD', '2020-09-08 10:00:00', NULL, 640,
        'Allergic symptoms in damp environments.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),

    -- Patient 1030 (0 allergies)

    -- Patient 1031 (4 allergies)
    (100, 1031, 6, 2, 'CODEINE', '2016-10-15 14:00:00', NULL, 518,
        'Severe nausea with codeine.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (101, 1031, 12, 2, 'ACE INHIBITORS', '2018-03-20 09:30:00', NULL, 518,
        'Dry cough with lisinopril.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (102, 1031, 21, 2, 'TREE NUTS', '2015-07-12 12:00:00', NULL, 518,
        'Oral itching with cashews.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (103, 1031, 27, 1, 'WHEAT', '2019-11-08 11:00:00', NULL, 518,
        'Bloating with wheat products.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),

    -- Patient 1032 (2 allergies)
    (104, 1032, 8, 2, 'LATEX', '2017-06-15 14:00:00', '2017-06-15 13:00:00', 442,
        'Contact dermatitis from latex.',
        'OBSERVED', 1, 'VERIFIED', 442),
    (105, 1032, 25, 1, 'MILK', '2018-09-20 08:00:00', NULL, 442,
        'Lactose intolerance.',
        'HISTORICAL', 1, 'UNVERIFIED', 442),

    -- Patient 1033 (3 allergies)
    (106, 1033, 1, 2, 'PENICILLIN', '2013-04-10 10:00:00', NULL, 589,
        'Hives with penicillin.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (107, 1033, 15, 1, 'TRAMADOL', '2017-08-22 14:00:00', NULL, 589,
        'Itching with tramadol.',
        'HISTORICAL', 1, 'VERIFIED', 589),
    (108, 1033, 23, 2, 'FISH', '2015-12-15 19:00:00', NULL, 589,
        'Lip swelling with salmon.',
        'HISTORICAL', 1, 'VERIFIED', 589),

    -- Patient 1034 (0 allergies)

    -- Patient 1035 (5 allergies)
    (109, 1035, 2, 2, 'CEFTRIAXONE', '2016-05-18 11:00:00', NULL, 640,
        'Severe diarrhea with ceftriaxone.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (110, 1035, 4, 1, 'ASPIRIN', '2018-09-12 09:00:00', NULL, 640,
        'GI upset with aspirin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (111, 1035, 16, 1, 'GABAPENTIN', '2019-02-20 14:00:00', NULL, 640,
        'Dizziness and drowsiness with gabapentin.',
        'HISTORICAL', 1, 'VERIFIED', 640),
    (112, 1035, 24, 1, 'EGGS', '2017-06-15 08:00:00', NULL, 640,
        'Mild nausea with eggs.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),
    (113, 1035, 31, 1, 'DUST MITES', '2020-01-10 10:00:00', NULL, 640,
        'Perennial allergic rhinitis.',
        'HISTORICAL', 1, 'UNVERIFIED', 640),

    -- Patient 1036 (2 allergies)
    (114, 1036, 10, 1, 'DOXYCYCLINE', '2018-07-20 10:30:00', NULL, 518,
        'Photosensitivity with doxycycline.',
        'HISTORICAL', 1, 'VERIFIED', 518),
    (115, 1036, 30, 1, 'POLLEN', '2019-04-15 09:00:00', NULL, 518,
        'Seasonal allergic rhinitis.',
        'HISTORICAL', 1, 'UNVERIFIED', 518),

    -- Patient 1026: Margaret E Wilson - DECEASED 2024-12-01 (2 allergies)
    -- Added 2026-02-04 - Important drug allergies documented for elderly patient
    (116, 1026, 1, 3, 'PENICILLIN', '2015-06-10 10:00:00', NULL, 508,
        'Patient reports severe anaphylactic reaction to penicillin VK in 1960s. Required emergency treatment. Patient instructed to avoid all penicillin and cephalosporin antibiotics. Medical alert bracelet worn.',
        'HISTORICAL', 1, 'VERIFIED', 508),
    (117, 1026, 8, 2, 'LATEX', '2018-08-15 14:30:00', '2018-08-15 14:00:00', 508,
        'Developed contact dermatitis with rash and swelling when exposed to latex gloves during medical procedure. Symptoms resolved with antihistamines. Non-latex gloves used for all subsequent procedures.',
        'OBSERVED', 1, 'VERIFIED', 508),

    -- Patient 1027: Robert J Anderson - DECEASED 2024-11-15 (1 allergy)
    -- Added 2026-02-04 - Documented drug allergy for combat veteran with PTSD
    (118, 1027, 3, 2, 'CODEINE', '2017-09-20 10:00:00', '2017-09-18 08:00:00', 528,
        'Patient experienced severe nausea, vomiting, and dizziness after taking codeine-containing cough syrup. Symptoms lasted 6 hours, required ED visit. Patient advised to avoid all codeine-containing medications. Alternatives prescribed for pain management.',
        'OBSERVED', 1, 'VERIFIED', 528);
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Allergy.PatientAllergy OFF;
GO

PRINT '118 patient allergy records inserted successfully';
PRINT 'Distribution: 39 patients (including Patients 1026, 1027 - DECEASED)';
GO
