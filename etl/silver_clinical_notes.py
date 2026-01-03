# ---------------------------------------------------------------------
# silver_clinical_notes.py
# ---------------------------------------------------------------------
# Transform Bronze Clinical Notes to Silver layer with:
#  - Patient identity resolution (PatientSID → PatientICN)
#  - Date standardization (ISO 8601)
#  - Note class standardization
#  - Text preview generation (first 200 characters)
#  - Note length validation
#  - Status standardization
#  - Author/Cosigner name cleaning
# ---------------------------------------------------------------------
# To run this script from the project root folder:
#  $ cd med-z1
#  $ python -m etl.silver_clinical_notes
# ---------------------------------------------------------------------

import polars as pl
from datetime import datetime, timezone
import logging
from lake.minio_client import MinIOClient, build_bronze_path, build_silver_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def standardize_document_class(doc_class: str | None) -> str | None:
    """
    Standardize document class values.

    Valid values: 'Progress Notes', 'Consults', 'Discharge Summaries', 'Imaging', 'Other'
    """
    if doc_class is None or doc_class.strip() == "":
        return "Other"

    doc_class = doc_class.strip()

    # Map to standard classes
    valid_classes = {
        'Progress Notes',
        'Consults',
        'Discharge Summaries',
        'Imaging',
        'Other'
    }

    if doc_class in valid_classes:
        return doc_class

    # Handle variations
    if 'progress' in doc_class.lower():
        return 'Progress Notes'
    elif 'consult' in doc_class.lower():
        return 'Consults'
    elif 'discharge' in doc_class.lower():
        return 'Discharge Summaries'
    elif 'imaging' in doc_class.lower() or 'radiology' in doc_class.lower():
        return 'Imaging'

    return 'Other'


def create_text_preview(text: str | None, length: int = 200) -> str | None:
    """
    Create text preview by taking first N characters and adding ellipsis if truncated.

    Args:
        text: Full note text
        length: Preview length (default 200 characters)

    Returns:
        Preview text with ellipsis if truncated, or full text if shorter
    """
    if text is None or text.strip() == "":
        return None

    text = text.strip()

    if len(text) <= length:
        return text

    # Find last space within length to avoid cutting mid-word
    preview = text[:length]
    last_space = preview.rfind(' ')

    if last_space > length * 0.8:  # If space is in last 20%, use it
        preview = preview[:last_space]

    return preview + "..."


def transform_tiu_document_definition_dim():
    """Transform Bronze Dim.TIUDocumentDefinition to Silver layer."""
    logger.info("Starting Silver transformation: TIU Document Type Definitions")

    minio_client = MinIOClient()

    # Read Bronze layer
    bronze_key = build_bronze_path(
        source_system="cdwwork",
        domain="tiu_document_definition_dim",
        filename="tiu_document_definition_dim_raw.parquet"
    )

    df = minio_client.read_parquet(bronze_key)
    logger.info(f"Read {len(df)} document type definitions from Bronze layer")

    # Transformations
    df = df.with_columns([
        # Standardize document class
        pl.col("DocumentClass").map_elements(
            standardize_document_class,
            return_dtype=pl.Utf8
        ).alias("DocumentClass"),

        # Ensure boolean columns are properly typed
        pl.col("IsActive").cast(pl.Boolean).alias("IsActive"),
    ])

    # Select and reorder columns
    df = df.select([
        "DocumentDefinitionSID",
        "TIUDocumentTitle",
        "DocumentClass",
        "VHAEnterpriseStandardTitle",
        "IsActive",
        "Sta3n",
        "TIUDocumentDefinitionIEN",
        "SourceSystem",
        "LoadDateTime",
    ])

    # Write to Silver layer
    silver_key = build_silver_path(
        domain="tiu_document_definition_dim",
        filename="tiu_document_definition_dim.parquet"
    )

    minio_client.write_parquet(df, silver_key)

    logger.info(f"Silver layer written to MinIO: {silver_key}")
    return len(df)


