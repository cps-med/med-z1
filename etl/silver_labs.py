# ---------------------------------------------------------------------
# silver_labs.py
# ---------------------------------------------------------------------
# Transform Bronze Laboratory Results to Silver layer with:
#  - Patient identity resolution (PatientSID → PatientICN)
#  - Date standardization (ISO 8601)
#  - Numeric result parsing and validation
#  - Reference range parsing
#  - Abnormal flag standardization
#  - Unit standardization
#  - Panel name enrichment
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_labs
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
import re
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_numeric_result(result_str: str, result_numeric: float | None) -> float | None:
    """
    Parse numeric result from text, handling special cases.

    Handles:
    - Direct numeric values
    - "<5.0" → 4.99
    - ">1000" → 1001.0
    - "Positive", "Negative", etc. → None
    """
    if result_numeric is not None:
        return result_numeric

    if result_str is None or result_str.strip() == "":
        return None

    result_str = result_str.strip()

    # Handle less-than values: "<5.0" → 4.99
    if result_str.startswith("<"):
        try:
            value = float(result_str[1:])
            return value - 0.01
        except ValueError:
            return None

    # Handle greater-than values: ">1000" → 1001.0
    if result_str.startswith(">"):
        try:
            value = float(result_str[1:])
            return value + 1.0
        except ValueError:
            return None

    # Try direct conversion
    try:
        return float(result_str)
    except ValueError:
        return None


def parse_reference_range(ref_range: str | None) -> tuple[float | None, float | None]:
    """
    Parse reference range string into low and high values.

    Examples:
    - "135 - 145" → (135.0, 145.0)
    - "3.5 - 5.0 mmol/L" → (3.5, 5.0)
    - "Negative" → (None, None)
    """
    if ref_range is None or ref_range.strip() == "":
        return (None, None)

    ref_range = ref_range.strip()

    # Pattern: "number - number" (with optional units after)
    pattern = r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)"
    match = re.search(pattern, ref_range)

    if match:
        try:
            low = float(match.group(1))
            high = float(match.group(2))
            return (low, high)
        except ValueError:
            return (None, None)

    return (None, None)


def standardize_abnormal_flag(flag: str | None) -> str | None:
    """
    Standardize abnormal flag values.

    Valid values: 'H', 'L', 'H*', 'L*', 'Panic', None
    """
    if flag is None or flag.strip() == "":
        return None

    flag = flag.strip().upper()

    valid_flags = {'H', 'L', 'H*', 'L*', 'PANIC'}

    if flag in valid_flags:
        return flag

    # Map common variations
    if flag in ['HIGH', 'HH', 'CRITICAL HIGH']:
        return 'H*'
    if flag in ['LOW', 'LL', 'CRITICAL LOW']:
        return 'L*'
    if flag in ['ABNORMAL']:
        return 'H'  # Default to High for generic abnormal

    return None


def transform_lab_test_dim():
    """Transform Bronze Dim.LabTest to Silver layer."""
    logger.info("Starting Silver transformation: Lab Test Definitions")

    minio_client = MinIOClient()

    # Read Bronze layer
    bronze_key = build_bronze_path(
        source_system="cdwwork",
        domain="lab_test_dim",
        filename="lab_test_dim_raw.parquet"
    )

    df = minio_client.read_parquet(bronze_key)
    logger.info(f"Read {len(df)} test definitions from Bronze layer")

    # Transformations
    df = df.with_columns([
        # Standardize date
        pl.col("CreatedDate").dt.strftime("%Y-%m-%d %H:%M:%S").alias("CreatedDate"),

        # Ensure boolean columns are properly typed
        pl.col("IsPanel").cast(pl.Boolean).alias("IsPanel"),
        pl.col("IsActive").cast(pl.Boolean).alias("IsActive"),

        # Parse reference ranges
        pl.struct([
            pl.col("RefRangeLow").cast(pl.Utf8),
            pl.col("RefRangeHigh").cast(pl.Utf8)
        ]).map_elements(
            lambda x: float(x["RefRangeLow"]) if x["RefRangeLow"] else None,
            return_dtype=pl.Float64
        ).alias("RefRangeLowNumeric"),

        pl.struct([
            pl.col("RefRangeLow").cast(pl.Utf8),
            pl.col("RefRangeHigh").cast(pl.Utf8)
        ]).map_elements(
            lambda x: float(x["RefRangeHigh"]) if x["RefRangeHigh"] else None,
            return_dtype=pl.Float64
        ).alias("RefRangeHighNumeric"),
    ])

    # Select and reorder columns
    df = df.select([
        "LabTestSID",
        "LabTestName",
        "LabTestCode",
        "LoincCode",
        "IsPanel",
        "PanelName",
        "Units",
        "RefRangeLow",
        "RefRangeHigh",
        "RefRangeLowNumeric",
        "RefRangeHighNumeric",
        "RefRangeText",
        "VistaPackage",
        "CreatedDate",
        "IsActive",
        "SourceSystem",
        "LoadDateTime",
    ])

    # Write to Silver layer
    silver_key = build_silver_path(
        domain="lab_test_dim",
        filename="lab_test_dim.parquet"
    )

    minio_client.write_parquet(df, silver_key)

    logger.info(f"Silver layer written to MinIO: {silver_key}")
    return len(df)


