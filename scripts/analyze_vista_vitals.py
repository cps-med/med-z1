#!/usr/bin/env python3
"""
Analyze Vista RPC Broker Vitals Data
Shows which patients have vitals data and how to test them

Usage:
    python scripts/analyze_vista_vitals.py
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def load_patient_registry():
    """Load patient registry to get ICN → DFN mappings"""
    registry_path = project_root / "mock" / "shared" / "patient_registry.json"
    with open(registry_path, 'r') as f:
        return json.load(f)


def load_vista_vitals(site_sta3n):
    """Load vitals data for a specific site"""
    vitals_path = project_root / "vista" / "app" / "data" / "sites" / site_sta3n / "vitals.json"

    if not vitals_path.exists():
        return None

    with open(vitals_path, 'r') as f:
        return json.load(f)


def analyze_vitals():
    """Analyze all Vista vitals data and show patient mappings"""

    print("=" * 80)
    print("VISTA RPC BROKER - VITALS DATA ANALYSIS")
    print("=" * 80)
    print()

    # Load patient registry
    registry = load_patient_registry()

    # Build DFN → ICN reverse lookup for each site
    dfn_to_icn = {}
    for patient in registry["patients"]:
        icn = patient["icn"]
        for facility in patient["treating_facilities"]:
            sta3n = facility["sta3n"]
            dfn = facility["dfn"]

            if sta3n not in dfn_to_icn:
                dfn_to_icn[sta3n] = {}

            dfn_to_icn[sta3n][dfn] = {
                "icn": icn,
                "name": f"{patient['name_last']}, {patient['name_first']}",
                "ssn": patient["ssn"],
                "dob": patient["dob"]
            }

    # Analyze vitals at each site
    sites = ["200", "500", "630"]
    patient_vitals_summary = defaultdict(lambda: {"sites": [], "total_vitals": 0, "vitals_by_site": {}})

    for site_sta3n in sites:
        vitals_data = load_vista_vitals(site_sta3n)

        if not vitals_data:
            print(f"⚠️  Site {site_sta3n}: No vitals data file found")
            continue

        site_name = vitals_data.get("site_name", "Unknown")
        vitals = vitals_data.get("vitals", [])

        # Count vitals per DFN
        vitals_by_dfn = defaultdict(list)
        for vital in vitals:
            dfn = vital["dfn"]
            vitals_by_dfn[dfn].append(vital)

        print(f"📍 Site {site_sta3n} ({site_name})")
        print(f"   {'─' * 76}")

        for dfn, patient_vitals in sorted(vitals_by_dfn.items()):
            if dfn in dfn_to_icn.get(site_sta3n, {}):
                patient_info = dfn_to_icn[site_sta3n][dfn]
                icn = patient_info["icn"]
                name = patient_info["name"]

                # Track by ICN for summary
                patient_vitals_summary[icn]["sites"].append(site_sta3n)
                patient_vitals_summary[icn]["total_vitals"] += len(patient_vitals)
                patient_vitals_summary[icn]["vitals_by_site"][site_sta3n] = len(patient_vitals)
                patient_vitals_summary[icn]["name"] = name
                patient_vitals_summary[icn]["ssn"] = patient_info["ssn"]

                # Show vitals types
                vital_types = defaultdict(int)
                for v in patient_vitals:
                    vital_types[v["type"]] += 1

                vitals_summary = ", ".join([f"{vtype} ({count})" for vtype, count in sorted(vital_types.items())])

                print(f"   DFN {dfn} → {icn} ({name})")
                print(f"     ✅ {len(patient_vitals)} vitals: {vitals_summary}")
            else:
                print(f"   DFN {dfn} → ❌ NOT IN REGISTRY (orphaned data)")

        print()

    # Summary by patient (ICN)
    print("=" * 80)
    print("PATIENT SUMMARY (By ICN)")
    print("=" * 80)
    print()

    for icn, summary in sorted(patient_vitals_summary.items()):
        print(f"🧑 {icn} - {summary['name']}")
        print(f"   SSN: {summary['ssn']}")
        print(f"   Total Vitals: {summary['total_vitals']}")
        print(f"   Sites with Vitals: {', '.join(sorted(summary['sites']))}")

        for site, count in sorted(summary['vitals_by_site'].items()):
            print(f"     - Site {site}: {count} vitals")

        print()

    # Testing guide
    print("=" * 80)
    print("TESTING GUIDE")
    print("=" * 80)
    print()
    print("To test Vista RPC Broker vitals retrieval, use these curl commands:")
    print()

    for icn, summary in sorted(patient_vitals_summary.items()):
        print(f"# Test {icn} ({summary['name']})")

        for site in sorted(summary['sites']):
            count = summary['vitals_by_site'][site]
            print(f"curl -X POST 'http://localhost:8003/rpc/execute?site={site}' \\")
            print(f"  -H 'Content-Type: application/json' \\")
            print(f"  -d '{{\"name\": \"GMV LATEST VM\", \"params\": [\"{icn}\"]}}' | jq")
            print(f"# Expected: {count} vitals in VistA format")
            print()

    print("=" * 80)
    print("PYTHON TESTING EXAMPLE")
    print("=" * 80)
    print()
    print("""
import requests

# Test ICN100001 at site 200
response = requests.post(
    'http://localhost:8003/rpc/execute?site=200',
    json={
        'name': 'GMV LATEST VM',
        'params': ['ICN100001']
    }
)

if response.json()['success']:
    vitals_data = response.json()['response']
    print("VistA Vitals Response:")
    print(vitals_data)
else:
    print("Error:", response.json()['error'])
""")


if __name__ == "__main__":
    analyze_vitals()
