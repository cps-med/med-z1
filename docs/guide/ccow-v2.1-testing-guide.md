# CCOW Context Vault v2.1 - Testing Guide

**Document Version:** v1.0
**Date:** 2026-01-27
**Purpose:** Testing guide for X-Session-ID header support (cross-application authentication)

---

## Table of Contents

1. [Overview](#1-overview)
   - [Curl Command Quoting Conventions](#11-curl-command-quoting-conventions)
   - [macOS Compatibility Note](#12-macos-compatibility-note)
2. [Prerequisites](#2-prerequisites)
3. [Test Scenarios](#3-test-scenarios)
4. [Regression Tests](#4-regression-tests)
5. [New Feature Tests](#5-new-feature-tests)
6. [Integration Tests](#6-integration-tests)
7. [Troubleshooting](#7-troubleshooting)
8. [Testing with Insomnia](#8-testing-with-insomnia-recommended)
9. [Quick Test Suite](#9-quick-test-suite-copy-paste-ready)
10. [Summary](#10-summary)

---

## 1. Overview

CCOW Vault v2.1 adds `X-Session-ID` header support to enable cross-application authentication. This guide covers testing both authentication methods:

- **Method 1:** `X-Session-ID` header (new - for external apps like med-z4)
- **Method 2:** `session_id` cookie (existing - for med-z1)

**Key Testing Goals:**
1. ✅ Verify no regression to existing cookie-based authentication
2. ✅ Verify new header-based authentication works correctly
3. ✅ Verify priority order (header > cookie)
4. ✅ Verify security (session validation works for both methods)

### 1.1 Curl Command Quoting Conventions

**This guide uses consistent quoting for all curl commands:**

```bash
# ✅ CORRECT - Single quotes for JSON data (prevents shell expansion)
-d '{"patient_id": "ICN100001", "set_by": "med-z1"}'

# ✅ CORRECT - Single quotes for static headers
-H 'Content-Type: application/json'

# ✅ CORRECT - Double quotes for headers with shell variables (allows $VAR expansion)
-H "X-Session-ID: $SESSION_ID"

# ❌ WRONG - Multi-line JSON causes "dquote>" prompt error
-d '{
  "patient_id": "ICN100001"
}'
```

**Why these conventions?**
- Single quotes prevent shell interpretation (safest for JSON)
- Double quotes required when using shell variables like `$SESSION_ID`
- Single-line JSON prevents parsing errors

### 1.2 macOS Compatibility Note

**Session ID Extraction:**
This guide uses `awk` for extracting session IDs from cookie files because it works on all systems (macOS, Linux, BSD):

```bash
# ✅ CORRECT - Works on macOS and Linux
SESSION_ID=$(awk '/session_id/ {print $NF}' cookies_alpha.txt)

# ❌ WRONG - Only works on Linux (GNU grep)
SESSION_ID=$(grep -oP 'session_id\s+\K[^;]+' cookies_alpha.txt)
```

**Why?**
- macOS uses BSD `grep` (no `-P` flag for Perl regex)
- Linux uses GNU `grep` (has `-P` flag)
- `awk` is POSIX standard and works everywhere

---

## 2. Prerequisites

### 2.1 Required Services

```bash
# Terminal 1: Start CCOW Vault service
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --reload --port 8001

# Terminal 2: Start med-z1 application (optional, for cookie-based tests)
uvicorn app.main:app --reload --port 8000
```

### 2.2 Verify CCOW Service is Running

```bash
curl http://localhost:8001/ccow/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "ccow-vault",
  "version": "2.1.0",
  "timestamp": "2026-01-27T18:30:00.000Z",
  "active_contexts": 0
}
```

**✅ Version should be `2.1.0` (not 2.0.0)**

### 2.3 Test Users

Use existing med-z1 test users:

| User | Email | Password |
|------|-------|----------|
| Clinician Alpha | clinician.alpha@va.gov | VaDemo2025! |
| Clinician Bravo | clinician.bravo@va.gov | VaDemo2025! |

---

## 3. Test Scenarios

### 3.1 Test Scenario Matrix

| Test ID | Method | Description | Expected Result |
|---------|--------|-------------|-----------------|
| T1 | Cookie | Set patient via cookie (med-z1 regression) | 200 OK |
| T2 | Cookie | Get patient via cookie | 200 OK |
| T3 | Cookie | Clear patient via cookie | 204 No Content |
| T4 | Header | Set patient via header (med-z4 new feature) | 200 OK |
| T5 | Header | Get patient via header | 200 OK |
| T6 | Header | Clear patient via header | 204 No Content |
| T7 | Both | Header takes priority over cookie | Uses header session |
| T8 | None | No auth provided | 401 Unauthorized |
| T9 | Header | Invalid session_id | 401 Unauthorized |

---

## 4. Regression Tests

### Test T1: Set Patient via Cookie (med-z1 Existing Behavior)

**Purpose:** Verify no regression to existing cookie-based authentication

```bash
# Step 1: Login to med-z1 to get session cookie
curl -X POST http://localhost:8000/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'email=clinician.alpha@va.gov&password=VaDemo2025!' \
  -c cookies_alpha.txt \
  -v

# Step 2: Set active patient via cookie
curl -X PUT http://localhost:8001/ccow/active-patient \
  -b cookies_alpha.txt \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100001", "set_by": "med-z1"}'
```

**Expected Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100001",
  "set_by": "med-z1",
  "set_at": "2026-01-27T18:30:00.000Z",
  "last_accessed_at": "2026-01-27T18:30:00.000Z"
}
```

✅ **Pass Criteria:** Status 200, patient_id matches request

---

### Test T2: Get Patient via Cookie

```bash
# Get active patient (should return ICN100001 from T1)
curl -X GET http://localhost:8001/ccow/active-patient \
  -b cookies_alpha.txt
```

**Expected Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100001",
  "set_by": "med-z1",
  "set_at": "2026-01-27T18:30:00.000Z",
  "last_accessed_at": "2026-01-27T18:30:05.000Z"
}
```

✅ **Pass Criteria:** Returns same patient_id as T1, last_accessed_at updated

---

### Test T3: Clear Patient via Cookie

```bash
# Clear active patient
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -b cookies_alpha.txt \
  -H 'Content-Type: application/json' \
  -d '{"cleared_by": "med-z1"}' \
  -v
```

**Expected Response:** 204 No Content (empty body)

**Verify cleared:**
```bash
curl -X GET http://localhost:8001/ccow/active-patient \
  -b cookies_alpha.txt
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "No active patient context for user"
}
```

✅ **Pass Criteria:** DELETE returns 204, subsequent GET returns 404

---

## 5. New Feature Tests

### Test T4: Set Patient via Header (med-z4 New Feature)

**Purpose:** Verify new header-based authentication works

```bash
# Step 1: Extract session_id from cookie file (from T1 login)
SESSION_ID=$(awk '/session_id/ {print $NF}' cookies_alpha.txt)
echo "Session ID: $SESSION_ID"

# Step 2: Set active patient via X-Session-ID header
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100010", "set_by": "med-z4"}'
```

**Expected Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100010",
  "set_by": "med-z4",
  "set_at": "2026-01-27T18:35:00.000Z",
  "last_accessed_at": "2026-01-27T18:35:00.000Z"
}
```

✅ **Pass Criteria:**
- Status 200
- patient_id = "ICN100010"
- set_by = "med-z4" (proves header auth worked)
- Same user_id as cookie-based test (proves session validation works)

---

### Test T5: Get Patient via Header

```bash
# Get active patient via header
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID"
```

**Expected Response (200 OK):**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "clinician.alpha@va.gov",
  "patient_id": "ICN100010",
  "set_by": "med-z4",
  "set_at": "2026-01-27T18:35:00.000Z",
  "last_accessed_at": "2026-01-27T18:35:05.000Z"
}
```

✅ **Pass Criteria:** Returns patient_id from T4, last_accessed_at updated

---

### Test T6: Clear Patient via Header

```bash
# Clear active patient via header
curl -X DELETE http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H 'Content-Type: application/json' \
  -d '{"cleared_by": "med-z4"}' \
  -v

# Verify cleared
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID"
```

**Expected Response (404 Not Found):**
```json
{
  "detail": "No active patient context for user"
}
```

✅ **Pass Criteria:** DELETE returns 204, subsequent GET returns 404

---

## 6. Integration Tests

### Test T7: Header Takes Priority Over Cookie

**Purpose:** Verify priority order when both are present

```bash
# Step 1: Login as two different users
curl -X POST http://localhost:8000/login \
  -d 'email=clinician.alpha@va.gov&password=VaDemo2025!' \
  -c cookies_alpha.txt

curl -X POST http://localhost:8000/login \
  -d 'email=clinician.bravo@va.gov&password=VaDemo2025!' \
  -c cookies_bravo.txt

# Step 2: Extract both session IDs
SESSION_ALPHA=$(awk '/session_id/ {print $NF}' cookies_alpha.txt)
SESSION_BRAVO=$(awk '/session_id/ {print $NF}' cookies_bravo.txt)

# Step 3: Set different patients for each user
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ALPHA" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100001", "set_by": "test"}'

curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_BRAVO" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100010", "set_by": "test"}'

# Step 4: Test priority - pass Bravo's header + Alpha's cookie
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_BRAVO" \
  -b cookies_alpha.txt
```

**Expected Response:**
```json
{
  "user_id": "<bravo-user-id>",
  "email": "clinician.bravo@va.gov",
  "patient_id": "ICN100010",
  ...
}
```

✅ **Pass Criteria:**
- Returns Bravo's patient (ICN100010), not Alpha's (ICN100001)
- Proves header took priority over cookie

---

### Test T8: No Authentication Provided

**Purpose:** Verify 401 when no session provided

```bash
# Attempt to get patient without auth
curl -X GET http://localhost:8001/ccow/active-patient \
  -v
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Missing authentication: X-Session-ID header or session_id cookie required"
}
```

✅ **Pass Criteria:** Status 401, clear error message

---

### Test T9: Invalid Session ID

**Purpose:** Verify session validation works

```bash
# Use fake/invalid session UUID
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: 00000000-0000-0000-0000-000000000000"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid or expired session"
}
```

✅ **Pass Criteria:** Status 401, validation error

---

## 7. Troubleshooting

### Issue 1: "Missing authentication" Error

**Symptom:**
```json
{"detail": "Missing authentication: X-Session-ID header or session_id cookie required"}
```

**Causes:**
1. Session cookie expired or not extracted correctly
2. Header typo (use `X-Session-ID`, not `X-Session-Id` or `session-id`)
3. Cookie not included in request (missing `-b cookies.txt`)

**Fix:**
```bash
# Verify session cookie exists
cat cookies_alpha.txt | grep session_id

# If expired, re-login
curl -X POST http://localhost:8000/login \
  -d 'email=clinician.alpha@va.gov&password=VaDemo2025!' \
  -c cookies_alpha.txt
```

---

### Issue 2: "Invalid or expired session" Error

**Symptom:**
```json
{"detail": "Invalid or expired session"}
```

**Causes:**
1. Session expired (15-minute TTL by default)
2. Session not found in `auth.sessions` table
3. Session marked as `is_active = FALSE`

**Fix:**
```bash
# Check session in database
psql -U postgres -d medz1 -c "
  SELECT session_id, user_id, is_active, expires_at
  FROM auth.sessions
  WHERE session_id = '<your-session-id>'::UUID;
"

# If expired, re-login
curl -X POST http://localhost:8000/login \
  -d 'email=clinician.alpha@va.gov&password=VaDemo2025!' \
  -c cookies_alpha.txt
```

---

### Issue 3: Version Shows 2.0.0 Instead of 2.1.0

**Symptom:**
```json
{"version": "2.0.0"}
```

**Cause:** CCOW service not restarted after code update

**Fix:**
```bash
# Stop old CCOW service
pkill -f "uvicorn ccow.main"

# Restart with new code
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn ccow.main:app --reload --port 8001

# Verify version
curl http://localhost:8001/ccow/health | grep version
# Should show: "version": "2.1.0"
```

---

### Issue 4: CORS Errors with curl on macOS

**Symptom:** 401 errors with curl despite valid session cookie (macOS specific)

**Cause:** curl on macOS may encounter CORS-related authentication issues

**Fix - Add CORS Headers:**
```bash
# Add Origin and Referer headers to simulate browser requests
curl -X GET http://localhost:8001/ccow/active-patient \
  -b "session_id=$SESSION_ID" \
  -H "Origin: http://localhost:8001" \
  -H "Referer: http://localhost:8001/"
```

**Note:**
- This is a local development workaround only
- Browsers handle these headers automatically
- **Insomnia does NOT require this workaround** (recommended tool for API testing)
- X-Session-ID header method does NOT require CORS headers

---

### Issue 5: Context Not Persisting Between Tests

**Symptom:** GET returns 404 immediately after PUT

**Causes:**
1. Using different session IDs for PUT and GET
2. Session expired between requests
3. CCOW service restarted (in-memory data lost)

**Fix:**
```bash
# Use same session for both operations
SESSION_ID=$(awk '/session_id/ {print $NF}' cookies_alpha.txt)

# Set patient
curl -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100001", "set_by": "test"}'

# Get patient (use SAME session_id)
curl -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID"
```

---

## 8. Testing with Insomnia (Recommended)

**Insomnia** is the recommended API testing tool for CCOW as it:
- ✅ Automatically handles cookies and headers correctly
- ✅ Does NOT require CORS workarounds (unlike curl on macOS)
- ✅ Provides clean UI for managing authentication
- ✅ Supports both cookie and header authentication methods

### 8.1 Quick Start

1. **Install Insomnia:** https://insomnia.rest/download
2. **Import Collection:** `docs/insomnia-ccow-collection.json` (if available)
3. **Configure Session:** Replace `YOUR_SESSION_ID_HERE` with actual session from browser cookies

### 8.2 Testing Cookie-Based Auth (med-z1)

**Method 1: Cookie Header**
```
GET http://localhost:8001/ccow/active-patient
Header: Cookie: session_id=<your-session-id>
```

**Method 2: Cookie Manager** (Automatic)
1. Click **Cookies** button (top right)
2. Select domain: `localhost:8001`
3. Add cookie: `session_id=<your-session-id>; Path=/; Domain=localhost`
4. All requests automatically include cookie

### 8.3 Testing Header-Based Auth (med-z4)

```
GET http://localhost:8001/ccow/active-patient
Header: X-Session-ID: <your-session-id>
```

**Benefits:**
- No cookie configuration needed
- Explicit authentication (clear which method is used)
- Perfect for testing med-z4 integration

### 8.4 Example Workflow

1. **Health Check** (no auth) → Verify service is v2.1.0
2. **PUT Set Patient** (cookie auth) → Test med-z1 integration
3. **GET Patient** (header auth) → Test med-z4 integration (same session)
4. **Verify same context** → Both methods see same patient

### 8.5 Common Insomnia Errors

**401 Unauthorized:**
- Check Cookie or X-Session-ID header is present
- Verify session hasn't expired (15 min TTL)
- Get fresh session by logging into med-z1

**422 Unprocessable Entity:**
- Verify Body Type is set to **JSON** (not Text)
- Check required fields: `patient_id`, `set_by`

**Connection Refused:**
- CCOW service not running
- Start with: `uvicorn ccow.main:app --reload --port 8001`

---

## 9. Quick Test Suite (Copy-Paste Ready)

```bash
#!/bin/bash
# CCOW v2.1 Quick Test Suite

echo "=== CCOW v2.1 Test Suite ==="
echo ""

# Prerequisites
echo "1. Checking CCOW service..."
HEALTH=$(curl -s http://localhost:8001/ccow/health | grep -o '"version":"2.1.0"')
if [ -z "$HEALTH" ]; then
  echo "❌ CCOW service not running or wrong version"
  exit 1
fi
echo "✅ CCOW v2.1 is running"
echo ""

# Login
echo "2. Logging in as Clinician Alpha..."
curl -X POST http://localhost:8000/login \
  -d 'email=clinician.alpha@va.gov&password=VaDemo2025!' \
  -c cookies_test.txt -s > /dev/null
SESSION_ID=$(awk '/session_id/ {print $NF}' cookies_test.txt)
echo "✅ Session ID: ${SESSION_ID:0:8}..."
echo ""

# Test T1: Cookie-based SET
echo "3. Testing cookie-based SET (regression)..."
RESP=$(curl -s -X PUT http://localhost:8001/ccow/active-patient \
  -b cookies_test.txt \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100001", "set_by": "med-z1"}')
if echo "$RESP" | grep -q "ICN100001"; then
  echo "✅ T1: Cookie-based SET works"
else
  echo "❌ T1: Cookie-based SET failed"
  echo "$RESP"
fi
echo ""

# Test T2: Cookie-based GET
echo "4. Testing cookie-based GET (regression)..."
RESP=$(curl -s -X GET http://localhost:8001/ccow/active-patient -b cookies_test.txt)
if echo "$RESP" | grep -q "ICN100001"; then
  echo "✅ T2: Cookie-based GET works"
else
  echo "❌ T2: Cookie-based GET failed"
  echo "$RESP"
fi
echo ""

# Test T4: Header-based SET
echo "5. Testing header-based SET (new feature)..."
RESP=$(curl -s -X PUT http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID" \
  -H 'Content-Type: application/json' \
  -d '{"patient_id": "ICN100010", "set_by": "med-z4"}')
if echo "$RESP" | grep -q "ICN100010"; then
  echo "✅ T4: Header-based SET works"
else
  echo "❌ T4: Header-based SET failed"
  echo "$RESP"
fi
echo ""

# Test T5: Header-based GET
echo "6. Testing header-based GET (new feature)..."
RESP=$(curl -s -X GET http://localhost:8001/ccow/active-patient \
  -H "X-Session-ID: $SESSION_ID")
if echo "$RESP" | grep -q "ICN100010"; then
  echo "✅ T5: Header-based GET works"
else
  echo "❌ T5: Header-based GET failed"
  echo "$RESP"
fi
echo ""

# Test T8: No auth
echo "7. Testing no authentication (security)..."
RESP=$(curl -s -w "%{http_code}" -X GET http://localhost:8001/ccow/active-patient)
if echo "$RESP" | grep -q "401"; then
  echo "✅ T8: No auth returns 401"
else
  echo "❌ T8: No auth should return 401"
  echo "$RESP"
fi
echo ""

# Cleanup
rm -f cookies_test.txt

echo "=== Test Suite Complete ==="
```

**To run:**
```bash
chmod +x ccow_test_suite.sh
./ccow_test_suite.sh
```

---

## 10. Summary

**✅ Regression Tests (med-z1 cookie-based):**
- T1: Set patient via cookie
- T2: Get patient via cookie
- T3: Clear patient via cookie

**✅ New Feature Tests (med-z4 header-based):**
- T4: Set patient via header
- T5: Get patient via header
- T6: Clear patient via header

**✅ Integration Tests:**
- T7: Header priority over cookie
- T8: No authentication returns 401
- T9: Invalid session returns 401

**All tests passing = v2.1 ready for production** ✅

---

**End of Document**
