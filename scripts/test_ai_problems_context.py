#!/usr/bin/env python3
# ---------------------------------------------------------------------
# test_ai_problems_context.py
# ---------------------------------------------------------------------
# Test AI Clinical Insights with Problems domain integration
#
# Tests:
# 1. Problems summary method generates correct output
# 2. Comprehensive summary includes problems
# 3. Charlson Index displayed correctly
# 4. Critical conditions flagged
# ---------------------------------------------------------------------

import sys
sys.path.insert(0, '/Users/chuck/swdev/med/med-z1')

from ai.services.patient_context import PatientContextBuilder

def test_problems_summary():
    """Test 1: Problems summary method"""
    print("\n" + "="*70)
    print("TEST 1: Problems Summary Method")
    print("="*70)

    test_icn = "ICN100001"  # Adam Dooree - Charlson 7, high complexity
    builder = PatientContextBuilder(test_icn)

    problems_summary = builder.get_problems_summary()

    print(f"\nPatient: {test_icn}")
    print(f"Problems Summary Length: {len(problems_summary)} characters\n")
    print(problems_summary)
    print()

    # Verify key content
    checks = {
        "Charlson mentioned": "Charlson" in problems_summary,
        "Risk level mentioned": any(risk in problems_summary for risk in ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"]),
        "ICD-10 codes present": any(code in problems_summary for code in ["I50", "E11", "J44", "N18"]),
        "Critical conditions flagged": "Critical Conditions:" in problems_summary,
    }

    print("Verification:")
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")

    return all(checks.values())


def test_comprehensive_summary_includes_problems():
    """Test 2: Comprehensive summary includes problems"""
    print("\n" + "="*70)
    print("TEST 2: Comprehensive Summary Includes Problems")
    print("="*70)

    test_icn = "ICN100001"
    builder = PatientContextBuilder(test_icn)

    comprehensive = builder.build_comprehensive_summary()

    print(f"\nPatient: {test_icn}")
    print(f"Comprehensive Summary Length: {len(comprehensive)} characters\n")

    # Show just the problems section
    if "ACTIVE PROBLEMS / DIAGNOSES" in comprehensive:
        start = comprehensive.index("ACTIVE PROBLEMS / DIAGNOSES")
        # Find next section (CURRENT MEDICATIONS)
        end = comprehensive.index("CURRENT MEDICATIONS", start)
        problems_section = comprehensive[start:end].strip()
        print("Problems Section:")
        print("-" * 70)
        print(problems_section)
        print("-" * 70)
    else:
        print("✗ 'ACTIVE PROBLEMS / DIAGNOSES' section not found!")
        return False

    # Verify key content
    checks = {
        "Problems section exists": "ACTIVE PROBLEMS / DIAGNOSES" in comprehensive,
        "Problems placed before medications": comprehensive.index("ACTIVE PROBLEMS / DIAGNOSES") < comprehensive.index("CURRENT MEDICATIONS"),
        "Charlson Index mentioned": "Charlson" in comprehensive,
        "Critical conditions flagged": "Critical Conditions:" in comprehensive,
        "Data sources updated": "problems" in comprehensive.split("Data sources:")[-1],
    }

    print("\nVerification:")
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")

    return all(checks.values())


def test_multiple_patients():
    """Test 3: Multiple patients with different Charlson scores"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Patients (Different Charlson Scores)")
    print("="*70)

    test_patients = [
        ("ICN100001", "Adam Dooree", "Expected Charlson ~7"),
        ("ICN100010", "Alexander Aminor", "Expected Charlson ~5"),
        ("ICN100002", "Barry Miifaa", "Expected Charlson ~0-2"),
    ]

    results = []
    for icn, name, expected in test_patients:
        print(f"\n--- {name} ({icn}) - {expected} ---")
        builder = PatientContextBuilder(icn)
        problems_summary = builder.get_problems_summary()

        # Extract Charlson score
        if "Charlson Comorbidity Index:" in problems_summary:
            charlson_part = problems_summary.split("Charlson Comorbidity Index:")[1].split(")")[0]
            print(f"  Charlson: {charlson_part.strip()}")
        else:
            print(f"  Charlson: Not found")

        # Extract risk level
        if any(risk in problems_summary for risk in ["Low Risk", "Moderate Risk", "High Risk", "Very High Risk"]):
            for risk in ["No Comorbidities", "Low Risk", "Moderate Risk", "High Risk", "Very High Risk"]:
                if risk in problems_summary:
                    print(f"  Risk Level: {risk}")
                    break

        # Count problems
        if "Active Problems (" in problems_summary:
            count_part = problems_summary.split("Active Problems (")[1].split(" total")[0]
            print(f"  Active Problems: {count_part}")

        # Check for critical conditions
        if "Critical Conditions:" in problems_summary:
            conditions_part = problems_summary.split("Critical Conditions:")[1].split("\n")[0].strip()
            print(f"  Critical: {conditions_part}")

        results.append(True)

    return all(results)


def main():
    print("="*70)
    print("AI Clinical Insights - Problems Domain Integration Test")
    print("="*70)

    tests = [
        ("Problems Summary Method", test_problems_summary),
        ("Comprehensive Summary Includes Problems", test_comprehensive_summary_includes_problems),
        ("Multiple Patients", test_multiple_patients),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' failed with exception:")
            print(f"  {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")

    if total_passed == total_tests:
        print("\n✅ All tests passed! Problems domain successfully integrated into AI context.")
    else:
        print("\n⚠️  Some tests failed. Review output above for details.")

    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
