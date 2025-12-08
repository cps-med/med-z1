# ---------------------------------------------------------------------
# bronze_patient.py
# ---------------------------------------------------------------------
# Create MinIO Parquet version of Patient from CDWWork database.
#  - pull from SPatient.SPatient
#  - save to med-z1/bronze/cdwwork/patient
#  - as patient_raw.parquet
# ---------------------------------------------------------------------
# To run this script from the project root folder, treat it as a
# module (for now... there are other options to consider later).
#  $ cd med-z1
#  $ python -m etl.bronze_patient
# ---------------------------------------------------------------------

# Import dependencies
import polars as pl
import logging
from config import CDWWORK_DB_CONFIG
from lake.minio_client import MinIOClient, build_bronze_path

logger = logging.getLogger(__name__)

def extract_patient_bronze():
    """Extract patient data from CDWWork to Bronze layer in MinIO."""
    logger.info("Starting Bronze patient extraction")

    # Initialize MinIO client
    minio_client = MinIOClient()
    logger.info("minio_client created")
    
    # Connection string for source database
    conn_str = (
        f"mssql://{CDWWORK_DB_CONFIG['user']}:"
        f"{CDWWORK_DB_CONFIG['password']}@"
        f"{CDWWORK_DB_CONFIG['server']}/"
        f"{CDWWORK_DB_CONFIG['name']}"
    )
    logger.info(f"Created DB connection string: {conn_str}")

    # Extract query
    query = """
    SELECT
        PatientSID,
        PatientIEN,
        Sta3n,
        PatientName,
        PatientLastName,
        PatientFirstName,
        PatientICN,
        PatientSSN,
        BirthDateTime,
        Gender,
        SourceSystemCode
    FROM Spatient.Spatient
    WHERE TestPatient = 'N' OR TestPatient = 'Y'
    """


    logger.info("Bronze extraction complete")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    extract_patient_bronze()
