-- Dim.FamilyRelationship - family member relationship dimension
-- Purpose: Standard relationship values for family-history domain

USE CDWWork;
GO

IF OBJECT_ID('Dim.FamilyRelationship', 'U') IS NOT NULL
    DROP TABLE Dim.FamilyRelationship;
GO

PRINT 'Creating table Dim.FamilyRelationship...';
GO

CREATE TABLE Dim.FamilyRelationship (
    FamilyRelationshipSID INT PRIMARY KEY IDENTITY(1,1),
    RelationshipCode VARCHAR(30) NOT NULL UNIQUE,
    RelationshipName VARCHAR(100) NOT NULL,
    Degree VARCHAR(20) NOT NULL,           -- FIRST_DEGREE, SECOND_DEGREE, OTHER
    IsActive CHAR(1) NOT NULL DEFAULT 'Y',
    CreatedDateTime DATETIME NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_FamilyRelationship_Code
    ON Dim.FamilyRelationship(RelationshipCode);
GO

CREATE INDEX IX_FamilyRelationship_Degree
    ON Dim.FamilyRelationship(Degree, IsActive);
GO

PRINT 'Table Dim.FamilyRelationship created successfully.';
GO
