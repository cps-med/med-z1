# mock

Mock Data Service for VA Healthcare Analytics and JLV Viewer Development

## Overview

**mock** is a subsystem of the med-z1 application that provides a mock data service that simulates patient, medical treatment, and other supporting data in formats compatible with:

- **VA Corporate Data Warehouse (CDW)** - Microsoft SQL Server 2019 data source
- **VA Summit Data Platform (SDP)** - Azure Data Lake Storage Gen2 (ADLS Gen2) with Parquet files (optional/future)
- **Drug-Drug Interaction Dataset** - For DDI risk analysis, will use a dataset such as the kaggle DDI CSV file.

The data available within mock is **synthetic** and does not contain PHI or PII. It supports local development, testing, and demonstration of the med-z1 application.