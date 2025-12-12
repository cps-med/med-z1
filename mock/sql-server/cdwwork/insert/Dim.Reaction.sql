-- =============================================
-- Insert Data: Dim.Reaction
-- Description: Seed reaction dimension with common allergy reactions
-- Author: Claude Code
-- Date: 2025-12-12
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Dim.Reaction ON;
GO

-- Insert reaction seed data
INSERT INTO Dim.Reaction (ReactionSID, ReactionName, IsActive)
VALUES
    -- Skin reactions (most common)
    (1, 'HIVES', 1),
    (2, 'RASH', 1),
    (3, 'ITCHING', 1),
    (4, 'SWELLING', 1),
    (5, 'REDNESS', 1),
    (6, 'BURNING SENSATION', 1),
    (7, 'BLISTERS', 1),
    (8, 'FLUSHING', 1),

    -- Respiratory reactions
    (10, 'WHEEZING', 1),
    (11, 'SHORTNESS OF BREATH', 1),
    (12, 'DIFFICULTY BREATHING', 1),
    (13, 'COUGH', 1),
    (14, 'THROAT TIGHTNESS', 1),
    (15, 'HOARSENESS', 1),
    (16, 'NASAL CONGESTION', 1),
    (17, 'RUNNY NOSE', 1),
    (18, 'SNEEZING', 1),

    -- Gastrointestinal reactions
    (20, 'NAUSEA', 1),
    (21, 'VOMITING', 1),
    (22, 'DIARRHEA', 1),
    (23, 'ABDOMINAL PAIN', 1),
    (24, 'CRAMPING', 1),
    (25, 'BLOATING', 1),

    -- Severe/systemic reactions
    (30, 'ANAPHYLAXIS', 1),
    (31, 'ANGIOEDEMA', 1),
    (32, 'HYPOTENSION', 1),
    (33, 'TACHYCARDIA', 1),
    (34, 'SEIZURE', 1),
    (35, 'LOSS OF CONSCIOUSNESS', 1),
    (36, 'CHEST PAIN', 1),
    (37, 'SHOCK', 1),

    -- Neurological reactions
    (40, 'HEADACHE', 1),
    (41, 'DIZZINESS', 1),
    (42, 'CONFUSION', 1),
    (43, 'DROWSINESS', 1),
    (44, 'LIGHTHEADEDNESS', 1),
    (45, 'TREMORS', 1),

    -- Other reactions
    (50, 'FEVER', 1),
    (51, 'CHILLS', 1),
    (52, 'SWEATING', 1),
    (53, 'FATIGUE', 1),
    (54, 'MUSCLE ACHES', 1),
    (55, 'JOINT PAIN', 1),
    (56, 'WATERY EYES', 1),
    (57, 'EYE SWELLING', 1),
    (58, 'RAPID PULSE', 1),
    (59, 'IRREGULAR HEARTBEAT', 1);
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Dim.Reaction OFF;
GO

PRINT '48 reaction records inserted successfully';
GO
