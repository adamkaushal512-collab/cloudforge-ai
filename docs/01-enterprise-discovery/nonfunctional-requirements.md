# CloudForge AI: Nonfunctional Requirements

| Field | Value |
|---|---|
| Document | Nonfunctional Requirements |
| Phase | 01: Enterprise Discovery |
| Status | Draft (not baselined, not approved) |
| Related | `platform-vision.md`, `stakeholders.md`, `use-cases.md`, `functional-requirements.md`, `security-governance.md`, `success-metrics.md`, `coverage-audit.md` |

---

## 1. Purpose and Disclaimer

This document specifies the quality attributes CloudForge AI must meet, such as availability, performance, scalability, isolation, security, and operability. It complements the functional requirements in `functional-requirements.md`.

> **Disclaimer:** CloudForge is a fictional enterprise. This document is a planning artifact.
>
> - **Every numeric value here is a proposed target, not a measured result.**
> - **No production metrics exist.**
> - **No load, chaos, DR, or security test has been run.**
> - **No SLA has been approved.**
>
> Where a value is not yet set, it is marked **[Open]** rather than invented.

### 1.1 Labels

The labels are the same as in all earlier discovery documents:

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input, not as a measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal. It is not measured or committed. |
| **[Open]** | An unresolved question or value that needs an owner and a decision. |

### 1.2 Status of the Numeric Values in This Document

| Value | Source | Status |
|---|---|---|
| 99.9% LLM gateway availability over a 30-day window | Requirements brief; `platform-vision.md` §8 | **[Target]**: proposed, not measured, not committed |
| p95 gateway-added latency < 200 ms, excluding model inference | Requirements brief | **[Target]** |
| 100 concurrent requests (initial test target) | Requirements brief | **[Target]** |
| Onboarding < 30 minutes | `platform-vision.md` §8 | **[Target]** |
| RTO / RPO | Requirements brief | **[Open]**: values TBD |
| All other numeric values | This document | **[Target]** if proposed here; **[Open]** if not yet set |

### 1.3 Conventions

- **Priority:**
  - **Must:** Required for the platform to be viable or safe.
  - **Should:** Important; a short-term workaround exists.
  - **Could:** Desirable.
  - Priorities are **[Assumption]**: they are proposed, not agreed.
- **Owner:** The stakeholder role proposed as accountable, consistent with the RACI in `stakeholders.md` §4. Owners are **[Assumption]**: no owner has accepted.
- **Phase:** Same meaning as in `functional-requirements.md`:
  - **VS:** first vertical slice
  - **KA:** knowledge assistant
  - **OA:** operations agent
  - **PM:** predictive maintenance
  - **Later:** after the initial workloads
- **References:** FR-xxx refers to `functional-requirements.md`. VS-ACn and UC-xx-ACn refer to `use-cases.md`. AC-nn, Cn, Dn, and SQn refer to `stakeholders.md`. Gn, An, Rn, and Qn refer to `platform-vision.md`.

### 1.4 Key Definitions

| Term | Definition (proposed) |
|---|---|
| **Gateway-added latency** | Time spent inside the gateway for a request: total server-side request duration minus time spent waiting on the upstream model deployment. For streaming requests, gateway-added time to first byte is measured instead (NFR-009). |
| **Valid request** | A well-formed, authenticated request that the gateway accepts for processing. Requests rejected for authentication, authorization, quota, or validation reasons are correct behavior, not failures. |
| **Platform-attributable failure** | A failure classified as a *platform* error by FR-038, such as a gateway crash, internal timeout, or misrouting. Provider-attributable and tenant-attributable errors are classified separately. |
| **30-day window** | A rolling 30-day period evaluated continuously **[Target]**. |

---

## 2. Nonfunctional Requirements

### 2.1 Availability and Reliability

#### NFR-001: LLM gateway availability
- **Requirement:** The LLM gateway inference and embeddings APIs shall achieve at least 99.9% availability, measured over a rolling 30-day window.
- **Category:** Availability · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:**
  - *SLI:* the proportion of valid requests not ending in a platform-attributable failure.
  - *SLO:* ≥ 99.9% over a rolling 30 days **[Target]**.
- **Measurement:**
  - Server-side request counters at the gateway edge, by error class (FR-038).
  - Synthetic probes every 60 seconds **[Target]** from at least two locations, as a cross-check for total outages that server-side metrics might miss.
- **Acceptance criteria:**
  1. The SLI is computed automatically and displayed on an SLO dashboard.
  2. Before production, a pre-production soak test (§5) shows the SLO is achievable under the NFR-013 load profile.
  3. No production result exists yet.
- **Dependencies / assumptions:**
  - Depends on FR-038 and NFR-002.
  - Whether provider outages count against this SLO is **[Open]** (vision Q3). This draft excludes provider-attributable failures from the SLO but tracks them in a separate SLI (NFR-002) **[Assumption]**.

#### NFR-002: Availability SLI definition and exclusions
- **Requirement:** The platform shall publish a written SLI specification for gateway availability. The specification shall define:
  - valid requests;
  - each error class;
  - exclusions;
  - the treatment of partial streams and of requests served by failover.
- **Category:** Availability · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** This requirement defines the SLI rather than having one. It defines three SLIs:
  1. *platform availability*: drives the SLO;
  2. *end-to-end availability*: includes provider failures; tracked, no SLO yet;
  3. *provider availability per deployment*: tracked.
- **Measurement:** Document review, plus sample reconciliation of request logs against the classifications.
- **Acceptance criteria:**
  1. The specification is reviewed by SRE, Platform eng, and app-team representatives.
  2. A test set of failure scenarios is classified as the specification says.
- **Dependencies / assumptions:** Resolves vision Q3 once approved **[Open]**. A request served successfully via failover (FR-021) counts as good **[Assumption]**.

#### NFR-003: Control-plane availability
- **Requirement:** The control-plane APIs (onboarding, project, credential, catalog, and reporting) shall meet a defined availability SLO.
- **Category:** Availability · **Priority:** Should · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:**
  - *SLI:* successful control-plane requests divided by valid requests.
  - *SLO:* **[Open]**. Expected to be lower than NFR-001, because control-plane outages do not stop inference traffic **[Assumption]**.
- **Measurement:** Server-side counters; synthetic onboarding probe.
- **Acceptance criteria:**
  1. An SLO value is agreed and measured.
  2. A control-plane outage does not affect the data plane: in fault-injection testing, gateway requests with already-issued credentials keep succeeding.
- **Dependencies / assumptions:** Data-plane and control-plane separation **[Assumption]**.

#### NFR-004: No single point of failure in the gateway path
- **Requirement:** Every component in the synchronous gateway request path shall run with at least two instances across at least two failure domains, such as availability zones. The components are ingress, gateway, authorization, and rate limiting.
- **Category:** Reliability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None. This is a structural requirement.
- **Measurement:** Architecture review; deployment manifest inspection; zone-failure fault injection.
- **Acceptance criteria:**
  1. With a single instance, or a single zone, removed in test, gateway requests keep succeeding.
  2. The error rate during the transition stays within the error budget.
- **Dependencies / assumptions:** At least two failure domains are available in the hosting environment **[Assumption]**. Mitigates vision R2.

#### NFR-005: Non-blocking dependencies in the request path
- **Requirement:** Failure of the usage metering, trace export, or reporting subsystems shall not cause gateway inference requests to fail.
- **Category:** Reliability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** Covered by NFR-001.
- **Measurement:** Fault injection that disables each subsystem in turn.
- **Acceptance criteria:**
  1. With metering storage unavailable, inference succeeds and usage records are buffered and later delivered, with no loss beyond the NFR-046 tolerance.
  2. With the trace backend unavailable, inference succeeds.
- **Dependencies / assumptions:** Audit is deliberately excluded. Audit failure must block *sensitive* operations (FR-073, NFR-044), but not ordinary inference **[Assumption]**. **[Open]** Whether an audit outage should block ordinary inference.

