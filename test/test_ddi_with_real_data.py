"""
Test DDI Analyzer with Real Data

Tests the DDI analyzer with actual DDI reference data loaded from PostgreSQL
and real patient medication data from PostgreSQL.

This verifies:
1. DDI reference data loads correctly from PostgreSQL reference.ddi
2. Real patient medications can be queried
3. Interactions are found for actual drug pairs
4. The complete flow works end-to-end

Usage:
    python scripts/test_ddi_with_real_data.py

Prerequisites:
    - DDI reference data loaded into PostgreSQL (reference.ddi)
    - PostgreSQL with patient medication data
    - Patient ICN with medications in the database
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.services.ddi_analyzer import DDIAnalyzer
from app.services.ddi_loader import get_ddi_stats, clear_ddi_cache
from app.db.medications import get_patient_medications


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'=' * 70}")
        print(f"  {title}")
        print('=' * 70)
    else:
        print('-' * 70)


def test_ddi_reference_load():
    """Test 1: Load DDI reference data from PostgreSQL"""
    print_separator("Test 1: Load DDI Reference Data")

    try:
        # Clear cache to force fresh load
        clear_ddi_cache()

        # Initialize analyzer (this will load DDI reference from PostgreSQL)
        print("\nInitializing DDI Analyzer (loading from PostgreSQL)...")
        analyzer = DDIAnalyzer()

        # Get statistics
        stats = get_ddi_stats()

        print("\n✅ DDI Reference Data Loaded Successfully!")
        print(f"   Total interactions: {stats['total_interactions']:,}")
        print(f"   Unique drugs: {stats['unique_drugs']:,}")
        print(f"   Memory usage: {stats['memory_mb']:.1f} MB")
        print(f"   Cached: {stats['cached']}")

        return analyzer

    except Exception as e:
        print(f"\n❌ Failed to load DDI reference data: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_patient_medications():
    """Test 2: Query patient medications from PostgreSQL"""
    print_separator("Test 2: Query Patient Medications")

    # Test with a known patient ICN
    # Update this with an ICN that has medications in your database
    # John Doe from demo data (no data available, so commenting out)
    # test_icn = "1011530429V926058"
    # Adam Dooree
    # test_icn = "ICN100001"
    # Alexander Aminor
    test_icn = "ICN100010"


    print(f"\nQuerying medications for patient: {test_icn}")

    try:
        medications = get_patient_medications(test_icn)

        if not medications:
            print(f"\n⚠️  No medications found for patient {test_icn}")
            print("   Try a different ICN or load medication data into PostgreSQL")
            return None, test_icn

        print(f"\n✅ Found {len(medications)} medications:")
        for i, med in enumerate(medications[:10], 1):  # Show first 10
            # Support multiple drug name fields (same logic as DDIAnalyzer)
            drug_name = (
                med.get('drug_name') or
                med.get('drug_name_national') or
                med.get('drug_name_local') or
                med.get('generic_name') or
                'Unknown'
            )
            print(f"   {i}. {drug_name}")

        if len(medications) > 10:
            print(f"   ... and {len(medications) - 10} more")

        return medications, test_icn

    except Exception as e:
        print(f"\n❌ Failed to query medications: {e}")
        import traceback
        traceback.print_exc()
        return None, test_icn


def test_ddi_analysis(analyzer, medications, patient_icn):
    """Test 3: Analyze medications for DDI risks"""
    print_separator("Test 3: DDI Risk Analysis")

    if not analyzer or not medications:
        print("\n⚠️  Skipping - prerequisites not met")
        return

    print(f"\nAnalyzing {len(medications)} medications for patient {patient_icn}...")

    try:
        interactions = analyzer.find_interactions(medications)

        if not interactions:
            print(f"\n✅ No drug-drug interactions found")
            print(f"   ({len(medications)} medications checked, all pairs safe)")
        else:
            print(f"\n⚠️  Found {len(interactions)} drug-drug interactions:")
            print()

            for i, interaction in enumerate(interactions, 1):
                print(f"{i}. {interaction['drug_a']} + {interaction['drug_b']}")
                # Truncate description for readability
                desc = interaction['description']
                if len(desc) > 100:
                    desc = desc[:100] + "..."
                print(f"   {desc}")
                print()

            print(f"✅ DDI analysis complete: {len(interactions)} interactions found")

        return interactions

    except Exception as e:
        print(f"\n❌ DDI analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_specific_drug_pairs(analyzer):
    """Test 4: Test known drug interaction pairs"""
    print_separator("Test 4: Test Known Interaction Pairs")

    if not analyzer:
        print("\n⚠️  Skipping - analyzer not initialized")
        return

    # Known interacting drug pairs (common in clinical practice)
    test_pairs = [
        ("Warfarin", "Aspirin"),
        ("Lisinopril", "Potassium Chloride"),
        ("Metformin", "Contrast Media"),
        ("Simvastatin", "Gemfibrozil"),
    ]

    print("\nTesting known interacting drug pairs:")
    found_count = 0

    for drug_a, drug_b in test_pairs:
        interaction = analyzer._check_pair(drug_a, drug_b)
        if interaction:
            found_count += 1
            print(f"   ✓ {drug_a} + {drug_b}: FOUND")
        else:
            print(f"   ✗ {drug_a} + {drug_b}: NOT FOUND (may not be in reference data)")

    print(f"\n{found_count}/{len(test_pairs)} known pairs found in reference data")


def main():
    """Run all tests with real data"""
    print("=" * 70)
    print("DDI Analyzer Real Data Test Suite")
    print("=" * 70)
    print("\nTesting DDI analyzer with PostgreSQL reference and clinical data...")

    # Test 1: Load DDI reference
    analyzer = test_ddi_reference_load()

    # Test 2: Query patient medications
    medications, patient_icn = test_patient_medications()

    # Test 3: Analyze for DDI risks
    interactions = test_ddi_analysis(analyzer, medications, patient_icn)

    # Test 4: Test known pairs
    test_specific_drug_pairs(analyzer)

    # Summary
    print_separator("Summary")

    if analyzer and medications and interactions is not None:
        print("\n✅ All tests completed successfully!")
        print("\nThe DDI analyzer is working correctly with real data:")
        print(f"   ✓ DDI reference loaded from PostgreSQL reference.ddi")
        print(f"   ✓ Patient medications queried from PostgreSQL")
        print(f"   ✓ DDI analysis completed")
        print("\nNext steps:")
        print("   1. Update ai/tools/__init__.py to export check_ddi_risks")
        print("   2. Test with LangGraph agent")
        print("   3. Integrate into med-z1 web UI")
    else:
        print("\n⚠️  Some tests did not complete")
        print("\nPossible issues:")
        print("   - DDI reference data not in MinIO")
        print("   - No patient medications in PostgreSQL")
        print("   - Database connection issues")

    print("=" * 70)


if __name__ == "__main__":
    main()
