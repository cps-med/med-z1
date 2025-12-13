# JLV Modernization Discussion Log (Consolidated)

> **Note:** This document captures the full prompt/response discussion in this chat, from beginning to end, in a single Markdown file. It does **not** include any of the attached/source documents themselves.

---

## Turn 1 — User Prompt

I am developing a new and modernized version of the Department of Veterans Affairs (VA) Joint Longitudinal Viewer (JLV) application, formerly called Joint Legacy Viewer (JLV). The current legacy version of JLV has become problematic in that the response time for users is very slow. For example, it can take anywhere from 5 to 30 seconds to retrieve external data and present it as widgets in the web UI. Sometimes, queries and responses take even longer, leading to a timeout situation. Additionally, JLV usage has increased to a extremely high level. This level of usage under the current architectural model often overwhelms the external VA VistA systems that receive queries via a Remote Procedure Call (RPC) interface. VistA system owners are complaining that JLV often negatively impacts VistA performance and would like the JLV team to address this. 

My new JLV solution takes a different approach. Instead of querying one or more VistA sites when a user needs the data, it implements an end-to-end ETL pipeline that retrieves, cleans, and prepares all VistA data on a daily basis by using the VA Corporate Data Warehose (CDW) as the data source, as opposed to VistA sites. CDW sources the data as the first step of the ETL pipeline. The pipeline continues by using a Medallion Data Architecture and "bronze", "silver", "gold" parquet files within a data lake. Then, as a final step in the pipeline, the gold data is loaded into a PostgreSQL serving database that is dedicated to the new JLV application. I belive performance under the new model will be significantly improved and will also eliminate the current issue of overwhelming VistA sites with RPC calls.

I have attached two documents related to the current legacy JLV application. These documents have the filename preface, "current". I have also attached a few documents that outline the technical approach and design for the new, modernized JLV application that takes a data warehouse based approach. These documets have the filename preface, "new". I am also taking a different approach to building the user-facing web UI. The current JLV application uses Java, JavaScript, and React as core components of the technology stack. The new system will heavily leverage Python and use FastAPI, HTMX, and Jinja2. Not to bias your response, but my personal preference is server-side rendering as opposed to using a complex JavaScript framework such as React to implement a Single Paga Application (SPA) UI. This is just my preference, I am open to using the best and proper technology stack for the new JLV implementation.

Please review all documents and put together an assessment of the current system challengs and the proposed new architecture. I need feedback on whether this is a good and practical design for the future system. Please take a critical view of the future documents, as opposed to politely agreeing or primarily highlighting the positive or good features. I truly want to know if the new architecture and implementation plan for a modern, data warehouse based solution is a better approach and will provide a better user experience, scalability, and maintainability. Please provide any suggestions on how to improve the overall approach, vision, and architecture for the new JLV application.

I would like to copy/paste your response into a markdown document that I save on my local macOS machine.

---

## Turn 1 — Assistant Response

# Assessment of legacy JLV challenges vs. proposed CDW/ETL-based “new JLV” architecture

## What the legacy JLV documents say (and what that implies)

### 1) User-perceived performance is fundamentally constrained by real-time external calls
The current JLV User Guide explicitly warns users that each widget may take “10 to 90 seconds” to load after selecting a patient, and that users may need to “wait for the widget data to load.” :contentReference[oaicite:0]{index=0} That’s not just a tuning issue; it’s an architectural symptom: the UI experience is tied to multiple downstream systems responding quickly and consistently.

### 2) Scalability is limited by shared downstream dependencies (especially VistA sites)
The System Design Document describes JLV as integrating with multiple external services, explicitly including “VistA Sites.” :contentReference[oaicite:1]{index=1} Under high usage, a design that “fans out” to VistA per user/patient interaction predictably turns into *load amplification* on VistA—exactly the pain you described, and it aligns with the integration model shown in the legacy architecture.

### 3) The current system already needs distributed state/caching to scale the web tier
The SDD notes that to support auto-scaling, JLV uses “an external and distributed caching service … Amazon ElastiCache for Redis,” tied to session management. :contentReference[oaicite:2]{index=2} This is important: even before your modernization, the current architecture has acknowledged horizontal scale concerns at the web tier—but that doesn’t solve the *downstream* bottleneck of real-time RPC/data-service calls.

**Bottom line on the legacy model:** the docs support your thesis: performance and reliability are bounded by real-time dependency chains, and high usage naturally “overdraws” VistA and other external services.

---

## Summary of the proposed “new JLV” approach (as described in your new docs)

Your new architecture replaces real-time VistA fan-out with a daily warehouse-fed serving model:

- Medallion pipeline (Bronze → Silver → Gold Parquet in object storage) :contentReference[oaicite:3]{index=3}  
- Gold loaded into a PostgreSQL serving database for low-latency UI queries :contentReference[oaicite:4]{index=4}  
- Python-first stack with server-side rendering: FastAPI + Jinja2 + HTMX :contentReference[oaicite:5]{index=5}  
- Explicit endpoint conventions for JSON and widget HTML partials :contentReference[oaicite:6]{index=6}  
- Patient identity strategy: ICN as primary identifier, internal SIDs used only for joins in the lake :contentReference[oaicite:7]{index=7}  
- An “aspirational” UX goal: patient overview < 4 seconds for 90% of patients (and no early focus on displaying data freshness in clinician UI) :contentReference[oaicite:8]{index=8}  
- Roadmap emphasizes “vertical slice” validation (end-to-end data → UI first) :contentReference[oaicite:9]{index=9}  

---

## Is the new architecture “better”? Yes—but only if you address the big hidden risks

### Where the new design is genuinely strong

