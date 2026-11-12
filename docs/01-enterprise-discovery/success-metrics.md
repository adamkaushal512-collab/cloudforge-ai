# CloudForge AI: Success Metrics, Cost, and Capacity

| Field | Value |
|---|---|
| Document | Success Metrics, Cost, and Capacity |
| Phase | 01: Enterprise Discovery |
| Status | Draft (not approved) |
| Related | `platform-vision.md`, `stakeholders.md`, `use-cases.md`, `functional-requirements.md`, `nonfunctional-requirements.md`, `security-governance.md`, `coverage-audit.md` |

---

## 1. Purpose and Disclaimer

This document defines how CloudForge AI's success will be measured. It also sets out hypothetical load, cost, and capacity assumptions for planning.

> **Disclaimer:** CloudForge is a fictional enterprise.
>
> - **No metric in this document has been measured.**
> - **No baseline exists.**
> - **No budget has been approved.**
> - **No live provider price has been quoted.**
>
> Every numeric target is **[Target]**: proposed, not committed. Every load and cost figure in §5–§6 is **hypothetical and illustrative**: it is neither a forecast nor production data.

### 1.1 Labels

The labels are the same as in all earlier discovery documents:

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input, not as a measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal. It is not measured or committed. |
| **[Open]** | An unresolved question or value. |

**Owners** are proposed, following the `stakeholders.md` RACI, and are **[Assumption]**: no owner has accepted.

---

## 2. Business Outcomes and Value Proposition

### 2.1 Value Proposition

CloudForge AI replaces duplicated, team-built AI infrastructure with shared services owned by the platform team **[Decision]**. This lets about 20 engineering teams **[Decision]** build AI applications faster, more securely, and with visible cost.

### 2.2 Intended Business Outcomes

All outcomes below are **[Assumption]**. None has been measured, and none has a baseline (vision Q1).

| Outcome | Vision goal | Leading KPIs | Lagging evidence |
|---|---|---|---|
| Less duplicated AI infrastructure | G1 | KPI-01, KPI-03 | Team-owned gateways, RAG stacks, and the like are retired over time |
| Faster time to first AI feature | G2 | KPI-04, KPI-05 | Time from team onboarding to first production AI feature **[Open]** |
| Consistent security and governance | G3 | KPI-14–KPI-18 | Security assessments; no cross-tenant incidents |
| Transparent, attributable AI spend | G4 | KPI-10–KPI-13 | FinOps can report spend by team and workload |
| Unified observability | G5 | KPI-19–KPI-24 | Incidents attributed correctly to platform, provider, or tenant |
| Support for LLM, agentic, and ML workloads | G6 | KPI-25–KPI-31 | All three initial workloads run on the platform |

---

## 3. KPI Definitions

**Format:** Each KPI states its numerator, denominator, unit, data source, collection frequency, proposed owner, measurement method, and target. "Baseline: none" applies to every KPI unless stated otherwise.

### 3.1 Adoption and Business

#### KPI-01: Team adoption
- **Target:** 16 of 20 teams (80%) **[Target]**. The time horizon is **[Open]** (vision Q2).
- **Definition:** **[Open]**. Proposed candidate **[Assumption]**: a team counts as adopted if it has at least one project with production traffic through the LLM gateway, or another platform service, in the trailing 30 days.
- **Numerator:** Teams meeting the adoption definition.
- **Denominator:** Teams in scope. This is 20 **[Decision]**; whether the denominator is fixed or tracks reorganizations is **[Open]**.
- **Unit:** Count and percentage.
- **Data source:** Tenant registry (FR-001) plus usage records (FR-031).
- **Frequency:** Monthly.
- **Owner:** Platform eng (A), reported to Engineering leadership.
- **Method:** Join tenants to teams; count teams whose tenants meet the definition.

