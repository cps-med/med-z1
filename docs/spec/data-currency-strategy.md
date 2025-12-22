# Data Currency Strategy for med-z1
**Analysis of T-1 Latency and Mitigation Strategies**

**Document Version:** 1.0
**Date:** 2025-12-13
**Status:** Proposed Strategy

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Critical Assessment](#critical-assessment)
4. [Recommended Strategy](#recommended-strategy)
5. [Alternative Approaches](#alternative-approaches)
6. [Implementation Guidance](#implementation-guidance)
7. [Decision Framework](#decision-framework)

---

## 1. Executive Summary

**The Core Question:** Will users reject a fast, reliable system with T-1 data in favor of a slow, unreliable system with real-time data?

**My Assessment:** The chatbot analysis in `docs/medz1-design-assessment.md` is thorough and technically sound, but may overweight the T-1 latency concern relative to the more fundamental problems med-z1 solves. I recommend a **phased, evidence-based approach** rather than building complex hybrid infrastructure preemptively.

**Key Recommendations:**

1. **Launch with T-1 data and excellent UX first** - Prove the core value proposition
2. **Make data currency transparent** - Trust through honesty, not through hiding limitations
3. **Gather real usage evidence** - Let actual clinical workflows drive hybrid decisions
4. **If hybrid is needed, start minimal** - Single domain, strict bounds, measure everything
5. **Prioritize incremental CDW refreshes** over real-time RPC if organizationally feasible

**Why This Differs from the Chatbot:** The chatbot assumes T-1 latency is a critical barrier to adoption. I believe the 10-30 second load times and frequent timeouts are far more critical. Solve the acute pain first, then iterate on currency if users demand it.

---

## 2. Problem Statement

### 2.1 Current Legacy JLV Pain Points

**Primary Issues (User-Facing):**
- 10-30+ second widget load times (sometimes 90 seconds)
- Frequent timeouts and failures
- Inconsistent performance across VistA sites
- Poor user experience drives workarounds and distrust

**Secondary Issues (Infrastructure):**
- RPC fan-out overwhelms VistA sites
- Scalability limited by downstream systems
- High operational complexity
- Difficult to troubleshoot performance issues

### 2.2 The T-1 Latency Concern

**Valid Clinical Scenarios Where T-1 Matters:**
- Morning rounds reviewing overnight vitals
- Verifying medication administered within last few hours
- Checking latest lab results that resulted today
- Confirming recent allergy/flag documentation
- Validating current patient location/admission status

**However:** Users currently experience these scenarios with:
- 10-30 second waits (often longer)
- Frequent timeouts
- No visibility into why data is slow or unavailable
- No trust in system reliability

**The Question:** Would users prefer:
- **Option A:** Reliable sub-second loads with yesterday's data (clearly labeled)
- **Option B:** 10-30 second loads with occasional real-time data (when it works)

I believe most users will choose Option A, especially if we provide transparency.

---

## 3. Critical Assessment

### 3.1 What the Chatbot Got Right

The analysis in `docs/medz1-design-assessment.md` is excellent on:

1. **Technical feasibility** - Hybrid architecture is absolutely possible
2. **Guardrails** - Rate limiting, caching, circuit breakers are essential if you go hybrid
3. **Pattern alignment** - Fits well with FastAPI/HTMX and lazy-load patterns
4. **Risk awareness** - Correctly identifies how hybrid can drift back to legacy problems
5. **Observability** - Strong emphasis on metrics and proving bounded load to VistA owners

**These are valuable insights to keep on file for potential future implementation.**

### 3.2 What I Question

**1. Prioritization and Timing**

The chatbot recommends treating data freshness as "Priority 1" and building hybrid infrastructure relatively early. I disagree.

**My View:** Prove the core value proposition first:
- Fast, reliable loads from serving DB
- Excellent UX with clear "as-of" timestamps
- Consistent performance regardless of VistA site health
- 90% reduction in VistA load

**Then** gather evidence:
- Which domains do users actually complain about?
- What workflows are truly blocked by T-1?
- Are there organizational alternatives (more frequent CDW refreshes)?

**2. Complexity vs. Value Tradeoff**

Hybrid architecture introduces significant complexity:
- New service (Real-time Delta Gateway)
- Redis for caching and rate limiting
- Circuit breaker logic
- Request coalescing
- Per-domain merge/reconciliation rules
- Security implications (more PHI in motion)
- Operational burden (monitoring, alerting, tuning)
- ATO surface area expansion

**Cost:** Weeks/months of development + ongoing operational overhead

**Benefit:** Unknown until users actually use the system and tell us what they need

**3. User Expectations May Differ from Assumptions**

The chatbot assumes "clinicians will assume JLV is current unless you tell them otherwise."

**Counter-argument:**
- Users already know current JLV is slow and unreliable
- Many clinical workflows already work with T-1 data (reports, analytics dashboards)
- Transparency builds trust - hiding T-1 latency would be worse than acknowledging it
- Fast + honest may beat slow + real-time

**4. False Binary: RPC or Nothing**

The chatbot frames the solution as "serve from CDW OR call VistA RPC." There are other options:
- Incremental CDW refreshes (every 6/12 hours instead of daily)
- Change data capture (CDC) streaming for high-priority domains
- Dedicated near-real-time feeds from CDW for specific domains
- Event-driven updates (new admission triggers refresh)

Some of these may be more organizationally/politically viable than resurrecting RPC calls.

---

## 4. Recommended Strategy

### 4.1 Phase 1: Launch with T-1 and Excellent UX (Months 1-3)

**Goal:** Prove the core value proposition - fast, reliable, consistent performance.

**Implementation:**

**A. Transparency-First UI Design**

```html
<!-- Global data currency indicator in header -->
<div class="data-currency-banner">
  <i class="icon-info"></i>
  <span>Data current as of: <strong>12-Dec-2025 05:00 ET</strong></span>
  <a href="/help/data-currency" class="help-link">Learn more</a>
</div>

<!-- Per-widget currency (in widget footer) -->
<div class="widget-footer">
  <span class="text-muted small">
    Updated: 12-Dec-2025 05:00 ET
  </span>
</div>
```

**B. Help/Documentation Content**

Create `/help/data-currency` page explaining:
- Why med-z1 uses overnight data (performance, reliability, VistA protection)
- What "as of" timestamp means
- Which workflows this supports well vs. limitations
- How to verify critical recent data (links to source systems if needed)

**C. Measurement and Feedback**

Instrument the application to capture:
- Page load times (prove the speed improvement)
- User satisfaction surveys (NPS, domain-specific ratings)
- Support tickets (categorize by data currency vs. other issues)
- Usage patterns (which domains are accessed most, when)

**D. Establish Baseline Performance**

Target SLOs (align with existing goals):
- Patient overview page: < 4 seconds (90th percentile)
- Individual widgets: < 500ms (95th percentile)
- Full domain pages: < 2 seconds (95th percentile)

**Success Criteria for Phase 1:**
- ✅ 90%+ reduction in VistA RPC load
- ✅ Consistent sub-4-second patient overview loads
- ✅ User satisfaction > baseline (measured via survey)
- ✅ < 5% of support tickets related to data currency concerns

If Phase 1 succeeds, you've proven the model. If data currency becomes the #1 complaint, you have evidence to justify Phase 2.

### 4.2 Phase 2: Evaluate Hybrid Need (Month 4)

**Before building anything**, answer these questions with evidence:

**Question 1: Is T-1 latency actually blocking critical workflows?**
- Evidence: User feedback, support tickets, interviews
- Threshold: > 20% of complaints are currency-related

**Question 2: Which specific domains need freshness?**
- Evidence: Usage analytics, clinician interviews
- Expected: Likely vitals, medications, labs (as chatbot predicted)
- But validate empirically

**Question 3: What's the organizational path to freshness?**
- Option A: VistA RPC (technical feasibility known, political risk)
- Option B: More frequent CDW loads (12-hour refresh? Incremental?)
- Option C: CDC/streaming from CDW for priority domains
- Option D: Federated query to CDW (bypassing local lake for "today" data)

**Question 4: What's the acceptable complexity/cost tradeoff?**
- Development time: X weeks
- Operational overhead: Y hours/week
- ATO implications: Z months delay
- User value: Measured improvement in satisfaction/workflows

**Decision Gate:** Only proceed to Phase 3 if evidence strongly supports hybrid need AND organizational path is clear.

### 4.3 Phase 3: Minimal Hybrid Implementation (If Justified)

**If** Phase 2 evidence justifies hybrid, implement the **absolute minimum viable version:**

**A. Start with Single Domain**

Pick ONE domain based on evidence (likely Vitals or Medications):
- Highest user complaints about currency
- Smallest payload for "today" data
- Clearest clinical benefit

**B. Manual Refresh Only (No Auto-Load)**

```html
<!-- Widget shows baseline + refresh option -->
<div class="widget vitals-widget">
  <!-- Fast baseline render from PostgreSQL -->
  <div class="vitals-baseline">
    <!-- 24 hours of vitals from serving DB -->
  </div>

  <!-- Optional refresh control -->
  <div class="vitals-freshness">
    <p class="text-muted small">
      Showing vitals as of 12-Dec-2025 05:00 ET
    </p>
    <button
      hx-post="/api/patient/{{icn}}/vitals/refresh-today"
      hx-target="#vitals-delta"
      hx-disabled-elt="this"
      class="btn btn-sm btn-outline">
      Check for today's updates
    </button>
    <span class="help-text">
      (May take 2-5 seconds; limited to once per 5 minutes)
    </span>
  </div>

  <div id="vitals-delta" class="vitals-delta"></div>
</div>
```

**C. Strict Guardrails (As Chatbot Recommended)**

- Single domain initially
- 5-minute cooldown per user/patient/domain
- 5-15 minute cache TTL
- Request coalescing (100 concurrent requests → 1 RPC call)
- Circuit breaker (trip on latency > 5s or error rate > 20%)
- Global rate limit per VistA site (conservative: 10-20 req/min)

**D. Measure Everything**

Track:
- % of users who click "refresh today" (measure demand)
- RPC call volume by site/domain/hour
- Latency p50/p95/p99
- Cache hit ratio
- Circuit breaker trips
- User satisfaction delta (before/after hybrid)

**Success Criteria for Phase 3:**
- ✅ VistA load stays within agreed budget (prove to site owners)
- ✅ "Today" refresh completes in < 5 seconds (95th percentile)
- ✅ Measurable improvement in user satisfaction for that domain
- ✅ < 5% of refresh attempts fail or timeout

**If Phase 3 succeeds:** Expand to 1-2 more domains with same discipline.

**If Phase 3 fails or shows low usage:** You avoided months of premature optimization.

---

## 5. Alternative Approaches

### 5.1 Incremental CDW Refreshes (Recommended to Explore First)

**Concept:** Instead of once-daily ETL, run incremental loads throughout the day.

**Example Schedule:**
- Full refresh: 05:00 daily (current plan)
- Incremental refresh: 11:00, 17:00, 23:00 (smaller time windows)

**Advantages:**
- No new runtime architecture (same ETL pipeline)
- No VistA RPC calls (site owners happy)
- Predictable load patterns
- Simpler to reason about (no two-source reconciliation)
- Lower ATO risk

**Challenges:**
- ETL orchestration complexity
- CDW may not support efficient incremental queries
- Need change detection (row-level timestamps in CDW)
- Still not "real-time" but improves from T-1 to T-6 or T-12

**Organizational Question:** Is this politically/technically feasible at VA?

### 5.2 Domain-Specific Federated Queries

**Concept:** For highest-priority domains, bypass the local serving DB and query CDW directly for "today."

**Architecture:**
```
User requests vitals page
  ↓
FastAPI app queries:
  1. PostgreSQL: Get vitals from 2 weeks ago to yesterday (fast, local)
  2. CDW API: Get vitals from midnight to now (slower, but acceptable for single query)
  ↓
Merge results and render
```

**Advantages:**
- No VistA RPC (avoids site overload concern)
- No new gateway service
- CDW is designed for query load (unlike VistA RPC)
- Can cache results similar to hybrid gateway

**Challenges:**
- CDW query latency (unknown)
- CDW may not have "real-time" data either (depends on their refresh schedule)
- Network/auth complexity (firewall, credentials)

### 5.3 Event-Driven Selective Refresh

**Concept:** External systems push events to med-z1 when high-value changes occur.

**Example:**
- New admission → Trigger refresh of patient demographics + vitals
- New medication order → Trigger refresh of medications for that patient
- Lab result → Trigger refresh of labs for that patient

**Advantages:**
- Only refresh when actually needed
- Targeted, small payloads
- Can trigger Gold ETL re-run for specific patient+domain

**Challenges:**
- Requires event bus infrastructure (Kafka, Azure Event Grid, etc.)
- Source systems must publish events
- Complex orchestration
- Likely a Phase 5+ capability

### 5.4 "Break Glass" Links to Source Systems

**Concept:** Accept T-1 latency in med-z1, but provide escape hatch for critical verification.

**UI Pattern:**
```html
<div class="vitals-widget">
  <!-- med-z1 data (T-1) -->

  <div class="verify-link">
    <i class="icon-external"></i>
    <a href="https://vista.site580.va.gov/patient/{{icn}}/vitals" target="_blank">
      Verify latest vitals in VistA
    </a>
    <span class="help-text">(opens source system)</span>
  </div>
</div>
```

**Advantages:**
- Extremely simple (just links)
- Zero med-z1 infrastructure
- Puts control in clinician hands
- Preserves med-z1 as "fast overview" + source systems as "verification"

**Disadvantages:**
- Context switch (user leaves med-z1)
- Assumes source system has good UI (often not true)
- Requires authentication to multiple systems

---

## 6. Implementation Guidance

### 6.1 If You Proceed with Hybrid Architecture

**I recommend following the chatbot's technical design** from `docs/medz1-design-assessment.md` (Turn 4), with these modifications:

**Simplifications:**

1. **Defer dedicated gateway service initially**
   - Start with hybrid logic in main FastAPI app
   - Extract to separate service only if RPC volume justifies it
   - Reduces deployment complexity for MVP

2. **Manual refresh only (no auto-check)**
   - Do NOT auto-fetch deltas on patient load
   - Explicit user action required
   - Dramatically reduces accidental load spikes

3. **Single domain for 3-6 months minimum**
   - Resist expansion pressure
   - Prove value and stability first
   - Iterate on patterns before scaling

**Additions:**

1. **Kill switch**
   - Feature flag to disable hybrid per domain
   - Graceful degradation when switched off
   - Allows instant rollback if problems arise

2. **VistA owner dashboard**
   - Public-facing metrics showing load budget compliance
   - Build trust proactively
   - Monthly reports to site owners

3. **User analytics**
   - Track who uses "refresh today" feature
   - Measure before/after satisfaction
   - Justify continued investment or deprecation

### 6.2 UI/UX Patterns for Data Currency

**Regardless of hybrid decision**, implement excellent currency UX:

**Pattern 1: Global Currency Banner**
```html
<div class="alert alert-info data-currency-notice">
  <i class="icon-clock"></i>
  <strong>Data Snapshot:</strong> All data current as of 12-Dec-2025 05:00 ET
  <a href="/help/data-currency" class="alert-link">Learn more</a>
</div>
```

**Pattern 2: Per-Domain Timestamps**
```html
<div class="card-footer text-muted small">
  <i class="icon-clock"></i> Updated: 12-Dec-2025 05:00 ET
</div>
```

**Pattern 3: Optional Refresh Control (If Hybrid)**
```html
<button
  hx-post="/api/refresh/{{domain}}/{{icn}}"
  hx-indicator="#spinner"
  hx-disabled-elt="this"
  class="btn btn-sm btn-outline-primary">
  <i class="icon-refresh"></i> Check for today's updates
</button>
<span class="text-muted small">(Available once per 5 minutes)</span>
```

**Pattern 4: Merge Display (Baseline + Delta)**
```html
<div class="vitals-timeline">
  <!-- PostgreSQL baseline (fast) -->
  <div class="vitals-baseline">
    <h6>Recent History (as of 12-Dec-2025 05:00 ET)</h6>
    <!-- Historical vitals -->
  </div>

  <!-- Optional delta overlay (if refreshed) -->
  <div class="vitals-today" id="vitals-delta">
    <h6>Today's Updates (as of 12-Dec-2025 14:30 ET)</h6>
    <span class="badge badge-success">Real-time</span>
    <!-- Today's vitals from RPC -->
  </div>
</div>
```

### 6.3 Database Schema Additions (If Hybrid)

**Add currency tracking to Gold + PostgreSQL:**

```sql
-- Add to all domain tables
ALTER TABLE patient_vitals ADD COLUMN data_source VARCHAR(20) DEFAULT 'cdw';
  -- Values: 'cdw', 'rpc_delta', 'manual'

ALTER TABLE patient_vitals ADD COLUMN extracted_at TIMESTAMP;
  -- When data was extracted from source

ALTER TABLE patient_vitals ADD COLUMN loaded_at TIMESTAMP DEFAULT NOW();
  -- When data was loaded into serving DB

-- Metadata table for tracking refreshes
CREATE TABLE data_refresh_log (
  id SERIAL PRIMARY KEY,
  patient_icn VARCHAR(50) NOT NULL,
  domain VARCHAR(50) NOT NULL,
  refresh_type VARCHAR(20), -- 'scheduled', 'user_requested', 'event_driven'
  source VARCHAR(20), -- 'cdw', 'vista_rpc', 'cdw_incremental'
  requested_by VARCHAR(100), -- User ID if user-requested
  requested_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP,
  status VARCHAR(20), -- 'pending', 'success', 'failed', 'cached'
  items_refreshed INT,
  error_message TEXT,
  latency_ms INT
);

CREATE INDEX idx_refresh_log_patient ON data_refresh_log(patient_icn, domain, requested_at DESC);
CREATE INDEX idx_refresh_log_stats ON data_refresh_log(domain, status, requested_at DESC);
```

---

## 7. Decision Framework

### 7.1 Go/No-Go Criteria for Hybrid

**Proceed with hybrid development if:**
- ✅ Phase 1 T-1 system has been in production for 3+ months
- ✅ > 20% of user complaints are data currency related
- ✅ Specific domains and workflows identified via evidence
- ✅ VistA site owners approve RPC budget (or alternative source available)
- ✅ Development resources available (4-8 weeks)
- ✅ ATO team approves expanded scope

**Do NOT proceed with hybrid if:**
- ❌ Users are satisfied with T-1 + transparency
- ❌ Complaints focus on other issues (UI, features, bugs)
- ❌ VistA site owners reject RPC approach
- ❌ Organizational alternatives available (more frequent CDW loads)
- ❌ Development resources needed for higher-priority features

### 7.2 Domain Selection Criteria (If Hybrid Approved)

**Prioritize domains that are:**
1. **High clinical impact** - Wrong data leads to wrong decisions
2. **High change frequency** - Data actually changes throughout the day
3. **Small delta payload** - "Today" data is small relative to history
4. **Clear time filter** - Easy to request "since midnight" or "last 24 hours"
5. **User demand evidence** - Actual complaints, not assumptions

**Likely candidates (validate with evidence):**
- Vitals (BP spikes, fever workup)
- Medications (new orders, administrations)
- Labs (new results)
- Admissions/Transfers (patient location)

**Poor candidates:**
- Patient Flags (infrequent changes, sensitive data)
- Allergies (infrequent changes after initial documentation)
- Demographics (very rare intraday changes)
- Historical diagnoses/problems (static)

### 7.3 Annual Review Cycle

**Commitment:** Review data currency strategy annually based on:
- User satisfaction trends
- Support ticket analysis
- Technological changes (new VA data infrastructure?)
- Organizational policy changes
- Cost/benefit reassessment

**Questions for Annual Review:**
1. Has T-1 latency caused clinical errors or near-misses?
2. What % of users actively use hybrid refresh features (if implemented)?
3. Are there new technical alternatives (CDC, event streams, etc.)?
4. What's the TCO of hybrid architecture (dev + ops)?
5. Would resources be better spent elsewhere?

---

## 8. Conclusion and Recommendations

### 8.1 Summary of Position

**The chatbot analysis is technically excellent** - if you decide to build hybrid architecture, follow that design. However, **I question whether hybrid is needed at all**, especially in early phases.

**My core recommendation:**

**Launch with T-1, transparency, and excellent UX. Let real users and real usage patterns drive the hybrid decision, not theoretical concerns.**

**Reasoning:**

1. **Users' acute pain is slow/unreliable loads, not T-1 latency**
   - Going from 30 seconds to 1 second is transformative
   - Going from T-1 to T-0 is incremental
   - Solve acute pain first

2. **Transparency builds trust more than hiding limitations**
   - Clear "as of" timestamps > silent staleness
   - Help documentation explaining tradeoffs
   - Honest communication about data sources

3. **Complexity has real costs**
   - Hybrid adds weeks/months to timeline
   - Operational overhead ongoing
   - ATO scope expansion
   - Opportunity cost (features not built)

4. **Evidence > assumptions**
   - We don't know if users will care about T-1
   - We don't know which domains need freshness
   - We don't know if organizational alternatives exist
   - Build the minimum, measure, iterate

5. **Fast + T-1 may be enough**
   - Many clinical workflows already use T-1 data (reports, dashboards)
   - Reliability matters more than real-time for many use cases
   - med-z1 as "fast overview" + source systems as "verification" is valid model

### 8.2 Action Items

**Immediate (Phase 1):**
- [ ] Implement clear "as of" timestamps globally and per-domain
- [ ] Create `/help/data-currency` documentation page
- [ ] Add user satisfaction surveys (domain-specific)
- [ ] Instrument support ticket categorization (currency vs. other)
- [ ] Define baseline performance SLOs and measure

**After 3-6 Months (Phase 2 Decision Gate):**
- [ ] Analyze user feedback and support tickets
- [ ] Interview clinical users about workflows
- [ ] Investigate organizational alternatives (CDW incremental refresh, etc.)
- [ ] Go/No-Go decision on hybrid based on evidence
- [ ] If Go: Choose single domain, define strict scope

**If Hybrid Approved (Phase 3):**
- [ ] Follow chatbot's technical design with simplifications noted above
- [ ] Single domain, manual refresh only
- [ ] 3-month pilot with heavy instrumentation
- [ ] Measure user adoption and satisfaction delta
- [ ] Expand cautiously only if pilot succeeds

### 8.3 Final Thought

**The best architecture is the simplest one that solves real user problems.**

Right now, the real problems are:
- Slow loads
- Timeouts
- Unreliability
- Poor VistA scalability

T-1 latency *might* be a problem, but it's not proven yet. Build the simple solution first, prove the value, then iterate based on evidence.

**Trust the data, not the assumptions.**

---

## 9. Implementation Decisions

### Decision: "As Of" Timestamp Placement (2025-12-13)

**Decision:** Implement page-level "as of" timestamps, right-aligned with page title (Option 2).

**Rationale:**
- Topbar already handles patient context and CCOW controls (separation of concerns)
- Page-level placement is contextual to the specific domain data being viewed
- Right-alignment pairs well with existing page header layout
- Can be consistently applied across all domain pages

**Implementation Pattern:**
```html
<div class="page-header">
  <h1 class="page-title">Vitals</h1>
  <span class="data-currency text-muted">
    As of: 12-Dec-2025 05:00 ET
  </span>
</div>
```

**Timestamp Format Decision:**
- Use **date + time** (not date only)
- Format: `12-Dec-2025 05:00 ET` (24-hour format, unambiguous date, explicit timezone)
- Rationale: Clinical users expect timestamps; differentiates "this morning" vs "yesterday"; future-proofs incremental refreshes

**Timestamp Source:**
- Use **completion time of PostgreSQL load** (when Gold data finished loading into serving DB)
- This is the true "data current as of" moment
- In production: Query from `etl_run_metadata` table
- In development: Use configured mock timestamp or dynamic calculation (yesterday at 5 AM)

**Implementation Details:**

1. **Create ETL metadata tracking table:**
```sql
CREATE TABLE etl_run_metadata (
  id SERIAL PRIMARY KEY,
  domain VARCHAR(50),
  run_type VARCHAR(20) DEFAULT 'full', -- 'full', 'incremental'
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  status VARCHAR(20), -- 'success', 'failed', 'partial'
  records_processed INT
);

CREATE INDEX idx_etl_metadata_domain ON etl_run_metadata(domain, completed_at DESC);
```

2. **Create utility module for data currency:**
```python
# app/utils/data_currency.py
from datetime import datetime, timedelta
from typing import Optional
from config import MOCK_DATA_AS_OF  # e.g., "2025-12-12 05:00:00"

def get_data_as_of_timestamp(domain: Optional[str] = None) -> datetime:
    """
    Returns the 'as of' timestamp for data currency display.

    In production: queries etl_run_metadata table for latest successful load
    In development: returns configured mock timestamp or calculates yesterday 5 AM

    Args:
        domain: Optional domain name (e.g., 'vitals', 'medications')
                If None, returns global timestamp

    Returns:
        datetime object representing when data was last refreshed
    """
    # TODO: In production, query etl_run_metadata table:
    # SELECT MAX(completed_at) FROM etl_run_metadata
    # WHERE domain = ? AND status = 'success'

    # For development: Use config or calculate
    if hasattr(config, 'MOCK_DATA_AS_OF') and MOCK_DATA_AS_OF:
        return datetime.strptime(MOCK_DATA_AS_OF, "%Y-%m-%d %H:%M:%S")
    else:
        # Default: yesterday at 5 AM ET
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.replace(hour=5, minute=0, second=0, microsecond=0)

def format_as_of_display(timestamp: datetime) -> str:
    """
    Format timestamp for 'as of' display in UI.

    Args:
        timestamp: datetime object

    Returns:
        Formatted string like "12-Dec-2025 05:00 ET"
    """
    return timestamp.strftime("%d-%b-%Y %H:%M ET")
```

3. **Add to config.py:**
```python
# config.py
# Mock data timestamp (development only)
MOCK_DATA_AS_OF = "2025-12-12 05:00:00"  # Update manually during development
```

4. **Use in route handlers:**
```python
# app/routes/vitals.py
from app.utils.data_currency import get_data_as_of_timestamp, format_as_of_display

@page_router.get("/patient/{icn}/vitals")
async def vitals_page(request: Request, icn: str):
    vitals = get_patient_vitals(icn)
    data_as_of = format_as_of_display(get_data_as_of_timestamp('vitals'))

    return templates.TemplateResponse(
        "vitals.html",
        {
            "request": request,
            "patient": {"icn": icn},
            "vitals": vitals,
            "data_as_of": data_as_of
        }
    )
```

5. **Use in templates:**
```html
<!-- templates/vitals.html -->
<div class="page-header">
  <h1 class="page-title">Vitals</h1>
  <span class="data-currency text-muted">
    As of: {{ data_as_of }}
  </span>
</div>
```

**Status:** Approved for implementation
**Next Step:**
1. Create `etl_run_metadata` table (DDL script)
2. Create `app/utils/data_currency.py` module
3. Add `MOCK_DATA_AS_OF` to config.py
4. Update page routes to include `data_as_of` in template context
5. Update page templates with timestamp display

---

**Document Status:** v1.0 - Strategic Analysis and Recommendations
**Next Review:** After Phase 1 deployment (3-6 months)
**Author:** Claude Code Assistant
**Feedback/Questions:** See `docs/medz1-design-assessment.md` for complementary chatbot analysis
