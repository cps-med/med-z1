-----------------------------------------------------------------------
-- NDimMill.CodeValue.sql (INSERT)
-- Populate code value system for Oracle Health (Cerner)
-- Phase 1: Essential code sets for Vitals and Allergies domains
-----------------------------------------------------------------------

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Populating NDimMill.CodeValue with Phase 1 code sets...';
GO

-- =======================================================================
-- VITAL_TYPE Code Set
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('VITAL_TYPE', 'BP', 'Blood Pressure', 'Systolic and diastolic blood pressure measurement', 1),
    ('VITAL_TYPE', 'PULSE', 'Pulse', 'Heart rate in beats per minute', 1),
    ('VITAL_TYPE', 'TEMP', 'Temperature', 'Body temperature', 1),
    ('VITAL_TYPE', 'WEIGHT', 'Weight', 'Body weight', 1),
    ('VITAL_TYPE', 'HEIGHT', 'Height', 'Body height', 1),
    ('VITAL_TYPE', 'RESPRATE', 'Respiratory Rate', 'Breaths per minute', 1),
    ('VITAL_TYPE', 'SPO2', 'Oxygen Saturation', 'Blood oxygen saturation percentage', 1),
    ('VITAL_TYPE', 'PAIN', 'Pain Score', 'Pain level on 0-10 scale', 1);

PRINT '  - Inserted 8 VITAL_TYPE codes';

-- =======================================================================
-- UNIT Code Set (for vital measurements)
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('UNIT', 'MMHG', 'mmHg', 'Millimeters of mercury (blood pressure)', 1),
    ('UNIT', 'BPM', 'bpm', 'Beats per minute (heart rate)', 1),
    ('UNIT', 'DEGF', '°F', 'Degrees Fahrenheit (temperature)', 1),
    ('UNIT', 'DEGC', '°C', 'Degrees Celsius (temperature)', 1),
    ('UNIT', 'LBS', 'lbs', 'Pounds (weight)', 1),
    ('UNIT', 'KG', 'kg', 'Kilograms (weight)', 1),
    ('UNIT', 'IN', 'in', 'Inches (height)', 1),
    ('UNIT', 'CM', 'cm', 'Centimeters (height)', 1),
    ('UNIT', 'PERCENT', '%', 'Percentage (oxygen saturation)', 1),
    ('UNIT', 'BRE_MIN', '/min', 'Breaths per minute (respiratory rate)', 1);

PRINT '  - Inserted 10 UNIT codes';

-- =======================================================================
-- ALLERGEN Code Set
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    -- Drug allergens
    ('ALLERGEN', 'PEN', 'Penicillin', 'Penicillin antibiotic allergy', 1),
    ('ALLERGEN', 'ASA', 'Aspirin', 'Aspirin (acetylsalicylic acid) allergy', 1),
    ('ALLERGEN', 'SULFA', 'Sulfa Drugs', 'Sulfonamide antibiotic allergy', 1),
    ('ALLERGEN', 'CODEINE', 'Codeine', 'Codeine opioid allergy', 1),
    ('ALLERGEN', 'MORPHINE', 'Morphine', 'Morphine opioid allergy', 1),
    ('ALLERGEN', 'IODINE', 'Iodine', 'Iodine contrast dye allergy', 1),
    ('ALLERGEN', 'LATEX', 'Latex', 'Natural rubber latex allergy', 1),

    -- Food allergens
    ('ALLERGEN', 'PEANUT', 'Peanuts', 'Peanut allergy', 1),
    ('ALLERGEN', 'SHELLFISH', 'Shellfish', 'Shellfish allergy', 1),
    ('ALLERGEN', 'EGGS', 'Eggs', 'Egg allergy', 1),
    ('ALLERGEN', 'MILK', 'Milk', 'Dairy/milk allergy', 1),

    -- Environmental allergens
    ('ALLERGEN', 'POLLEN', 'Pollen', 'Seasonal pollen allergy', 1),
    ('ALLERGEN', 'DUST', 'Dust Mites', 'Dust mite allergy', 1);

PRINT '  - Inserted 13 ALLERGEN codes';

-- =======================================================================
-- REACTION Code Set (adverse reactions to allergens)
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('REACTION', 'RASH', 'Rash', 'Skin rash or dermatitis', 1),
    ('REACTION', 'HIVES', 'Hives', 'Urticaria (raised, itchy welts)', 1),
    ('REACTION', 'ITCHING', 'Itching', 'Pruritus without visible rash', 1),
    ('REACTION', 'SWELLING', 'Swelling', 'Angioedema or localized swelling', 1),
    ('REACTION', 'ANAPHYLAXIS', 'Anaphylaxis', 'Severe systemic allergic reaction', 1),
    ('REACTION', 'NAUSEA', 'Nausea', 'Feeling of sickness in stomach', 1),
    ('REACTION', 'VOMITING', 'Vomiting', 'Emesis', 1),
    ('REACTION', 'DIARRHEA', 'Diarrhea', 'Loose or watery stools', 1),
    ('REACTION', 'DYSPNEA', 'Shortness of Breath', 'Difficulty breathing or dyspnea', 1),
    ('REACTION', 'WHEEZING', 'Wheezing', 'Whistling sound during breathing', 1),
    ('REACTION', 'BRONCHOSPASM', 'Bronchospasm', 'Airway constriction', 1),
    ('REACTION', 'HYPOTENSION', 'Low Blood Pressure', 'Hypotension', 1),
    ('REACTION', 'TACHYCARDIA', 'Rapid Heart Rate', 'Tachycardia', 1);

PRINT '  - Inserted 13 REACTION codes';

