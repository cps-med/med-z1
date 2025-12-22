# Mock User Credentials for med-z1

## Shared Password (All Users)

**Password**: `VaDemo2025!`

## Mock Users

| Email                          | Display Name              | Home Site (Sta3n) | Role       |
|--------------------------------|---------------------------|-------------------|------------|
| clinician.alpha@va.gov         | Dr. Alice Anderson, MD    | 508 (Atlanta)     | Physician  |
| clinician.bravo@va.gov         | Dr. Bob Brown, DO         | 648 (Portland)    | Physician  |
| clinician.charlie@va.gov       | Nurse Carol Chen, RN      | 663 (Seattle)     | Nurse      |
| clinician.delta@va.gov         | Dr. David Davis, MD       | 509 (Augusta)     | Physician  |
| clinician.echo@va.gov          | Pharmacist Emma Evans, PharmD | 531 (Boise)   | Pharmacist |
| clinician.foxtrot@va.gov       | Dr. Frank Foster, MD      | 516 (Bay Pines)   | Physician  |
| clinician.golf@va.gov          | Dr. Grace Green, MD       | 552 (Dayton)      | Physician  |

## Quick Login Credentials

Copy-paste for testing:
- **Email**: `clinician.alpha@va.gov`
- **Password**: `VaDemo2025!`

## Password Hash (bcrypt, 12 rounds)

The bcrypt hash for `VaDemo2025!` (used in SQL INSERT scripts):
```
$2b$12$82AjMBnKPIr1y39YN0PiBe50XhmZ3AOJiYZKYnDBpF/TnEYxkeqRG
```

## Changing the Shared Password

If you need to change the shared password:

1. Update this file with the new password
2. Run: `python scripts/generate_password_hash.py --generate-sql`
3. Update `db/seeds/auth_users.sql` with new hashes
4. Reload the `auth.users` table:
   ```bash
   docker exec -i postgres16 psql -U postgres -d medz1 < db/seeds/auth_users.sql
   ```

## Security Note

⚠️ **Development Only**: This shared password approach is for local development only.
Production systems must use unique, strong passwords per user and secure credential management.

## User Details

### User 1: Dr. Alice Anderson
- **Email**: `clinician.alpha@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Dr. Alice Anderson, MD
- **Role**: Physician
- **Home Site**: Atlanta VAMC (Sta3n 508)
- **Profile**: Primary care physician, VistA site

### User 2: Dr. Bob Brown
- **Email**: `clinician.bravo@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Dr. Bob Brown, DO
- **Role**: Physician
- **Home Site**: Portland VAMC (Sta3n 648)
- **Profile**: Cardiologist, Cerner site

### User 3: Nurse Carol Chen
- **Email**: `clinician.charlie@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Nurse Carol Chen, RN
- **Role**: Registered Nurse
- **Home Site**: Seattle/Puget Sound VA (Sta3n 663)
- **Profile**: Critical care nurse, Cerner site

### User 4: Dr. David Davis
- **Email**: `clinician.delta@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Dr. David Davis, MD
- **Role**: Physician
- **Home Site**: Augusta VAMC (Sta3n 509)
- **Profile**: Emergency medicine, VistA site

### User 5: Pharmacist Emma Evans
- **Email**: `clinician.echo@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Pharmacist Emma Evans, PharmD
- **Role**: Pharmacist
- **Home Site**: Boise VAMC (Sta3n 531)
- **Profile**: Clinical pharmacist, Cerner site

### User 6: Dr. Frank Foster
- **Email**: `clinician.foxtrot@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Dr. Frank Foster, MD
- **Role**: Physician
- **Home Site**: C.W. Bill Young VAMC (Sta3n 516, Bay Pines, FL)
- **Profile**: Internal medicine, Cerner site

### User 7: Dr. Grace Green
- **Email**: `clinician.golf@va.gov`
- **Password**: `VaDemo2025!`
- **Display Name**: Dr. Grace Green, MD
- **Role**: Physician
- **Home Site**: Dayton VAMC (Sta3n 552)
- **Profile**: Family medicine, VistA site