1) **You eliminate VistA load amplification**
Moving the primary read path away from VistA RPC (and onto a serving store) should directly address the VistA performance complaints. This is the cleanest way to stop JLV from being a “distributed denial of service by success.”

2) **You decouple UI latency from external system latency**
The legacy guide’s 10–90 second widget loading expectation :contentReference[oaicite:10]{index=10} is the opposite of what a clinician-facing system should normalize. Your serving DB approach is the right pattern to make “fast most of the time” achievable.

3) **Your medallion + serving DB split is conceptually correct**
Gold Parquet is great for replayability and auditability, and Postgres is a pragmatic serving layer for interactive queries :contentReference[oaicite:11]{index=11}. This is a very standard, defensible analytics/serving pattern.

4) **SSR + HTMX is a valid modernization choice**
FastAPI + Jinja2 + HTMX is a coherent decision in your ADRs :contentReference[oaicite:12]{index=12} and can be excellent for accessibility and maintainable UI patterns (especially for data-heavy pages).

---

## The critical issues you must resolve (or the new system will fail in production)

### 1) **Clinical “freshness” and correctness risk (daily ETL is not automatically acceptable)**
A daily CDW-fed pipeline introduces **data latency** by definition. Even if CDW is updated frequently, you’re still choosing a batch refresh cadence unless you implement incremental/near-real-time updates.

Your plan explicitly says data freshness indicators/ETL status will *initially* be treated as admin concerns, not prominent in the clinician UI. :contentReference[oaicite:13]{index=13}  
That’s a risky product decision for a longitudinal clinical viewer.

**Why it matters:** clinicians will assume JLV is current unless you tell them otherwise. For certain domains (meds, labs, allergies, flags, encounters), “as of” time can change decisions.

**Suggestion:** treat freshness as a first-class UX element, at least at the **domain/widget level**:
- “Data current as of: <timestamp>” per domain
- A clear indicator when a domain is stale/unavailable
- A workflow for “refresh now” for limited, critical domains (even if that refresh is from a more recent feed, not VistA RPC)

If you want to keep VistA off the hot path, consider a **hybrid freshness strategy**:
- Batch CDW for the majority of domains
- Near-real-time deltas (CDC/incremental loads) for a small set of high-risk domains
- Optional “break glass / verify source” links rather than synchronous RPC calls

### 2) **Data completeness risk: CDW may not cover everything JLV shows today**
Legacy JLV integrates with more than VistA (e.g., CVIX, DoD services, etc.). :contentReference[oaicite:14]{index=14}  
If “new JLV” is CDW-only, you may deliver great performance but regress on data breadth unless you explicitly define:
- Which domains are “CDW-backed”
- Which domains remain “external-integrated”
- What the user experience is when a domain is not available in the serving store

**Suggestion:** define a **Domain Sourcing Matrix** early:
- Source of truth (CDW, DoD feed, imaging exchange, etc.)
- Update cadence and expected latency
- SLA and fallback behavior
- Clinical risk level (drives freshness UX + validation rigor)

### 3) **Serving DB scale and query shape risk**
Your design calls for “patient-centric views for low-latency queries” in Postgres :contentReference[oaicite:15]{index=15}. Good. But at national VA scale, you must assume:
- very large tables (labs, meds, notes)
- heavy time-range filtering
- concurrency spikes (clinic hours)
- repeated access patterns (same patient viewed by multiple staff)

**Suggestion:** plan now for:
- Partitioning strategy (often by patient and/or event_date, domain-dependent)
- Index strategy driven by real UI query patterns
- Precomputed “summary” tables for widgets (not just raw event tables)
- Aggressive read optimization (materialized views, denormalized “gold for UI” tables)
- Caching layer for widget queries (legacy JLV already uses distributed caching for scale :contentReference[oaicite:16]{index=16}—your new system will likely need something similar, even if the DB is fast)

Also: your UI pattern includes per-widget endpoints (`/api/dashboard/widget/<domain>/{icn}`) :contentReference[oaicite:17]{index=17}. This is clean, but it can create **N+1 query patterns** if the dashboard loads many widgets at once.

**Suggestion:** add an optional “dashboard bundle” endpoint:
- one request returns the small summary payloads for multiple widgets
- or the server renders the whole dashboard in one pass (SSR advantage), with HTMX used for drill-down rather than initial hydration

### 4) **Operational reliability risk: orchestration, lineage, and backfills**
Your plan correctly flags orchestration as an open question (Prefect/Airflow/ADF). :contentReference[oaicite:18]{index=18}  
At production scale, this is not optional—ETL failures become clinical UX failures.

**Suggestion:** “production-grade pipeline” needs, at minimum:
- idempotent jobs + checkpoints (re-runnable safely)
- late-arriving data handling
- backfill mechanisms (by date range / facility / domain)
- data quality gates in Silver/Gold (row counts, null thresholds, referential expectations)
- lineage metadata: source extract timestamp, pipeline version, load timestamp (you already plan metadata like `LoadDateTime`) :contentReference[oaicite:19]{index=19}

### 5) **Security/ATO scope is bigger than it looks**
Your architecture doc lists the right future-state bullets: SSO, RBAC, audit logging, PHI/PII protections. :contentReference[oaicite:20]{index=20}  
But the *shape* of your new system increases the footprint: you’re now storing broad clinical data centrally (lake + serving DB). That’s a bigger “blast radius” than distributed, on-demand retrieval.

**Suggestion:** treat “data minimization” as a design principle:
- store only what you need for JLV use cases (especially initially)
- define retention rules per domain (notes and some audit-adjacent data get huge fast)
- encrypt everything, isolate environments, formalize secrets management, and design audit events early (don’t bolt on)

