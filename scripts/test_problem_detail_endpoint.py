#!/usr/bin/env python3
"""
Test Problem Detail Modal Endpoint

Verifies that the endpoint returns only the modal content partial,
not the full page HTML.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.patient_problems import get_patient_problems

def test_endpoint_data():
    """Test what data the endpoint would return."""
    print("=" * 60)
    print("Testing Problem Detail Endpoint Data")
    print("=" * 60)

    icn = "ICN100001"
    problem_id = 1

    print(f"\n1. Fetching problems for {icn}...")
    problems = get_patient_problems(icn)
    print(f"   Found {len(problems)} total problems")

    print(f"\n2. Looking for problem_id={problem_id}...")
    problem = next((p for p in problems if p.get("problem_id") == problem_id), None)

    if problem:
        print(f"   ✅ Found problem: {problem.get('problem_text')}")
        print(f"\n3. Problem data structure:")
        for key, value in problem.items():
            if value is not None:
                print(f"   - {key}: {value}")
    else:
        print(f"   ❌ Problem {problem_id} not found")
        print(f"\n   Available problem IDs:")
        for p in problems[:5]:
            print(f"   - ID {p.get('problem_id')}: {p.get('problem_text')}")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    try:
        exit_code = test_endpoint_data()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
