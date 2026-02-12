-- Dim.FamilyRelationship - seed relationship values

USE CDWWork;
GO

SET QUOTED_IDENTIFIER ON;
GO

PRINT 'Inserting Dim.FamilyRelationship values...';
GO

INSERT INTO Dim.FamilyRelationship (RelationshipCode, RelationshipName, Degree, IsActive)
VALUES
    ('MOTHER', 'Mother', 'FIRST_DEGREE', 'Y'),
    ('FATHER', 'Father', 'FIRST_DEGREE', 'Y'),
    ('SISTER', 'Sister', 'FIRST_DEGREE', 'Y'),
    ('BROTHER', 'Brother', 'FIRST_DEGREE', 'Y'),
    ('SON', 'Son', 'FIRST_DEGREE', 'Y'),
    ('DAUGHTER', 'Daughter', 'FIRST_DEGREE', 'Y'),
    ('MAT_GRANDMOTHER', 'Maternal Grandmother', 'SECOND_DEGREE', 'Y'),
    ('MAT_GRANDFATHER', 'Maternal Grandfather', 'SECOND_DEGREE', 'Y'),
    ('PAT_GRANDMOTHER', 'Paternal Grandmother', 'SECOND_DEGREE', 'Y'),
    ('PAT_GRANDFATHER', 'Paternal Grandfather', 'SECOND_DEGREE', 'Y'),
    ('AUNT', 'Aunt', 'SECOND_DEGREE', 'Y'),
    ('UNCLE', 'Uncle', 'SECOND_DEGREE', 'Y'),
    ('COUSIN', 'Cousin', 'OTHER', 'Y'),
    ('UNKNOWN', 'Unknown Relative', 'OTHER', 'Y');
GO

PRINT 'Inserted relationship rows:';
SELECT COUNT(*) AS FamilyRelationshipCount FROM Dim.FamilyRelationship;
GO
