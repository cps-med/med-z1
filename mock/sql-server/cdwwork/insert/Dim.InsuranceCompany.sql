-- =====================================================================
-- Dim.InsuranceCompany - Mock Insurance Company Data
-- =====================================================================
-- Purpose: Insert mock insurance company records for development
-- Note: Includes mix of commercial, government, and special values
-- =====================================================================

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

-- Clear existing data
DELETE FROM Dim.InsuranceCompany;
GO

-- Insert mock insurance companies
INSERT INTO Dim.InsuranceCompany (InsuranceCompanySID, InsuranceCompanyName, InsuranceCompanyIEN, Sta3n)
VALUES
    -- Government Programs
    (1, 'Medicare', '1', 442),
    (2, 'Medicaid', '2', 442),
    (3, 'TRICARE', '3', 442),
    (4, 'VA', '4', 442),
    (5, 'Veterans Affairs', '5', 442),

    -- Commercial Insurers (Major National)
    (10, 'Blue Cross Blue Shield', '10', 442),
    (11, 'Aetna', '11', 442),
    (12, 'UnitedHealthcare', '12', 442),
    (13, 'Cigna', '13', 442),
    (14, 'Humana', '14', 442),

    -- Commercial Insurers (Other)
    (20, 'Kaiser Permanente', '20', 442),
    (21, 'Anthem', '21', 442),
    (22, 'Centene', '22', 442),
    (23, 'Molina Healthcare', '23', 442),

    -- Special Values
    (90, 'Uninsured', '90', 442),
    (91, 'Unknown', '91', 442),
    (92, 'Self-Pay', '92', 442);
GO

PRINT 'Inserted ' + CAST(@@ROWCOUNT AS VARCHAR) + ' insurance company records';
GO

-- Verify data
SELECT
    InsuranceCompanySID,
    InsuranceCompanyName,
    InsuranceCompanyIEN,
    Sta3n
FROM Dim.InsuranceCompany
ORDER BY InsuranceCompanySID;
GO
