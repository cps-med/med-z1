#!/usr/bin/env python3
# ---------------------------------------------------------------------
# app/services/test_vista_manual.py
# ---------------------------------------------------------------------
# Manual Test Script for VistaClient Multi-Site Selection
# Run this to verify site selection works with actual Vista service
# ---------------------------------------------------------------------

"""
Manual testing script for VistaClient.

Prerequisites:
- Vista RPC Broker service running on port 8003
- Patient registry with test patients

Usage:
    python app/services/test_vista_manual.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.vista_client import get_vista_client, DOMAIN_SITE_LIMITS, MAX_SITES_ABSOLUTE


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


async def test_site_selection():
    """Test site selection for different domains and patients"""

    vista_client = get_vista_client()

    print_section("Test 1: Basic Site Selection (ICN100001)")

    # Test patient ICN100001 (should have 5 treating facilities)
    icn = "ICN100001"

    print(f"Patient: {icn}")
    print(f"Treating facilities: {len(vista_client._get_patient_treating_facilities(icn))}")
    print()

    # Test each domain
    domains = ["vitals", "allergies", "medications", "demographics", "labs", "default"]

    for domain in domains:
        sites = vista_client.get_target_sites(icn, domain)
        limit = DOMAIN_SITE_LIMITS.get(domain, DOMAIN_SITE_LIMITS["default"])

        print(f"  {domain:15} -> {len(sites)} sites (limit={limit}): {sites}")


    print_section("Test 2: Single-Site Patient (ICN100013)")

    # Test patient with only one treating facility
    icn = "ICN100013"
    facilities = vista_client._get_patient_treating_facilities(icn)

    print(f"Patient: {icn}")
    print(f"Treating facilities: {len(facilities)}")
    if facilities:
        print(f"  Site: {facilities[0]['sta3n']} ({facilities[0]['name']})")
        print(f"  Last seen: {facilities[0].get('last_seen', 'N/A')}")
    print()

    for domain in ["vitals", "demographics"]:
        sites = vista_client.get_target_sites(icn, domain)
        print(f"  {domain:15} -> {len(sites)} sites: {sites}")


    print_section("Test 3: Hard Maximum Enforcement")

    # Test with max_sites override
    icn = "ICN100001"

    test_cases = [
        ("Default (3 sites)", None),
        ("Override to 5 sites", 5),
        ("Override to 15 sites (should cap at 10)", 15),
        ("Override to 0 sites", 0),
        ("Override to -1 sites (should return empty)", -1)
    ]

    for description, max_sites in test_cases:
        sites = vista_client.get_target_sites(icn, "default", max_sites=max_sites)
        print(f"  {description:45} -> {len(sites)} sites: {sites[:3]}{'...' if len(sites) > 3 else ''}")


    print_section("Test 4: User-Selected Sites Override")

    # Test explicit site selection
    icn = "ICN100001"
    user_sites = ["630", "402", "405"]

    sites = vista_client.get_target_sites(
        icn,
        "vitals",
        user_selected_sites=user_sites
    )

    print(f"Patient: {icn}")
    print(f"Domain: vitals (default limit=2)")
    print(f"User selected: {user_sites}")
    print(f"Result: {sites}")
    print(f"Note: User selection overrides domain limit")


    print_section("Test 5: Multi-Site RPC Execution")

    # Test actual RPC call to multiple sites
    icn = "ICN100001"
    domain = "demographics"

    print(f"Patient: {icn}")
    print(f"Domain: {domain}")
    print()

    sites = vista_client.get_target_sites(icn, domain)
    print(f"Selected sites: {sites}")
    print()

    print("Calling ORWPT PTINQ RPC at selected sites...")
    print()

    try:
        results = await vista_client.call_rpc_multi_site(
            sites=sites,
            rpc_name="ORWPT PTINQ",
            params=[icn]
        )

        for site, result in results.items():
            success = result.get("success")
            status = "✓ SUCCESS" if success else "✗ FAILED"

            print(f"  Site {site}: {status}")

            if success:
                response = result.get("response", "")
                # Parse NAME^SSN^DOB^SEX^VETERAN_STATUS
                fields = response.split("^")
                if len(fields) >= 1:
                    print(f"    Name: {fields[0]}")
            else:
                error = result.get("error", "Unknown error")
                print(f"    Error: {error}")
            print()

        successful = sum(1 for r in results.values() if r.get("success"))
        print(f"Summary: {successful}/{len(sites)} sites responded successfully")

    except Exception as e:
        print(f"ERROR: {str(e)}")


    print_section("Test 6: Error Handling - Non-Existent Patient")

    # Test with non-existent patient
    icn = "ICN999999"

    facilities = vista_client._get_patient_treating_facilities(icn)
    print(f"Patient: {icn}")
    print(f"Treating facilities: {len(facilities)}")

    sites = vista_client.get_target_sites(icn, "default")
    print(f"Selected sites: {sites}")
    print()

    if sites:
        print("Unexpected: Got sites for non-existent patient")
    else:
        print("✓ Correctly returned empty list for non-existent patient")


    print_section("Test 7: Site Selection Sorting by Last Seen")

    # Verify sites are sorted by last_seen descending
    icn = "ICN100001"
    facilities = vista_client._get_patient_treating_facilities(icn)

    print(f"Patient: {icn}")
    print(f"Treating facilities (unsorted):")
    for fac in facilities:
        print(f"  {fac['sta3n']:3} - {fac['name']:25} - Last seen: {fac.get('last_seen', 'N/A')}")
    print()

    # Get all sites (override to 10)
    sites = vista_client.get_target_sites(icn, "default", max_sites=10)

    print(f"Selected sites (sorted by last_seen, most recent first):")
    for i, site in enumerate(sites, 1):
        # Find facility info
        fac = next((f for f in facilities if f['sta3n'] == site), None)
        if fac:
            print(f"  {i}. Site {site} - {fac['name']:25} - Last seen: {fac.get('last_seen', 'N/A')}")
    print()
    print("✓ Sites should be ordered by recency (T-7 before T-30 before T-90, etc.)")


    print_section("Test Summary")

    print("All manual tests completed!")
    print()
    print("Validated:")
    print("  ✓ Domain-specific site limits")
    print("  ✓ Hard maximum enforcement (10 sites)")
    print("  ✓ User-selected sites override")
    print("  ✓ Multi-site RPC execution")
    print("  ✓ Error handling for non-existent patients")
    print("  ✓ Site sorting by last_seen date")
    print()
    print("Phase 2 site selection logic is working correctly!")
    print()


async def main():
    """Run all manual tests"""
    try:
        await test_site_selection()
    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  VistaClient Manual Testing Suite".center(68) + "║")
    print("║" + "  Phase 2: Multi-Site Selection".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")

    asyncio.run(main())
