"""
DDI Reference Data Loader

Loads drug-drug interaction reference data from MinIO for use by the
AI Clinical Insights feature. Provides cached access to the DDI dataset
processed through the medallion architecture.

Architecture:
- Loads from MinIO med-z1 bucket (Gold layer Parquet)
- Converts from Polars to Pandas for compatibility with DDIAnalyzer
- Caches in memory to avoid repeated MinIO calls
- Thread-safe for concurrent access

Data Source: Kaggle DrugBank dataset (~191K interactions)
MinIO Path: med-z1/gold/ddi/ddi_reference.parquet

Design Reference: docs/spec/ai-insight-design.md Section 3.1
"""

import pandas as pd
import logging
from typing import Optional

from lake.minio_client import MinIOClient

logger = logging.getLogger(__name__)

# Module-level cache for DDI reference data
_ddi_cache: Optional[pd.DataFrame] = None


def get_ddi_reference(force_reload: bool = False) -> pd.DataFrame:
    """
    Get DDI reference data from MinIO (cached).

    Loads the drug-drug interaction reference dataset from the MinIO
    gold layer. The data is cached in memory after the first load to
    avoid repeated MinIO calls.

    The reference data contains ~191K drug-drug interactions from the
    DrugBank dataset (via Kaggle), processed through the medallion
    architecture (Bronze → Silver → Gold).

    Args:
        force_reload: If True, bypass cache and reload from MinIO
                     (default: False, use cache if available)

    Returns:
        Pandas DataFrame with columns:
            - drug_1: First drug in interaction pair
            - drug_2: Second drug in interaction pair
            - interaction_description: Description of the interaction

    Raises:
        FileNotFoundError: If DDI Parquet file not found in MinIO
        ValueError: If required columns are missing from dataset

    Example:
        >>> ddi_data = get_ddi_reference()
        >>> print(f"Loaded {len(ddi_data):,} interactions")
        Loaded 191,541 interactions
        >>> print(ddi_data.columns.tolist())
        ['drug_1', 'drug_2', 'interaction_description']
    """
    global _ddi_cache

    # Return cached data if available and not forcing reload
    if _ddi_cache is not None and not force_reload:
        logger.debug(f"Returning cached DDI data ({len(_ddi_cache):,} interactions)")
        return _ddi_cache

    logger.info("Loading DDI reference data from MinIO...")

    try:
        # Initialize MinIO client
        client = MinIOClient()

        # Load DDI reference Parquet from Gold layer
        # Path: med-z1/gold/ddi/ddi_reference.parquet
        object_key = "gold/ddi/ddi_reference.parquet"

        # Read Parquet file (returns Polars DataFrame)
        df_polars = client.read_parquet(object_key)

        # Convert to Pandas for compatibility with DDIAnalyzer
        df_pandas = df_polars.to_pandas()

        # Validate required columns exist
        required_columns = ['drug_1', 'drug_2', 'interaction_description']
        missing_columns = [col for col in required_columns if col not in df_pandas.columns]

        if missing_columns:
            raise ValueError(
                f"DDI reference data missing required columns: {missing_columns}. "
                f"Found columns: {df_pandas.columns.tolist()}"
            )

        # Cache for future calls
        _ddi_cache = df_pandas

        logger.info(
            f"Successfully loaded DDI reference: {len(df_pandas):,} interactions, "
            f"{df_pandas.memory_usage(deep=True).sum() / 1024 / 1024:.1f} MB in memory"
        )

        return df_pandas

    except FileNotFoundError:
        logger.error(
            f"DDI reference file not found in MinIO: {object_key}. "
            "Ensure DDI data has been processed through ETL pipeline."
        )
        raise

    except Exception as e:
        logger.error(f"Failed to load DDI reference data: {e}")
        raise


def clear_ddi_cache() -> None:
    """
    Clear the in-memory DDI reference cache.

    Useful for:
    - Testing with different datasets
    - Forcing a reload after DDI data updates
    - Freeing memory when DDI analysis not needed

    Example:
        >>> clear_ddi_cache()
        >>> # Next call to get_ddi_reference() will reload from MinIO
    """
    global _ddi_cache
    _ddi_cache = None
    logger.info("DDI reference cache cleared")


def get_ddi_stats() -> dict:
    """
    Get statistics about the loaded DDI reference data.

    Returns:
        Dict with keys:
            - total_interactions: Total number of interactions
            - unique_drugs: Number of unique drugs in dataset
            - memory_mb: Memory usage in megabytes
            - cached: Whether data is currently cached

    Example:
        >>> stats = get_ddi_stats()
        >>> print(f"Total interactions: {stats['total_interactions']:,}")
        Total interactions: 191,541
    """
    if _ddi_cache is None:
        return {
            'total_interactions': 0,
            'unique_drugs': 0,
            'memory_mb': 0.0,
            'cached': False
        }

    unique_drugs = set(
        list(_ddi_cache['drug_1'].unique()) +
        list(_ddi_cache['drug_2'].unique())
    )

    return {
        'total_interactions': len(_ddi_cache),
        'unique_drugs': len(unique_drugs),
        'memory_mb': _ddi_cache.memory_usage(deep=True).sum() / 1024 / 1024,
        'cached': True
    }
