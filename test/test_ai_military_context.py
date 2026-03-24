"""
Test AI integration with military history data.
Tests that PatientContextBuilder includes environmental exposures.
"""

from ai.services.patient_context import PatientContextBuilder

# Test patients with different exposure profiles
test_patients = [
    ("ICN100001", "Adam Dooree - Agent Orange exposure"),
    ("ICN100007", "Adam Amajor - Former POW"),
    ("ICN100010", "Alexander Aminor - Gulf War veteran + Radiation"),
    ("ICN100002", "Barry Miifaa - Gulf War veteran"),
    ("ICN100003", "Carol Soola - Not service connected"),
    ("ICN100028", "Robert J Anderson (DECEASED) - Camp Lejeune"),
]

print("=" * 80)
print("AI Military History Context Test")
print("=" * 80)

for icn, description in test_patients:
    print(f"\n{'=' * 80}")
    print(f"Patient: {description}")
    print(f"ICN: {icn}")
    print(f"{'=' * 80}\n")

    builder = PatientContextBuilder(icn)
    demographics = builder.get_demographics_summary()

    print(demographics)
    print()

    # Verify exposure mentions
    checks = []
    if "Agent Orange" in demographics:
        checks.append("✅ Agent Orange exposure detected in context")
    if "Former POW" in demographics:
        checks.append("✅ POW status detected in context")
    if "Gulf War" in demographics:
        checks.append("✅ Gulf War exposure detected in context")
    if "Camp Lejeune" in demographics:
        checks.append("✅ Camp Lejeune exposure detected in context")
    if "high priority care" in demographics:
        checks.append("✅ High priority care indicator detected")
    if "ionizing radiation" in demographics:
        checks.append("✅ Radiation exposure detected in context")

    if checks:
        for check in checks:
            print(check)
    else:
        print("ℹ️  No military exposures found (expected for non-SC patients)")

print("\n" + "=" * 80)
print("Test complete")
print("=" * 80)
