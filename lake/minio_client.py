"""
MinIO Client for med-z1 Data Lake

Provides a reusable boto3-based client for reading and writing Parquet files
to MinIO object storage. Supports the medallion architecture (Bronze, Silver, Gold).

Usage:
    from lake.minio_client import MinIOClient

    # Initialize client
    client = MinIOClient()

    # Write a Parquet file
    import polars as pl
    df = pl.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    client.write_parquet(df, "bronze/cdwwork/patient/patient_raw.parquet")

    # Read a Parquet file
    df = client.read_parquet("bronze/cdwwork/patient/patient_raw.parquet")

    # Get object info
    exists = client.exists("bronze/cdwwork/patient/patient_raw.parquet")
"""

import logging
from pathlib import Path
from typing import Optional, Union
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
import polars as pl

from config import MINIO_CONFIG

logger = logging.getLogger(__name__)


class MinIOClient:
    """
    MinIO client for med-z1 data lake operations.

    This class provides a simple interface for reading and writing Parquet files
    to MinIO object storage using boto3 (S3-compatible API).

    Attributes:
        bucket_name: Name of the MinIO bucket
        s3_client: boto3 S3 client configured for MinIO
    """

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        use_ssl: Optional[bool] = None,
    ):
        """
        Initialize MinIO client.

        Args:
            endpoint: MinIO endpoint (default: from config.MINIO_CONFIG)
            access_key: MinIO access key (default: from config.MINIO_CONFIG)
            secret_key: MinIO secret key (default: from config.MINIO_CONFIG)
            bucket_name: MinIO bucket name (default: from config.MINIO_CONFIG)
            use_ssl: Use SSL/TLS (default: from config.MINIO_CONFIG)
        """
        # Load from config if not provided
        self.endpoint = endpoint or MINIO_CONFIG["endpoint"]
        self.access_key = access_key or MINIO_CONFIG["access_key"]
        self.secret_key = secret_key or MINIO_CONFIG["secret_key"]
        self.bucket_name = bucket_name or MINIO_CONFIG["bucket_name"]
        self.use_ssl = use_ssl if use_ssl is not None else MINIO_CONFIG["use_ssl"]

        # Construct endpoint URL
        protocol = "https" if self.use_ssl else "http"
        endpoint_url = f"{protocol}://{self.endpoint}"

        # Initialize boto3 S3 client
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=boto3.session.Config(signature_version="s3v4"),
        )

        logger.info(f"MinIO client initialized: {endpoint_url}, bucket={self.bucket_name}")

    def write_parquet(
        self,
        df: pl.DataFrame,
        object_key: str,
        compression: str = "snappy",
    ) -> None:
        """
        Write a Polars DataFrame to MinIO as a Parquet file.

        Args:
            df: Polars DataFrame to write
            object_key: S3 object key (path) in the bucket
            compression: Compression algorithm (default: snappy)

        Example:
            client.write_parquet(df, "bronze/cdwwork/patient/patient_raw.parquet")
        """
        try:
            # Write DataFrame to in-memory buffer as Parquet
            buffer = BytesIO()
            df.write_parquet(buffer, compression=compression)
            buffer.seek(0)

            # Upload to MinIO
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=buffer.getvalue(),
                ContentType="application/parquet",
            )

            logger.info(f"Written Parquet file: s3://{self.bucket_name}/{object_key} ({len(df)} rows)")

        except ClientError as e:
            logger.error(f"Failed to write Parquet file to MinIO: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing Parquet file: {e}")
            raise

    def read_parquet(
        self,
        object_key: str,
        columns: Optional[list[str]] = None,
    ) -> pl.DataFrame:
        """
        Read a Parquet file from MinIO into a Polars DataFrame.

        Args:
            object_key: S3 object key (path) in the bucket
            columns: Optional list of columns to read (default: all columns)

        Returns:
            Polars DataFrame

        Example:
            df = client.read_parquet("bronze/cdwwork/patient/patient_raw.parquet")
        """
        try:
            # Download from MinIO
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )

            # Read Parquet from bytes
            parquet_bytes = response["Body"].read()
            buffer = BytesIO(parquet_bytes)

            # Read into Polars DataFrame
            df = pl.read_parquet(buffer, columns=columns)

            logger.info(f"Read Parquet file: s3://{self.bucket_name}/{object_key} ({len(df)} rows)")

            return df

        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"Parquet file not found: s3://{self.bucket_name}/{object_key}")
                raise FileNotFoundError(f"Object not found: {object_key}")
            else:
                logger.error(f"Failed to read Parquet file from MinIO: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error reading Parquet file: {e}")
            raise

    def exists(self, object_key: str) -> bool:
        """
        Check if an object exists in MinIO.

        Args:
            object_key: S3 object key (path) in the bucket

        Returns:
            True if object exists, False otherwise

        Example:
            if client.exists("bronze/cdwwork/patient/patient_raw.parquet"):
                print("File exists")
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                logger.error(f"Error checking object existence: {e}")
                raise

    def delete(self, object_key: str) -> None:
        """
        Delete an object from MinIO.

        Args:
            object_key: S3 object key (path) in the bucket

        Example:
            client.delete("bronze/cdwwork/patient/patient_raw.parquet")
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            logger.info(f"Deleted object: s3://{self.bucket_name}/{object_key}")
        except ClientError as e:
            logger.error(f"Failed to delete object from MinIO: {e}")
            raise

    def list_objects(
        self,
        prefix: str = "",
        max_keys: int = 1000,
    ) -> list[str]:
        """
        List objects in MinIO with a given prefix.

        Args:
            prefix: Object key prefix (directory path)
            max_keys: Maximum number of keys to return

        Returns:
            List of object keys

        Example:
            objects = client.list_objects(prefix="bronze/cdwwork/patient/")
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys,
            )

            if "Contents" not in response:
                return []

            return [obj["Key"] for obj in response["Contents"]]

        except ClientError as e:
            logger.error(f"Failed to list objects from MinIO: {e}")
            raise

    def get_object_size(self, object_key: str) -> int:
        """
        Get the size of an object in bytes.

        Args:
            object_key: S3 object key (path) in the bucket

        Returns:
            Size in bytes

        Example:
            size = client.get_object_size("bronze/cdwwork/patient/patient_raw.parquet")
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key,
            )
            return response["ContentLength"]
        except ClientError as e:
            logger.error(f"Failed to get object size: {e}")
            raise