#### NFR-006: Workload-service availability SLOs
- **Requirement:** The RAG retrieval, agent runtime, MCP broker, and model-serving services shall each have a defined availability SLO before their workload goes to production.
- **Category:** Availability · **Priority:** Should · **Owner:** SRE · **Phase:** KA / OA / PM
- **SLI / SLO:** Same SLI pattern as NFR-001; SLO values **[Open]**.
- **Measurement:** As NFR-001.
- **Acceptance criteria:**
  1. An SLO is agreed and measured for each service before its workload's production launch.
- **Dependencies / assumptions:** These services are not part of the first slice (vision §7.3).

### 2.2 Performance

#### NFR-007: Gateway-added latency (p95)
- **Requirement:** At the 95th percentile, the gateway shall add less than 200 ms of latency to non-streaming requests, excluding model inference time.
- **Category:** Performance · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:**
  - *SLI:* gateway-added latency per request (§1.4).
  - *SLO:* p95 < 200 ms over a rolling 30 days **[Target]**, at loads up to the NFR-013 profile.
- **Measurement:**
  - Server-side tracing spans: the total gateway span minus the upstream-call span.
  - In load tests, a mock provider with fixed latency isolates gateway overhead.
  - Percentiles are computed from histograms, not averages.
- **Acceptance criteria:**
  1. A load test at NFR-013 load with a mock provider shows p95 gateway-added latency < 200 ms.
  2. The same metric is exported in production.
  3. No test has been run yet.
- **Dependencies / assumptions:** Includes authentication, authorization, policy, rate limiting, and routing (FR-022). Excludes client network time.

#### NFR-008: Gateway-added latency (p99)
- **Requirement:** The platform shall measure and report p99 gateway-added latency, and shall meet a p99 SLO once one is defined.
- **Category:** Performance · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *SLI* as NFR-007 at p99; *SLO* **[Open]**.
- **Measurement:** As NFR-007.
- **Acceptance criteria:**
  1. p99 is reported in load-test results and dashboards.
  2. An SLO value is agreed after baseline data exists.
- **Dependencies / assumptions:** A baseline is needed first (vision Q1).

#### NFR-009: Streaming time-to-first-byte overhead
- **Requirement:** For streaming requests, gateway-added time to first byte shall meet a defined p95 target.
- **Category:** Performance · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:**
  - *SLI:* time from request receipt to the first byte sent to the client, minus time from the upstream call to the first upstream byte.
  - *SLO:* **[Open]**. Proposed to align with NFR-007 **[Assumption]**.
- **Measurement:** Tracing spans; streaming load test with a mock provider.
- **Acceptance criteria:**
  1. The metric is reported.
  2. Once agreed, the target is met in load testing.
- **Dependencies / assumptions:** FR-019.

#### NFR-010: Authorization decision latency
- **Requirement:** The authentication and authorization checks in the gateway path shall complete within a defined share of the NFR-007 latency budget.
- **Category:** Performance · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *SLI:* p95 duration of the auth span. *SLO:* **[Open]**.
- **Measurement:** Tracing spans under load.
- **Acceptance criteria:**
  1. The auth span is instrumented separately.
  2. Its p95 is reported in load tests.
- **Dependencies / assumptions:** Token validation without a synchronous identity-provider call per request, for example cached signing keys **[Assumption]**.

#### NFR-011: Retrieval latency
- **Requirement:** The RAG retrieval API, including permission filtering, shall meet a defined p95 latency target.
- **Category:** Performance · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *SLI:* server-side retrieval duration. *SLO:* **[Open]**.
- **Measurement:** Tracing spans; a load test against a representative test corpus with ACLs.
- **Acceptance criteria:**
  1. A target is agreed.
  2. The target is met with ACL filtering enabled.
- **Dependencies / assumptions:** UC-KA-A2 (ACL filtering is feasible within acceptable latency).

#### NFR-012: Usage and trace data freshness
- **Requirement:** Usage records and traces shall be queryable by the tenant within a defined delay after the request completes.
- **Category:** Performance · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *SLI:* the delay from request completion to the record being queryable. *SLO:* **[Open]** (FR-037 report latency).
- **Measurement:** Synthetic requests, timed until they appear in the reporting API.
- **Acceptance criteria:**
  1. The freshness delay is measured and reported.
  2. The agreed target is met in pre-production testing.
- **Dependencies / assumptions:** FR-031, FR-035, FR-037.

### 2.3 Scalability

#### NFR-013: Initial concurrency target
- **Requirement:** The gateway shall sustain 100 concurrent in-flight requests for at least 30 minutes **[Target]**, while meeting NFR-007 and keeping the platform-attributable error rate below 0.1%.
- **Category:** Scalability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** Not an SLO. This is a load-test acceptance target: concurrency 100 **[Target]**; error rate < 0.1% **[Target]**, consistent with the NFR-001 budget.
- **Measurement:**
  - Load-test tool driving a closed-loop workload with 100 concurrent clients.
  - Mock provider with configurable latency, to avoid provider limits and cost.
  - A separate, smaller test against a real provider.
- **Acceptance criteria:**
  1. A test report records concurrency, duration, latency percentiles, and error rate.
  2. All targets are met.
  3. No test has been run yet.
- **Dependencies / assumptions:**
  - 100 concurrent requests is an initial test target, not a forecast of production demand **[Assumption]**.
  - The 30-minute duration is proposed **[Target]**.

#### NFR-014: Horizontal scalability
- **Requirement:** The gateway data plane shall scale horizontally, adding or removing instances without downtime or configuration changes by tenants.
- **Category:** Scalability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** Load test that scales instances up and down mid-test.
- **Acceptance criteria:**
  1. Throughput increases as instances are added.
  2. No requests fail beyond the error budget during scaling events.
- **Dependencies / assumptions:** A stateless gateway, with rate-limit state held in a shared store **[Assumption]**.

#### NFR-015: Tenant-count scalability
- **Requirement:** The platform shall support at least 20 tenants with multiple projects each, with headroom for growth, without architectural change.
- **Category:** Scalability · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None. The headroom factor is **[Open]**.
- **Measurement:** A synthetic test that creates tenants and projects at the target scale and runs isolation and performance tests.
- **Acceptance criteria:**
  1. Onboarding, isolation (NFR-020), and latency (NFR-007) targets hold with synthetic tenants at the agreed scale.
- **Dependencies / assumptions:** About 20 teams **[Decision]**.

#### NFR-016: Autoscaling
- **Requirement:** Gateway and workload services shall autoscale on load signals within defined bounds.
- **Category:** Scalability · **Priority:** Should · **Owner:** SRE · **Phase:** KA
- **SLI / SLO:** *SLI:* time from load increase to added capacity. *Target:* **[Open]**.
- **Measurement:** Step-load test.
- **Acceptance criteria:**
  1. Under a step increase in load, capacity is added and latency returns within the NFR-007 target within the agreed time.
- **Dependencies / assumptions:** Kubernetes autoscaling (vision A5).

### 2.4 Multi-Tenant Isolation and Noisy-Neighbour Protection

#### NFR-017: Noisy-neighbour latency and error protection
- **Requirement:** When one tenant drives load above its rate limit, the other tenants' p95 gateway-added latency and platform-attributable error rate shall remain within their SLOs (NFR-001, NFR-007).
- **Category:** Isolation · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** The SLIs of NFR-001 and NFR-007, sliced per tenant.
- **Measurement:** A multi-tenant load test with one "aggressor" tenant at several times its limit and other tenants at normal load.
- **Acceptance criteria:**
  1. The aggressor's excess requests are rate-limited (FR-029).
  2. The other tenants' p95 and error rate meet their targets.
- **Dependencies / assumptions:** FR-029, FR-030.

#### NFR-018: Per-tenant concurrency limits
- **Requirement:** The gateway shall enforce per-tenant concurrent-request caps, so that one tenant cannot take all gateway or provider capacity.
- **Category:** Isolation · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None. Cap values **[Open]**.
- **Measurement:** Load test exceeding the cap.
- **Acceptance criteria:**
  1. Requests beyond the cap are rejected or queued as configured.
  2. Other tenants are unaffected, as in NFR-017.
