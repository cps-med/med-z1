#!/usr/bin/env python3
"""
Test script to verify vitals query layer returns data_source field.
Queries vitals for ICN100001 (Adam Dooree) who has both CDWWork and CDWWork2 vitals.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.vitals import get_patient_vitals

def test_vitals_data_source():
    """Test that vitals query returns data_source field."""
    print("=" * 70)
    print("Testing Vitals Query Layer - Data Source Field")
    print("=" * 70)

    # Test patient with both CDWWork and CDWWork2 vitals
    icn = "ICN100001"
    print(f"\nQuerying vitals for patient: {icn}")

    vitals = get_patient_vitals(icn, limit=15)

    print(f"Retrieved {len(vitals)} vitals\n")

    # Group by data source
    source_counts = {}
    for vital in vitals:
        source = vital.get('data_source', 'UNKNOWN')
        source_counts[source] = source_counts.get(source, 0) + 1

    print("Data Source Distribution:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count} vitals")

    print("\nSample Vitals (first 5):")
    print("-" * 70)
    for i, vital in enumerate(vitals[:5], 1):
        print(f"{i}. {vital['vital_type']} ({vital['vital_abbr']})")
        print(f"   Value: {vital['result_value']}")
        print(f"   Date: {vital['taken_datetime'][:10] if vital['taken_datetime'] else 'N/A'}")
        print(f"   Source: {vital.get('data_source', 'MISSING')}")
        print()

    # Verify all vitals have data_source
    missing_source = [v for v in vitals if 'data_source' not in v]
    if missing_source:
        print(f"❌ FAIL: {len(missing_source)} vitals missing data_source field")
        return False
    else:
        print("✅ PASS: All vitals have data_source field")

    # Verify we have both sources
    if 'CDWWork' in source_counts and 'CDWWork2' in source_counts:
        print("✅ PASS: Both CDWWork and CDWWork2 vitals present")
    else:
        print(f"❌ FAIL: Expected both sources, got: {list(source_counts.keys())}")
        return False

    print("\n" + "=" * 70)
    print("Test completed successfully!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_vitals_data_source()
    sys.exit(0 if success else 1)
