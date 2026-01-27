# Session Timeout Behavior Guide

## Overview

This document explains when user sessions expire, what actions reset the timeout timer, and how the session activity tracking works in med-z1.

**Current Default Timeout:** 25 minutes (as of 2026-01-19, aligned with clinical workflow patterns)

---

## Session Timeout Mechanism

### How It Works

The med-z1 application uses a **sliding window timeout** mechanism:

1. **Initial Login**: Session created with `expires_at = NOW + 25 minutes`
2. **User Activity**: Every authenticated request extends `expires_at` by 25 more minutes
3. **Inactivity**: If no requests for 25 minutes, session expires
4. **Expiry Check**: On next request, expired sessions are invalidated and user redirected to login

### Key Timestamps

Each session in the database has three timestamps:

```sql
SELECT
    created_at,        -- When session was created (never changes)
    last_activity_at,  -- Last authenticated request (updates constantly)
    expires_at         -- When session will expire (extends with each request)
FROM auth.sessions;
```

**Example Timeline:**
```
14:00:00 - User logs in
           created_at = 14:00:00
           expires_at = 14:25:00 (25 min timeout)

14:05:00 - User clicks "Vitals" page
           last_activity_at = 14:05:00
           expires_at = 14:30:00 (extended!)

14:10:00 - User refreshes page
           last_activity_at = 14:10:00
           expires_at = 14:35:00 (extended again!)

14:40:00 - User idle for 30 minutes
           expires_at = 14:35:00 (no change, user inactive)

14:41:00 - User tries to click dashboard
           Session expired! (NOW > expires_at)
           Redirected to login page
```

---

## Actions That Reset the Timeout

### ✅ Actions That EXTEND Session (Reset Timer)

**All authenticated requests extend the session.** This includes:

#### 1. Page Navigation
- ✅ Click "Dashboard" link → **Extends session**
- ✅ Click "Vitals" page → **Extends session**
- ✅ Click "Medications" page → **Extends session**
- ✅ Click patient search → **Extends session**
- ✅ Navigate to demographics page → **Extends session**

#### 2. Page Refreshes
- ✅ **Normal refresh** (F5 or Ctrl+R) → **Extends session**
- ✅ **Hard refresh** (Ctrl+Shift+R) → **Extends session**
- ✅ Browser back/forward buttons → **Extends session**

#### 3. HTMX Dynamic Updates
- ✅ Load patient header partial → **Extends session**
- ✅ Load vitals widget → **Extends session**
- ✅ Update medications table → **Extends session**
- ✅ Load patient search results → **Extends session**
- ✅ Any HTMX `hx-get`, `hx-post`, `hx-put` request → **Extends session**

#### 4. User Actions
- ✅ Select patient from search → **Extends session**
- ✅ Click pagination links → **Extends session**
- ✅ Submit forms → **Extends session**
- ✅ Click "View Flags" modal → **Extends session**

#### 5. API Requests
- ✅ Get patient demographics → **Extends session**
- ✅ Get vitals data → **Extends session**
- ✅ Set CCOW context → **Extends session**
- ✅ Any authenticated API call → **Extends session**

### ❌ Actions That DO NOT Extend Session

Only **public routes** skip session extension:

#### 1. Static Assets (Loaded by Browser)
- ❌ CSS files (`/static/styles.css`) → **Does not extend**
- ❌ JavaScript files (`/static/htmx.js`) → **Does not extend**
- ❌ Images (`/static/logo.png`) → **Does not extend**
- ❌ Favicon (`/favicon.ico`) → **Does not extend**

#### 2. Login Page (Before Authentication)
- ❌ Load login page (`/login`) → **Does not extend**
- ❌ Submit login form → **Does not extend** (creates new session instead)

#### 3. API Documentation (Development)
- ❌ Swagger UI (`/docs`) → **Does not extend**
- ❌ OpenAPI schema (`/openapi.json`) → **Does not extend**

**Important:** Static assets are excluded because they're loaded automatically by the browser, often in the background. We don't want CSS/JS file requests to keep sessions alive indefinitely.

---

## Practical Examples

### Scenario 1: Active User (Session Stays Alive)

```
14:00 - Login (expires_at = 14:25)
14:05 - Click Vitals (expires_at = 14:30) ✅
14:10 - Refresh page (expires_at = 14:35) ✅
14:15 - View medications (expires_at = 14:40) ✅
14:20 - Select different patient (expires_at = 14:45) ✅
14:25 - Click dashboard (expires_at = 14:50) ✅

Result: Session NEVER expires because user is active every 5 minutes.
```