- **Dependencies / assumptions:** FR-029.

#### NFR-019: Compute isolation and quotas
- **Requirement:** Tenant workloads shall run with enforced CPU, memory, and (where applicable) GPU limits and quotas. Network policies shall deny cross-tenant traffic by default.
- **Category:** Isolation · **Priority:** Must · **Owner:** Platform eng · **Phase:** OA / PM
- **SLI / SLO:** None.
- **Measurement:** Configuration audit; a test pod attempting to reach another tenant's services; resource-exhaustion test.
- **Acceptance criteria:**
  1. Cross-tenant network attempts fail.
  2. A tenant exceeding its quota cannot schedule more workloads.
  3. Other tenants' workloads are unaffected.
- **Dependencies / assumptions:** FR-016. Namespace isolation is adequate for the initial data classifications (C3) **[Assumption]**.

#### NFR-020: Continuous cross-tenant isolation verification
- **Requirement:** An automated cross-tenant access test suite (FR-013) shall run in CI for every release and on a schedule in each environment. Any unexpected allow shall block the release.
- **Category:** Isolation / Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Target:* 0 unexpected cross-tenant allows **[Target]**.
- **Measurement:** Test suite results.
- **Acceptance criteria:**
  1. The suite covers every resource type in the release.
  2. The release pipeline fails on any unexpected allow.
- **Dependencies / assumptions:** FR-012, FR-013.

#### NFR-021: Provider capacity partitioning
- **Requirement:** The platform shall allocate shared provider rate limits and quotas across tenants, so that one tenant cannot exhaust a provider limit for all tenants.
- **Category:** Isolation · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** None.
- **Measurement:** A test with simulated provider limits.
- **Acceptance criteria:**
  1. When one tenant consumes its allocation, other tenants can still use theirs.
- **Dependencies / assumptions:** Provider limit information is available **[Assumption]**.

### 2.5 Security, Authentication, Authorization, and Encryption

The detailed security controls will be specified in `security-governance.md`. The requirements below set the measurable baseline.

#### NFR-022: Encryption in transit
- **Requirement:** All network traffic shall be encrypted with TLS 1.2 or higher, with TLS 1.3 preferred. This covers client-to-platform, service-to-service, and platform-to-provider traffic.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Target:* 0 plaintext endpoints **[Target]**.
- **Measurement:** TLS scanning of endpoints; service-mesh or configuration audit.
- **Acceptance criteria:**
  1. A scan finds no endpoints accepting plaintext or TLS below 1.2.
- **Dependencies / assumptions:** **[Open]** Whether mutual TLS is required between internal services.

#### NFR-023: Encryption at rest
- **Requirement:** All persisted tenant data, credentials, usage records, traces, audit records, indexes, and model artifacts shall be encrypted at rest, with keys held in a managed key service.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Target:* 100% of data stores encrypted **[Target]**.
- **Measurement:** Configuration audit of all data stores.
- **Acceptance criteria:**
  1. Every data store in the inventory has encryption at rest enabled with managed keys.
- **Dependencies / assumptions:** **[Open]** Whether per-tenant keys are needed for higher data classifications.

#### NFR-024: Secrets management and rotation
- **Requirement:** All secrets, including provider credentials and signing keys, shall be stored in a secrets manager and rotated on a defined schedule without service interruption.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Rotation interval:* **[Open]**.
- **Measurement:** Secret-scanning of repositories and images; a rotation exercise.
- **Acceptance criteria:**
  1. No secrets are found in code, images, or logs.
  2. A rotation exercise completes with no failed requests beyond the error budget.
- **Dependencies / assumptions:** FR-023.

#### NFR-025: Token and credential lifetime
- **Requirement:** Access tokens and project credentials shall have bounded lifetimes, and revocation shall take effect within a defined maximum delay.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Maximum token lifetime and revocation delay:* **[Open]**.
- **Measurement:** A test that revokes a credential and measures the time until the first rejection.
- **Acceptance criteria:**
  1. A revoked credential is rejected within the agreed delay.
- **Dependencies / assumptions:** FR-003, FR-006.

#### NFR-026: Authorization coverage
- **Requirement:** All public and internal API endpoints shall be covered by automated authorization tests: positive tests, and negative tests for deny-by-default.
- **Category:** Security · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Target:* 100% endpoint coverage **[Target]**.
- **Measurement:** Endpoint inventory compared with the test inventory in CI.
- **Acceptance criteria:**
  1. CI fails when an endpoint has no authorization test.
- **Dependencies / assumptions:** FR-010.

#### NFR-027: Vulnerability remediation
- **Requirement:** Platform images and dependencies shall be scanned continuously. Vulnerabilities shall be remediated within time limits defined per severity.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Remediation windows:* **[Open]**.
- **Measurement:** Scanner reports; tracking of the age of open findings.
- **Acceptance criteria:**
  1. Scanning runs in CI and on deployed images.
  2. A release with known critical vulnerabilities is blocked unless an exception is approved.
- **Dependencies / assumptions:** An enterprise vulnerability policy exists **[Assumption]**.

#### NFR-028: Security testing before production
- **Requirement:** Each workload phase shall complete a security assessment, including penetration testing of tenant isolation and authorization, before production launch.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** An assessment report.
- **Acceptance criteria:**
  1. No unresolved critical or high findings exist at launch, unless an exception is approved.
  2. No assessment has been performed yet.
- **Dependencies / assumptions:** Who performs the assessment (internal or external) is **[Open]**.

#### NFR-029: Least privilege for platform components
- **Requirement:** Each platform service shall run under its own identity, with only the permissions it needs. Platform-admin access to tenant data shall be audit logged.
- **Category:** Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** A permissions review of service identities.
- **Acceptance criteria:**
  1. No service identity has wildcard or cluster-admin permissions without a documented exception.
- **Dependencies / assumptions:** FR-068.

### 2.6 Observability

#### NFR-030: Trace coverage
- **Requirement:** Every request entering a platform service shall carry a trace ID (FR-034). Spans shall be recorded for the gateway, authorization, upstream calls, retrieval, and agent and tool steps.
- **Category:** Observability · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:**
  - *Target:* 100% of requests have a trace ID **[Target]**.
  - Span sampling rate for storage: **[Open]**.
  - Error and slow requests are always retained **[Assumption]**.
- **Measurement:** Comparison of request counts with trace counts; sampling configuration review.
- **Acceptance criteria:**
  1. Every sampled request shows a complete span tree.
  2. Every response includes a trace ID.
- **Dependencies / assumptions:** An open tracing standard **[Assumption]**.

#### NFR-031: Correlation across signals
- **Requirement:** The trace ID shall act as a correlation ID that appears in logs, usage records, audit events, and approval records for the same request or run.
- **Category:** Observability · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** For sample requests, search each signal store by trace ID.
- **Acceptance criteria:**
  1. Searching by a single trace ID returns the matching logs, usage record, and audit events.
- **Dependencies / assumptions:** FR-031, FR-068.

#### NFR-032: Service and tenant metrics
- **Requirement:** Each platform service shall emit request rate, error rate (by error class), latency histograms, and saturation metrics. Gateway metrics shall be broken down by tenant, project, and model.
- **Category:** Observability · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** Feeds the SLIs for NFR-001 and NFR-007.
- **Measurement:** Metric inventory review.
- **Acceptance criteria:**
  1. Dashboards show the four metric types per service.
  2. The tenant breakdown is visible only to authorized roles.
- **Dependencies / assumptions:** **[Assumption]** Per-tenant metric cardinality stays manageable at about 20 tenants.

#### NFR-033: Structured, safe logging
- **Requirement:** Platform logs shall be structured and shall include the trace ID. They shall never contain secrets, credentials, or prompt or response content, unless content capture is enabled under FR-036.
- **Category:** Observability / Privacy · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Target:* 0 secret or content leaks in logs **[Target]**.
- **Measurement:** Automated log scanning with secret and PII detectors in pre-production and production.
- **Acceptance criteria:**
  1. Scanning of test-run logs finds no secrets or content.
