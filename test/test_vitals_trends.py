#!/usr/bin/env python3
"""
Test script for Vitals Trend Analyzer
Tests the analyze_vitals_trends functionality with multiple patients
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai.services.vitals_trend_analyzer import VitalsTrendAnalyzer
from ai.tools.vitals_tools import analyze_vitals_trends


def test_direct_analyzer():
    """Test VitalsTrendAnalyzer directly."""
    print("=" * 80)
    print("TEST 1: Direct VitalsTrendAnalyzer Test")
    print("=" * 80)

    # Test with multiple patients
    test_patients = [
        "ICN100001",
        "ICN100002",
        "ICN100004",
        "ICN100009",
        "ICN100010"
    ]

    for icn in test_patients:
        print(f"\n--- Testing patient: {icn} ---")

        analyzer = VitalsTrendAnalyzer(patient_icn=icn)
        trends = analyzer.analyze_trends(days=90)

        if 'error' in trends:
            print(f"❌ Error: {trends['error']}")
            continue

        print(f"✅ Total readings: {trends['total_readings']}")
        print(f"   Date range: {trends['date_range']}")

        # Print summary of each vital type
        if 'bp' in trends:
            bp = trends['bp']
            print(f"   BP: {bp['avg_systolic']}/{bp['avg_diastolic']} mmHg - {bp['status']} ({bp['reading_count']} readings)")

        if 'hr' in trends:
            hr = trends['hr']
            print(f"   HR: {hr['avg']} bpm - {hr['status']} ({hr['reading_count']} readings)")

        if 'temp' in trends:
            temp = trends['temp']
            print(f"   Temp: {temp['avg']}°F - {temp['status']} ({temp['reading_count']} readings)")

        if 'weight' in trends:
            weight = trends['weight']
            print(f"   Weight: {weight['avg']} lbs - {weight['status']} ({weight['reading_count']} readings)")


def test_langchain_tool():
    """Test the analyze_vitals_trends LangChain tool."""
    print("\n" + "=" * 80)
    print("TEST 2: LangChain Tool Test (analyze_vitals_trends)")
    print("=" * 80)

    # Test with one patient to see full formatted output
    test_icn = "ICN100001"
    print(f"\n--- Testing tool with patient: {test_icn} ---\n")

    result = analyze_vitals_trends.invoke({"patient_icn": test_icn, "days": 90})
    print(result)


def test_short_period():
    """Test with shorter time period (30 days)."""
    print("\n" + "=" * 80)
    print("TEST 3: Short Period Test (30 days)")
    print("=" * 80)

    test_icn = "ICN100002"
    print(f"\n--- Testing patient: {test_icn} (last 30 days) ---\n")

    result = analyze_vitals_trends.invoke({"patient_icn": test_icn, "days": 30})
    print(result)


if __name__ == "__main__":
    print("Testing Vitals Trend Analyzer")
    print("=" * 80)

    try:
        # Run all tests
        test_direct_analyzer()
        test_langchain_tool()
        test_short_period()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