#### KPI-02: Initial workloads live on the platform
- **Target:** 3 of 3 initial workloads in production on platform services **[Target]**. Horizon **[Open]**.
- **Numerator:** Initial workloads (UC-KA, UC-OA, UC-PM) whose use-case acceptance criteria pass in production.
- **Denominator:** 3.
- **Unit:** Count.
- **Data source:** Release records; acceptance-test evidence.
- **Frequency:** Per release.
- **Owner:** Platform eng.
- **Method:** Review against `use-cases.md` acceptance criteria.

#### KPI-03: Duplicated infrastructure retired
- **Target:** **[Open]**. A baseline inventory is needed first (SQ2).
- **Numerator:** Team-owned AI infrastructure components retired after migration.
- **Denominator:** Components in the baseline inventory.
- **Unit:** Percentage.
- **Data source:** Discovery inventory (not yet created).
- **Frequency:** Quarterly.
- **Owner:** Engineering leadership.
- **Method:** Periodic inventory survey.

### 3.2 Developer Experience

#### KPI-04: Onboarding time
- **Target:** < 30 minutes to first authenticated gateway request **[Target]**. The statistic (median, p90, or percentage of tenants) is **[Open]** (NFR-Q5).
- **Numerator / denominator:** For the percentage form: onboardings completed in under 30 minutes, divided by onboardings completed.
- **Unit:** Minutes; percentage.
- **Data source:** Onboarding start and end events (FR-004).
- **Frequency:** Continuous; reported monthly.
- **Owner:** Platform eng.
- **Method:** Elapsed time between events. Before launch, measured in moderated usability tests (NFR-050), which have not yet been run. The start and end events are **[Open]** (vision Q10).

#### KPI-05: Onboarding completion rate
- **Target:** **[Open]**.
- **Numerator:** Onboardings reaching a first successful request.
- **Denominator:** Onboardings started.
- **Unit:** Percentage.
- **Data source:** FR-004 events.
- **Frequency:** Monthly.
- **Owner:** Platform eng.
- **Method:** Event funnel.

#### KPI-06: Developer satisfaction
- **Target:** **[Open]**; the first survey sets the baseline.
- **Numerator / denominator:** Favourable responses divided by responses.
- **Unit:** Percentage or score.
- **Data source:** Survey (NFR-054).
- **Frequency:** Quarterly.
- **Owner:** Platform eng.
- **Method:** Survey; instrument **[Open]**.

### 3.3 Reliability, Performance, and Capacity

#### KPI-07: Gateway availability
- **Target:** ≥ 99.9% over a rolling 30-day window **[Target]**. The 43.2-minute equivalent error budget is in NFR §3.3.
- **Numerator:** Valid requests not ending in a platform-attributable failure.
- **Denominator:** Valid requests.
- **Unit:** Percentage.
- **Data source:** Gateway request metrics by error class (FR-038).
- **Frequency:** Continuous; reported daily and per 30-day window.
- **Owner:** SRE.
- **Method:** NFR-001/NFR-002. **Unresolved [Open]:**
  - the exact success and error definitions, including partial streams and failover;
  - whether upstream provider failures count (vision Q3, NFR-Q1). The NFR draft excludes them from the SLO and tracks them separately **[Assumption]**.

#### KPI-08: Gateway-added latency (p95)
- **Target:** p95 < 200 ms, excluding model inference **[Target]**.
- **Numerator / denominator:** Not a ratio. This is the 95th percentile of the gateway-added latency distribution.
- **Unit:** Milliseconds.
- **Data source:** Tracing spans: the gateway span minus the upstream span.
- **Frequency:** Continuous; reported daily.
- **Owner:** Platform eng.
- **Method:** NFR-007. Histogram-based percentiles; load tests use a mock provider.

