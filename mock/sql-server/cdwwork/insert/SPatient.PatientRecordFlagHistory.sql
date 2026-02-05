/*
|--------------------------------------------------------------------------------
| Insert: SPatient.PatientRecordFlagHistory.sql
|--------------------------------------------------------------------------------
| Insert sample data into table:  SPatient.PatientRecordFlagHistory
|
| Sample patient flag history records with realistic narrative text
| Covers initial assignments, reviews, continuations, and inactivations
|
| IMPORTANT: Contains SENSITIVE narrative text with clinical details
|--------------------------------------------------------------------------------
*/

PRINT '==== SPatient.PatientRecordFlagHistory ====';
GO

-- set the active database
USE CDWWork;
GO

-- Ensure QUOTED_IDENTIFIER is ON (best practice)
SET QUOTED_IDENTIFIER ON;
GO

-- Sample history records for patient flag assignments
-- PatientRecordFlagAssignmentSID values correspond to IDENTITY values from Assignment table
-- Assuming sequential assignment: SID 1 = first INSERT, SID 2 = second INSERT, etc.
--
-- Action Codes:
--   1 = NEW ASSIGNMENT
--   2 = CONTINUE
--   3 = INACTIVATE
--   4 = REACTIVATE
--   5 = ENTERED IN ERROR
INSERT INTO SPatient.PatientRecordFlagHistory
(
    PatientRecordFlagAssignmentSID, PatientSID, HistoryDateTime, ActionCode, ActionName,
    EnteredByDUZ, EnteredByName, ApprovedByDUZ, ApprovedByName, TiuDocumentIEN,
    HistoryComments, EventSiteSta3n
)
VALUES
    -- ========================================================================
    -- Patient 1001: HIGH RISK FOR SUICIDE (AssignmentSID 1)
    -- ========================================================================
    -- Initial assignment
    (1, 1001, '2024-11-15 09:30:00', 1, 'NEW ASSIGNMENT',
     12345, 'Dr. Sarah Johnson', 67890, 'Dr. Michael Chen (Chief of Staff)',
     900001,
     N'Flag created after ED visit for suicidal ideation on 11/14/24. Patient expressed intent with plan involving firearm access. Safety plan established and documented in linked TIU note. Patient admitted to Mental Health ward for stabilization. Firearm safety counseling completed. CONTACT: Dr. Johnson x5542 or VA Police if patient presents with concerning behavior.',
     '518'),

    -- 90-day review - continued
    (1, 1001, '2025-01-15 10:00:00', 2, 'CONTINUE',
     23456, 'Dr. Emily Rodriguez', 67890, 'Dr. Michael Chen (Chief of Staff)',
     900250,
     N'Reviewed in Suicide Prevention team meeting 1/15/25. Veteran remains at elevated risk based on PHQ-9 score of 18, recent housing instability, and chronic pain (9/10). Safety plan reviewed and updated with new emergency contacts. Veteran engaged in weekly therapy and medication management. Continue flag for next 90-day period pending clinical improvement.',
     '518'),

    -- ========================================================================
    -- Patient 1002: BEHAVIORAL (AssignmentSID 2) - INACTIVE
    -- ========================================================================
    -- Initial assignment
    (2, 1002, '2023-08-01 14:00:00', 1, 'NEW ASSIGNMENT',
     34567, 'Patricia Williams, RN', 78901, 'Dr. Robert Martinez (Chief of Staff)',
     901000,
     N'History of aggressive behavior towards staff on 7/30/23. Patient became verbally threatening and physically intimidating when asked to wait for prescription refill. Yelled profanities and approached pharmacy window in aggressive manner. Implemented two-person escort policy and de-escalation protocol per VHA Directive 2010-053. CONTACT: Nurse Williams x3421 or VA Police for standby if patient becomes agitated.',
     '663'),

    -- Inactivated after improvement
    (2, 1002, '2024-03-10 11:45:00', 3, 'INACTIVATE',
     34567, 'Patricia Williams, RN', 78901, 'Dr. Robert Martinez (Chief of Staff)',
     901450,
     N'Behavioral issues stable for >6 months with no incidents reported. Patient successfully completed anger management program (12 weeks) and demonstrates improved coping skills. Staff report consistently positive interactions during recent visits. Patient has apologized for past behavior and shows genuine remorse. Flag inactivated per policy. Will monitor; can reactivate if concerning issues recur.',
     '663'),

    -- ========================================================================
    -- Patient 1003: VIOLENCE PREVENTION (AssignmentSID 3)
    -- ========================================================================
    -- Initial assignment
    (3, 1003, '2024-06-20 13:15:00', 1, 'NEW ASSIGNMENT',
     45678, 'James Anderson, LCSW', 89012, 'Dr. Lisa Thompson (Chief of Staff)',
     902000,
     N'History of violent outbursts documented in clinical file. Veteran has combat-related PTSD with specific trauma triggers. Triggered by loud noises (backfires, doors slamming) and crowded waiting areas. Previous incident: physical altercation in clinic 6/18/24 when startled by alarm. RECOMMEND: Quiet exam rooms away from main entrance, minimize wait times, staff awareness of triggers, offer first/last appointments. CONTACT: Social Work (x4200) or VA Police if de-escalation needed.',
     '528'),

    -- 6-month review continued
    (3, 1003, '2024-12-01 14:00:00', 2, 'CONTINUE',
     45678, 'James Anderson, LCSW', 89012, 'Dr. Lisa Thompson (Chief of Staff)',
     902300,
     N'6-month review completed 12/1/24. Veteran actively engaged in PTSD treatment (PE therapy, medication management) with measurable improvement in symptom severity (PCL-5 decreased from 58 to 42). However, risk factors persist given combat history and environmental triggers. Veteran appreciates staff accommodations and reports feeling safer with current protocols. Continue flag and current precautions. Next review June 2025.',
     '528'),

    -- ========================================================================
    -- Patient 1007: DRUG SEEKING BEHAVIOR (AssignmentSID 5)
    -- ========================================================================
    (5, 1007, '2024-06-15 16:30:00', 1, 'NEW ASSIGNMENT',
     56789, 'Dr. Angela Martinez', 90123, 'Dr. Patricia Davis (Chief of Staff)',
     903000,
     N'Pattern of drug-seeking behavior documented over past 3 months. Patient has requested early refills of oxycodone on 4 occasions citing "lost medication" or "spilled pills." Urine drug screen 6/10/24 positive for non-prescribed benzodiazepines. Patient admits to obtaining medications from multiple sources. Referred to Addiction Medicine for assessment and treatment. RECOMMEND: Controlled substance agreement required, pill counts, urine drug screens, no early refills. CONTACT: Dr. Martinez x6789 for prescribing questions.',
     '589'),

    -- ========================================================================
    -- Patient 1009: CRISIS NOTE (AssignmentSID 6) - OVERDUE
    -- ========================================================================
    (6, 1009, '2024-05-20 10:00:00', 1, 'NEW ASSIGNMENT',
     67890, 'Dr. Michael Foster', 12345, 'Dr. Susan Lee (Chief of Staff)',
     904000,
     N'Crisis intervention following family emergency and acute mental health decompensation. Patient presented to ED 5/19/24 with severe anxiety, panic attacks, and brief suicidal thoughts (no plan/intent). Recently experienced death of spouse and loss of housing. Immediate crisis plan implemented with daily check-ins from Social Work. Patient stabilized with medication adjustment and intensive case management. CONTACT: Dr. Foster x7890 or Crisis Line x7777 for acute concerns.',
     '640'),

    -- Review (would have continued but is now overdue - demonstrating overdue scenario)
    (6, 1009, '2024-08-15 09:00:00', 2, 'CONTINUE',
     67890, 'Dr. Michael Foster', 12345, 'Dr. Susan Lee (Chief of Staff)',
     904200,
     N'3-month review 8/15/24. Patient improved significantly with therapy and medication. Crisis resolved, patient relocated to stable housing. Stressors reduced but continue flag given recent trauma history and need for ongoing monitoring. Next review 11/15/24.',
     '640'),

    -- ========================================================================
    -- Patient 1010: HIGH RISK FOR SUICIDE (AssignmentSID 7)
    -- ========================================================================
    (7, 1010, '2024-07-22 11:00:00', 1, 'NEW ASSIGNMENT',
     78901, 'Dr. Jennifer Williams', 23456, 'Dr. David Kim (Chief of Staff)',
     905000,
     N'Flag created following disclosure of suicidal ideation during primary care visit 7/21/24. Patient reports persistent thoughts of self-harm related to chronic illness diagnosis (terminal cancer). Has access to lethal means (firearms at home). Safety plan created with family involvement, firearms temporarily removed by family member. Patient agrees to Emergency Department evaluation if thoughts intensify. Enrolled in palliative care and mental health services. CONTACT: Dr. Williams x8901 or Crisis Line immediately if concerning contact.',
     '640'),

    (7, 1010, '2024-12-05 09:30:00', 2, 'CONTINUE',
     78901, 'Dr. Jennifer Williams', 23456, 'Dr. David Kim (Chief of Staff)',
     905150,
     N'90-day review 12/5/24. Patient continues to struggle with cancer diagnosis but reports safety plan is effective. No acute suicidal ideation at this time. Strong family support system in place. Engaged in palliative care and psychotherapy. Continue flag given ongoing risk factors and terminal illness. Next review 3/5/25.',
     '640'),

    -- ========================================================================
    -- Patient 1010: VIOLENCE PREVENTION (AssignmentSID 8)
    -- ========================================================================
    (8, 1010, '2024-07-22 11:15:00', 1, 'NEW ASSIGNMENT',
     78901, 'Dr. Jennifer Williams', 23456, 'Dr. David Kim (Chief of Staff)',
     905001,
     N'Concurrent flag with suicide risk. Patient has history of explosive anger when frustrated, documented altercation with staff in 2023 (threw clipboard). Related to PTSD and current health crisis. Family reports patient sometimes "loses control" when in pain or stressed. RECOMMEND: Calm environment, clear communication, pain management prioritization, de-escalation training for care team. CONTACT: Security x9999 if patient shows signs of agitation.',
     '640'),

    -- ========================================================================
    -- Patient 1014: DISRUPTIVE BEHAVIOR (AssignmentSID 10)
    -- ========================================================================
    (10, 1014, '2024-08-10 13:00:00', 1, 'NEW ASSIGNMENT',
     89012, 'Maria Gonzalez, LCSW', 34567, 'Dr. Thomas White (Chief of Staff)',
     906000,
     N'Pattern of disruptive behavior in clinic settings. Patient frequently arrives late, becomes loud and confrontational when asked to follow clinic policies. On 8/9/24 patient shouted at receptionist and used profane language when informed of wait time. Patient has cognitive impairment (TBI history) which contributes to frustration intolerance. RECOMMEND: First appointment of day to minimize wait, written instructions, patience with communication difficulties. CONTACT: Social Work x1234 for de-escalation support.',
     '688'),

    -- ========================================================================
    -- Patient 1016: PATIENT ADVOCATE REFERRAL (AssignmentSID 11) - INACTIVE
    -- ========================================================================
    (11, 1016, '2024-01-15 09:00:00', 1, 'NEW ASSIGNMENT',
     90123, 'Thomas Reed, Patient Advocate', 45678, 'Dr. Karen Miller (Chief of Staff)',
     907000,
     N'Patient filed formal complaint regarding medication errors and communication breakdown with pharmacy. Patient Advocate investigating concerns. Temporarily flagged to ensure all staff are aware of ongoing investigation and provide enhanced service during resolution period. CONTACT: Patient Advocate x2345 for case coordination.',
     '663'),

    (11, 1016, '2024-04-10 09:00:00', 2, 'CONTINUE',
     90123, 'Thomas Reed, Patient Advocate', 45678, 'Dr. Karen Miller (Chief of Staff)',
     907100,
     N'Investigation ongoing. Medication error confirmed and corrected. Working with patient on resolution. Continue flag during complaint resolution process.',
     '663'),

    (11, 1016, '2024-06-20 10:30:00', 3, 'INACTIVATE',
     90123, 'Thomas Reed, Patient Advocate', 45678, 'Dr. Karen Miller (Chief of Staff)',
     907200,
     N'Case resolved to patient satisfaction. Pharmacy process improvements implemented. Patient satisfied with response and resolution. No ongoing concerns. Flag inactivated.',
     '663'),

    -- ========================================================================
    -- Patient 1024: HIGH RISK FOR SUICIDE (AssignmentSID 15) - INACTIVE
    -- ========================================================================
    (15, 1024, '2024-03-10 11:00:00', 1, 'NEW ASSIGNMENT',
     12346, 'Dr. Rachel Adams', 67891, 'Dr. James Brown (Chief of Staff)',
     908000,
     N'Flag created after patient disclosed suicidal ideation following divorce and job loss. Patient presented to Mental Health clinic with plan but no immediate intent. Safety plan established, means restriction counseling provided. Patient started on antidepressant and enrolled in intensive outpatient program. CONTACT: Dr. Adams x3456 or Crisis Line for acute concerns.',
     '660'),

    (15, 1024, '2024-06-10 09:00:00', 2, 'CONTINUE',
     12346, 'Dr. Rachel Adams', 67891, 'Dr. James Brown (Chief of Staff)',
     908100,
     N'90-day review. Patient showing good improvement. PHQ-9 decreased from 21 to 12. Stressors stabilizing - gained new employment, attending therapy regularly. Suicide risk decreased but continue flag as precaution during recovery period.',
     '660'),

    (15, 1024, '2024-09-15 10:00:00', 3, 'INACTIVATE',
     12346, 'Dr. Rachel Adams', 67891, 'Dr. James Brown (Chief of Staff)',
     908200,
     N'Patient demonstrates sustained clinical improvement over 6 months. PHQ-9 now 5 (minimal symptoms). Strong protective factors: stable employment, new relationship, engaged in therapy, no suicidal ideation for 4+ months. Patient agrees flag can be removed. Will continue outpatient mental health treatment. Flag inactivated - patient successfully stabilized.',
     '660'),

    -- ========================================================================
    -- Patient 1026: PALLIATIVE CARE (AssignmentSID 16) - DECEASED 2024-12-01
    -- Updated 2026-02-04 - Corrected from BEHAVIORAL to PALLIATIVE CARE
    -- ========================================================================
    -- Initial assignment when goals of care shifted to comfort
    (16, 1026, '2024-10-15 09:00:00', 1, 'NEW ASSIGNMENT',
     15002, 'Dr. Sarah Mitchell (Palliative Care)', 15001, 'Dr. James Anderson (Hospitalist)',
     NULL,
     N'87-year-old female veteran with advanced multi-organ failure (CHF EF 35%, COPD on home O2, CKD Stage 3b, uncontrolled DM2). Goals of care discussion held 10/15/24 with patient and family. Patient elected comfort-focused care given poor prognosis and progressive decline. DNR/DNI status established per patient wishes. Palliative Care flag activated to ensure all staff aware of comfort care goals. Patient desires to maximize quality of life, avoid hospitalizations if possible, focus on symptom management. CONTACT: Palliative Care team x2800 for care coordination and symptom management support.',
     '508'),

    -- Review during final hospitalization
    (16, 1026, '2024-11-15 10:00:00', 2, 'CONTINUE',
     15002, 'Dr. Sarah Mitchell (Palliative Care)', 15001, 'Dr. James Anderson (Hospitalist)',
     50121,
     N'30-day review completed during current hospitalization (admitted 11/25/24 for acute decompensation). Patient''s condition deteriorating with cardiorenal syndrome and multi-organ failure. Comfort measures only plan remains appropriate and consistent with patient''s clearly expressed wishes. Family at bedside, supportive of care plan. Morphine and lorazepam PRN managing dyspnea and anxiety effectively. Patient appears comfortable. Continue palliative care flag. Prognosis: hours to days.',
     '508'),

    -- Inactivation at time of death
    (16, 1026, '2024-12-01 14:35:00', 3, 'INACTIVATE',
     15001, 'Dr. James Anderson (Hospitalist)', 15003, 'Dr. Robert Chen (Chief of Medicine)',
     50123,
     N'Patient expired 12/1/24 at 14:35 hours. Death was expected and peaceful, consistent with natural progression of multi-organ system failure. Daughter present at bedside. Patient received compassionate end-of-life care consistent with her expressed wishes for comfort and dignity. All palliative care goals met. Flag inactivated at time of death per standard protocol. Discharge summary and death certificate completed.',
     '508'),

    -- ========================================================================
    -- Patient 1027: HIGH RISK FOR SUICIDE (AssignmentSID 17) - DECEASED 2024-11-15
    -- Updated 2026-02-04 - Combat veteran with PTSD, MDD, died by suicide
    -- ========================================================================
    -- Initial assignment after first suicide attempt
    (17, 1027, '2019-06-21 14:00:00', 1, 'NEW ASSIGNMENT',
     15004, 'Dr. Jennifer Williams (Staff Psychiatrist)', 15005, 'Dr. Michael Foster (Chief of Psychiatry)',
     50124,
     N'46-year-old OIF/OEF combat veteran admitted following serious suicide attempt by overdose on 6/20/19. Patient found unresponsive, required medical stabilization. Reports escalating depression over 6 months following divorce and job loss. Made deliberate plan, wrote suicide note. On psychiatric evaluation, patient expresses ongoing wish to die and regret that he survived. ACUTE HIGH RISK: Recent serious attempt, ongoing ideation, multiple risk factors (depression, PTSD, substance use, social isolation). Patient agrees to voluntary psychiatric hospitalization. HIGH RISK FOR SUICIDE flag activated per VHA suicide prevention protocols. CONTACT: Dr. Williams x4567 or Suicide Prevention Coordinator x7777 for concerns.',
     '528'),

    -- Continue after 2023 psychiatric hospitalization
    (17, 1027, '2023-03-17 11:00:00', 2, 'CONTINUE',
     15004, 'Dr. Jennifer Williams (Staff Psychiatrist)', 15005, 'Dr. Michael Foster (Chief of Psychiatry)',
     50125,
     N'Patient discharged today after 7-day psychiatric hospitalization for PTSD exacerbation with suicidal ideation. Admission triggered by Afghanistan withdrawal news coverage causing intense combat flashbacks. Patient came to ED voluntarily before acting on plan - this represents significant improvement in insight and help-seeking compared to 2019 attempt. Made good progress during hospitalization, suicidal ideation decreased significantly. However, chronic risk factors remain: combat PTSD, major depression, history of previous attempt. Patient engaged in treatment, sober 18 months, strong family support. Continue HIGH RISK flag with close outpatient monitoring. Next review: June 2023.',
     '528'),

    -- Continue after final outpatient visit (day before death)
    (17, 1027, '2024-11-14 15:45:00', 2, 'CONTINUE',
     15004, 'Dr. Jennifer Williams (Staff Psychiatrist)', 15005, 'Dr. Michael Foster (Chief of Psychiatry)',
     50126,
     N'Patient seen today for routine follow-up, presenting with worsening depression over past 4-6 weeks. Recent job loss, social isolation, increased PTSD symptoms. Endorsed passive suicidal ideation but DENIES plan or intent. Safety plan reviewed and updated, patient has crisis numbers, agreed to call if symptoms worsen. RISK ASSESSMENT: MODERATE-HIGH given recent stressors and symptom escalation. Protective factors: States he won''t act on thoughts, mother''s birthday next week. Medications adjusted, urgent follow-up scheduled in 1 week. Patient appeared to engage with safety planning but affect remained flat. Continue HIGH RISK flag with close monitoring. Will call patient in 2-3 days to check in.',
     '528'),

    -- Inactivation at time of death
    (17, 1027, '2024-11-15 10:00:00', 3, 'INACTIVATE',
     15005, 'Dr. Michael Foster (Chief of Psychiatry)', 15006, 'Dr. Sarah Mitchell (Chief of Staff)',
     50127,
     N'Patient died by suicide on 11/15/24 at 08:30 hours. Found unresponsive at home by friend, brought to ED, resuscitation unsuccessful. This represents tragic loss of combat veteran with chronic PTSD and depression. Patient was seen in psychiatry clinic day before death (11/14/24) with worsening symptoms but denied active plan/intent. HIGH RISK flag was active and appropriate. Despite close clinical monitoring, evidence-based treatment, and safety planning, patient completed suicide <24 hours after clinic visit. Root Cause Analysis initiated per VHA Directive 1074. Clinical documentation review shows appropriate risk assessment and safety planning at last visit. No evidence of medical error or deviation from standard of care. Flag inactivated at time of death per protocol. Suicide Prevention Team notified, psychological autopsy scheduled, family support services offered.',
     '528'),

    -- ========================================================================
    -- Patient 1032: DRUG SEEKING BEHAVIOR (AssignmentSID 19) - INACTIVE
    -- ========================================================================
    (19, 1032, '2024-02-20 16:00:00', 1, 'NEW ASSIGNMENT',
     34568, 'Dr. Mark Johnson', 89013, 'Dr. Laura Martinez (Chief of Staff)',
     910000,
     N'Drug-seeking behavior identified. Patient requested early opioid refills multiple times, reported "lost prescriptions" twice in one month. Referral to Addiction Medicine. Controlled substance agreement implemented with pill counts and UDS monitoring.',
     '589'),

    (19, 1032, '2024-05-18 10:00:00', 2, 'CONTINUE',
     34568, 'Dr. Mark Johnson', 89013, 'Dr. Laura Martinez (Chief of Staff)',
     910100,
     N'Patient initially resistant to addiction treatment but now engaged. Transitioned to buprenorphine MAT program. Behavior improved with structure and support. Continue flag during MAT stabilization.',
     '589'),

    (19, 1032, '2024-08-25 15:30:00', 3, 'INACTIVATE',
     34568, 'Dr. Mark Johnson', 89013, 'Dr. Laura Martinez (Chief of Staff)',
     910200,
     N'Patient successfully stabilized on MAT for 3 months. No drug-seeking behavior observed. Compliant with treatment plan, negative UDS results, engaged in counseling. Patient demonstrates understanding of recovery process and commitment to treatment. Flag inactivated - patient doing well in MAT program.',
     '589');
GO