- **Dependencies / assumptions:** FR-036; C6.

#### NFR-034: SLO dashboards and burn-rate visibility
- **Requirement:** The platform shall provide SLO dashboards showing the current SLI, the error budget remaining, and the burn rate for each defined SLO.
- **Category:** Observability · **Priority:** Should · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** As in §3.
- **Measurement:** Dashboard review.
- **Acceptance criteria:**
  1. The dashboard for NFR-001 shows the remaining budget computed as in §3.2.
- **Dependencies / assumptions:** NFR-001, NFR-002.

### 2.7 Disaster Recovery, Backups, RTO, and RPO

#### NFR-035: Defined RTO and RPO per data and service class
- **Requirement:** The platform shall define a recovery time objective (RTO) and a recovery point objective (RPO) for each service and data class, and shall meet them in DR tests.
- **Category:** DR · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** **All values are [Open] (TBD).** Classes to define:

  | Class | RTO | RPO |
  |---|---|---|
  | Gateway data plane (stateless) | TBD | N/A (stateless) **[Assumption]** |
  | Control-plane state (tenants, projects, credentials, catalog, policies) | TBD | TBD |
  | Usage records | TBD | TBD |
  | Audit records | TBD | TBD (expected to be the strictest **[Assumption]**) |
  | Traces | TBD | TBD (may tolerate loss **[Assumption]**) |
  | RAG indexes | TBD | TBD (rebuildable from sources **[Assumption]**) |
  | Agent run state | TBD | TBD |
  | Model registry and artifacts | TBD | TBD |

- **Measurement:** DR drills that measure the actual restore time and the data-loss window.
- **Acceptance criteria:**
  1. Values are agreed by SRE, Security, and Engineering leadership.
  2. A drill demonstrates them for each class.
- **Dependencies / assumptions:** The DR topology (single or multi-region) is **[Open]**.

#### NFR-036: Backups and restore verification
- **Requirement:** All stateful stores that cannot be rebuilt shall be backed up on a schedule consistent with their RPO. Restores shall be tested on a defined schedule.
- **Category:** DR · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Restore test frequency:* **[Open]**.
- **Measurement:** Backup job monitoring; restore test reports.
- **Acceptance criteria:**
  1. Backup jobs alert on failure.
  2. A restore test recovers data to within the RPO.
- **Dependencies / assumptions:** NFR-035. Backups are encrypted (NFR-023).

#### NFR-037: Audit record durability
- **Requirement:** Audit records whose write has been acknowledged shall not be lost.
- **Category:** DR / Security · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Target:* 0 acknowledged audit records lost **[Target]**.
- **Measurement:** Fault injection during audit writes, followed by reconciliation.
- **Acceptance criteria:**
  1. After a simulated node or zone failure, every acknowledged audit record is present.
- **Dependencies / assumptions:** FR-069, FR-073.

#### NFR-038: Environment rebuild from code
- **Requirement:** Each platform environment shall be reproducible from version-controlled infrastructure and configuration code.
- **Category:** DR / Maintainability · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Rebuild time:* **[Open]**, contributing to the RTO.
- **Measurement:** A periodic rebuild of a non-production environment from code.
- **Acceptance criteria:**
  1. An environment rebuilt from code passes the smoke and isolation test suites.
- **Dependencies / assumptions:** NFR-058.

#### NFR-039: DR drills
- **Requirement:** The platform shall run DR drills that exercise the loss of a failure domain and data restoration, at a defined frequency.
- **Category:** DR · **Priority:** Should · **Owner:** SRE · **Phase:** KA
- **SLI / SLO:** *Frequency:* **[Open]**.
- **Measurement:** Drill reports recording the RTO and RPO achieved.
- **Acceptance criteria:**
  1. Each drill produces a report and follow-up actions.
- **Dependencies / assumptions:** NFR-035.

### 2.8 Fault Tolerance, Retries, Timeouts, Circuit Breakers, and Graceful Degradation

#### NFR-040: Timeouts on all outbound calls
- **Requirement:** Every outbound call from a platform service shall have an explicit, configurable timeout. Outbound calls go to providers, identity, stores, MCP servers, and similar dependencies.
- **Category:** Fault tolerance · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Default values:* **[Open]**.
- **Measurement:** Code and config review; fault injection with hanging dependencies.
- **Acceptance criteria:**
  1. Against a dependency that never responds, the calling request fails with a timeout error within the configured time plus a small margin, and resources are released.
- **Dependencies / assumptions:** Model inference timeouts must allow for long generations **[Assumption]**.

#### NFR-041: Bounded retries with backoff
- **Requirement:** Retries shall occur only for errors classified as retryable. They shall use exponential backoff with jitter, a maximum attempt count, and an overall retry budget. Non-idempotent tool actions shall never be retried automatically.
- **Category:** Fault tolerance · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Maximum attempts and retry budget:* **[Open]**.
- **Measurement:** Fault-injection tests counting attempts.
- **Acceptance criteria:**
  1. Retry counts never exceed the configured maximum.
  2. A sensitive or write tool call (UC-OA) is executed at most once per approval.
- **Dependencies / assumptions:** FR-041, FR-048, FR-071.

#### NFR-042: Circuit breakers per upstream deployment
- **Requirement:** The gateway shall apply circuit breakers per provider deployment. A breaker opens on a sustained error or timeout rate, sheds load to failover targets or fails fast, and probes for recovery.
- **Category:** Fault tolerance · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *Breaker thresholds and failover completion time:* **[Open]**.
- **Measurement:** Fault injection that degrades a mock provider.
- **Acceptance criteria:**
  1. Under injected failure, the breaker opens and traffic shifts to the alternate (FR-021) or fails fast.
  2. After recovery, the breaker closes.
- **Dependencies / assumptions:** FR-021.

#### NFR-043: Graceful degradation matrix
- **Requirement:** Each platform service shall behave as follows when a dependency fails.

  | Failed dependency | Required behavior | Rationale |
  |---|---|---|
  | Usage metering store | Continue serving; buffer records durably; backfill | NFR-005 |
  | Trace backend | Continue serving; drop or buffer spans | NFR-005 |
  | Identity / authorization decision | **Fail closed**: reject requests | Least privilege **[Decision]** |
  | Policy store | Use the last known-good policy for a bounded period, then fail closed **[Assumption]** | Availability vs safety |
  | Audit sink | Block sensitive operations (FR-073); ordinary inference **[Open]** (NFR-005) | No unaudited sensitive actions |
  | RAG ACL data missing or stale | **Fail closed**: exclude documents | UC-KA §4.6 |
  | Primary model deployment | Fail over (FR-021) or return an explicit error | UC-KA §4.6 |
  | Approval service | Sensitive actions remain pending or expire; never auto-approve | UC-OA §5.6 |

- **Category:** Fault tolerance · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS (gateway rows); KA / OA (others)
- **SLI / SLO:** None.
- **Measurement:** Fault-injection test per row.
- **Acceptance criteria:**
  1. Each row has a passing fault-injection test before the relevant phase launches.
- **Dependencies / assumptions:** The policy-store grace period is **[Open]**.

#### NFR-044: Load shedding
- **Requirement:** Under overload, the gateway shall shed excess load with explicit "retry later" responses rather than degrading latency for all requests or failing unpredictably.
- **Category:** Fault tolerance · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** A load test beyond capacity.
- **Acceptance criteria:**
  1. Beyond capacity, rejected requests receive a retry-later response.
  2. Accepted requests still meet NFR-007.
- **Dependencies / assumptions:** NFR-018.

### 2.9 Cost Efficiency and Resource Utilization