#### KPI-09: Initial capacity test
- **Target:** Pass at 100 concurrent requests **[Target]** under the defined workload. Pass means p95 gateway-added latency < 200 ms and a platform-attributable error rate < 0.1% for 30 minutes (NFR-013).
- **Defined workload (proposed) [Assumption]:**
  - 100 closed-loop clients;
  - mock provider with fixed latency;
  - 2,000 input and 500 output tokens per request, matching §5;
  - at least 3 synthetic tenants;
  - one noisy-neighbour aggressor in a separate run.
- **Unit:** Pass/fail, plus a report of percentiles and error rate.
- **Data source:** Load-test report.
- **Frequency:** Before slice launch; on data-plane releases.
- **Owner:** Platform eng.
- **Method:** NFR §5. **No test has been run.**

### 3.4 Usage and Cost Attribution

#### KPI-10: Request attribution coverage
- **Target:** 100% of production requests attributable to a tenant and project **[Target]**.
- **Numerator:** Production gateway requests with a usage record carrying a valid tenant and project.
- **Denominator:** Production gateway requests, from gateway request logs.
- **Unit:** Percentage.
- **Data source:** Usage records (FR-031) reconciled with gateway logs.
- **Frequency:** Daily.
- **Owner:** FinOps (A), Platform eng (R).
- **Method:** Reconciliation (NFR-046).

#### KPI-11: Compute cost attribution coverage
- **Target:** **[Open]** (NFR-047).
- **Numerator:** Platform-incurred cost allocated to tenants and projects.
- **Denominator:** Total platform-incurred cost.
- **Unit:** Percentage.
- **Data source:** Cloud billing, cluster usage, and FR-082.
- **Frequency:** Monthly.
- **Owner:** FinOps.
- **Method:** Allocation report. Shared-overhead treatment is **[Open]** (FR-Q11).

#### KPI-12: Platform cost per 1,000 requests
- **Target:** None until a baseline exists; this is a trend metric.
- **Numerator:** Platform infrastructure cost, excluding model tokens.
- **Denominator:** Gateway requests ÷ 1,000.
- **Unit:** Currency per 1,000 requests.
- **Data source:** Billing plus usage records.
- **Frequency:** Monthly.
- **Owner:** FinOps.
- **Method:** NFR-048.

#### KPI-13: Metering reconciliation variance
- **Target:** Tolerance **[Open]** (NFR-045).
- **Numerator:** |Platform-recorded tokens − provider-reported tokens|.
- **Denominator:** Provider-reported tokens.
- **Unit:** Percentage.
- **Data source:** Usage records and provider usage reports.
- **Frequency:** Per billing period.
- **Owner:** FinOps.
- **Method:** Reconciliation.

### 3.5 Security Coverage

#### KPI-14: Authenticated and authorized request coverage
- **Target:** 100% of production requests authenticated and authorized **[Target]**.
- **Numerator:** Production requests processed with a validated identity *and* a recorded allow decision.
- **Denominator:** Production requests processed (accepted by any platform API).
- **Unit:** Percentage.
- **Data source:** Gateway and API logs; authorization decision logs (SEC-024).
- **Frequency:** Daily.
- **Owner:** Security / IAM.
- **Method:** Reconcile processed requests with authentication and authorization records. Any processed request without both is a defect. Rejected requests are excluded from both numerator and denominator.

#### KPI-15: Cross-tenant unexpected allows
- **Target:** 0 **[Target]**.
- **Numerator:** Unexpected allows in the cross-tenant test suite.
- **Denominator:** Not applicable (count); suite size is reported alongside.
- **Unit:** Count.
- **Data source:** CI results (SEC-036, NFR-020).
- **Frequency:** Every release.
- **Owner:** Security / IAM.
- **Method:** Automated suite.

#### KPI-16: Sensitive actions without approval
- **Target:** 0 **[Target]**.
- **Numerator:** Sensitive operations executed without a permitting policy and a recorded business-owner authorization.
- **Denominator:** Not applicable (count); total sensitive operations are reported alongside.
- **Unit:** Count.
- **Data source:** Audit log (SEC-050, SEC-070).
- **Frequency:** Weekly review.
- **Owner:** Security / IAM.
- **Method:** Audit query joining executions to approvals.

