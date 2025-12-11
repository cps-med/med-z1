-- =====================================================================
-- Dim.InsuranceCompany - Insurance Company Dimension Table
-- =====================================================================
-- Purpose: Maps InsuranceCompanySID to insurance company names
-- Used by: SPatient.SPatientInsurance (foreign key relationship)
-- =====================================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Drop table if it exists (for development/testing)
IF OBJECT_ID('Dim.InsuranceCompany', 'U') IS NOT NULL
    DROP TABLE Dim.InsuranceCompany;
GO

-- Create Insurance Company Dimension Table
CREATE TABLE Dim.InsuranceCompany (
    InsuranceCompanySID INT NOT NULL,
    InsuranceCompanyName VARCHAR(100) NOT NULL,
    InsuranceCompanyIEN VARCHAR(50),
    Sta3n SMALLINT,

    CONSTRAINT PK_InsuranceCompany PRIMARY KEY CLUSTERED (InsuranceCompanySID)
);
GO

PRINT 'Table Dim.InsuranceCompany created successfully';
GO