#### NFR-045: Metering accuracy
- **Requirement:** Token usage recorded by the platform shall reconcile with provider-reported usage within a defined tolerance per billing period.
- **Category:** Cost · **Priority:** Must · **Owner:** FinOps · **Phase:** VS
- **SLI / SLO:** *Reconciliation tolerance:* **[Open]**.
- **Measurement:** Periodic reconciliation of platform usage records against provider usage reports.
- **Acceptance criteria:**
  1. A reconciliation report is produced.
  2. The variance is within the agreed tolerance.
- **Dependencies / assumptions:** Providers expose usage data (D7) **[Assumption]**.

#### NFR-046: Usage record completeness
- **Requirement:** The platform shall lose no more than a defined fraction of usage records, including during the NFR-005 degradation scenarios.
- **Category:** Cost · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *SLI:* usage records divided by gateway requests. *Target:* **[Open]**, with 100% as the design goal **[Assumption]**.
- **Measurement:** Reconciliation of request logs against usage records (FR-031).
- **Acceptance criteria:**
  1. Reconciliation of test runs, including fault-injected runs, meets the target.
- **Dependencies / assumptions:** FR-031.

#### NFR-047: Cost attribution coverage
- **Requirement:** At least a defined percentage of platform-incurred cost shall be attributed to tenants and projects. The remainder shall be reported as shared overhead.
- **Category:** Cost · **Priority:** Should · **Owner:** FinOps · **Phase:** KA
- **SLI / SLO:** *Target percentage:* **[Open]**.
- **Measurement:** A monthly attribution report.
- **Acceptance criteria:**
  1. The report shows attributed versus unattributed cost.
  2. The target is met.
- **Dependencies / assumptions:** FR-081, FR-082; overhead allocation is **[Open]** (FR-Q11).

#### NFR-048: Platform overhead cost visibility
- **Requirement:** The platform shall report its own infrastructure cost per unit of work, such as per 1,000 gateway requests, so that its efficiency can be tracked over time.
- **Category:** Cost · **Priority:** Should · **Owner:** FinOps · **Phase:** KA
- **SLI / SLO:** None. This is a trend metric with no target until a baseline exists.
- **Measurement:** Platform infrastructure cost divided by request volume.
- **Acceptance criteria:**
  1. The metric is reported monthly.
- **Dependencies / assumptions:** Needed to evaluate G1 claims (vision Q1).

#### NFR-049: Resource utilization and idle scale-down
- **Requirement:** Platform and tenant workloads shall declare resource requests and limits. Non-production and idle workloads shall scale down when unused.
- **Category:** Cost · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *Utilization targets:* **[Open]**.
- **Measurement:** Cluster utilization reports; policy checks for missing resource requests.
- **Acceptance criteria:**
  1. Admission policy rejects workloads without resource requests.
  2. Idle non-production workloads scale down.
- **Dependencies / assumptions:** NFR-019.

### 2.10 Developer Experience

#### NFR-050: Onboarding time
- **Requirement:** A new team shall be able to go from starting self-service onboarding to a first successful authenticated gateway request in under 30 minutes **[Target]**.
- **Category:** Developer experience · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:**
  - *SLI:* the elapsed time between the onboarding start and completion events (FR-004).
  - *Target:* < 30 minutes **[Target]**.
  - The statistic (median, p90, or percentage of tenants) is **[Open]**.
- **Measurement:** Event timestamps from FR-004; moderated usability tests with developers new to the platform before launch.
- **Acceptance criteria:**
  1. Usability test participants meet the target under the agreed statistic.
  2. Production onboarding times are reported.
  3. No tests have been run yet.
- **Dependencies / assumptions:**
  - Start and end events are **[Open]** (vision Q10).
  - Excludes time spent waiting for organizational approvals outside the platform **[Assumption]**. **[Open]** Confirm this exclusion.

#### NFR-051: API documentation completeness
- **Requirement:** Every public API operation, error code, and quota shall be documented before the operation is released.
- **Category:** Developer experience · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Target:* 100% documented **[Target]**.
- **Measurement:** A CI check comparing the API specification with the documentation.
- **Acceptance criteria:**
  1. Release fails if a public operation is undocumented.
- **Dependencies / assumptions:** FR-079.

#### NFR-052: Actionable errors
- **Requirement:** Every error response shall include a stable error code, a human-readable message, and the trace ID. Retryable errors shall include retry guidance.
- **Category:** Developer experience · **Priority:** Should · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** API contract tests.
- **Acceptance criteria:**
  1. Contract tests verify the error schema for all documented errors.
- **Dependencies / assumptions:** FR-022, FR-038.

#### NFR-053: API versioning and backward compatibility
- **Requirement:** Public APIs and SDKs shall be versioned. Breaking changes shall be made only in a new version, with a defined deprecation notice period.
- **Category:** Developer experience / Maintainability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Notice period:* **[Open]**.
- **Measurement:** API diff checks in CI.
- **Acceptance criteria:**
  1. CI detects breaking changes to a released version and blocks them.
- **Dependencies / assumptions:** FR-075.

#### NFR-054: Developer satisfaction
- **Requirement:** The platform shall measure developer satisfaction periodically.
- **Category:** Developer experience · **Priority:** Could · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *Target:* **[Open]**; no baseline exists.
- **Measurement:** A survey instrument, to be defined in `success-metrics.md`.
- **Acceptance criteria:**
  1. The first survey establishes a baseline.
- **Dependencies / assumptions:** None.

### 2.11 Maintainability, Upgradeability, and Deployment Safety

#### NFR-055: Zero-downtime deployments
- **Requirement:** Deployments of data-plane services shall not cause the gateway SLI to breach its error budget.
- **Category:** Deployment safety · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** Error budget consumption per deployment is tracked.
- **Measurement:** Run synthetic traffic during deployments in pre-production; compare SLI before and after.
- **Acceptance criteria:**
  1. A rolling deployment under NFR-013 load causes no platform-attributable failures beyond in-flight request draining limits.
- **Dependencies / assumptions:** NFR-004.

#### NFR-056: Progressive delivery and automated rollback
- **Requirement:** Data-plane changes shall roll out progressively, for example via canary, with automated rollback when SLIs regress beyond defined thresholds.
- **Category:** Deployment safety · **Priority:** Should · **Owner:** SRE · **Phase:** KA
- **SLI / SLO:** *Rollback trigger thresholds:* **[Open]**.
- **Measurement:** A deliberate faulty canary in pre-production.
- **Acceptance criteria:**
  1. A faulty canary is rolled back automatically before full rollout.
- **Dependencies / assumptions:** NFR-032.

#### NFR-057: Rollback time
- **Requirement:** Any platform release shall be reversible to the previous version within a defined time.
- **Category:** Deployment safety · **Priority:** Should · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Target:* **[Open]**.
- **Measurement:** A timed rollback exercise.
- **Acceptance criteria:**
  1. A rollback exercise meets the target.
- **Dependencies / assumptions:** Schema migrations must be backward compatible **[Assumption]**.

#### NFR-058: Infrastructure and configuration as code
- **Requirement:** All infrastructure, platform configuration, and policies shall be managed as version-controlled code and changed only through reviewed changes.
- **Category:** Maintainability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** *Target:* 0 unmanaged manual production changes **[Target]**.
- **Measurement:** Drift detection between code and the live environment.
- **Acceptance criteria:**
  1. Drift detection runs on a schedule and alerts on differences.
- **Dependencies / assumptions:** FR-067 (policies as code) **[Assumption]**.

#### NFR-059: Dependency and Kubernetes upgradeability
- **Requirement:** The platform shall keep Kubernetes and its critical dependencies within their supported versions, and shall upgrade them without breaching SLOs.
- **Category:** Upgradeability · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *Upgrade cadence:* **[Open]**.
- **Measurement:** A version inventory; upgrade rehearsal in non-production.
- **Acceptance criteria:**
  1. No production component runs an end-of-support version without an approved exception.
- **Dependencies / assumptions:** None.

#### NFR-060: Automated test gates
- **Requirement:** Each platform change shall pass the following gates in CI before deployment:
  - unit, integration, and contract tests;
  - authorization tests (NFR-026);
  - isolation tests (NFR-020).