### Scenario 2: Idle User (Session Expires)

```
14:00 - Login (expires_at = 14:25)
14:05 - Click Vitals (expires_at = 14:30) ✅
14:10 - User takes phone call, walks away from computer
        ... 30 minutes pass ...
14:40 - User returns, clicks Dashboard
        ❌ Session expired at 14:30
        → Redirected to login page
```

### Scenario 3: User Leaves Browser Tab Open

```
14:00 - Login (expires_at = 14:25)
14:05 - View patient dashboard (expires_at = 14:30) ✅
14:10 - Switch to different browser tab (email, etc.)
        ... 30 minutes pass ...
14:40 - Switch back to med-z1 tab
        ❌ Tab still visible, but session expired

14:41 - Click any link
        → Session check fails
        → Redirected to login page
```

**Note:** Just keeping the browser tab open does NOT extend the session. You must actively interact with the application.

### Scenario 4: Page Auto-Refresh (Custom Implementation)

**Currently NOT implemented**, but if you were to add auto-refresh:

```javascript
// Example: Auto-refresh every 5 minutes
setInterval(() => {
    htmx.ajax('GET', '/api/dashboard/widgets/refresh', {
        target: '#widgets-container'
    });
}, 5 * 60 * 1000);
```

This would extend the session every 5 minutes, keeping the user logged in indefinitely (as long as browser tab is open).

**Recommendation:** Only implement auto-refresh if genuinely needed, as it may keep idle users logged in unnecessarily.

---

## Session Expiry Process

When a session expires, the following happens:

### 1. User Attempts Action

```
User clicks "Vitals" link
  ↓
Request sent to /patient/ICN123/vitals
  ↓
AuthMiddleware intercepts request
```

### 2. Middleware Checks Session

```python
# app/middleware/auth.py, line 76
if session['expires_at'] < datetime.now():
    logger.info(f"Session expired: {session_id}")
    auth_db.log_audit_event(
        event_type='session_timeout',
        user_id=session['user_id'],
        session_id=session_id,
        success=False,
        failure_reason='Session expired'
    )
    auth_db.invalidate_session(session_id)
    return self._redirect_to_login_with_cleared_cookie()
```

### 3. Session Invalidated

```sql
-- Session marked as inactive in database
UPDATE auth.sessions
SET is_active = FALSE
WHERE session_id = '<expired-session>';

-- Audit event logged
INSERT INTO auth.audit_log (event_type, user_id, success, failure_reason)
VALUES ('session_timeout', '<user-id>', FALSE, 'Session expired');
```

### 4. User Redirected

```
Browser receives 303 redirect to /login
  ↓
Session cookie cleared
  ↓
User sees login page
```

---

## Configuration

### Default Timeout

```bash
# .env
SESSION_TIMEOUT_MINUTES=25
```

**Note:** Default changed from 15 to 25 minutes on 2026-01-19 to better align with clinical workflow patterns (users frequently multitask, take phone calls, etc.).

### Adjusting Timeout

**Development (testing session expiry):**
```bash
# Short timeout for rapid testing
SESSION_TIMEOUT_MINUTES=2
```

**Development (normal work):**
```bash
# Standard timeout (current default)
SESSION_TIMEOUT_MINUTES=25
```

**Production (extended for clinical users):**
```bash
# Longer timeout for clinical workflow
SESSION_TIMEOUT_MINUTES=30
```

**Production (high security):**
```bash
# Shorter timeout for sensitive environments
SESSION_TIMEOUT_MINUTES=5
```

### Testing Session Timeout

To test session timeout behavior:

1. Set short timeout in `.env`:
   ```bash
   SESSION_TIMEOUT_MINUTES=2
   ```

2. Restart med-z1 app:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Login and note the time

4. Wait 2 minutes without any activity

5. Try to click any link → Should redirect to login

6. Check audit log:
   ```sql
   SELECT * FROM auth.audit_log
   WHERE event_type = 'session_timeout'
   ORDER BY event_timestamp DESC
   LIMIT 5;
   ```

---

## Technical Implementation

### Middleware Flow

```python
# app/middleware/auth.py

async def dispatch(self, request: Request, call_next):
    # 1. Skip public routes (static assets, login page)
    if self._is_public_route(request.url.path):
        return await call_next(request)

    # 2. Extract session cookie
    session_id = request.cookies.get("session_id")

    # 3. Validate session (active, not expired)
    session = auth_db.get_session(session_id)
    if session['expires_at'] < datetime.now():
        # Session expired - redirect to login
        return self._redirect_to_login_with_cleared_cookie()

    # 4. EXTEND session timeout (sliding window)
    auth_db.extend_session(session_id)  # ← KEY LINE

    # 5. Continue to route handler
    response = await call_next(request)
    return response
```

