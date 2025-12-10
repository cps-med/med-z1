# Patient Flags Research - VA CDW Schema for med-z1

**Document Purpose:** Comprehensive specification for implementing VA Patient Record Flags (PRF) in the med-z1 mock CDW database, synthesized from multiple research sources.

**Last Updated:** 2025-12-09

---

## Executive Summary

**Confirmed:** VA Corporate Data Warehouse (CDW) contains Patient Record Flags data in the **SPatient** domain.

**Source Systems:**
- VistA Patient Record Flags package (FileMan files #26.11 through #26.17)
- Transmitted via HL7 ORU^R01 and QBP^Q11/ORF^R04 messages
- Maps to CDW logical objects in the "Patient Record Flag 1.0" domain

**Recommended Implementation for med-z1:**
- Three-table design: Flag definitions (dimension), Assignments (fact), and History (audit trail)
- All tables in `SPatient` schema due to sensitive narrative content
- Supports both National (Category I) and Local (Category II) flags
- Tracks full audit history with action codes and narrative text

---

## 1. VistA Source Data Model

### 1.1 VistA FileMan Files

The Patient Record Flags package introduces these core files under the `^DGPF` global:

| VistA File # | File Name | CDW Destination | Description |
|--------------|-----------|-----------------|-------------|
| **26.15** | PRF NATIONAL FLAG | `Dim.PatientRecordFlag` | Category I (National) flag definitions |
| **26.11** | PRF LOCAL FLAG | `Dim.PatientRecordFlag` | Category II (Local) flag definitions |
| **26.13** | PRF ASSIGNMENT | `SPatient.PatientRecordFlagAssignment` | Core assignment: patient ↔ flag linkage |
| **26.14** | PRF ASSIGNMENT HISTORY | `SPatient.PatientRecordFlagHistory` | Audit trail of actions and narrative updates |
| **26.16** | PRF TYPE | (Optional) | Usage classifications |
| **26.17-26.22** | HL7 logs and events | (Not needed for mock) | HL7 transmission logs |

**References:**
- [OSEHRA VistA File 26.13 Documentation](https://code.osehra.org/dox/File_26_13.html)
- [ViViaN VistA Documentation - File 26.14](https://vivianr.worldvista.org/dox/Global_XkRHUEYoMjYuMTQ%3D.html)
- [VA VDL - PRF HL7 Interface Specification](https://www.va.gov/vdl/documents/clinical/patient_record_flags/prfhl7is.doc)

### 1.2 Key VistA Field Mappings

**From File #26.13 (PRF ASSIGNMENT):**
- Patient pointer → `PatientSID`
- Flag (pointer to 26.11 or 26.15) → `FlagName`, `FlagCategory`, IENs
- Assignment Date/Time → `AssignmentDateTime`
- Status → `AssignmentStatus`, `IsActive`
- Owner Site → `OwnerSiteSta3n`
- Review Date → `NextReviewDateTime`

**From File #26.14 (PRF ASSIGNMENT HISTORY):**
- `.01` Assignment pointer → `PatientRecordFlagAssignmentSID`
- `.02` Date/Time → `HistoryDateTime`
- `.03` Action (1-5) → `ActionCode`, `ActionName`
- `.04` Entered By → `EnteredByDUZ`
- `.05` Approved By → `ApprovedByDUZ`
- `.06` TIU PN Link → `TiuDocumentIEN`
- `1;0` History Comments → `HistoryComments` (narrative)

**Action Codes (from 26.14 .03 field):**

| Code | Action Name | Semantics |
|------|-------------|-----------|
| 1 | NEW ASSIGNMENT | Flag initially created for patient |
| 2 | CONTINUE | Reviewed and left in effect |
| 3 | INACTIVATE | Flag ended (often with resolution narrative) |
| 4 | REACTIVATE | Flag turned back on |
| 5 | ENTERED IN ERROR | Data quality correction |

### 1.3 HL7 Transmission Format

PRF data is transmitted via HL7 messages:
- **OBR.4** (Universal Service ID) carries flag name and reference to table VA085 (file 26.15)
- **OBX segments** carry:
  - Status: `S~Status~L`
  - Narrative: `N~Narrative~L`
  - Comments: `C~Comment~L`
  - DBRS data: `D~DBRS-Update/Delete~L`

This explains why narrative is treated as sensitive data in CDW.

---

## 2. CDW Schema Mapping

### 2.1 CDW Domain Structure

**Domain Name:** Patient Record Flag 1.0
**Subject Area:** SPatient

**Published CDW Objects** (from VA Vendor Portal CDW Domains workbook):
- `SPatient.PatientRecordFlagAssignment` ← VistA file #26.13
- `SPatient.PatientRecordFlagHistory` ← VistA file #26.14

**Why SPatient Schema?**

1. **Sensitive Narrative Content:** The narrative text contains specific threat details, safety instructions, and clinical reasoning that qualifies as highly sensitive PHI
2. **Access Control:** SPatient schema allows tighter permission controls - users can see that a flag exists without accessing the detailed narrative
3. **Performance:** Separating large text (LOB) fields keeps main tables lean for joining and filtering
4. **CDW Convention:** Matches existing patterns like `SPatient.SPatient`, `SPatient.SPatientAddress`, etc.

---

## 3. Mock CDW Schema Design for med-z1

### 3.1 Design Overview

**Three-table architecture:**

1. **Dim.PatientRecordFlag** (Dimension table)
   - Definitions of National and Local flags
   - Flag metadata: name, category, type, review rules
   - Non-sensitive reference data (uses Dim schema per CDW convention)

2. **SPatient.PatientRecordFlagAssignment** (Core fact table)
   - One row per current assignment of a flag to a patient
   - Metadata only: status, dates, ownership, review schedule
   - **Sensitive narrative stored separately** (see below)

3. **SPatient.PatientRecordFlagHistory** (Audit/history table)
   - One row per history event (assignment, review, inactivation)
   - Contains action codes, timestamps, approvers
   - **Contains sensitive narrative text** in `HistoryComments` field

**Separation Strategy:**
- Assignment table holds structured metadata for filtering/sorting
- History table holds narrative text, loaded only when user requests details
- This mirrors the 1:1 extension pattern used elsewhere in SPatient schema

---

### 3.2 Table Definitions (SQL Server)

#### Table 1: Dim.PatientRecordFlag

```sql
-- Flag Definitions Dimension Table
-- Combines National (Cat I) and Local (Cat II) flags
-- Uses Dim schema per CDW convention for dimension/reference tables
CREATE TABLE Dim.PatientRecordFlag (
    PatientRecordFlagSID        INT IDENTITY(1,1) PRIMARY KEY,

    -- Flag identification
    FlagName                    NVARCHAR(100) NOT NULL,
    FlagType                    VARCHAR(30),          -- 'CLINICAL', 'BEHAVIORAL', 'RESEARCH', 'ADMINISTRATIVE'
    FlagCategory                CHAR(1) NOT NULL,     -- 'I' (National) or 'II' (Local)
    FlagSourceType              CHAR(1) NOT NULL,     -- 'N' (National file 26.15) or 'L' (Local file 26.11)

    -- VistA pointers
    NationalFlagIEN             INT NULL,             -- IEN in file 26.15 (if National)
    LocalFlagIEN                INT NULL,             -- IEN in file 26.11 (if Local)

    -- Review rules (from 26.11 or 26.15)
    ReviewFrequencyDays         INT NULL,             -- How often flag must be reviewed
    ReviewNotificationDays      INT NULL,             -- Days before review to notify

    -- Status
    IsActive                    BIT DEFAULT 1,
    InactivationDate            DATE NULL,

    -- Audit
    CreatedDateTimeUTC          DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedDateTimeUTC          DATETIME2 NULL
);

CREATE INDEX IX_FlagName ON Dim.PatientRecordFlag (FlagName);
CREATE INDEX IX_FlagCategory ON Dim.PatientRecordFlag (FlagCategory, IsActive);
```

**Notes:**
- Category I (National) flags are enterprise-wide, shared via HL7 across all VA facilities
- Category II (Local) flags are facility-specific, only visible at the owning site
- In JLV-style applications, you typically see Cat I from all sites, Cat II only from current user's facility

#### Table 2: SPatient.PatientRecordFlagAssignment

```sql
-- Core Assignment Table (Fact)
-- One row per active or historical assignment of a flag to a patient
CREATE TABLE SPatient.PatientRecordFlagAssignment (
    PatientRecordFlagAssignmentSID  BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Core relationships
    PatientSID                      BIGINT NOT NULL,      -- FK to SPatient.SPatient
    PatientRecordFlagSID            INT NULL,             -- FK to Dim.PatientRecordFlag (optional)

    -- Denormalized flag info (for queries without joining to Dim)
    FlagName                        NVARCHAR(100) NOT NULL,
    FlagCategory                    CHAR(1) NOT NULL,     -- 'I' or 'II'
    FlagSourceType                  CHAR(1) NOT NULL,     -- 'N' or 'L'
    NationalFlagIEN                 INT NULL,
    LocalFlagIEN                    INT NULL,

    -- Assignment state
    IsActive                        BIT NOT NULL,
    AssignmentStatus                VARCHAR(20) NOT NULL, -- 'ACTIVE', 'INACTIVE', 'ENTERED IN ERROR'
    AssignmentDateTime              DATETIME2 NOT NULL,   -- When flag was initially assigned
    InactivationDateTime            DATETIME2 NULL,       -- When flag was inactivated (if applicable)

    -- Ownership and facility tracking
    OwnerSiteSta3n                  VARCHAR(10) NULL,     -- Owning facility (3-digit station number)
    OriginatingSiteSta3n            VARCHAR(10) NULL,     -- Site that created the flag
    LastUpdateSiteSta3n             VARCHAR(10) NULL,     -- Site of last change

    -- Review metadata
    ReviewFrequencyDays             INT NULL,             -- From flag definition
    ReviewNotificationDays          INT NULL,             -- From flag definition
    LastReviewDateTime              DATETIME2 NULL,       -- Last time flag was reviewed
    NextReviewDateTime              DATETIME2 NULL,       -- When flag must be reviewed next

    -- Audit trail
    CreatedDateTimeUTC              DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    UpdatedDateTimeUTC              DATETIME2 NULL,

    -- Foreign key constraints (if using Dim table)
    CONSTRAINT FK_PRFAssign_FlagDim FOREIGN KEY (PatientRecordFlagSID)
        REFERENCES Dim.PatientRecordFlag (PatientRecordFlagSID)
);

-- Critical indexes for patient-centric queries
CREATE INDEX IX_PRFAssign_Patient
    ON SPatient.PatientRecordFlagAssignment (PatientSID, IsActive, FlagCategory);

CREATE INDEX IX_PRFAssign_Review
    ON SPatient.PatientRecordFlagAssignment (NextReviewDateTime, IsActive)
    WHERE NextReviewDateTime IS NOT NULL;

CREATE INDEX IX_PRFAssign_Site
    ON SPatient.PatientRecordFlagAssignment (OwnerSiteSta3n, IsActive);
```

**Design Rationale:**
- **No narrative text here** - keeps table lean for filtering/sorting
- `PatientSID` allows direct joins to `SPatient.SPatient` without intermediate lookups
- `IsActive` flag enables quick filtering to current flags only
- Denormalized `FlagName` and category fields avoid dimension join for common queries
- Station fields (`Sta3n`) track ownership and updates across facilities

#### Table 3: SPatient.PatientRecordFlagHistory

```sql
-- History/Audit Table
-- One row per event (new assignment, review, inactivation, etc.)
-- Contains SENSITIVE narrative text
CREATE TABLE SPatient.PatientRecordFlagHistory (
    PatientRecordFlagHistorySID     BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Relationships
    PatientRecordFlagAssignmentSID  BIGINT NOT NULL,      -- FK to Assignment table
    PatientSID                      BIGINT NOT NULL,      -- Denormalized for easier querying

    -- Event details (direct mapping from VistA file 26.14)
    HistoryDateTime                 DATETIME2 NOT NULL,   -- .02 DATE/TIME
    ActionCode                      TINYINT NOT NULL,     -- .03 ACTION (1-5)
    ActionName                      VARCHAR(50) NOT NULL, -- Decoded action name

    -- User tracking (VistA NEW PERSON file #200 IENs)
    EnteredByDUZ                    INT NOT NULL,         -- .04 ENTERED BY
    EnteredByName                   VARCHAR(100) NULL,    -- Resolved name for display
    ApprovedByDUZ                   INT NOT NULL,         -- .05 APPROVED BY
    ApprovedByName                  VARCHAR(100) NULL,    -- Resolved name for display

    -- Clinical documentation linkage
    TiuDocumentIEN                  INT NULL,             -- .06 TIU PN LINK (Progress Note #8925)

    -- SENSITIVE: Narrative text explaining the action
    HistoryComments                 NVARCHAR(MAX) NULL,   -- 1;0 HISTORY COMMENTS (word-processing field)

    -- Facility context
    EventSiteSta3n                  VARCHAR(10) NULL,     -- Site where this event occurred

    -- Audit
    CreatedDateTimeUTC              DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

    -- Foreign key
    CONSTRAINT FK_PRFHist_Assignment FOREIGN KEY (PatientRecordFlagAssignmentSID)
        REFERENCES SPatient.PatientRecordFlagAssignment (PatientRecordFlagAssignmentSID)
);

-- Indexes for timeline queries
CREATE INDEX IX_PRFHist_Assignment
    ON SPatient.PatientRecordFlagHistory (PatientRecordFlagAssignmentSID, HistoryDateTime);

CREATE INDEX IX_PRFHist_Patient
    ON SPatient.PatientRecordFlagHistory (PatientSID, HistoryDateTime);

CREATE INDEX IX_PRFHist_Action
    ON SPatient.PatientRecordFlagHistory (ActionCode, HistoryDateTime);
```

**Design Rationale:**
- **Contains sensitive narrative** in `HistoryComments` field - this is why it's in SPatient schema
- Each history row captures a specific event: initial assignment, review, continuation, inactivation
- `ActionCode` maps directly to VistA ACTION field values (1-5)
- TIU linkage allows tracing to associated clinical notes
- Denormalized `PatientSID` enables patient-level queries without joining through Assignment table

---

## 4. Sample Data for med-z1 Mock Database

### 4.1 Flag Definitions (Dimension Data)

```sql
-- Insert common National (Category I) and Local (Category II) flags
INSERT INTO Dim.PatientRecordFlag
    (FlagName, FlagType, FlagCategory, FlagSourceType, NationalFlagIEN, LocalFlagIEN,
     ReviewFrequencyDays, ReviewNotificationDays)
VALUES
    -- Category I (National) Flags
    ('HIGH RISK FOR SUICIDE', 'CLINICAL', 'I', 'N', 1, NULL, 90, 7),
    ('BEHAVIORAL', 'BEHAVIORAL', 'I', 'N', 2, NULL, 730, 30),
    ('CRISIS NOTE', 'CLINICAL', 'I', 'N', 3, NULL, 180, 14),
    ('VIOLENCE PREVENTION', 'BEHAVIORAL', 'I', 'N', 4, NULL, 365, 30),

    -- Category II (Local) Flags
    ('RESEARCH STUDY', 'RESEARCH', 'II', 'L', NULL, 5, 365, 30),
    ('DRUG SEEKING BEHAVIOR', 'BEHAVIORAL', 'II', 'L', NULL, 6, 180, 14),
    ('ELOPEMENT RISK', 'CLINICAL', 'II', 'L', NULL, 7, 90, 7),
    ('PATIENT ADVOCATE REFERRAL', 'ADMINISTRATIVE', 'II', 'L', NULL, 8, 365, 30);
```

**Common Flag Types:**
- **CLINICAL:** Medical/safety concerns (suicide risk, elopement, communicable disease)
- **BEHAVIORAL:** Disruptive behavior, threatening conduct, drug-seeking
- **RESEARCH:** Patient enrolled in research study, special protocols
- **ADMINISTRATIVE:** Patient advocate involvement, legal holds, special instructions

### 4.2 Sample Patient Flag Assignments

Assumes you have patients with `PatientSID` values 100001-100036 in your `SPatient.SPatient` table.

```sql
-- Sample assignments for several patients
INSERT INTO SPatient.PatientRecordFlagAssignment
    (PatientSID, PatientRecordFlagSID, FlagName, FlagCategory, FlagSourceType,
     NationalFlagIEN, LocalFlagIEN, IsActive, AssignmentStatus,
     AssignmentDateTime, InactivationDateTime,
     OwnerSiteSta3n, OriginatingSiteSta3n, LastUpdateSiteSta3n,
     ReviewFrequencyDays, ReviewNotificationDays, LastReviewDateTime, NextReviewDateTime)
VALUES
    -- Patient 1: Active High Risk for Suicide flag
    (100001, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-11-15 09:30:00', NULL,
     '518', '518', '518', 90, 7, '2025-01-15 10:00:00', '2025-04-15 10:00:00'),

    -- Patient 2: Inactive Behavioral flag (resolved)
    (100002, 2, 'BEHAVIORAL', 'I', 'N', 2, NULL,
     0, 'INACTIVE', '2023-08-01 14:00:00', '2024-03-10 11:45:00',
     '663', '663', '663', 730, 30, '2024-02-01 09:00:00', NULL),

    -- Patient 5: Active Violence Prevention flag
    (100005, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-06-20 13:15:00', NULL,
     '528', '528', '528', 365, 30, '2024-12-01 14:00:00', '2025-06-20 14:00:00'),

    -- Patient 7: Active local Research Study flag
    (100007, 5, 'RESEARCH STUDY', 'II', 'L', NULL, 5,
     1, 'ACTIVE', '2024-09-10 08:00:00', NULL,
     '442', '442', '442', 365, 30, NULL, '2025-09-10 08:00:00'),

    -- Patient 10: Active Drug Seeking Behavior (local)
    (100010, 6, 'DRUG SEEKING BEHAVIOR', 'II', 'L', NULL, 6,
     1, 'ACTIVE', '2024-10-05 16:30:00', NULL,
     '589', '589', '589', 180, 14, NULL, '2025-04-03 16:30:00'),

    -- Patient 15: Multiple flags (both active)
    (100015, 1, 'HIGH RISK FOR SUICIDE', 'I', 'N', 1, NULL,
     1, 'ACTIVE', '2024-07-22 11:00:00', NULL,
     '640', '640', '640', 90, 7, '2024-12-05 09:30:00', '2025-03-05 09:30:00'),

    (100015, 4, 'VIOLENCE PREVENTION', 'I', 'N', 4, NULL,
     1, 'ACTIVE', '2024-07-22 11:15:00', NULL,
     '640', '640', '640', 365, 30, NULL, '2025-07-22 11:15:00');
```

**Station Numbers (Sta3n) used above:**
- 518: Northport VA Medical Center
- 528: Upstate New York HCS (Buffalo)
- 442: Cheyenne VA Medical Center
- 589: VA Southern Nevada Healthcare System
- 640: Palo Alto VA Medical Center
- 663: Puget Sound VA Medical Center

### 4.3 Sample History Records

```sql
-- Suppose the identity values assigned above are:
-- PatientRecordFlagAssignmentSID 1 = Patient 100001, HIGH RISK FOR SUICIDE
-- PatientRecordFlagAssignmentSID 2 = Patient 100002, BEHAVIORAL
-- etc.

INSERT INTO SPatient.PatientRecordFlagHistory
    (PatientRecordFlagAssignmentSID, PatientSID, HistoryDateTime, ActionCode, ActionName,
     EnteredByDUZ, EnteredByName, ApprovedByDUZ, ApprovedByName, TiuDocumentIEN,
     HistoryComments, EventSiteSta3n)
VALUES
    -- Patient 100001: HIGH RISK FOR SUICIDE - Initial assignment
    (1, 100001, '2024-11-15 09:30:00', 1, 'NEW ASSIGNMENT',
     12345, 'Dr. Sarah Johnson', 67890, 'Dr. Michael Chen (Chief of Staff)',
     900001,
     N'Flag created after ED visit for suicidal ideation on 11/14/24. Patient expressed intent with plan. Safety plan established and documented in linked TIU note. Patient admitted to Mental Health ward. Contact: Dr. Johnson x5542 or VA Police if patient presents.',
     '518'),

    -- Patient 100001: 90-day review - continued
    (1, 100001, '2025-01-15 10:00:00', 2, 'CONTINUE',
     23456, 'Dr. Emily Rodriguez', 67890, 'Dr. Michael Chen (Chief of Staff)',
     900250,
     N'Reviewed in Suicide Prevention team meeting 1/15/25. Veteran remains at elevated risk based on PHQ-9 score of 18 and continued stressors (housing instability, chronic pain). Safety plan reviewed and updated. Continue flag for next 90-day period.',
     '518'),

    -- Patient 100002: BEHAVIORAL - Initial assignment
    (2, 100002, '2023-08-01 14:00:00', 1, 'NEW ASSIGNMENT',
     34567, 'Patricia Williams, RN', 78901, 'Dr. Robert Martinez (Chief of Staff)',
     901000,
     N'History of aggressive behavior towards staff on 7/30/23. Patient became verbally threatening when asked to wait for prescription. Implemented two-person escort policy and de-escalation protocol per VHA Directive 2010-053. Contact: Nurse Williams x3421 or VA Police for standby.',
     '663'),

    -- Patient 100002: BEHAVIORAL - Inactivated after improvement
    (2, 100002, '2024-03-10 11:45:00', 3, 'INACTIVATE',
     34567, 'Patricia Williams, RN', 78901, 'Dr. Robert Martinez (Chief of Staff)',
     901450,
     N'Behavioral issues stable for >6 months with no incidents. Patient completed anger management program and demonstrates improved coping skills. Staff report positive interactions. Flag inactivated per policy. Will monitor; can reactivate if issues recur.',
     '663'),

    -- Patient 100005: VIOLENCE PREVENTION - Initial assignment
    (3, 100005, '2024-06-20 13:15:00', 1, 'NEW ASSIGNMENT',
     45678, 'James Anderson, LCSW', 89012, 'Dr. Lisa Thompson (Chief of Staff)',
     902000,
     N'History of violent outbursts documented in file. Veteran has PTSD with combat trauma. Triggered by loud noises and crowded spaces. RECOMMEND: Quiet exam rooms, minimize wait times, staff awareness of triggers. Contact Social Work (x4200) or VA Police if de-escalation needed.',
     '528'),

    -- Patient 100005: VIOLENCE PREVENTION - 6-month review continued
    (3, 100005, '2024-12-01 14:00:00', 2, 'CONTINUE',
     45678, 'James Anderson, LCSW', 89012, 'Dr. Lisa Thompson (Chief of Staff)',
     902300,
     N'6-month review completed. Veteran engaged in PTSD treatment with improvement in symptom management. However, risk factors persist. Continue flag and current precautions. Next review June 2025.',
     '528');
```

**Key Narrative Elements:**
- **Clinical context:** Why was flag created? What happened?
- **Risk factors:** Specific behaviors, triggers, or conditions
- **Recommendations:** What should staff do? ("RECOMMEND: ...")
- **Contact information:** Who to call in crisis situations
- **Review outcomes:** For CONTINUE actions, why flag remains necessary

---

## 5. Querying Patient Flags for UI

### 5.1 Get All Active Flags for a Patient

This query is suitable for the "View Patient Flags" modal in med-z1.

```sql
DECLARE @PatientSID BIGINT = 100001;  -- Example ICN100001

SELECT
    a.PatientRecordFlagAssignmentSID,
    a.FlagName,
    a.FlagCategory,
    CASE
        WHEN a.FlagCategory = 'I' THEN 'National'
        WHEN a.FlagCategory = 'II' THEN 'Local'
    END AS FlagScope,
    a.FlagSourceType,
    a.AssignmentStatus,
    a.AssignmentDateTime,
    a.OwnerSiteSta3n,
    a.ReviewFrequencyDays,
    a.NextReviewDateTime,
    CASE
        WHEN a.NextReviewDateTime < GETDATE() THEN 'OVERDUE'
        WHEN DATEDIFF(DAY, GETDATE(), a.NextReviewDateTime) <= a.ReviewNotificationDays THEN 'DUE SOON'
        ELSE 'CURRENT'
    END AS ReviewStatus,
    h.HistoryDateTime AS LastActionDateTime,
    h.ActionName AS LastAction,
    h.EnteredByName AS LastEnteredBy,
    h.HistoryComments AS LastNarrative
FROM SPatient.PatientRecordFlagAssignment a
-- Get most recent history record for each assignment
OUTER APPLY (
    SELECT TOP 1
        HistoryDateTime,
        ActionName,
        EnteredByName,
        HistoryComments
    FROM SPatient.PatientRecordFlagHistory h
    WHERE h.PatientRecordFlagAssignmentSID = a.PatientRecordFlagAssignmentSID
    ORDER BY h.HistoryDateTime DESC
) h
WHERE a.PatientSID = @PatientSID
  AND a.IsActive = 1
ORDER BY
    CASE WHEN a.FlagCategory = 'I' THEN 1 ELSE 2 END,  -- National flags first
    a.AssignmentDateTime DESC;
```

**Returns:**
- All active flags for the patient
- Latest action and narrative for each flag
- Review status (current, due soon, overdue)
- Ownership and timeline information

### 5.2 Get Flag Count for Patient (for badge display)

```sql
DECLARE @PatientSID BIGINT = 100001;

SELECT
    COUNT(*) AS TotalActiveFlags,
    SUM(CASE WHEN FlagCategory = 'I' THEN 1 ELSE 0 END) AS NationalFlags,
    SUM(CASE WHEN FlagCategory = 'II' THEN 1 ELSE 0 END) AS LocalFlags,
    SUM(CASE WHEN NextReviewDateTime < GETDATE() THEN 1 ELSE 0 END) AS OverdueForReview
FROM SPatient.PatientRecordFlagAssignment
WHERE PatientSID = @PatientSID
  AND IsActive = 1;
```

**Use in UI:**
- Display count in badge on "View Flags" button
- Different styling for overdue flags (red badge)

### 5.3 Get Complete Flag History Timeline

For detailed flag view or audit purposes:

```sql
DECLARE @PatientRecordFlagAssignmentSID BIGINT = 1;

SELECT
    h.HistoryDateTime,
    h.ActionCode,
    h.ActionName,
    h.EnteredByName,
    h.ApprovedByName,
    h.TiuDocumentIEN,
    h.HistoryComments,
    h.EventSiteSta3n
FROM SPatient.PatientRecordFlagHistory h
WHERE h.PatientRecordFlagAssignmentSID = @PatientRecordFlagAssignmentSID
ORDER BY h.HistoryDateTime DESC;
```

**Returns:**
- Complete audit trail for a specific flag assignment
- All review actions, continuations, and status changes
- Full narrative history

---

## 6. Business Rules and Implementation Guidance

### 6.1 Category I vs. Category II Flags

**Category I (National):**
- Shared across **all VA facilities** via HL7 synchronization
- Visible to any VA provider accessing the patient record
- Examples: High Risk for Suicide, Behavioral flags with enterprise impact
- Typically have stricter review requirements (90-180 days)

**Category II (Local):**
- **Facility-specific**, only visible at the owning site
- Not transmitted via HL7 to other facilities
- Examples: Research study participation, local administrative flags
- More flexible review periods (up to 365 days)

**Implementation for med-z1:**
- In a JLV-style viewer aggregating multi-site data:
  - Category I flags appear from all facilities
  - Category II flags appear only if user is viewing data from that facility
- Consider filtering based on user's current facility context

### 6.2 Narrative Display and Security

**Critical UI Consideration:**
The narrative text in `HistoryComments` contains:
- Specific threat details ("Patient stated 'I will kill you'")
- Safety instructions ("Call VA Police immediately")
- Clinical reasoning and risk assessment
- PHI and sensitive behavioral information

**Recommended UI Pattern:**
1. **Initial view:** Show flag name, category, dates (from Assignment table)
2. **"View Details" action:** Requires user click/confirmation
3. **Details view:** Display narrative text (from History table)
4. **Access logging:** Log who viewed sensitive narratives and when

**Example UI workflow:**
```
[Flag Card]
⚠️ HIGH RISK FOR SUICIDE
Category: National | Assigned: 2024-11-15 | Review: 2025-04-15

[Button: "View Safety Details"]
  ↓ (User clicks, triggers lazy load)
  ↓ (Query SPatient.PatientRecordFlagHistory)
  ↓
[Expanded Details Panel]
Narrative: "Flag created after ED visit for suicidal ideation..."
Contact: Dr. Johnson x5542 or VA Police
[Close Details]
```

### 6.3 Review Date Logic

**Review requirements:**
- Each flag has a `ReviewFrequencyDays` (e.g., 90 days for suicide risk)
- `NextReviewDateTime` = `LastReviewDateTime` + `ReviewFrequencyDays`
- `ReviewNotificationDays` determines when to alert users (e.g., 7 days before)

**Review states:**
- **CURRENT:** `NextReviewDateTime` > GETDATE() + `ReviewNotificationDays`
- **DUE SOON:** GETDATE() between (`NextReviewDateTime` - `ReviewNotificationDays`) and `NextReviewDateTime`
- **OVERDUE:** `NextReviewDateTime` < GETDATE()

**Important:** Overdue flags remain **active** until explicitly reviewed and either continued or inactivated. An overdue flag does NOT automatically inactivate.

### 6.4 Lazy Loading Pattern

**Performance optimization:**

1. **List view query:** Join only to Assignment table
   ```sql
   SELECT FlagName, FlagCategory, AssignmentDateTime, NextReviewDateTime
   FROM SPatient.PatientRecordFlagAssignment
   WHERE PatientSID = @PatientSID AND IsActive = 1;
   ```

2. **Detail view query:** Load history only when user clicks "View Details"
   ```sql
   SELECT HistoryComments, ActionName, HistoryDateTime
   FROM SPatient.PatientRecordFlagHistory
   WHERE PatientRecordFlagAssignmentSID = @AssignmentSID
   ORDER BY HistoryDateTime DESC;
   ```

**Benefits:**
- Faster initial page load
- Reduced memory footprint for large text fields
- Supports granular security (can restrict History table access)

---

## 7. ETL Pipeline Considerations for Phase 3

When implementing the Bronze → Silver → Gold → PostgreSQL pipeline for flags:

### 7.1 Bronze Layer
- **Source:** Mock SQL Server `SPatient.PatientRecordFlagAssignment` and `SPatient.PatientRecordFlagHistory`
- **Output:** Parquet files with minimal transformation
- **File structure:**
  ```
  lake/bronze/patient_record_flag_assignment/
    └── patient_record_flag_assignment_YYYYMMDD.parquet
  lake/bronze/patient_record_flag_history/
    └── patient_record_flag_history_YYYYMMDD.parquet
  ```

### 7.2 Silver Layer
- **Transformation:**
  - Harmonize if multiple source systems (in med-z1, only one CDW mock)
  - Resolve lookups (Station names, provider names from DUZ)
  - Data quality checks (missing required fields, invalid dates)
- **Output:** Cleaned Parquet files with consistent schema

### 7.3 Gold Layer
- **Transformation:**
  - Create patient-centric views
  - Calculate review status (CURRENT, DUE SOON, OVERDUE)
  - Join Assignment ↔ History to create denormalized flag view
- **Output:** Query-optimized Parquet suitable for PostgreSQL load

### 7.4 PostgreSQL Serving DB
- Load Gold Parquet into PostgreSQL tables (same schema as above)
- Create indexes for patient-centric queries
- Consider materialized views for common queries

---

## 8. Sample Patients Distribution Recommendation

For your 36-patient mock database:

| Flag Status | Count | Example Patients |
|-------------|-------|------------------|
| No active flags | 20 | Most patients (baseline) |
| 1 active flag | 10 | Common scenario |
| 2+ active flags | 3 | Complex cases |
| Historical (inactive) flags only | 3 | Resolved issues |

**Suggested flag type distribution:**
- 5-6 patients: HIGH RISK FOR SUICIDE (Cat I)
- 3-4 patients: BEHAVIORAL (Cat I or II)
- 2-3 patients: VIOLENCE PREVENTION (Cat I)
- 2-3 patients: Local flags (RESEARCH STUDY, DRUG SEEKING, etc.)
- 1-2 patients: Multiple concurrent flags

**Review status distribution:**
- 70% CURRENT (within review window)
- 20% DUE SOON (approaching review date)
- 10% OVERDUE (past review date)

---

## 9. References and Resources

### 9.1 VA and VistA Documentation
- [OSEHRA VistA File 26.13 (PRF Assignment)](https://code.osehra.org/dox/File_26_13.html)
- [ViViaN VistA File 26.14 (PRF History)](https://vivianr.worldvista.org/dox/Global_XkRHUEYoMjYuMTQ%3D.html)
- [ViViaN VistA File 26.11 (PRF Local Flag)](https://vivian.worldvista.org/dox/Global_XkRHUEYoMjYuMTE%3D.html)
- [VA VDL - PRF HL7 Interface Specification](https://www.va.gov/vdl/documents/clinical/patient_record_flags/prfhl7is.doc)
- [VA VDL - PRF Release Notes](https://www.va.gov/VDL/documents/Clinical/Patient_Record_Flags/prfrn.pdf)

### 9.2 CDW Architecture
- [VA VINCI Architecture](https://www.hsrd.research.va.gov/for_researchers/vinci/architecture.cfm)
- VA Vendor Portal - CDW Domains Workbook (requires VA network access)

### 9.3 Clinical Policy References
- VHA Directive 2010-053: Patient Record Flags
- IHS Patient Record Flags Phase III User Guide

---

## 10. Next Steps for med-z1 Implementation

### 10.1 Immediate Actions (Mock Database Setup)

1. **Create schemas and tables:**
   ```bash
   # Execute DDL from Section 3.2 in SQL Server
   sqlcmd -S localhost -U sa -i create_patient_flags_schema.sql
   ```

2. **Populate sample data:**
   ```bash
   # Insert flag definitions and assignments from Section 4
   sqlcmd -S localhost -U sa -i insert_patient_flags_sample_data.sql
   ```

3. **Test queries:**
   ```bash
   # Verify data with queries from Section 5
   sqlcmd -S localhost -U sa -i test_patient_flags_queries.sql
   ```

### 10.2 Phase 3 Preparation

1. **Create Phase 3 design specification:**
   - Use this research document as foundation
   - Create `docs/patient-flags-design.md` (similar to `patient-topbar-design.md`)
   - Define ETL pipeline specifics
   - Design API endpoints
   - Design UI/UX for flags modal

2. **Update implementation roadmap:**
   - Add detailed tasks for Phase 3
   - Estimate timeline (1 week per roadmap)

3. **Prepare for ETL development:**
   - Review Bronze ETL pattern from patient demographics
   - Plan Silver transformations (minimal for single-source mock)
   - Design Gold schema for PostgreSQL

---

## Appendix A: Comparison to Real CDW

**What we know for certain:**
- ✅ CDW has `SPatient.PatientRecordFlagAssignment` table
- ✅ CDW has `SPatient.PatientRecordFlagHistory` table
- ✅ Source is VistA files #26.13 and #26.14
- ✅ Data is in SPatient domain due to sensitivity

**What we inferred from VistA/HL7 specs:**
- Field names and types based on FileMan definitions
- Business logic from VHA directives and user guides
- HL7 message structure from PRF HL7 spec

**Production differences to expect:**
- Exact column names may differ (e.g., `Sta3n` vs `StationNumber`)
- Additional audit fields (ETL timestamps, source system IDs)
- Possibly more normalization (separate Station dimension table)
- Additional views abstracting the raw tables
- Stricter security/permissions on SPatient tables

**Migration strategy:**
When you eventually connect to real CDW:
1. Query information schema: `SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'PatientRecordFlagAssignment'`
2. Compare to mock schema
3. Adjust ETL and API queries as needed
4. Core business logic should remain unchanged

---

## Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-09 | AI Research Synthesis | Initial comprehensive specification combining two research documents |

---

**End of Document**
