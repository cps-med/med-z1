# Clinical Task Tracking - Design Specification

**Document Version:** v1.0  
**Created:** 2026-02-10  
**Last Updated:** 2026-02-10  
**Status:** DESIGN PHASE  
**Feature Domain:** Clinical Workflow Management, Task Tracking  
**Priority:** MEDIUM - Enhances clinician workflow efficiency and care coordination  

**Implementation Status Source:** `docs/spec/implementation-status.md`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Clinical Context](#2-clinical-context)
3. [Data Architecture](#3-data-architecture)
4. [PostgreSQL Schema](#4-postgresql-schema)
5. [UI Design](#5-ui-design)
6. [API Endpoints](#6-api-endpoints)
7. [AI Integration](#7-ai-integration)
8. [Security & Authorization](#8-security--authorization)
9. [Implementation Roadmap](#9-implementation-roadmap)
10. [Appendices](#10-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

The Clinical Task Tracking feature provides clinicians with a **patient-centric task management system** that:

- Reduces cognitive load by **externalizing mental to-do lists** into structured, trackable tasks
- Improves **care coordination** by making tasks visible to all clinicians viewing a patient
- Leverages **AI insights** to proactively suggest clinical action items
- Maintains **audit trails** showing who created tasks, when, and based on what clinical data
- Integrates seamlessly with med-z1's **patient-centric workflow** (CCOW context, dashboard widgets, HTMX interactions)

### 1.2 Key Features (Phase 1 Implementation)

**Core Task Management:**
- ✅ Create, update, complete tasks associated with patients
- ✅ Three-state lifecycle: TODO → IN_PROGRESS → COMPLETED
- ✅ Priority levels: High, Medium, Low (visual indicators)
- ✅ Rich task descriptions (supports multi-line narrative text)
- ✅ Audit trail: Created by, created at, completed by, completed at

**UI Components:**
- ✅ **Dashboard widget** (2x1 grid) - Shows 5-8 most urgent tasks for active patient
- ✅ **Sidebar navigation** - "Tasks" link below Demographics
- ✅ **Full page view** - Comprehensive task list with filtering and status management
- ✅ **Quick create modal** - Fast task creation from any page

**AI Integration:**
- ✅ **AI-suggested tasks** - AI Insights chatbot analyzes patient data and suggests tasks
- ✅ **"Add to Tasks" button** - One-click task creation from AI suggestions
- ✅ **Audit trail** - Tasks record whether AI-generated or user-created

**Architecture Alignment:**
- ✅ **Patient-centric storage** - Tasks belong to patients (visible to care team)
- ✅ **User-centric workflow** - Clinicians create personal reminders, filter "My Tasks" vs "All Tasks"
- ✅ **Pattern B routing** - Dedicated `app/routes/tasks.py` router (following Vitals, Problems pattern)
- ✅ **PostgreSQL-backed** - Persistent storage in `clinical.patient_tasks` table
- ✅ **HTMX-powered** - Dynamic updates without full page refreshes

### 1.3 Out of Scope (Future Phases)

**Phase 2+ Enhancements:**
- ⏸️ Due dates / deadlines (calendar integration)
- ⏸️ Task categories/types (Lab Review, Medication, Follow-up, Consult, etc.)
- ⏸️ Task assignment to other users (care team delegation)
- ⏸️ Clinical data deep links (link task to specific lab result, medication order, note)
- ⏸️ Recurring tasks (e.g., "Review pending labs daily")
- ⏸️ Task comments/notes (threaded discussions on tasks)
- ⏸️ Email/push notifications for overdue tasks
- ⏸️ Bulk actions (complete multiple tasks, reassign tasks)
- ⏸️ Task templates (e.g., "Post-discharge follow-up checklist")
- ⏸️ Integration with external EHR task systems (CPRS worklist sync)

### 1.4 Expected Impact

**Clinician Efficiency:**
- **Reduced cognitive load** - Externalize mental reminders into structured system
- **Faster task capture** - Quick create modal accessible from any page
- **Contextual awareness** - Tasks always visible when viewing patient

**Care Coordination:**
- **Team visibility** - All clinicians see tasks for shared patients
- **Handoff support** - Tasks facilitate shift changes and coverage transitions
- **Care gaps** - AI proactively identifies missing follow-ups

**Quality Metrics:**
- **Task completion rate** - Measure clinician follow-through
- **Time to completion** - Identify workflow bottlenecks
- **AI suggestion adoption** - Measure AI value-add

---

## 2. Clinical Context

### 2.1 Task Management in Healthcare

**Problem Statement:**

Clinicians maintain complex mental to-do lists that are:
- **Fragile** - Easily forgotten during interruptions or shift changes
- **Invisible** - Care team members can't see each other's action items
- **Unstructured** - No prioritization, deadlines, or completion tracking
- **Disconnected from data** - No link between tasks and clinical evidence

**Current Workarounds:**
- Paper sticky notes on monitors (lost, not sharable)
- Personal notebooks (not accessible to care team)
- Email reminders (clutters inbox, no structure)
- CPRS "flag orders" (too heavyweight, billing-focused)

**med-z1 Solution:**
- **Patient-centric** - Tasks attached to patient record (visible to care team)
- **User-friendly** - Quick create, HTMX interactions, visual priority indicators
- **AI-assisted** - Proactive suggestions based on clinical data analysis
- **Audit-trailed** - Complete record of who did what, when, and why

### 2.2 Task Ownership Model

**Design Decision: Patient-Centric with User Attribution**

| Aspect | Design Choice | Rationale |
|--------|---------------|-----------|
| **Storage** | Tasks stored in patient record | Aligns with med-z1's patient-centric architecture |
| **Visibility** | Visible to all clinicians viewing patient | Supports care coordination and team handoffs |
| **Creation** | User creates task, tracked via `created_by_user_id` | Personal reminders + team visibility |
| **Filtering** | User can filter "My Tasks" (created by me) vs "All Tasks" | Balances personal workflow with team awareness |
| **Completion** | Any clinician can complete any task | Flexible care team collaboration |

**Example Scenarios:**

1. **Personal Reminder:**
   - Dr. Alpha creates task: "Review discharge summary for Patient ICN100001"
   - Dr. Alpha sees task in "My Tasks" filter
   - Dr. Beta (covering for Alpha) also sees task when viewing Patient ICN100001
   - Either Alpha or Beta can complete the task

2. **AI-Generated Task:**
   - User asks AI Insights: "What should I follow up on for this patient?"
   - AI suggests: "Patient overdue for A1C screening (last: 8 months ago)"
   - User clicks "Add to Tasks" → Task created, attributed to user
   - Task visible to entire care team

3. **Care Coordination:**
   - Primary care physician creates task: "Cardiology consult recommended"
   - Cardiologist views patient, sees task from PCP
   - Cardiologist reviews consult, completes task

### 2.3 Task Lifecycle

**Three-State Model:**

```
┌──────────┐
│   TODO   │ ← Task created (default state)
└────┬─────┘
     │
     ↓
┌──────────────┐
│ IN_PROGRESS  │ ← Clinician actively working on task
└────┬─────────┘
     │
     ↓
┌──────────┐
│COMPLETED │ ← Task finished (archived after 7 days)
└──────────┘
```

**Status Definitions:**

- **TODO** - Task created, not yet started (default)
- **IN_PROGRESS** - Clinician actively working on task
- **COMPLETED** - Task finished (timestamp recorded, visible for 7 days, then auto-archived)

**Phase 2+ Status Extensions:**
- CANCELLED - Task no longer relevant (archived immediately)
- DEFERRED - Postponed to future date (with reason)

### 2.4 Priority Levels

**Three-Level Priority System:**

| Priority | Visual Indicator | Use Case | Example |
|----------|------------------|----------|---------|
| **High** | Red badge, top of list | Urgent patient safety issue | "Call patient about critical lab result (K+ 6.5)" |
| **Medium** | Yellow badge, middle | Important but not urgent | "Review discharge summary from recent admission" |
| **Low** | Gray badge, bottom | Nice to have, low urgency | "Update patient education materials" |

**Default Priority:** Medium (if not specified)

**Phase 1 Note:** Priority is **user-assigned**, not AI-calculated. Phase 2+ could introduce AI-suggested priority based on clinical urgency scoring.

### 2.5 Use Cases

**Primary Use Cases:**

1. **Personal Clinical Reminders**
   - Clinician creates task to remind themselves to review specific clinical data
   - Example: "Check renal function before next Lisinopril refill"

2. **AI-Driven Care Gaps**
   - AI analyzes patient data, identifies overdue screenings or missing follow-ups
   - Example: "Patient overdue for pneumonia vaccine (age 68, COPD)"

3. **Post-Visit Action Items**
   - After reviewing patient chart, clinician creates tasks for follow-up
   - Example: "Order echocardiogram based on abnormal EKG"

4. **Team Handoff Communication**
   - Clinician creates task for next shift or covering provider
   - Example: "Overnight team: Monitor patient for hypoglycemia (insulin dose increased)"

5. **Care Coordination**
   - Task serves as communication between specialists
   - Example: "Primary care: Please review cardiology consult recommendations"

---

## 3. Data Architecture

### 3.1 Architectural Decision: Application-Managed Data

**Key Principle:** Tasks are **created and managed within med-z1**, not sourced from external systems.

**Implications:**

| Aspect | Design Choice | Rationale |
|--------|---------------|-----------|
| **Data Source** | PostgreSQL `clinical.patient_tasks` table | Single source of truth, no ETL pipeline needed |
| **Storage Layer** | Serving database only (no Bronze/Silver/Gold) | Tasks are operational data, not analytics |
| **Real-Time Sync** | Not applicable (no external source) | Tasks live only in med-z1 |
| **Vista Integration** | Not applicable (tasks not in VistA) | Phase 2+ could sync with CPRS worklist |

**Architecture Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│ USER INTERACTION                                            │
│ - Web UI (HTMX)                                             │
│ - AI Insights Chatbot                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER (FastAPI)                                 │
│ - app/routes/tasks.py (API + Page routers)                  │
│ - app/db/patient_tasks.py (Query layer)                     │
│ - ai/tools/task_tools.py (AI task suggestion tool)          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ POSTGRESQL SERVING DATABASE                                 │
│ - clinical.patient_tasks (task records)                     │
│ - auth.users (task creators)                                │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Data Ownership and Visibility

**Patient-Centric Storage:**

- Tasks are **owned by patients** (stored in patient record)
- Tasks are **created by users** (audit trail via `created_by_user_id`)
- Tasks are **visible to all clinicians** who view the patient
- Tasks are **completable by any clinician** (not locked to creator)

**User Filtering:**

Users can filter task views:
- **"My Tasks"** - Show only tasks I created (`created_by_user_id = current_user`)
- **"All Tasks"** - Show all tasks for this patient (no user filter)
- **"My Active Tasks"** - My tasks with status TODO or IN_PROGRESS

**Phase 2+ Assignment:**

Future enhancement: `assigned_to_user_id` field
- Task creator can assign to specific user
- Assigned user sees task in "Assigned to Me" filter
- Unassigned tasks visible to all (current Phase 1 behavior)

### 3.3 Integration Points

**CCOW Context Management:**

- **Dashboard widget load:** Queries CCOW for active patient ICN
- **Full page load:** `/tasks` redirects to `/patient/{icn}/tasks` using CCOW ICN
- **Task creation:** Auto-associates task with currently active patient from CCOW
- **Patient context switch:** Task widget refreshes to show new patient's tasks

**AI Insights Chatbot:**

- **User query:** "What tasks should I track for this patient?"
- **AI tool invocation:** `suggest_patient_tasks(patient_icn: str)`
- **AI response:** Markdown list with "Add to Tasks" buttons
- **Button click:** HTMX POST to `/api/patient/{icn}/tasks/from-ai` with pre-filled data
- **Result:** Task created, widget refreshes (OOB swap)

**Authentication & Sessions:**

- **User context:** `request.state.user` from `AuthMiddleware`
- **Task creation:** Automatically sets `created_by_user_id = request.state.user['user_id']`
- **Task completion:** Automatically sets `completed_by_user_id = request.state.user['user_id']`

---

## 4. PostgreSQL Schema

### 4.1 Table: `clinical.patient_tasks`

**Purpose:** Store all clinical tasks associated with patients

**DDL:**

```sql
-- File: db/ddl/create_patient_tasks_table.sql

CREATE TABLE IF NOT EXISTS clinical.patient_tasks (
    -- Primary key
    task_id SERIAL PRIMARY KEY,

    -- Patient association (ICN-based, patient-centric)
    patient_key VARCHAR(50) NOT NULL,  -- ICN, e.g., "ICN100001"

    -- Task content
    title VARCHAR(500) NOT NULL,       -- Brief task description
    description TEXT,                  -- Rich narrative text (optional)
    priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',  -- HIGH, MEDIUM, LOW
    status VARCHAR(50) NOT NULL DEFAULT 'TODO',      -- TODO, IN_PROGRESS, COMPLETED

    -- User attribution (audit trail)
    created_by_user_id UUID NOT NULL REFERENCES auth.users(user_id),
    created_by_display_name VARCHAR(255),  -- Denormalized for display
    completed_by_user_id UUID REFERENCES auth.users(user_id),
    completed_by_display_name VARCHAR(255),

    -- AI attribution (track AI-generated tasks)
    is_ai_generated BOOLEAN NOT NULL DEFAULT FALSE,
    ai_suggestion_source TEXT,  -- Free text: "AI suggested based on overdue A1C screening"

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,

    -- Indexes for common queries
    CONSTRAINT chk_priority CHECK (priority IN ('HIGH', 'MEDIUM', 'LOW')),
    CONSTRAINT chk_status CHECK (status IN ('TODO', 'IN_PROGRESS', 'COMPLETED'))
);

-- Index: Get all tasks for a patient (most common query)
CREATE INDEX idx_patient_tasks_patient_key ON clinical.patient_tasks(patient_key);

-- Index: Get user's created tasks (for "My Tasks" filter)
CREATE INDEX idx_patient_tasks_created_by ON clinical.patient_tasks(created_by_user_id);

-- Index: Get tasks by status (for filtering)
CREATE INDEX idx_patient_tasks_status ON clinical.patient_tasks(status);

-- Composite index: Patient + Status (optimized for dashboard widget)
CREATE INDEX idx_patient_tasks_patient_status ON clinical.patient_tasks(patient_key, status);

-- Updated_at trigger (auto-update on any column change)
CREATE OR REPLACE FUNCTION update_patient_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patient_tasks_updated_at
BEFORE UPDATE ON clinical.patient_tasks
FOR EACH ROW
EXECUTE FUNCTION update_patient_tasks_updated_at();

-- Completed_at auto-population (when status changes to COMPLETED)
CREATE OR REPLACE FUNCTION set_patient_tasks_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        NEW.completed_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patient_tasks_completed_at
BEFORE UPDATE ON clinical.patient_tasks
FOR EACH ROW
EXECUTE FUNCTION set_patient_tasks_completed_at();

-- Comments
COMMENT ON TABLE clinical.patient_tasks IS 'Patient-centric clinical task tracking (Phase 1: MVP feature set)';
COMMENT ON COLUMN clinical.patient_tasks.patient_key IS 'Patient ICN (e.g., ICN100001). Tasks belong to patient, visible to all clinicians.';
COMMENT ON COLUMN clinical.patient_tasks.created_by_user_id IS 'User who created task (audit trail). Used for "My Tasks" filter.';
COMMENT ON COLUMN clinical.patient_tasks.is_ai_generated IS 'TRUE if task created via AI Insights chatbot "Add to Tasks" button';
```

### 4.2 Sample Data

**Example Tasks:**

```sql
-- Task 1: User-created, high priority, in progress
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Review discharge summary from recent CHF admission',
    'Patient was discharged 2 days ago from Alexandria VAMC. Need to review discharge meds and follow-up plan.',
    'HIGH',
    'IN_PROGRESS',
    '11111111-1111-1111-1111-111111111111',  -- Clinician Alpha UUID
    'Dr. Alpha',
    FALSE,
    NOW() - INTERVAL '1 day'
);

-- Task 2: AI-generated, medium priority, todo
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100001',
    'Patient overdue for A1C screening',
    'Last A1C: 8.2% on 2025-06-15 (8 months ago). Current diabetes guidelines recommend A1C every 6 months for uncontrolled diabetes.',
    'MEDIUM',
    'TODO',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    TRUE,
    'AI Insights suggested based on diabetes diagnosis and lab history',
    NOW() - INTERVAL '2 hours'
);

-- Task 3: Low priority, completed
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    completed_by_user_id, completed_by_display_name,
    completed_at, created_at
) VALUES (
    'ICN100001',
    'Update patient education materials',
    'Provide patient with CHF self-management handout.',
    'LOW',
    'COMPLETED',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    '22222222-2222-2222-2222-222222222222',  -- Clinician Beta UUID
    'Dr. Beta',
    NOW() - INTERVAL '3 hours',
    NOW() - INTERVAL '1 week'
);
```

### 4.3 Audit Trail Pattern

**Audit Fields:**

| Field | Purpose | Populated When |
|-------|---------|----------------|
| `created_by_user_id` | Track who created task | Task creation (always) |
| `created_by_display_name` | User-friendly name | Task creation (denormalized from `auth.users`) |
| `created_at` | When task created | Task creation (auto) |
| `updated_at` | Last modification time | Any UPDATE (trigger auto-updates) |
| `completed_by_user_id` | Who completed task | Status → COMPLETED |
| `completed_by_display_name` | User-friendly name | Status → COMPLETED (denormalized) |
| `completed_at` | When completed | Status → COMPLETED (trigger auto-populates) |
| `is_ai_generated` | AI vs. user-created | Task creation (TRUE if from AI chatbot) |
| `ai_suggestion_source` | AI reasoning | AI task creation (free text explanation) |

**Phase 2+ Enhancements:**

Separate `clinical.patient_task_audit_log` table:
- Track all status changes (TODO → IN_PROGRESS → COMPLETED)
- Track priority changes (LOW → HIGH escalation)
- Track title/description edits
- Full audit trail for compliance and analytics

### 4.4 Schema Evolution

**Phase 1 (Current):**
- Single table: `clinical.patient_tasks`
- Core fields: title, description, priority, status, audit fields
- No task categories, due dates, assignments

**Phase 2+ Extensions:**

```sql
-- Phase 2: Due dates and categories
ALTER TABLE clinical.patient_tasks
ADD COLUMN due_date TIMESTAMP WITH TIME ZONE,
ADD COLUMN category VARCHAR(50),  -- LAB_REVIEW, MEDICATION, FOLLOWUP, CONSULT
ADD COLUMN is_overdue BOOLEAN GENERATED ALWAYS AS (
    due_date IS NOT NULL AND due_date < NOW() AND status != 'COMPLETED'
) STORED;

-- Phase 3: Task assignment
ALTER TABLE clinical.patient_tasks
ADD COLUMN assigned_to_user_id UUID REFERENCES auth.users(user_id),
ADD COLUMN assigned_to_display_name VARCHAR(255),
ADD COLUMN assigned_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN assigned_by_user_id UUID REFERENCES auth.users(user_id);

-- Phase 4: Clinical data links
CREATE TABLE clinical.patient_task_links (
    task_link_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES clinical.patient_tasks(task_id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL,  -- LAB_RESULT, MEDICATION, CLINICAL_NOTE, VITAL_SIGN
    link_id VARCHAR(100) NOT NULL,   -- Foreign key to clinical domain table
    link_display_text VARCHAR(500),  -- User-friendly description
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Phase 5: Task comments/discussion
CREATE TABLE clinical.patient_task_comments (
    comment_id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES clinical.patient_tasks(task_id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(user_id),
    user_display_name VARCHAR(255),
    comment_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

---

## 5. UI Design

### 5.1 Dashboard Widget (2x1 Grid)

**Placement:** To the right of Demographics widget (may require dashboard grid reflow)

**Widget Specification:**

```html
<!-- File: app/templates/partials/tasks_widget.html -->

<div class="widget widget--2x1" id="widget-tasks"
     hx-get="/api/patient/dashboard/widget/tasks/{{ patient.icn }}"
     hx-trigger="load, taskUpdated from:body"
     hx-swap="innerHTML">

    <!-- Header -->
    <div class="widget__header">
        <i class="widget__icon fa-solid fa-tasks"></i>
        <h3 class="widget__title">My Active Tasks</h3>
        <span class="widget__badge" id="task-count-badge">{{ task_count }}</span>
        <button class="widget__action-btn"
                hx-get="/api/patient/tasks/quick-create-modal?icn={{ patient.icn }}"
                hx-target="#modal-container"
                hx-swap="innerHTML"
                title="Quick Create Task">
            <i class="fa-solid fa-plus"></i>
        </button>
    </div>

    <!-- Body: Scrollable task list -->
    <div class="widget__body" style="max-height: 220px; overflow-y: auto;">
        {% if tasks|length == 0 %}
            <div class="widget__empty-state">
                <i class="fa-regular fa-clipboard"></i>
                <p>No active tasks for this patient</p>
                <button class="btn btn--sm btn--secondary"
                        hx-get="/api/patient/tasks/quick-create-modal?icn={{ patient.icn }}"
                        hx-target="#modal-container"
                        hx-swap="innerHTML">
                    Create First Task
                </button>
            </div>
        {% else %}
            {% for task in tasks %}
            <div class="task-item task-item--{{ task.priority|lower }}"
                 id="task-{{ task.task_id }}">

                <!-- Priority indicator -->
                <span class="task-item__priority-badge task-item__priority-badge--{{ task.priority|lower }}">
                    {{ task.priority }}
                </span>

                <!-- Task title -->
                <div class="task-item__title">{{ task.title }}</div>

                <!-- Status badge -->
                <span class="task-item__status-badge task-item__status-badge--{{ task.status|lower }}">
                    {% if task.status == 'TODO' %}
                        <i class="fa-regular fa-circle"></i>
                    {% elif task.status == 'IN_PROGRESS' %}
                        <i class="fa-solid fa-spinner fa-spin"></i>
                    {% endif %}
                    {{ task.status|replace('_', ' ') }}
                </span>

                <!-- Quick actions -->
                <div class="task-item__actions">
                    {% if task.status == 'TODO' %}
                        <button class="btn btn--xs btn--primary"
                                hx-post="/api/patient/tasks/{{ task.task_id }}/start"
                                hx-target="#task-{{ task.task_id }}"
                                hx-swap="outerHTML"
                                title="Start Task">
                            <i class="fa-solid fa-play"></i>
                        </button>
                    {% elif task.status == 'IN_PROGRESS' %}
                        <button class="btn btn--xs btn--success"
                                hx-post="/api/patient/tasks/{{ task.task_id }}/complete"
                                hx-target="#task-{{ task.task_id }}"
                                hx-swap="outerHTML"
                                title="Complete Task">
                            <i class="fa-solid fa-check"></i>
                        </button>
                    {% endif %}
                    <button class="btn btn--xs btn--secondary"
                            hx-get="/api/patient/tasks/{{ task.task_id }}/edit-modal"
                            hx-target="#modal-container"
                            hx-swap="innerHTML"
                            title="Edit Task">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                </div>
            </div>
            {% endfor %}
        {% endif %}
    </div>

    <!-- Footer: View all link -->
    <div class="widget__footer">
        <a href="/patient/{{ patient.icn }}/tasks" class="widget__footer-link">
            View All Tasks →
        </a>
    </div>
</div>
```

**Widget Features:**

- **Task count badge:** Shows number of active tasks (TODO + IN_PROGRESS)
- **Quick create button:** Opens modal without leaving dashboard
- **Priority indicators:** Color-coded badges (red=high, yellow=medium, gray=low)
- **Inline actions:** Start, complete, edit buttons (HTMX-powered)
- **Scrollable body:** Max 5-8 tasks visible, scroll for more
- **Empty state:** Friendly message + "Create First Task" CTA

**CSS Classes (to be added to `app/static/styles.css`):**

```css
/* Task Widget Styles */
.task-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem;
    border-bottom: 1px solid #e5e7eb;
    transition: background-color 0.2s;
}

.task-item:hover {
    background-color: #f9fafb;
}

.task-item--high {
    border-left: 3px solid #dc2626; /* Red */
}

.task-item--medium {
    border-left: 3px solid #f59e0b; /* Yellow */
}

.task-item--low {
    border-left: 3px solid #6b7280; /* Gray */
}

.task-item__priority-badge {
    font-size: 0.625rem;
    font-weight: 600;
    padding: 0.125rem 0.375rem;
    border-radius: 0.25rem;
    text-transform: uppercase;
}

.task-item__priority-badge--high {
    background-color: #fee2e2;
    color: #dc2626;
}

.task-item__priority-badge--medium {
    background-color: #fef3c7;
    color: #f59e0b;
}

.task-item__priority-badge--low {
    background-color: #f3f4f6;
    color: #6b7280;
}

.task-item__title {
    flex: 1;
    font-size: 0.875rem;
    color: #111827;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.task-item__status-badge {
    font-size: 0.75rem;
    color: #6b7280;
    display: flex;
    align-items: center;
    gap: 0.25rem;
}

.task-item__actions {
    display: flex;
    gap: 0.25rem;
}
```

### 5.2 Sidebar Navigation

**Update:** `app/templates/base.html`

```html
<!-- Existing sidebar navigation -->
<nav class="sidebar__nav">
    <ul class="nav-list">
        <li class="nav-item">
            <a href="/dashboard" class="nav-link {% if request.url.path == '/dashboard' %}nav-link--active{% endif %}">
                <i class="fa-solid fa-table-columns"></i>
                <span>Dashboard</span>
            </a>
        </li>
        <li class="nav-item">
            <a href="#" class="nav-link" id="nav-demographics">
                <i class="fa-solid fa-user"></i>
                <span>Demographics</span>
            </a>
        </li>

        <!-- NEW: Tasks navigation item -->
        <li class="nav-item">
            <a href="/tasks" class="nav-link {% if request.url.path.startswith('/patient/') and 'tasks' in request.url.path %}nav-link--active{% endif %}"
               id="nav-tasks">
                <i class="fa-solid fa-tasks"></i>
                <span>Tasks</span>
                <span class="nav-badge" id="nav-tasks-badge" style="display: none;">0</span>
            </a>
        </li>
        <!-- END NEW -->

        <li class="nav-item">
            <a href="#" class="nav-link" id="nav-vitals">
                <i class="fa-solid fa-heartbeat"></i>
                <span>Vitals</span>
            </a>
        </li>
        <!-- ... rest of nav items ... -->
    </ul>
</nav>
```

**Badge Updates:**

Add JavaScript to update task count badge dynamically:

```javascript
// File: app/static/app.js (add to existing)

// Update task count badge in sidebar
document.body.addEventListener('taskUpdated', function(event) {
    const badge = document.getElementById('nav-tasks-badge');
    if (badge) {
        const count = event.detail.activeTaskCount || 0;
        if (count > 0) {
            badge.textContent = count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
});
```

### 5.3 Full Page View

**File:** `app/templates/patient_tasks.html`

**Page Structure:**

```html
{% extends "base.html" %}

{% block title %}Tasks - {{ patient.name }}{% endblock %}

{% block content %}
<div class="page-container">

    <!-- Page Header -->
    <div class="page-header">
        <div class="page-header__title">
            <i class="fa-solid fa-tasks"></i>
            <h1>Clinical Tasks</h1>
        </div>
        <div class="page-header__actions">
            <button class="btn btn--primary"
                    hx-get="/api/patient/tasks/quick-create-modal?icn={{ patient.icn }}"
                    hx-target="#modal-container"
                    hx-swap="innerHTML">
                <i class="fa-solid fa-plus"></i> New Task
            </button>
        </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
        <div class="filter-group">
            <label for="filter-status">Status</label>
            <select id="filter-status" name="status"
                    hx-get="/patient/{{ patient.icn }}/tasks/filtered"
                    hx-target="#tasks-content"
                    hx-include="[name='created_by'], [name='priority']"
                    hx-trigger="change">
                <option value="active" selected>Active (TODO + In Progress)</option>
                <option value="TODO">Todo</option>
                <option value="IN_PROGRESS">In Progress</option>
                <option value="COMPLETED">Completed</option>
                <option value="all">All</option>
            </select>
        </div>

        <div class="filter-group">
            <label for="filter-created-by">Created By</label>
            <select id="filter-created-by" name="created_by"
                    hx-get="/patient/{{ patient.icn }}/tasks/filtered"
                    hx-target="#tasks-content"
                    hx-include="[name='status'], [name='priority']"
                    hx-trigger="change">
                <option value="all" selected>All Clinicians</option>
                <option value="me">My Tasks</option>
            </select>
        </div>

        <div class="filter-group">
            <label for="filter-priority">Priority</label>
            <select id="filter-priority" name="priority"
                    hx-get="/patient/{{ patient.icn }}/tasks/filtered"
                    hx-target="#tasks-content"
                    hx-include="[name='status'], [name='created_by']"
                    hx-trigger="change">
                <option value="all" selected>All Priorities</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
            </select>
        </div>

        <button class="btn btn--secondary btn--sm"
                hx-get="/patient/{{ patient.icn }}/tasks"
                hx-target="#tasks-content"
                hx-swap="innerHTML">
            <i class="fa-solid fa-rotate-right"></i> Refresh
        </button>
    </div>

    <!-- Task Summary Cards -->
    <div class="summary-cards">
        <div class="summary-card">
            <div class="summary-card__value">{{ summary.todo_count }}</div>
            <div class="summary-card__label">To Do</div>
        </div>
        <div class="summary-card">
            <div class="summary-card__value">{{ summary.in_progress_count }}</div>
            <div class="summary-card__label">In Progress</div>
        </div>
        <div class="summary-card">
            <div class="summary-card__value">{{ summary.completed_today_count }}</div>
            <div class="summary-card__label">Completed Today</div>
        </div>
        <div class="summary-card">
            <div class="summary-card__value">{{ summary.ai_generated_count }}</div>
            <div class="summary-card__label">AI Suggested</div>
        </div>
    </div>

    <!-- Task List -->
    <div id="tasks-content">
        {% if tasks|length == 0 %}
            <div class="empty-state">
                <i class="fa-regular fa-clipboard fa-3x"></i>
                <p>No tasks match your filters</p>
                <button class="btn btn--primary"
                        hx-get="/api/patient/tasks/quick-create-modal?icn={{ patient.icn }}"
                        hx-target="#modal-container"
                        hx-swap="innerHTML">
                    Create First Task
                </button>
            </div>
        {% else %}
            <!-- Grouped by Priority -->
            {% if high_priority_tasks|length > 0 %}
            <div class="task-group">
                <h2 class="task-group__header task-group__header--high">
                    <i class="fa-solid fa-exclamation-circle"></i>
                    High Priority ({{ high_priority_tasks|length }})
                </h2>
                <div class="task-group__items">
                    {% for task in high_priority_tasks %}
                        {% include "partials/task_card.html" %}
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if medium_priority_tasks|length > 0 %}
            <div class="task-group">
                <h2 class="task-group__header task-group__header--medium">
                    <i class="fa-solid fa-info-circle"></i>
                    Medium Priority ({{ medium_priority_tasks|length }})
                </h2>
                <div class="task-group__items">
                    {% for task in medium_priority_tasks %}
                        {% include "partials/task_card.html" %}
                    {% endfor %}
                </div>
            </div>
            {% endif %}

            {% if low_priority_tasks|length > 0 %}
            <div class="task-group">
                <h2 class="task-group__header task-group__header--low">
                    <i class="fa-solid fa-circle"></i>
                    Low Priority ({{ low_priority_tasks|length }})
                </h2>
                <div class="task-group__items">
                    {% for task in low_priority_tasks %}
                        {% include "partials/task_card.html" %}
                    {% endfor %}
                </div>
            </div>
            {% endif %}
        {% endif %}
    </div>

</div>

<!-- Modal Container -->
<div id="modal-container"></div>

{% endblock %}
```

**Task Card Partial:** `app/templates/partials/task_card.html`

```html
<div class="task-card task-card--{{ task.priority|lower }}" id="task-card-{{ task.task_id }}">

    <!-- Header -->
    <div class="task-card__header">
        <div class="task-card__title-row">
            <h3 class="task-card__title">{{ task.title }}</h3>
            <span class="task-card__status task-card__status--{{ task.status|lower }}">
                {% if task.status == 'TODO' %}
                    <i class="fa-regular fa-circle"></i> To Do
                {% elif task.status == 'IN_PROGRESS' %}
                    <i class="fa-solid fa-spinner fa-spin"></i> In Progress
                {% elif task.status == 'COMPLETED' %}
                    <i class="fa-solid fa-check-circle"></i> Completed
                {% endif %}
            </span>
        </div>
    </div>

    <!-- Description -->
    {% if task.description %}
    <div class="task-card__description">
        {{ task.description }}
    </div>
    {% endif %}

    <!-- Metadata -->
    <div class="task-card__metadata">
        <div class="metadata-item">
            <i class="fa-solid fa-user"></i>
            <span>Created by {{ task.created_by_display_name }}</span>
        </div>
        <div class="metadata-item">
            <i class="fa-solid fa-clock"></i>
            <span>{{ task.created_at|format_datetime }}</span>
        </div>
        {% if task.is_ai_generated %}
        <div class="metadata-item metadata-item--ai">
            <i class="fa-solid fa-robot"></i>
            <span>AI Suggested</span>
            {% if task.ai_suggestion_source %}
            <span class="metadata-item__tooltip">{{ task.ai_suggestion_source }}</span>
            {% endif %}
        </div>
        {% endif %}
        {% if task.completed_at %}
        <div class="metadata-item">
            <i class="fa-solid fa-check"></i>
            <span>Completed by {{ task.completed_by_display_name }} on {{ task.completed_at|format_datetime }}</span>
        </div>
        {% endif %}
    </div>

    <!-- Actions -->
    <div class="task-card__actions">
        {% if task.status == 'TODO' %}
            <button class="btn btn--sm btn--primary"
                    hx-post="/api/patient/tasks/{{ task.task_id }}/start"
                    hx-target="#task-card-{{ task.task_id }}"
                    hx-swap="outerHTML">
                <i class="fa-solid fa-play"></i> Start Task
            </button>
            <button class="btn btn--sm btn--success"
                    hx-post="/api/patient/tasks/{{ task.task_id }}/complete"
                    hx-target="#task-card-{{ task.task_id }}"
                    hx-swap="outerHTML"
                    hx-confirm="Are you sure you want to mark this task as complete?">
                <i class="fa-solid fa-check"></i> Complete
            </button>
        {% elif task.status == 'IN_PROGRESS' %}
            <button class="btn btn--sm btn--success"
                    hx-post="/api/patient/tasks/{{ task.task_id }}/complete"
                    hx-target="#task-card-{{ task.task_id }}"
                    hx-swap="outerHTML"
                    hx-confirm="Are you sure you want to mark this task as complete?">
                <i class="fa-solid fa-check"></i> Complete
            </button>
            <button class="btn btn--sm btn--secondary"
                    hx-post="/api/patient/tasks/{{ task.task_id }}/revert-to-todo"
                    hx-target="#task-card-{{ task.task_id }}"
                    hx-swap="outerHTML">
                <i class="fa-solid fa-rotate-left"></i> Revert to To Do
            </button>
        {% endif %}

        <button class="btn btn--sm btn--secondary"
                hx-get="/api/patient/tasks/{{ task.task_id }}/edit-modal"
                hx-target="#modal-container"
                hx-swap="innerHTML">
            <i class="fa-solid fa-pen"></i> Edit
        </button>

        {% if task.status != 'COMPLETED' %}
        <button class="btn btn--sm btn--danger"
                hx-delete="/api/patient/tasks/{{ task.task_id }}"
                hx-target="#task-card-{{ task.task_id }}"
                hx-swap="outerHTML"
                hx-confirm="Are you sure you want to delete this task?">
            <i class="fa-solid fa-trash"></i> Delete
        </button>
        {% endif %}
    </div>

</div>
```

### 5.4 Quick Create Modal

**File:** `app/templates/modals/task_create_modal.html`

```html
<div class="modal modal--active" id="task-create-modal">
    <div class="modal__overlay" onclick="closeModal()"></div>
    <div class="modal__content modal__content--medium">

        <!-- Modal Header -->
        <div class="modal__header">
            <h2 class="modal__title">
                <i class="fa-solid fa-plus-circle"></i>
                Create New Task
            </h2>
            <button class="modal__close" onclick="closeModal()">
                <i class="fa-solid fa-times"></i>
            </button>
        </div>

        <!-- Modal Body -->
        <div class="modal__body">
            <form id="task-create-form"
                  hx-post="/api/patient/{{ patient_icn }}/tasks"
                  hx-target="#widget-tasks"
                  hx-swap="outerHTML"
                  hx-on::after-request="closeModal(); htmx.trigger(body, 'taskUpdated')">

                <!-- Title -->
                <div class="form-group">
                    <label for="task-title" class="form-label required">Task Title</label>
                    <input type="text"
                           id="task-title"
                           name="title"
                           class="form-input"
                           placeholder="Brief description of task"
                           required
                           maxlength="500"
                           value="{{ prefilled_title | default('') }}">
                    <small class="form-help">Max 500 characters</small>
                </div>

                <!-- Description -->
                <div class="form-group">
                    <label for="task-description" class="form-label">Description (Optional)</label>
                    <textarea id="task-description"
                              name="description"
                              class="form-textarea"
                              rows="4"
                              placeholder="Additional details or context">{{ prefilled_description | default('') }}</textarea>
                </div>

                <!-- Priority -->
                <div class="form-group">
                    <label for="task-priority" class="form-label">Priority</label>
                    <select id="task-priority" name="priority" class="form-select">
                        <option value="HIGH" {% if prefilled_priority == 'HIGH' %}selected{% endif %}>High</option>
                        <option value="MEDIUM" {% if prefilled_priority == 'MEDIUM' or not prefilled_priority %}selected{% endif %}>Medium</option>
                        <option value="LOW" {% if prefilled_priority == 'LOW' %}selected{% endif %}>Low</option>
                    </select>
                </div>

                <!-- AI Generated Indicator (hidden input) -->
                {% if is_ai_generated %}
                <input type="hidden" name="is_ai_generated" value="true">
                <input type="hidden" name="ai_suggestion_source" value="{{ ai_suggestion_source }}">

                <div class="alert alert--info">
                    <i class="fa-solid fa-robot"></i>
                    <div>
                        <strong>AI-Suggested Task</strong>
                        <p>{{ ai_suggestion_source }}</p>
                    </div>
                </div>
                {% endif %}

                <!-- Actions -->
                <div class="modal__actions">
                    <button type="button" class="btn btn--secondary" onclick="closeModal()">
                        Cancel
                    </button>
                    <button type="submit" class="btn btn--primary">
                        <i class="fa-solid fa-save"></i> Create Task
                    </button>
                </div>

            </form>
        </div>

    </div>
</div>

<script>
function closeModal() {
    document.getElementById('task-create-modal').remove();
}
</script>
```

### 5.5 Responsive Design

**Breakpoints:**

- **Desktop (≥1024px):** Dashboard widget 2x1 grid, full page 2-column card layout
- **Tablet (768px - 1023px):** Dashboard widget stacks to 1 column, full page 1-column cards
- **Mobile (<768px):** All components stack vertically, simplified task cards

---

## 6. API Endpoints

### 6.1 Routing Pattern: Pattern B (Dedicated Router)

**Rationale:** Task tracking requires:
- Multiple API endpoints (CRUD operations)
- Full page views with complex filtering
- Widget rendering
- Modal rendering

This complexity warrants a dedicated router following the pattern established by Vitals, Problems, and Medications domains.

**File:** `app/routes/tasks.py`

### 6.2 API Router Endpoints (JSON + HTML Widgets)

**Prefix:** `/api/patient`
**Tags:** `["tasks"]`

```python
# File: app/routes/tasks.py

from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from app.db import patient_tasks
from app.utils.ccow_client import ccow_client
from app.templates import templates

router = APIRouter(prefix="/api/patient", tags=["tasks"])

# ----------------------------------------------------------------------------
# 1. Dashboard Widget Endpoint
# ----------------------------------------------------------------------------
@router.get("/dashboard/widget/tasks/{icn}", response_class=HTMLResponse)
async def get_tasks_widget(request: Request, icn: str):
    """
    Render task widget for dashboard (2x1 grid).
    Shows 5-8 most urgent tasks (TODO + IN_PROGRESS only).
    Sorted by: Priority (HIGH > MEDIUM > LOW) → Created date (newest first)
    """
    user = request.state.user

    # Get active tasks for patient
    tasks = patient_tasks.get_patient_tasks(
        patient_icn=icn,
        status="active",  # TODO + IN_PROGRESS
        limit=8
    )

    # Get task count for badge
    task_count = len(tasks)

    # Get patient info for context
    from app.db import patient
    patient_info = patient.get_patient_by_icn(icn)

    return templates.TemplateResponse(
        "partials/tasks_widget.html",
        {
            "request": request,
            "patient": patient_info,
            "tasks": tasks,
            "task_count": task_count
        }
    )


# ----------------------------------------------------------------------------
# 2. Get All Tasks for Patient (JSON API)
# ----------------------------------------------------------------------------
@router.get("/{icn}/tasks")
async def get_patient_tasks_api(
    request: Request,
    icn: str,
    status: Optional[str] = "active",  # active, TODO, IN_PROGRESS, COMPLETED, all
    created_by: Optional[str] = "all",  # all, me
    priority: Optional[str] = "all"     # all, HIGH, MEDIUM, LOW
):
    """
    Get all tasks for a patient with optional filtering.
    Returns JSON for API consumers.
    """
    user = request.state.user
    user_id = user["user_id"] if created_by == "me" else None

    tasks = patient_tasks.get_patient_tasks(
        patient_icn=icn,
        status=status if status != "all" else None,
        created_by_user_id=user_id,
        priority=priority if priority != "all" else None
    )

    return {"tasks": tasks, "count": len(tasks)}


# ----------------------------------------------------------------------------
# 3. Create New Task
# ----------------------------------------------------------------------------
@router.post("/{icn}/tasks", response_class=HTMLResponse)
async def create_task(request: Request, icn: str):
    """
    Create new task for patient.
    Returns updated widget HTML (for HTMX swap).
    """
    user = request.state.user
    form_data = await request.form()

    # Validate required fields
    title = form_data.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Task title is required")

    # Create task
    task_id = patient_tasks.create_task(
        patient_icn=icn,
        title=title,
        description=form_data.get("description"),
        priority=form_data.get("priority", "MEDIUM"),
        created_by_user_id=user["user_id"],
        created_by_display_name=user["display_name"],
        is_ai_generated=form_data.get("is_ai_generated") == "true",
        ai_suggestion_source=form_data.get("ai_suggestion_source")
    )

    # Return updated widget
    return await get_tasks_widget(request, icn)


# ----------------------------------------------------------------------------
# 4. Update Task Status (Start, Complete, Revert)
# ----------------------------------------------------------------------------
@router.post("/tasks/{task_id}/start", response_class=HTMLResponse)
async def start_task(request: Request, task_id: int):
    """
    Update task status: TODO → IN_PROGRESS.
    Returns updated task card HTML.
    """
    user = request.state.user

    # Update status
    patient_tasks.update_task_status(task_id, "IN_PROGRESS")

    # Get updated task
    task = patient_tasks.get_task_by_id(task_id)

    # Return updated card
    return templates.TemplateResponse(
        "partials/task_card.html",
        {"request": request, "task": task}
    )


@router.post("/tasks/{task_id}/complete", response_class=HTMLResponse)
async def complete_task(request: Request, task_id: int):
    """
    Update task status: IN_PROGRESS (or TODO) → COMPLETED.
    Records completed_by_user_id and completed_at.
    Returns updated task card HTML.
    """
    user = request.state.user

    # Update status and completion fields
    patient_tasks.complete_task(
        task_id=task_id,
        completed_by_user_id=user["user_id"],
        completed_by_display_name=user["display_name"]
    )

    # Get updated task
    task = patient_tasks.get_task_by_id(task_id)

    # Return updated card
    return templates.TemplateResponse(
        "partials/task_card.html",
        {"request": request, "task": task}
    )


@router.post("/tasks/{task_id}/revert-to-todo", response_class=HTMLResponse)
async def revert_task_to_todo(request: Request, task_id: int):
    """
    Update task status: IN_PROGRESS → TODO.
    Returns updated task card HTML.
    """
    user = request.state.user

    # Update status
    patient_tasks.update_task_status(task_id, "TODO")

    # Get updated task
    task = patient_tasks.get_task_by_id(task_id)

    # Return updated card
    return templates.TemplateResponse(
        "partials/task_card.html",
        {"request": request, "task": task}
    )


# ----------------------------------------------------------------------------
# 5. Update Task Details (Title, Description, Priority)
# ----------------------------------------------------------------------------
@router.put("/tasks/{task_id}")
async def update_task(request: Request, task_id: int):
    """
    Update task details (title, description, priority).
    Returns JSON response.
    """
    user = request.state.user
    form_data = await request.form()

    # Update task
    patient_tasks.update_task(
        task_id=task_id,
        title=form_data.get("title"),
        description=form_data.get("description"),
        priority=form_data.get("priority")
    )

    # Return updated task
    task = patient_tasks.get_task_by_id(task_id)
    return {"task": task}


# ----------------------------------------------------------------------------
# 6. Delete Task
# ----------------------------------------------------------------------------
@router.delete("/tasks/{task_id}", response_class=HTMLResponse)
async def delete_task(request: Request, task_id: int):
    """
    Delete task (hard delete from database).
    Returns empty string (HTMX removes element).
    """
    user = request.state.user

    # Delete task
    patient_tasks.delete_task(task_id)

    # Return empty (HTMX removes card from DOM)
    return ""


# ----------------------------------------------------------------------------
# 7. Quick Create Modal Endpoint
# ----------------------------------------------------------------------------
@router.get("/tasks/quick-create-modal", response_class=HTMLResponse)
async def get_quick_create_modal(
    request: Request,
    icn: str,
    prefilled_title: Optional[str] = None,
    prefilled_description: Optional[str] = None,
    prefilled_priority: Optional[str] = None,
    is_ai_generated: bool = False,
    ai_suggestion_source: Optional[str] = None
):
    """
    Render quick create modal (for HTMX modal container).
    Supports pre-filling for AI-suggested tasks.
    """
    return templates.TemplateResponse(
        "modals/task_create_modal.html",
        {
            "request": request,
            "patient_icn": icn,
            "prefilled_title": prefilled_title,
            "prefilled_description": prefilled_description,
            "prefilled_priority": prefilled_priority,
            "is_ai_generated": is_ai_generated,
            "ai_suggestion_source": ai_suggestion_source
        }
    )


# ----------------------------------------------------------------------------
# 8. Task Edit Modal Endpoint
# ----------------------------------------------------------------------------
@router.get("/tasks/{task_id}/edit-modal", response_class=HTMLResponse)
async def get_task_edit_modal(request: Request, task_id: int):
    """
    Render task edit modal with existing task data.
    """
    task = patient_tasks.get_task_by_id(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return templates.TemplateResponse(
        "modals/task_edit_modal.html",
        {
            "request": request,
            "task": task
        }
    )
```

### 6.3 Page Router Endpoints (Full HTML Pages)

**No Prefix**
**Tags:** `["tasks-pages"]`

```python
# File: app/routes/tasks.py (continued)

page_router = APIRouter(tags=["tasks-pages"])

# ----------------------------------------------------------------------------
# 1. CCOW Redirect (Sidebar Nav Click)
# ----------------------------------------------------------------------------
@page_router.get("/tasks", response_class=HTMLResponse)
async def tasks_ccow_redirect(request: Request):
    """
    Redirect to patient-specific tasks page using CCOW active patient.
    Called when user clicks "Tasks" in sidebar nav.
    """
    # Get active patient from CCOW
    patient_icn = ccow_client.get_active_patient(request)

    if not patient_icn:
        # No patient selected, show error or redirect to dashboard
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": "No patient selected. Please search and select a patient first."
            }
        )

    # Redirect to patient-specific tasks page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/patient/{patient_icn}/tasks", status_code=303)


# ----------------------------------------------------------------------------
# 2. Full Tasks Page
# ----------------------------------------------------------------------------
@page_router.get("/patient/{icn}/tasks", response_class=HTMLResponse)
async def get_tasks_page(
    request: Request,
    icn: str,
    status: Optional[str] = "active",
    created_by: Optional[str] = "all",
    priority: Optional[str] = "all"
):
    """
    Render full tasks page with filtering.
    """
    user = request.state.user

    # Get patient info
    from app.db import patient
    patient_info = patient.get_patient_by_icn(icn)

    if not patient_info:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Get tasks with filters
    user_id = user["user_id"] if created_by == "me" else None
    tasks = patient_tasks.get_patient_tasks(
        patient_icn=icn,
        status=status if status != "all" else None,
        created_by_user_id=user_id,
        priority=priority if priority != "all" else None
    )

    # Group tasks by priority
    high_priority = [t for t in tasks if t["priority"] == "HIGH"]
    medium_priority = [t for t in tasks if t["priority"] == "MEDIUM"]
    low_priority = [t for t in tasks if t["priority"] == "LOW"]

    # Get summary stats
    summary = patient_tasks.get_task_summary(icn)

    return templates.TemplateResponse(
        "patient_tasks.html",
        {
            "request": request,
            "patient": patient_info,
            "tasks": tasks,
            "high_priority_tasks": high_priority,
            "medium_priority_tasks": medium_priority,
            "low_priority_tasks": low_priority,
            "summary": summary,
            "active_filters": {
                "status": status,
                "created_by": created_by,
                "priority": priority
            }
        }
    )


# ----------------------------------------------------------------------------
# 3. Filtered Tasks Partial (HTMX Target)
# ----------------------------------------------------------------------------
@page_router.get("/patient/{icn}/tasks/filtered", response_class=HTMLResponse)
async def get_filtered_tasks(
    request: Request,
    icn: str,
    status: Optional[str] = "active",
    created_by: Optional[str] = "all",
    priority: Optional[str] = "all"
):
    """
    Render filtered tasks partial (for HTMX swap into #tasks-content).
    """
    user = request.state.user

    # Get tasks with filters
    user_id = user["user_id"] if created_by == "me" else None
    tasks = patient_tasks.get_patient_tasks(
        patient_icn=icn,
        status=status if status != "all" else None,
        created_by_user_id=user_id,
        priority=priority if priority != "all" else None
    )

    # Group tasks by priority
    high_priority = [t for t in tasks if t["priority"] == "HIGH"]
    medium_priority = [t for t in tasks if t["priority"] == "MEDIUM"]
    low_priority = [t for t in tasks if t["priority"] == "LOW"]

    return templates.TemplateResponse(
        "partials/tasks_list.html",
        {
            "request": request,
            "tasks": tasks,
            "high_priority_tasks": high_priority,
            "medium_priority_tasks": medium_priority,
            "low_priority_tasks": low_priority
        }
    )
```

### 6.4 Router Registration

**File:** `app/main.py`

```python
# Add to existing router registrations
from app.routes import tasks

app.include_router(tasks.router)        # API routes
app.include_router(tasks.page_router)   # Full pages
```

---

## 7. AI Integration

### 7.1 AI Tool: `suggest_patient_tasks()`

**Purpose:** Analyze patient data and suggest clinical action items

**File:** `ai/tools/task_tools.py`

```python
from langchain.tools import tool
from typing import List, Dict
from app.db import patient_problems, patient_medications, patient_labs, patient_vitals
import datetime

@tool
def suggest_patient_tasks(patient_icn: str) -> str:
    """
    Analyze patient clinical data and suggest actionable tasks.

    Returns markdown-formatted list of suggested tasks with:
    - Task title
    - Clinical rationale
    - Priority level
    - "Add to Tasks" button markup

    Args:
        patient_icn: Patient ICN (e.g., "ICN100001")

    Returns:
        Markdown string with suggested tasks and HTMX button markup
    """
    suggestions = []

    # -------------------------------------------------------------------------
    # 1. Check for overdue screenings (diabetes A1C)
    # -------------------------------------------------------------------------
    problems = patient_problems.get_patient_problems(patient_icn, status="Active")
    has_diabetes = any("diabetes" in p.get("problem_name", "").lower() for p in problems)

    if has_diabetes:
        # Check last A1C date
        labs = patient_labs.get_patient_labs(patient_icn, test_name="Hemoglobin A1c", days=180)
        if not labs:
            suggestions.append({
                "title": "Patient overdue for A1C screening",
                "description": "Patient has active diabetes diagnosis but no A1C test in past 6 months. Current guidelines recommend A1C every 6 months for uncontrolled diabetes.",
                "priority": "MEDIUM",
                "rationale": "Diabetes diagnosis + no recent A1C"
            })

    # -------------------------------------------------------------------------
    # 2. Check for medication-lab monitoring (warfarin → INR)
    # -------------------------------------------------------------------------
    meds = patient_medications.get_patient_medications(patient_icn, status="Active")
    on_warfarin = any("warfarin" in m.get("drug_name", "").lower() for m in meds)

    if on_warfarin:
        # Check last INR date
        inr_labs = patient_labs.get_patient_labs(patient_icn, test_name="INR", days=30)
        if not inr_labs:
            suggestions.append({
                "title": "INR monitoring needed for warfarin",
                "description": "Patient on warfarin but no INR test in past 30 days. Warfarin requires regular INR monitoring to prevent bleeding/clotting complications.",
                "priority": "HIGH",
                "rationale": "Active warfarin prescription + no recent INR"
            })

    # -------------------------------------------------------------------------
    # 3. Check for recent hospital discharge (follow-up needed)
    # -------------------------------------------------------------------------
    from app.db import patient_encounters
    encounters = patient_encounters.get_patient_encounters(patient_icn, days=14)
    recent_discharge = any(e.get("encounter_type") == "Inpatient" for e in encounters)

    if recent_discharge:
        suggestions.append({
            "title": "Review discharge summary from recent hospitalization",
            "description": "Patient discharged from inpatient stay within past 14 days. Review discharge medications, follow-up appointments, and care plan.",
            "priority": "HIGH",
            "rationale": "Recent inpatient discharge (14 days)"
        })

    # -------------------------------------------------------------------------
    # 4. Check for critical vitals (hypertension)
    # -------------------------------------------------------------------------
    vitals = patient_vitals.get_patient_vitals(patient_icn, days=7)
    critical_bp = any(
        v.get("systolic_bp", 0) > 180 or v.get("diastolic_bp", 0) > 120
        for v in vitals
    )

    if critical_bp:
        suggestions.append({
            "title": "Follow up on hypertensive crisis (BP >180/120)",
            "description": "Patient had critically elevated blood pressure reading in past 7 days. Assess for target organ damage and adjust treatment.",
            "priority": "HIGH",
            "rationale": "Critical BP reading (>180 systolic or >120 diastolic)"
        })

    # -------------------------------------------------------------------------
    # 5. Format as markdown with HTMX buttons
    # -------------------------------------------------------------------------
    if not suggestions:
        return "I analyzed this patient's clinical data and did not identify any urgent action items at this time. All screenings appear up-to-date and no critical values were found."

    markdown = "Based on my analysis of this patient's clinical data, I suggest the following tasks:\n\n"

    for i, suggestion in enumerate(suggestions, 1):
        markdown += f"### {i}. {suggestion['title']}\n\n"
        markdown += f"**Priority:** {suggestion['priority']}\n\n"
        markdown += f"**Rationale:** {suggestion['rationale']}\n\n"
        markdown += f"{suggestion['description']}\n\n"

        # HTMX button to add task
        markdown += f"""<button class="btn btn--sm btn--primary"
            hx-get="/api/patient/tasks/quick-create-modal?icn={patient_icn}&prefilled_title={suggestion['title']}&prefilled_description={suggestion['description']}&prefilled_priority={suggestion['priority']}&is_ai_generated=true&ai_suggestion_source={suggestion['rationale']}"
            hx-target="#modal-container"
            hx-swap="innerHTML">
            <i class="fa-solid fa-plus"></i> Add to Tasks
        </button>\n\n"""

        markdown += "---\n\n"

    return markdown
```

### 7.2 AI Tool Registration

**File:** `ai/tools/__init__.py`

```python
from ai.tools.ddi_tools import check_ddi_risks
from ai.tools.patient_context_tools import get_patient_summary
from ai.tools.vitals_tools import analyze_vitals_trends
from ai.tools.notes_tools import get_clinical_notes_summary
from ai.tools.task_tools import suggest_patient_tasks  # NEW

ALL_TOOLS = [
    check_ddi_risks,
    get_patient_summary,
    analyze_vitals_trends,
    get_clinical_notes_summary,
    suggest_patient_tasks  # NEW
]
```

### 7.3 AI Insights Chatbot Integration

**User Query Examples:**

1. **"What tasks should I track for this patient?"**
   - AI invokes `suggest_patient_tasks(icn)`
   - Returns markdown with task suggestions + "Add to Tasks" buttons

2. **"Are there any overdue screenings or follow-ups?"**
   - AI invokes `suggest_patient_tasks(icn)`
   - Focuses response on preventive care gaps

3. **"Help me prioritize my work for this patient"**
   - AI invokes `get_patient_summary(icn)` + `suggest_patient_tasks(icn)`
   - Combines clinical context with actionable tasks

**HTMX Button Flow:**

```
1. User clicks "Add to Tasks" button in AI response
   ↓
2. HTMX GET /api/patient/tasks/quick-create-modal?icn=...&prefilled_title=...&is_ai_generated=true
   ↓
3. Modal opens with pre-filled fields + AI attribution
   ↓
4. User reviews, optionally edits, clicks "Create Task"
   ↓
5. HTMX POST /api/patient/{icn}/tasks (with is_ai_generated=true)
   ↓
6. Task saved to database, widget refreshes, modal closes
```

### 7.4 System Prompt Update

**File:** `ai/prompts/system_prompts.py`

```python
# Add to existing CLINICAL_INSIGHT_SYSTEM_PROMPT

CLINICAL_INSIGHT_SYSTEM_PROMPT = """
You are a clinical decision support assistant for the med-z1 longitudinal health record viewer.

# Available Tools

... (existing tools) ...

5. **suggest_patient_tasks(patient_icn: str)**
   - Analyzes patient clinical data and suggests actionable tasks
   - Returns markdown-formatted task suggestions with "Add to Tasks" buttons
   - Use when:
     - User asks "What should I follow up on?"
     - User asks "Are there any overdue screenings?"
     - User asks "Help me prioritize my work"
     - User asks "What tasks should I track?"
   - Tool performs checks for:
     - Overdue screenings (A1C for diabetics, colonoscopy, etc.)
     - Medication-lab monitoring (warfarin→INR, ACE inhibitor→creatinine)
     - Recent hospital discharge follow-up
     - Critical vitals requiring escalation
     - Care gaps based on diagnoses

# Task Management Integration

When suggesting clinical actions, ALWAYS format your response with "Add to Tasks" buttons:

**Example:**
User: "What should I follow up on for this patient?"

AI Response:
"I've analyzed this patient's clinical data and identified 3 action items:

### 1. Patient overdue for A1C screening
**Priority:** MEDIUM
**Rationale:** Active diabetes diagnosis, last A1C 8 months ago

<button hx-get="/api/patient/tasks/quick-create-modal?icn=ICN100001&prefilled_title=Patient overdue for A1C screening&...">Add to Tasks</button>

---

### 2. Review discharge summary from recent hospitalization
**Priority:** HIGH
**Rationale:** Discharged 5 days ago from CHF admission

<button hx-get="/api/patient/tasks/quick-create-modal?...">Add to Tasks</button>
"

# Task Prioritization Guidance

- **HIGH Priority:** Patient safety issues, critical lab values, recent hospitalizations, time-sensitive medications
- **MEDIUM Priority:** Overdue screenings, routine follow-ups, medication refills
- **LOW Priority:** Patient education, non-urgent documentation updates
"""
```

---

## 8. Security & Authorization

### 8.1 Authentication Requirements

**All task endpoints require authentication:**

- ✅ `AuthMiddleware` validates session on every request
- ✅ `request.state.user` injected with user context
- ❌ Unauthenticated requests return 401 Unauthorized

### 8.2 Authorization Model (Phase 1)

**Current Implementation:**

| Action | Authorization Rule | Enforcement |
|--------|-------------------|-------------|
| **View tasks** | Any authenticated user can view any patient's tasks | No row-level security (Phase 1) |
| **Create tasks** | Any authenticated user can create tasks for any patient | Audit trail tracks creator |
| **Update tasks** | Any authenticated user can update any task (status, details) | Audit trail tracks updater |
| **Complete tasks** | Any authenticated user can complete any task | Audit trail tracks completer |
| **Delete tasks** | Any authenticated user can delete any task (Phase 1) | Audit trail tracks deleter |

**Rationale:**
- Phase 1 focuses on workflow efficiency, not access control
- All clinicians on care team should see all tasks for shared patients
- Audit trail provides accountability

### 8.3 Future Authorization Enhancements (Phase 2+)

**Role-Based Access Control (RBAC):**

```python
# Example Phase 2+ authorization logic

def can_delete_task(user: dict, task: dict) -> bool:
    """Check if user can delete task"""
    # Only creator or admin can delete
    return (
        task["created_by_user_id"] == user["user_id"] or
        user.get("role") == "admin"
    )

def can_assign_task(user: dict, task: dict) -> bool:
    """Check if user can assign task to another user"""
    # Only creator, assignee, or team lead can reassign
    return (
        task["created_by_user_id"] == user["user_id"] or
        task.get("assigned_to_user_id") == user["user_id"] or
        user.get("role") in ["team_lead", "admin"]
    )
```

### 8.4 Audit Logging

**Current Audit Trail (Database Fields):**

- `created_by_user_id`, `created_by_display_name`, `created_at`
- `completed_by_user_id`, `completed_by_display_name`, `completed_at`
- `is_ai_generated`, `ai_suggestion_source`
- `updated_at` (auto-updated on any change)

**Future Audit Enhancements (Phase 2+):**

Separate `clinical.patient_task_audit_log` table:
- Track all state transitions (TODO → IN_PROGRESS → COMPLETED)
- Track priority escalations (LOW → HIGH)
- Track title/description edits (before/after values)
- Track assignment changes
- Compliance-grade audit trail with immutability guarantees

### 8.5 Data Privacy Considerations

**Patient Data Linking:**

- Tasks contain **free-text descriptions** (may include PHI)
- Tasks are **patient-centric** (always linked to patient ICN)
- Tasks are **visible to all clinicians** viewing the patient

**Phase 1 Privacy Controls:**

- ✅ All data stored in PostgreSQL (encrypted at rest)
- ✅ HTTPS for all API communication (encrypted in transit)
- ✅ Session-based authentication (no password in cookies)
- ❌ No patient-level authorization (all clinicians see all patients)
- ❌ No data export/reporting controls (Phase 2+)

**Phase 2+ Privacy Enhancements:**

- Patient consent flags (opt-in/opt-out for task tracking)
- Sensitive flag (hide task details from non-primary team)
- Automatic PHI redaction in task descriptions
- Compliance with VA Privacy Act requirements

---

## 9. Implementation Roadmap

### 9.1 Phase 1: Core Task Management (2-3 weeks)

**Week 1: Database & Backend**

**Day 1-2: Database Schema**
- [x] Create DDL: `db/ddl/create_patient_tasks_table.sql`
- [x] Run DDL on development PostgreSQL
- [x] Create seed data: Insert 10-15 test tasks for test patients
- [x] Verify indexes and triggers

**Day 3-5: Query Layer**
- [x] Create `app/db/patient_tasks.py` with functions:
  - `get_patient_tasks()` - Retrieve tasks with filters
  - `create_task()` - Insert new task
  - `update_task_status()` - Change status
  - `complete_task()` - Mark complete with audit fields
  - `update_task()` - Edit title/description/priority
  - `delete_task()` - Hard delete
  - `get_task_summary()` - Stats for full page
  - `get_task_by_id()` - Single task retrieval

**Day 6-7: API Routes**
- [x] Create `app/routes/tasks.py`
- [x] Implement API router (8 endpoints)
- [x] Implement page router (3 endpoints)
- [x] Register routers in `app/main.py`
- [x] Test all endpoints with Postman/curl

**Week 2: UI Implementation**

**Day 8-10: Dashboard Widget**
- [x] Create `app/templates/partials/tasks_widget.html`
- [x] Add CSS styles to `app/static/styles.css`
- [x] Update `app/templates/dashboard.html` to include widget
- [x] Test widget loading, HTMX interactions
- [x] Test quick actions (start, complete buttons)

**Day 11-12: Full Page View**
- [x] Create `app/templates/patient_tasks.html`
- [x] Create `app/templates/partials/task_card.html`
- [x] Create `app/templates/partials/tasks_list.html`
- [x] Implement filtering (status, created_by, priority)
- [x] Test HTMX filtering and pagination

**Day 13-14: Modals**
- [x] Create `app/templates/modals/task_create_modal.html`
- [x] Create `app/templates/modals/task_edit_modal.html`
- [x] Test modal open/close, form submission
- [x] Test HTMX swap and widget refresh

**Week 3: AI Integration & Polish**

**Day 15-16: AI Tool**
- [x] Create `ai/tools/task_tools.py`
- [x] Implement `suggest_patient_tasks()` tool
- [x] Register tool in `ai/tools/__init__.py`
- [x] Update system prompt in `ai/prompts/system_prompts.py`
- [x] Test AI suggestions in `/insight` chatbot

**Day 17-18: HTMX Button Integration**
- [x] Test "Add to Tasks" button flow
- [x] Test pre-filled modal from AI suggestions
- [x] Test AI attribution fields (is_ai_generated, ai_suggestion_source)
- [x] Test widget refresh after AI task creation

**Day 19-20: Testing & Bug Fixes**
- [x] End-to-end testing (create → start → complete workflow)
- [x] Test filtering on full page
- [x] Test CCOW redirect from sidebar
- [x] Test multi-user scenarios (Dr. Alpha creates, Dr. Beta completes)
- [x] Fix any bugs, polish UI

**Day 21: Documentation**
- [x] Update `CLAUDE.md` with task tracking feature
- [x] Update `app/README.md` with routing examples
- [x] Create user guide for task tracking

### 9.2 Phase 2: Enhanced Task Attributes (2-3 weeks)

**Due Dates & Overdue Warnings**
- Add `due_date` column to schema
- Implement overdue badge in widget
- Add calendar picker in modal
- Email/push notifications for overdue tasks

**Task Categories**
- Add `category` column (LAB_REVIEW, MEDICATION, FOLLOWUP, CONSULT)
- Implement category filtering on full page
- Add category icons in task cards
- Category-specific workflows (e.g., link to lab result)

**Clinical Data Links**
- Create `clinical.patient_task_links` table
- Deep links to lab results, medications, clinical notes
- "View Linked Data" button in task card
- Automatic link creation from AI suggestions

### 9.3 Phase 3: Team Collaboration (3-4 weeks)

**Task Assignment**
- Add `assigned_to_user_id` column
- Implement assignment dropdown (select user from care team)
- "Assigned to Me" filter on full page
- Assignment notification (email/push)

**Task Comments**
- Create `clinical.patient_task_comments` table
- Threaded discussion on tasks
- @ mentions for specific users
- Comment notifications

**Bulk Actions**
- Select multiple tasks (checkboxes)
- Bulk complete, bulk assign, bulk delete
- Bulk priority update

### 9.4 Phase 4: Advanced AI Features (4-6 weeks)

**Proactive AI Task Generation**
- Nightly batch job analyzes all patients
- AI creates draft tasks in "AI Suggested" section
- User reviews and approves/dismisses suggestions
- Machine learning to improve suggestion quality

**AI Priority Scoring**
- AI calculates clinical urgency score (0-100)
- Auto-prioritize tasks based on severity, time-sensitivity
- Explain AI reasoning (explainable AI)

**Care Gap Analysis**
- AI scans for missing screenings, overdue follow-ups
- Generates "Care Gap Report" with suggested tasks
- Preventive care optimization

### 9.5 Phase 5: Integration & Enterprise Features (6-8 weeks)

**CPRS Worklist Sync**
- Sync med-z1 tasks with CPRS "flag orders"
- Bidirectional updates (create in med-z1, see in CPRS)
- Map task categories to CPRS order types

**Reporting & Analytics**
- Task completion rate by user, by facility
- Time to completion metrics
- AI suggestion adoption rate
- Care gap closure tracking

**Mobile Optimization**
- Responsive design improvements
- Progressive Web App (PWA) for offline access
- Push notifications for overdue tasks

---

## 10. Appendices

### 10.1 Database Query Layer Implementation

**File:** `app/db/patient_tasks.py`

```python
from typing import List, Dict, Optional, Any
from sqlalchemy import text
from app.db import engine
import uuid

# ----------------------------------------------------------------------------
# Get Patient Tasks (with filtering)
# ----------------------------------------------------------------------------
def get_patient_tasks(
    patient_icn: str,
    status: Optional[str] = None,  # "active", "TODO", "IN_PROGRESS", "COMPLETED", or None
    created_by_user_id: Optional[str] = None,
    priority: Optional[str] = None,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Get all tasks for a patient with optional filtering.

    Args:
        patient_icn: Patient ICN (e.g., "ICN100001")
        status: Filter by status ("active"=TODO+IN_PROGRESS, "TODO", "IN_PROGRESS", "COMPLETED", None=all)
        created_by_user_id: Filter by creator (UUID string or None)
        priority: Filter by priority ("HIGH", "MEDIUM", "LOW", None=all)
        limit: Max number of tasks to return (None=all)

    Returns:
        List of task dictionaries sorted by priority, created_at DESC
    """

    # Build WHERE clauses
    where_clauses = ["patient_key = :patient_icn"]
    params = {"patient_icn": patient_icn}

    if status:
        if status == "active":
            where_clauses.append("status IN ('TODO', 'IN_PROGRESS')")
        else:
            where_clauses.append("status = :status")
            params["status"] = status

    if created_by_user_id:
        where_clauses.append("created_by_user_id = :created_by_user_id")
        params["created_by_user_id"] = created_by_user_id

    if priority:
        where_clauses.append("priority = :priority")
        params["priority"] = priority

    where_sql = " AND ".join(where_clauses)

    # Build LIMIT clause
    limit_sql = f"LIMIT {limit}" if limit else ""

    # Query
    query = text(f"""
        SELECT
            task_id,
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            completed_by_user_id,
            completed_by_display_name,
            is_ai_generated,
            ai_suggestion_source,
            created_at,
            updated_at,
            completed_at
        FROM clinical.patient_tasks
        WHERE {where_sql}
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
            END,
            created_at DESC
        {limit_sql}
    """)

    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [dict(row._mapping) for row in result]


# ----------------------------------------------------------------------------
# Create Task
# ----------------------------------------------------------------------------
def create_task(
    patient_icn: str,
    title: str,
    created_by_user_id: str,
    created_by_display_name: str,
    description: Optional[str] = None,
    priority: str = "MEDIUM",
    is_ai_generated: bool = False,
    ai_suggestion_source: Optional[str] = None
) -> int:
    """
    Create new task for patient.

    Returns:
        task_id (int) of newly created task
    """
    query = text("""
        INSERT INTO clinical.patient_tasks (
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            is_ai_generated,
            ai_suggestion_source
        ) VALUES (
            :patient_icn,
            :title,
            :description,
            :priority,
            'TODO',
            :created_by_user_id,
            :created_by_display_name,
            :is_ai_generated,
            :ai_suggestion_source
        )
        RETURNING task_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "patient_icn": patient_icn,
            "title": title,
            "description": description,
            "priority": priority,
            "created_by_user_id": created_by_user_id,
            "created_by_display_name": created_by_display_name,
            "is_ai_generated": is_ai_generated,
            "ai_suggestion_source": ai_suggestion_source
        })
        conn.commit()
        return result.scalar()


# ----------------------------------------------------------------------------
# Update Task Status
# ----------------------------------------------------------------------------
def update_task_status(task_id: int, status: str) -> None:
    """
    Update task status (TODO, IN_PROGRESS, COMPLETED).
    Note: Use complete_task() for COMPLETED status to populate audit fields.
    """
    query = text("""
        UPDATE clinical.patient_tasks
        SET status = :status
        WHERE task_id = :task_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {"task_id": task_id, "status": status})
        conn.commit()


# ----------------------------------------------------------------------------
# Complete Task
# ----------------------------------------------------------------------------
def complete_task(
    task_id: int,
    completed_by_user_id: str,
    completed_by_display_name: str
) -> None:
    """
    Mark task as completed and populate audit fields.
    """
    query = text("""
        UPDATE clinical.patient_tasks
        SET
            status = 'COMPLETED',
            completed_by_user_id = :completed_by_user_id,
            completed_by_display_name = :completed_by_display_name,
            completed_at = NOW()
        WHERE task_id = :task_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "task_id": task_id,
            "completed_by_user_id": completed_by_user_id,
            "completed_by_display_name": completed_by_display_name
        })
        conn.commit()


# ----------------------------------------------------------------------------
# Update Task Details
# ----------------------------------------------------------------------------
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None
) -> None:
    """
    Update task details (title, description, priority).
    Only updates fields that are not None.
    """
    updates = []
    params = {"task_id": task_id}

    if title is not None:
        updates.append("title = :title")
        params["title"] = title

    if description is not None:
        updates.append("description = :description")
        params["description"] = description

    if priority is not None:
        updates.append("priority = :priority")
        params["priority"] = priority

    if not updates:
        return  # Nothing to update

    update_sql = ", ".join(updates)
    query = text(f"""
        UPDATE clinical.patient_tasks
        SET {update_sql}
        WHERE task_id = :task_id
    """)

    with engine.connect() as conn:
        conn.execute(query, params)
        conn.commit()


# ----------------------------------------------------------------------------
# Delete Task
# ----------------------------------------------------------------------------
def delete_task(task_id: int) -> None:
    """
    Hard delete task from database.
    Phase 2+ should implement soft delete (archived flag).
    """
    query = text("""
        DELETE FROM clinical.patient_tasks
        WHERE task_id = :task_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {"task_id": task_id})
        conn.commit()


# ----------------------------------------------------------------------------
# Get Single Task
# ----------------------------------------------------------------------------
def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """
    Get single task by ID.
    Returns None if not found.
    """
    query = text("""
        SELECT
            task_id,
            patient_key,
            title,
            description,
            priority,
            status,
            created_by_user_id,
            created_by_display_name,
            completed_by_user_id,
            completed_by_display_name,
            is_ai_generated,
            ai_suggestion_source,
            created_at,
            updated_at,
            completed_at
        FROM clinical.patient_tasks
        WHERE task_id = :task_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"task_id": task_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None


# ----------------------------------------------------------------------------
# Get Task Summary (for full page stats)
# ----------------------------------------------------------------------------
def get_task_summary(patient_icn: str) -> Dict[str, int]:
    """
    Get summary statistics for patient's tasks.

    Returns:
        {
            "todo_count": 5,
            "in_progress_count": 2,
            "completed_today_count": 3,
            "ai_generated_count": 1
        }
    """
    query = text("""
        SELECT
            COUNT(*) FILTER (WHERE status = 'TODO') AS todo_count,
            COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress_count,
            COUNT(*) FILTER (WHERE status = 'COMPLETED' AND completed_at::DATE = CURRENT_DATE) AS completed_today_count,
            COUNT(*) FILTER (WHERE is_ai_generated = TRUE AND status != 'COMPLETED') AS ai_generated_count
        FROM clinical.patient_tasks
        WHERE patient_key = :patient_icn
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"patient_icn": patient_icn})
        row = result.fetchone()
        return dict(row._mapping) if row else {
            "todo_count": 0,
            "in_progress_count": 0,
            "completed_today_count": 0,
            "ai_generated_count": 0
        }
```

### 10.2 Test Data SQL

**File:** `scripts/create_test_tasks.sql`

```sql
-- Test tasks for Patient ICN100001 (Adam Dooree)

-- Task 1: High priority, in progress, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Review discharge summary from recent CHF admission',
    'Patient discharged 2 days ago from Alexandria VAMC. Need to review discharge medications, ensure no DDIs with current med list, and confirm follow-up cardiology appointment scheduled.',
    'HIGH',
    'IN_PROGRESS',
    '11111111-1111-1111-1111-111111111111',  -- Clinician Alpha
    'Dr. Alpha',
    FALSE,
    NOW() - INTERVAL '1 day'
);

-- Task 2: Medium priority, todo, AI-generated
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, ai_suggestion_source, created_at
) VALUES (
    'ICN100001',
    'Patient overdue for A1C screening',
    'Last A1C: 8.2% on 2025-06-15 (8 months ago). Current ADA guidelines recommend A1C every 6 months for uncontrolled diabetes (target <7% for most patients). Patient has active Type 2 diabetes diagnosis.',
    'MEDIUM',
    'TODO',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    TRUE,
    'AI Insights: Active diabetes diagnosis + no A1C in past 6 months',
    NOW() - INTERVAL '2 hours'
);

-- Task 3: High priority, todo, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Call patient about abnormal INR result (5.2)',
    'INR critically elevated at 5.2 (target 2-3 for afib). Patient on warfarin 5mg daily. Assess for bleeding symptoms, hold next dose, recheck INR in 48 hours.',
    'HIGH',
    'TODO',
    '22222222-2222-2222-2222-222222222222',  -- Clinician Beta
    'Dr. Beta',
    FALSE,
    NOW() - INTERVAL '3 hours'
);

-- Task 4: Medium priority, todo, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Schedule echocardiogram',
    'Patient has new-onset systolic murmur on exam. Obtain echo to rule out valvular disease or worsening cardiomyopathy. EF was 40% on last echo 2 years ago.',
    'MEDIUM',
    'TODO',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    FALSE,
    NOW() - INTERVAL '6 hours'
);

-- Task 5: Low priority, todo, user-created
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    is_ai_generated, created_at
) VALUES (
    'ICN100001',
    'Update patient education materials for CHF self-management',
    'Provide patient with revised CHF handout including daily weight monitoring instructions, dietary sodium limits, and warning signs of decompensation.',
    'LOW',
    'TODO',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    FALSE,
    NOW() - INTERVAL '1 week'
);

-- Task 6: Medium priority, completed yesterday
INSERT INTO clinical.patient_tasks (
    patient_key, title, description, priority, status,
    created_by_user_id, created_by_display_name,
    completed_by_user_id, completed_by_display_name,
    completed_at, created_at
) VALUES (
    'ICN100001',
    'Review cardiology consult recommendations',
    'Cardiologist recommended increasing metoprolol to 100mg BID and adding spironolactone 25mg daily for CHF management.',
    'MEDIUM',
    'COMPLETED',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    '11111111-1111-1111-1111-111111111111',
    'Dr. Alpha',
    NOW() - INTERVAL '1 day' + INTERVAL '3 hours',
    NOW() - INTERVAL '3 days'
);

-- Add similar test tasks for Patient ICN100010 (Alexander Aminor)
-- ... (repeat pattern for 2-3 more patients)
```

### 10.3 Configuration Updates

**File:** `config.py`

```python
# Add task-related configuration

# Task Tracking Settings
TASK_DEFAULT_PAGE_SIZE = int(os.getenv("TASK_DEFAULT_PAGE_SIZE", "20"))
TASK_WIDGET_MAX_ITEMS = int(os.getenv("TASK_WIDGET_MAX_ITEMS", "8"))
TASK_AUTO_ARCHIVE_COMPLETED_DAYS = int(os.getenv("TASK_AUTO_ARCHIVE_COMPLETED_DAYS", "7"))

# AI Task Suggestion Settings
AI_TASK_SUGGESTION_ENABLED = os.getenv("AI_TASK_SUGGESTION_ENABLED", "true").lower() == "true"
AI_TASK_MAX_SUGGESTIONS = int(os.getenv("AI_TASK_MAX_SUGGESTIONS", "5"))
```

**File:** `.env` (example)

```bash
# Task Tracking
TASK_DEFAULT_PAGE_SIZE=20
TASK_WIDGET_MAX_ITEMS=8
TASK_AUTO_ARCHIVE_COMPLETED_DAYS=7

# AI Task Suggestions
AI_TASK_SUGGESTION_ENABLED=true
AI_TASK_MAX_SUGGESTIONS=5
```

---

## 11. Known Issues

### 11.1 Dashboard Widget Auto-Refresh Issue

**Issue Date:** 2026-02-10

**Description:**
After creating or editing a task via the modal on the Dashboard page, the task widget does not automatically refresh to show the new/updated task. User must perform a manual page refresh (Command+R) or navigate away and back to see the updated task list.

**Expected Behavior:**
- User creates/edits a task via modal
- Modal closes
- Task widget automatically refreshes to display the new/updated task immediately
- No manual page refresh required

**Current Workaround:**
Manual page refresh (Command+R) or navigate to another page and back to Dashboard.

**Technical Details:**
- Widget container: `#widget-tasks` in `dashboard.html`
- HTMX trigger: `hx-trigger="load, taskUpdated from:body"`
- Success script attempts multiple refresh approaches:
  1. Direct `htmx.ajax()` call to widget endpoint
  2. `document.body.dispatchEvent(new CustomEvent('taskUpdated'))`
  3. `htmx.trigger(document.body, 'taskUpdated')`
- None of the approaches successfully trigger widget refresh

**Potential Causes:**
- HTMX event listener not properly bound to dynamically loaded widget content
- Event bubbling/propagation issue with custom events
- Timing issue where event fires before widget is ready to listen
- Possible conflict with widget's `innerHTML` swap strategy

**Files Involved:**
- `app/routes/tasks.py` (lines 512-527: create success script, lines 610-626: edit success script)
- `app/templates/dashboard.html` (lines 28-36: widget container with hx-trigger)
- `app/templates/partials/tasks_widget.html` (widget HTML partial)

**Priority:** Medium (functionality works, but UX is degraded)

**Follow-up Required:** Yes - investigate HTMX event propagation in dynamically swapped content

---

## Document Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.0 | 2026-02-10 | Claude Code | Initial design specification |
| v1.1 | 2026-02-10 | Claude Code | Added Section 11: Known Issues - Dashboard widget auto-refresh issue |

---

**End of Document**
