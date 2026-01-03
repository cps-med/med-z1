-- =============================================
-- Insert Data: TIU.TIUDocumentText
-- Description: Clinical note text content (120 notes with SOAP format)
-- Author: Claude Code
-- Date: 2026-01-02
-- Note: All clinical content is synthetic and does not contain real PHI/PII
-- Note: Apostrophes are properly escaped (doubled) for SQL Server
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Insert clinical note text content
INSERT INTO TIU.TIUDocumentText (TIUDocumentSID, DocumentText, TextLength)
VALUES
    -- Progress Notes (SOAP format) - Patient 1001 (ICN100001)
    (50001, 'SUBJECTIVE: Patient presents for routine follow-up of hypertension and diabetes mellitus type 2. Reports good medication compliance. Blood pressure log shows values ranging 128-138/78-84 mmHg over past 2 weeks. Fasting glucose readings 110-125 mg/dL. Denies chest pain, shortness of breath, or peripheral edema. No hypoglycemic episodes. Diet adherence good. Walking 20 minutes daily.

OBJECTIVE: Vital Signs: BP 132/80, HR 72, RR 14, Temp 98.4 degrees F, SpO2 98% RA. Wt 185 lbs (unchanged). General: Alert, well-appearing, no distress. CV: RRR, no murmurs. Lungs: CTA bilaterally. Extremities: No edema, pulses 2+ bilaterally.

Labs (drawn today): Glucose 118 mg/dL, HbA1c 6.8% (improved from 7.2% 3 months ago), Creatinine 1.0 mg/dL, K+ 4.2 mEq/L.

ASSESSMENT:
1. Hypertension - well controlled on current regimen
2. Diabetes mellitus type 2 - improved glycemic control, HbA1c at goal
3. Hyperlipidemia - on statin therapy

PLAN:
1. Continue current medications: Lisinopril 20mg daily, Metformin 1000mg BID, Atorvastatin 40mg daily
2. Repeat basic metabolic panel and lipid panel in 3 months
3. Continue lifestyle modifications: diet, exercise
4. Return to clinic in 3 months or PRN
5. Patient educated on signs/symptoms of hypoglycemia and hyperglycemia
6. Discussed importance of medication compliance and blood pressure monitoring

Follow-up appointment scheduled for March 2026.', 1255),

    (50002, 'CARDIOLOGY PROGRESS NOTE

SUBJECTIVE: 68-year-old male with history of CAD status post PCI to LAD 2023, presents for routine cardiology follow-up. Reports occasional chest tightness with exertion, resolves with rest. No chest pain at rest. No palpitations, syncope, or near-syncope. Compliant with dual antiplatelet therapy. Walking tolerance about 2 blocks before mild dyspnea.

OBJECTIVE: BP 128/76, HR 68 regular, SpO2 97% RA. JVP normal. Cardiac exam: RRR, no murmurs, rubs, or gallops. Lungs clear. Extremities warm, no edema.

Recent stress test (12/15/25): Negative for reversible ischemia, functional capacity 7.5 METs.
Echo (11/20/25): EF 55%, no wall motion abnormalities, trivial MR.

ASSESSMENT:
1. Coronary artery disease, stable - status post PCI LAD
2. Chest discomfort with exertion - likely musculoskeletal, reassuring stress test
3. Hypertension - well controlled

PLAN:
1. Continue aspirin 81mg daily, clopidogrel 75mg daily
2. Continue metoprolol 50mg BID, atorvastatin 80mg daily
3. Reassured patient regarding benign nature of current symptoms
4. Continue cardiac rehabilitation program
5. Follow-up 6 months
6. Call office if symptoms worsen or change in character

Next cardiology visit June 2026.', 1122),

    (50003, 'CARDIOLOGY CONSULT

REASON FOR CONSULT: Evaluate for coronary artery disease

HISTORY OF PRESENT ILLNESS: 68-year-old male veteran presents with 3-month history of substernal chest pressure with moderate exertion (climbing stairs, brisk walking). Chest discomfort described as pressure/heaviness, rated 4-5/10, no radiation. Relieved with rest within 5 minutes. No associated diaphoresis, nausea, or dyspnea. No symptoms at rest. Denies orthopnea or PND.

PAST MEDICAL HISTORY:
- Hypertension x 10 years
- Hyperlipidemia x 8 years
- Type 2 diabetes mellitus x 5 years
- Former smoker (quit 2020, 30 pack-year history)

MEDICATIONS: Lisinopril 20mg daily, Metformin 1000mg BID, Atorvastatin 40mg daily

FAMILY HISTORY: Father with MI at age 62

PHYSICAL EXAMINATION:
Vitals: BP 138/82, HR 74, RR 14, SpO2 98%
General: Well-appearing, no acute distress
CV: RRR, normal S1/S2, no murmurs
Lungs: Clear to auscultation bilaterally
Extremities: No edema, distal pulses 2+

DIAGNOSTIC DATA:
ECG: Normal sinus rhythm, no ST-T changes, old inferior Q waves
Lipid panel: Total chol 180, LDL 95, HDL 42, TG 165

ASSESSMENT: Likely stable angina pectoris, high pretest probability for obstructive CAD given age, risk factors, and symptom description.

RECOMMENDATIONS:
1. Stress myocardial perfusion imaging to assess for inducible ischemia
2. Start aspirin 81mg daily, metoprolol 25mg BID
3. Increase atorvastatin to 80mg daily
4. If stress test positive, will need cardiac catheterization
5. Aggressive risk factor modification: smoking cessation counseling (patient already quit), diabetes management, BP control
6. Will follow up after stress test results available
7. Educated patient on calling 911 for prolonged or worsening chest pain

Thank you for this consult. Will co-manage with primary care.

Electronically signed: Dr. Emily Johnson, MD, Cardiology', 1876),

    (50004, 'SUBJECTIVE: Patient returns for follow-up of chronic back pain. Currently managed with physical therapy and NSAIDs. Reports pain improved from 7/10 to 4/10 with PT exercises. No radicular symptoms. Able to perform ADLs with minimal difficulty.

OBJECTIVE: BP 130/78, HR 70. Musculoskeletal: Lumbar ROM slightly limited, no paraspinal tenderness, negative straight leg raise bilaterally, strength 5/5 lower extremities, sensation intact.

ASSESSMENT: Chronic mechanical low back pain, improving with conservative management.

PLAN: Continue physical therapy 2x weekly for 4 more weeks. Continue naproxen 500mg BID with food. Avoid prolonged sitting/standing. Return PRN if symptoms worsen. Consider lumbar MRI if no improvement in 6 weeks.', 651),

    (50005, 'PRIMARY CARE NOTE

SUBJECTIVE: Annual wellness visit. Patient feeling well overall. Denies new symptoms. Medications well-tolerated. No hospitalizations or ER visits since last visit. Up to date with preventive care. Nonsmoker, occasional alcohol use (1-2 drinks/week).

OBJECTIVE: Vitals: BP 124/76, HR 68, BMI 27.2. General: Alert, healthy-appearing. HEENT: Normocephalic, PERRL, TMs clear. CV: RRR, no murmurs. Lungs: CTA. Abd: Soft, non-tender. Ext: No edema.

ASSESSMENT:
1. Health maintenance visit - age 45
2. Hypertension - well controlled
3. Overweight - BMI 27.2

PLAN:
1. Preventive care: Flu vaccine administered today, updated tetanus (Td)
2. Screening: Ordered lipid panel, fasting glucose, TSH
3. Counseling: Diet and exercise for weight management, discussed DASH diet
4. Continue lisinopril 10mg daily
5. Schedule colonoscopy (patient now age 45, average risk)
6. Return to clinic in 12 months for annual exam or PRN

Patient verbalized understanding and agreement with plan.', 967),

    (50006, 'CHEST X-RAY REPORT

EXAM: Chest X-Ray, PA and Lateral
INDICATION: Cough and fever

TECHNIQUE: Frontal and lateral radiographs of the chest

COMPARISON: Prior chest x-ray dated 08/15/2025

FINDINGS:
Lungs: There is a focal area of increased opacity in the right lower lobe, consistent with pneumonic consolidation. No pleural effusion or pneumothorax. The left lung is clear.

Heart: Normal size and contour. Cardiomediastinal silhouette is unremarkable.

Bones: No acute osseous abnormality.

IMPRESSION:
Right lower lobe pneumonia. Correlate clinically and treat appropriately. Follow-up imaging after treatment to document resolution is recommended.

Reported by: Dr. Robert Chen, MD, Radiology
Date: 12/15/2025 16:45', 721),

    (50007, 'SUBJECTIVE: Patient presents with acute onset cough x 3 days, productive of yellow sputum. Associated fever (max temp 101.2 degrees F), chills, and mild shortness of breath. Denies chest pain or hemoptysis. No recent sick contacts.

OBJECTIVE: T 100.8 degrees F, BP 118/72, HR 88, RR 18, SpO2 94% RA. General: Mild distress with coughing. Lungs: Decreased breath sounds and crackles in right lower lung base. Labs: WBC 14.2, CXR shows RLL infiltrate.

ASSESSMENT: Community-acquired pneumonia, right lower lobe

PLAN: Start azithromycin 500mg x 1, then 250mg daily x 4 days. Supportive care: rest, fluids, acetaminophen for fever. Return to clinic in 3 days or sooner if worsening. Call if temp greater than 103 degrees F, severe SOB, or chest pain. Follow-up CXR in 6 weeks to document resolution.', 753),

    (50008, 'SPECIALTY CLINIC NOTE - ORTHOPEDICS

SUBJECTIVE: 45-year-old male presents with right knee pain x 6 months, worse with activity. Pain described as aching, located medial joint line. No history of acute injury. Pain interferes with recreational basketball. No locking or giving way. Tried ibuprofen with minimal relief.

OBJECTIVE: Vitals stable. Right knee exam: No effusion, full ROM, neg McMurray, neg Lachman, tenderness to palpation medial joint line. Valgus stress test mildly positive. X-rays show mild medial joint space narrowing, small osteophytes.

ASSESSMENT: Degenerative joint disease, right knee - mild. Medial meniscus pathology possible.

PLAN:
1. Trial of physical therapy x 6 weeks - focus on quadriceps strengthening
2. Activity modification - avoid high-impact activities temporarily
3. Consider intra-articular corticosteroid injection if no improvement
4. May need MRI if persistent symptoms despite conservative care
5. Discussed long-term management options including weight loss, bracing

RTC 6 weeks after PT.', 941),

    (50009, 'SUBJECTIVE: Routine DM follow-up. Blood glucose readings running 100-130 fasting. Denies hypoglycemic episodes. Diet compliance good. Regular exercise 3-4x/week. Feet exam at home shows no wounds.

OBJECTIVE: BP 126/78, Wt 178 lbs (-3 lbs since last visit). A1C 6.5% (target less than 7%). Foot exam: No ulcers, monofilament sensation intact bilaterally, pedal pulses palpable.

ASSESSMENT: Type 2 diabetes mellitus - well controlled

PLAN: Continue current regimen. Repeat A1C in 3 months. Annual diabetic eye exam due - referral placed to ophthalmology. Continue metformin 1000mg BID. Discussed diabetic foot care. RTC 3 months.', 599),

    (50010, 'NEPHROLOGY CONSULT

REASON FOR CONSULT: Chronic kidney disease, progressive

HISTORY: 68-year-old male with CKD stage 3b (baseline Cr 1.8-2.0) due to diabetic nephropathy and hypertensive nephrosclerosis. Recent labs show Cr 2.4, up from 2.0 three months ago. No acute symptoms. Urine output normal. No hematuria or dysuria. Denies NSAIDs use.

PAST MEDICAL HISTORY:
- CKD stage 3b
- Type 2 diabetes x 15 years
- Hypertension x 20 years
- Diabetic retinopathy

MEDICATIONS: Lisinopril 40mg daily, metformin 500mg BID, insulin glargine 30 units qHS, furosemide 20mg daily

PHYSICAL EXAM: BP 142/86, trace bilateral pedal edema, otherwise unremarkable

LABS:
Cr 2.4 (eGFR 28), BUN 42, K+ 5.2, Phos 4.8, Ca 8.9, albumin 3.8
UA: 2+ protein, no RBC, no WBC
24-hour urine protein: 2.8 grams

ASSESSMENT:
1. CKD stage 4 (eGFR 28), progressive - diabetic nephropathy, hypertensive nephrosclerosis
2. Hyperkalemia, mild
3. Nephrotic-range proteinuria
4. Hypertension, suboptimally controlled

RECOMMENDATIONS:
1. Discontinue metformin (contraindicated eGFR less than 30)
2. Start losartan 50mg daily for proteinuria reduction and BP control
3. Dietary: Low potassium diet, protein restriction 0.8 g/kg/day
4. Hold lisinopril, will switch to losartan
5. Increase furosemide to 40mg daily for edema
6. Renal diet education with dietitian
7. Repeat labs in 2 weeks (BMP, CBC)
8. Discussed progression of CKD, potential need for dialysis in future
9. Will follow closely in nephrology clinic every 3 months
10. Consider renal biopsy if unexplained rapid decline

Thank you for this consult.

Electronically signed: Dr. Sarah Martinez, MD, Nephrology', 1689),

    (50011, 'SUBJECTIVE: Post-operative follow-up for inguinal hernia repair (12/1/25). Incision healing well, no drainage or redness. Pain well-controlled with acetaminophen. Tolerating regular diet. Bowel movements normal.

OBJECTIVE: Vitals stable, afebrile. Incision: Clean, dry, intact, no erythema or drainage. Abdomen soft, non-tender.

ASSESSMENT: Post-op day 2 inguinal hernia repair - uncomplicated

PLAN: Continue current pain management. Activity restrictions: No heavy lifting greater than 10 lbs x 4 weeks. Incision care reviewed. Sutures will dissolve. Return to clinic in 2 weeks for wound check. Call if fever, increasing pain, or wound concerns. Cleared to return to light work in 1 week.', 640),

    (50012, 'DISCHARGE SUMMARY

ADMISSION DATE: 11/29/2025
DISCHARGE DATE: 12/01/2025

ADMITTING DIAGNOSIS: Community-acquired pneumonia

DISCHARGE DIAGNOSIS:
1. Community-acquired pneumonia, right lower lobe - resolved
2. Type 2 diabetes mellitus - stable
3. Hypertension - stable

HOSPITAL COURSE:
68-year-old male admitted with fever, productive cough, and hypoxemia (SpO2 88% RA). Chest x-ray confirmed right lower lobe infiltrate. Started on IV ceftriaxone and azithromycin. Blood cultures: no growth. Respiratory status improved significantly by hospital day 2. Switched to oral antibiotics on day 2. Patient afebrile x 24 hours, SpO2 greater than 95% on room air at discharge.

PROCEDURES: None

DISCHARGE MEDICATIONS:
1. Azithromycin 250mg PO daily x 4 days (to complete 5-day course)
2. Lisinopril 20mg PO daily
3. Metformin 1000mg PO BID
4. Atorvastatin 40mg PO daily

DISCHARGE INSTRUCTIONS:
- Complete full course of antibiotics
- Rest and increase oral fluids
- Follow up with primary care in 1 week
- Return to ED if fever recurs, worsening shortness of breath, or chest pain
- Follow-up chest x-ray in 6 weeks to document resolution
- No smoking

FOLLOW-UP: Primary care clinic appointment 12/08/2025

DISCHARGE CONDITION: Stable, afebrile, SpO2 96% room air

Discharge summary completed by: Dr. Jennifer Smith, MD
Electronically signed: 12/01/2025 18:00', 1298),

    -- Additional Progress Notes - Patient 1001 continuing
    (50013, 'SUBJECTIVE: Established patient with COPD presents for routine follow-up. Using albuterol inhaler 2-3 times daily, no recent exacerbations. Chronic cough productive of clear sputum. No fever or hemoptysis. Quit smoking 2 years ago.

OBJECTIVE: SpO2 95% RA. Lungs: Prolonged expiratory phase, scattered wheezes, no crackles. PFTs (last month): FEV1 55% predicted.

ASSESSMENT: COPD, moderate - stable

PLAN: Continue tiotropium daily, albuterol PRN. Influenza and pneumococcal vaccines up to date. Discussed pulmonary rehabilitation referral. RTC 3 months or PRN for exacerbation. Provided COPD action plan.', 524),

    (50014, 'SUBJECTIVE: Patient with history of depression presents for medication management. Currently on sertraline 100mg daily x 6 months. Reports mood improved, PHQ-9 score today: 6 (from baseline 18). Sleep improved, energy better. No SI/HI. Tolerating medication well, no side effects.

OBJECTIVE: Alert, cooperative, appropriate affect. Mood described as pretty good overall. PHQ-9: 6

ASSESSMENT: Major depressive disorder - in remission on current treatment

PLAN: Continue sertraline 100mg daily. Continue psychotherapy with clinic counselor. RTC 3 months for medication management. Crisis resources reviewed. Call clinic or 988 if worsening symptoms or SI.', 588),

    (50015, 'PSYCHIATRY CONSULT

REASON FOR CONSULTATION: Depression screening positive, medication management

HISTORY OF PRESENT ILLNESS: 55-year-old male veteran referred for evaluation of depressive symptoms. Reports low mood x 6 months following job loss. Symptoms: Anhedonia, decreased energy, poor concentration, insomnia, feelings of worthlessness. Denies SI/HI/AVH. No prior psychiatric history. No current psychotherapy.

PAST PSYCHIATRIC HISTORY: None

SUBSTANCE USE: Denies alcohol/drug use. Former smoker.

MENTAL STATUS EXAM:
Appearance: Casually dressed, good hygiene
Behavior: Cooperative
Speech: Normal rate and volume
Mood: Depressed
Affect: Dysthymic, congruent
Thought process: Linear, goal-directed
Thought content: No SI/HI/delusions
Perception: No AVH
Cognition: Alert, oriented x 3
Insight: Good
Judgment: Intact

PHQ-9 SCORE: 18 (moderately severe depression)

ASSESSMENT: Major depressive disorder, single episode, moderate severity

RECOMMENDATIONS:
1. Start sertraline 50mg daily, increase to 100mg after 2 weeks
2. Refer to VA psychotherapy program - CBT recommended
3. Safety planning - no access to firearms, crisis line 988
4. Follow up psychiatry clinic 4 weeks to assess medication response
5. Monitor for worsening symptoms or emergence of SI
6. Discussed side effects of SSRI: GI upset, headache, sexual dysfunction
7. Emphasize medication takes 4-6 weeks for full effect
8. Encourage exercise, social engagement, sleep hygiene

Will co-manage with primary care. Patient agrees with plan.

Electronically signed: Dr. Michael Thompson, MD, Psychiatry', 1567),

    (50016, 'SUBJECTIVE: Patient presents for pre-operative clearance for elective knee arthroscopy scheduled next week. Feels well, no active medical issues. No chest pain, SOB, or other symptoms.

OBJECTIVE: BP 128/76, HR 68, RR 14, SpO2 99%. Physical exam unremarkable. ECG: NSR, no acute changes. CMP: WNL.

ASSESSMENT: Preoperative medical clearance - low risk

PLAN: Cleared for surgery. Continue home medications through surgery except hold aspirin 5 days before. NPO after midnight. Patient counseled on post-op expectations.', 471),

    (50017, 'CT SCAN ABDOMEN/PELVIS REPORT

EXAM: CT Abdomen and Pelvis with IV Contrast
INDICATION: Abdominal pain

TECHNIQUE: Multidetector CT of the abdomen and pelvis after administration of IV contrast. No oral contrast given.

COMPARISON: None

FINDINGS:
Liver: Normal size and attenuation. No focal lesion.
Gallbladder: Normal, no stones or wall thickening.
Pancreas: Normal size and attenuation.
Spleen: Normal.
Kidneys: Normal size bilaterally. No hydronephrosis or stones.
Adrenals: Normal.
GI Tract: Mild sigmoid diverticulosis without evidence of diverticulitis.
Bladder: Normal.
Pelvis: Unremarkable.
Vessels: Aorta and IVC normal caliber, no aneurysm.
Lymph Nodes: No pathologic adenopathy.
Bones: No aggressive osseous lesion. Mild degenerative changes lumbar spine.

IMPRESSION:
1. No acute intra-abdominal pathology to explain patient symptoms
2. Sigmoid diverticulosis without acute inflammation
3. Consider functional GI disorder

Reported by: Dr. Lisa Park, MD, Radiology
Date: 11/10/2025 16:15', 1074),

    (50018, 'SUBJECTIVE: Patient with history of AF on warfarin presents for anticoagulation management. INR checked today. No bleeding or bruising. Diet consistent. No new medications.

OBJECTIVE: INR 2.8 (target 2-3). Vitals stable. No signs of bleeding.

ASSESSMENT: Atrial fibrillation on warfarin - therapeutic INR

PLAN: Continue warfarin 5mg daily. Repeat INR in 4 weeks. Reviewed bleeding precautions. Patient has good understanding of warfarin therapy.', 382),

    (50019, 'NEUROLOGY CONSULT

REASON FOR CONSULT: Evaluation of chronic headaches

HISTORY OF PRESENT ILLNESS: 45-year-old male with 5-year history of episodic headaches, increasing in frequency over past 6 months. Headaches described as bilateral, throbbing, frontotemporal, severity 6-7/10. Associated photophobia and phonophobia. Duration 4-12 hours. No aura, no focal neurologic symptoms. Frequency now 2-3 times per week. Triggered by stress, lack of sleep. Partial relief with ibuprofen. No nausea/vomiting. Never evaluated by neurology previously.

PAST MEDICAL HISTORY: Hypertension

FAMILY HISTORY: Mother with migraines

NEUROLOGIC EXAM:
Mental status: Alert, oriented x 3, normal speech and language
Cranial nerves: II-XII intact
Motor: 5/5 strength all extremities
Sensory: Intact to light touch and pinprick
Reflexes: 2+ symmetric, toes downgoing
Coordination: Normal finger-to-nose, heel-to-shin
Gait: Normal

ASSESSMENT: Migraine without aura, chronic - transformed from episodic

RECOMMENDATIONS:
1. Start topiramate 25mg nightly, increase by 25mg weekly to target 100mg daily for prophylaxis
2. Sumatriptan 100mg PO for acute attacks, max 200mg/day
3. Headache diary to track triggers, frequency, response to treatment
4. Lifestyle modifications: Regular sleep schedule, stress reduction, avoid triggers
5. Consider MRI brain if red flags develop (new onset after age 50, focal neuro signs, sudden severe headache)
6. Follow up neurology clinic 6 weeks to assess response
7. Counseled on medication side effects: topiramate can cause paresthesias, weight loss, kidney stones

Thank you for allowing me to participate in this patient care.

Electronically signed: Dr. David Kim, MD, Neurology', 1548),

    (50020, 'SUBJECTIVE: Diabetic foot exam visit. Patient reports no foot pain, no wounds. Checking feet daily at home as instructed. Wearing diabetic shoes.

OBJECTIVE: Bilateral foot exam: Skin intact, no calluses or ulcers. Monofilament sensation intact all sites. Pedal pulses 2+ bilaterally. No deformities. Toenails trimmed appropriately.

ASSESSMENT: Diabetic foot surveillance - no abnormalities

PLAN: Continue daily foot inspections. Annual diabetic foot exam complete. Reinforced importance of proper footwear and nail care. Return PRN for any foot concerns or wounds.', 500),

    (50021, 'SUBJECTIVE: Patient with history of BPH presents with urinary symptoms: Frequency, nocturia x 3, weak stream, hesitancy. No hematuria or pain. Symptoms gradually worsening x 6 months. IPSS score: 18 (moderate symptoms).

OBJECTIVE: Vitals stable. Abdomen: No suprapubic tenderness, no palpable bladder. Rectal: Prostate moderately enlarged, smooth, no nodules. PSA 2.8 ng/mL (age-appropriate).

ASSESSMENT: Benign prostatic hyperplasia with moderate LUTS

PLAN: Start tamsulosin 0.4mg daily. Trial for 4-6 weeks. Discussed side effects: orthostatic hypotension, retrograde ejaculation. May add 5-alpha reductase inhibitor if inadequate response. Urology referral if no improvement or development of retention. RTC 6 weeks.', 658),

    (50022, 'DISCHARGE SUMMARY

ADMISSION DATE: 10/13/2025
DISCHARGE DATE: 10/15/2025

ADMITTING DIAGNOSIS: Acute decompensated heart failure

DISCHARGE DIAGNOSES:
1. Acute on chronic systolic heart failure, EF 30%
2. Volume overload
3. Hypertension
4. Chronic kidney disease stage 3

HOSPITAL COURSE:
72-year-old male admitted with dyspnea, orthopnea, bilateral lower extremity edema. Home medication: Lisinopril, furosemide. Exam significant for elevated JVP, bilateral crackles, 3+ pitting edema. BNP 1850. CXR: pulmonary edema. Treated with IV furosemide bolus followed by continuous infusion. Diuresed 3L negative balance over 48 hours. Dyspnea resolved, edema improved. Echo: EF 30%, LV dilation, moderate MR. Cr stable.

Transitioned to oral diuretics. Patient euvolemic at discharge.

DISCHARGE MEDICATIONS:
1. Furosemide 80mg PO BID (increased from 40mg daily)
2. Lisinopril 20mg PO daily
3. Carvedilol 6.25mg PO BID (new)
4. Potassium chloride 20mEq PO daily

DISCHARGE INSTRUCTIONS:
- Daily weights - call if weight gain greater than 3 lbs in 24 hours or greater than 5 lbs in 1 week
- Fluid restriction 2L per day
- Low sodium diet (less than 2g/day)
- Monitor for worsening dyspnea, chest pain, edema

FOLLOW-UP:
- Cardiology clinic 1 week
- Heart failure clinic enrollment
- Repeat echo in 3 months

DISCHARGE CONDITION: Stable, euvolemic, SpO2 95% room air

Discharge summary completed by: Dr. Jennifer Smith, MD', 1395),

    (50023, 'SUBJECTIVE: Annual wellness visit, age 65. Patient feels well. No new medical concerns. Medications taken as prescribed. Up to date with colonoscopy (2023). No family history changes.

OBJECTIVE: BP 122/74, HR 64, BMI 26.5. Physical exam unremarkable.

ASSESSMENT: Health maintenance - age 65, Medicare wellness visit

PLAN: Updated problem list and medication list. Ordered: Lipid panel, HbA1c, TSH, CBC, CMP. Flu vaccine given. Shingrix series initiated. Discussed advance directives. Schedule follow-up after labs result.', 439),

    (50024, 'PRIMARY CARE NOTE

SUBJECTIVE: Follow-up for newly diagnosed type 2 diabetes. Patient started metformin 500mg BID 4 weeks ago, tolerating well. Checking blood sugars: Fasting 110-130, post-prandial 140-160. Diet changes implemented: Reduced carbs, portion control. Walking 30 min 5x/week.

OBJECTIVE: BP 126/78, Wt 192 lbs (down 5 lbs from last visit). HbA1c 7.2% (baseline 8.4%).

ASSESSMENT:
1. Type 2 diabetes mellitus, newly diagnosed - improving
2. Obesity - weight loss in progress

PLAN:
1. Increase metformin to 1000mg BID
2. Continue lifestyle modifications
3. Diabetic education class referral placed
4. Ophthalmology referral for diabetic eye exam
5. Monofilament foot exam today: Normal
6. Repeat HbA1c in 3 months, target less than 7%
7. Discussed hypoglycemia symptoms and prevention
8. Return 3 months or PRN', 774),

    (50025, 'SUBJECTIVE: Patient presents with right shoulder pain x 2 weeks after lifting heavy box. Pain with overhead activities and reaching behind back. No numbness or tingling. Taking ibuprofen with moderate relief.

OBJECTIVE: Right shoulder: Limited abduction (100 degrees), external rotation painful. Positive Hawkins and Neer impingement signs. Strength 4+/5 supraspinatus, normal deltoid. No atrophy.

ASSESSMENT: Right shoulder impingement syndrome, likely rotator cuff tendinitis

PLAN: Physical therapy referral - focus on rotator cuff strengthening and scapular stabilization. Continue NSAIDs. Ice after activities. Activity modification. Consider corticosteroid injection if no improvement after 6 weeks PT. RTC 6 weeks.', 646),

    (50026, 'CHEST X-RAY REPORT

EXAM: Chest X-Ray, 2 views
INDICATION: Follow-up pneumonia

TECHNIQUE: PA and lateral chest radiographs

COMPARISON: 09/20/2025

FINDINGS:
Lungs: Previous right lower lobe opacity has resolved. Lungs are now clear bilaterally. No new infiltrate, effusion, or pneumothorax.
Heart: Normal size.
Mediastinum: Unremarkable.
Bones: No acute abnormality.

IMPRESSION:
Resolution of previously seen right lower lobe pneumonia. No acute cardiopulmonary disease.

Reported by: Dr. Robert Chen, MD, Radiology
Date: 09/28/2025 17:00', 570),

    (50027, 'SUBJECTIVE: Patient with history of GERD presents with breakthrough heartburn despite omeprazole 20mg daily. Symptoms: Burning chest pain 3-4x/week, worse after meals and lying down. No dysphagia, odynophagia, or weight loss.

OBJECTIVE: Vitals stable. Abdomen soft, non-tender, no masses. Epigastric area non-tender.

ASSESSMENT: Gastroesophageal reflux disease, inadequately controlled on current therapy

PLAN: Increase omeprazole to 40mg daily before breakfast. Lifestyle modifications reviewed: Avoid late meals, elevate head of bed, avoid trigger foods (spicy, acidic, fatty). Trial for 4 weeks. If persistent, consider EGD. RTC 4 weeks.', 569),

    (50028, 'CARDIOLOGY CONSULT

REASON FOR CONSULT: Pre-operative cardiac risk assessment

HISTORY: 70-year-old male scheduled for elective total knee replacement. History of CAD status post CABG 2018 (LIMA to LAD, SVG to OM). No recent angina. Functional capacity: Can walk 1 block, climb 1 flight stairs without symptoms. On appropriate cardiac medications.

CARDIAC HISTORY:
- CAD status post CABG 2018
- Hypertension
- Hyperlipidemia
- Remote MI (2017)

MEDICATIONS: Aspirin 81mg, metoprolol 50mg BID, atorvastatin 80mg, lisinopril 10mg

PHYSICAL EXAM: BP 128/76, HR 62 regular. CV: RRR, no murmurs. Lungs clear. No edema.

ASSESSMENT: CAD status post CABG, stable - intermediate surgical risk for non-cardiac surgery

RECOMMENDATIONS:
1. Patient acceptable cardiac risk for planned knee surgery
2. Continue aspirin perioperatively (orthopedic surgery comfortable with this)
3. Continue beta blocker perioperatively
4. Hold lisinopril morning of surgery, resume post-op
5. Ensure adequate beta blockade through perioperative period (HR goal 60-70)
6. Telemetry monitoring first 24 hours post-op
7. Troponin on post-op day 1 and 2
8. Early mobilization post-operatively
9. Reinforce smoking cessation (if applicable)

Thank you for this consultation.

Electronically signed: Dr. Emily Johnson, MD, Cardiology', 1256),

    (50029, 'SUBJECTIVE: Patient presents for annual physical. Feeling well. No new symptoms. Medications: Lisinopril 10mg daily for HTN. Regular exercise 3x/week. Denies tobacco, occasional alcohol.

OBJECTIVE: BP 124/78, HR 68, BMI 24.8. General: Well-appearing. HEENT, CV, Lungs, Abd: All normal. Labs: Lipids WNL, glucose 92, Cr 0.9, CBC normal.

ASSESSMENT: Annual health maintenance, well-controlled HTN

PLAN: Continue lisinopril. Flu vaccine given. Colonoscopy due (age 50) - referral placed. Discussed lifestyle, diet. RTC 12 months.', 434),

    (50030, 'CARDIOLOGY PROGRESS NOTE

SUBJECTIVE: Patient with history of systolic heart failure (EF 35%) presents for routine follow-up. Compliant with medications and dietary sodium restriction. No dyspnea at rest. Can walk 2 blocks before mild SOB. No orthopnea or PND. Weight stable. No edema.

OBJECTIVE: BP 118/72, HR 66, JVP normal. Cardiac exam: RRR, S3 gallop present. Lungs: Clear. Extremities: No edema. BNP 280 (stable from prior 265).

ASSESSMENT:
1. Chronic systolic heart failure, NYHA class II - compensated
2. Ischemic cardiomyopathy

PLAN: Continue carvedilol 25mg BID, lisinopril 40mg daily, furosemide 40mg daily, spironolactone 25mg daily. Daily weights. Sodium restriction less than 2g/day. Cardiac rehab ongoing. ICD in place for primary prevention. RTC 3 months or PRN if symptoms worsen.', 765),

    (50031, 'SUBJECTIVE: Follow-up for chronic pain syndrome. Currently on tramadol 50mg TID PRN. Pain level average 5-6/10. Able to perform ADLs with modifications. Physical therapy helping. Denies opioid side effects.

OBJECTIVE: Vitals stable. Pain behavior appropriate. No sedation. PDMP checked: No concerning patterns.

ASSESSMENT: Chronic pain syndrome, musculoskeletal - stable

PLAN: Continue tramadol 50mg TID PRN (not exceeding 300mg/day). Continue PT 2x/week. Pain management agreement renewed. Next opioid refill in 30 days. RTC 1 month.', 472),

    (50032, 'MRI LUMBAR SPINE REPORT

EXAM: MRI Lumbar Spine without contrast
INDICATION: Low back pain, radicular symptoms

TECHNIQUE: Sagittal and axial T1, T2, and STIR sequences

COMPARISON: None

FINDINGS:
Alignment: Normal lordosis.

L3-L4: Mild disc desiccation. No significant stenosis.

L4-L5: Moderate disc desiccation and height loss. Broad-based disc bulge with superimposed right paracentral protrusion causing mild central canal stenosis and moderate right neural foraminal narrowing. Possible contact with exiting right L4 nerve root.

L5-S1: Mild disc bulge, no significant stenosis.

No fracture. Conus ends at T12-L1.

IMPRESSION:
1. L4-L5 disc protrusion with right neural foraminal stenosis - may correlate with right L5 radiculopathy
2. Mild multilevel degenerative changes

Correlation with clinical findings recommended.

Reported by: Dr. Lisa Park, MD, Radiology
Date: 07/30/2025 16:30', 897),

    (50033, 'SUBJECTIVE: Patient with osteoarthritis both knees presents for corticosteroid injection. Pain 7/10, worse with stairs and prolonged standing. Previous injection 6 months ago provided 4 months relief.

OBJECTIVE: Bilateral knee exam: Crepitus with ROM, mild effusion left knee, no warmth or erythema. ROM mildly limited by pain.

ASSESSMENT: Osteoarthritis, bilateral knees - moderate

PLAN: Performed intra-articular injection left knee (Depo-Medrol 40mg + 1% lidocaine 2mL). Aseptic technique used. Post-injection instructions given: Rest 24 hours, ice PRN, expect relief in 3-5 days. Call if fever, increasing warmth, or severe pain. Continue topical NSAIDs. RTC 4-6 months or PRN.', 598),

    (50034, 'DISCHARGE SUMMARY

ADMISSION DATE: 07/08/2025
DISCHARGE DATE: 07/10/2025

ADMITTING DIAGNOSIS: Syncope

DISCHARGE DIAGNOSES:
1. Vasovagal syncope
2. Dehydration
3. Hypertension

HOSPITAL COURSE:
45-year-old male admitted after witnessed syncopal episode at home. Patient standing in bathroom, felt lightheaded, then lost consciousness briefly. No prodrome. Quick recovery, no confusion. No incontinence or tongue biting. Exam: Orthostatic vitals positive (BP drop 25mmHg standing). Telemetry: NSR, no arrhythmias. Echo: Normal EF, no structural abnormalities. Labs: Mild dehydration. Neuro exam normal.

Diagnosed with vasovagal syncope in setting of dehydration and possible orthostatic hypotension.

DISCHARGE MEDICATIONS:
1. Lisinopril 10mg PO daily (reduced from 20mg)
2. Encourage oral hydration

DISCHARGE INSTRUCTIONS:
- Increase fluid intake
- Avoid prolonged standing
- Tilt table test if recurrent episodes
- Return to ED if recurrent syncope, chest pain, palpitations

FOLLOW-UP: Primary care 1 week, Cardiology PRN if recurrent

DISCHARGE CONDITION: Stable, ambulating

Discharge summary completed by: Dr. Jennifer Smith, MD', 1056),

    (50035, 'SUBJECTIVE: Follow-up for hypothyroidism. On levothyroxine 75mcg daily x 6 months. Energy improved. No palpitations, tremor, or hair loss. Compliant with medication on empty stomach.

OBJECTIVE: Vitals: HR 68. Thyroid: Non-palpable. TSH 2.1 mIU/L (target 0.5-4.5), Free T4 1.2 ng/dL (normal).

ASSESSMENT: Hypothyroidism - euthyroid on current dose

PLAN: Continue levothyroxine 75mcg daily. Repeat TSH in 6 months. Patient educated on importance of consistent timing and empty stomach dosing. RTC 6 months or PRN if symptoms recur.', 476),

    (50036, 'PRIMARY CARE NOTE

SUBJECTIVE: New patient visit. Recently moved to area, establishing care. History of HTN, hyperlipidemia. On atorvastatin 20mg, lisinopril 10mg daily. Feels well. No active concerns.

OBJECTIVE: BP 132/82, HR 70, BMI 28.2. Physical exam unremarkable. Med reconciliation completed.

ASSESSMENT:
1. Hypertension - on treatment
2. Hyperlipidemia - on statin
3. Overweight

PLAN: Continue current medications. Ordered fasting lipid panel, CMP. Flu vaccine given. Discussed diet and exercise for weight management. Established as primary care provider. RTC after labs result for medication adjustment if needed.', 549),

    (50037, 'SUBJECTIVE: Routine HTN follow-up. BP readings at home 120-135/75-82. No headaches, vision changes. Compliant with lisinopril 20mg daily. Regular exercise, DASH diet adherence good.

OBJECTIVE: BP 128/78, HR 68. CV exam normal.

ASSESSMENT: Hypertension - well controlled

PLAN: Continue lisinopril 20mg daily. Repeat basic metabolic panel in 6 months. Continue lifestyle modifications. RTC 6 months or PRN.', 382),

    (50038, 'NEPHROLOGY CONSULT

REASON FOR CONSULT: Microalbuminuria in diabetic patient

HISTORY: 58-year-old male with 10-year history of type 2 diabetes, recent spot urine albumin/creatinine ratio 145 mg/g (abnormal). eGFR 68 mL/min. BP slightly elevated 142/88. Currently on metformin and glipizide. Not on ACE inhibitor or ARB.

ASSESSMENT:
1. Diabetic kidney disease, early stage (albuminuria with preserved GFR)
2. Diabetes - target HbA1c less than 7% for renal protection
3. Hypertension - target BP less than 130/80 in diabetic CKD

RECOMMENDATIONS:
1. Start lisinopril 10mg daily - dual benefit for BP and proteinuria
2. Target HbA1c less than 7%
3. Repeat urine albumin/creatinine ratio in 3 months
4. Monitor potassium and creatinine 2 weeks after starting ACE inhibitor
5. Dietary: Sodium restriction less than 2g/day
6. Tight glycemic control to slow progression
7. Annual urine albumin screening
8. Will follow in nephrology clinic every 6 months

Electronically signed: Dr. Sarah Martinez, MD, Nephrology', 1016),

    (50039, 'SUBJECTIVE: Patient presents with acute bronchitis symptoms: Productive cough x 5 days, clear to yellow sputum, no fever. Mild fatigue. No SOB or chest pain. Viral URI 1 week ago.

OBJECTIVE: T 98.6 degrees F, SpO2 98% RA. Lungs: Scattered rhonchi, no wheezes or crackles. No tachypnea or respiratory distress.

ASSESSMENT: Acute bronchitis, likely viral

PLAN: Supportive care: Rest, fluids, honey for cough. Albuterol inhaler PRN if wheezing develops. Return if fever, worsening SOB, or no improvement in 7-10 days. Antibiotics not indicated for viral bronchitis.', 513),

    (50040, 'DISCHARGE SUMMARY

ADMISSION DATE: 02/03/2025
DISCHARGE DATE: 02/05/2025

ADMITTING DIAGNOSIS: Cellulitis, right lower extremity

DISCHARGE DIAGNOSIS:
1. Cellulitis, right lower extremity - improving
2. Type 2 diabetes mellitus
3. Peripheral arterial disease

HOSPITAL COURSE:
65-year-old male admitted with right lower leg erythema, warmth, swelling. Small abrasion noted. Started on IV vancomycin and ceftriaxone. Blood cultures negative. Responded well to antibiotics - erythema decreased, swelling improved. Switched to oral antibiotics on day 2.

DISCHARGE MEDICATIONS:
1. Cephalexin 500mg PO QID x 10 days (to complete 14-day course)
2. Metformin 1000mg PO BID
3. Lisinopril 20mg PO daily
4. Aspirin 81mg PO daily

DISCHARGE INSTRUCTIONS:
- Complete full antibiotic course
- Elevate leg when sitting
- Monitor for worsening redness, fever, or drainage
- Wound care: Keep clean and dry
- Follow up with primary care in 1 week

FOLLOW-UP: Primary care clinic 02/12/2025

DISCHARGE CONDITION: Stable, afebrile, cellulitis improving

Discharge summary completed by: Dr. Michael Brown, MD', 982),

    -- Patient 1002 (ICN100002) notes starting
    (50041, 'SUBJECTIVE: New diagnosis of hypertension. BP readings at pharmacy 145/92, 148/90. No symptoms. Family history of HTN. No current medications.

OBJECTIVE: BP 142/88 (repeated 138/86), HR 74, BMI 29.5. Physical exam unremarkable.

ASSESSMENT: Essential hypertension, newly diagnosed

PLAN: Start lisinopril 10mg daily. Home BP monitoring instructed. Lifestyle modifications: Low sodium diet, weight loss goal 10 lbs, regular exercise 30 min 5x/week. Labs ordered: BMP, lipids, HbA1c, TSH. RTC 4 weeks for BP recheck and lab review.', 466),

    (50042, 'PRIMARY CARE NOTE

SUBJECTIVE: Annual wellness visit. Patient age 50, healthy. No chronic conditions. Screening current except colonoscopy due.

OBJECTIVE: BP 118/74, BMI 24.2. Exam normal.

ASSESSMENT: Health maintenance age 50

PLAN: Colonoscopy referral. Flu vaccine given. Lipid panel, glucose ordered. Continue current lifestyle. RTC 12 months.', 307),

    (50043, 'CARDIOLOGY CONSULT

REASON FOR CONSULT: Palpitations

HISTORY: 55-year-old female with episodes of palpitations x 3 months. Described as heart racing, sudden onset, lasting minutes. Associated lightheadedness. No syncope or chest pain. Caffeine intake: 3 cups coffee daily.

ASSESSMENT: Likely paroxysmal supraventricular tachycardia vs. premature atrial contractions

RECOMMENDATIONS:
1. Event monitor x 30 days to capture symptoms
2. Reduce caffeine intake
3. If SVT documented, consider EP study vs. medication
4. Echocardiogram to assess structure
5. TSH to rule out hyperthyroidism
6. Follow up after event monitor results

Electronically signed: Dr. Emily Johnson, MD, Cardiology', 694),

    (50044, 'SUBJECTIVE: DM follow-up. Blood sugars 90-140. A1C improved to 6.9% from 7.5%. Diet and exercise compliance good. No hypoglycemia.

OBJECTIVE: BP 124/76, Wt 175 lbs (-8 lbs). Foot exam normal.

ASSESSMENT: Type 2 DM - improving control

PLAN: Continue metformin 1000mg BID. Repeat A1C 3 months. Annual eye exam scheduled. RTC 3 months.', 310),

    (50045, 'CHEST X-RAY REPORT

EXAM: Chest X-Ray PA/Lateral
INDICATION: Cough, fever

FINDINGS: No acute infiltrate. Heart size normal. No effusion or pneumothorax. Lungs clear.

IMPRESSION: No acute cardiopulmonary disease

Reported by: Dr. Robert Chen, MD, Radiology', 246),

    (50046, 'SUBJECTIVE: Acute pharyngitis symptoms x 3 days: Sore throat, fever (max 101 degrees F), painful swallowing. No cough or nasal congestion.

OBJECTIVE: T 100.2 degrees F. Oropharynx: Tonsillar exudate, pharyngeal erythema. Anterior cervical lymphadenopathy. Rapid strep: Positive.

ASSESSMENT: Acute streptococcal pharyngitis

PLAN: Amoxicillin 500mg TID x 10 days. Supportive care: Salt water gargles, acetaminophen for fever. Return if worsening or no improvement 48 hours.', 433),

    (50047, 'CARDIOLOGY PROGRESS NOTE

SUBJECTIVE: Post-MI follow-up (MI 9/2025). Cardiac rehab ongoing. No angina. Compliant with medications. Quit smoking post-MI.

OBJECTIVE: BP 118/72, HR 58. Exam unremarkable.

ASSESSMENT: CAD status post STEMI with PCI to RCA - stable

PLAN: Continue aspirin, ticagrelor (dual antiplatelet x 12 months), atorvastatin 80mg, metoprolol, lisinopril. Cardiac rehab ongoing. Stress test in 3 months. RTC 8 weeks.', 391),

    (50048, 'SUBJECTIVE: Follow-up for anxiety disorder. Started sertraline 6 weeks ago, now 100mg daily. Anxiety improved significantly. GAD-7 score: 5 (from 16).

OBJECTIVE: Alert, less anxious appearing. GAD-7: 5

ASSESSMENT: Generalized anxiety disorder - responding to treatment

PLAN: Continue sertraline 100mg daily. Continue therapy. RTC 3 months.', 315),

    (50049, 'DISCHARGE SUMMARY

ADMISSION: 11/27/2025
DISCHARGE: 11/29/2025

DIAGNOSIS: Acute gastroenteritis, dehydration

COURSE: 48-year-old with nausea, vomiting, diarrhea x 2 days. Dehydrated on presentation. IV fluids given. Symptoms resolved. Tolerating oral intake.

DISCHARGE MEDS: Ondansetron PRN

FOLLOW-UP: Primary care 1 week if not improved

CONDITION: Stable, tolerating PO

Completed by: Dr. Sarah Lee, MD', 391),

    (50050, 'SUBJECTIVE: Patient with chronic allergic rhinitis presents for seasonal allergy management. Symptoms: Nasal congestion, sneezing, itchy watery eyes. Worse in spring. OTC antihistamines provide minimal relief.

OBJECTIVE: Vitals normal. HEENT: Pale boggy nasal turbinates, clear rhinorrhea. Conjunctiva mildly injected.

ASSESSMENT: Allergic rhinitis, seasonal

PLAN: Start fluticasone nasal spray 2 sprays each nostril daily. Add cetirizine 10mg daily. Avoid known allergens when possible. Trial for 4 weeks. May need allergy testing if inadequate response. RTC 4 weeks or PRN.', 516),

    (50051, 'SUBJECTIVE: Follow-up for osteoporosis. On alendronate 70mg weekly x 2 years. No fractures. Tolerating medication well. Taking with full glass of water, staying upright 30 minutes. Calcium and vitamin D supplementation daily.

OBJECTIVE: Vitals normal. No acute findings.

ASSESSMENT: Osteoporosis - on treatment

PLAN: Continue alendronate 70mg weekly. Continue calcium 1200mg and vitamin D 1000 IU daily. DEXA scan in 1 year to assess treatment response. Discussed fall prevention. RTC 6 months.', 469),

    (50052, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents for medication refills. Chronic conditions stable: HTN, HLD. No new symptoms. Compliant with medications. Denies side effects.

OBJECTIVE: BP 126/78, HR 72. Exam unremarkable.

ASSESSMENT:
1. Hypertension - controlled
2. Hyperlipidemia - on statin

PLAN: Refill lisinopril 10mg daily, atorvastatin 20mg daily for 90 days. Due for annual labs - ordered lipid panel, CMP. RTC 3 months or after labs.', 404),

    (50053, 'SUBJECTIVE: Patient with IBS presents with abdominal cramping and diarrhea x 1 week. Stress at work increased recently. No blood in stool, no fever. Similar episodes in past.

OBJECTIVE: Vitals normal. Abdomen: Soft, mild diffuse tenderness, active bowel sounds, no guarding or rebound.

ASSESSMENT: Irritable bowel syndrome with diarrhea, acute flare

PLAN: Loperamide PRN for diarrhea. Dietary modifications: Low FODMAP trial. Stress management discussed. Return if worsening, blood in stool, or fever. Consider GI referral if no improvement. RTC 2 weeks.', 508),

    (50054, 'SUBJECTIVE: Routine follow-up for asthma. Using albuterol 1-2 times per week for exercise-induced symptoms. No nighttime awakenings. No recent exacerbations or ED visits. Peak flow readings stable.

OBJECTIVE: Vitals: SpO2 99% RA. Lungs: Clear bilaterally, no wheezes.

ASSESSMENT: Asthma, mild intermittent - well controlled

PLAN: Continue albuterol MDI 2 puffs PRN before exercise. Continue low-dose inhaled corticosteroid. Asthma action plan reviewed. Flu vaccine given. RTC 6 months or PRN.', 457),

    (50055, 'SUBJECTIVE: Patient presents with insomnia x 2 months. Difficulty falling asleep and staying asleep. Wakes feeling unrefreshed. Daytime fatigue affecting work. Denies snoring or witnessed apneas. Caffeine intake: 2 cups coffee AM only.

OBJECTIVE: Vitals normal. Alert but appears fatigued. Physical exam unremarkable.

ASSESSMENT: Chronic insomnia disorder

PLAN: Sleep hygiene counseling provided. Recommend regular sleep schedule, avoid screens 1 hour before bed, relaxation techniques. Trial of melatonin 3mg at bedtime. Avoid daytime naps. If no improvement, consider CBT for insomnia or sleep study. RTC 4 weeks.', 574),

    (50056, 'SUBJECTIVE: Follow-up for vitamin D deficiency. Started vitamin D3 2000 IU daily 3 months ago. Energy improved. No bone pain.

OBJECTIVE: Vitals normal. 25-OH vitamin D level: 38 ng/mL (goal greater than 30).

ASSESSMENT: Vitamin D deficiency - replete

PLAN: Continue vitamin D3 2000 IU daily for maintenance. Recheck level in 6 months. Encourage sun exposure 15-20 min daily when possible. RTC 6 months.', 371),

    (50057, 'SUBJECTIVE: Patient with history of migraines presents with acute headache x 4 hours. Throbbing, left-sided, 8/10 severity. Associated photophobia and nausea. Took sumatriptan 100mg at home 2 hours ago with minimal relief.

OBJECTIVE: BP 128/82, HR 76. Neurologic exam: Cranial nerves intact, no focal deficits. Appears in moderate distress from pain.

ASSESSMENT: Acute migraine, refractory to initial abortive therapy

PLAN: IV fluids 1L NS, IV ketorolac 30mg, IV metoclopramide 10mg given. Observed in clinic 1 hour - headache improved to 3/10. Discharged home. Follow up with neurology if increasing frequency. Headache diary recommended. RTC PRN.', 655),

    (50058, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents requesting FMLA paperwork for knee surgery scheduled next month. Currently working full-time. Surgery: Right knee arthroscopy. Expected recovery 6-8 weeks.

OBJECTIVE: Vitals normal. Right knee exam: Effusion, limited ROM due to pain.

ASSESSMENT: Right knee degenerative joint disease requiring surgery

PLAN: FMLA paperwork completed for 8 weeks medical leave starting surgery date. Provided copy to patient. Surgery clearance completed previously. RTC post-op for wound check and recovery assessment.', 498),

    (50059, 'SUBJECTIVE: Follow-up for newly diagnosed hyperlipidemia. Started atorvastatin 20mg daily 6 weeks ago. No muscle pain or weakness. Tolerating well.

OBJECTIVE: Vitals normal. Repeat lipid panel: Total chol 165, LDL 88 (down from 142), HDL 48, TG 145.

ASSESSMENT: Hyperlipidemia - responding to statin therapy, at LDL goal

PLAN: Continue atorvastatin 20mg daily. Recheck lipids in 3 months. Lifestyle modifications: Mediterranean diet, regular exercise. Monitor for muscle symptoms. RTC 3 months.', 451),

    (50060, 'SUBJECTIVE: Patient presents for tobacco cessation counseling. Smoking 1 pack per day x 25 years. Motivated to quit due to upcoming grandchild birth. Tried quitting before without medications.

OBJECTIVE: Vitals: BP 134/84, HR 78. Lung exam: Decreased breath sounds bilaterally, no wheezes.

ASSESSMENT: Tobacco use disorder, motivated for cessation

PLAN: Discussed nicotine replacement options. Started varenicline 0.5mg daily x 3 days, then 0.5mg BID x 4 days, then 1mg BID. Set quit date 2 weeks from today. Quitline referral provided. Discussed side effects: nausea, vivid dreams, mood changes. RTC 2 weeks.', 555),

    (50061, 'SUBJECTIVE: Established patient with obesity presents for weight management. Current BMI 35. Ready to make lifestyle changes. Diet: High carbs, large portions, frequent fast food. Exercise: Minimal, sedentary job.

OBJECTIVE: Wt 245 lbs, Ht 66 inches, BMI 35.2. BP 138/86. Labs: HbA1c 5.9% (prediabetes), lipids borderline high.

ASSESSMENT:
1. Obesity class 2
2. Prediabetes
3. Hypertension

PLAN: Dietary referral for medical nutrition therapy. Start food diary. Goal: 1-2 lbs per week weight loss. Exercise prescription: 30 min moderate activity 5 days/week. Consider weight loss medication if lifestyle modifications insufficient. Repeat HbA1c in 3 months. RTC 4 weeks.', 647),

    (50062, 'SUBJECTIVE: Patient with eczema presents with flare. Itchy rash bilateral hands and forearms x 1 week. Using moisturizer, no improvement. Recent exposure to new dish soap.

OBJECTIVE: Skin exam: Erythematous, dry, scaly plaques bilateral dorsal hands and forearms. No weeping or secondary infection.

ASSESSMENT: Atopic dermatitis, acute flare - likely irritant contact component

PLAN: Triamcinolone 0.1% cream BID x 2 weeks to affected areas. Moisturize frequently with fragrance-free cream. Avoid irritant (new soap). Wear gloves for wet work. If no improvement, consider patch testing. RTC 2 weeks or PRN.', 541),

    (50063, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents with fatigue x 3 months. Excessive daytime sleepiness despite 8 hours sleep nightly. Snoring reported by spouse. Witnessed apneas. Morning headaches. BMI 38.

OBJECTIVE: BP 142/88, BMI 38. HEENT: Crowded oropharynx, Mallampati class 3. Neck circumference 18 inches.

ASSESSMENT: Suspected obstructive sleep apnea

PLAN: Referral for sleep study (polysomnography). Sleep hygiene counseling. Discussed CPAP therapy if OSA confirmed. Weight loss strongly encouraged. RTC after sleep study results. May need CPAP titration.', 524),

    (50064, 'SUBJECTIVE: Follow-up for peripheral neuropathy. Burning pain bilateral feet, worse at night. Started gabapentin 300mg TID 4 weeks ago. Pain improved from 7/10 to 4/10. Tolerating medication without side effects.

OBJECTIVE: Vitals normal. Neuro: Decreased sensation to light touch bilateral feet, absent ankle reflexes. Gait normal.

ASSESSMENT: Peripheral neuropathy - improving on gabapentin

PLAN: Increase gabapentin to 400mg TID for better pain control. Continue diabetic foot care. Check HbA1c and B12 level. RTC 4 weeks to reassess. Consider referral to podiatry if foot issues develop.', 520),

    (50065, 'SUBJECTIVE: Patient presents with urinary tract infection symptoms: Dysuria, urgency, frequency x 2 days. No fever, back pain, or hematuria. No vaginal discharge. Sexually active.

OBJECTIVE: T 98.6 degrees F, no CVA tenderness. Urinalysis: Positive leukocyte esterase, nitrites positive, WBC 50-100, bacteria many.

ASSESSMENT: Acute uncomplicated cystitis

PLAN: Nitrofurantoin 100mg BID x 5 days. Increase fluid intake. Phenazopyridine for dysuria PRN x 2 days. Return if fever, back pain, or no improvement in 48 hours. Discussed prevention: Post-coital voiding, adequate hydration.', 513),

    (50066, 'SUBJECTIVE: Routine well-child check, age 12. No health concerns. School performance good. Active in sports. Up to date with vaccines except HPV series.

OBJECTIVE: Wt 45 kg, Ht 152 cm, BMI 19.5 (50th percentile). Tanner stage 3. Physical exam normal. Vision, hearing screening passed.

ASSESSMENT: Health supervision age 12 years - normal development

PLAN: HPV vaccine series initiated today (dose 1 of 2). Tdap booster given. Anticipatory guidance: Screen time limits, nutrition, safety. Sports physical clearance provided. RTC 12 months or PRN.', 500),

    (50067, 'SUBJECTIVE: Patient with history of diverticulosis presents with left lower quadrant abdominal pain x 2 days. Pain constant, 6/10 severity. Low-grade fever. Change in bowel habits with constipation. No nausea or vomiting.

OBJECTIVE: T 100.4 degrees F, BP 128/78. Abdomen: Tender LLQ, no guarding or rebound. WBC 13.2.

ASSESSMENT: Suspected acute diverticulitis, mild

PLAN: CT abdomen/pelvis ordered to confirm. Start cipro 500mg BID and metronidazole 500mg TID x 10 days. Clear liquid diet x 2 days, advance as tolerated. Return if worsening pain, fever greater than 101, vomiting. Follow up in 2 days with CT results. If confirmed, colonoscopy in 6 weeks after resolution.', 641),

    (50068, 'PRIMARY CARE NOTE

SUBJECTIVE: Medicare annual wellness visit, age 72. Overall health good. Chronic conditions: HTN, HLD, mild cognitive impairment. Medications taken as prescribed. Denies falls. Uses cane for stability. Living independently.

OBJECTIVE: BP 132/76, HR 68, BMI 26.8. Cognitive screening (Mini-Cog): 3/5 (stable from last year). Functional assessment: Independent in ADLs, needs assistance with IADLs (medications, finances).

ASSESSMENT:
1. Hypertension - controlled
2. Hyperlipidemia - on statin
3. Mild cognitive impairment - stable

PLAN: Continue current medications. Updated health risk assessment. Advance care planning discussed. Fall risk assessment: Low risk. Pneumonia and flu vaccines up to date. Memory clinic follow-up in 6 months. RTC 12 months.', 759),

    (50069, 'SUBJECTIVE: Patient presents with acute ankle sprain. Injury occurred yesterday playing basketball. Twisted ankle, heard pop. Immediate pain and swelling. Difficulty weight-bearing. Iced and elevated at home.

OBJECTIVE: Right ankle: Moderate swelling, ecchymosis over lateral malleolus. Tender over ATFL. ROM limited by pain. Ottawa ankle rules: Tender at posterior edge lateral malleolus. X-ray: No fracture.

ASSESSMENT: Right ankle sprain grade 2

PLAN: RICE protocol: Rest, ice 20 min q2-3h, compression wrap, elevate. Air cast boot for stability. Weight-bear as tolerated with crutches. NSAIDs for pain. Physical therapy referral in 1 week. Return if no improvement in 5-7 days. Expected recovery 4-6 weeks.', 671),

    (50070, 'SUBJECTIVE: Follow-up for polymyalgia rheumatica. On prednisone 15mg daily, tapered from 20mg. Symptoms well controlled: No shoulder or hip stiffness. Morning stiffness less than 30 minutes. No headaches or vision changes.

OBJECTIVE: Vitals normal. ESR 18 (down from 72). Shoulder and hip ROM: Full, no tenderness.

ASSESSMENT: Polymyalgia rheumatica - in remission on prednisone

PLAN: Continue prednisone taper: Decrease to 12.5mg daily x 4 weeks, then 10mg daily. Monitor for symptom recurrence. Check ESR and CRP with each dose change. Long-term: Goal to taper off in 1-2 years. Calcium and vitamin D supplementation for bone health. RTC 4 weeks.', 591),

    -- Patient 1010 (ICN100010) notes starting
    (50071, 'SUBJECTIVE: New patient with history of seizure disorder presents for medication management. Last seizure 2 years ago. On levetiracetam 1000mg BID. Compliant with medications. No recent seizures, auras, or breakthrough symptoms. Denies side effects.

OBJECTIVE: Vitals normal. Neurologic exam: Alert, oriented x 3. Cranial nerves intact. Motor 5/5, sensation intact. Gait normal. Recent EEG (3 months ago): No epileptiform activity.

ASSESSMENT: Seizure disorder - well controlled on current regimen

PLAN: Continue levetiracetam 1000mg BID. CBC and CMP ordered for routine monitoring. Discussed seizure precautions: No driving until seizure-free x 1 year per state law. Avoid triggers: Sleep deprivation, alcohol. RTC 6 months or PRN if seizure occurs. Neurology co-management.', 669),

    (50072, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with chronic venous insufficiency presents with bilateral leg swelling and varicose veins. Symptoms worse end of day. Using compression stockings inconsistently. No leg ulcers. Aching sensation in calves.

OBJECTIVE: Bilateral lower extremities: Varicose veins, mild edema, hemosiderin staining medial ankles. No ulceration. Pedal pulses palpable.

ASSESSMENT: Chronic venous insufficiency with varicose veins

PLAN: Compression stockings 20-30 mmHg daily wear. Leg elevation when sitting. Regular exercise, especially walking. Weight loss if BMI elevated. Vascular surgery referral for vein ablation evaluation if symptoms persist. Monitor for venous ulcers. RTC 3 months.', 588),

    (50073, 'SUBJECTIVE: Follow-up for Parkinson disease. On carbidopa/levodopa 25/100 TID. Tremor improved but still present. Some bradykinesia. No falls. Able to perform ADLs independently. No hallucinations or confusion.

OBJECTIVE: Vitals normal. Neuro: Mild resting tremor right hand. Bradykinesia with finger tapping. Rigidity: Mild cogwheel at wrists. Gait: Slightly shuffling, no festination. UPDRS score: 24 (mild).

ASSESSMENT: Parkinson disease, early stage - partial response to levodopa

PLAN: Increase carbidopa/levodopa to 25/100 four times daily. Physical therapy referral for gait training. Consider adding dopamine agonist if inadequate response. Movement disorder neurology follow-up in 2 months. Discussed future medication adjustments. RTC 6 weeks.', 666),

    (50074, 'SUBJECTIVE: Patient presents with symptoms of benign prostatic hyperplasia: Nocturia x 4-5, weak stream, hesitancy, incomplete emptying. IPSS score: 22 (severe). No hematuria. PSA 3.2 ng/mL (age-appropriate).

OBJECTIVE: Vitals normal. Abdo: No suprapubic distention. Rectal: Prostate markedly enlarged, smooth, no nodules. Post-void residual (bladder scan): 180 mL.

ASSESSMENT: Benign prostatic hyperplasia with severe LUTS and elevated PVR

PLAN: Start tamsulosin 0.4mg daily and finasteride 5mg daily (combination therapy). Avoid decongestants and anticholinergics. Urology referral for elevated PVR and severe symptoms - may need surgical intervention (TURP). Uroflow study recommended. RTC 4 weeks or sooner if urinary retention develops.', 685),

    (50075, 'SUBJECTIVE: Follow-up for restless legs syndrome. Started ropinirole 0.5mg at bedtime 6 weeks ago. Symptoms significantly improved: Urge to move legs decreased, sleep quality better. No daytime sleepiness or side effects.

OBJECTIVE: Vitals normal. Neuro exam normal. Ferritin 45 ng/mL (normal).

ASSESSMENT: Restless legs syndrome - responding to dopamine agonist

PLAN: Continue ropinirole 0.5mg at bedtime. Avoid late caffeine. Monitor for augmentation (symptoms earlier in day or more severe). If symptoms worsen, may increase dose to 1mg. RTC 3 months or PRN.', 494),

    (50076, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with fibromyalgia presents for pain management. Widespread pain, fatigue, and poor sleep. On duloxetine 60mg daily x 3 months. Pain improved from 8/10 to 5/10. Sleep still poor despite sleep hygiene measures.

OBJECTIVE: Vitals normal. Tender points: 14 of 18 positive. No joint swelling or inflammation.

ASSESSMENT:
1. Fibromyalgia - partial response to duloxetine
2. Insomnia

PLAN: Increase duloxetine to 90mg daily for better pain control. Add low-dose amitriptyline 10mg at bedtime for sleep and pain. Encourage regular gentle exercise (swimming, walking). Physical therapy and CBT referrals. Avoid opioids. RTC 6 weeks.', 560),

    (50077, 'SUBJECTIVE: Follow-up for celiac disease. On gluten-free diet x 6 months. GI symptoms resolved: No diarrhea, bloating, or abdominal pain. Energy improved. Careful with diet compliance. Seeing dietitian regularly.

OBJECTIVE: Wt 152 lbs (up 8 lbs from diagnosis). BMI 22.5. Abdomen: Soft, non-tender.

ASSESSMENT: Celiac disease - in remission on gluten-free diet

PLAN: Continue strict gluten-free diet lifelong. Tissue transglutaminase IgA to assess mucosal healing - level 12 (normal, down from 98). Annual monitoring of TTG-IgA. Check for nutrient deficiencies: Iron, B12, folate, vitamin D - all normal. Celiac support group resources provided. RTC 12 months.', 563),

    (50078, 'SUBJECTIVE: Patient with history of shingles 2 weeks ago presents for post-herpetic neuralgia management. Vesicular rash resolved but persistent burning pain in left T6 dermatome, severity 7/10. Interfering with sleep and daily activities.

OBJECTIVE: Skin exam: Healed vesicles with hyperpigmentation left mid-thorax, T6 distribution. Allodynia present in affected area.

ASSESSMENT: Post-herpetic neuralgia following herpes zoster

PLAN: Start gabapentin 300mg TID, titrate up by 300mg every 3 days to max 900mg TID as tolerated. Lidocaine patches 5% to affected area 12 hours on/12 hours off. Capsaicin cream may help after acute phase resolves. Pain management referral if refractory. RTC 2 weeks.', 623),

    (50079, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents with recurrent epistaxis x 1 month. Episodes 2-3 times weekly, lasting 5-10 minutes. Resolves with pressure. No trauma. On aspirin 81mg for CAD. No easy bruising or other bleeding.

OBJECTIVE: Vitals: BP 168/94 (elevated). Nasal exam: Anterior septum - visible vessel (Kiesselbach plexus), dried blood. No active bleeding. No masses or polyps.

ASSESSMENT:
1. Recurrent epistaxis - likely anterior septal vessel
2. Hypertension - uncontrolled

PLAN: ENT referral for cautery of bleeding vessel. Saline nasal spray QID for moisture. Humidifier at night. Avoid nose picking, forceful blowing. Address HTN: Increase lisinopril to 20mg daily. Recheck BP in 1 week. Aspirin: Continue (benefit outweighs risk). RTC 2 weeks.', 689),

    (50080, 'SUBJECTIVE: Follow-up for hypothyroidism in pregnancy. Currently 16 weeks gestation. On levothyroxine 125mcg daily. Energy good, no palpitations. Taking prenatal vitamins. OB care established.

OBJECTIVE: Vitals: BP 118/72, HR 76. TSH 1.8 mIU/L (goal less than 2.5 in pregnancy), Free T4 1.3 ng/dL (normal).

ASSESSMENT: Hypothyroidism in pregnancy - euthyroid on current dose

PLAN: Continue levothyroxine 125mcg daily. Recheck TSH every 4 weeks through pregnancy (increased thyroid hormone needs). Coordinate care with OB. Postpartum: Expect to decrease dose back to pre-pregnancy level. RTC 4 weeks for TSH recheck.', 547),

    (50081, 'SUBJECTIVE: Patient with gout presents with acute flare: Right first MTP joint pain, swelling, redness x 2 days. Severity 9/10, unable to bear weight. Denies fever. Triggered by recent shellfish meal and beer. On allopurinol 300mg daily for prophylaxis.

OBJECTIVE: Right great toe: Erythema, warmth, swelling, exquisite tenderness to palpation. ROM severely limited by pain. Uric acid 8.2 mg/dL (elevated despite allopurinol).

ASSESSMENT: Acute gouty arthritis, first MTP joint - breakthrough flare on allopurinol

PLAN: Colchicine 1.2mg now, then 0.6mg in 1 hour. Then 0.6mg daily x 7 days. Indomethacin 50mg TID with food x 5 days for inflammation. Continue allopurinol 300mg daily (do not stop during flare). Increase allopurinol to 400mg daily after flare resolves. Dietary counseling: Limit purine-rich foods, alcohol. Hydration. RTC 1 week.', 787),

    (50082, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents for preconception counseling. Planning pregnancy in next 6 months. Currently on lisinopril for HTN. No chronic medical conditions otherwise. Last Pap 1 year ago: Normal. Up to date with vaccines.

OBJECTIVE: BP 126/78, BMI 24.5. Physical exam unremarkable.

ASSESSMENT: Preconception counseling

PLAN:
1. Stop lisinopril (teratogenic ACE inhibitor). Switch to labetalol 200mg BID for HTN.
2. Start prenatal vitamin with folic acid 400-800 mcg daily now
3. Update immunity: Rubella immune (prior MMR), give Tdap if greater than 10 years
4. Genetic carrier screening offered
5. Avoid alcohol, tobacco
6. Discussed prenatal care timeline
7. Optimize chronic conditions before conception
8. RTC after positive pregnancy test for early OB referral', 655),

    (50083, 'SUBJECTIVE: Follow-up for chronic lymphocytic leukemia (CLL), Rai stage 0. Diagnosed 3 years ago. Watch and wait approach. No B symptoms: Fevers, night sweats, weight loss. Energy level good. No infections.

OBJECTIVE: Vitals normal. No lymphadenopathy. No hepatosplenomegaly. CBC: WBC 18.2 (lymphocytes 85%), Hgb 13.8, Plt 165 - stable from prior.

ASSESSMENT: CLL, Rai stage 0 - stable, no treatment indicated

PLAN: Continue observation. Repeat CBC in 3 months. Hematology follow-up every 6 months. Treatment criteria: Progressive lymphocytosis, symptomatic lymphadenopathy, cytopenias, B symptoms. Annual flu vaccine (live vaccines contraindicated). RTC 3 months or sooner if concerning symptoms.', 624),

    (50084, 'SUBJECTIVE: Patient with chronic tinnitus presents for follow-up. Constant bilateral ringing x 2 years. Worse in quiet environments. Affects sleep quality. Previous audiogram showed mild high-frequency hearing loss. No vertigo or ear pain.

OBJECTIVE: Vitals normal. Otoscopy: TMs clear bilaterally, no cerumen impaction. Neuro: Cranial nerves intact.

ASSESSMENT: Chronic subjective tinnitus with mild hearing loss

PLAN: Sound therapy: White noise machine at night. Hearing aid evaluation (amplification may help). Avoid loud noise exposure. Limit caffeine and alcohol. Cognitive behavioral therapy referral for coping strategies. ENT follow-up. Consider MRI brain/IAC if symptoms change or asymmetric hearing loss. RTC 3 months.', 599),

    (50085, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents with left eye redness and discharge x 3 days. Symptoms: Crusting in morning, gritty sensation, tearing. No vision changes or photophobia. No trauma. Contacts wearer.

OBJECTIVE: Left eye: Injected conjunctiva, mucopurulent discharge, no corneal opacity. Visual acuity normal. Right eye normal.

ASSESSMENT: Bacterial conjunctivitis, left eye

PLAN: Erythromycin ophthalmic ointment 0.5% to left eye QID x 7 days. Warm compresses. Avoid contact lens wear until infection resolved (at least 24 hours after completing treatment). Wash hands frequently. Avoid sharing towels. Return if worsening, vision changes, or no improvement in 3 days.', 582),

    (50086, 'SUBJECTIVE: Follow-up for peripheral arterial disease. Bilateral calf claudication with walking 2 blocks, relieved with rest. No rest pain. No wounds or ulcers. On aspirin and statin. Quit smoking 6 months ago (great success). Able to walk further than 3 months ago.

OBJECTIVE: Vitals normal. Bilateral lower extremities: No ulcers. Femoral pulses 2+, popliteal 1+, dorsalis pedis/PT absent bilaterally. ABI: Right 0.68, Left 0.72 (moderate PAD).

ASSESSMENT: Peripheral arterial disease with claudication - stable

PLAN: Continue aspirin 81mg, atorvastatin 80mg, cilostazol 100mg BID. Supervised exercise therapy: Walk to near-max pain, rest, repeat x 30 min, 3-5x/week. Vascular surgery follow-up every 6 months. If symptoms worsen or rest pain develops, may need revascularization. Foot care education. RTC 3 months.', 781),

    (50087, 'SUBJECTIVE: Patient with history of stroke (left MCA, 2 years ago) presents for routine follow-up. Residual right-sided weakness, using cane. No new neurologic symptoms. On aspirin, statin, and BP medications. PT twice weekly. Independent in ADLs with assistive devices.

OBJECTIVE: BP 128/76, HR 68. Neuro: Right arm strength 4/5, right leg 4+/5. Mild right facial droop (residual). Speech normal. Gait with cane: Steady.

ASSESSMENT: History of ischemic stroke with residual hemiparesis - stable

PLAN: Continue secondary stroke prevention: Aspirin 81mg, atorvastatin 80mg, lisinopril 20mg. Continue PT. Carotid ultrasound: Less than 50% stenosis bilaterally (stable). Annual echocardiogram and carotid US. Aggressive risk factor control. RTC 6 months. Call 911 if new neuro symptoms.', 669),

    (50088, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with Barrett esophagus (2 cm segment, no dysplasia) on surveillance. Last EGD 1 year ago: No dysplasia. Currently on omeprazole 20mg daily. No dysphagia or heartburn. No alarm symptoms.

OBJECTIVE: Vitals normal. Abdomen soft, non-tender.

ASSESSMENT: Barrett esophagus without dysplasia - on surveillance

PLAN: Continue omeprazole 20mg daily for acid suppression. Repeat EGD with biopsies in 12 months (surveillance interval for non-dysplastic Barrett). GI follow-up. Discussed progression risk (low without dysplasia). Weight loss and head of bed elevation recommended. RTC 12 months or sooner if dysphagia or GI bleeding.', 545),

    (50089, 'SUBJECTIVE: Follow-up for hemochromatosis (C282Y homozygous). On therapeutic phlebotomy program x 2 years. Currently maintenance phase: Phlebotomy every 3 months. Energy good. No joint pain. Compliant with blood donations.

OBJECTIVE: Vitals normal. Ferritin 68 ng/mL (goal 50-100), transferrin saturation 32%.

ASSESSMENT: Hereditary hemochromatosis - well controlled on maintenance phlebotomy

PLAN: Continue phlebotomy every 3 months to maintain ferritin 50-100. Monitor ferritin every 3-6 months. Annual liver enzymes and AFP (cirrhosis screening). Avoid iron supplements and vitamin C supplements. Limit alcohol. Genetic counseling for family members offered. RTC 6 months.', 574),

    (50090, 'SUBJECTIVE: Patient with chronic hepatitis B (inactive carrier) presents for routine monitoring. No symptoms. Liver enzymes normal last check. On tenofovir 300mg daily for 5 years. No history of cirrhosis. Compliant with medication.

OBJECTIVE: Vitals normal. Abdomen: No hepatomegaly. Labs: ALT 28, AST 32 (normal), HBV DNA undetectable, HBsAg positive.

ASSESSMENT: Chronic hepatitis B, inactive carrier on antiviral therapy - viral suppression

PLAN: Continue tenofovir 300mg daily indefinitely. Monitor ALT, AST, HBV DNA every 6 months. Annual AFP and liver ultrasound for HCC screening. Avoid alcohol. Ensure contacts vaccinated. Hepatology co-management. RTC 6 months.', 527),

    (50091, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents with symptoms of carpal tunnel syndrome: Numbness and tingling right hand (thumb, index, middle fingers), worse at night. Symptoms wake patient from sleep. Shaking hand provides relief. Occupation: Data entry. No neck pain.

OBJECTIVE: Right hand: Positive Tinel at wrist, positive Phalen maneuver. Thenar atrophy: None. Sensation: Decreased light touch median nerve distribution. Motor: Thumb opposition strength 5/5.

ASSESSMENT: Carpal tunnel syndrome, right - moderate symptoms

PLAN: Night wrist splint in neutral position. Ergonomic assessment at work. NSAIDs PRN. If no improvement in 6 weeks, nerve conduction study and orthopedic referral for possible corticosteroid injection or surgical release. Avoid repetitive wrist motions. RTC 6 weeks.', 681),

    (50092, 'SUBJECTIVE: Follow-up for Raynaud phenomenon. Episodes of bilateral finger color changes (white, blue, red) with cold exposure. Frequency increased in winter. No digital ulcers. No other connective tissue disease symptoms.

OBJECTIVE: Vitals normal. Hands: No digital ulcers, normal capillary refill. Nailfold capillary exam: Normal (no dilated loops).

ASSESSMENT: Primary Raynaud phenomenon

PLAN: Keep hands warm: Gloves in cold weather. Avoid smoking (vasoconstriction). Calcium channel blocker trial: Nifedipine ER 30mg daily for severe episodes. Rheumatology referral if digital ulcers develop or secondary causes suspected. Monitor for systemic sclerosis (rare progression). RTC 3 months or PRN.', 564),

    (50093, 'SUBJECTIVE: Patient with diagnosed plantar fasciitis presents for follow-up. Heel pain, worse with first steps in morning. On stretching program and night splint x 4 weeks. Pain improved from 8/10 to 5/10. Still limiting activities.

OBJECTIVE: Right foot: Tenderness plantar medial calcaneal tubercle. Tight Achilles tendon. Gait: Mild antalgic.

ASSESSMENT: Plantar fasciitis, right - improving but persistent

PLAN: Continue stretching exercises and night splint. Add heel cups for cushioning. Consider NSAID course x 2 weeks. Physical therapy referral for formal program. If no improvement, consider corticosteroid injection or referral to podiatry for orthotic evaluation. Avoid barefoot walking. RTC 6 weeks.', 580),

    (50094, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with history of pulmonary embolism (6 months ago, provoked by surgery) presents for anticoagulation review. On rivaroxaban 20mg daily. No bleeding complications. No recurrent VTE symptoms.

OBJECTIVE: Vitals normal. Lungs clear. Lower extremities: No edema or calf tenderness.

ASSESSMENT: History of provoked PE on anticoagulation - completing planned course

PLAN: Complete 6 months total anticoagulation (2 more months). Repeat lower extremity ultrasound: No residual DVT. After completion, stop anticoagulation (provoked event, low recurrence risk). Counsel on VTE prevention: Mobilize early after surgery, stay hydrated on flights. RTC 2 months to stop anticoagulation.', 556),

    (50095, 'SUBJECTIVE: Follow-up for benign essential tremor. Bilateral hand tremor, worse with action and stress. Interfering with writing and eating. No tremor at rest. Family history: Father had tremor. On propranolol 40mg BID x 3 months. Tremor improved 50%, tolerating well.

OBJECTIVE: Vitals: BP 118/72, HR 58. Neuro: Bilateral postural and kinetic tremor, improved with propranolol. No resting tremor. Gait normal.

ASSESSMENT: Essential tremor - partial response to beta blocker

PLAN: Increase propranolol to 60mg BID for better tremor control. Avoid caffeine, ensure adequate sleep. If inadequate response, may add primidone. Neurology follow-up if refractory. Occupational therapy for adaptive strategies. RTC 6 weeks.', 583),

    -- Patient 1013 (ICN100013) notes starting
    (50096, 'SUBJECTIVE: Patient presents with recurrent sinusitis, 4th episode this year. Current symptoms: Facial pressure, purulent nasal discharge, post-nasal drip x 10 days. No improvement with OTC decongestants. No fever. History of allergic rhinitis.

OBJECTIVE: T 98.8 degrees F. Sinus exam: Tenderness over maxillary sinuses bilaterally. Nasal mucosa: Boggy, purulent drainage. Oropharynx: Post-nasal drip visible.

ASSESSMENT: Acute bacterial rhinosinusitis, recurrent

PLAN: Amoxicillin-clavulanate 875/125 mg BID x 10 days. Saline nasal rinses BID. Intranasal steroid spray. If no improvement in 48-72 hours, consider CT sinuses. ENT referral for recurrent sinusitis evaluation (may need sinus surgery). Address underlying allergies. RTC 2 weeks or sooner if worsening.', 694),

    (50097, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with type 1 diabetes (diagnosed age 12, now 35) presents for routine diabetes management. On insulin pump therapy. CGM shows time in range 72%. Recent A1C 7.1% (goal less than 7%). No severe hypoglycemia. Annual eye exam: No retinopathy. Urine albumin: Normal.

OBJECTIVE: BP 122/76, Wt 165 lbs (stable). Foot exam: Monofilament intact, no ulcers, pedal pulses 2+.

ASSESSMENT: Type 1 diabetes mellitus - good glycemic control on insulin pump

PLAN: Continue current insulin pump settings. CGM data reviewed - adjust basal rates overnight. Annual labs: Lipids, TSH, vitamin B12 ordered. Continue ACE inhibitor for renal protection. Endocrinology co-management. Diabetic foot care reviewed. RTC 3 months.', 651),

    (50098, 'SUBJECTIVE: Patient with history of melanoma (stage 1A, excised 2 years ago) presents for skin surveillance. No new or changing lesions noted. Performing monthly self-exams. Using sunscreen SPF 50 daily. Avoiding tanning beds.

OBJECTIVE: Full body skin exam: Multiple benign nevi. Surgical scar right shoulder: Well-healed. No suspicious lesions identified.

ASSESSMENT: History of melanoma, stage 1A - no evidence of recurrence

PLAN: Continue full body skin exams every 6 months x 5 years, then annually. Monthly self-skin exams. Sun protection: Broad-spectrum SPF 30+, protective clothing, avoid peak sun hours. Photograph any changing lesions. Dermatology referral if suspicious lesions. RTC 6 months.', 561),

    (50099, 'SUBJECTIVE: Patient with chronic migraine presents for Botox injection visit. Headaches 15+ days per month despite prophylactic medication (topiramate 100mg BID). Last Botox treatment 12 weeks ago provided good relief for 10 weeks.

OBJECTIVE: Vitals normal. Neuro exam normal.

ASSESSMENT: Chronic migraine - responding to Botox therapy

PLAN: OnabotulinumtoxinA (Botox) injections performed today: 155 units across 31 sites (frontalis, temporalis, occipitalis, cervical paraspinal muscles). Expect benefit in 1-2 weeks, lasting 10-12 weeks. Continue topiramate. Sumatriptan for breakthrough headaches. Next Botox treatment in 12 weeks. Headache diary. RTC 12 weeks or PRN for severe headache.', 581),

    (50100, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with ulcerative colitis (pancolitis, diagnosed 5 years ago) on maintenance mesalamine presents for routine follow-up. Currently in remission: No blood in stool, normal bowel movements 1-2x daily. No abdominal pain. Compliant with mesalamine 1.2g TID.

OBJECTIVE: Vitals normal. Abdomen soft, non-tender, normal bowel sounds.

ASSESSMENT: Ulcerative colitis - in remission on mesalamine

PLAN: Continue mesalamine 1.2g TID. Colonoscopy surveillance every 1-2 years (per GI). Next scope due in 6 months. Monitor for flare symptoms: Bloody diarrhea, urgency, abdominal pain. Annual colorectal cancer screening (higher risk). GI co-management. RTC 6 months or sooner if flare.', 545),

    (50101, 'SUBJECTIVE: Follow-up for psoriasis. Plaques on elbows, knees, scalp. Topical steroids provide temporary relief but lesions recur. Impacting quality of life. Candidate for systemic therapy per dermatology.

OBJECTIVE: Skin exam: Erythematous plaques with silvery scale bilateral elbows and knees. Scalp: Multiple plaques. BSA involved: 8%. PASI score: 12 (moderate).

ASSESSMENT: Moderate plaque psoriasis - inadequate response to topicals

PLAN: Dermatology initiated biologics: Adalimumab loading dose 80mg today, then 40mg every other week. TB screening negative. Hepatitis panel negative. Discussed infection risks, injection technique. Monitor for serious infections. Follow up dermatology in 12 weeks to assess response. RTC 3 months.', 606),

    (50102, 'SUBJECTIVE: Patient presents with acute cholecystitis symptoms: Right upper quadrant pain x 8 hours, constant, severe 8/10. Nausea, vomiting x 2. Pain radiates to right shoulder. History of gallstones on prior ultrasound.

OBJECTIVE: T 100.8 degrees F, BP 138/82, HR 98. Abdomen: Tender RUQ, positive Murphy sign, no rebound. WBC 15.8.

ASSESSMENT: Suspected acute cholecystitis

PLAN: NPO. IV fluids started. RUQ ultrasound STAT: Gallstones, gallbladder wall thickening, pericholecystic fluid, positive sonographic Murphy sign - confirms cholecystitis. Surgery consult for cholecystectomy. IV antibiotics: Ceftriaxone and metronidazole. Admit to hospital. Pain control. Likely laparoscopic cholecystectomy within 24-48 hours.', 663),

    (50103, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with atrial fibrillation (paroxysmal) on apixaban for stroke prevention presents for routine follow-up. No palpitations recently. Last episode 2 months ago, self-resolved. On metoprolol for rate control. CHA2DS2-VASc score: 4 (high stroke risk).

OBJECTIVE: BP 124/76, HR 68 regular. ECG: Normal sinus rhythm. No peripheral edema.

ASSESSMENT:
1. Paroxysmal atrial fibrillation - currently in sinus rhythm
2. On anticoagulation for stroke prevention

PLAN: Continue apixaban 5mg BID indefinitely. Continue metoprolol 50mg BID. No bleeding complications. Cardiology follow-up every 6 months. If more frequent episodes, may need rhythm control strategy (ablation vs. antiarrhythmics). RTC 6 months or sooner if symptoms.', 664),

    (50104, 'SUBJECTIVE: Follow-up for iron deficiency anemia. Started ferrous sulfate 325mg daily 8 weeks ago. Energy improved. No longer short of breath. Tolerating iron supplement - mild constipation managed with stool softener. Colonoscopy (workup): Normal, no source of bleeding identified.

OBJECTIVE: Vitals normal. Conjunctiva: Pink. Repeat CBC: Hgb 13.2 (up from 9.8), MCV 86 (was 72), ferritin 45 (was 8).

ASSESSMENT: Iron deficiency anemia - resolved with iron supplementation

PLAN: Continue ferrous sulfate 325mg daily x 3 more months to replete stores. Recheck CBC and ferritin in 3 months. Once ferritin greater than 50, can stop iron. Menstrual history: Regular, not heavy. Diet: Increase iron-rich foods. RTC 3 months.', 598),

    (50105, 'SUBJECTIVE: Patient with history of basal cell carcinoma (nose, excised 1 year ago) presents for follow-up. Surgical site healed well. No new skin lesions noted. Using sunscreen regularly.

OBJECTIVE: Nose: Well-healed scar, no recurrence. Full skin exam: No suspicious lesions.

ASSESSMENT: History of basal cell carcinoma, no evidence of recurrence

PLAN: Annual full body skin exams. Monthly self-exams. Sun protection counseling reinforced. Dermatology follow-up annually. Low risk of metastasis but can recur locally. RTC 12 months or sooner if new/changing lesions.', 435),

    (50106, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient presents with symptoms of overactive bladder: Urinary frequency (10+ times daily), urgency, occasional urge incontinence. No dysuria or hematuria. Impacting quality of life. Fluid intake: 8 glasses water daily. Caffeine: 3 cups coffee daily.

OBJECTIVE: Vitals normal. Abdomen: No suprapubic tenderness, no masses. Post-void residual: 45 mL (normal). Urinalysis: Normal.

ASSESSMENT: Overactive bladder syndrome

PLAN: Behavioral modifications: Bladder diary, timed voiding every 2-3 hours, reduce caffeine to 1 cup daily. Pelvic floor exercises (Kegels). Trial of mirabegron 25mg daily (beta-3 agonist, fewer anticholinergic side effects). If inadequate response after 8 weeks, may try anticholinergic. Urology referral if refractory. RTC 8 weeks.', 716),

    (50107, 'SUBJECTIVE: Follow-up for rheumatoid arthritis. On methotrexate 15mg weekly and hydroxychloroquine 200mg BID x 6 months. Joint pain and stiffness significantly improved. Morning stiffness less than 30 minutes (was 2+ hours). Able to perform ADLs without difficulty. No medication side effects.

OBJECTIVE: Vitals normal. Hand exam: No active synovitis. Grip strength: Normal. ESR 18 (down from 52), CRP 0.8 (down from 3.2).

ASSESSMENT: Rheumatoid arthritis - in remission on DMARD therapy

PLAN: Continue methotrexate 15mg weekly with folic acid 1mg daily. Continue hydroxychloroquine. Monitor CBC, CMP, AST/ALT every 3 months. Annual ophthalmology for hydroxychloroquine retinal screening. Rheumatology co-management every 6 months. Low-dose prednisone no longer needed. RTC 3 months.', 717),

    (50108, 'SUBJECTIVE: Patient with history of DVT (provoked by prolonged immobility from leg fracture, 2 years ago) planning international flight next month (12 hours). Concerned about VTE recurrence. Not currently on anticoagulation.

OBJECTIVE: Vitals normal. Lower extremities: No edema, calf tenderness, or varicosities.

ASSESSMENT: History of provoked DVT, planning long-haul flight - VTE prophylaxis needed

PLAN: VTE prevention for flight:
1. Aisle seat for frequent walking (every 1-2 hours)
2. Calf exercises while seated
3. Stay well hydrated
4. Avoid alcohol
5. Consider compression stockings 15-20 mmHg
6. Low risk given provoked event, but prophylactic enoxaparin 40mg SC day of travel could be considered
Discussed signs of DVT/PE: Calf pain, swelling, chest pain, SOB - seek care immediately. RTC after trip if any concerns.', 689),

    (50109, 'PRIMARY CARE NOTE

SUBJECTIVE: Patient with chronic urticaria x 6 months. Daily hives, itching. Antihistamines (cetirizine 10mg daily) provide partial relief. No identifiable triggers: Food diary unrevealing. No new medications or products. No angioedema.

OBJECTIVE: Skin: Multiple urticarial lesions (wheals) on trunk and arms, blanch with pressure. No angioedema.

ASSESSMENT: Chronic spontaneous urticaria

PLAN: Increase antihistamine: Cetirizine 10mg BID (can safely double dose for chronic urticaria). If inadequate, may add H2 blocker (famotidine). Avoid triggers if identified. Keep symptom diary. Allergy/immunology referral if refractory to high-dose antihistamines (may need omalizumab). Check TSH (thyroid disease association). RTC 4 weeks.', 638),

    (50110, 'SUBJECTIVE: Follow-up for temporal arteritis (giant cell arteritis). Diagnosed 4 months ago with elevated ESR, positive temporal artery biopsy. On prednisone taper, currently 30mg daily (started 60mg). Symptoms resolved: No headache, jaw claudication, or vision changes. Tolerating prednisone.

OBJECTIVE: Vitals: BP 138/84. Temporal arteries: Non-tender, palpable. ESR 22 (down from 88 at diagnosis).

ASSESSMENT: Giant cell arteritis - in remission on prednisone taper

PLAN: Continue prednisone taper: Decrease to 25mg daily x 2 weeks, then 20mg daily. Very slow taper over 12-18 months. Monitor ESR with each dose change. Calcium 1200mg and vitamin D 1000 IU daily for bone protection. Consider DEXA scan and bisphosphonate if prolonged steroid use. Rheumatology co-management. Call immediately if vision changes or severe headache. RTC 2 weeks.', 720),

    -- Remaining notes for Patient 1003, 1004 (shorter clinical notes)
    (50111, 'SUBJECTIVE: Patient presents for sports physical clearance. Age 16, plays varsity soccer. No health concerns. No chest pain with exertion. No syncope. Family history negative for sudden cardiac death.

OBJECTIVE: Vitals: BP 112/68, HR 58. General: Well-developed athlete. CV: RRR, no murmurs. Lungs: CTA. Musculoskeletal: Full ROM all joints, normal strength.

ASSESSMENT: Pre-participation sports physical - cleared

PLAN: Cleared for all sports participation. Reviewed concussion symptoms and protocol. Discussed hydration, nutrition. RTC 12 months or PRN for injury.', 497),

    (50112, 'SUBJECTIVE: Follow-up for acne vulgaris. On topical tretinoin and benzoyl peroxide x 3 months. Moderate improvement but persistent inflammatory lesions. Impacting self-esteem.

OBJECTIVE: Face: Moderate comedonal and inflammatory acne, bilateral cheeks and forehead. Some post-inflammatory hyperpigmentation. No scarring.

ASSESSMENT: Moderate acne vulgaris - inadequate response to topicals alone

PLAN: Add oral doxycycline 100mg BID x 3 months. Continue topical regimen. Sunscreen daily (photosensitivity with doxy). Avoid picking lesions. Dermatology referral if no improvement (may need isotretinoin). RTC 6 weeks.', 523),

    (50113, 'SUBJECTIVE: Patient presents with acute low back pain after lifting furniture 2 days ago. Pain 7/10, worse with movement. No leg pain, numbness, or weakness. No bowel/bladder changes. Taking ibuprofen with mild relief.

OBJECTIVE: Vitals normal. Lumbar spine: Paraspinal muscle spasm, limited ROM. Straight leg raise negative. Strength 5/5 lower extremities. Reflexes symmetric.

ASSESSMENT: Acute mechanical low back pain, lumbar strain

PLAN: NSAIDs scheduled x 1 week. Ice/heat alternating. Activity as tolerated - avoid bed rest. Physical therapy referral if not improving in 1 week. Red flags reviewed. No imaging needed at this time. RTC 1 week or sooner if neurologic symptoms develop.', 621),

    (50114, 'SUBJECTIVE: Annual flu shot visit. Patient age 68, requests influenza vaccine. No acute illness. No egg allergy.

OBJECTIVE: Vitals normal. No contraindications to vaccine.

ASSESSMENT: Seasonal influenza vaccination

PLAN: Influenza vaccine (quadrivalent, high-dose for age 65+) administered today in left deltoid. Vaccine information statement provided. Observed 15 minutes - no reaction. Advised possible mild arm soreness. Return if signs of allergic reaction (rare).', 396),

    (50115, 'SUBJECTIVE: Patient with lactose intolerance presents for dietary counseling. Symptoms of bloating, gas, diarrhea after dairy products. Avoiding milk but concerned about calcium intake.

OBJECTIVE: Vitals normal. Abdomen: Soft, non-tender, normal bowel sounds.

ASSESSMENT: Lactose intolerance

PLAN: Dietary counseling: Lactose-free alternatives (almond milk, lactose-free dairy), calcium-fortified foods. Calcium supplementation 600mg BID with vitamin D. Lactase enzyme supplements available OTC for occasional dairy consumption. Nutrition referral provided. RTC PRN.', 475),

    (50116, 'SUBJECTIVE: Follow-up for mild persistent asthma. On low-dose inhaled corticosteroid (fluticasone 110mcg BID) and albuterol PRN. Well-controlled: Using rescue inhaler less than 2x/week. No nighttime symptoms. No activity limitations. Peak flow measurements stable.

OBJECTIVE: Vitals: SpO2 99% RA. Lungs: Clear, no wheezes. Peak flow: 420 L/min (personal best 450).

ASSESSMENT: Asthma, mild persistent - well controlled on current therapy

PLAN: Continue fluticasone 110mcg BID. Albuterol PRN. Annual flu vaccine. Asthma action plan current. Spirometry stable. RTC 6 months or sooner if increased symptoms.', 503),

    (50117, 'SUBJECTIVE: Patient presents with plantar wart on right foot x 3 months. Over-the-counter salicylic acid treatments tried without success. Painful with walking.

OBJECTIVE: Right foot plantar surface: 1 cm hyperkeratotic lesion with central black dots. Tender to palpation.

ASSESSMENT: Verruca plantaris (plantar wart)

PLAN: Liquid nitrogen cryotherapy performed today. May require multiple treatments. Continue salicylic acid 40% plaster at home between treatments. Callus debridement. Return in 2-3 weeks for repeat cryotherapy if not resolved. Avoid going barefoot in public areas.', 490),

    (50118, 'SUBJECTIVE: Follow-up for vitamin B12 deficiency. On monthly B12 injections x 6 months. Energy significantly improved. No more numbness/tingling in feet. Compliant with injection schedule.

OBJECTIVE: Vitals normal. Neuro: Sensation intact lower extremities. Gait normal. B12 level: 650 pg/mL (normal, up from 180).

ASSESSMENT: Vitamin B12 deficiency - replete on monthly injections

PLAN: Continue cyanocobalamin 1000 mcg IM monthly indefinitely (pernicious anemia, lifelong treatment). Annual CBC to monitor. RTC 12 months or PRN if symptoms recur.', 459),

    (50119, 'SUBJECTIVE: Patient presents for routine blood pressure check. Diagnosed with hypertension 2 months ago, started on lisinopril 10mg daily. Home BP log shows readings 118-135/72-85. No side effects from medication.

OBJECTIVE: BP 128/78 (repeated 124/76), HR 72. Cardiovascular exam normal.

ASSESSMENT: Essential hypertension - well controlled on lisinopril

PLAN: Continue lisinopril 10mg daily. Repeat BMP to check potassium and creatinine: Normal. Continue home BP monitoring. Lifestyle modifications ongoing. RTC 3 months.', 443),

    (50120, 'SUBJECTIVE: Patient presents with symptoms of acute sinusitis: Facial pressure, purulent nasal discharge, congestion x 7 days. No improvement with OTC decongestants. Mild frontal headache. No fever.

OBJECTIVE: T 98.6 degrees F. Sinus exam: Tenderness over maxillary and frontal sinuses. Nasal mucosa edematous with purulent drainage. Pharynx: Post-nasal drip.

ASSESSMENT: Acute bacterial rhinosinusitis

PLAN: Amoxicillin-clavulanate 875/125mg BID x 10 days. Saline nasal rinses TID. Intranasal steroid spray. Analgesics for pain. Return if no improvement in 3-5 days or worsening symptoms. RTC 2 weeks or PRN.', 555);
GO

PRINT '120 clinical note text records inserted successfully';
PRINT 'All notes have properly escaped apostrophes for SQL Server compatibility';
GO
