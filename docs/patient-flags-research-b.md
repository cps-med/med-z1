PROMPT:
I am adding Patient Flags functionality to the med-z1 VA JLV modernization application that I am developing. I am hoping to get Patient Flag data from the VA Corporate Data Warehouse (CDW), but I am not sure if CDW contains this data and if it does contain the data, which schema and view name it exists in. I would like to better understand the VA CDW flags schema so that I can mock it up in my local SQL Server database. Please research this topic to help me understand the VA CDW cdwwork database table structure and sample data for flags records. Attached are two relatively old PDS documents that provide information on the VistA (and possibly CPRS) design of the Patient Records Flag package. As part of your research, please include OSEHRA and/or Open VistA websites or any other useful informaton sources. There may be publicly available information from VA on the CDW layout.

RESPONSE:
Short version:

* Yes, CDW **does** have Patient Record Flag data.
* In the logical CDW model it sits in the **SPatient** domain as:

  * `SPatient.PatientRecordFlagAssignment` (from VistA **PRF ASSIGNMENT** file #26.13)
  * `SPatient.PatientRecordFlagHistory` (from VistA **PRF ASSIGNMENT HISTORY** file #26.14) ([Vendor Portal][1])
* The *precise* CDWWork table layouts are not public, but between:

  * the VistA PRF FileMan definitions, ([vivianr.worldvista.org][2])
  * the PRF HL7 Interface Specification, ([Veterans Affairs][3])
  * and the CDW Domains workbook snippet for “Patient Record Flag 1.0” ([Vendor Portal][1])
    we can reconstruct a very CDW-like schema that’s good enough to mock in your local SQL Server / `cdwwork` for med-z1.

Below I’ll:

1. Tie PRF in VistA / CPRS to CDW
2. Show the CDW logical objects we *know* exist
3. Propose practical `SPatient.PatientRecordFlagAssignment` and `SPatient.PatientRecordFlagHistory` table designs (T-SQL)
4. Give a few realistic sample rows and how you’d query them for a JLV-style UI.

---

## 1. VistA PRF data model – what CDW is ingesting

The Patient Record Flags package introduces a small cluster of FileMan files under the `^DGPF` global: ([vistapedia.com][4])

* **26.11 – PRF LOCAL FLAG** (`^DGPF(26.11`)

  * Category II **local** flags; includes review frequency and notification days. ([vivian.worldvista.org][5])
* **26.12 – PRF LOCAL FLAG HISTORY**
* **26.13 – PRF ASSIGNMENT** (`^DGPF(26.13`)

  * The core “this patient has this flag” record.
* **26.14 – PRF ASSIGNMENT HISTORY** (`^DGPF(26.14`)

  * History/audit for each assignment (new, continue, inactivate, etc.). ([vivianr.worldvista.org][2])
* **26.15 – PRF NATIONAL FLAG**
* **26.16 – PRF TYPE** (usage classifications) ([Veterans Affairs][6])
* **26.17–26.22 – HL7 logs and events**

From the **26.14 PRF ASSIGNMENT HISTORY** FileMan DD: ([vivianr.worldvista.org][2])

Key fields (I’ll paraphrase):

* `.01 NUMBER` – internal entry number
* `.01 (pointer)` – **PRF ASSIGNMENT** (#26.13) – the parent assignment
* `.02 DATE/TIME` – when the event occurred (initial assignment or review date/time)
* `.03 ACTION` –

  * `1` NEW ASSIGNMENT
  * `2` CONTINUE
  * `3` INACTIVATE
  * `4` REACTIVATE
  * `5` ENTERED IN ERROR
* `.04 ENTERED BY` – pointer to NEW PERSON (#200)
* `.05 APPROVED BY` – pointer to NEW PERSON (#200); output-transformed to “CHIEF OF STAFF” when POSTMASTER (.5) is stored
* `.06 TIU PN LINK` – pointer to TIU DOCUMENT (#8925) – linked progress note
* `1;0 HISTORY COMMENTS` – word-processing comments/narrative text

From **26.11 PRF LOCAL FLAG** you also get: ([vivian.worldvista.org][5])

* Review frequency (days)
* Notification days before review date

The **PRF HL7 Interface Specification** (your `prfhl7is.docx`) and the public VDL copy show that: ([Veterans Affairs][3])

* PRF assignments are sent as **ORU^R01** and **QBP^Q11/ORF^R04** messages.
* **OBR.4 (Universal Service ID)** has:

  1. PRF NATIONAL FLAG IEN
  2. Flag name
  3. Table `VA085` (Patient Record Flags), which references file 26.15.
* **OBX** segments carry:

  * Status (“S~Status~L”)
  * Narrative (“N~Narrative~L”)
  * Comments (“C~Comment~L”)
  * DBRS data (“D~DBRS-Update/Delete~L”)
    with `OBX.5` pulling from ACTION (.03) and narrative/DBRS fields in file 26.14.

Net: CDW is fundamentally ingesting:

* **Assignments** (26.13) – patient + flag + high-level status/ownership/review metadata
* **History** (26.14) – timeline of actions + narrative and TIU linkage.

That’s exactly what you want to mimic in `cdwwork`.

---

## 2. Where this appears in CDW

From a public **“CDW Domains”** workbook (posted on VA’s Vendor Portal), you get a mapping row: ([Vendor Portal][1])

> Patient Record Flag 1.0, **SPatient**, **PatientRecordFlagAssignment**, 13, PRF ASSIGNMENT (26.13) …
> SPatient, **PatientRecordFlagHistory**, 13, PRF ASSIGNMENT HISTORY (26.14) …

This tells you:

* There is a CDW domain/version “**Patient Record Flag 1.0**”.
* It lives in the **SPatient** subject area.
* It exposes at least two tables/views:

  * `SPatient.PatientRecordFlagAssignment`

    * Source: VistA **PRF ASSIGNMENT** (file #26.13).
  * `SPatient.PatientRecordFlagHistory`

    * Source: VistA **PRF ASSIGNMENT HISTORY** (file #26.14).

We don’t get all the columns, but based on:

* Standard CDW naming (e.g., `SPatient.SPatient`, `SPatient.SPatientTreatingFacility`, etc.)
* VistA PRF file structure
* HL7 content (OBR/OBX segments) ([Veterans Affairs][3])

we can build a very plausible CDW-style mock that will feel “right” when you eventually hook to a real CDW instance.

---

## 3. CDW-style mock schema for `cdwwork`

### 3.1. High-level design

You can think of three main pieces:

1. **Flag dimension / lookup** (optional in your mock)

   * National vs Local flags, flag name, category (I/II), usage type (from 26.16), review rules.

2. **SPatient.PatientRecordFlagAssignment**

   * One row per **current assignment** of a flag to a patient (26.13).
   * Contains pointers to patient, flag, ownership and state.

3. **SPatient.PatientRecordFlagHistory**

   * One row per **history event** (26.14) related to an assignment.
   * Contains action code, timestamp, user/approver, narrative, TIU note link.

Below is a concrete SQL Server design that keeps those relationships and uses CDW-ish conventions (`SID` keys, `Sta3n`, etc.).

---

### 3.2. `SPatient.PatientRecordFlagAssignment` (mock)

```sql
-- Create schema if you want to mirror CDW
CREATE SCHEMA SPatient;
GO

CREATE TABLE SPatient.PatientRecordFlagAssignment (
    PatientRecordFlagAssignmentSID  BIGINT IDENTITY(1,1) PRIMARY KEY,

    -- Core relationships
    PatientSID                      BIGINT      NOT NULL,  -- FK to SPatient.SPatient in your mock
    FlagName                        NVARCHAR(100) NOT NULL, -- e.g. 'HIGH RISK FOR SUICIDE'
    FlagCategory                    CHAR(1)     NOT NULL,   -- 'I' or 'II'
    FlagSourceType                  CHAR(1)     NOT NULL,   -- 'N' (National) / 'L' (Local)
    NationalFlagIEN                 INT         NULL,       -- Pointer to 26.15
    LocalFlagIEN                    INT         NULL,       -- Pointer to 26.11

    -- Assignment state (from 26.13 + derived)
    IsActive                        BIT         NOT NULL,
    AssignmentStatus                VARCHAR(20) NOT NULL,   -- 'ACTIVE','INACTIVE','ENTERED IN ERROR'
    AssignmentDateTime              DATETIME2   NOT NULL,   -- Initial assign date/time
    InactivationDateTime            DATETIME2   NULL,

    -- Ownership / sites
    OwnerSiteSta3n                  VARCHAR(10) NULL,       -- Owning facility (3-digit)
    OriginatingSiteSta3n            VARCHAR(10) NULL,       -- Site that created flag
    LastUpdateSiteSta3n             VARCHAR(10) NULL,       -- Site of last change

    -- Review metadata (from flag + assignment)
    ReviewFrequencyDays             INT         NULL,       -- from PRF LOCAL/NATIONAL FLAG
    ReviewNotificationDays          INT         NULL,
    LastReviewDateTime              DATETIME2   NULL,
    NextReviewDateTime              DATETIME2   NULL,

    -- Audit
    CreatedDateTimeUTC              DATETIME2   NOT NULL 
        CONSTRAINT DF_PRFAssign_Created DEFAULT SYSUTCDATETIME(),
    UpdatedDateTimeUTC              DATETIME2   NULL
);

-- Helpful index for "show me flags for this patient"
CREATE INDEX IX_PRFAssign_PatientSID 
    ON SPatient.PatientRecordFlagAssignment (PatientSID, IsActive, FlagCategory);
```

Notes / rationale:

* `FlagCategory` I vs II and `FlagSourceType` N vs L reflect how VistA distinguishes **category I (National)** vs **category II (Local)** flags. ([Indian Health Service][7])
* `ReviewFrequencyDays` and `ReviewNotificationDays` mirror fields in 26.11/26.15 that control review cadence. ([vivian.worldvista.org][5])
* The various `Sta3n` fields are exactly what JLV and CDW normally use to track facility ownership.

If you want to be even closer to CDW, you could split out a small dimension like `SPatient.PatientRecordFlagDim` and use a `FlagSID` here instead of storing `FlagName`/IENs directly, but for med-z1 this is probably overkill.

---

### 3.3. `SPatient.PatientRecordFlagHistory` (mock)

```sql
CREATE TABLE SPatient.PatientRecordFlagHistory (
    PatientRecordFlagHistorySID     BIGINT IDENTITY(1,1) PRIMARY KEY,

    PatientRecordFlagAssignmentSID  BIGINT      NOT NULL,  -- FK to Assignment
    PatientSID                      BIGINT      NOT NULL,  -- denormalized for easier joins

    -- Direct mapping from 26.14
    HistoryDateTime                 DATETIME2   NOT NULL,  -- .02 DATE/TIME (#26.14)
    ActionCode                      TINYINT     NOT NULL,  -- .03 ACTION (1..5)
    ActionName                      VARCHAR(50) NOT NULL,  -- 'NEW ASSIGNMENT','CONTINUE', etc.

    EnteredByDUZ                    INT         NOT NULL,  -- .04 ENTERED BY (#200 IEN)
    ApprovedByDUZ                   INT         NOT NULL,  -- .05 APPROVED BY (#200 IEN)
    TiuDocumentIEN                  INT         NULL,      -- .06 TIU PN LINK (#8925 IEN)

    HistoryComments                 NVARCHAR(MAX) NULL,    -- 1;0 HISTORY COMMENTS

    -- Facility context for this event (optional but helpful)
    EventSiteSta3n                  VARCHAR(10) NULL,

    CreatedDateTimeUTC              DATETIME2   NOT NULL 
        CONSTRAINT DF_PRFHist_Created DEFAULT SYSUTCDATETIME()
);

CREATE INDEX IX_PRFHist_AssignDate 
    ON SPatient.PatientRecordFlagHistory (PatientRecordFlagAssignmentSID, HistoryDateTime);

CREATE INDEX IX_PRFHist_PatientDate 
    ON SPatient.PatientRecordFlagHistory (PatientSID, HistoryDateTime);
```

`ActionCode` maps directly to the 26.14 ACTION field: ([vivianr.worldvista.org][2])

| ActionCode | ActionName       | Semantics                                     |
| ---------- | ---------------- | --------------------------------------------- |
| 1          | NEW ASSIGNMENT   | Flag created for patient                      |
| 2          | CONTINUE         | Reviewed and left in effect                   |
| 3          | INACTIVATE       | Flag ended (often with safety-plan narrative) |
| 4          | REACTIVATE       | Flag turned back on                           |
| 5          | ENTERED IN ERROR | Data quality fix                              |

The **HL7 OBX segments** you saw in the spec map neatly into this history table:

* **Status** OBX segments → `ActionCode` / `ActionName`
* **Narrative / Comments** OBX segments → `HistoryComments`
* **DBRS** (if you care) could be added as separate columns (`DbrsCode`, `DbrsOther`) based on the “DBRS-Update/Delete” mapping in the HL7 spec.

---

## 4. Example data you can drop into your mock CDWWork

Here’s a small, concrete example to make this feel real.

### 4.1. Sample assignments

```sql
-- Example patients
-- 100001 = ICN 5000000001V123456 in your mock SPatient.SPatient
-- 100002 = ICN 5000000002V123456

INSERT INTO SPatient.PatientRecordFlagAssignment (
    PatientSID,
    FlagName,
    FlagCategory,
    FlagSourceType,
    NationalFlagIEN,
    LocalFlagIEN,
    IsActive,
    AssignmentStatus,
    AssignmentDateTime,
    InactivationDateTime,
    OwnerSiteSta3n,
    OriginatingSiteSta3n,
    LastUpdateSiteSta3n,
    ReviewFrequencyDays,
    ReviewNotificationDays,
    LastReviewDateTime,
    NextReviewDateTime
)
VALUES
-- Cat I National: HIGH RISK FOR SUICIDE
(100001, 'HIGH RISK FOR SUICIDE', 'I', 'N',
  1, NULL,       -- NationalFlagIEN=1 in PRF NATIONAL FLAG (#26.15)
  1, 'ACTIVE',   -- IsActive, AssignmentStatus
  '2024-11-15T09:30:00', NULL,
  '518', '518', '518', 90, 7,
  '2025-01-15T10:00:00', '2025-04-15T10:00:00'),

-- Cat II Local: BEHAVIORAL
(100002, 'BEHAVIORAL', 'II', 'L',
  NULL, 5,        -- LocalFlagIEN=5 in PRF LOCAL FLAG (#26.11)
  0, 'INACTIVE',  -- IsActive, AssignmentStatus
  '2023-08-01T14:00:00', '2024-03-10T11:45:00',
  '663', '663', '663', 365, 30,
  '2024-02-01T09:00:00', NULL);
```

### 4.2. Sample history rows

```sql
-- Suppose the identity values assigned above are:
--  PatientRecordFlagAssignmentSID 1 → HIGH RISK FOR SUICIDE
--  PatientRecordFlagAssignmentSID 2 → BEHAVIORAL

INSERT INTO SPatient.PatientRecordFlagHistory (
    PatientRecordFlagAssignmentSID,
    PatientSID,
    HistoryDateTime,
    ActionCode,
    ActionName,
    EnteredByDUZ,
    ApprovedByDUZ,
    TiuDocumentIEN,
    HistoryComments,
    EventSiteSta3n
)
VALUES
-- NEW assignment of High Risk for Suicide
(1, 100001,
 '2024-11-15T09:30:00',
 1, 'NEW ASSIGNMENT',
 12345, 67890, 900001,
 N'Flag created after ED visit for suicidal ideation. Safety plan established and documented in linked TIU note.',
 '518'),

-- 90-day review – continued
(1, 100001,
 '2025-01-15T10:00:00',
 2, 'CONTINUE',
 23456, 67890, 900250,
 N'Reviewed in Suicide Prevention team meeting. Veteran remains at elevated risk; continue flag.',
 '518'),

-- NEW assignment of Behavioral local flag
(2, 100002,
 '2023-08-01T14:00:00',
 1, 'NEW ASSIGNMENT',
 34567, 78901, 901000,
 N'History of aggressive behavior towards staff. Implemented two-person escort and de-escalation protocol.',
 '663'),

-- Later inactivated
(2, 100002,
 '2024-03-10T11:45:00',
 3, 'INACTIVATE',
 34567, 78901, 901450,
 N'Behavioral issues stable for >1 year with no incidents. Flag inactivated per policy.',
 '663');
```

---

## 5. How you’d query this for JLV / med-z1

**All active flags for a patient:**

```sql
SELECT
    a.PatientRecordFlagAssignmentSID,
    a.FlagName,
    a.FlagCategory,
    a.FlagSourceType,
    a.AssignmentStatus,
    a.AssignmentDateTime,
    a.OwnerSiteSta3n,
    a.ReviewFrequencyDays,
    a.NextReviewDateTime,
    h.HistoryDateTime      AS LastActionDateTime,
    h.ActionName           AS LastAction,
    h.HistoryComments      AS LastNarrative
FROM SPatient.PatientRecordFlagAssignment a
OUTER APPLY (
    SELECT TOP (1) *
    FROM SPatient.PatientRecordFlagHistory h
    WHERE h.PatientRecordFlagAssignmentSID = a.PatientRecordFlagAssignmentSID
    ORDER BY h.HistoryDateTime DESC
) h
WHERE a.PatientSID = @PatientSID
  AND a.IsActive = 1
ORDER BY 
    CASE WHEN a.FlagCategory = 'I' THEN 1 ELSE 2 END,
    a.AssignmentDateTime DESC;
```

This gives you a very JLV-like view:

* Category I (national) flags at the top
* One row per active flag with:

  * Latest action and narrative text
  * Ownership site and review dates

You can then build your med-z1 “Patient Flags” UI off of this (or wrap it behind a FastAPI endpoint if the flags live in your mock `cdwwork` SQL Server instance).

---

## 6. How close is this to “real” CDW?

Real talk:

* The **table names, domain, and VistA source mapping** for flags in CDW (`SPatient.PatientRecordFlagAssignment` and `SPatient.PatientRecordFlagHistory`) are explicitly visible in the public CDW Domains workbook. ([Vendor Portal][1])
* The **field-level layout** of those CDW views is not published publicly, so I can’t guarantee exact column names or types.
* The design above is intentionally:

  * Aligned with VistA fields (#26.11, 26.13, 26.14, 26.15) ([vivianr.worldvista.org][2])
  * Consistent with HL7 payloads defined in the PRF HL7 spec. ([Veterans Affairs][3])
  * Consistent with typical CDW convention (SPatient domain, `SID` surrogate keys, `Sta3n` codes).

When you eventually get to a VA environment where you can see CDWWork or production CDW, you should be able to:

```sql
SELECT TOP 50 *
FROM SPatient.PatientRecordFlagAssignment;

SELECT TOP 50 *
FROM SPatient.PatientRecordFlagHistory;
```

and then tweak your mock schema / mappings if necessary. But for your current med-z1 **JLV modernization** work, this mock will give you:

* The right **relationships**
* The right **semantics**
* Enough realism to plug into your patient-dashboard and test flag-aware workflows.

If you’d like, next step I can:

* Add a small **FlagDim**/table (National + Local) that mirrors 26.11/26.15, and
* Sketch the REST/GraphQL endpoints you’d expose from your med-z1 backend to serve flags to the React/HTMX UI.

[1]: https://www.vendorportal.ecms.va.gov/FBODocumentServer/DocumentServer.aspx?DocumentId=5404959&FileName=36C10E20Q0070-0003001.xlsx&utm_source=chatgpt.com "CDW Domains - VA Vendor Portal"
[2]: https://vivianr.worldvista.org/dox/Global_XkRHUEYoMjYuMTQ%3D.html?utm_source=chatgpt.com "Global: ^DGPF(26.14"
[3]: https://www.va.gov/vdl/documents/clinical/patient_record_flags/prfhl7is.doc?utm_source=chatgpt.com "Patient Record Flags (PRF)"
[4]: https://www.vistapedia.com/index.php/VistA_Database_Globals?utm_source=chatgpt.com "VistA Database Globals"
[5]: https://vivian.worldvista.org/dox/Global_XkRHUEYoMjYuMTE%3D.html?utm_source=chatgpt.com "Global: ^DGPF(26.11 - ViViaN - WorldVistA"
[6]: https://www.va.gov/VDL/documents/Clinical/Patient_Record_Flags/prfrn.pdf?utm_source=chatgpt.com "Patient Record Flags Release Notes Patch DG*5.3*425 ..."
[7]: https://www.ihs.gov/RPMS/PackageDocs/PIMS/dg_53_650_ug.pdf?utm_source=chatgpt.com "Patient Record Flags Phase III"
