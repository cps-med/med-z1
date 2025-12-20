# CCOW v2.0 API Testing Guide

## Overview

CCOW Context Vault v2.0 requires authentication via `session_id` cookie. The `user_id` is **automatically extracted** from the session by the CCOW vault - you never pass it manually.

---

## Authentication Flow

```
Browser/Client          med-z1 App           CCOW Vault          PostgreSQL
     |                       |                     |                   |
     |-- Login ------------->|                     |                   |
     |                       |-- Validate -------->|                   |
     |<-- session_id cookie--|                     |                   |
     |                       |                     |                   |
     |-- Select Patient ---->|                     |                   |
     |   (with cookie)       |                     |                   |
     |                       |-- Set Context ----->|                   |
     |                       |   (forward cookie)  |                   |
     |                       |                     |-- Validate ------->|
     |                       |                     |   session          |
     |                       |                     |<-- user_id --------|
     |                       |                     |                   |
     |                       |                     | Store context:    |
     |                       |                     | {user_id: X,      |
     |                       |                     |  patient_id: Y}   |
     |                       |<-- Success ---------|                   |
     |<-- Dashboard with ----|                     |                   |
     |    patient data       |                     |                   |
```

---

## Testing with curl

### Prerequisites
1. Login to med-z1 app at http://localhost:8000
2. Get your `session_id` from browser DevTools → Cookies
3. Use that session_id in curl commands below

### Example Commands

**1. Health Check (No Auth Required)**
```bash
curl http://localhost:8001/ccow/health
```

**2. Set Active Patient**
```bash
curl -X PUT "http://localhost:8001/ccow/active-patient" \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION_ID_HERE" \
  -d '{
    "patient_id": "ICN100001",
    "set_by": "manual-test"
  }'
```

Expected Response:
```json
{
  "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100001",
  "set_by": "manual-test",
  "set_at": "2025-12-20T19:45:00.123456Z",
  "last_accessed_at": "2025-12-20T19:45:00.123456Z"
}
```

**3. Get Active Patient**
```bash
curl -X GET "http://localhost:8001/ccow/active-patient" \
  -b "session_id=YOUR_SESSION_ID_HERE"
```

Expected Response (if context exists):
```json
{
  "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100001",
  "set_by": "manual-test",
  "set_at": "2025-12-20T19:45:00.123456Z",
  "last_accessed_at": "2025-12-20T19:45:05.789012Z"
}
```

Expected Response (if no context):
```json
{
  "detail": "No active patient context for user"
}
```

**4. Clear Active Patient**
```bash
curl -X DELETE "http://localhost:8001/ccow/active-patient" \
  -H "Content-Type: application/json" \
  -b "session_id=YOUR_SESSION_ID_HERE" \
  -d '{"cleared_by": "manual-test"}'
```

Expected Response: `204 No Content` (empty body)

**5. Get Context History (User Scope)**
```bash
curl -X GET "http://localhost:8001/ccow/history?scope=user" \
  -b "session_id=YOUR_SESSION_ID_HERE"
```

Expected Response:
```json
{
  "history": [
    {
      "action": "set",
      "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
      "email": "clinician.alpha@va.gov",
      "patient_id": "ICN100001",
      "actor": "manual-test",
      "timestamp": "2025-12-20T19:45:00.123456Z"
    }
  ],
  "scope": "user",
  "total_count": 1,
  "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc"
}
```

**6. Get Context History (Global Scope - All Users)**
```bash
curl -X GET "http://localhost:8001/ccow/history?scope=global" \
  -b "session_id=YOUR_SESSION_ID_HERE"
```

**7. Get All Active Contexts (Admin)**
```bash
curl -X GET "http://localhost:8001/ccow/active-patients" \
  -b "session_id=YOUR_SESSION_ID_HERE"
```

Expected Response:
```json
{
  "contexts": [
    {
      "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
      "email": "clinician.alpha@va.gov",
      "patient_id": "ICN100001",
      "set_by": "manual-test",
      "set_at": "2025-12-20T19:45:00.123456Z",
      "last_accessed_at": "2025-12-20T19:45:05.789012Z"
    }
  ],
  "total_count": 1
}
```

**8. Trigger Manual Cleanup (Admin)**
```bash
curl -X POST "http://localhost:8001/ccow/cleanup" \
  -b "session_id=YOUR_SESSION_ID_HERE"
```

Expected Response:
```json
{
  "removed_count": 0,
  "message": "Cleaned up 0 stale contexts"
}
```

---

## Testing with Swagger UI

**Problem:** Swagger UI at http://localhost:8001/docs doesn't automatically send cookies.

**Workaround 1: Use Browser DevTools**

1. Open http://localhost:8001/docs in same browser where you're logged into med-z1
2. Open DevTools (F12) → Console tab
3. Run this to set cookie:
   ```javascript
   document.cookie = "session_id=YOUR_SESSION_ID_HERE; path=/";
   ```
4. Now test endpoints in Swagger UI - they'll include the cookie

**Workaround 2: Use curl (Recommended)**

Swagger UI is not ideal for cookie-based auth. Use curl commands above instead.

