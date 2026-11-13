# ADR-005: AI Integration Boundaries

| Field | Value |
|---|---|
| Status | **Proposed** (not Accepted) |
| Date | 2026-11-12 |
| Deciders | Proposed: Enterprise architecture (A), Platform eng, Security / IAM, Data engineering, ML engineering representatives. **No review held.** |
| Traces | FR-040–FR-066, FR-071; FR-Q9; UC-OA-Q4; SEC-020, SEC-043, SEC-045, SEC-050; NFR-043 |

## Context

Phase 2 introduces several candidate frameworks: LangGraph, Temporal, MCP, OpenSearch, MLflow, OpenTelemetry, and Entra ID / AWS IAM. Their responsibilities overlap: durable state, retries, authorization, and storage. Phase 1 left the orchestration framework open (FR-Q9) and placed checkpointing in the agent runtime (FR-042).

## Decision

The decision has six parts, set out in `ai-platform-integrations.md` §2:

1. **LangGraph** owns agent run execution and checkpoints, including approval interrupts.
2. **Temporal** owns long-running *platform* workflows: ingestion and re-sync, promotion pipelines, and approval timers. It never owns an agent run's reasoning state.
3. **The MCP broker** is the only path to tools. **The gateway** is the only path to models. Both are enforced by network egress policy.
4. **The retrieval service** is the only path to OpenSearch for tenants, and it applies ACL filters server-side.
5. **MLflow** owns tracking and registry metadata. It is never an authorization source.
6. **Authorization** is always deterministic policy (SEC-020). No framework, and no model output, makes authorization decisions.

## Alternatives Considered

| Option | Why it was not chosen |
|---|---|
| Temporal for everything (agent runs as Temporal workflows wrapping LangGraph steps) | Two state models per run; more complexity for UC-OA. Revisit if run durability needs exceed LangGraph checkpoints. |
| LangGraph only (no Temporal) | Weak fit for long-running ingestion and promotion pipelines; Temporal can be deferred until UC-KA |
| Direct tool and model access from agents | Breaks SEC-043, SEC-051, and FR-022 |
| Dedicated vector DB instead of OpenSearch | Adds a new technology; OpenSearch is a managed AWS service **[Assumption]** sufficient for UC-KA |

## Consequences

**Positive:**

- Clear ownership.
- Single choke points for models and tools.
- Simpler security review.

**Negative:**

- Two orchestration technologies (ARR-5).
- MLflow requires a multi-tenancy wrapper (ARR-7).

## Risks

- Boundary drift as teams take shortcuts. Mitigated by egress policy and architecture review.
- OpenSearch ACL-filter performance is unverified (AR-Q22).

## Validation Criteria

**None has been executed.**

- V-6: OpenSearch ACL-filtered retrieval shows zero leakage, with latency recorded.
- V-7: LangGraph interrupt and resume with the approval service; no repeated tool calls; no execution without approval.
- Egress tests: tenant namespaces cannot reach Bedrock or tool endpoints directly.
