# ADR-001: Centralized LLM Gateway

| Field | Value |
|---|---|
| Status | **Proposed** (not Accepted) |
| Date | 2026-11-12 |
| Deciders | Proposed: Enterprise architecture (A), Platform eng, Security / IAM, SRE. **No review held.** |
| Traces | G1, G3, G4; FR-017–FR-031; NFR-001, NFR-007; SEC-020–SEC-023, SEC-041; C4, R2 |

## Context

About 20 teams each build their own model access, credentials, and monitoring (vision §2.1). Phase 1 requires the following:

- one provider-agnostic API (FR-017);
- central policy enforcement before routing (FR-022);
- central provider credentials (FR-023);
- per-request metering (FR-031).

The gateway is also the main single-point-of-failure risk (R2).

## Decision

All LLM and embedding traffic shall pass through one multi-tenant LLM gateway, operated by the platform team. The gateway is the **authoritative** layer for:

- authentication;
- authorization (an embedded PDP over signed policy);
- quotas and rate limits;
- routing and failover;
- usage metering.

**LiteLLM is a candidate implementation aid only.** It is not deployed and not selected. If adopted, it must sit *behind* CloudForge's own authentication, policy, and metering, and must not replace them.

## Alternatives Considered

| Option | Why it was not chosen |
|---|---|
| Per-team SDK access directly to providers | Perpetuates duplication; no central policy or metering (G1, G3, G4) |
| Shared client SDK only (no gateway) | Cannot enforce policy or protect credentials server-side |
| Managed API gateway in front of Bedrock only | Lacks tenant-aware metering, model entitlement, and multi-provider routing **[Assumption]** |
| Adopt LiteLLM proxy as the gateway, as-is | Undecided. Subject to evaluation (V-5); control-plane integration and authZ ownership are the concerns. |

## Consequences

**Positive:**

- One place for policy, metering, and credentials.
- Enables KPI-10 and KPI-14.
- Provider abstraction (R7).

**Negative:**

- An extra network hop.
- The gateway becomes a tier-0 service requiring HA (NFR-004), and the platform team owns that reliability.

## Risks

- Latency budget breach (ARR-1).
- Single point of failure (R2), mitigated by multi-AZ deployment, ADR-002 snapshots, and failover.
- Supply-chain risk if LiteLLM is adopted (ARR-6).

## Validation Criteria

**None has been executed.**

- V-1 load test: p95 gateway-added latency < 200 ms at 100 concurrent requests; error rate < 0.1% **[Target]**.
- Negative tests: unauthenticated requests, non-entitled models, and over-quota requests never reach a provider.
- V-5: a written LiteLLM evaluation, with a recorded decision.
