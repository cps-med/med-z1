#!/usr/bin/env python3
"""
Test Problems Vista RPC Integration and Merge/Dedupe Logic

Tests:
1. Parse Vista ORQQPL LIST responses
2. Create canonical problem keys
3. Merge PostgreSQL + Vista data with deduplication
4. Verify Vista is preferred for duplicates
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.realtime_overlay import (
    parse_vista_problems,
    create_canonical_problem_key,
    merge_problems_data
)


def test_parse_vista_problems():
    """Test parsing Vista ORQQPL LIST response"""
    print("\n=== Test 1: Parse Vista Problems ===")

    # Sample Vista response (site 200)
    vista_response = """200-123^Congestive heart failure^I50.23^Active^3180209^1^42343007^0
200-456^Acute exacerbation of COPD^J44.1^Active^3260207^1^195951007^1
200-789^Type 2 diabetes mellitus with CKD^E11.22^Active^3100209^1^44054006^0"""

    problems = parse_vista_problems(vista_response, "200")

    print(f"Parsed {len(problems)} problems from Vista site 200")
    assert len(problems) == 3, f"Expected 3 problems, got {len(problems)}"

    # Check first problem
    p1 = problems[0]
    assert p1["problem_text"] == "Congestive heart failure"
    assert p1["icd10_code"] == "I50.23"
    assert p1["problem_status"] == "Active"
    assert p1["service_connected"] == True
    assert p1["updated_today"] == False
    assert p1["source_site"] == "200"
    assert p1["is_realtime"] == True
    print(f"✓ Problem 1: {p1['problem_text']} ({p1['icd10_code']})")

    # Check second problem (updated today)
    p2 = problems[1]
    assert p2["updated_today"] == True, "Expected updated_today=True for COPD"
    print(f"✓ Problem 2: {p2['problem_text']} - UPDATED TODAY")

    # Check third problem
    p3 = problems[2]
    assert p3["service_connected"] == True
    print(f"✓ Problem 3: {p3['problem_text']} ({p3['icd10_code']})")

    print("✅ Parse Vista problems test PASSED")
    return problems


def test_canonical_keys():
    """Test canonical problem key generation"""
    print("\n=== Test 2: Canonical Problem Keys ===")

    # Problem from Vista site 200
    vista_problem = {
        "icd10_code": "I50.23",
        "onset_date": "2018-02-09",
        "source_site": "200"
    }

    # Same problem from PostgreSQL (should generate same key minus site)
    pg_problem = {
        "icd10_code": "I50.23",
        "onset_date": "2018-02-09",
        "data_source": "VistA Site 200"
    }

    vista_key = create_canonical_problem_key(vista_problem)
    pg_key = create_canonical_problem_key(pg_problem)

    print(f"Vista key: {vista_key}")
    print(f"PG key: {pg_key}")

    # Keys should be same (both resolve to site 200)
    assert vista_key == pg_key, f"Expected matching keys, got {vista_key} vs {pg_key}"
    print("✅ Canonical key test PASSED")

    return vista_key


def test_merge_dedupe():
    """Test merge with deduplication (Vista preferred)"""
    print("\n=== Test 3: Merge with Deduplication ===")

    # PostgreSQL data (historical, T-1 and earlier)
    pg_problems = [
        {
            "problem_text": "Congestive heart failure",
            "icd10_code": "I50.23",
            "onset_date": "2018-02-09",
            "problem_status": "Active",
            "data_source": "VistA Site 200",
            "service_connected": True,
        },
        {
            "problem_text": "Type 2 diabetes mellitus with CKD",
            "icd10_code": "E11.22",
            "onset_date": "2010-02-09",
            "problem_status": "Active",
            "data_source": "VistA Site 200",
            "service_connected": True,
        },
        {
            "problem_text": "PTSD",  # NOT in Vista (old problem)
            "icd10_code": "F43.10",
            "onset_date": "2012-05-10",
            "problem_status": "Active",
            "data_source": "VistA Site 508",
            "service_connected": True,
        }
    ]

    # Vista responses (real-time, T-0)
    vista_responses = {
        "200": """200-123^Congestive heart failure^I50.23^Active^3180209^1^42343007^0
