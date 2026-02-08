-- EncMill.ProblemList - Cerner/Oracle Health Problem List
-- Purpose: Patient problem list from Cerner Millennium platform (different schema from VistA)
-- Source: Oracle Health (formerly Cerner) problem list
-- Scope: Problems from Cerner-based VA facilities (CDWWork2)
-- Note: Schema intentionally differs from VistA to exercise Silver-layer harmonization

USE CDWWork2;
GO

-- Drop table if exists (for development)
IF OBJECT_ID('EncMill.ProblemList', 'U') IS NOT NULL
    DROP TABLE EncMill.ProblemList;
GO

PRINT 'Creating table EncMill.ProblemList...';
GO

CREATE TABLE EncMill.ProblemList (
    DiagnosisSID BIGINT PRIMARY KEY IDENTITY(2001,1),
    PatientKey INT NOT NULL,
    PatientICN VARCHAR(50),
    FacilityCode INT NOT NULL,

    -- Problem identification (Cerner-specific naming)
    ProblemID VARCHAR(20),
    DiagnosisCode VARCHAR(10),  -- ICD-10 code
    DiagnosisDescription VARCHAR(500),
    ClinicalTermCode VARCHAR(20),  -- SNOMED CT (Cerner uses clinical_term_code)
    ClinicalTermDescription VARCHAR(500),

    -- Problem metadata (Cerner-specific naming)
    StatusCode VARCHAR(20) NOT NULL,  -- A (Active), I (Inactive), R (Resolved)
    OnsetDateTime DATETIME,
    RecordDateTime DATETIME NOT NULL,
    LastUpdateDateTime DATETIME,
    ResolvedDateTime DATETIME,

    -- Clinical context (Cerner-specific naming)
    ResponsibleProviderID INT,
    ResponsibleProviderName VARCHAR(200),
    RecordingLocation VARCHAR(200),
    Comments VARCHAR(1000),

    -- Annotations (Cerner-specific naming)
    ServiceConnectedFlag CHAR(1) DEFAULT 'N',
    AcuteFlag CHAR(1) DEFAULT 'N',
    ChronicFlag CHAR(1) DEFAULT 'N',

    -- Audit fields (Cerner-specific naming)
    CreatedByUserID INT,
    CreatedByUserName VARCHAR(200),
    CreatedDateTime DATETIME,
    ModifiedByUserID INT,
    ModifiedByUserName VARCHAR(200),
    ModifiedDateTime DATETIME
);
GO

-- Create indexes for common queries
CREATE INDEX IX_EncMillProblem_Patient ON EncMill.ProblemList(PatientKey, StatusCode);
CREATE INDEX IX_EncMillProblem_ICN ON EncMill.ProblemList(PatientICN);
CREATE INDEX IX_EncMillProblem_DiagCode ON EncMill.ProblemList(DiagnosisCode);
CREATE INDEX IX_EncMillProblem_ClinTerm ON EncMill.ProblemList(ClinicalTermCode);
CREATE INDEX IX_EncMillProblem_Status ON EncMill.ProblemList(StatusCode);
CREATE INDEX IX_EncMillProblem_Onset ON EncMill.ProblemList(OnsetDateTime);
CREATE INDEX IX_EncMillProblem_Chronic ON EncMill.ProblemList(ChronicFlag) WHERE ChronicFlag = 'Y';
GO

PRINT 'Table EncMill.ProblemList created successfully.';
GO
