# Clinical Tasks Widget - Manual Testing Guide

**Created:** 2026-02-10
**Phase:** Week 2, Day 8-10 - Dashboard Widget Implementation
**Status:** Ready for Testing

---

## Prerequisites

1. **Database:** PostgreSQL with seed data (15 test tasks)
2. **FastAPI app:** Running on http://localhost:8000
3. **Browser:** Chrome, Firefox, or Safari (latest 2 versions)
4. **Test User:** clinician.alpha@va.gov / VaDemo2025!

---

## Starting the Application

```bash
# Terminal 1: Start FastAPI app
cd /Users/chuck/swdev/med/med-z1
source .venv/bin/activate
uvicorn app.main:app --reload

# Access the application
# http://localhost:8000
```

---

## Test Cases

### TEST 1: Widget Loads on Dashboard

**Steps:**
1. Navigate to http://localhost:8000
2. Login as clinician.alpha@va.gov
3. Search for and select patient "Dooree, Adam" (ICN100001)
4. Observe dashboard loads with widgets

**Expected Results:**
- ✓ Tasks widget appears as a 2x1 (wide) widget
- ✓ Widget is positioned to the right of Demographics widget
- ✓ Widget header shows "My Active Tasks" with task count badge
- ✓ Widget body shows 5-8 active tasks (TODO + IN_PROGRESS)
- ✓ Tasks are sorted by priority (HIGH > MEDIUM > LOW)
- ✓ Widget footer shows "View All Tasks" link and "+" quick create button

**Screenshots:**
- [ ] Full dashboard view
- [ ] Tasks widget close-up

---

### TEST 2: Task Priority Visual Indicators

**Steps:**
1. On the dashboard with patient ICN100001 selected
2. Observe tasks in the widget

**Expected Results:**
- ✓ HIGH priority tasks have red badge and red left border
- ✓ MEDIUM priority tasks have yellow badge and yellow left border
- ✓ LOW priority tasks have gray badge and gray left border
- ✓ Each task shows priority badge on the left
- ✓ Tasks are visually grouped by priority

---

### TEST 3: Task Status Indicators

**Steps:**
1. Observe tasks with different statuses in the widget

**Expected Results:**
- ✓ TODO tasks show hollow circle icon + "To Do" text
- ✓ IN_PROGRESS tasks show spinning icon + "In Progress" text (blue color)
- ✓ AI-generated tasks show robot icon + "AI" badge (purple)
- ✓ Task creator name is displayed (e.g., "Dr. Alice Anderson, MD")

---

### TEST 4: Quick Actions - Start Task

**Steps:**
1. Find a task with status "TODO" in the widget
2. Click the "Play" icon button (blue)
3. Observe the widget

**Expected Results:**
- ✓ Widget refreshes via HTMX (no full page reload)
- ✓ Task status changes from "To Do" to "In Progress"
- ✓ Task icon changes from hollow circle to spinning icon
- ✓ Action buttons change to "Complete" (green check) and "Revert" (gray rotate)
- ✓ Task count badge updates

---

### TEST 5: Quick Actions - Complete Task

**Steps:**
1. Find a task with status "TODO" or "IN_PROGRESS"
2. Click the "Check" icon button (green)
3. Confirm the completion in the dialog
4. Observe the widget

**Expected Results:**
- ✓ Browser confirmation dialog appears: "Mark this task as complete?"
- ✓ After confirming, widget refreshes via HTMX
- ✓ Task is removed from the active tasks list (no longer TODO/IN_PROGRESS)
- ✓ Task count badge decreases by 1
- ✓ Widget shows fewer tasks

---

### TEST 6: Quick Actions - Revert Task

**Steps:**
1. Start a task (see TEST 4) so it's "IN_PROGRESS"
2. Click the "Rotate" icon button (gray)
3. Observe the widget

**Expected Results:**
- ✓ Widget refreshes via HTMX
- ✓ Task status changes from "In Progress" back to "To Do"
- ✓ Task icon changes from spinning to hollow circle
- ✓ Action buttons change back to "Start" and "Complete"

---

