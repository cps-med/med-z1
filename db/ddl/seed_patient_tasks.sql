-- ============================================================================
-- Clinical Task Tracking - Seed Data
-- ============================================================================
-- Purpose: Create test tasks for development and testing
-- Created: 2026-02-10
-- Test Patients: ICN100001 (Dooree, Adam), ICN100002 (Miifaa, Barry),
--                ICN100010 (Aminor, Alexander), ICN100013 (Thompson, Irving)
-- Test Users: Dr. Anderson, Dr. Brown, Nurse Chen, Dr. Davis
-- ============================================================================

-- Clear existing seed data (for clean recreate during development)
DELETE FROM clinical.patient_tasks;

-- Reset sequence to 1
ALTER SEQUENCE clinical.patient_tasks_task_id_seq RESTART WITH 1;

-- ============================================================================
-- Tasks for Patient ICN100001 (Dooree, Adam)
-- ============================================================================

-- Task 1: High priority, IN_PROGRESS, user-created, recent
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Review discharge summary from recent CHF admission',
    'Patient discharged 2 days ago from Alexandria VAMC. Need to review discharge medications, ensure no DDIs with current med list, and confirm follow-up cardiology appointment scheduled.',
    'HIGH',
    'IN_PROGRESS',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson
    'Dr. Alice Anderson, MD',
    FALSE,
    NOW() - INTERVAL '1 day'
);

-- Task 2: Medium priority, TODO, AI-generated
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100001',
    'Patient overdue for A1C screening',
    'Last A1C: 8.2% on 2025-06-15 (8 months ago). Current ADA guidelines recommend A1C every 6 months for uncontrolled diabetes (target <7% for most patients). Patient has active Type 2 diabetes diagnosis.',
    'MEDIUM',
    'TODO',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson
    'Dr. Alice Anderson, MD',
    TRUE,
    'AI Insights: Active diabetes diagnosis + no A1C in past 6 months',
    NOW() - INTERVAL '2 hours'
);

-- Task 3: High priority, TODO, user-created (different clinician)
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Call patient about abnormal INR result (5.2)',
    'INR critically elevated at 5.2 (target 2-3 for afib). Patient on warfarin 5mg daily. Assess for bleeding symptoms, hold next dose, recheck INR in 48 hours.',
    'HIGH',
    'TODO',
    '76bb61c4-8d22-4605-b290-f1a2b757019b',  -- Dr. Brown
    'Dr. Bob Brown, DO',
    FALSE,
    NOW() - INTERVAL '3 hours'
);

-- Task 4: Medium priority, TODO, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Schedule echocardiogram',
    'Patient has new-onset systolic murmur on exam. Obtain echo to rule out valvular disease or worsening cardiomyopathy. EF was 40% on last echo 2 years ago.',
    'MEDIUM',
    'TODO',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson
    'Dr. Alice Anderson, MD',
    FALSE,
    NOW() - INTERVAL '6 hours'
);

-- Task 5: Low priority, TODO, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Update patient education materials for CHF self-management',
    'Provide patient with revised CHF handout including daily weight monitoring instructions, dietary sodium limits, and warning signs of decompensation.',
    'LOW',
    'TODO',
    'a7b8f182-f105-4c97-aaa0-8765e1d6ec3d',  -- Nurse Chen
    'Nurse Carol Chen, RN',
    FALSE,
    NOW() - INTERVAL '1 week'
);

-- Task 6: Medium priority, COMPLETED yesterday
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    completed_by_user_id, completed_by_display_name,
    is_ai_generated, created_at, completed_at
) VALUES (
    'ICN100001',
    'Review cardiology consult recommendations',
    'Cardiologist recommended increasing metoprolol to 100mg BID and adding spironolactone 25mg daily for CHF management. Reviewed and implemented medication changes.',
    'MEDIUM',
    'COMPLETED',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson (creator)
    'Dr. Alice Anderson, MD',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson (completer)
    'Dr. Alice Anderson, MD',
    FALSE,
    NOW() - INTERVAL '3 days',
    NOW() - INTERVAL '1 day'
);

-- ============================================================================
-- Tasks for Patient ICN100002 (Miifaa, Barry)
-- ============================================================================

-- Task 7: High priority, TODO, AI-generated
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100002',
    'INR monitoring needed for warfarin',
    'Patient on warfarin but no INR test in past 30 days. Warfarin requires regular INR monitoring to prevent bleeding/clotting complications. Last INR: 2.8 on 2025-12-15.',
    'HIGH',
    'TODO',
    '76bb61c4-8d22-4605-b290-f1a2b757019b',  -- Dr. Brown
    'Dr. Bob Brown, DO',
    TRUE,
    'AI Insights: Active warfarin prescription + no recent INR',
    NOW() - INTERVAL '4 hours'
);

-- Task 8: Medium priority, IN_PROGRESS, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100002',
    'Medication reconciliation after ER visit',
    'Patient presented to ER 3 days ago with chest pain. Rule out MI protocol completed. Need to reconcile medications and ensure patient is on appropriate post-event therapy.',
    'MEDIUM',
    'IN_PROGRESS',
    'd388af7d-4ac5-438e-ab70-db14ba59081b',  -- Dr. Davis
    'Dr. David Davis, MD',
    FALSE,
    NOW() - INTERVAL '2 days'
);