def transform_lab_chem():
    """Transform Bronze Chem.LabChem to Silver layer."""
    logger.info("Starting Silver transformation: Lab Results")

    minio_client = MinIOClient()

    # Read Bronze layer
    bronze_key = build_bronze_path(
        source_system="cdwwork",
        domain="lab_chem",
        filename="lab_chem_raw.parquet"
    )

    df = minio_client.read_parquet(bronze_key)
    logger.info(f"Read {len(df)} lab results from Bronze layer")

    # Transformations

    # 1. Date standardization
    df = df.with_columns([
        pl.col("CollectionDateTime").dt.strftime("%Y-%m-%d %H:%M:%S").alias("CollectionDateTime"),
        pl.col("ResultDateTime").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ResultDateTime"),
    ])

    # 2. Numeric result parsing
    df = df.with_columns([
        pl.struct([
            pl.col("Result").cast(pl.Utf8),
            pl.col("ResultNumeric")
        ]).map_elements(
            lambda x: parse_numeric_result(x["Result"], x["ResultNumeric"]),
            return_dtype=pl.Float64
        ).alias("ResultNumericParsed"),
    ])

    # 3. Reference range parsing
    df = df.with_columns([
        pl.col("RefRange").map_elements(
            lambda x: parse_reference_range(x)[0],
            return_dtype=pl.Float64
        ).alias("RefRangeLowNumeric"),

        pl.col("RefRange").map_elements(
            lambda x: parse_reference_range(x)[1],
            return_dtype=pl.Float64
        ).alias("RefRangeHighNumeric"),
    ])

    # 4. Abnormal flag standardization
    df = df.with_columns([
        pl.col("AbnormalFlag").map_elements(
            standardize_abnormal_flag,
            return_dtype=pl.Utf8
        ).alias("AbnormalFlagStd"),
    ])

    # 5. Add calculated fields
    df = df.with_columns([
        # IsAbnormal boolean flag
        (pl.col("AbnormalFlagStd").is_not_null()).alias("IsAbnormal"),

        # IsCritical flag (H* or L*)
        (pl.col("AbnormalFlagStd").is_in(["H*", "L*", "PANIC"])).alias("IsCritical"),

        # Days since collection (use non-timezone-aware datetime for compatibility)
        (
            (pl.lit(datetime.now()) - pl.col("CollectionDateTime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S"))
            .dt.total_days()
        ).alias("DaysSinceCollection"),
    ])

    # 6. Patient identity resolution (PatientICN is already in the Bronze data from JOIN)
    # Verify PatientICN exists
    if "PatientICN" not in df.columns:
        logger.warning("PatientICN not found in Bronze data - identity resolution may be incomplete")
        df = df.with_columns([
            pl.lit(None).cast(pl.Utf8).alias("PatientICN")
        ])

    # Select and reorder columns
    df = df.select([
        "LabChemSID",
        "PatientSID",
        "PatientICN",
        "PatientName",
        "LabTestSID",
        "LabTestName",
        "LabTestCode",
        "LoincCode",
        "PanelName",
        "LabOrderSID",
        "AccessionNumber",
        "Result",
        "ResultNumeric",
        "ResultNumericParsed",
        "ResultUnit",
        "AbnormalFlag",
        "AbnormalFlagStd",
        "IsAbnormal",
        "IsCritical",
        "RefRange",
        "RefRangeLowNumeric",
        "RefRangeHighNumeric",
        "DefaultUnits",
        "DefaultRefRangeLow",
        "DefaultRefRangeHigh",
        "DefaultRefRangeText",
        "CollectionDateTime",
        "ResultDateTime",
        "DaysSinceCollection",
        "VistaPackage",
        "LocationSID",
        "CollectionLocation",
        "CollectionLocationType",
        "Sta3n",
        "PerformingLabSID",
        "OrderingProviderSID",
        "SpecimenType",
        "SourceSystem",
        "LoadDateTime",
    ])

    # Write to Silver layer
    silver_key = build_silver_path(
        domain="lab_chem",
        filename="lab_chem.parquet"
    )

    minio_client.write_parquet(df, silver_key)

    logger.info(f"Silver layer written to MinIO: {silver_key}")
    return len(df)


def main():
    """Execute Silver ETL for Laboratory Results."""
    logger.info("=" * 70)
    logger.info("SILVER ETL: Laboratory Results (Chemistry)")
    logger.info("=" * 70)

    try:
        # Transform Dim.LabTest
        test_count = transform_lab_test_dim()
        logger.info(f"✅ Lab Test Definitions transformed: {test_count}")

        # Transform Chem.LabChem
        result_count = transform_lab_chem()
        logger.info(f"✅ Lab Results transformed: {result_count}")

        logger.info("=" * 70)
        logger.info("SILVER ETL COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Silver ETL failed: {e}")
        raise


if __name__ == "__main__":
    main()