**Workaround 3: Use Insomnia (Recommended)**

See detailed setup below in "Testing with Insomnia" section.

Import the pre-configured collection from `docs/insomnia-ccow-collection.json`.

---

## Testing with Insomnia

### Prerequisites

1. Install Insomnia: https://insomnia.rest/download
2. Login to med-z1 at http://localhost:8000
3. Get your session_id from browser cookies

### Quick Start: Import Collection

1. Open Insomnia
2. Click **Create** → **Import**
3. Select **From File**
4. Choose `docs/insomnia-ccow-collection.json`
5. Collection "med-z1 CCOW API" will be imported with 8 pre-configured requests

### Configure Session ID

After importing, you must replace `YOUR_SESSION_ID_HERE` with your actual session ID:

**Option A: Edit Each Request**
1. Click on a request (e.g., "Get Active Patient")
2. Go to **Headers** tab
3. Find the Cookie header: `session_id=YOUR_SESSION_ID_HERE`
4. Replace with your actual session ID
5. Repeat for all 7 authenticated requests

**Option B: Use Environment Variable (Easier)**
1. Click **Environment** dropdown (top left)
2. Select **Base Environment**
3. Update `session_id` value:
   ```json
   {
     "base_url": "http://localhost:8001",
     "session_id": "a2364061-83c2-4aa1-8368-740c3d0ff531"
   }
   ```
4. Click **Done**
5. Update all Cookie headers to use environment variable:
   ```
   Cookie: session_id={{ _.session_id }}
   ```

### Manual Request Setup (Without Import)

If you prefer to create requests manually:

#### Example: GET Active Patient

**Request Configuration:**
- **Method:** GET
- **URL:** `http://localhost:8001/ccow/active-patient`
- **Body:** (leave empty)

**Headers Tab:**
```
Cookie: session_id=a2364061-83c2-4aa1-8368-740c3d0ff531
```

**Click Send** → Expected Response (200 OK):
```json
{
  "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100001",
  "set_by": "med-z1",
  "set_at": "2025-12-20T19:45:00.123456Z",
  "last_accessed_at": "2025-12-20T19:45:05.789012Z"
}
```

#### Example: PUT Set Active Patient

**Request Configuration:**
- **Method:** PUT
- **URL:** `http://localhost:8001/ccow/active-patient`
- **Body Type:** JSON

**Headers Tab:**
```
Cookie: session_id=a2364061-83c2-4aa1-8368-740c3d0ff531
Content-Type: application/json
```

**Body Tab:**
```json
{
  "patient_id": "ICN100002",
  "set_by": "insomnia-test"
}
```

**Click Send** → Expected Response (200 OK):
```json
{
  "user_id": "45fe0c87-5fe7-42b6-a2ee-f20bb5f1bebc",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100002",
  "set_by": "insomnia-test",
  "set_at": "2025-12-20T19:50:00.123456Z",
  "last_accessed_at": "2025-12-20T19:50:00.123456Z"
}
```

### Using Insomnia Cookie Manager

Insomnia has a built-in cookie manager that automatically handles cookies:

1. Click **Cookies** button (top right, near Send)
2. Select domain: **localhost:8001**
3. Click **Add Cookie**
4. Enter cookie string:
   ```
   session_id=a2364061-83c2-4aa1-8368-740c3d0ff531; Path=/; Domain=localhost
   ```
5. Click **Done**

Now all requests to `localhost:8001` will automatically include the cookie (no need to add Cookie header manually).

### Common Errors in Insomnia

**Error: 401 Unauthorized - "Missing session cookie"**

**Cause:** Cookie header not included in request

**Solution:**
- Check Headers tab has: `Cookie: session_id=YOUR_SESSION_ID`
- OR use Cookie Manager to add cookie automatically

---

**Error: 401 Unauthorized - "Invalid or expired session"**

**Cause:** Session ID is wrong, expired, or from different environment

**Solution:**
1. Get fresh session ID from browser (logout/login if needed)
2. Update Cookie header with new session ID
3. Verify session in database:
   ```bash
   python scripts/debug_ccow_session.py <session_id>
   ```

---

**Error: 422 Unprocessable Entity**

**Cause:** Request body missing required fields or wrong format

**Solution:**
- Verify Body Type is set to **JSON** (not Text, Form, etc.)
- Check JSON syntax is valid
- Include required fields: `patient_id` and `set_by`

---

**Error: Request timed out**

**Cause:** CCOW vault service not running

**Solution:**
```bash
# Start CCOW vault
uvicorn ccow.main:app --reload --port 8001
```

### Testing Workflow

**1. Health Check (No Auth Required)**
```
GET http://localhost:8001/ccow/health
(No cookie needed)

Expected: 200 OK
```

**2. Get Active Patient**
```
GET http://localhost:8001/ccow/active-patient
Cookie: session_id=...

Expected: 200 OK (if context exists) or 404 (if no context)
```

**3. Set Active Patient**
```
PUT http://localhost:8001/ccow/active-patient
Cookie: session_id=...
Body: {"patient_id": "ICN100001", "set_by": "insomnia"}

Expected: 200 OK with PatientContext object
```

