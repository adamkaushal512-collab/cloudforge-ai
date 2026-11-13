# CloudForge AI: Control Plane and Data Plane

| Field | Value |
|---|---|
| Document | Control Plane / Data Plane Separation |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. Not implemented. |
| ADR | `adr/002-control-data-plane-separation.md` |

---

## 1. Purpose

This document defines what the control plane manages, what the data plane executes, how configuration flows between them, and how the platform behaves safely when either plane, or a dependency, fails.

Labels are as in `architecture-overview.md` §1.1. **Nothing described here is implemented or tested.**

---

## 2. Responsibilities

| Concern | Control plane (management) | Data plane (execution) |
|---|---|---|
| Tenants and projects | Create, update, deactivate (FR-001, FR-002, FR-005) | Reads the tenant and project context from validated tokens and the config snapshot |
| Credentials | Issue, revoke (FR-003) | Validates credentials; checks the revocation list in the snapshot |
| Roles and entitlements | Role bindings, model entitlements (FR-008, FR-026) | Enforces them through the embedded policy decision point (PDP) |
| Policy | Author, version, approve (FR-067) | Evaluates signed policy bundles locally |
| Model catalog and providers | Lifecycle, routing aliases, provider configuration (FR-024–FR-027) | Routes using the catalog snapshot |
| Quotas and limits | Define limits (FR-029, FR-030) | Counts and enforces them in the rate-limit store |
| MCP registry and source registry | Register, classify, approve (FR-046, FR-047, FR-051) | The MCP broker and ingestion workers enforce the registered state |
| Approvals | Approval service: requests, decisions, timeouts (FR-071) | Agent runs pause and resume; the broker checks for a valid approval record |
| Reporting | Usage and trace query APIs (FR-037) | Emits usage events and traces |
| Executes inference, retrieval, agents, tools, training | Never | Always |

**Rule [Proposed]:** No synchronous call from the data-plane request path to the control plane. The only exception is approval lookups for sensitive operations, which deliberately fail closed.

---

## 3. Configuration Distribution

The mechanism below is **[Proposed]**.

1. Every committed control-plane change produces a new **config snapshot version**. A snapshot contains:
   - tenants, projects, and entitlements;
   - the revocation list;
   - the catalog;
   - quotas;
   - the policy bundle;
   - the MCP registry.
2. The snapshot is **signed** with a KMS key and published to an object store.
3. Data-plane services poll for new versions, or are notified of them. They verify the signature and then swap atomically to the new version.
4. Each service reports the **snapshot version it is running** as a metric. SRE alerts on version skew or staleness.
5. **Propagation target:** **[Open]**. It must not exceed the credential revocation delay (NFR-025).

**Why snapshots and not live lookups:**

- They keep the gateway latency budget, p95 < 200 ms **[Target]** (NFR-007).
- They decouple data-plane availability from control-plane availability (NFR-003).

---

## 4. Safe Behavior During Outages

Each row aligns with NFR-043 (graceful degradation). All behaviors are **[Proposed]** and untested.

| Failure | Data-plane behavior | Control-plane behavior | Safety rationale |
|---|---|---|---|
| **Control plane down** | Keep serving with the last-known-good snapshot, up to a **maximum staleness** of **[Open]**; after that, fail closed | Onboarding, credential issuance, and config changes unavailable | Availability of existing traffic. The staleness cap limits how long a revoked credential can stay usable. |
| **Config distribution down** | As above | Changes are committed but not propagated; alert fires | Same |
| **Microsoft Entra ID down** | Existing tokens keep validating against cached signing keys until they expire; new token acquisition fails | Logins fail | Tokens are short-lived (NFR-025), which bounds exposure |
| **Policy bundle invalid or signature fails** | Reject the new bundle; keep the previous one; alert | n/a | Never run unsigned policy |
| **Rate-limit store down** | **[Open]**: fail closed (reject), or fall back to conservative per-instance limits for a bounded time | n/a | Prevents unbounded spend while keeping availability. Needs a decision (AR-Q8). |
| **Usage pipeline down** | Serve; buffer usage events durably on local disk with backpressure; backfill later | n/a | NFR-005, NFR-046 |
| **Observability backend down** | Serve; drop or buffer spans | n/a | NFR-005 |
| **Audit store unreachable** | Block sensitive operations (FR-073). **[Open]** whether to block ordinary inference (NFR-Q8). | Block control-plane writes that require audit **[Proposed]** | No unaudited security-relevant change |
| **Approval service down** | Sensitive actions stay pending, then expire; never auto-approve | Approvals unavailable | SEC-050 |
| **Amazon Bedrock degraded** | Circuit breaker; fail over to an alternate approved model or region profile, if configured (FR-021); otherwise an explicit error | n/a | NFR-042 |
| **One Availability Zone lost** | Remaining zones serve (at least 2 replicas across 2 zones) | Aurora fails over | NFR-004 |

---

## 5. Data-Plane Independence Checklist

These are design review checks. **None has been verified.**

- [ ] The gateway request path has no synchronous dependency on the control-plane API or database.
- [ ] Every data-plane service exposes its snapshot version and age as metrics.
- [ ] Maximum snapshot staleness is configured and enforced, failing closed when exceeded.
- [ ] Signed bundle verification is tested with a tampered bundle.
- [ ] Fault injection covers each row of §4 (NFR §5 testing strategy).

---

## 6. Open Questions

| ID | Question |
|---|---|
| AR-Q8 | What does the gateway do when the rate-limit store fails: fail closed, or apply bounded local limits? |
| AR-Q9 | What are the maximum snapshot staleness and the propagation target? These must fit within NFR-025. |
| AR-Q10 | Should the approval lookup be a synchronous call to the approval service, or be carried as a signed approval token? |
