# ADR-002: Control-Plane / Data-Plane Separation

| Field | Value |
|---|---|
| Status | **Proposed** (not Accepted) |
| Date | 2026-11-12 |
| Deciders | Proposed: Enterprise architecture (A), Platform eng, SRE, Security / IAM. **No review held.** |
| Traces | NFR-003, NFR-005, NFR-007, NFR-025, NFR-043; FR-067; SEC-020 |

## Context

Phase 1 requires three things:

- control-plane outages must not stop inference (NFR-003);
- the gateway must stay within a strict latency budget (NFR-007);
- degraded behavior must be explicit, including failing closed on security (NFR-043).

Live control-plane lookups on every request would couple availability and add latency.

## Decision

- The control plane is the sole writer of configuration. It publishes **versioned, KMS-signed config snapshots**: tenants, entitlements, the revocation list, the catalog, quotas, policy, and registries.
- Data-plane services verify the signature and evaluate policy locally. They make **no synchronous calls** to the control plane in the request path. The exception is approval checks for sensitive operations, which fail closed.
- Each data-plane service enforces a **maximum snapshot staleness**. Once the cap is exceeded, it fails closed. The value is **[Open]** and must be at most the NFR-025 revocation delay.

## Alternatives Considered

| Option | Why it was not chosen |
|---|---|
| Synchronous lookups to the control-plane API | Couples availability; adds latency |
| Shared database read by both planes | Tight coupling; blast radius |
| Push-only without signature | Integrity risk (tampered policy) |

## Consequences

**Positive:**

- The data plane survives control-plane outages.
- Predictable latency.
- The policy version used for every decision is auditable (SEC-024).

**Negative:**

- Config changes, including revocations, propagate with a delay.
- Snapshot size and distribution must scale with tenants.
- Version-skew monitoring is required.

## Risks

- Stale snapshots allow a revoked credential (ARR-3).
- Bugs in snapshot generation propagate everywhere. Mitigation: canary rollout of snapshots **[Proposed]**.

## Validation Criteria

**None has been executed.**

- V-2 fault injection: with the control plane down, the data plane serves until the staleness cap and then fails closed.
- A tampered bundle is rejected, and the previous version is retained.
- A revocation timing test meets NFR-025 (value **[Open]**).
