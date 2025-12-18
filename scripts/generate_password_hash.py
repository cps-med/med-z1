#!/usr/bin/env python3
"""
Generate bcrypt password hashes for mock users.

Usage:
    # Generate single password hash interactively
    python scripts/generate_password_hash.py

    # Generate SQL INSERT statements for all mock users
    python scripts/generate_password_hash.py --generate-sql

    # Non-interactive mode (provide password via command line)
    python scripts/generate_password_hash.py --password "VaDemo2025!"
"""

import bcrypt
import sys
import argparse
from pathlib import Path

# Import bcrypt rounds from project config
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from config import BCRYPT_ROUNDS

# Mock user data (matches docs/mock-users.md)
MOCK_USERS = [
    {
        "email": "clinician.alpha@va.gov",
        "display_name": "Dr. Alice Anderson, MD",
        "first_name": "Alice",
        "last_name": "Anderson",
        "home_site_sta3n": 508,  # Atlanta VAMC
    },
    {
        "email": "clinician.bravo@va.gov",
        "display_name": "Dr. Bob Brown, DO",
        "first_name": "Bob",
        "last_name": "Brown",
        "home_site_sta3n": 648,  # Portland VAMC
    },
    {
        "email": "clinician.charlie@va.gov",
        "display_name": "Nurse Carol Chen, RN",
        "first_name": "Carol",
        "last_name": "Chen",
        "home_site_sta3n": 663,  # Seattle/Puget Sound VA
    },
    {
        "email": "clinician.delta@va.gov",
        "display_name": "Dr. David Davis, MD",
        "first_name": "David",
        "last_name": "Davis",
        "home_site_sta3n": 509,  # Augusta VAMC
    },
    {
        "email": "clinician.echo@va.gov",
        "display_name": "Pharmacist Emma Evans, PharmD",
        "first_name": "Emma",
        "last_name": "Evans",
        "home_site_sta3n": 531,  # Boise VAMC
    },
    {
        "email": "clinician.foxtrot@va.gov",
        "display_name": "Dr. Frank Foster, MD",
        "first_name": "Frank",
        "last_name": "Foster",
        "home_site_sta3n": 516,  # C.W. Bill Young VAMC (Bay Pines, FL)
    },
    {
        "email": "clinician.golf@va.gov",
        "display_name": "Dr. Grace Green, MD",
        "first_name": "Grace",
        "last_name": "Green",
        "home_site_sta3n": 552,  # Dayton VAMC
    },
]


def hash_password(password: str) -> str:
    """Generate bcrypt hash for a password using configured rounds."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def generate_sql_inserts(password: str) -> None:
    """Generate SQL INSERT statements for all mock users with hashed password."""
    password_hash = hash_password(password)

    print("-- =====================================================")
    print("-- Mock User Data for med-z1 Authentication")
    print("-- =====================================================")
    print(f"-- Password for all users: {password}")
    print(f"-- Bcrypt rounds: {BCRYPT_ROUNDS}")
    print(f"-- Generated hash: {password_hash}")
    print("--")
    print("-- Usage:")
    print("--   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql")
    print("-- =====================================================")
    print()
    print("-- Clear existing data (development only)")
    print("TRUNCATE TABLE auth.sessions CASCADE;")
    print("TRUNCATE TABLE auth.audit_logs CASCADE;")
    print("DELETE FROM auth.users;")
    print()
    print("-- Insert mock users")
    print("INSERT INTO auth.users (")
    print("    email,")
    print("    password_hash,")
    print("    display_name,")
    print("    first_name,")
    print("    last_name,")
    print("    home_site_sta3n,")
    print("    is_active,")
    print("    created_by")
    print(") VALUES")

    for i, user in enumerate(MOCK_USERS):
        is_last = (i == len(MOCK_USERS) - 1)
        comma = ";" if is_last else ","

        print(f"-- User {i+1}: {user['display_name']}")
        print("(")
        print(f"    '{user['email']}',")
        print(f"    '{password_hash}',  -- {password}")
        print(f"    '{user['display_name']}',")
        print(f"    '{user['first_name']}',")
        print(f"    '{user['last_name']}',")
        print(f"    {user['home_site_sta3n']},")
        print("    TRUE,")
        print("    'mock_data_script'")
        print(f"){comma}")
        if not is_last:
            print()

    print()
    print("-- Verify inserts")
    print("SELECT")
    print("    email,")
    print("    display_name,")
    print("    home_site_sta3n,")
    print("    is_active")
    print("FROM auth.users")
    print("ORDER BY email;")
    print()
    print("-- Print summary")
    print("SELECT 'Inserted ' || COUNT(*) || ' mock users' AS summary")
    print("FROM auth.users;")
    print()
    print("-- =====================================================")
    print("-- Copy the above SQL and save to:")
    print("--   db/seeds/auth_users.sql")
    print("-- =====================================================")


def main():
    parser = argparse.ArgumentParser(
        description='Generate bcrypt password hashes for mock users',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--generate-sql', action='store_true',
                        help='Generate SQL INSERT statements for all mock users')
    parser.add_argument('--password', type=str,
                        help='Password to hash (default: prompt interactively)')

    args = parser.parse_args()

    if args.generate_sql:
        # Bulk SQL generation mode
        if args.password:
            password = args.password
        else:
            password = input("Enter shared password for all mock users [VaDemo2025!]: ").strip()
            if not password:
                password = "VaDemo2025!"

        generate_sql_inserts(password)
    else:
        # Single password hash mode
        if args.password:
            password = args.password
        else:
            password = input("Enter password to hash: ").strip()

        if not password:
            print("Error: Password cannot be empty")
            sys.exit(1)

        hashed = hash_password(password)
        print(f"\nBcrypt rounds: {BCRYPT_ROUNDS}")
        print(f"Hashed password: {hashed}")
        print("\nCopy the hash above and use in your SQL INSERT statement.")


if __name__ == "__main__":
    main()
