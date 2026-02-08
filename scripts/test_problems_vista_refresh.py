#!/usr/bin/env python3
"""
Test Problems VistA Refresh Endpoint

Tests the real-time VistA refresh endpoint for the problems domain.
Verifies that PostgreSQL and VistA data are properly merged.

Usage:
  # Terminal 1: Start all services
  uvicorn app.main:app --reload  # Port 8000
  uvicorn vista.app.main:app --reload --port 8003  # Port 8003

  # Terminal 2: Run this test
  python scripts/test_problems_vista_refresh.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.patient_problems import get_patient_problems
from app.services.vista_client import VistaClient
from app.services.realtime_overlay import merge_problems_data


async def test_vista_refresh():
    """Test VistA refresh for problems."""
    print("=" * 60)
    print("Testing Problems VistA Refresh Endpoint")
    print("=" * 60)

    icn = "ICN100001"

    print(f"\n1. Getting PostgreSQL problems for {icn}...")
    pg_problems = get_patient_problems(icn)
    print(f"   ✅ Found {len(pg_problems)} problems in PostgreSQL")

    print(f"\n2. Querying VistA sites for {icn}...")
    vista_client = VistaClient()

    # Get target sites for problems domain
    target_sites = vista_client.get_target_sites(icn, domain="problems")
    print(f"   Target sites: {target_sites}")

    # Call ORQQPL LIST RPC at all target sites
    vista_results_raw = await vista_client.call_rpc_multi_site(
        sites=target_sites,
        rpc_name="ORQQPL LIST",
        params=[icn]
    )

    # Extract successful responses
    vista_results = {}
    for site, response in vista_results_raw.items():
        if response.get("success"):
            vista_results[site] = response.get("response", "")
            print(f"   ✅ Site {site}: Success")
        else:
            print(f"   ❌ Site {site}: {response.get('error')}")

    print(f"\n3. Merging PostgreSQL + VistA data...")
    problems, merge_stats = merge_problems_data(pg_problems, vista_results, icn)

    print(f"\n4. Merge Statistics:")
    print(f"   PostgreSQL count: {merge_stats['pg_count']}")
    print(f"   VistA count: {merge_stats['vista_count']}")
    print(f"   VistA sites: {merge_stats['vista_sites']}")
    print(f"   Duplicates removed: {merge_stats['duplicates_removed']}")
    print(f"   Total merged: {merge_stats['total_merged']}")

    # Verify merge
    assert merge_stats['pg_count'] == len(pg_problems), "PG count mismatch"
    assert merge_stats['vista_count'] > 0, "No VistA problems found"
    assert merge_stats['total_merged'] == len(problems), "Merged count mismatch"

    # Check for VistA-sourced problems
    vista_sourced = [p for p in problems if p.get('source') == 'vista']
    print(f"\n5. VistA-sourced problems: {len(vista_sourced)}")

    if vista_sourced:
        print(f"\n   Example VistA problem:")
        p = vista_sourced[0]
        print(f"   - {p['problem_text']}")
        print(f"   - ICD-10: {p['icd10_code']}")
        print(f"   - Status: {p['problem_status']}")
        print(f"   - Source: {p.get('source')} (site {p.get('source_site')})")
        if p.get('is_realtime'):
            print(f"   - ✨ Real-time data (T-0)")

    print("\n" + "=" * 60)
    print("✅ VistA Refresh Test PASSED")
    print("=" * 60)
    print(f"\nProblems domain VistA integration is working!")
    print(f"  - {merge_stats['pg_count']} historical problems (PostgreSQL)")
    print(f"  - {merge_stats['vista_count']} real-time problems (VistA)")
    print(f"  - {merge_stats['duplicates_removed']} duplicates removed")
    print(f"  - {merge_stats['total_merged']} total problems available")

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_vista_refresh())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
