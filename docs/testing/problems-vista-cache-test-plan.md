# Problems VistA Cache Persistence - Manual Test Plan

**Test Date:** 2026-02-08
**Feature:** VistA Cache Persistence for Problems Domain
**Bug Fix:** Align Problems page with Vitals/Medications pattern (auto-merge cached VistA data on page load)

---

## Prerequisites

1. ✅ Web app running: `uvicorn app.main:app --reload`
2. ✅ VistA service running on port 8003
3. ✅ Browser open to http://localhost:8000
4. ✅ Logged into med-z1
5. ✅ Test patient selected: **ICN100001** (Adam Dooree)

---

## Test 1: Initial Page Load (No Cache)

**Expected:** Page shows PostgreSQL data only, no VistA cache

### Steps:
1. Navigate to Problems page: http://localhost:8000/patient/ICN100001/problems
2. Observe the problems list and statistics

### Expected Results:
- ✓ Page renders successfully
- ✓ Shows problems from PostgreSQL (T-1 and earlier)
- ✓ Charlson score displayed (should be 7 for ICN100001)
- ✓ No "Vista refreshed" indicator/timestamp

### Server Logs to Check:
```
DEBUG: No cached Vista data for ICN100001/problems - using PostgreSQL only
```

---

## Test 2: VistA Refresh (Cache Data)

**Expected:** Fetch VistA data and store in session cache

### Steps:
1. On Problems page, click "Refresh VistA" button
2. Wait for page to update (1-3 seconds)
3. Observe merge results

### Expected Results:
- ✓ Page updates with merged data
- ✓ Vista refresh indicator shows (timestamp, sites queried)
- ✓ Problem count may increase (if T-0 problems exist)
- ✓ "Last Updated" shows current time

### Server Logs to Check:
```
INFO: Merging PG data with cached Vista responses from sites: ['200', '500', '630']
INFO: Merged: X problems (Y PG + Z Vista)
INFO: ✓ Cached Vista responses for ICN100001/problems: 3 sites, ~N bytes (Vista: Z records)
```

---

## Test 3: Navigate Away and Back (Cache Persists)

**Expected:** Cached VistA data auto-merges on page load

###Steps:
1. After VistA refresh in Test 2, navigate to **Demographics** page
2. Click browser back button OR click "Problems" in left nav
3. Observe problems page loads