- **Category:** Maintainability · **Priority:** Must · **Owner:** Platform eng · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** Pipeline configuration review.
- **Acceptance criteria:**
  1. A change that fails any gate cannot be deployed.
- **Dependencies / assumptions:** None.

### 2.12 Data Privacy, Retention, and Compliance

#### NFR-061: Data classification enforcement
- **Requirement:** The platform shall enforce, through policy, which data classifications may be sent to which models, indexed in RAG, or used for training.
- **Category:** Privacy · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS (model routing); KA / PM (others)
- **SLI / SLO:** None.
- **Measurement:** Policy tests that attempt disallowed combinations.
- **Acceptance criteria:**
  1. Disallowed combinations are rejected and logged.
- **Dependencies / assumptions:** FR-024, FR-051, FR-067. Classifications are **[Open]** (vision Q6).

#### NFR-062: Retention periods
- **Requirement:** Each data type shall have a defined retention period, enforced automatically:
  - audit records;
  - usage records;
  - traces;
  - logs;
  - captured content;
  - agent run state;
  - indexes;
  - model artifacts.
- **Category:** Privacy / Compliance · **Priority:** Must · **Owner:** Security / IAM (with Legal) · **Phase:** VS
- **SLI / SLO:** *Retention values:* **[Open]** (FR-Q6).
- **Measurement:** Lifecycle policy configuration review; sample checks that expired data is deleted.
- **Acceptance criteria:**
  1. Data older than its retention period is not retrievable.
  2. Audit retention meets the agreed minimum.
- **Dependencies / assumptions:** FR-035, FR-036, FR-069.

#### NFR-063: Content minimization by default
- **Requirement:** By default, the platform shall not persist prompt or response content. Persistence shall occur only under FR-036 opt-in, with redaction and the NFR-062 retention.
- **Category:** Privacy · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** *Target:* 0 content persisted without opt-in **[Target]**.
- **Measurement:** Data store inspection and log scanning (NFR-033).
- **Acceptance criteria:**
  1. Inspection of all stores after test traffic without opt-in finds no prompt or response content.
- **Dependencies / assumptions:** FR-036; C6.

#### NFR-064: Provider data-handling requirements
- **Requirement:** Only model providers whose terms prohibit training on CloudForge data, and meet the agreed retention and residency terms, shall be approvable in the catalog.
- **Category:** Privacy / Compliance · **Priority:** Must · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** Review of the provider approval record (FR-025).
- **Acceptance criteria:**
  1. Each approved provider has a recorded data-handling review.
- **Dependencies / assumptions:** **[Assumption]** This is the policy Security will require; to be confirmed (vision Q5).

#### NFR-065: Data residency
- **Requirement:** The platform shall process and store data only in approved regions for each data classification.
- **Category:** Compliance · **Priority:** Should (Must if residency constraints apply) · **Owner:** Security / IAM · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** Configuration audit of regions per store and provider.
- **Acceptance criteria:**
  1. No data store or provider deployment is outside an approved region.
- **Dependencies / assumptions:** **[Open]** Residency constraints (vision Q6).

#### NFR-066: Deletion
- **Requirement:** The platform shall complete verified deletion of tenant or source data within a defined period of a valid request (FR-005, FR-058), except where retention obligations apply.
- **Category:** Privacy · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA
- **SLI / SLO:** *Deletion completion time:* **[Open]**.
- **Measurement:** A deletion test followed by store inspection.
- **Acceptance criteria:**
  1. After deletion, the data is absent from primary stores and indexes.
  2. Data in backups expires per the backup retention period.
- **Dependencies / assumptions:** NFR-036.

#### NFR-067: Compliance control mapping
- **Requirement:** The platform shall maintain a mapping of its controls to the compliance frameworks applicable to CloudForge.
- **Category:** Compliance · **Priority:** Should · **Owner:** Security / IAM · **Phase:** KA
- **SLI / SLO:** None.
- **Measurement:** Document review.
- **Acceptance criteria:**
  1. The mapping exists and is reviewed by Security.
- **Dependencies / assumptions:** **[Open]** Which frameworks apply. None is assumed in this document.

### 2.13 Capacity Planning and Workload Management

#### NFR-068: Capacity model
- **Requirement:** The platform shall maintain a capacity model for gateway, provider quotas, compute, and storage, reviewed on a defined schedule and before onboarding each initial workload.
- **Category:** Capacity · **Priority:** Should · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Review cadence:* **[Open]**.
- **Measurement:** Review records; comparison of forecast with observed usage once data exists.
- **Acceptance criteria:**
  1. A capacity model exists and has been reviewed before each workload launch.
- **Dependencies / assumptions:** No demand data exists yet (vision Q1).

#### NFR-069: Capacity headroom
- **Requirement:** The platform shall keep provisioned or burstable capacity above observed peak demand by a defined headroom factor.
- **Category:** Capacity · **Priority:** Should · **Owner:** SRE · **Phase:** KA
- **SLI / SLO:** *Headroom factor:* **[Open]**.
- **Measurement:** Peak utilization compared with capacity.
- **Acceptance criteria:**
  1. Headroom is reported.
  2. An alert fires when headroom falls below the factor.
- **Dependencies / assumptions:** NFR-068.

#### NFR-070: Provider quota monitoring
- **Requirement:** The platform shall monitor consumption against provider rate limits and quotas, and alert before exhaustion.
- **Category:** Capacity · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Alert threshold:* **[Open]**.
- **Measurement:** Provider quota metrics.
- **Acceptance criteria:**
  1. A simulated approach to the provider limit triggers an alert before rejections begin.
- **Dependencies / assumptions:** NFR-021.

#### NFR-071: Workload priority classes
- **Requirement:** The platform shall support priority classes, such as interactive, batch, and training. Under contention, interactive inference shall be favoured over batch and training workloads.
- **Category:** Workload management · **Priority:** Should · **Owner:** Platform eng · **Phase:** KA / PM
- **SLI / SLO:** None.
- **Measurement:** A contention test mixing interactive and batch load.
- **Acceptance criteria:**
  1. Under contention, interactive requests meet NFR-007 while batch work is delayed or throttled.
- **Dependencies / assumptions:** UC-PM batch and training workloads.

#### NFR-072: Fair scheduling of scarce compute
- **Requirement:** Scarce compute, such as GPU, shall be scheduled fairly across tenants according to quotas and priority.
- **Category:** Workload management · **Priority:** Could · **Owner:** Platform eng · **Phase:** PM
- **SLI / SLO:** *Queue wait targets:* **[Open]**.
- **Measurement:** Scheduling metrics.
- **Acceptance criteria:**
  1. No tenant within its quota is starved in a multi-tenant queue test.
- **Dependencies / assumptions:** GPU need is **[Open]** (UC-PM-Q4).

### 2.14 Operational Support, Incident Response, and Alerting

#### NFR-073: On-call coverage
- **Requirement:** Production platform services shall have a staffed on-call rotation, with defined coverage hours.
- **Category:** Operations · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Coverage hours (for example 24×7 or business hours):* **[Open]**.
- **Measurement:** Rotation schedule review.
- **Acceptance criteria:**
  1. A rotation exists before production launch.
  2. The pager reaches the on-call engineer in a test page.
- **Dependencies / assumptions:** Platform team size is **[Open]** (stakeholders SR6). A 99.9% SLO with business-hours-only coverage may be inconsistent **[Assumption]**.

#### NFR-074: SLO-based alerting
- **Requirement:** Paging alerts shall be based on SLO burn rate (§3.3), not on individual infrastructure signals. Every paging alert shall link to a runbook.
- **Category:** Operations · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** Burn-rate thresholds as in §3.3 **[Target]**.
- **Measurement:** Alert configuration review; synthetic SLI degradation test.
- **Acceptance criteria:**
  1. Synthetic degradation at a fast burn rate triggers a page.
  2. Each alert links to a runbook.
