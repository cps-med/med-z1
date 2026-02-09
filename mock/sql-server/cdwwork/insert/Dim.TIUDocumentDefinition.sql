-- =============================================
-- Insert Data: Dim.TIUDocumentDefinition
-- Description: Seed TIU document type definitions (note types)
-- Author: Claude Code
-- Date: 2026-01-02
-- =============================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Enable IDENTITY_INSERT for explicit SID values
SET IDENTITY_INSERT Dim.TIUDocumentDefinition ON;
GO

-- Insert TIU document type definitions
INSERT INTO Dim.TIUDocumentDefinition (
    DocumentDefinitionSID, TIUDocumentTitle, DocumentClass,
    VHAEnterpriseStandardTitle, IsActive, Sta3n
)
VALUES
    -- Progress Notes (100-series)
    (100, 'GEN MED PROGRESS NOTE', 'Progress Notes', 'Physician Progress Note', 1, NULL),
    (101, 'CARDIOLOGY PROGRESS NOTE', 'Progress Notes', 'Cardiology Progress Note', 1, NULL),
    (102, 'PRIMARY CARE NOTE', 'Progress Notes', 'Primary Care Progress Note', 1, NULL),
    (103, 'SPECIALTY CLINIC NOTE', 'Progress Notes', 'Specialty Care Progress Note', 1, NULL),

    -- Consults (200-series)
    (200, 'CARDIOLOGY CONSULT', 'Consults', 'Cardiology Consultation Note', 1, NULL),
    (201, 'NEPHROLOGY CONSULT', 'Consults', 'Nephrology Consultation Note', 1, NULL),
    (202, 'PSYCHIATRY CONSULT', 'Consults', 'Psychiatry Consultation Note', 1, NULL),
    (203, 'NEUROLOGY CONSULT', 'Consults', 'Neurology Consultation Note', 1, NULL),

    -- Discharge Summaries (300-series)
    (300, 'DISCHARGE SUMMARY', 'Discharge Summaries', 'Inpatient Discharge Summary', 1, NULL),
    (301, 'OBSERVATION DISCHARGE', 'Discharge Summaries', 'Observation Discharge Summary', 1, NULL),

    -- Imaging Reports (400-series)
    (400, 'CHEST X-RAY REPORT', 'Imaging', 'Radiology Report - Chest X-Ray', 1, NULL),
    (401, 'CT SCAN REPORT', 'Imaging', 'Radiology Report - CT Scan', 1, NULL),
    (402, 'MRI REPORT', 'Imaging', 'Radiology Report - MRI', 1, NULL);
GO

-- Disable IDENTITY_INSERT
SET IDENTITY_INSERT Dim.TIUDocumentDefinition OFF;
GO

PRINT '13 TIU document type definitions inserted successfully';
GO