# -----------------------------------------------------------
# Path Construction Utilities
# -----------------------------------------------------------

def build_bronze_path(
    source_system: str,
    domain: str,
    filename: str,
) -> str:
    """
    Build a standardized Bronze layer object key.

    Args:
        source_system: Source system name (e.g., "cdwwork", "cdwwork1")
        domain: Clinical domain (e.g., "patient", "encounter", "medication")
        filename: Parquet filename (e.g., "patient_raw.parquet")

    Returns:
        Object key string

    Example:
        path = build_bronze_path("cdwwork", "patient", "patient_raw.parquet")
        # Returns: "bronze/cdwwork/patient/patient_raw.parquet"
    """
    return f"bronze/{source_system.lower()}/{domain.lower()}/{filename}"


def build_silver_path(
    domain: str,
    filename: str,
) -> str:
    """
    Build a standardized Silver layer object key.

    Args:
        domain: Clinical domain (e.g., "patient", "encounter", "medication")
        filename: Parquet filename (e.g., "patient_cleaned.parquet")

    Returns:
        Object key string

    Example:
        path = build_silver_path("patient", "patient_cleaned.parquet")
        # Returns: "silver/patient/patient_cleaned.parquet"
    """
    return f"silver/{domain.lower()}/{filename}"


def build_gold_path(
    view_name: str,
    filename: str,
) -> str:
    """
    Build a standardized Gold layer object key.

    Args:
        view_name: Gold view name (e.g., "patient_demographics", "medication_summary")
        filename: Parquet filename (e.g., "patient_demographics.parquet")

    Returns:
        Object key string

    Example:
        path = build_gold_path("patient_demographics", "patient_demographics.parquet")
        # Returns: "gold/patient_demographics/patient_demographics.parquet"
    """
    return f"gold/{view_name.lower()}/{filename}"


def build_ai_path(
    subdomain: str,
    filename: str,
) -> str:
    """
    Build a standardized AI/ML layer object key.

    Args:
        subdomain: AI subdomain (e.g., "embeddings", "models", "vectors")
        filename: File name

    Returns:
        Object key string

    Example:
        path = build_ai_path("embeddings", "patient_notes.parquet")
        # Returns: "ai/embeddings/patient_notes.parquet"
    """
    return f"ai/{subdomain.lower()}/{filename}"


# -----------------------------------------------------------
# Convenience Functions
# -----------------------------------------------------------

def get_default_client() -> MinIOClient:
    """
    Get a MinIO client with default configuration from config.py.

    Returns:
        MinIOClient instance

    Example:
        from lake.minio_client import get_default_client
        client = get_default_client()
    """
    return MinIOClient()
