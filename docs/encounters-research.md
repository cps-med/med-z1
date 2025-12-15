Prompt:
I would like to continue building the healthcare data viewer (modern and improved JLV application) mentioned in earlier chats to implement an "Encounters" clinical domain. I'm not sure if the scope of encounters within VA is both inpatient and outpatient, so I will need guidance to clarify this. 

Can you reserach information on how encounters data is stored within the VA CDW data warehouse, and in particular within the CDWWork database. This database has created a set of database views for the various data that orginated in VistA files. I would like to replecate the "schema.table" structure (and specific column definitions) from CDW so that I can create a version of this on my local development machine using a SQL Server database.

Please research all potentially useful sources of information to provide guidance and specific technical information. If you can find information on how encounters are used in the legacy JLV application, i.e., with encounter-related widget(s), that would be helpful.

As a point of reference, I have attached the JLV legacy application user guide, which may have information about how encounters and encounter-related widgets are implemented in the legacy application. I do not need to exactly replicate the widget implementation in the new system, but I am interested in having a clear idea of what VistA and CDW data, files, and tables support this clinical domain.

Response:
Based on your request and the JLV documentation, "Encounters" in the VA ecosystem is split into two distinct clinical domains: **Outpatient Encounters** and **Inpatient Admissions**.

The legacy JLV application handles these with two separate widgets:

  * **Encounters - Outpatient:** Displays clinic visits, appointments, and procedures.
  * **Admissions:** Displays hospital stays, discharge summaries, and ward movements.

To replicate the data backend for your **med-z1** application, you should create a local SQL Server database (e.g., named `CDWWork`) and implement the following schemas and tables. This structure mirrors the actual VA CDW architecture.

### 1\. Recommended Database Schema Architecture