---

## UI stack choice: SSR/HTMX vs React SPA (practical take)

Your SSR approach is coherent and already codified as an ADR. :contentReference[oaicite:21]{index=21} I don’t see a technical reason you *must* go back to React, **provided** you anticipate two realities:

1) **Some domains will still need “real” client-side interactivity**
You’re already using Chart.js in your roadmap achievements (JS is fine; the question is *how much*). :contentReference[oaicite:22]{index=22}  
Just avoid the trap of rebuilding a mini-SPA ad hoc across many HTMX fragments without consistent patterns.

2) **SSR makes it easier to ship a fast first view**
That aligns with your goal to beat the legacy “wait for widgets” model :contentReference[oaicite:23]{index=23} and your performance target (<4 seconds for 90%). :contentReference[oaicite:24]{index=24}

**Recommendation:** keep SSR/HTMX, but define strict UX patterns:
- what loads server-rendered vs lazy
- how state is represented (URL params > hidden state)
- standardized partial conventions (errors, empty states, “as of” timestamp)

---

## Concrete improvements I would make to your “new JLV” architecture (prioritized)

### Priority 1 — Make data freshness a first-class product feature
- Add “as of” timestamps per domain (Gold + serving DB rows should carry provenance)
- Show staleness in the clinician UI (not just admin) :contentReference[oaicite:25]{index=25}
- Define which domains must be near-real-time and how you’ll achieve that (incremental loads, deltas, or limited live lookup)

### Priority 2 — Add a domain sourcing + SLA matrix
Use the legacy integration list as a forcing function :contentReference[oaicite:26]{index=26}:
- What’s served from Postgres?
- What’s served from lake?
- What still requires external integration?
- What’s the fallback UX?

### Priority 3 — Engineer the dashboard to avoid N+1 load patterns
You already have clean widget endpoints :contentReference[oaicite:27]{index=27}—add:
- bundled fetch/render for initial dashboard
- caching of common widget summaries
- consistent “details modal” pattern (your roadmap already values widget + full page + modal consistency) :contentReference[oaicite:28]{index=28}

### Priority 4 — Decide the production orchestration platform early
You’ve identified it as an open question :contentReference[oaicite:29]{index=29}; close it with criteria:
- alignment with VA environment (often ADF is politically/operationally viable)
- monitoring + alerting integration
- backfills and replays
- support for parameterized runs (facility/date/domain)

### Priority 5 — Validate serving DB scalability with realistic volumes
Your current implementation success is encouraging, but it’s proven on small synthetic data (e.g., 36 patients) :contentReference[oaicite:30]{index=30}. Before committing:
- generate volumes that mimic “worst clinic day” patterns (labs/meds/notes)
- benchmark: p95 and p99 query latency by endpoint
- test concurrent widget loads and caching effectiveness

---

## Final verdict

Your proposed architecture is **directionally and structurally better** than the legacy real-time RPC fan-out model for **performance, scalability, and protecting VistA**—and the documents you provided strongly support that conclusion (legacy widget latency expectations alone are damning). :contentReference[oaicite:31]{index=31}

However, the modernization will only be “successful JLV” (not just “fast JLV”) if you squarely address:
- **freshness + clinical trust**
- **data completeness across domains**
- **serving DB scale and dashboard query patterns**
- **production orchestration + backfill discipline**
- **security/ATO implications of centralized clinical data**

If you want, I can also produce a “Decision & Risk Register” section you can paste directly into your architecture doc (each risk with severity, likelihood, mitigation, and an owner) using the exact structure of your existing docs and ADR style.

---

## Turn 2 — User Prompt

This is very helpful feedback that I will review in further detail. As a follow-up question, please assess the value and feasibility of a hybrid approach that augments the new CDW (1 day latency) issue with realtime RPC calls to VistA for only the current day (or perhaps the current day and t-1). These could be the same full data requests, or requests for smaller payload responses that can be a "lazy load" type mechanism and the user can request the rest of the data if needed. Something to that effect. I am trying to convey the spirit of a hybrid architecture that solve the data currency issue in an efficent way. Please provide feedaback and advice/recommendations.

---

## Turn 2 — Assistant Response

## Hybrid “CDW + real-time VistA for today” approach: value, feasibility, and the traps

A hybrid model can be *very* high-value if you keep it narrowly scoped and operationally disciplined. It can also quietly drift back into “legacy JLV with extra steps” if you don’t put hard guardrails around what gets called, how often, and for whom.

Below is the practical assessment and a recommended way to structure it.

---

## The value proposition

### What you gain
- **Clinical trust**: “today’s changes” (new meds, labs, orders, admissions, flags) are exactly where latency hurts decisions.
- **Better UX without sacrificing your core win**: most browsing/longitudinal review hits the serving DB (fast), while the user gets a clear “today overlay” that is fresh.
- **Targeted load on VistA**: if you constrain the real-time scope to small deltas and a small set of domains, you can dramatically reduce RPC volume vs. legacy fan-out.

### Where it’s especially valuable
Hybrid makes the most sense for domains where:
- Data is **high-impact if stale**
- “Today’s delta” is **small relative to history**
- There’s a clean **filter by date/time** or “since last seen” concept

Typical candidates:
- **Meds / orders** (especially changes, new starts/stops)
- **Labs / vitals** (new results today)
- **Admissions / transfers** (patient location/status)
- **Allergies / reactions**
- **Patient flags / advisories** (high safety impact)

---

## Feasibility: yes, but only with constraints

### What makes it feasible
- You already have a serving model. Add a **“freshness overlay service”** that fetches deltas for a few domains and merges/overlays them in the UI.
- You can implement **lazy-load** on the client (HTMX) so you aren’t fetching deltas unless the user is actually looking at that widget or a “refresh” affordance.

