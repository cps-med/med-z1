-- Create table: Vital.VitalSignQualifier
-- Purpose: Many-to-many relationship between VitalSign and Qualifiers
-- Example: A BP measurement can have multiple qualifiers (SITTING + LEFT ARM + ADULT cuff)

USE CDWWork;
GO

CREATE TABLE Vital.VitalSignQualifier (
    VitalSignQualifierSID   BIGINT IDENTITY(1,1) PRIMARY KEY,
    VitalSignSID            BIGINT NOT NULL,
    VitalQualifierSID       INT NOT NULL,

    CONSTRAINT FK_VSQual_Sign FOREIGN KEY (VitalSignSID)
        REFERENCES Vital.VitalSign(VitalSignSID),
    CONSTRAINT FK_VSQual_Qualifier FOREIGN KEY (VitalQualifierSID)
        REFERENCES Dim.VitalQualifier(VitalQualifierSID)
);
GO

-- Index for fast retrieval of qualifiers for a specific vital sign
CREATE INDEX IX_VitalSignQualifier_SignID
    ON Vital.VitalSignQualifier(VitalSignSID);
GO

PRINT 'Table Vital.VitalSignQualifier created successfully with index';
GO
