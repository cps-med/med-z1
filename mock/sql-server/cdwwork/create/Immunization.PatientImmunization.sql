-- Create table: Immunization.PatientImmunization
-- Purpose: Stores actual patient immunization records (fact table)
-- VistA alignment: File #9000010.11 (V IMMUNIZATION)

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

CREATE TABLE Immunization.PatientImmunization (
    PatientImmunizationSID  BIGINT IDENTITY(1,1) PRIMARY KEY,
    PatientSID              BIGINT NOT NULL,                -- FK to SPatient.SPatient
    VaccineSID              INT NOT NULL,                   -- FK to Dim.Vaccine
    VisitSID                BIGINT,                         -- FK to encounter (optional)

    -- Administration details
    AdministeredDateTime    DATETIME2(3) NOT NULL,          -- When vaccine was given
    Series                  VARCHAR(50),                    -- "1 of 2", "2 of 2", "BOOSTER", "COMPLETE"
    Dose                    VARCHAR(50),                    -- "0.5 ML", "1 ML"
    Route                   VARCHAR(50),                    -- "IM", "SC", "PO", "ID"
    SiteOfAdministration    VARCHAR(100),                   -- "L DELTOID", "R DELTOID", "LT ARM"

    -- Safety tracking
    Reaction                VARCHAR(255),                   -- Adverse reaction text

    -- Provider and location
    OrderingProviderSID     INT,                            -- FK to provider
    AdministeringProviderSID INT,                           -- FK to provider
    LocationSID             INT,                            -- FK to Dim.Location
    Sta3n                   SMALLINT,                       -- Station number

    -- Additional details
    LotNumber               VARCHAR(50),                    -- Vaccine lot number (recall tracking)
    Comments                VARCHAR(MAX),                   -- Free-text clinical notes

    -- Audit fields
    IsActive                BIT DEFAULT 1,
    CreatedDateTimeUTC      DATETIME2(3) DEFAULT GETUTCDATE(),
    ModifiedDateTimeUTC     DATETIME2(3),

    -- Foreign key constraint for VaccineSID (Dim.Vaccine has proper PK)
    CONSTRAINT FK_PatientImmunization_Vaccine
        FOREIGN KEY (VaccineSID) REFERENCES Dim.Vaccine(VaccineSID)

    -- NOTE: Foreign key constraints omitted for PatientSID and LocationSID
    -- to match existing CDWWork pattern (SPatient.SPatient has no PK defined).
    -- Data integrity enforced at application/ETL layer.
);
GO

-- Index for patient-centric queries (most common: "show me this patient's immunizations")
CREATE INDEX IX_PatientImmunization_Patient_Date
    ON Immunization.PatientImmunization (PatientSID, AdministeredDateTime DESC);
GO

-- Index for vaccine-centric queries ("which patients got Shingrix?")
CREATE INDEX IX_PatientImmunization_Vaccine
    ON Immunization.PatientImmunization (VaccineSID, AdministeredDateTime DESC);
GO

-- Index for date-range queries ("all immunizations last 6 months")
CREATE INDEX IX_PatientImmunization_Date
    ON Immunization.PatientImmunization (AdministeredDateTime DESC);
GO

-- Filtered index for active records only (improves widget performance)
CREATE INDEX IX_PatientImmunization_Active
    ON Immunization.PatientImmunization (IsActive, PatientSID, AdministeredDateTime DESC)
    WHERE IsActive = 1;
GO

PRINT 'Table Immunization.PatientImmunization created successfully with indexes';
GO