#### KPI-17: Audit completeness
- **Target:** 100% **[Target]**.
- **Numerator:** Security-relevant events with a complete audit record.
- **Denominator:** Security-relevant events, from service logs.
- **Unit:** Percentage.
- **Data source:** Audit store versus service event logs.
- **Frequency:** Monthly sample.
- **Owner:** Security / IAM.
- **Method:** Sampled reconciliation.

#### KPI-18: Vulnerability remediation within window
- **Target:** **[Open]** (NFR-027).
- **Numerator:** Findings remediated within their severity window.
- **Denominator:** Findings due in the period.
- **Unit:** Percentage.
- **Data source:** Scanner and tracker.
- **Frequency:** Monthly.
- **Owner:** Security / IAM.
- **Method:** Tracker report.

### 3.6 Operational

| ID | KPI | Numerator / denominator | Unit | Data source | Freq. | Owner | Target |
|---|---|---|---|---|---|---|---|
| KPI-19 | Request error rate by class | Failed requests per class (platform / provider / tenant) ÷ valid requests | % | Gateway metrics (FR-038) | Continuous | SRE | Platform class covered by KPI-07; others **[Open]** |
| KPI-20 | End-to-end latency (including provider) | p50 / p95 total request duration | ms | Tracing | Continuous | SRE | Tracked; no target **[Open]** |
| KPI-21 | Saturation | Utilized ÷ available capacity, for gateway CPU and memory, concurrency, and provider quota | % | Metrics (NFR-032, NFR-070) | Continuous | SRE | Headroom factor **[Open]** (NFR-069) |
| KPI-22 | Tracing coverage | Requests with a trace ID ÷ requests | % | Gateway logs vs traces | Daily | SRE | 100% **[Target]** (NFR-030) |
| KPI-23 | Incident response | Mean time to acknowledge and to mitigate, per severity | Minutes | Incident tooling | Per incident; monthly | SRE | **[Open]** (NFR-075) |
| KPI-24 | Deployment reliability | Change failure rate = failed or rolled-back deployments ÷ deployments; also rollback time | %; minutes | CI/CD records | Monthly | Platform eng | **[Open]** |

### 3.7 AI-Specific

The measurement methods below need evaluation datasets and/or human review that do not yet exist **[Open]** (UC-KA-Q4). Workload-level quality is owned by application teams. The platform provides the tooling **[Decision]** (ownership boundary).

| ID | KPI | Numerator / denominator | Unit | Data source | Freq. | Owner | Target |
|---|---|---|---|---|---|---|---|
| KPI-25 | Answer quality (UC-KA) | Answers rated helpful ÷ rated answers; plus offline eval score | % | Feedback on traces; eval runs | Weekly | APP (KA team) | **[Open]** |
| KPI-26 | Groundedness / citation validity (UC-KA) | Answers whose claims are supported by cited retrieved chunks ÷ evaluated answers; and answers whose citations are all in the retrieved set ÷ answers | % | Eval runs (LLM-assisted plus human-sampled **[Assumption]**); trace data | Weekly | APP | Citation validity 100% **[Target]** (UC-KA-AC2); groundedness **[Open]** |
| KPI-27 | Unauthorized document exposure (UC-KA) | Answers citing documents the user cannot access (count) | Count | ACL test suite; audit sampling | Per release; monthly | Security / IAM | 0 **[Target]** |
| KPI-28 | Agent task success (UC-OA) | Runs reaching a correct outcome (diagnosis rated useful, or action succeeded) ÷ completed runs | % | Run records; operator ratings | Weekly | APP (OA team) | **[Open]** |
| KPI-29 | Tool authorization failures (UC-OA) | Denied tool calls ÷ tool calls, by agent and tool | % | MCP broker logs (FR-048) | Daily | Security / IAM | Monitored for anomalies. A denial is a working control, so there is no zero target **[Assumption]** |
| KPI-30 | Model drift (UC-PM) | Time from drift onset to alert; and deployed models with drift monitoring ÷ deployed models | Hours; % | Monitoring (FR-064) | Continuous | APP (PM team) / Platform eng | Coverage 100% **[Target]**; detection time **[Open]** |
| KPI-31 | Evaluation coverage | Production LLM apps, agents, and models with an eval suite run before each release ÷ total | % | Release records | Per release | Platform eng / APP | **[Open]** |
| KPI-32 | Approval turnaround (UC-OA) | Time from approval request to decision (p50/p95); also rejection and expiry rates | Minutes; % | Approval records (FR-071) | Weekly | Security / IAM | **[Open]**; also watched for rubber-stamping (SECR-7) |

