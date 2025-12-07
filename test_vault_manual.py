# -----------------------------------------------------------
# test_vault_manual.py
# -----------------------------------------------------------

from ccow.vault import ContextVault

# Create a vault
vault = ContextVault(max_history=5)

# Test 1: Initially empty
print("Test 1: Initially empty")
print(vault.get_current())  # None
print()

# Test 2: Set a patient
print("Test 2: Set patient")
context = vault.set_context(patient_id="P123", set_by="test-app")
print(f"Set: {context.patient_id} by {context.set_by}")
print(f"Current: {vault.get_current().patient_id}")
print()

# Test 3: Change patient
print("Test 3: Change patient")
vault.set_context(patient_id="P456", set_by="test-app")
print(f"Current: {vault.get_current().patient_id}")
print()

# Test 4: View history
print("Test 4: History")
history = vault.get_history()
print(f"History entries: {len(history)}")
for entry in history:
    print(f"  - {entry.action}: {entry.patient_id} by {entry.actor}")
print()

# Test 5: Clear context
print("Test 5: Clear")
cleared = vault.clear_context(cleared_by="test-app")
print(f"Cleared: {cleared}")
print(f"Current: {vault.get_current()}")
print()

# Test 6: History after clear
print("Test 6: History after clear")
history = vault.get_history()
for entry in history:
    print(f"  - {entry.action}: {entry.patient_id} by {entry.actor}")