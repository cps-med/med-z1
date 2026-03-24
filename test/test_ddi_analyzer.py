"""
Unit tests for DDI Analyzer

Tests the drug-drug interaction analyzer with sample medications to verify:
1. Drug name normalization works correctly
2. Interaction matching finds known pairs
3. All medication pairs are checked
4. Results are formatted correctly

Usage:
    python scripts/test_ddi_analyzer.py

Note: This test uses mock DDI data since the actual DDI reference may not be
      loaded yet in MinIO. Replace with real data loader once available.

Design Reference: docs/spec/ai-insight-design.md Section 7.1
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from ai.services.ddi_analyzer import DDIAnalyzer


def create_mock_ddi_data() -> pd.DataFrame:
    """
    Create mock DDI reference data for testing.

    Returns a small DataFrame with known drug interactions
    for testing purposes.
    """
    data = {
        'drug_1': ['warfarin', 'aspirin', 'lisinopril', 'metformin'],
        'drug_2': ['aspirin', 'ibuprofen', 'potassium chloride', 'glyburide'],
        'interaction_description': [
            'The risk or severity of bleeding can be increased when Warfarin is combined with Aspirin',
            'The risk or severity of bleeding and gastrointestinal ulceration can be increased when Aspirin is combined with Ibuprofen',
            'The risk or severity of hyperkalemia can be increased when Lisinopril is combined with Potassium supplements',
            'The risk or severity of hypoglycemia can be increased when Metformin is combined with Glyburide'
        ]
    }
    return pd.DataFrame(data)


def test_drug_name_normalization():
    """Test 1: Drug name normalization"""
    print("\n" + "=" * 70)
    print("Test 1: Drug Name Normalization")
    print("=" * 70)

    # Create analyzer with mock data
    mock_data = create_mock_ddi_data()
    analyzer = DDIAnalyzer(ddi_data=mock_data)

    test_cases = [
        ("Warfarin 5MG", "warfarin"),
        ("ASPIRIN 81MG Tablet", "aspirin tablet"),
        ("Metformin 500MG", "metformin"),
        ("Lisinopril 10MG", "lisinopril"),
        ("Potassium Chloride 20MEQ", "potassium chloride"),
    ]

    print("\nNormalization Test Cases:")
    all_passed = True
    for input_drug, expected in test_cases:
        result = analyzer._normalize_drug_name(input_drug)
        passed = result == expected
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        print(f"  {status} '{input_drug}' → '{result}' (expected: '{expected}')")

    print(f"\n{'✅ All normalization tests passed!' if all_passed else '❌ Some tests failed'}")
    return all_passed


def test_interaction_matching():
    """Test 2: Interaction matching for known pairs"""
    print("\n" + "=" * 70)
    print("Test 2: Interaction Matching")
    print("=" * 70)

    # Create analyzer with mock data
    mock_data = create_mock_ddi_data()
    analyzer = DDIAnalyzer(ddi_data=mock_data)

    # Test cases: (drug_a, drug_b, should_match)
    test_cases = [
        ("Warfarin 5MG", "Aspirin 81MG", True),   # Known interaction
        ("Aspirin 81MG", "Ibuprofen 400MG", True),  # Known interaction
        ("Lisinopril 10MG", "Potassium Chloride 20MEQ", True),  # Known interaction
        ("Warfarin 5MG", "Metformin 500MG", False),  # No interaction in mock data
        ("Tylenol 500MG", "Aspirin 81MG", False),  # No interaction (drug not in dataset)
    ]

    print("\nInteraction Matching Test Cases:")
    all_passed = True
    for drug_a, drug_b, should_match in test_cases:
        interaction = analyzer._check_pair(drug_a, drug_b)
        matched = interaction is not None
        passed = matched == should_match

        all_passed = all_passed and passed
        status = "✓" if passed else "✗"

        if matched:
            print(f"  {status} {drug_a} + {drug_b} → FOUND")
            print(f"      {interaction['description'][:80]}...")
        else:
            print(f"  {status} {drug_a} + {drug_b} → NOT FOUND (expected: {'found' if should_match else 'not found'})")

    print(f"\n{'✅ All matching tests passed!' if all_passed else '❌ Some tests failed'}")
    return all_passed


def test_bidirectional_matching():
    """Test 3: Bidirectional matching (A+B == B+A)"""
    print("\n" + "=" * 70)
    print("Test 3: Bidirectional Matching")
    print("=" * 70)

    # Create analyzer with mock data
    mock_data = create_mock_ddi_data()
    analyzer = DDIAnalyzer(ddi_data=mock_data)

    print("\nTesting that drug order doesn't matter:")
    test_pairs = [
        ("Warfarin 5MG", "Aspirin 81MG"),
        ("Lisinopril 10MG", "Potassium Chloride 20MEQ"),
    ]

    all_passed = True
    for drug_a, drug_b in test_pairs:
        # Check A+B
        interaction_ab = analyzer._check_pair(drug_a, drug_b)
        # Check B+A (reversed)
        interaction_ba = analyzer._check_pair(drug_b, drug_a)

        both_found = (interaction_ab is not None) and (interaction_ba is not None)
        passed = both_found

        all_passed = all_passed and passed
        status = "✓" if passed else "✗"

        print(f"  {status} {drug_a} + {drug_b}")
        print(f"      Forward:  {'Found' if interaction_ab else 'Not found'}")
        print(f"      Backward: {'Found' if interaction_ba else 'Not found'}")

    print(f"\n{'✅ All bidirectional tests passed!' if all_passed else '❌ Some tests failed'}")
    return all_passed


def test_medication_list_analysis():
    """Test 4: Analyzing a full medication list"""
    print("\n" + "=" * 70)
    print("Test 4: Medication List Analysis")
    print("=" * 70)

    # Create analyzer with mock data
    mock_data = create_mock_ddi_data()
    analyzer = DDIAnalyzer(ddi_data=mock_data)

    # Sample medication list
    medications = [
        {'drug_name': 'Warfarin 5MG'},
        {'drug_name': 'Aspirin 81MG'},
        {'drug_name': 'Lisinopril 10MG'},
        {'drug_name': 'Potassium Chloride 20MEQ'},
        {'drug_name': 'Metformin 500MG'},
    ]

    print(f"\nAnalyzing medication list ({len(medications)} medications):")
    for med in medications:
        print(f"  - {med['drug_name']}")

    interactions = analyzer.find_interactions(medications)

    print(f"\nFound {len(interactions)} interactions:")
    for i, interaction in enumerate(interactions, 1):
        print(f"  {i}. {interaction['drug_a']} + {interaction['drug_b']}")
        print(f"     {interaction['description'][:80]}...")

    # Expected: 2 interactions (Warfarin+Aspirin, Lisinopril+Potassium)
    expected_count = 2
    passed = len(interactions) == expected_count

    status = "✅" if passed else "❌"
    print(f"\n{status} Expected {expected_count} interactions, found {len(interactions)}")

    return passed


def test_no_interactions():
    """Test 5: No interactions found (negative case)"""
    print("\n" + "=" * 70)
    print("Test 5: No Interactions Found")
    print("=" * 70)

    # Create analyzer with mock data
    mock_data = create_mock_ddi_data()
    analyzer = DDIAnalyzer(ddi_data=mock_data)

    # Medication list with no interactions
    medications = [
        {'drug_name': 'Metformin 500MG'},
        {'drug_name': 'Atorvastatin 20MG'},  # Not in mock data
        {'drug_name': 'Omeprazole 40MG'},  # Not in mock data
    ]

    print(f"\nAnalyzing medication list ({len(medications)} medications):")
    for med in medications:
        print(f"  - {med['drug_name']}")

    interactions = analyzer.find_interactions(medications)

    print(f"\nFound {len(interactions)} interactions (expected: 0)")

    passed = len(interactions) == 0
    status = "✅" if passed else "❌"
    print(f"\n{status} {'No interactions found as expected' if passed else 'Unexpected interactions found'}")

    return passed


def main():
    """Run all DDI analyzer tests"""
    print("=" * 70)
    print("DDI Analyzer Unit Test Suite")
    print("=" * 70)
    print("\nTesting DDI analyzer with mock reference data...")

    results = []

    # Run all tests
    results.append(("Drug Name Normalization", test_drug_name_normalization()))
    results.append(("Interaction Matching", test_interaction_matching()))
    results.append(("Bidirectional Matching", test_bidirectional_matching()))
    results.append(("Medication List Analysis", test_medication_list_analysis()))
    results.append(("No Interactions Found", test_no_interactions()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
        all_passed = all_passed and passed

    print("=" * 70)

    if all_passed:
        print("\n✅ All DDI analyzer tests passed!")
        print("\nNext steps:")
        print("  1. Load actual DDI reference data into MinIO")
        print("  2. Test with real patient medications")
        print("  3. Integrate with LangGraph agent")
    else:
        print("\n❌ Some tests failed - please review and fix")
        sys.exit(1)


if __name__ == "__main__":
    main()
