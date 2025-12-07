# ---------------------------------------------------------------------
# test_vault_manual.py
# ---------------------------------------------------------------------
# Manual test script for the CCOW ContextVault.
#
# This script creates a local ContextVault instance and interacts
# with it directly via Python method calls (set_context, get_current,
# clear_context, get_history). Does NOT use the HTTP REST API or
# FastAPI web service layer - purely in-process testing for quick
# verification of core vault functionality.
# ---------------------------------------------------------------------

import time
from ccow.vault import ContextVault
from config import CCOW_ENABLED, CCOW_URL, CCOW_VAULT_PORT, PROJECT_ROOT

# Define a few ANSI Color Escape codes
YELLOW = "\033[33m"
RESET = "\033[0m"

# Verify environment variables
print()
print(f"CCOW Configuration:")
print(f"  Enabled: {CCOW_ENABLED}")
print(f"  URL: {CCOW_URL}")
print(f"  Port: {CCOW_VAULT_PORT}")
print(f"  Project root: {PROJECT_ROOT}")

# Create a vault
vault = ContextVault(max_history=5)

# Print output header
print(f"\n{'=' * 40}")
print("\t CCOW Vault Manual Test")
print(f"{'=' * 40}\n")

# Test 1: Initially empty
print("Test 1: Initially empty")
print(f"{YELLOW}{vault.get_current()}{RESET}")
print()

# Test 2: Set a patient
print("Test 2: Set patient")
context = vault.set_context(patient_id="P123", set_by="test-app")
print(f"{YELLOW}Set: {context.patient_id} by {context.set_by} at {context.set_at.strftime('%Y-%m-%d %H:%M:%S UTC')}{RESET}")
print(f"{YELLOW}Current: {vault.get_current().patient_id}{RESET}")
print()

print("Pausing for 3 seconds...\n")
time.sleep(3)

# Test 3: Change patient
print("Test 3: Change patient")
vault.set_context(patient_id="P456", set_by="test-app")
print(f"{YELLOW}Current: {vault.get_current().patient_id}{RESET}")
print()

# Test 4: View history
print("Test 4: History")
history = vault.get_history()
print(f"{YELLOW}History entries: {len(history)}{RESET}")
for entry in history:
    print(f"{YELLOW}  - {entry.action}: {entry.patient_id} by {entry.actor} at {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}{RESET}")
print()

print("Pausing for 2 seconds...\n")
time.sleep(2)

# Test 5: Clear context
print("Test 5: Clear")
cleared = vault.clear_context(cleared_by="test-app")
print(f"{YELLOW}Cleared: {cleared}{RESET}")
print(f"{YELLOW}Current: {vault.get_current()}{RESET}")
print()

# Test 6: History after clear
print("Test 6: History after clear")
history = vault.get_history()
for entry in history:
    print(f"{YELLOW}  - {entry.action}: {entry.patient_id} by {entry.actor} at {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}{RESET}")
print()