---

## 4. KPI Summary

| KPI | Target | Status |
|---|---|---|
| KPI-01 Team adoption | 16 of 20 (80%) | **[Target]**; definition and horizon **[Open]** |
| KPI-04 Onboarding time | < 30 min | **[Target]**; statistic **[Open]** |
| KPI-07 Gateway availability | ≥ 99.9% / rolling 30 days | **[Target]**; error definitions and provider treatment **[Open]** |
| KPI-08 Gateway-added p95 latency | < 200 ms, excluding inference | **[Target]** |
| KPI-09 Capacity test | 100 concurrent requests, pass | **[Target]** |
| KPI-10 Request attribution | 100% | **[Target]** |
| KPI-14 Authenticated and authorized | 100% | **[Target]** |
| KPI-15 / 16 / 27 | 0 | **[Target]** |
| KPI-17, 22, 26 (citations), 30 (coverage) | 100% | **[Target]** |
| All others | n/a | **[Open]** |

**Measured values:** none. No KPI has a measured value.

---

## 5. Hypothetical Initial Load

**This is a hypothetical planning scenario [Assumption].** It is not a forecast and not observed demand.

| Parameter | Value | Label |
|---|---|---|
| Active teams | 5 | [Assumption] |
| Requests per team per day | 2,000 | [Assumption] |
| Requests per day | 5 × 2,000 = **10,000** | Derived |
| Input tokens per request | 2,000 | [Assumption] |
| Output tokens per request | 500 | [Assumption] |
| Input tokens per day | 10,000 × 2,000 = **20,000,000** | Derived |
| Output tokens per day | 10,000 × 500 = **5,000,000** | Derived |
| **Total tokens per day** | 20M + 5M = **25,000,000** | Derived |
| 30-day totals (derived) | 300,000 requests; 600M input; 150M output; 750M total tokens | Derived |

### 5.1 Capacity Sanity Check

This is a hypothetical calculation using Little's law: concurrency = arrival rate × time in system.

- Average arrival rate = 10,000 ÷ 86,400 s ≈ **0.116 requests/s**.
- With a peak-to-average factor of 10 **[Assumption]** and an end-to-end request duration of 10 s, including inference **[Assumption]**: peak concurrency ≈ 0.116 × 10 × 10 ≈ **12 concurrent requests**.
- Under these assumptions, the 100-concurrent-request test target (KPI-09) has roughly 8× headroom over this hypothetical peak.

**[Open]** The real peak factor, request duration, and growth (NFR-Q7). These assumptions must be replaced with observed data.

---

## 6. Illustrative Cost

### 6.1 Standalone Hypothetical Pricing Example

> **This is a standalone arithmetic example with hypothetical prices.**
>
> - It is **not** the cost of the §5 workload.
> - It is **not** a live provider quote.
> - It is **not** a budget.