200-456^Acute exacerbation of COPD^J44.1^Active^3260207^1^195951007^1
200-789^Type 2 diabetes mellitus with CKD^E11.22^Active^3100209^1^44054006^0""",
        "500": """500-890^Gastroesophageal reflux disease^K21.9^Active^3260207^0^235595009^1"""
    }

    # Merge
    merged, stats = merge_problems_data(pg_problems, vista_responses, "ICN100001")

    print(f"\nMerge Statistics:")
    print(f"  PG count: {stats['pg_count']}")
    print(f"  Vista count: {stats['vista_count']}")
    print(f"  Vista sites: {stats['vista_sites']}")
    print(f"  Duplicates removed: {stats['duplicates_removed']}")
    print(f"  Total merged: {stats['total_merged']}")

    # Assertions
    assert stats["pg_count"] == 3, f"Expected 3 PG problems, got {stats['pg_count']}"
    assert stats["vista_count"] == 4, f"Expected 4 Vista problems, got {stats['vista_count']}"
    assert stats["duplicates_removed"] == 2, f"Expected 2 duplicates, got {stats['duplicates_removed']}"
    assert stats["total_merged"] == 5, f"Expected 5 merged problems, got {stats['total_merged']}"

    # Verify Vista preferred for duplicates
    chf_problem = [p for p in merged if p["icd10_code"] == "I50.23"][0]
    assert chf_problem.get("source") == "vista", "Expected Vista version of CHF problem to be preferred"
    assert chf_problem.get("is_realtime") == True, "Expected realtime flag for Vista problem"
    print(f"\n✓ CHF duplicate resolved: Vista version preferred (source={chf_problem.get('source')})")

    # Verify unique problems included
    ptsd_problems = [p for p in merged if p["icd10_code"] == "F43.10"]
    assert len(ptsd_problems) == 1, f"Expected 1 PTSD problem, got {len(ptsd_problems)}"
    assert ptsd_problems[0].get("source") == "postgresql", "Expected PG source for unique PTSD problem"
    print(f"✓ Unique PG problem included: PTSD (source=postgresql)")

    # Verify new Vista-only problems included
    copd_problems = [p for p in merged if p["icd10_code"] == "J44.1"]
    assert len(copd_problems) == 1, f"Expected 1 COPD problem, got {len(copd_problems)}"
    assert copd_problems[0].get("updated_today") == True, "Expected updated_today flag for COPD"
    print(f"✓ New Vista problem included: COPD exacerbation (updated_today=True)")

    gerd_problems = [p for p in merged if p["icd10_code"] == "K21.9"]
    assert len(gerd_problems) == 1, f"Expected 1 GERD problem, got {len(gerd_problems)}"
    assert gerd_problems[0].get("source_site") == "500", "Expected site 500 for GERD"
    print(f"✓ Multi-site Vista problem included: GERD from site 500")

    print("\n✅ Merge/dedupe test PASSED")
    return merged, stats


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Problems Vista RPC Integration")
    print("=" * 60)

    try:
        # Test 1: Parse Vista problems
        vista_problems = test_parse_vista_problems()

        # Test 2: Canonical keys
        canonical_key = test_canonical_keys()

        # Test 3: Merge with deduplication
        merged_problems, stats = test_merge_dedupe()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print(f"\nPhase 3 (VistA RPC Integration) is COMPLETE!")
        print(f"  - ORQQPL LIST handler implemented")
        print(f"  - Mock data for 3 sites (200, 500, 630)")
        print(f"  - Parse/merge/dedupe logic working")
        print(f"  - {len(merged_problems)} problems merged from {len(stats['vista_sites'])} Vista sites")

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