### Database Update

```sql
-- app/db/auth.py, extend_session()

UPDATE auth.sessions
SET
    last_activity_at = NOW(),           -- Track activity
    expires_at = NOW() + INTERVAL '25 minutes'  -- Extend by 25 min
WHERE session_id = :session_id
AND is_active = TRUE;
```

---

## Security Considerations

### Automatic Logout (Inactivity)

✅ **Good:**
- Protects against walk-away attacks (user leaves desk unlocked)
- Reduces risk of session hijacking for idle sessions
- Complies with security policies (VA requires auto-logout)

⚠️ **Trade-off:**
- User loses work if idle too long
- Can be frustrating for users on long phone calls

### Session Extension on Every Request

✅ **Good:**
- Sliding window timeout (user-friendly)
- Active users never experience unexpected logout
- Encourages continuous workflow

⚠️ **Trade-off:**
- Active users stay logged in indefinitely
- Must rely on users to logout when done

### Recommendations

**For Production:**

1. **Set appropriate timeout** based on use case:
   - Clinical workstations: 25-30 minutes (users multitask)
   - Public terminals: 5 minutes (shared computers)
   - Remote access: 15-20 minutes (balance security/convenience)

2. **Add logout button** prominently in UI (already implemented)

3. **Add session warning** (future enhancement):
   ```javascript
   // Warn user 2 minutes before expiry
   setTimeout(() => {
       alert("Your session will expire in 2 minutes. Click OK to stay logged in.");
       htmx.ajax('GET', '/api/ping'); // Extend session
   }, 23 * 60 * 1000); // 23 minutes (25 min timeout - 2 min warning)
   ```

4. **Monitor session duration** via audit logs:
   ```sql
   -- Find average session duration
   SELECT AVG(EXTRACT(EPOCH FROM (logout_at - login_at)) / 60) AS avg_minutes
   FROM auth.audit_log
   WHERE event_type IN ('login', 'logout');
   ```

---

## Troubleshooting

### Problem: Session expires too quickly

**Symptoms:**
- User logged out after only a few minutes
- "Session expired" message appears unexpectedly

**Solutions:**
1. Check `SESSION_TIMEOUT_MINUTES` in `.env`
2. Verify database `expires_at` is being updated:
   ```sql
   SELECT session_id, last_activity_at, expires_at
   FROM auth.sessions
   WHERE user_id = '<your-user-id>';
   ```
3. Check if `extend_session()` is being called (add logging)

### Problem: Session never expires

**Symptoms:**
- User stays logged in indefinitely
- Session persists even after 15+ minutes idle

**Solutions:**
1. Check if session extension is working:
   ```sql
   SELECT * FROM auth.sessions WHERE is_active = TRUE;
   -- Verify expires_at is in the future
   ```
2. Verify middleware is checking expiry:
   ```python
   # Add logging to auth middleware
   logger.info(f"Session check: expires_at={session['expires_at']}, now={datetime.now()}")
   ```
3. Check if custom code is extending session unexpectedly

### Problem: Static assets causing timeouts

**Symptoms:**
- CSS/JS loading seems to affect session
- Session behavior unpredictable

**Solutions:**
1. Verify static routes are in `PUBLIC_ROUTES`:
   ```python
   PUBLIC_ROUTES = ["/static", "/favicon.ico"]
   ```
2. Check middleware logs to confirm static requests skip auth

---

## Summary

**Session expires when:**
- ❌ No authenticated requests for 25 minutes (configurable)
- ❌ User clicks logout
- ❌ User closes browser (session cookie cleared)

**Session stays alive when:**
- ✅ User navigates between pages
- ✅ User refreshes pages (normal or hard refresh)
- ✅ HTMX loads partials/widgets
- ✅ Any authenticated API request is made

**Session does NOT extend when:**
- ❌ Browser loads CSS/JS files (static assets)
- ❌ Browser loads favicon
- ❌ User is on login page (not authenticated yet)

**Key Principle:**
> "Any intentional user interaction with the application extends the session timeout by 25 minutes."

The system uses a **sliding window timeout** - as long as you're actively using the application, your session will never expire. Only extended periods of inactivity (default: 25 minutes) will cause automatic logout.
