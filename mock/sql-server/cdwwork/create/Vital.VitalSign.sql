-- Create table: Vital.VitalSign
-- Purpose: Stores actual vital sign measurements
-- VistA alignment: File #120.5 (GMRV VITAL MEASUREMENT)

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE Vital.VitalSign (
    VitalSignSID            BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID              BIGINT NOT NULL,
    VitalTypeSID            INT NOT NULL,
    VitalSignTakenDateTime  DATETIME2(3) NOT NULL,      -- When vital was taken
    VitalSignEnteredDateTime DATETIME2(3),               -- When entered into VistA
    ResultValue             VARCHAR(50),                 -- String representation (e.g., "120/80")

    -- Numeric values for querying/graphing
    NumericValue            DECIMAL(10,2),               -- For single-value vitals (temp, pulse, etc.)
    Systolic                INT,                         -- For BP only
    Diastolic               INT,                         -- For BP only

    -- Metric equivalents (optional, for conversion)
    MetricValue             DECIMAL(10,2),               -- E.g., weight in kg, temp in C

    -- Location and staff
    LocationSID             INT,                         -- Hospital location
    EnteredByStaffSID       INT,                         -- Staff who entered

    -- Quality and status
    IsInvalid               CHAR(1) DEFAULT 'N',         -- Soft delete flag
    EnteredInError          CHAR(1) DEFAULT 'N',

    -- Metadata
    Sta3n                   SMALLINT,
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    UpdatedDateTimeUTC      DATETIME2(3),

    CONSTRAINT FK_VitalSign_Type FOREIGN KEY (VitalTypeSID) REFERENCES Dim.VitalType(VitalTypeSID)
);
GO

-- Indexing (Critical for performance)
CREATE INDEX IX_VitalSign_Patient_Date
    ON Vital.VitalSign(PatientSID, VitalSignTakenDateTime DESC);
GO

CREATE INDEX IX_VitalSign_Type_Date
    ON Vital.VitalSign(VitalTypeSID, VitalSignTakenDateTime DESC);
GO

-- Index for recent vitals queries (widget)
SET QUOTED_IDENTIFIER ON;
GO

CREATE INDEX IX_VitalSign_Patient_Type_Recent
    ON Vital.VitalSign(PatientSID, VitalTypeSID, VitalSignTakenDateTime DESC)
    WHERE IsInvalid = 'N';
GO

PRINT 'Table Vital.VitalSign created successfully with indexes';
GO