- **Dependencies / assumptions:** NFR-034.

#### NFR-075: Incident severity and response targets
- **Requirement:** The platform shall define incident severity levels with acknowledgement and update-frequency targets for each level.
- **Category:** Operations · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Severity definitions and response targets:* **[Open]**.
- **Measurement:** Incident records: time to acknowledge, time to mitigate.
- **Acceptance criteria:**
  1. Severity definitions are published.
  2. Incident tooling records acknowledgement and mitigation times.
- **Dependencies / assumptions:** Aligns with any existing enterprise incident process **[Assumption]**.

#### NFR-076: Runbooks
- **Requirement:** Runbooks shall exist for each paging alert and for each failure mode in NFR-043 before the relevant phase goes to production.
- **Category:** Operations · **Priority:** Must · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** *Target:* 100% coverage of paging alerts **[Target]**.
- **Measurement:** Comparison of the alert inventory with the runbook inventory.
- **Acceptance criteria:**
  1. No paging alert lacks a runbook.
- **Dependencies / assumptions:** NFR-074.

#### NFR-077: Post-incident reviews
- **Requirement:** Incidents above a defined severity shall receive a blameless post-incident review with tracked actions.
- **Category:** Operations · **Priority:** Should · **Owner:** SRE · **Phase:** VS
- **SLI / SLO:** None.
- **Measurement:** A review record per qualifying incident.
- **Acceptance criteria:**
  1. Each qualifying incident has a review and tracked actions.
- **Dependencies / assumptions:** NFR-075.

#### NFR-078: Tenant status communication
- **Requirement:** The platform shall publish service status and incident updates that tenants can see, and shall attribute incidents to platform, provider, or tenant where known.
- **Category:** Operations · **Priority:** Should · **Owner:** SRE · **Phase:** KA
- **SLI / SLO:** *Update frequency during incidents:* **[Open]** (NFR-075).
- **Measurement:** Status-page records.
- **Acceptance criteria:**
  1. During a simulated incident, a status update is published within the agreed time.
- **Dependencies / assumptions:** FR-038; AC-06.

---

## 3. SLI, SLO, and SLA

### 3.1 Comparison

| Concept | Definition | CloudForge AI status |
|---|---|---|
| **SLI** (Service Level Indicator) | A measured quantity of service behavior, such as the proportion of good requests | Defined (proposed) in NFR-001, 002, 007, 012, 030, 046, 050. **Nothing has been measured yet.** |
| **SLO** (Service Level Objective) | An internal target for an SLI over a window, used to manage reliability through error budgets | **Proposed only [Target]:** 99.9% gateway availability over 30 days (NFR-001); p95 gateway-added latency < 200 ms (NFR-007). All others **[Open]**. |
| **SLA** (Service Level Agreement) | A formal commitment to consumers, with consequences if it is missed | **None exists or is approved.** **[Open]** Whether internal SLAs are needed at all. If they are, they should be looser than the SLOs **[Assumption]**. |

### 3.2 Proposed SLO Summary

| SLO | SLI | Target | Window | Status |
|---|---|---|---|---|
| Gateway availability | Valid requests without platform-attributable failure / valid requests | ≥ 99.9% | Rolling 30 days | **[Target]** |
| Gateway-added latency | p95 of gateway-added latency (non-streaming) | < 200 ms | Rolling 30 days | **[Target]** |
| Gateway-added latency (p99) | p99 | **[Open]** | Rolling 30 days | **[Open]** |
| Streaming TTFB overhead | p95 gateway-added TTFB | **[Open]** | Rolling 30 days | **[Open]** |
| Control-plane availability | Successful / valid control-plane requests | **[Open]** | Rolling 30 days | **[Open]** |
| Retrieval latency | p95 retrieval duration | **[Open]** | Rolling 30 days | **[Open]** |
| Usage/trace freshness | Delay to queryable | **[Open]** | Rolling 30 days | **[Open]** |
| Onboarding time | Start → first successful request | < 30 min (statistic **[Open]**) | Per onboarding | **[Target]** |

### 3.3 Proposed Error-Budget Calculation

The budget follows arithmetically from the proposed 99.9% target. **These figures describe the target. They are not forecasts or measurements.**

**Time-based equivalent (30-day window):**

- 30 days × 24 h × 60 min = **43,200 minutes**
- Error budget = (1 − 0.999) × 43,200 = **43.2 minutes** of full unavailability per 30 days

**Request-based budget (used for the SLO, since the SLI is request-based):**

- Allowed bad requests = 0.001 × (valid requests in the window)
- *Illustrative only:* if a window contained 1,000,000 valid requests, the budget would be 1,000 platform-attributable failures. No request volume forecast exists **[Open]**.

**Comparison of candidate targets (time-based, 30 days):**

| Target | Budget (minutes / 30 days) |
|---|---|
| 99.5% | 216.0 |
| **99.9% (proposed)** | **43.2** |
| 99.95% | 21.6 |
| 99.99% | 4.32 |

**Proposed burn-rate alerting [Target].** This adopts the common multi-window approach. Burn rate = observed error rate ÷ 0.001.

| Alert | Long window | Short window | Burn rate | Budget consumed if sustained over long window | Action |
|---|---|---|---|---|---|
| Fast burn | 1 h | 5 min | 14.4 | 2% (14.4 × 1 h ÷ 720 h) | Page |
| Medium burn | 6 h | 30 min | 6 | 5% (6 × 6 h ÷ 720 h) | Page |
| Slow burn | 3 days | 6 h | 1 | 10% (1 × 72 h ÷ 720 h) | Ticket |

**Proposed error-budget policy [Assumption].** No policy has been agreed:

- If the budget is exhausted within the window, prioritize reliability work over feature releases for the gateway until the SLI recovers.
- Deployments that consume more than a defined share of the budget trigger a review.
- **[Open]** Who has authority to invoke the policy. Proposed: SRE, per stakeholders RACI row 4.

---

## 4. First Vertical Slice NFRs

**Flow [Decision]:**

```
Developer onboarding → AuthN/AuthZ → LLM gateway → inference → usage and trace reporting
```

These NFRs apply to the slice (Phase = VS). Values are **[Target]** or **[Open]** as stated in each requirement.

| Slice step | Required NFRs (Must) | Recommended NFRs (Should) |
|---|---|---|
| Developer onboarding | NFR-050, NFR-051, NFR-053 | NFR-003, NFR-052 |
| AuthN / AuthZ | NFR-020, NFR-022, NFR-024, NFR-025, NFR-026, NFR-029 | NFR-010 |
| LLM gateway | NFR-001, NFR-002, NFR-004, NFR-005, NFR-007, NFR-013, NFR-014, NFR-017, NFR-040, NFR-041, NFR-043 (gateway rows), NFR-055 | NFR-008, NFR-015, NFR-018, NFR-044 |
| Inference | NFR-061 (model routing), NFR-064, NFR-070 | NFR-065 |
| Usage and trace reporting | NFR-023, NFR-030, NFR-031, NFR-032, NFR-033, NFR-037, NFR-045, NFR-046, NFR-062, NFR-063 | NFR-012, NFR-034 |
| Cross-cutting operations | NFR-035, NFR-036, NFR-058, NFR-060, NFR-073, NFR-074, NFR-075, NFR-076, NFR-027, NFR-028 | NFR-038, NFR-057, NFR-068, NFR-077 |

### 4.1 Slice Exit Criteria

| Exit criterion | Evidence required | Status |
|---|---|---|
| Gateway availability SLI instrumented, with 99.9% SLO dashboard (VS-AC6) | NFR-001, NFR-002, NFR-034 | Not started |
| p95 gateway-added latency < 200 ms at 100 concurrent requests | NFR-007 + NFR-013 load-test report | Not started |
| Noisy-neighbour test passes | NFR-017 report | Not started |
| Cross-tenant suite: 0 unexpected allows | NFR-020 CI results | Not started |
| Graceful degradation (metering/trace down → serve; authz down → reject) | NFR-043 fault-injection results | Not started |
| Onboarding usability test < 30 min | NFR-050 report | Not started |
| RTO/RPO agreed for slice data classes | NFR-035 | Values TBD **[Open]** |
| Security assessment complete | NFR-028 report | Not started |

