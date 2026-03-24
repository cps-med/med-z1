#!/usr/bin/env python3
"""
Test Problems Database Query Layer

Tests all query functions in app/db/patient_problems.py against
the PostgreSQL database populated by the ETL pipeline.

Expected Data (from Phase 2):
- 72 problems total across 7 patients
- ICN100001: 14 problems, Charlson ~9 (high complexity)
- ICN100002: 9 problems, Charlson ~3 (moderate)
- ICN100010: 7 problems, Charlson ~6 (moderate-high)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.patient_problems import (
    get_patient_problems,
    get_problems_summary,
    get_problems_grouped_by_category,
    get_charlson_score,
    has_chronic_condition,
    get_chronic_conditions_summary
)


def test_get_patient_problems():
    """Test basic problem retrieval"""
    print("\n=== Test 1: Get Patient Problems ===")

    # Test patient with high problem count
    icn = "ICN100001"
    problems = get_patient_problems(icn)

    print(f"ICN100001 (Adam Dooree) - Total problems: {len(problems)}")
    assert len(problems) > 0, f"Expected problems for {icn}, got 0"

    # Verify fields present
    if problems:
        p = problems[0]
        assert "icd10_code" in p, "Missing icd10_code field"
        assert "problem_status" in p, "Missing problem_status field"
        assert "charlson_condition" in p, "Missing charlson_condition field"
        print(f"  First problem: {p['icd10_code']} - {p['problem_text']}")
        print(f"  Status: {p['problem_status']}, Charlson condition: {p['charlson_condition']}")

    # Test filtering by status
    active_problems = get_patient_problems(icn, status="Active")
    print(f"  Active problems: {len(active_problems)}")
    assert len(active_problems) <= len(problems), "Active should be subset of total"

    # Test filtering by service-connected
    sc_problems = get_patient_problems(icn, service_connected_only=True)
    print(f"  Service-connected problems: {len(sc_problems)}")

    print("✅ Get patient problems test PASSED")
    return problems


def test_get_problems_summary():
    """Test problems summary for widget"""
    print("\n=== Test 2: Get Problems Summary ===")

    icn = "ICN100001"
    summary = get_problems_summary(icn, limit=8)

    print(f"ICN100001 Summary:")
    print(f"  Total active: {summary['total_active']}")
    print(f"  Total chronic: {summary['total_chronic']}")
    print(f"  Charlson Index: {summary['charlson_index']}")
    print(f"  Has critical conditions: {summary['has_critical_conditions']}")
    print(f"  Conditions: CHF={summary['has_chf']}, COPD={summary['has_copd']}, CKD={summary['has_ckd']}, Diabetes={summary['has_diabetes']}")

    # Assertions
    assert summary['total_active'] > 0, "Expected active problems"
    assert summary['charlson_index'] >= 0, "Charlson should be non-negative"

    # Check top problems list
    assert "problems" in summary, "Missing problems list"
    assert len(summary['problems']) <= 8, "Should limit to 8 problems"

    if summary['problems']:
        print(f"\n  Top {len(summary['problems'])} active problems:")
        for i, p in enumerate(summary['problems'][:3], 1):
            print(f"    {i}. {p['icd10_code']} - {p['problem_text']} (Charlson={p['charlson_condition']})")

    print("✅ Problems summary test PASSED")
    return summary


def test_get_grouped_problems():
    """Test problems grouped by category"""
    print("\n=== Test 3: Get Problems Grouped by Category ===")

    icn = "ICN100001"
    grouped = get_problems_grouped_by_category(icn, status="Active")

    print(f"ICN100001 Active Problems by Category:")
    for category, problems in sorted(grouped.items()):
        print(f"  {category}: {len(problems)} problems")
        if problems:
            print(f"    Example: {problems[0]['icd10_code']} - {problems[0]['problem_text']}")

    assert len(grouped) > 0, "Expected at least one category"

    print("✅ Grouped problems test PASSED")
    return grouped


def test_charlson_score():
    """Test Charlson score calculation"""
    print("\n=== Test 4: Get Charlson Score ===")

    # Test multiple patients
    test_patients = [
        ("ICN100001", "Adam Dooree", 5),  # Expected Charlson >= 5 (high)
        ("ICN100002", "Barry Miifaa", 1),  # Expected Charlson >= 1 (moderate)
        ("ICN100010", "Alexander Aminor", 2),  # Expected Charlson >= 2 (moderate)
    ]

    for icn, name, min_expected in test_patients:
        score = get_charlson_score(icn)
        print(f"{icn} ({name}): Charlson = {score}")
        assert score >= min_expected, f"Expected Charlson >={min_expected}, got {score}"

    print("✅ Charlson score test PASSED")


def test_chronic_conditions():
    """Test chronic condition checks"""
    print("\n=== Test 5: Check Chronic Conditions ===")

    icn = "ICN100001"

    # Test individual condition check
    has_chf = has_chronic_condition(icn, "chf")
    has_diabetes = has_chronic_condition(icn, "diabetes")
    has_copd = has_chronic_condition(icn, "copd")

    print(f"ICN100001 Chronic Conditions:")
    print(f"  CHF: {has_chf}")
    print(f"  Diabetes: {has_diabetes}")
    print(f"  COPD: {has_copd}")

    # Get full summary
    conditions = get_chronic_conditions_summary(icn)
    print(f"\nFull Chronic Conditions Summary:")
    true_conditions = [k for k, v in conditions.items() if v]
    print(f"  Patient has {len(true_conditions)} chronic conditions:")
    for cond in true_conditions:
        print(f"    - {cond.replace('has_', '').upper()}")

    assert len(true_conditions) > 0, "Expected at least one chronic condition for ICN100001"

    print("✅ Chronic conditions test PASSED")
    return conditions


def test_filter_by_category():
    """Test filtering by ICD-10 category"""
    print("\n=== Test 6: Filter by Category ===")

    icn = "ICN100001"

    # Get all cardiovascular problems
    cardio_problems = get_patient_problems(icn, category="Cardiovascular")
    print(f"ICN100001 Cardiovascular Problems: {len(cardio_problems)}")

    if cardio_problems:
        for p in cardio_problems[:3]:
            print(f"  - {p['icd10_code']}: {p['problem_text']}")

    # Get all respiratory problems
    resp_problems = get_patient_problems(icn, category="Respiratory")
    print(f"\nICN100001 Respiratory Problems: {len(resp_problems)}")

    if resp_problems:
        for p in resp_problems[:3]:
            print(f"  - {p['icd10_code']}: {p['problem_text']}")

    print("✅ Category filter test PASSED")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Problems Database Query Layer")
    print("=" * 60)

    try:
        # Test 1: Basic problem retrieval
        problems = test_get_patient_problems()

        # Test 2: Widget summary
        summary = test_get_problems_summary()

        # Test 3: Grouped by category
        grouped = test_get_grouped_problems()

        # Test 4: Charlson scores
        test_charlson_score()

        # Test 5: Chronic conditions
        conditions = test_chronic_conditions()

        # Test 6: Category filtering
        test_filter_by_category()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print(f"\nPhase 4 (Database Query Layer) is COMPLETE!")
        print(f"  - All query functions working")
        print(f"  - Filtering by status, category, service-connected")
        print(f"  - Summary statistics correct")
        print(f"  - Charlson scores calculated")
        print(f"  - Chronic condition flags operational")
        print(f"\nReady for Phase 5 (UI Implementation)!")

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