| Item | Quantity | Hypothetical price | Cost |
|---|---|---|---|
| Input tokens | 50,000,000 | $2.00 per million | 50 × $2 = **$100** |
| Output tokens | 10,000,000 | $8.00 per million | 10 × $8 = **$80** |
| **Total (per month in this example)** | | | **$180 / month** |

### 6.2 Same Hypothetical Prices Applied to the §5 Workload

This is for scale only, and is **not a budget or estimate of actual spend**.

- Per day: 20M input × $2/M = $40, plus 5M output × $8/M = $40, giving **$80/day**.
- Per 30 days: 30 × $80 = **$2,400**.

This shows that the §6.1 example ($180/month) corresponds to a much smaller volume than the §5 scenario. Actual prices depend on the approved models and providers (vision Q5). They must come from provider agreements, not from this document.

### 6.3 Cost Components

| Component | Drivers | Attribution approach (proposed) | Label |
|---|---|---|---|
| Model tokens (external providers) | Requests × tokens × price per model | Per request, via usage records (FR-031, FR-081) | [Assumption] |
| GPU / compute (self-hosted models, training, serving) | GPU-hours, node-hours | Per tenant namespace and job (FR-082) | [Assumption] |
| Platform compute (gateway, control plane, brokers) | Node-hours | Shared overhead; allocation method **[Open]** (FR-Q11) | [Open] |
| Storage | GB-months: indexes, artifacts, audit, traces, backups | Per tenant where tenant-scoped; audit as shared overhead **[Assumption]** | [Assumption] |
| Network | Egress to providers; cross-zone traffic | Mostly shared; per-tenant where measurable | [Open] |
| Vector search | Index size, queries, embedding tokens | Per tenant index (FR-054) | [Assumption] |
| Observability | Trace, log, and metric volume and retention | Shared, with per-tenant volume reporting | [Open] |
| Platform operations | Platform team, on-call, tooling | Outside per-request attribution; funding model **[Open]** (vision Q4) | [Open] |

---

## 7. Assumptions, Validation Plan, and Open Questions

### 7.1 Assumptions

| ID | Assumption | Area | Validation |
|---|---|---|---|
| SM-A1 | Adoption can be measured as production traffic in a trailing 30 days | Adoption | Agree the definition with leadership (vision Q2) |
| SM-A2 | 5 active teams × 2,000 requests/day is a reasonable early load | Capacity | Early-adopter usage data after slice launch |
| SM-A3 | 2,000 input and 500 output tokens per request are representative | Capacity, cost | Trace token distributions from early adopters |
| SM-A4 | Peak factor 10 and request duration 10 s | Capacity | Observed traffic and latency |
| SM-A5 | Per-request token cost dominates early spend | Cost | First monthly FinOps report |
| SM-A6 | App teams will own and fund AI quality evaluation | AI metrics | Confirm ownership (stakeholders §3 grey areas) |
| SM-A7 | Provider usage reports are available for reconciliation | Cost | Provider review (D7) |

### 7.2 Validation Plan

| Step | Activity | KPIs validated | When |
|---|---|---|---|
| 1 | Agree KPI definitions, statistics, and horizons with owners | All | Before slice build completes |
| 2 | Instrument the slice: usage, trace, auth decision, and onboarding events | KPI-04, 07, 08, 10, 14, 22 | During slice build |
| 3 | Run load, noisy-neighbour, and usability tests | KPI-04, 08, 09 | Before slice launch |
| 4 | Baseline the first 30 days of early-adopter data | KPI-07, 08, 10, 12, 19–21 | After slice launch |
| 5 | Replace §5 assumptions with observed volumes; re-run the capacity model | KPI-09, 21 | After step 4 |
| 6 | First FinOps reconciliation and attribution report | KPI-10, 11, 13 | First billing period |
| 7 | Set targets currently marked **[Open]** from baselines | All **[Open]** | After step 4 |

**Status:** No step has been started.

### 7.3 Open Questions

