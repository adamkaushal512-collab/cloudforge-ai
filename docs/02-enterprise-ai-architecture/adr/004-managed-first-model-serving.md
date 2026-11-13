# ADR-004: Managed-First Model Serving

| Field | Value |
|---|---|
| Status | **Proposed** (not Accepted) |
| Date | 2026-11-12 |
| Deciders | Proposed: Enterprise architecture (A), Security / IAM, FinOps, Platform eng. **No review held.** |
| Traces | Vision §5.2 (consume, not pretrain); vision A7, Q5; R7; FR-020, FR-021, FR-025; NFR-064, NFR-065; SEC-042, SEC-043, SEC-083 |

## Context

The platform consumes models and does not train foundation models (vision §5.2). The platform team's capacity is limited (SR6). Phase 1 left the approved providers open (vision Q5).

## Decision

1. **Amazon Bedrock is the default model source.** Access is through IAM roles and VPC interface endpoints, with no static keys. Bedrock is subject to Security's provider approval and data-handling review (SEC-042, NFR-064).
2. **Self-hosted vLLM on EKS is optional.** It is enabled for a model only when at least one of these criteria is met **[Proposed]**:
   - (a) the required model is unavailable on Bedrock in approved regions;
   - (b) a classification or residency constraint rules out Bedrock;
   - (c) sustained volume makes self-hosting cheaper on a FinOps analysis, with the threshold **[Open]**.
3. **The vertical slice uses Bedrock only.**

## Alternatives Considered

| Option | Why it was not chosen |
|---|---|
| Self-hosted first (vLLM for all models) | High GPU and operations burden; slower to the first slice |
| Multiple external API providers from the start | More approvals and egress paths; can be added later through gateway adapters |
| SageMaker endpoints for open models | Viable alternative to vLLM on EKS; not chosen to keep one compute platform (EKS). Revisit if GPU operations prove costly. |

## Consequences

**Positive:**

- Fastest path to the slice.
- No GPU operations initially.
- Model breadth through one provider.

**Negative:**

- Dependence on Bedrock quotas and model availability.
- Per-token pricing at high volume.
- Region-dependent model availability.

## Risks

- Insufficient quotas (ARR-2).
- Required models are absent from Bedrock.
- Cross-region inference conflicts with residency (AR-Q16).

## Validation Criteria

**None has been executed.**

- V-4: Bedrock spike via PrivateLink with IAM-only access. Inference and embeddings work, and quotas are documented.
- Security approval of Bedrock and of the initial model list.
- A documented FinOps threshold for criterion (c).