-- =======================================================================
-- SEVERITY Code Set (allergy severity levels)
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('SEVERITY', 'MILD', 'Mild', 'Minor symptoms, no treatment required', 1),
    ('SEVERITY', 'MODERATE', 'Moderate', 'Noticeable symptoms, may require treatment', 1),
    ('SEVERITY', 'SEVERE', 'Severe', 'Serious symptoms, requires immediate treatment', 1),
    ('SEVERITY', 'LIFE_THREAT', 'Life-Threatening', 'Potentially fatal reaction (anaphylaxis)', 1);

PRINT '  - Inserted 4 SEVERITY codes';

-- =======================================================================
-- FAMILY_RELATIONSHIP Code Set
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('FAMILY_RELATIONSHIP', 'MOTHER', 'Mother', 'Biological or adoptive mother', 1),
    ('FAMILY_RELATIONSHIP', 'FATHER', 'Father', 'Biological or adoptive father', 1),
    ('FAMILY_RELATIONSHIP', 'SISTER', 'Sister', 'Full or half sister', 1),
    ('FAMILY_RELATIONSHIP', 'BROTHER', 'Brother', 'Full or half brother', 1),
    ('FAMILY_RELATIONSHIP', 'SON', 'Son', 'Biological or adoptive son', 1),
    ('FAMILY_RELATIONSHIP', 'DAUGHTER', 'Daughter', 'Biological or adoptive daughter', 1),
    ('FAMILY_RELATIONSHIP', 'MAT_GRANDMOTHER', 'Maternal Grandmother', 'Mother of mother', 1),
    ('FAMILY_RELATIONSHIP', 'MAT_GRANDFATHER', 'Maternal Grandfather', 'Father of mother', 1),
    ('FAMILY_RELATIONSHIP', 'PAT_GRANDMOTHER', 'Paternal Grandmother', 'Mother of father', 1),
    ('FAMILY_RELATIONSHIP', 'PAT_GRANDFATHER', 'Paternal Grandfather', 'Father of father', 1),
    ('FAMILY_RELATIONSHIP', 'AUNT', 'Aunt', 'Aunt (maternal or paternal)', 1),
    ('FAMILY_RELATIONSHIP', 'UNCLE', 'Uncle', 'Uncle (maternal or paternal)', 1),
    ('FAMILY_RELATIONSHIP', 'UNKNOWN', 'Unknown Relative', 'Relationship not specified', 1);

PRINT '  - Inserted 13 FAMILY_RELATIONSHIP codes';

-- =======================================================================
-- FAMILY_HISTORY_CONDITION Code Set
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('FAMILY_HISTORY_CONDITION', 'HTN', 'Hypertension', 'Family history of hypertension', 1),
    ('FAMILY_HISTORY_CONDITION', 'CAD', 'Coronary Artery Disease', 'Family history of coronary artery disease', 1),
    ('FAMILY_HISTORY_CONDITION', 'MI', 'Myocardial Infarction', 'Family history of myocardial infarction', 1),
    ('FAMILY_HISTORY_CONDITION', 'STROKE', 'Stroke', 'Family history of stroke', 1),
    ('FAMILY_HISTORY_CONDITION', 'T2DM', 'Type 2 Diabetes Mellitus', 'Family history of type 2 diabetes', 1),
    ('FAMILY_HISTORY_CONDITION', 'BREAST_CA', 'Breast Cancer', 'Family history of breast cancer', 1),
    ('FAMILY_HISTORY_CONDITION', 'COLON_CA', 'Colon Cancer', 'Family history of colon cancer', 1),
    ('FAMILY_HISTORY_CONDITION', 'ALZHEIMERS', 'Alzheimer Disease', 'Family history of Alzheimer disease', 1),
    ('FAMILY_HISTORY_CONDITION', 'ASTHMA', 'Asthma', 'Family history of asthma', 1),
    ('FAMILY_HISTORY_CONDITION', 'ADHD', 'Attention-Deficit/Hyperactivity Disorder', 'Family history of ADHD', 1),
    ('FAMILY_HISTORY_CONDITION', 'AUTISM', 'Autism Spectrum Disorder', 'Family history of autism spectrum disorder', 1),
    ('FAMILY_HISTORY_CONDITION', 'SUBSTANCE_USE', 'Substance Use Disorder', 'Family history of substance use disorder', 1),
    ('FAMILY_HISTORY_CONDITION', 'NONE_REPORTED', 'No Known Family History', 'No family history reported', 1);

PRINT '  - Inserted 13 FAMILY_HISTORY_CONDITION codes';

-- =======================================================================
-- FAMILY_HISTORY_STATUS Code Set
-- =======================================================================

INSERT INTO NDimMill.CodeValue (CodeSet, Code, DisplayText, Description, IsActive)
VALUES
    ('FAMILY_HISTORY_STATUS', 'ACTIVE', 'Active', 'Current known family-history finding', 1),
    ('FAMILY_HISTORY_STATUS', 'RESOLVED', 'Resolved', 'Historical family-history finding', 1),
    ('FAMILY_HISTORY_STATUS', 'UNKNOWN', 'Unknown', 'Status not known', 1);

PRINT '  - Inserted 3 FAMILY_HISTORY_STATUS codes';

-- =======================================================================
-- Summary
-- =======================================================================

PRINT '';
PRINT 'Code value population complete:';
SELECT CodeSet, COUNT(*) AS CodeCount
FROM NDimMill.CodeValue
GROUP BY CodeSet
ORDER BY CodeSet;

PRINT '';
PRINT 'Total code values inserted:';
SELECT COUNT(*) AS TotalCodes FROM NDimMill.CodeValue;
GO
