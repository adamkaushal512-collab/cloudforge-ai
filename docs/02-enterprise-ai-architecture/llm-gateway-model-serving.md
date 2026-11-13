# CloudForge AI: LLM Gateway and Model Serving

| Field | Value |
|---|---|
| Document | LLM Gateway and Model Serving Architecture |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. Not implemented. |
| ADRs | `adr/001-centralized-llm-gateway.md`, `adr/004-managed-first-model-serving.md` |
| Diagrams | `c3-llm-gateway-components.mmd`, `ai-request-flow.mmd` |

---

## 1. Purpose

This document describes the internal design of the LLM gateway and how it routes to Amazon Bedrock and, optionally, to self-hosted vLLM on EKS.

**No gateway has been built. No latency or throughput figure here has been measured.**

---

## 2. Gateway Components (C3)

**Diagram:** `diagrams/02-enterprise-ai-architecture/c3-llm-gateway-components.mmd`. All components are **[Proposed]**.

| Component | Responsibility | Phase 1 trace |
|---|---|---|
| API handler | Provider-agnostic inference, embeddings, and streaming endpoints; request validation and size limits | FR-017–FR-019, FR-022 |
| Authenticator | Validates Entra ID tokens or project credentials using cached JWKS; checks the revocation list from the snapshot | FR-006, FR-007, SEC-012, SEC-013 |
| Policy enforcement point (with embedded PDP) | Evaluates the tenant, project, role, model entitlement, and data classification against the signed policy bundle | FR-010, FR-022, SEC-020, SEC-023, SEC-044 |
| Rate limiter / quota enforcer | Request, token, and concurrency limits per tenant and project | FR-029, FR-030, NFR-018 |
| Guardrail hooks | Optional input and output checks (FR-074). Advisory signals only; never a source of permission. | FR-074, SEC-048 |
| Router | Resolves the logical model alias to a deployment; failover; circuit breakers; timeouts and retries | FR-020, FR-021, NFR-040–NFR-042 |
| Provider adapters | The Bedrock adapter (AWS SDK, Converse / InvokeModel APIs) and the OpenAI-compatible adapter (vLLM) | FR-017 |
| Usage emitter | Asynchronous, durable usage events (tokens, cost estimate, error class) | FR-031, FR-038, FR-081 |
| Telemetry | OpenTelemetry spans and metrics; trace ID propagation | FR-034, FR-035, NFR-030–NFR-032 |
| Config cache | Holds and verifies signed snapshots from the control plane | ADR-002 |

**Request pipeline order [Proposed]:**

```
handler → authenticate → authorize (PDP) → rate limit/quota → guardrails (input)
        → route → provider call → guardrails (output) → respond
```

Usage and telemetry are emitted asynchronously at completion.

Requests rejected by authentication, policy, or quota never reach a provider (FR-022 acceptance criteria).

---

## 3. Routing

| Aspect | Design [Proposed] |
|---|---|
| Aliases | The catalog maps a logical ID (for example `chat-general`) to one or more deployments, in priority order |
| Bedrock deployments | A Bedrock model ID or inference profile in an approved region. **[Open]** Whether cross-region inference profiles are permitted, given residency (NFR-065). |
| vLLM deployments | Internal Kubernetes service endpoint for each served model |
| Failover | Only to deployments the project is entitled to, with a compatible data classification (FR-021) |
| Circuit breaker | Per deployment; thresholds **[Open]** (NFR-042) |
| Timeouts / retries | Bounded; retries only on retryable errors (NFR-040, NFR-041) |
| Error classes | Platform / provider / tenant, used for availability measurement (FR-038, NFR-002) |

---

## 4. Latency Budget

The p95 gateway-added latency target is under 200 ms **[Target]** (NFR-007). It **excludes** model inference.

The budget split below is **illustrative and unmeasured**:

| Stage | Design intent |
|---|---|
| Authentication | Local JWT verification; no network call per request |
| Authorization | In-process PDP over a cached bundle |
| Rate limiting | One round trip to the Redis-compatible store in the same AZ |
| Routing | In-memory |
| Usage / telemetry | Off the critical path (asynchronous) |

**Validation:** The NFR-013 load test with a mock provider is planned and has **not** been run.

---

## 5. LiteLLM: A Candidate, Not a Deployed Fact

LiteLLM is **not deployed, has not been evaluated, and has not been selected**. It is one candidate for implementing the provider adapters and part of the routing layer. It could be used either as a library inside the gateway, or as an internal proxy behind CloudForge's own authentication and policy layer.

The evaluation criteria below are **[Proposed]**:

| Criterion | Question to answer |
|---|---|
| Control | Can CloudForge keep its own authN/authZ, policy, quota, and metering as the authoritative layer (ADR-001)? |
| Bedrock support | Does it cover the needed Bedrock APIs, streaming, and embeddings? |
| Latency | Does it fit within the NFR-007 budget under the NFR-013 load? |
| Security | Supply-chain review (SEC-080); no credential exposure (SEC-041) |
| Operability | OpenTelemetry support, failure behavior, upgrade cadence |
| Licensing / support | Acceptable license and support model for enterprise use **[Open]** |

**Alternatives:**

- a custom adapter layer on the AWS SDK;
- other open-source gateways;
- a managed API gateway in front of Bedrock, which alone is insufficient for tenant metering and policy **[Assumption]**.

---

## 6. Model Serving

### 6.1 Amazon Bedrock (Default)

Bedrock is the default model source **[Proposed]** (ADR-004).

- **Access:** Via IAM role, with no static keys. Reached through a VPC interface endpoint (PrivateLink).
- **Throughput:** On-demand initially. Provisioned throughput **[Open]**, to be decided on observed demand.
- **Before launch:**
  - per-account, per-region quotas must be confirmed **[Open]** (NFR-070);
  - model approval and a data-handling review are required (SEC-042, NFR-064).

### 6.2 Self-Hosted vLLM on EKS (Optional)

**Not part of the vertical slice.** This option is enabled only if ADR-004 criteria are met. Examples:

- a required model is unavailable on Bedrock;
- a classification or residency constraint rules Bedrock out;
- sustained volume makes self-hosting cheaper.

**Design [Proposed]:**

- GPU node pool (Karpenter, candidate).
- vLLM Deployments, one per model, exposing the OpenAI-compatible API.
- Weights pulled from an approved, integrity-verified artifact store (SEC-083).
- Autoscaling on queue depth or utilization.
- GPU cost attributed to the platform or to dedicated tenants (FR-082).

**Risks:** GPU capacity availability; operational burden; model licensing; patching cadence.

---

## 7. Open Questions

| ID | Question |
|---|---|
| AR-Q15 | Adopt LiteLLM (library or proxy), or a custom adapter? (ADR-001 validation) |
| AR-Q16 | Are Bedrock cross-region inference profiles acceptable under residency policy? |
| AR-Q17 | Which models make up the initial approved catalog? (vision Q5) |
| AR-Q18 | What thresholds trigger provisioned throughput or vLLM? (ADR-004) |