def transform_tiu_clinical_notes():
    """Transform Bronze TIU Clinical Notes to Silver layer."""
    logger.info("Starting Silver transformation: Clinical Notes")

    minio_client = MinIOClient()

    # Read Bronze layer
    bronze_key = build_bronze_path(
        source_system="cdwwork",
        domain="tiu_clinical_notes",
        filename="tiu_clinical_notes_raw.parquet"
    )

    df = minio_client.read_parquet(bronze_key)
    logger.info(f"Read {len(df)} clinical notes from Bronze layer")

    # Transformations

    # 1. Date standardization (ISO 8601 format)
    df = df.with_columns([
        pl.col("ReferenceDateTime").dt.strftime("%Y-%m-%d %H:%M:%S").alias("ReferenceDateTime"),
        pl.col("EntryDateTime").dt.strftime("%Y-%m-%d %H:%M:%S").alias("EntryDateTime"),
        pl.when(pl.col("CreatedDateTimeUTC").is_not_null())
          .then(pl.col("CreatedDateTimeUTC").dt.strftime("%Y-%m-%d %H:%M:%S"))
          .otherwise(None)
          .alias("CreatedDateTimeUTC"),
        pl.when(pl.col("UpdatedDateTimeUTC").is_not_null())
          .then(pl.col("UpdatedDateTimeUTC").dt.strftime("%Y-%m-%d %H:%M:%S"))
          .otherwise(None)
          .alias("UpdatedDateTimeUTC"),
    ])

    # 2. Standardize document class
    df = df.with_columns([
        pl.col("DocumentClass").map_elements(
            standardize_document_class,
            return_dtype=pl.Utf8
        ).alias("DocumentClass"),
    ])

    # 3. Create text preview (200 characters)
    df = df.with_columns([
        pl.col("DocumentText").map_elements(
            lambda x: create_text_preview(x, length=200),
            return_dtype=pl.Utf8
        ).alias("TextPreview"),
    ])

    # 4. Validate text length (calculate if missing)
    df = df.with_columns([
        pl.when(pl.col("TextLength").is_null())
          .then(
              pl.when(pl.col("DocumentText").is_not_null())
                .then(pl.col("DocumentText").str.len_chars())
                .otherwise(0)
          )
          .otherwise(pl.col("TextLength"))
          .alias("TextLength"),
    ])

    # 5. Clean author and cosigner names (remove extra whitespace, handle nulls)
    df = df.with_columns([
        pl.when(pl.col("AuthorName").is_not_null())
          .then(pl.col("AuthorName").str.strip_chars())
          .otherwise(None)
          .alias("AuthorName"),
        pl.when(pl.col("CosignerName").is_not_null())
          .then(pl.col("CosignerName").str.strip_chars())
          .otherwise(None)
          .alias("CosignerName"),
    ])

    # 6. Create composite patient identifier (for future harmonization with Cerner)
    df = df.with_columns([
        pl.col("PatientICN").alias("PatientKey"),  # Silver uses ICN as PatientKey
    ])

    # Select and reorder columns for Silver layer
    df = df.select([
        # Primary keys
        "TIUDocumentSID",
        "PatientSID",
        "PatientICN",
        "PatientKey",
        "PatientName",
        "DocumentDefinitionSID",

        # Document metadata
        "TIUDocumentTitle",
        "DocumentClass",
        "VHAEnterpriseStandardTitle",
        "Status",

        # Dates
        "ReferenceDateTime",
        "EntryDateTime",
        "CreatedDateTimeUTC",
        "UpdatedDateTimeUTC",

        # Author information
        "AuthorSID",
        "AuthorName",
        "CosignerSID",
        "CosignerName",

        # Visit and location
        "VisitSID",
        "Sta3n",

        # Note content
        "DocumentText",
        "TextLength",
        "TextPreview",

        # Source identifiers
        "TIUDocumentIEN",
        "SourceSystem",
        "LoadDateTime",
    ])

    # Write to Silver layer
    silver_key = build_silver_path(
        domain="tiu_clinical_notes",
        filename="tiu_clinical_notes.parquet"
    )

    minio_client.write_parquet(df, silver_key)

    logger.info(f"Silver layer written to MinIO: {silver_key}")
    return len(df)


def main():
    """Execute Silver ETL for Clinical Notes."""
    logger.info("=" * 70)
    logger.info("SILVER ETL: Clinical Notes")
    logger.info("=" * 70)

    try:
        # Transform Dim.TIUDocumentDefinition
        def_count = transform_tiu_document_definition_dim()
        logger.info(f"✅ TIU Document Type Definitions transformed: {def_count}")

        # Transform TIU Clinical Notes
        note_count = transform_tiu_clinical_notes()
        logger.info(f"✅ Clinical Notes transformed: {note_count}")

        logger.info("=" * 70)
        logger.info("SILVER ETL COMPLETE")
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"❌ Silver ETL failed: {e}")
        raise


if __name__ == "__main__":
    main()
