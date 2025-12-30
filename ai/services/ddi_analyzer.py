"""
Drug-Drug Interaction (DDI) Analyzer Service

Provides functionality to identify potential drug-drug interactions from a reference
database. Refactored from notebook/src/ddi_transforms.py for production use in the
AI Clinical Insights feature.

Architecture:
- Loads DDI reference data from MinIO Parquet (cached in memory)
- Normalizes drug names for fuzzy matching
- Checks all medication pairs for interactions
- Returns interaction details from DrugBank dataset

Data Source: Kaggle DrugBank dataset (~191K interactions)
Schema: drug_1, drug_2, interaction_description

Design Reference: docs/spec/ai-insight-design.md Section 7.1
"""

import pandas as pd
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class DDIAnalyzer:
    """
    Drug-drug interaction analyzer.

    Analyzes a patient's medication list to identify potential drug-drug
    interactions using the DrugBank reference database.

    The analyzer:
    1. Loads DDI reference data at initialization (cached in memory)
    2. Normalizes drug names (removes dosages, lowercase)
    3. Checks all medication pairs against reference database
    4. Returns list of interactions with descriptions

    Attributes:
        ddi_data: Cached DataFrame of DDI reference data from MinIO

    Example:
        >>> analyzer = DDIAnalyzer()
        >>> medications = [
        ...     {'drug_name': 'Warfarin 5MG'},
        ...     {'drug_name': 'Ibuprofen 400MG'}
        ... ]
        >>> interactions = analyzer.find_interactions(medications)
        >>> for interaction in interactions:
        ...     print(f"{interaction['drug_a']} + {interaction['drug_b']}")
        ...     print(f"  {interaction['description']}")
    """

    def __init__(self, ddi_data: Optional[pd.DataFrame] = None):
        """
        Initialize DDI analyzer with reference data.

        Args:
            ddi_data: Optional pre-loaded DDI DataFrame. If None, loads from MinIO.
                     Useful for testing with mock data.
        """
        if ddi_data is not None:
            self.ddi_data = ddi_data
        else:
            self.ddi_data = self._load_ddi_reference()

        logger.info(f"DDI Analyzer initialized with {len(self.ddi_data):,} reference interactions")

    def _load_ddi_reference(self) -> pd.DataFrame:
        """
        Load DDI reference data from MinIO Parquet (cached in memory).

        Loads the processed DDI data from the med-z1 MinIO bucket.
        The data has been processed through the medallion architecture
        (Bronze → Silver → Gold) and is stored as Parquet for fast loading.

        Returns:
            DataFrame with columns: drug_1, drug_2, interaction_description

        Raises:
            FileNotFoundError: If DDI Parquet file not found in MinIO
            ValueError: If required columns are missing from dataset
        """
        from app.services.ddi_loader import get_ddi_reference
        return get_ddi_reference()

    def find_interactions(self, medications: List[Dict]) -> List[Dict]:
        """
        Find drug-drug interactions for a medication list.

        Checks all unique pairs of medications against the DDI reference
        database and returns any matching interactions.

        Args:
            medications: List of medication dicts with drug name key
                        Supports multiple key names: 'drug_name', 'drug_name_national',
                        'drug_name_local', 'generic_name'
                        Example: [{'drug_name_national': 'Warfarin 5MG'}, ...]

        Returns:
            List of interaction dicts with keys:
                - drug_a: First drug name (original)
                - drug_b: Second drug name (original)
                - description: Interaction description from DrugBank

        Example:
            >>> medications = [
            ...     {'drug_name': 'Aspirin 81MG'},
            ...     {'drug_name': 'Warfarin 5MG'},
            ...     {'drug_name': 'Metformin 500MG'}
            ... ]
            >>> interactions = analyzer.find_interactions(medications)
            >>> len(interactions)
            1  # Aspirin + Warfarin interaction found
        """
        if not medications:
            return []

        # Extract drug names - support multiple possible key names
        drug_names = []
        for med in medications:
            # Try different possible drug name fields (in priority order)
            drug_name = (
                med.get('drug_name') or
                med.get('drug_name_national') or
                med.get('drug_name_local') or
                med.get('generic_name')
            )
            if drug_name:
                drug_names.append(drug_name)
            else:
                logger.warning(f"Medication missing drug name field: {med}")

        if not drug_names:
            logger.warning("No valid drug names found in medication list")
            return []

        interactions = []

        # Check all unique pairs
        for i, drug_a in enumerate(drug_names):
            for drug_b in drug_names[i + 1:]:
                interaction = self._check_pair(drug_a, drug_b)
                if interaction:
                    interactions.append(interaction)

        logger.info(
            f"Checked {len(drug_names)} medications, "
            f"found {len(interactions)} interactions"
        )

        # Phase 1 MVP: Return interactions without severity sorting
        # Future enhancement: Add severity classification via LLM or rule-based logic
        return interactions

    def _check_pair(self, drug_a: str, drug_b: str) -> Optional[Dict]:
        """
        Check if two drugs interact.

        Normalizes drug names and queries the DDI reference database
        for a matching interaction. Checks both directions (A+B and B+A)
        since the reference data may have interactions listed either way.

        Args:
            drug_a: First drug name (with dosage)
            drug_b: Second drug name (with dosage)

        Returns:
            Interaction dict if found, None otherwise
            Dict keys: drug_a, drug_b, description

        Example:
            >>> analyzer._check_pair('Warfarin 5MG', 'Aspirin 81MG')
            {
                'drug_a': 'Warfarin 5MG',
                'drug_b': 'Aspirin 81MG',
                'description': 'The risk or severity of bleeding...'
            }
        """
        # Normalize drug names (case-insensitive, remove doses)
        drug_a_clean = self._normalize_drug_name(drug_a)
        drug_b_clean = self._normalize_drug_name(drug_b)

        # Query DDI reference data (check both directions)
        # Note: Column names normalized from Kaggle "Drug 1", "Drug 2", "Interaction Description"
        match = self.ddi_data[
            ((self.ddi_data['drug_1'] == drug_a_clean) &
             (self.ddi_data['drug_2'] == drug_b_clean)) |
            ((self.ddi_data['drug_1'] == drug_b_clean) &
             (self.ddi_data['drug_2'] == drug_a_clean))
        ]

        if not match.empty:
            row = match.iloc[0]  # Take first match if multiple found
            return {
                'drug_a': drug_a,  # Return original names (with dosages)
                'drug_b': drug_b,
                'description': row['interaction_description']
            }

        return None

    def _normalize_drug_name(self, drug: str) -> str:
        """
        Normalize drug name for matching.

        Removes dosage information and standardizes the drug name for
        consistent matching against the reference database.

        Normalization steps:
        1. Remove dosage patterns (e.g., "100MG", "10ML", "5%", "20MEQ")
        2. Convert to lowercase
        3. Collapse multiple spaces to single space
        4. Strip leading/trailing whitespace

        Args:
            drug: Drug name with dosage (e.g., "Warfarin 5MG")

        Returns:
            Normalized drug name (e.g., "warfarin")

        Example:
            >>> analyzer._normalize_drug_name("Warfarin 5MG Tablet")
            'warfarin tablet'
            >>> analyzer._normalize_drug_name("Ibuprofen 400MG")
            'ibuprofen'
            >>> analyzer._normalize_drug_name("Potassium Chloride 20MEQ")
            'potassium chloride'
        """
        # Remove dosage patterns like "100MG", "10ML", "5MCG", "2.5G", "10%", "20MEQ"
        # Pattern explanation:
        # \d+ - one or more digits
        # \.?\d* - optional decimal point and digits
        # \s* - optional whitespace
        # (MG|ML|MCG|MEQ|G|%|UNITS?) - dosage units (case-insensitive)
        clean = re.sub(
            r'\d+\.?\d*\s*(MG|ML|MCG|MEQ|G|%|UNITS?)',
            '',
            drug,
            flags=re.IGNORECASE
        )

        # Lowercase
        clean = clean.lower()

        # Collapse multiple spaces to single space
        clean = re.sub(r'\s+', ' ', clean)

        # Strip leading/trailing whitespace
        clean = clean.strip()

        return clean

    def get_interaction_count(self) -> int:
        """
        Get total number of interactions in reference database.

        Returns:
            Total count of drug-drug interactions available

        Example:
            >>> analyzer.get_interaction_count()
            191541
        """
        return len(self.ddi_data)

    def search_drug(self, drug_name: str) -> List[str]:
        """
        Search for a drug in the reference database.

        Useful for debugging and understanding what drug names exist
        in the reference data.

        Args:
            drug_name: Drug name to search for (partial match ok)

        Returns:
            List of matching drug names from reference database

        Example:
            >>> analyzer.search_drug('warfarin')
            ['Warfarin', 'Warfarin Sodium', ...]
        """
        normalized = self._normalize_drug_name(drug_name)

        # Search in both drug_1 and drug_2 columns
        matches_1 = self.ddi_data[
            self.ddi_data['drug_1'].str.contains(normalized, case=False, na=False)
        ]['drug_1'].unique()

        matches_2 = self.ddi_data[
            self.ddi_data['drug_2'].str.contains(normalized, case=False, na=False)
        ]['drug_2'].unique()

        # Combine and deduplicate
        all_matches = list(set(list(matches_1) + list(matches_2)))
        all_matches.sort()

        return all_matches