**4. Verify Context Set**
```
GET http://localhost:8001/ccow/active-patient
Cookie: session_id=...

Expected: 200 OK showing ICN100001
```

**5. Check History**
```
GET http://localhost:8001/ccow/history?scope=user
Cookie: session_id=...

Expected: 200 OK with history array showing set event
```

**6. Clear Context**
```
DELETE http://localhost:8001/ccow/active-patient
Cookie: session_id=...
Body: {"cleared_by": "insomnia"}

Expected: 204 No Content
```

**7. Verify Context Cleared**
```
GET http://localhost:8001/ccow/active-patient
Cookie: session_id=...

Expected: 404 Not Found
```

---

## Testing Multi-User Context Isolation

To test that each user maintains independent context:

**Terminal 1 (User Alpha):**
```bash
# Login as clinician.alpha@va.gov, get session_id from browser
SESSION_ALPHA="your-alpha-session-id"

# Set patient for Alpha
curl -X PUT "http://localhost:8001/ccow/active-patient" \
  -H "Content-Type: application/json" \
  -b "session_id=$SESSION_ALPHA" \
  -d '{"patient_id": "ICN100001", "set_by": "test"}'

# Verify Alpha sees ICN100001
curl -X GET "http://localhost:8001/ccow/active-patient" \
  -b "session_id=$SESSION_ALPHA"
```

**Terminal 2 (User Beta):**
```bash
# Login as clinician.beta@va.gov in different browser/incognito, get session_id
SESSION_BETA="your-beta-session-id"

# Set different patient for Beta
curl -X PUT "http://localhost:8001/ccow/active-patient" \
  -H "Content-Type: application/json" \
  -b "session_id=$SESSION_BETA" \
  -d '{"patient_id": "ICN100002", "set_by": "test"}'

# Verify Beta sees ICN100002
curl -X GET "http://localhost:8001/ccow/active-patient" \
  -b "session_id=$SESSION_BETA"
```

**Back to Terminal 1:**
```bash
# Verify Alpha STILL sees ICN100001 (not ICN100002)
curl -X GET "http://localhost:8001/ccow/active-patient" \
  -b "session_id=$SESSION_ALPHA"
```

**Check Global History:**
```bash
# See both users' context changes
curl -X GET "http://localhost:8001/ccow/history?scope=global" \
  -b "session_id=$SESSION_ALPHA"
```

---

## Error Responses

**401 Unauthorized - Missing Cookie**
```json
{
  "detail": "Missing session cookie"
}
```
**Solution:** Include `-b "session_id=..."` in curl command

**401 Unauthorized - Invalid Session**
```json
{
  "detail": "Invalid or expired session"
}
```
**Solution:**
- Logout and login again to get fresh session
- Session may have expired (default: 15 minutes idle)
- Verify session exists in database

**404 Not Found - No Context**
```json
{
  "detail": "No active patient context for user"
}
```
**Solution:** This is normal if user hasn't selected a patient yet

**422 Unprocessable Entity - Missing Fields**
```json
{
  "detail": [
    {
      "loc": ["body", "patient_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solution:** Include required fields in request body

---

## Key Differences from v1.1

| Aspect | v1.1 | v2.0 |
|--------|------|------|
| Authentication | None | Required (session cookie) |
| User Identification | N/A | Automatic from session |
| Context Scope | Global (single) | Per-user (isolated) |
| Request Body | `{patient_id, set_by}` | Same (no change) |
| Response | `{patient_id, set_by, ...}` | Adds `user_id`, `email` |
| History | Global only | User or global scope |

---

## Common Mistakes

❌ **Don't** try to pass `user_id` in request body
```bash
# WRONG - user_id is not a valid parameter
curl -X PUT "http://localhost:8001/ccow/active-patient" \
  -d '{"user_id": "xxx", "patient_id": "ICN100001"}'
```

✅ **Do** pass session cookie - user_id is extracted automatically
```bash
# CORRECT
curl -X PUT "http://localhost:8001/ccow/active-patient" \
  -b "session_id=xxx" \
  -d '{"patient_id": "ICN100001", "set_by": "test"}'
```

❌ **Don't** forget the cookie
```bash
# WRONG - will get 401 error
curl -X GET "http://localhost:8001/ccow/active-patient"
```

✅ **Do** include the cookie
```bash
# CORRECT
curl -X GET "http://localhost:8001/ccow/active-patient" \
  -b "session_id=xxx"
```

---

## Troubleshooting

**Problem:** Getting 401 errors

**Solution:**
1. Verify you're logged into med-z1 app
2. Get fresh session_id from browser cookies
3. Check session hasn't expired (15 min idle timeout)
4. Run debug script: `python scripts/debug_ccow_session.py <session_id>`

**Problem:** Getting 404 "No active patient context"

**Solution:** This is expected if you haven't set a patient yet. Use SET endpoint first.

**Problem:** Set succeeds but GET returns different patient

**Solution:** You might be using a different session_id. Each user has their own context. Verify session_id is consistent.

**Problem:** Swagger UI doesn't work

**Solution:** Swagger UI doesn't handle cookies well. Use curl or browser DevTools workaround above.