| ID | Question | Related |
|---|---|---|
| SM-Q1 | Adoption definition and time horizon for 16 of 20 | vision Q2, KPI-01 |
| SM-Q2 | Do provider failures count against KPI-07? | vision Q3, NFR-Q1 |
| SM-Q3 | Onboarding statistic; are approval waits excluded? | NFR-Q5, KPI-04 |
| SM-Q4 | What are the approved models and their contracted prices? | vision Q5 |
| SM-Q5 | Funding model and overhead allocation | vision Q4, FR-Q11 |
| SM-Q6 | Who builds evaluation datasets, and how is groundedness judged? | UC-KA-Q4, KPI-25/26 |
| SM-Q7 | Real expected volumes and growth | NFR-Q7 |
| SM-Q8 | Who receives the KPI reports, and how often? | AC-14 |

---

## 8. Traceability

### 8.1 Metrics to Goals

| Goal | KPIs |
|---|---|
| G1 Reduce duplication | KPI-01, KPI-02, KPI-03 |
| G2 Accelerate delivery | KPI-04, KPI-05, KPI-06 |
| G3 Security and governance | KPI-14–KPI-18, KPI-27, KPI-29, KPI-32 |
| G4 Cost transparency | KPI-10–KPI-13 |
| G5 Unified observability | KPI-07, KPI-08, KPI-19–KPI-24 |
| G6 Diverse workloads | KPI-02, KPI-25–KPI-31 |

### 8.2 Metrics to Requirements

| KPI | FR | NFR | SEC | Stakeholder / use-case AC |
|---|---|---|---|---|
| KPI-01 | FR-001, FR-031 | n/a | n/a | AC-04 |
| KPI-02 | n/a | n/a | n/a | UC-KA/OA/PM ACs |
| KPI-04, 05 | FR-004, FR-079 | NFR-050 | n/a | AC-01, VS-AC2 |
| KPI-06 | n/a | NFR-054 | n/a | AC-14 |
| KPI-07 | FR-038 | NFR-001, NFR-002 | n/a | AC-05, VS-AC6 |
| KPI-08 | FR-022 | NFR-007 | n/a | S01 |
| KPI-09 | FR-017 | NFR-013, NFR-017 | SEC-037 | VS |
| KPI-10 | FR-031 | NFR-046 | SEC-034 | AC-12, VS-AC5 |
| KPI-11, 12 | FR-082 | NFR-047, NFR-048 | n/a | AC-12 |
| KPI-13 | FR-031 | NFR-045 | n/a | AC-12 |
| KPI-14 | FR-006, FR-007, FR-010 | NFR-026 | SEC-010–SEC-024 | AC-07, VS-AC3 |
| KPI-15 | FR-013 | NFR-020 | SEC-036 | AC-08, VS-AC4 |
| KPI-16, 32 | FR-071, FR-072 | n/a | SEC-050, SEC-054 | AC-10, UC-OA-AC1 |
| KPI-17 | FR-068 | NFR-037 | SEC-070, SEC-071 | AC-09 |
| KPI-18 | n/a | NFR-027 | SEC-080 | S05 |
| KPI-19–21 | FR-038 | NFR-032, NFR-069, NFR-070 | n/a | AC-06 |
| KPI-22 | FR-034 | NFR-030 | n/a | AC-06 |
| KPI-23 | n/a | NFR-075 | SEC-073 | S04 |
| KPI-24 | n/a | NFR-055–NFR-057 | n/a | S04 |
| KPI-25, 26 | FR-057 | n/a | SEC-045 | UC-KA-AC2 |
| KPI-27 | FR-055 | n/a | SEC-046 | AC-11, UC-KA-AC1 |
| KPI-28, 29 | FR-041, FR-048 | n/a | SEC-051 | UC-OA-AC2 |
| KPI-30 | FR-064 | n/a | n/a | UC-PM-AC2 |
| KPI-31 | FR-062 | n/a | n/a | AC-03 |