### Expected Results:
- ✓ Page loads quickly (no new VistA RPC calls)
- ✓ Shows same merged data as Test 2
- ✓ Problem count matches Test 2 (includes VistA data)
- ✓ No "Vista refreshed" indicator (didn't click button)

### Server Logs to Check (KEY TEST!):
```
INFO: Merging PG data with cached Vista responses from sites: ['200', '500', '630']
INFO: Merged: X problems (Y PG + Z Vista)
```

**This is the fix!** Before the fix, logs would show NO merge message and page would only show PostgreSQL data.

---

## Test 4: Page Refresh (Cache Still Persists)

**Expected:** F5 refresh still uses cached VistA data

### Steps:
1. On Problems page (after Test 3), press **F5** (page refresh)
2. Observe page reloads

### Expected Results:
- ✓ Page reloads with merged data
- ✓ Problem count still includes VistA data
- ✓ Still within 30-minute cache TTL

### Server Logs to Check:
```
INFO: Merging PG data with cached Vista responses from sites: ['200', '500', '630']
INFO: Merged: X problems (Y PG + Z Vista)
```

---

## Test 5: Cache Expiration (30-Minute TTL)

**Expected:** After 30 minutes, cache expires and page shows PostgreSQL only

### Steps:
1. Wait 31 minutes (or manually clear session cookies)
2. Reload Problems page

### Expected Results:
- ✓ Page shows PostgreSQL data only
- ✓ Problem count may decrease (no VistA T-0 data)
- ✓ No merge messages in logs

### Server Logs to Check:
```
INFO: Vista cache EXPIRED for ICN100001/problems (age: 31.2 min, TTL: 30 min)
DEBUG: No cached Vista data for ICN100001/problems - using PostgreSQL only
```

---

## Test 6: Different Patient (Cache is Per-ICN)

**Expected:** Switching patients doesn't show cached data from previous patient

### Steps:
1. After Test 2 (VistA refresh for ICN100001), switch to **ICN100010** (Alexander Aminor)
2. Navigate to Problems page for ICN100010

### Expected Results:
- ✓ Page shows PostgreSQL data only for ICN100010
- ✓ No cached data from ICN100001 (cache is per-patient)

### Server Logs to Check:
```
DEBUG: No cached Vista data for ICN100010/problems - using PostgreSQL only
```

---

## Test 7: Compare with Vitals (Consistency Check)

**Expected:** Problems should behave identically to Vitals domain

### Steps:
1. Navigate to Vitals page for ICN100001
2. Click "Refresh VistA" on Vitals
3. Navigate to Demographics, then back to Vitals
4. Observe: Vitals shows cached merged data WITHOUT clicking "Refresh VistA" again

### Expected Results:
- ✓ Vitals auto-merges cached data on page load
- ✓ Problems auto-merges cached data on page load
- ✓ **Same behavior across domains** ← This is the bug fix!

---

## Success Criteria

✅ **Bug Fix Verified** if:
1. Test 3 server logs show "Merging PG data with cached Vista responses"
2. Test 3 page shows merged data (not just PostgreSQL)
3. Test 4 page refresh shows merged data
4. Problems behaves identically to Vitals/Medications domains

❌ **Bug Still Present** if:
- Test 3/4 show PostgreSQL data only
- Test 3/4 server logs show "No cached Vista data"
- User must click "Refresh VistA" again after navigation

---

## Code Changes Summary

**File Modified:** `app/routes/problems.py:366` (`patient_problems_page()`)

**Change:** Added VistA cache check after fetching PostgreSQL data:

```python
# Get all problems from PostgreSQL (no filters yet - need all for potential merge)
all_problems = get_patient_problems(icn, status=None, category=None, service_connected_only=False)

# Check if we have cached Vista responses to merge with PG data
from app.services.vista_cache import VistaSessionCache
from app.services.realtime_overlay import merge_problems_data

problems_cache = VistaSessionCache.get_cached_data(request, icn, "problems")

if problems_cache and "vista_responses" in problems_cache:
    # Merge PG data with cached Vista responses
    logger.info(f"Merging PG data with cached Vista responses from sites: {problems_cache.get('sites')}")
    all_problems, merge_stats = merge_problems_data(all_problems, problems_cache["vista_responses"], icn)
    logger.info(f"Merged: {merge_stats['total_merged']} problems ({merge_stats['pg_count']} PG + {merge_stats['vista_count']} Vista)")
else:
    logger.debug(f"No cached Vista data for {icn}/problems - using PostgreSQL only")
```

**Pattern Matched:** Vitals (`app/routes/vitals.py:240-249`), Medications (`app/routes/medications.py:297-314`)

---

## Troubleshooting

**Issue:** Server logs show no merge messages
- **Solution:** Check that `logger` is configured for INFO level in problems.py

**Issue:** Cache appears empty even after VistA refresh
- **Solution:** Check session middleware is enabled in `app/main.py`
- **Solution:** Verify cookies are being set (inspect browser DevTools → Application → Cookies)

**Issue:** Merge happens but data looks identical
- **Solution:** ICN100001 might not have T-0 VistA problems; check Vista mock data files
- **Solution:** Try different test patient (ICN100010, ICN100013)

---

## Next Steps After Test

1. ✅ Verify all 7 tests pass
2. ✅ Document results in this file
3. ✅ Update `docs/spec/problems-design.md` (mark Phase 6 Day 15 task complete)
4. ✅ Proceed to Phase 6 Day 15-16: AI Integration