---

## 5. Testing Strategy

No test of any kind has been executed. This section is a plan only.

| Test type | Purpose | Key NFRs | Environment | Cadence (proposed) |
|---|---|---|---|---|
| Unit / integration / contract | Correctness of components and API contracts, including error schema and versioning | NFR-052, NFR-053, NFR-060 | CI | Every change |
| Authorization tests | Positive and deny-by-default coverage for all endpoints | NFR-026 | CI | Every change |
| Cross-tenant isolation suite | Verify no cross-tenant access for every resource type | NFR-019, NFR-020 | CI + each environment | Every release + scheduled |
| Load / performance | Latency, concurrency, scaling | NFR-007–NFR-016 | Pre-production, with mock provider; a limited real-provider run | Each release affecting the data plane; before each phase launch |
| Soak | Stability and SLO achievability over hours | NFR-001, NFR-005 | Pre-production | Before each phase launch |
| Noisy-neighbour | Isolation under aggressor load | NFR-017, NFR-018, NFR-021 | Pre-production | Before each phase launch |
| Fault injection / chaos | Timeouts, retries, circuit breakers, degradation matrix, zone loss | NFR-004, NFR-005, NFR-040–NFR-044, NFR-037 | Pre-production; later in production with safeguards **[Open]** | Before each phase launch, then periodically |
| DR drills / restore tests | RTO/RPO verification | NFR-035, NFR-036, NFR-039 | Dedicated DR exercise | **[Open]** frequency |
| Security assessment / penetration test | Isolation, authorization, secrets, injection | NFR-022–NFR-029 | Pre-production | Before each phase launch |
| Vulnerability and secret scanning | Dependencies, images, repositories, logs | NFR-024, NFR-027, NFR-033 | CI + runtime | Continuous |
| Data-handling inspection | Content minimization, retention, deletion | NFR-062, NFR-063, NFR-066 | Pre-production | Before each phase launch |
| Usability testing | Onboarding time, docs, error clarity | NFR-050, NFR-051, NFR-052 | Pre-production, with developers new to the platform | Before slice launch, then on major changes |
| Deployment safety rehearsals | Zero-downtime, canary rollback, timed rollback | NFR-055–NFR-057 | Pre-production | Each release-pipeline change |
| Reconciliation | Metering completeness and accuracy | NFR-045, NFR-046 | Pre-production, then production | Each billing period |

**Load-test profile (proposed) [Target]:**

- 100 concurrent clients sustained for 30 minutes.
- Mock provider with fixed latency.
- Mixed request sizes. **[Open]** The request size distribution.
- At least 3 synthetic tenants, one of them acting as the noisy-neighbour aggressor.

---

## 6. Traceability to Functional Requirements

| NFR(s) | Qualifies functional requirement(s) | Stakeholder / use-case link |
|---|---|---|
| NFR-001, 002, 004, 005 | FR-017, FR-018, FR-020, FR-038 | AC-05, VS-AC6 |
| NFR-003 | FR-001–FR-004, FR-024, FR-037 | AC-01 |
| NFR-006 | FR-040–FR-050, FR-055, FR-063 | UC-KA, UC-OA, UC-PM |
| NFR-007, 008, 010 | FR-017, FR-022 | S01 |
| NFR-009 | FR-019 | UC-KA |
| NFR-011 | FR-055 | UC-KA-A2 |
| NFR-012 | FR-031, FR-035, FR-037 | AC-12 |
| NFR-013–NFR-016 | FR-017, FR-020 | G6 |
| NFR-017, 018, 021 | FR-029, FR-030 | AC-08, C4 |
| NFR-019 | FR-016 | AC-08, UC-PM-AC5 |
| NFR-020 | FR-012, FR-013 | AC-08, VS-AC4 |
| NFR-022–NFR-025, 029 | FR-003, FR-006, FR-007, FR-023 | AC-07 |
| NFR-026 | FR-008, FR-010 | AC-07, VS-AC3 |
| NFR-027, 028 | All | AC-07, AC-08 |
| NFR-030, 031, 032 | FR-034, FR-035, FR-038 | AC-06, VS-AC5 |
| NFR-033, 063 | FR-036 | C6, SQ8 |
| NFR-034, 074 | FR-038 | AC-05 |
| NFR-035–NFR-039 | FR-069 and all stateful FRs | AC-09 |
| NFR-040–NFR-044 | FR-021, FR-041–FR-043, FR-048, FR-071, FR-073 | UC-KA §4.6, UC-OA §5.6 |
| NFR-045–NFR-047 | FR-031, FR-081, FR-082 | AC-12 |
| NFR-048, 049 | FR-082 | G1, G4 |
| NFR-050–NFR-053 | FR-004, FR-075, FR-076, FR-079 | AC-01, VS-AC2 |
| NFR-054 | (none) | AC-14 |
| NFR-055–NFR-060 | All deployed components | R2 |
| NFR-061 | FR-024, FR-051, FR-067 | vision Q6 |
| NFR-062, 066 | FR-005, FR-035, FR-036, FR-058, FR-069 | AC-09 |
| NFR-064, 065 | FR-024, FR-025 | vision Q5, Q6 |
| NFR-067 | FR-067, FR-068 | S05 |
| NFR-068–NFR-072 | FR-016, FR-029, FR-030, FR-060 | SR6 |
| NFR-073–NFR-078 | FR-038 | AC-06, S04 |

### 6.1 Priority Summary (Draft)

| Priority | Count |
|---|---|
| Must | 45 |
| Should | 31 (includes NFR-065, which becomes Must if residency constraints apply) |
| Could | 2 |
| **Total** | **78** |

---

## 7. Unresolved Questions

| ID | Question | Related NFRs | Suggested owner |
|---|---|---|---|
| NFR-Q1 | Do provider outages count against the gateway availability SLO? (vision Q3) | NFR-001, NFR-002 | SRE, Engineering leadership |
| NFR-Q2 | What are the RTO and RPO for each data and service class? | NFR-035 | SRE, Security, Engineering leadership |
| NFR-Q3 | Single-region or multi-region DR topology? | NFR-035, NFR-039 | EA, SRE |
| NFR-Q4 | Should any internal SLAs exist, or SLOs only? | §3 | Engineering leadership |
| NFR-Q5 | What statistic defines the onboarding target (median, p90, % of tenants), and are approval waits excluded? | NFR-050 | Platform eng, Security |
| NFR-Q6 | What are the p99, streaming TTFB, retrieval latency, and freshness targets? | NFR-008, 009, 011, 012 | Platform eng (after baseline) |
| NFR-Q7 | What is the expected production request volume and growth, beyond the 100-concurrency test target? | NFR-013, NFR-068 | Platform eng, app teams |
| NFR-Q8 | Should an audit-sink outage block ordinary inference, or only sensitive operations? | NFR-005, NFR-043 | Security |
| NFR-Q9 | What are the retention periods per data type? (FR-Q6) | NFR-062 | Security, Legal |
| NFR-Q10 | Which compliance frameworks and residency constraints apply? | NFR-065, NFR-067 | Security, Legal |
| NFR-Q11 | On-call coverage hours, and is the coverage consistent with a 99.9% SLO? | NFR-073 | SRE, Engineering leadership |
| NFR-Q12 | Is mutual TLS required between internal services? Are per-tenant encryption keys required? | NFR-022, NFR-023 | Security |
| NFR-Q13 | What are the metering reconciliation tolerance and the cost-attribution coverage target? | NFR-045, NFR-047 | FinOps |
| NFR-Q14 | Is chaos testing allowed in production, and under what safeguards? | §5 | SRE, Security |
| NFR-Q15 | Who may invoke the error-budget policy? | §3.3 | SRE, Engineering leadership |