You will need to create three schemas in your local database:

  * **`[Outpat]`**: For outpatient encounter data (VistA File \#9000010).
  * **`[Inpat]`**: For inpatient admission data (VistA Patient Treatment File \#45 / Patient Movement \#405).
  * **`[Dim]`**: For "Dimension" tables (lookups for Patients, Providers, Locations).

### 2\. SQL Server Table Definitions

Run these scripts on your local SQL Server to create the structures necessary to power both the *Encounters* and *Admissions* widgets.

#### A. Dimension Tables (Lookups)

These tables store the static data referenced by the clinical tables (Foreign Keys).

```sql
CREATE SCHEMA [Dim] AUTHORIZATION [dbo];
GO

-- Stores Clinic and Ward locations
CREATE TABLE [Dim].[Location] (
    [LocationSID] INT IDENTITY(1,1) PRIMARY KEY,
    [LocationName] VARCHAR(100),
    [StationNumber] VARCHAR(10) -- e.g., '500' for a generic site
);

-- Stores Healthcare Providers
CREATE TABLE [Dim].[Provider] (
    [ProviderSID] INT IDENTITY(1,1) PRIMARY KEY,
    [ProviderName] VARCHAR(100),
    [ProviderSSN] VARCHAR(9), -- often masked in lower environments
    [ProviderTitle] VARCHAR(50)
);

-- Stores ICD-10 Diagnosis Codes
CREATE TABLE [Dim].[ICD10] (
    [ICD10SID] INT IDENTITY(1,1) PRIMARY KEY,
    [ICD10Code] VARCHAR(20),
    [ICD10Description] VARCHAR(255)
);
```

#### B. Outpatient Domain (The "Encounters" Widget)

This replicates the **`[Outpat].[Visit]`** table in CDW. This is the primary source for the "Encounters - Outpatient" widget.

```sql
CREATE SCHEMA [Outpat] AUTHORIZATION [dbo];
GO

-- Main table for Outpatient Encounters
CREATE TABLE [Outpat].[Visit] (
    [VisitSID] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [VisitDateTime] DATETIME2(0), -- JLV Column: "Encounter Date"
    [PatientSID] INT, -- Links to your Patient table
    [LocationSID] INT, -- Links to Dim.Location. JLV Column: "Location" or "Clinic"
    [PrimaryProviderSID] INT, -- Links to Dim.Provider. JLV Column: "Provider"
    [ServiceCategory] VARCHAR(50), -- e.g., 'Ambulatory', 'Telehealth'
    [VisitID] VARCHAR(50), -- The Source ID from VistA
    [Sta3n] INT, -- The VA Station Number (e.g., 688)
    FOREIGN KEY ([LocationSID]) REFERENCES [Dim].[Location]([LocationSID]),
    FOREIGN KEY ([PrimaryProviderSID]) REFERENCES [Dim].[Provider]([ProviderSID])
);

-- Diagnosis table (One visit can have multiple diagnoses)
-- JLV Column: "Diagnosis"
CREATE TABLE [Outpat].[VDiagnosis] (
    [VDiagnosisSID] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [VisitSID] BIGINT, -- Links back to the Visit
    [ICD10SID] INT, -- Links to Dim.ICD10
    [PrimarySecondary] VARCHAR(1), -- 'P' for Primary, 'S' for Secondary
    FOREIGN KEY ([VisitSID]) REFERENCES [Outpat].[Visit]([VisitSID]),
    FOREIGN KEY ([ICD10SID]) REFERENCES [Dim].[ICD10]([ICD10SID])
);
```

#### C. Inpatient Domain (The "Admissions" Widget)

This replicates the **`[Inpat].[Inpatient]`** table in CDW. This is the primary source for the "Admissions" widget.

```sql
CREATE SCHEMA [Inpat] AUTHORIZATION [dbo];
GO

-- Main table for Inpatient Stays (Admissions)
CREATE TABLE [Inpat].[Inpatient] (
    [InpatientSID] BIGINT IDENTITY(1,1) PRIMARY KEY,
    [PatientSID] INT,
    [AdmitDateTime] DATETIME2(0), -- JLV Column: "Adm Date"
    [DischargeDateTime] DATETIME2(0), -- JLV Column: "Discharge Date"
    [AdmitLocationSID] INT, -- Links to Dim.Location (Ward)
    [DischargeLocationSID] INT,
    [AdmittingProviderSID] INT, -- JLV Column: "Provider"
    [DischargeDiagnosisSID] INT, -- Primary Diagnosis at discharge
    [Sta3n] INT,
    FOREIGN KEY ([AdmitLocationSID]) REFERENCES [Dim].[Location]([LocationSID]),
    FOREIGN KEY ([AdmittingProviderSID]) REFERENCES [Dim].[Provider]([ProviderSID])
);
```

### 3\. Mapping Legacy JLV Columns to CDW Data

When you build your API endpoints (using FastAPI), you will query the tables above to populate the specific columns seen in the JLV Legacy user guide.

**Widget: Encounters - Outpatient**

| JLV Widget Column | CDW Source Table & Column | Notes |
| :--- | :--- | :--- |
| **Encounter Date** | `[Outpat].[Visit].[VisitDateTime]` | Date of the visit. |
| **Clinic** | `[Dim].[Location].[LocationName]` | Joined via `LocationSID`. |
| **Provider** | `[Dim].[Provider].[ProviderName]` | Joined via `PrimaryProviderSID`. |
| **Diagnosis** | `[Dim].[ICD10].[ICD10Description]` | Joined via `[Outpat].[VDiagnosis]`. |
| **Location** | `[Dim].[Location].[LocationName]` | Often synonymous with Clinic in VistA. |

**Widget: Admissions**

| JLV Widget Column | CDW Source Table & Column | Notes |
| :--- | :--- | :--- |
| **Adm Date** | `[Inpat].[Inpatient].[AdmitDateTime]` | Start of the stay. |
| **Discharge Date** | `[Inpat].[Inpatient].[DischargeDateTime]` | End of the stay (NULL if active). |
| **Ward** | `[Dim].[Location].[LocationName]` | The specific ward (e.g., "7 East"). |
| **Provider** | `[Dim].[Provider].[ProviderName]` | Admitting or Attending provider. |
| **Diagnosis** | `[Dim].[ICD10].[ICD10Description]` | Primary discharge diagnosis. |