### What makes it risky
- If you do “the same full data requests” via RPC even for “today,” you’re back to **expensive fan-out**.
- If you allow per-widget real-time refresh with no rate limits, a busy clinic can hammer VistA again—just in a different pattern.
- You create a **two-source-of-truth reconciliation problem** (CDW snapshot vs. real-time deltas) that must be handled consistently.

---

## The architectural pattern that works

### Pattern: Snapshot + Overlay (not “two full sources”)
1) **Default view** uses CDW-derived serving DB (fast, stable).
2) Each widget optionally shows a **“Today updates”** section:
   - fetched from VistA *as deltas only*
   - merged into the display
3) The UI explicitly communicates:
   - “Snapshot as of: <timestamp>”
   - “Today updates checked at: <timestamp>”
   - a one-click “Recheck today” (throttled)

### Keep overlay payloads small and structured
Prefer delta calls that return:
- only records within **today (and optionally t-1)**  
- or records **since <timestamp>**
- plus a minimal “summary first” payload:
  - counts, latest timestamp, “new since last check”
  - then expand to full detail on demand

If VistA RPC APIs don’t support deltas cleanly, you can still approximate:
- “Get latest N items” (bounded)
- “Get items after last known event time” (if supported)
- “Get status/summary only” first, then drill down

---

## The guardrails you should treat as non-negotiable

### 1) Hard limits on RPC volume
- **Per user / per patient** rate limits (e.g., no more than once per X minutes per domain)
- **Global concurrency limits** per VistA site (circuit breaker)
- **Timeouts + graceful degradation** (“today updates unavailable right now; snapshot shown”)

### 2) Domain allowlist (start tiny)
Don’t make “real-time overlay” a generic mechanism at first.
Start with **2–4 domains**, validate load, then expand.

### 3) Cache real-time overlays aggressively
Even if you avoid Redis for the main app, you will likely want it (or equivalent) here:
- cache “today overlay” results for short TTL (e.g., 1–5 minutes)
- dedupe concurrent requests: if 8 clinicians open the same patient, they should share the same overlay result where safe/allowed

### 4) Clear reconciliation rules
Decide how you present conflicting data:
- If snapshot shows Med A active, overlay shows Med A discontinued today:
  - UI should show the discontinuation clearly and prefer the overlay for “current state”
- Maintain a simple precedence rule:
  - **Overlay wins for “current status”**
  - Snapshot remains for historical context

### 5) Audit and traceability
Every overlay fetch should be logged with:
- patient, domain, VistA site, latency, outcome, and whether served from cache
This becomes your evidence when VistA owners ask “are you hammering us?”

---

## Recommended implementation approach (practical)

### Phase 1: “Freshness indicators + manual recheck”
- Show snapshot “as of” per domain
- Add a button: “Check for today’s updates” per domain (lazy-load)
- Rate-limit heavily
- Measure usage + load impact

### Phase 2: “Auto-check once per patient session”
- When user opens a patient:
  - auto-check overlays for only your top 2–3 high-risk domains
  - everything else stays manual
- Add caching and request coalescing

### Phase 3: “Smarter deltas”
- Move from “today only” to “since last check” where possible
- Reduce payload sizes further
- Tune based on telemetry

---

## Alternatives that may be better than RPC (if feasible in your environment)

If your goal is “fresh today,” but you want to avoid live VistA fan-out:
- **Incremental loads / CDC** into your lake/serving DB multiple times per day for high-risk domains (even hourly)
- A near-real-time feed via a VA-standard integration layer (depends on what you can access organizationally)

If you can do that, you can shrink the RPC overlay to “break glass only,” which is ideal.

---

## My recommendation

A hybrid approach is worth pursuing **if you implement it as “delta overlay” with strict guardrails**, not as “CDW plus full real-time calls.”

If you want a simple, defensible rule set to start with:

- **Serving DB is the default** for everything.
- **Overlay is limited to:**
  - 3 domains (e.g., meds, labs, flags)
  - today (and optionally t-1) only
  - cached 2–5 minutes
  - max 1 overlay refresh per domain per patient per clinician every N minutes
  - global circuit breaker per VistA site

That gives you a path to address data currency while preserving your main win: performance and protecting VistA.

If you paste a list of the specific widgets/domains you plan to support in your first MVP, I can propose an initial allowlist + overlay strategy and a concrete set of RPC throttling/caching rules for each domain.

---

## Turn 3 — User Prompt

Attached are design documents for the first set of clinical domains that will be implemented on the dashboard as "widgets" and from a sidbar menu area as more detailed and dedicated pages.

---

## Turn 3 — Assistant Response

# Hybrid “CDW + limited real-time VistA RPC” overlay: value, feasibility, and how to do it safely

A hybrid approach can be **high-value** because it directly addresses the one weakness of a CDW-centric design: **clinical currency**. At the same time, it can accidentally re-introduce the very problem you’re trying to eliminate (VistA load / latency / timeouts) if it isn’t **tightly scoped, rate-limited, cached, and made optional**.

Below is a critical assessment and a set of concrete recommendations.

---

## Why a hybrid can be worth it

Your new architecture is fundamentally aiming to replace “on-demand real-time aggregation from many systems” (which legacy JLV explicitly does) with “pre-staged data optimized for low-latency UI.” The legacy SDD frames JLV as pulling disparate systems “in real time” for browser display, which aligns with the performance pain you’re seeing at scale. :contentReference[oaicite:32]{index=32}

A hybrid overlay is worth considering if:

- **Clinicians truly need “today” data** for a subset of domains (e.g., meds administered this morning, new vitals, a lab that resulted an hour ago).
- The “as of yesterday” gap creates **clinical distrust** (“I don’t trust JLV because it’s stale”).
- You can keep real-time calls limited to **a small number of high-value, high-change** slices.

Done right, the hybrid becomes a **“freshness veneer”** over the serving DB, not a return to full real-time aggregation.

---

## The biggest risk: you accidentally rebuild legacy JLV’s failure modes

If you allow UI-driven RPC calls to grow into “just fetch everything real-time,” you will drift back toward the legacy operating model (lots of concurrent, user-triggered, fan-out calls) that overloads sites.

So the hybrid must be designed to **fail safely**:

- If the real-time path is slow or unavailable, the UI still works from the serving DB.
- The system *never* devolves into broad “patient context triggers dozens of RPCs.”
- VistA owners can see and trust that load is bounded (quotas + monitoring + circuit breakers).

---

## A practical hybrid pattern that stays bounded

### Pattern A (recommended): “Delta overlay” service (today / t-1 only)

**Idea:** The UI renders from PostgreSQL (CDW-derived gold), and then optionally overlays a **small delta dataset** representing “today (and maybe t-1)” from VistA.

Key properties:

1. **Narrow scope by domain**
   - Start with 1–3 domains where currency matters most (often: meds, vitals, labs/clinical results).
   - Do *not* do this for every widget.

2. **Narrow scope by time**
   - Today only, or today + t-1, with explicit “start_time/end_time” constraints.

3. **Narrow scope by payload**
   - Return a minimal “summary delta” first (counts, most recent event timestamp, newest N items), and only fetch details on demand.

This aligns with a pattern you’re already using successfully: **lazy loading** of sensitive or heavy details (your Patient Flags design loads the list first and fetches narrative/history only on user action). :contentReference[oaicite:33]{index=33}

### Pattern B: “User-invoked refresh” instead of automatic refresh

Instead of auto-calling RPC when a patient is selected, add an explicit per-domain control:

- “Refresh today’s vitals (real-time)” button
- Shows last refresh timestamp + status
- Enforces a cooldown (e.g., 2–5 minutes)

This single decision dramatically reduces accidental traffic spikes.

### Pattern C: “As-of + freshness indicator” UX (non-negotiable)

To avoid clinical confusion and support governance, every domain should show:

- **As-of timestamp for the CDW snapshot**
- **As-of timestamp for real-time delta (if enabled)**
- A clear merge rule: “CDW + Today’s Updates”

This fits nicely with your server-rendered approach: the base page loads fast, then HTMX pulls in optional partials. Your newer architecture explicitly supports a serving DB for low-latency UI queries via FastAPI. :contentReference[oaicite:34]{index=34}

---

## What you must build to make the hybrid feasible (and not anger VistA owners)

### 1) A dedicated “Real-time Gateway” (do not call VistA directly from general app routes)

Put all RPC interaction behind a single internal service with:

- **Per-site rate limiting**
- **Per-user and per-patient throttles**
- **Aggressive caching** (patient+domain+time-window key)
- **Circuit breakers** (trip on latency/error rate and fall back to CDW)
- **Request coalescing** (100 users open the same patient ≠ 100 RPC calls)

Legacy JLV already uses distributed caching for session scaling (Redis/ElastiCache) in its AWS deployment. That’s a hint that caching is operationally accepted in this ecosystem—reuse the concept for delta caching. :contentReference[oaicite:35]{index=35}

### 2) Strict caching/TTL rules (example defaults)

- **TTL 5–15 minutes** per patient+domain for “today delta”
- **Stale-while-revalidate** behavior:
  - Serve cached delta instantly
  - Refresh in background if TTL expired
- **Max refresh frequency** per user/session (cooldown)

### 3) A bounded data contract (“delta schema”) per domain

Do not return raw RPC payloads to the UI.

Instead define a minimal canonical delta model, e.g.:

- `event_time`
- `type` (med admin, new order, result)
- `summary fields`
- `source_site`
- `source="vista_rpc"`
- optional `details_url`

This prevents the hybrid from becoming “two parallel implementations of the same domain.”

### 4) A deterministic merge rule

You need a clear rule for combining:

- CDW baseline (yesterday)
- Today delta (RPC)

Examples:
- **Append-only** for vitals/labs (“show newest first; tag the source”)
- **Override** for some status fields (“today’s status wins”)
- **De-dup** using stable keys when possible (hard part)

If de-dup keys aren’t stable, prefer a UI presentation that tolerates duplicates but makes source/time explicit, rather than silently “guessing” merges.

---

## Where “lazy load” fits especially well

You mentioned “smaller payloads” and lazy-loading details. That’s exactly right.

A concrete approach:

1. **Widget loads from PostgreSQL** instantly (fast path).
2. In parallel, fetch **real-time summary delta** (count + most recent timestamp + newest 3 items).
3. Only if the user expands the widget / opens the full page do you fetch:
   - full “today” list
   - then per-item details

Your Patient Flags domain already demonstrates the UI mechanics for this (load list first; load narrative/history only on reveal). :contentReference[oaicite:36]{index=36}  
And your Medications design shows you’re comfortable with “minimal custom JS + HTMX triggers” for progressive detail interactions. :contentReference[oaicite:37]{index=37}

---

## My recommendations (if you want this to succeed in VA reality)

1. **Start CDW-only first, then add hybrid only where proven necessary.**  
   Don’t speculate—instrument usage and gather clinician feedback per domain.

2. **Make real-time delta explicitly bounded and optionally user-invoked.**  
   Auto-refresh at patient open is what causes the worst spikes.