-- Task 9: Low priority, COMPLETED, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    completed_by_user_id, completed_by_display_name,
    is_ai_generated, created_at, completed_at
) VALUES (
    'ICN100002',
    'Refill patient''s blood pressure medications',
    'Patient called pharmacy requesting refill of lisinopril 20mg and metoprolol 50mg. Both due for renewal.',
    'LOW',
    'COMPLETED',
    '7d3ccf18-b5e8-4513-8178-da6de0839721',  -- Pharmacist Evans (creator)
    'Pharmacist Emma Evans, PharmD',
    '7d3ccf18-b5e8-4513-8178-da6de0839721',  -- Pharmacist Evans (completer)
    'Pharmacist Emma Evans, PharmD',
    FALSE,
    NOW() - INTERVAL '5 hours',
    NOW() - INTERVAL '2 hours'
);

-- ============================================================================
-- Tasks for Patient ICN100010 (Aminor, Alexander)
-- ============================================================================

-- Task 10: High priority, TODO, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100010',
    'Follow up on critical potassium level (K+ 6.1)',
    'Lab reported critical hyperkalemia. Patient on ACE inhibitor and spironolactone. Repeat labs ordered stat, nephrology consult placed. Monitor for EKG changes.',
    'HIGH',
    'TODO',
    '6c84a732-4834-40ed-8c49-3fd8c69df8f6',  -- Dr. Foster
    'Dr. Frank Foster, MD',
    FALSE,
    NOW() - INTERVAL '30 minutes'
);

-- Task 11: Medium priority, TODO, AI-generated
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100010',
    'Patient overdue for colonoscopy screening',
    'Patient is 58 years old with family history of colon cancer. Last colonoscopy: 2015 (10 years ago). Current guidelines recommend colonoscopy every 10 years, or every 5 years with family history.',
    'MEDIUM',
    'TODO',
    '87661185-e2d1-4a1a-ac16-eb7d5ea71de0',  -- Dr. Green
    'Dr. Grace Green, MD',
    TRUE,
    'AI Insights: Age 58 + family history + overdue by 5 years',
    NOW() - INTERVAL '1 day'
);

-- Task 12: Medium priority, COMPLETED, user-created (team handoff scenario)
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    completed_by_user_id, completed_by_display_name,
    is_ai_generated, created_at, completed_at
) VALUES (
    'ICN100010',
    'Review radiology report for chest X-ray',
    'Chest X-ray ordered for chronic cough. Radiology report finalized this morning. Need to review findings and communicate results to patient.',
    'MEDIUM',
    'COMPLETED',
    '5dbd2ba1-4b8d-4d0c-a4ea-5a3f9f6969c2',  -- Dr. Anderson (creator)
    'Dr. Alice Anderson, MD',
    '76bb61c4-8d22-4605-b290-f1a2b757019b',  -- Dr. Brown (completer, team handoff)
    'Dr. Bob Brown, DO',
    FALSE,
    NOW() - INTERVAL '8 hours',
    NOW() - INTERVAL '1 hour'
);

-- ============================================================================
-- Tasks for Patient ICN100013 (Thompson, Irving)
-- ============================================================================

-- Task 13: High priority, TODO, AI-generated
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100013',
    'Review discharge summary from recent hospitalization',
    'Patient discharged 5 days ago from CHF admission. Discharge summary includes medication changes and 2-week follow-up. Need to review and schedule appointments.',
    'HIGH',
    'TODO',
    'd388af7d-4ac5-438e-ab70-db14ba59081b',  -- Dr. Davis
    'Dr. David Davis, MD',
    TRUE,
    'AI Insights: Recent inpatient discharge (5 days ago)',
    NOW() - INTERVAL '12 hours'
);

-- Task 14: Medium priority, IN_PROGRESS, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100013',
    'Prior authorization for new COPD inhaler',
    'Patient''s current inhaler (albuterol) not providing adequate symptom control. Pulmonologist recommended switching to Symbicort. Need to complete prior authorization paperwork.',
    'MEDIUM',
    'IN_PROGRESS',
    '7d3ccf18-b5e8-4513-8178-da6de0839721',  -- Pharmacist Evans
    'Pharmacist Emma Evans, PharmD',
    FALSE,
    NOW() - INTERVAL '1 day'
);

-- Task 15: Low priority, TODO, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100013',
    'Update advance directives documentation',
    'Patient expressed interest in updating healthcare proxy and living will during last visit. Send forms to patient and schedule follow-up discussion.',
    'LOW',
    'TODO',
    'a7b8f182-f105-4c97-aaa0-8765e1d6ec3d',  -- Nurse Chen
    'Nurse Carol Chen, RN',
    FALSE,
    NOW() - INTERVAL '2 weeks'
);

-- ============================================================================
-- Verification Query
-- ============================================================================

-- Display all seeded tasks with summary
SELECT
    task_id,
    patient_key,
    LEFT(title, 50) || '...' AS title_preview,
    priority,
    status,
    created_by_display_name,
    is_ai_generated,
    created_at
FROM clinical.patient_tasks
ORDER BY patient_key, priority, created_at DESC;

-- Summary statistics
SELECT
    status,
    COUNT(*) AS task_count
FROM clinical.patient_tasks
GROUP BY status
ORDER BY status;

SELECT
    priority,
    COUNT(*) AS task_count
FROM clinical.patient_tasks
GROUP BY priority
ORDER BY
    CASE priority
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END;

SELECT
    is_ai_generated,
    COUNT(*) AS task_count
FROM clinical.patient_tasks
GROUP BY is_ai_generated;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS: Seeded 15 test tasks across 4 patients';
END $$;
