# ADR-003: Hybrid Tenant Isolation

| Field | Value |
|---|---|
| Status | **Proposed** (not Accepted) |
| Date | 2026-11-12 |
| Deciders | Proposed: Security / IAM (A), Enterprise architecture, Platform eng, FinOps. **No review held.** |
| Traces | C3 (efficiency vs isolation); FR-012, FR-013, FR-016; NFR-017–NFR-021; SEC-030–SEC-037; R3 |

## Context

There are about 20 internal teams. Shared infrastructure lowers cost and operating load. Some data classifications may require stronger separation (`stakeholders.md` C3; vision Q6 **[Open]**). A tenant isolation failure is a top risk (R3).

## Decision

Adopt a **hybrid** model:

- **Standard tier (default, pooled):**
  - shared EKS cluster, with a namespace per tenant project;
  - shared gateway;
  - shared OpenSearch domain, with an index per tenant;
  - IAM ABAC on `tenant_id` and `project_id` session tags;
  - default-deny network policy.
- **Restricted tier (siloed resources):**
  - dedicated node pools;
  - dedicated OpenSearch domain;
  - per-tenant KMS keys and buckets;
  - a dedicated AWS account where Security requires it.
- **Assignment:** Security assigns the tier by policy.

## Alternatives Considered

| Option | Why it was not chosen |
|---|---|
| Fully pooled | May not satisfy higher classifications |
| Fully siloed (cluster or account per tenant) | About 20× operating overhead and cost; slows onboarding (NFR-050) |
| Virtual clusters per tenant | Added complexity; benefit unclear at this scale **[Assumption]** |

## Consequences

**Positive:**

- Cost-efficient by default.
- A path to stronger isolation where it is needed.

**Negative:**

- Two operating models.
- Pooled isolation depends on correct logic in every service, so continuous testing is required (SEC-036).

## Risks

- A logical-isolation bug in the pooled tier (ARR-4).
- An unclear tier threshold delays Restricted tenants (AR-Q11).

## Validation Criteria

**None has been executed.**

- V-3: the cross-tenant suite shows 0 unexpected allows **[Target]** across the API, network, IAM, and OpenSearch.
- The noisy-neighbour test (NFR-017) passes.
- Security sets the classification threshold and approves the tier criteria.