3. **Build (and show) “VistA Load Budget” reporting.**  
   Per site: calls/minute, latency, errors, and top requesting functions/domains. This is how you win back trust with site owners.

4. **Prefer “today-only deltas,” not full re-queries.**  
   The hybrid should *never* be “call the same full data request but just for today.” It should be “what changed today.”

5. **Be open to a non-RPC alternative for freshness (if available later).**  
   Even if RPC is the first feasibility path, keep the gateway’s interface abstract so you could later swap to a push/event feed or more frequent warehouse increments without rewriting the UI and domain logic.

---

## Bottom line

A hybrid can be a strong design *if* you treat real-time as a **small, rate-limited, cache-backed delta overlay**, not as a return to full real-time aggregation.

If you want, I can propose a **reference design** (components + sequence diagrams + suggested endpoints + caching keys + per-domain rollout order) that matches your current FastAPI/HTMX patterns and your existing “lazy-load details” approach.

---

## Turn 4 — User Prompt

Yes, please create a proposed reference design with your recommended approach that is compatible with the current FastAPI/HTMX patterns and the existing "lazy-load details" approach. I would like a fairly thorough specification that includes a summary of the current challenges and the goals for the new system. Plus, of course, as comprehensive a design as you are able to create based on your understanding of the current system state and desired future state. My goal is to develop a high-value, high-performant application that users both love and trust. I realize that is a high bar, but I would like to aim high.

---

## Turn 4 — Assistant Response

# Reference design: Modern JLV with CDW serving DB + bounded “today” real-time delta overlay

This is a proposed **reference architecture + implementation spec** that fits your current **FastAPI + Jinja2 + HTMX** approach :contentReference[oaicite:38]{index=38} and your proven **lazy-load details** pattern (e.g., Patient Flags narrative/history loads only when revealed) :contentReference[oaicite:39]{index=39}.

It assumes the **primary path** is CDW→Medallion→PostgreSQL serving DB :contentReference[oaicite:40]{index=40} and adds an **optional, tightly bounded overlay** for “today / t-1” freshness.

---

## 1. Summary of current challenges

### 1.1 User experience and trust
Legacy JLV widgets can take **10–90 seconds** to load depending on date ranges :contentReference[oaicite:41]{index=41}, and you’re seeing 5–30+ seconds (including timeouts). That’s a trust killer: clinicians stop believing the system is reliable, even when the data is correct.

### 1.2 Scalability and VistA impact
The legacy model triggers **interactive, user-driven fan-out** to external systems, which:
- Creates high variance latency (best case fast; worst case timeouts)
- Amplifies load on VistA RPC endpoints as usage scales
- Causes the “JLV is hurting my site” complaints you’re hearing

### 1.3 Maintainability and operability
When UI performance depends on many upstream systems and per-site behavior, engineering ends up fighting:
- Site-specific RPC quirks and latency
- Caching bugs and “why is this patient slow?”
- Hard-to-test end-to-end behavior

---

## 2. Goals for the modernized system

### 2.1 Product goals
1. **Fast**: widgets and pages feel instant (sub-second), consistently.
2. **Trusted**: clinicians can clearly see what’s current vs. “as of last refresh,” with explicit timestamps.
3. **Safe for VistA**: no uncontrolled interactive load against sites.
4. **Maintainable**: domain implementations follow repeatable patterns (routes + db layer + templates) :contentReference[oaicite:42]{index=42}.
5. **Secure / auditable**: sensitive content is minimized, gated, and logged (your flags pattern is a great precedent) :contentReference[oaicite:43]{index=43}.

### 2.2 Technical goals
- **CDW serving DB is the default** for all widgets/pages :contentReference[oaicite:44]{index=44}.
- Optional “today delta” calls are:
  - bounded (time window, payload size)
  - cached and rate-limited
  - safe to fail (never blocks baseline UI)

---

## 3. Architectural principles

1. **Baseline-first rendering** (SSR): render from PostgreSQL first; progressive enhancement via HTMX for optional additions :contentReference[oaicite:45]{index=45}.
2. **Bounded freshness overlay**: “today” is a *delta*, not a second full retrieval system.
3. **Lazy-load sensitive and heavy details**: follow the same pattern as Patient Flags narrative/history and medication row details :contentReference[oaicite:46]{index=46} :contentReference[oaicite:47]{index=47}.
4. **Isolation of real-time risk**: real-time RPC access must live behind a dedicated gateway with guardrails.
5. **Make currency visible**: every domain exposes “as-of” information (CDW snapshot + delta refresh timestamp).

---

## 4. Proposed high-level architecture

### 4.1 Components

**A) ETL + Lakehouse (daily)**
- CDW → Bronze/Silver/Gold parquet → PostgreSQL serving DB :contentReference[oaicite:48]{index=48}

**B) Web UI App (FastAPI + Jinja2 + HTMX)**
- Renders dashboard + domain pages from serving DB :contentReference[oaicite:49]{index=49}
- Uses domain routing patterns you’ve already standardized (Pattern A/B) :contentReference[oaicite:50]{index=50}
- Hosts HTMX endpoints like `/api/dashboard/widget/<domain>/{icn}` :contentReference[oaicite:51]{index=51}

**C) CCOW Vault (separate service)**
- Patient context store (already in your architecture) :contentReference[oaicite:52]{index=52}
- App queries vault on page load and when user refreshes context :contentReference[oaicite:53]{index=53} :contentReference[oaicite:54]{index=54}

**D) Real-time Delta Gateway (new, separate service strongly recommended)**
- Only component allowed to talk to VistA RPC
- Implements caching, throttling, circuit breakers, coalescing
- Provides “today / t-1” deltas for selected domains only

