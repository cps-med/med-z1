-- Create table: ImmunizationMill.VaccineAdmin
-- Purpose: Cerner vaccine administration event table (CLINICAL_EVENT pattern)
-- Cerner/Oracle Health alignment: CLINICAL_EVENT table for immunizations
--
-- IMPORTANT NOTES:
-- 1. PersonSID = Cerner patient identifier (maps to VistA PatientSID via ICN)
-- 2. PatientICN = Denormalized for joins (same ICN across VistA and Cerner)
-- 3. Series stored as SeriesNumber + TotalInSeries (e.g., "1" and "2" instead of "1 of 2")
-- 4. DoseAmount + DoseUnit separated (Cerner pattern vs VistA combined "0.5 ML")
-- 5. Foreign key to PersonSID omitted (VeteranMill.SPerson has no PK in mock env)

USE CDWWork2;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Cerner vaccine administration event table
CREATE TABLE ImmunizationMill.VaccineAdmin (
    VaccineAdminSID     BIGINT IDENTITY(1,1) PRIMARY KEY,
    PersonSID           BIGINT NOT NULL,                -- Cerner patient ID
    EncounterSID        BIGINT,                         -- Cerner encounter ID
    PatientICN          VARCHAR(50),                    -- Denormalized ICN for joins (CRITICAL)

    -- Vaccine reference
    VaccineCodeSID      BIGINT NOT NULL,                -- FK to ImmunizationMill.VaccineCode

    -- Administration details
    AdministeredDateTime DATETIME NOT NULL,
    SeriesNumber        VARCHAR(50),                    -- "1", "2", "3" (Cerner splits series)
    TotalInSeries       VARCHAR(50),                    -- "2", "3" (total doses in series)
    DoseAmount          VARCHAR(50),                    -- "0.5", "1.0"
    DoseUnit            VARCHAR(50),                    -- "ML", "MG"
    RouteCode           VARCHAR(50),                    -- "IM", "SC", "PO", "ID"
    BodySite            VARCHAR(100),                   -- "LEFT DELTOID", "RIGHT ARM"

    -- Safety tracking
    AdverseReaction     VARCHAR(500),                   -- Adverse reaction text

    -- Provider and location
    ProviderSID         BIGINT,                         -- Ordering/administering provider
    FacilitySID         INT,                            -- Facility/location

    -- Metadata
    IsActive            BIT DEFAULT 1,
    CreatedDateTimeUTC  DATETIME2(3) DEFAULT GETUTCDATE(),

    -- Foreign key to VaccineCode (has proper PK)
    CONSTRAINT FK_VaccineAdmin_VaccineCode
        FOREIGN KEY (VaccineCodeSID) REFERENCES ImmunizationMill.VaccineCode(VaccineCodeSID)

    -- NOTE: Foreign key to PersonSID omitted (VeteranMill.SPerson has no PK in mock)
);
GO

-- Index for patient-centric queries (Cerner PersonSID)
CREATE INDEX IX_VaccineAdmin_Person_Date
    ON ImmunizationMill.VaccineAdmin (PersonSID, AdministeredDateTime DESC);
GO

-- Index for ICN-based queries (CRITICAL for cross-system joins in Silver ETL)
CREATE INDEX IX_VaccineAdmin_ICN_Date
    ON ImmunizationMill.VaccineAdmin (PatientICN, AdministeredDateTime DESC);
GO

-- Index for date-range queries
CREATE INDEX IX_VaccineAdmin_Date
    ON ImmunizationMill.VaccineAdmin (AdministeredDateTime DESC);
GO

-- Filtered index for active records
CREATE INDEX IX_VaccineAdmin_Active
    ON ImmunizationMill.VaccineAdmin (IsActive, PersonSID, AdministeredDateTime DESC)
    WHERE IsActive = 1;
GO

PRINT 'Table ImmunizationMill.VaccineAdmin created successfully with indexes';
GO