### TEST 7: Empty State

**Steps:**
1. Select a patient with no tasks (e.g., ICN100005 or any patient without seed data)
2. Observe the tasks widget

**Expected Results:**
- ✓ Widget shows empty state with clipboard icon
- ✓ Message: "No active tasks for this patient"
- ✓ "Create First Task" button is displayed
- ✓ Clicking button would open quick create modal (modal implementation in Day 13-14)

---

### TEST 8: Error State

**Steps:**
1. Stop the PostgreSQL database
2. Refresh the dashboard
3. Observe the tasks widget

**Expected Results:**
- ✓ Widget shows error icon
- ✓ Message: "Error loading tasks"
- ✓ Widget does not break the page layout
- ✓ Other widgets still load normally

---

### TEST 9: Responsive Design

**Steps:**
1. On the dashboard with tasks widget visible
2. Resize browser window to mobile width (< 768px)
3. Observe widget layout

**Expected Results:**
- ✓ Tasks widget collapses to single column (1x1 equivalent)
- ✓ Task items stack vertically
- ✓ Action buttons remain visible and usable
- ✓ Text truncation works correctly (no overflow)

---

### TEST 10: View All Tasks Link

**Steps:**
1. Click "View All Tasks" link in widget footer
2. Observe navigation

**Expected Results:**
- ✓ Navigates to `/patient/ICN100001/tasks`
- ✓ Full tasks page loads (placeholder HTML in Phase 1)
- ✓ Sidebar "Tasks" navigation item is highlighted as active
- ✓ Can navigate back to dashboard

---

### TEST 11: HTMX Reload on Task Update

**Steps:**
1. Have two browser windows open to the same dashboard
2. In Window 1: Complete a task
3. In Window 2: Click "View All Tasks" then return to dashboard
4. Observe both windows

**Expected Results:**
- ✓ Window 1: Widget updates immediately after completing task
- ✓ Window 2: Widget shows stale data until page refresh
- ✓ After refresh in Window 2, both windows show consistent data
- ✓ Task count badges match in both windows

---

## Performance Checks

### Load Time
- [ ] Widget loads within 2 seconds on dashboard
- [ ] HTMX swap (task action) completes in < 500ms

### Database Queries
- [ ] Widget endpoint makes 2 queries: get_patient_tasks() + get_task_summary()
- [ ] No N+1 query problems
- [ ] Indexed queries (check logs for Index Scan vs Seq Scan)

---

## Browser Compatibility

Test in multiple browsers:

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Accessibility Checks

- [ ] Widget is keyboard navigable (Tab through actions)
- [ ] Action buttons have title attributes (hover tooltips)
- [ ] Icons have semantic meaning (Font Awesome classes)
- [ ] Color contrast meets WCAG AA standards

---

## Known Limitations (Phase 1)

- ⚠️ Quick create button opens modal (modal implementation in Day 13-14)
- ⚠️ No due dates shown (Phase 2 feature)
- ⚠️ No task categories shown (Phase 2 feature)
- ⚠️ No "My Tasks" vs "All Tasks" filter in widget (full page feature)

---

## Troubleshooting

### Widget doesn't load
- Check browser console for JavaScript errors
- Check FastAPI logs for endpoint errors
- Verify patient has ICN (not null)
- Verify user is authenticated (session cookie)

### Widget shows old data
- Clear browser cache
- Hard refresh (Cmd+Shift+R or Ctrl+Shift+R)
- Check that hx-trigger includes "taskUpdated from:body"

### Styles look wrong
- Verify styles.css loaded (check Network tab)
- Clear browser cache
- Check for CSS conflicts in dev tools

---

## Next Steps

After completing widget testing:
- **Day 11-12:** Full page view implementation
- **Day 13-14:** Modal implementation (quick create/edit)

---

## Test Completion Checklist

- [ ] All 11 test cases passed
- [ ] Performance benchmarks met
- [ ] Browser compatibility confirmed
- [ ] Accessibility checks passed
- [ ] Screenshots captured for documentation

---

**Tested By:** ___________________
**Date:** ___________________
**Notes:** ___________________