**E) Shared Cache (Redis strongly recommended)**
- Stores delta results and “in-flight” locks for request coalescing
- Also stores rate-limit counters and circuit breaker state

**F) Audit + Observability**
- Structured logs, metrics, tracing
- Explicit “sensitive access” logging pattern (as in flags) :contentReference[oaicite:55]{index=55}

---

## 5. User flows and request flows

### 5.1 Patient selection / context (baseline)
This matches your plan and roadmap approach: query CCOW on load, and provide an explicit user action to set or refresh context :contentReference[oaicite:56]{index=56} :contentReference[oaicite:57]{index=57}.

**Flow**
1. Browser loads page
2. Web UI app calls CCOW: `GET /ccow/active-patient`
3. If present, UI app queries serving DB for demographics and renders header
4. Dashboard widgets load via HTMX widget endpoints (baseline)

### 5.2 Dashboard widget load (baseline SSR + HTMX)
You already have this working well (e.g., meds widget endpoint returning an HTMX fragment, and vitals widget HTML endpoint) :contentReference[oaicite:58]{index=58} :contentReference[oaicite:59]{index=59}.

**Key requirement**: baseline widget endpoints never call VistA.

### 5.3 “Today updates” delta overlay (optional and bounded)
**Critical design choice**: the UI should *not* automatically trigger real-time RPC calls for every patient + every widget.

Instead:
- baseline loads instantly
- UI shows a “Freshness” line + a “Refresh Today” control for domains that support it
- clicking refresh triggers a delta fetch via the gateway

---

## 6. Real-time Delta Gateway design

### 6.1 What it does (and does not do)

**Does**
- Fetch today/t-1 deltas for a *short list* of domains (start with Vitals + Medications; expand only if proven valuable)
- Cache delta responses with TTL
- Enforce hard rate limits per site/patient/user
- Coalesce concurrent requests for same key
- Trip circuit breakers when a site is slow/unhealthy

**Does not**
- Perform broad “get everything” calls
- Replace the serving DB for normal reads
- Block baseline UI rendering

### 6.2 Deployment model
Recommended: run as a separate FastAPI service (similar to CCOW Vault being separate) :contentReference[oaicite:60]{index=60}.

Why: it makes it easier to prove to VistA owners that:
- only one controlled component calls RPC
- traffic is bounded and measurable
- you can scale/disable it independently

### 6.3 Delta API surface (gateway internal API)

**Primary endpoints**
- `POST /rt/patient/{icn}/refresh`
  - body: `{ "domains": ["vitals","medications"], "window": "today|today_t-1", "force": false }`
  - returns: per-domain delta status + summary (and links)

- `GET /rt/patient/{icn}/{domain}/status?window=today`
  - *must not call VistA*
  - returns: cached delta availability + timestamps + whether refresh allowed

- `GET /rt/patient/{icn}/{domain}/delta?window=today`
  - may call VistA if cache miss + allowed
  - returns: delta payload (summary + small list of new items)

**Cache keys**
- `rt:{site}:{icn}:{domain}:{window}` → delta payload (TTL 5–15 min)
- `rt:lock:{site}:{icn}:{domain}:{window}` → in-flight lock (TTL 30–60s)

### 6.4 Guardrails (non-negotiable)

**Rate limiting (example defaults)**
- Per site: 30 requests/minute (token bucket)
- Per patient per site: 6 requests/minute
- Per user: 10 requests/minute
- Cooldown per domain button in UI: 2–5 minutes

**Circuit breaker**
- Trip if latency p95 > X seconds or error rate > Y% for rolling window
- While open: return “delta unavailable; showing CDW snapshot” without attempting calls

**Request coalescing**
- If 50 users click refresh for same patient/domain within 5 seconds:
  - only 1 RPC call executes
  - others await cached result or receive “refresh in progress”

---

## 7. How the Web UI integrates with the gateway (FastAPI/HTMX-compatible)

### 7.1 Browser-facing routes live in the Web UI app
Keep your existing conventions:
- JSON APIs: `/api/patient/{icn}/<domain>` :contentReference[oaicite:61]{index=61}  
- Widget HTML: `/api/dashboard/widget/<domain>/{icn}` :contentReference[oaicite:62]{index=62}  
- Full pages: `/patient/{icn}/<domain>` :contentReference[oaicite:63]{index=63}  

Add **UI-owned** delta endpoints that proxy to the gateway:

- `GET /api/patient/{icn}/{domain}/freshness` → returns **HTML fragment** (status line + refresh button)
- `POST /api/patient/{icn}/{domain}/refresh-today` → returns **HTML fragment** (delta banner + small list)
- `GET /api/patient/{icn}/{domain}/today-items` → optional detail list (paged/limited)

### 7.2 Widget template pattern (baseline + freshness strip)

Within `app/templates/partials/<domain>_widget.html`:

- Render baseline content from Postgres
- Include a small “freshness strip” div that HTMX loads quickly and safely

Example (conceptual):

```html
<div class="widget">
  <!-- baseline content rendered from Postgres -->

  <div class="widget-freshness"
       hx-get="/api/patient/{{ patient.icn }}/vitals/freshness"
       hx-trigger="load"
       hx-swap="innerHTML">
    <span class="text-muted">Checking freshness…</span>
  </div>

  <div class="widget-delta" id="vitals-delta-{{ patient.icn }}"></div>
</div>
````

Important: `/freshness` should **not** call VistA; it reads cached status from the gateway (or shows “Refresh available”).

### 7.3 Refresh button UX (bounded + explicit)

The freshness fragment returns:

* “CDW as-of: <timestamp>”
* “Today delta: last refreshed <timestamp> (or not yet)”
* “Refresh today” button (disabled if cooldown / breaker open)

This keeps user trust high and avoids silent background RPC traffic.

---

## 8. Domain-by-domain “today delta” strategy (start narrow)

### 8.1 Recommended initial domains

**Vitals**

* You already have a clear separation between:

  * all vitals JSON (`GET /api/patient/{icn}/vitals`)
  * recent summary for widget (`GET /api/patient/{icn}/vitals/recent`)
  * widget HTML endpoint (`GET /api/dashboard/widget/vitals/{icn}`) 
* Delta overlay can return: “new vitals since midnight” + “latest per vital type”

**Medications**

* You already model “recent meds for widget” plus “details endpoint” for expandable rows 
* Delta overlay can return:

  * New inpatient administrations in last 24h
  * New outpatient orders since t-1
  * Keep payload small (top N)

### 8.2 Domains that probably should *not* use real-time initially

* **Patient Flags**: sensitive, high-risk, plus you already have strong lazy-load controls and access logging; real-time adds risk without clear benefit for “today” 
* **Allergies**: changes are relatively infrequent; your baseline performance is already excellent (~26–31ms in testing) 

---

## 9. Data contracts: delta payload shapes

### 9.1 Generic delta response

```json
{
  "patient_icn": "ICN100001",
  "domain": "vitals",
  "window": "today",
  "status": "fresh|stale|unavailable|in_progress",
  "cdw_as_of": "2025-12-12T05:00:00Z",
  "delta_refreshed_at": "2025-12-13T14:22:10Z",
  "source_site": "580",
  "items_new_count": 3,
  "items": [
    { "id": "vital:123", "event_time": "2025-12-13T13:10:00Z", "summary": "BP 150/92" }
  ],
  "ttl_seconds": 600
}
```

### 9.2 “Summary first, details later”

For items that need more data:

* return an `id` and a short `summary`
* UI can lazy-load details via HTMX using a dedicated endpoint (same pattern as flags history reveal and medication details)  

---

## 10. Observability, SLOs, and “prove it to VistA owners”

### 10.1 Proposed SLOs

* Baseline widget HTML endpoints: p95 < 300ms
* Baseline JSON endpoints: p95 < 300ms
* Delta refresh click: p95 < 2s (acceptable), but must never block baseline UI
* Error budget: delta can fail; baseline must not

(You already have evidence your SSR+HTMX approach can be very fast in practice; allergies testing shows ~26–31ms endpoints) .

### 10.2 Required metrics (gateway)

* Requests by site/domain/window
* Cache hit ratio
* Rate-limit rejects
* Circuit breaker opens
* RPC latency p50/p95/p99
* “Top patients” (to detect runaway scenarios)

### 10.3 Required reporting (for governance)

A simple dashboard/table that VistA owners can see:

* “Max calls/min per site” and whether you stayed within it
* “Average latency and error rate per site”
* “Most common domains requested”

This is how you prevent “you’re hurting my system” from becoming political again.

---

## 11. Security and privacy considerations

1. **Do not cache sensitive narratives** unless absolutely necessary; if you ever do, TTL should be very short and access must be audited.
2. Follow your own proven pattern:

   * separate sensitive data into separate tables/endpoints
   * lazy-load it only when explicitly requested
   * log access (the flags design spells this out clearly) 
3. Authentication/authorization is currently “future,” but delta overlays increase risk; plan for permission gating earlier for any real-time calls.

---

## 12. Implementation roadmap (practical steps)

### Phase 0: Baseline stability (already largely aligned with your docs)

* Ensure all widgets/pages render from Postgres only 
* Ensure CCOW refresh reliably triggers widget reload (you already fixed a related issue by moving from `htmx.ajax()` to `fetch()`) 

### Phase 1: Add freshness UI (no VistA calls yet)

* Add `cdw_as_of` metadata into templates (global + per-domain)
* Implement `/api/patient/{icn}/{domain}/freshness` fragments that show:

  * CDW as-of timestamp
  * “Today updates available: click refresh” (but no gateway yet)

### Phase 2: Introduce gateway with “status only”

* Deploy gateway + Redis
* Implement `GET /rt/.../status` to return cached info only
* Wire UI freshness fragment to display real cache state (still no RPC)

### Phase 3: Enable refresh for **Vitals only**

* Implement delta fetch with strict bounds
* Add refresh button + cooldown
* Add metrics and VistA load reporting

### Phase 4: Add Medications delta

* Keep payload small; focus on “new since midnight / last 24h”
* Use your existing details endpoint patterns for deeper drill-down 

---

## 13. What I would challenge (to keep the bar high)

1. **Avoid silent auto-refresh of real-time deltas.**
   Even if it feels “modern,” it’s how you accidentally recreate legacy load patterns at scale.

2. **Be ruthless about domain selection.**
   If a domain isn’t meaningfully time-sensitive, don’t add real-time complexity.

3. **Make “as-of” and “refresh” explicit everywhere.**
   Trust comes from transparency, not from pretending everything is “real-time.”

4. **Treat “site selection” as a real problem.**
   For “today” data, choosing the wrong facility/site can mislead users. Start with a conservative strategy (e.g., primary station from demographics/search results) and evolve it as you add encounter context (your search results already include station in the roadmap) .

---

If you want, I can extend this into a **domain-specific mini-spec** for (a) Vitals delta overlay and (b) Medications delta overlay that includes:

* exact HTMX fragments
* gateway caching keys/TTLs
* suggested RPC payload minimization strategy
* merge/display rules (“CDW baseline + Today updates” without risky de-dup logic)

---

## Turn 5 — User Prompt

No thank you, this is the information I need for now.
