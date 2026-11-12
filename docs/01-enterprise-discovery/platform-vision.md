# CloudForge AI: Platform Vision

| Field | Value |
|---|---|
| Document | Platform Vision |
| Phase | 01: Enterprise Discovery |
| Status | Draft |
| Scope | Multi-tenant enterprise AI Platform as a Service (PaaS) |

> **Note:** CloudForge is a fictional enterprise. This document is a planning artifact. It contains no customer interviews, measured baselines, or production results.

---

## How to Read This Document

Each statement in this document has one of the labels below, so readers can tell decided facts apart from expectations.

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input to discovery, not as an empirically measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. Needs evidence before it is relied on. |
| **[Target]** | A proposed goal. It is not a measured result and has not been committed to. |
| **[Open]** | An unresolved question. It needs an owner and a decision. |

No baselines have been measured yet. Any statement about current-state cost, effort, or duplication is qualitative until the discovery work in this phase produces data.

---

## 1. Executive Summary

CloudForge is a fictional global technology enterprise with about 20 engineering teams **[Decision]**. Teams that build AI-enabled applications each build and run their own LLM gateways, security controls, MCP integrations, monitoring, retrieval-augmented generation (RAG) pipelines, and deployment infrastructure **[Decision]**.

CloudForge AI is a proposed multi-tenant AI Platform as a Service that consolidates this shared infrastructure. A central platform team will provide the common AI capabilities. Application teams will keep ownership of their business logic **[Decision]**.

The platform will be proven through a first vertical slice: developer onboarding → authentication and authorization → LLM gateway → model inference → usage and trace reporting **[Decision]**. Three initial workloads will validate it: an enterprise knowledge assistant, an AI operations agent, and predictive maintenance **[Decision]**.

The proposed success targets are:

- developer onboarding in under 30 minutes;
- 80% adoption across the 20 teams;
- 99.9% LLM gateway availability.

All three are **[Target]**. None has been measured.

---

## 2. Business Problem

### 2.1 Current State (as Established)

The following duplication across teams is an established premise of this program **[Decision]**:

| Duplicated capability | What each team builds independently |
|---|---|
| LLM gateways | Provider access, routing, credentials, rate limiting |
| Security | Authentication, authorization, secrets handling, guardrails |
| MCP integrations | Connectors between agents and tools or data sources |
| Monitoring | Logging, tracing, and metrics for AI workloads |
| RAG | Ingestion, embedding, indexing, and retrieval pipelines |
| Deployment infrastructure | Build, packaging, and runtime environments |

### 2.2 Likely Consequences

The consequences below are expected but **not yet measured**. They are labelled **[Assumption]** until discovery confirms them.

- **Engineering cost:** Effort goes into rebuilding infrastructure instead of product features **[Assumption]**.
- **Inconsistent security posture:** Each team's implementation may enforce different controls, which makes enterprise-wide assurance hard **[Assumption]**.
- **Limited cost visibility:** Model and infrastructure spend is spread across teams and hard to attribute or optimize **[Assumption]**.
- **Fragmented observability:** There is no common view of AI usage, quality, or incidents across the enterprise **[Assumption]**.
- **Slow time to first AI feature:** New teams must set up infrastructure before they can build **[Assumption]**.
- **Governance gaps:** Model approval, data-use policy, and audit trails may be applied unevenly **[Assumption]**.

**[Open]** We have no quantified baseline for any of these consequences. See §11.

---

## 3. Platform Vision

### 3.1 Vision Statement

> Any CloudForge engineering team can build, deploy, and operate secure, observable, cost-attributed AI applications on shared enterprise infrastructure, and can concentrate its effort on business logic that differentiates its product.

### 3.2 Core Services

The platform is planned to provide these core services **[Decision]**:

| Service | Purpose |
|---|---|
| **LLM Gateway** | A single governed entry point to model providers, with routing, quotas, credential isolation, and policy enforcement |
| **Agent Orchestration** | Runtime and patterns for building and running multi-step agents |
| **MCP** | Managed Model Context Protocol servers and a registry of tool and data integrations |
| **RAG** | Shared ingestion, embedding, indexing, and retrieval capabilities |
| **MLOps** | Training, evaluation, model registry, and deployment for non-LLM ML workloads, such as predictive maintenance |
| **Security** | Identity, tenant isolation, authorization, secrets, guardrails, and audit |
| **Observability** | Traces, metrics, and logs for AI requests and agent runs |
| **FinOps** | Usage metering, cost attribution per tenant or team, budgets, and reporting |
| **Kubernetes** | The shared compute substrate for platform services and tenant workloads |
| **Self-Service Developer Tooling** | Onboarding, templates, CLI, portal, and documentation |

### 3.3 Guiding Principles

These are proposed principles. They have not yet been ratified.

1. **Paved road, not a mandate.** The platform should be the easiest path, so teams adopt it because it saves them work.
2. **Multi-tenant by default.** Every service isolates tenants and attributes usage per tenant.
3. **Secure and governed by default.** Controls are built into the platform rather than added by each team.
4. **Observable end to end.** Every request through the platform can be traced and its cost attributed.
5. **Self-service first.** Common tasks need no ticket to the platform team.
6. **Incremental delivery.** Value is proven through thin vertical slices before the platform broadens.

---

## 4. Goals

All goals are **[Target]** unless otherwise stated.

| # | Goal | Description |
|---|---|---|
| G1 | Reduce duplication | Replace team-specific AI infrastructure with shared platform services |
| G2 | Accelerate delivery | Shorten the path from a new team to its first working AI request |
| G3 | Standardize security and governance | Apply consistent identity, authorization, policy, and audit controls |
| G4 | Provide cost transparency | Attribute model and infrastructure usage to teams and workloads |
| G5 | Provide unified observability | Give a common view of AI usage, latency, errors, and traces |
| G6 | Support diverse workloads | Serve LLM-based, agentic, and classical ML workloads |

---

## 5. Scope Boundaries

### 5.1 In Scope

- The shared AI infrastructure services listed in §3.2 **[Decision]**
- Multi-tenant isolation, identity, and authorization for platform services
- Self-service onboarding and developer tooling
- Platform support for the three initial workloads (§5.3)
- The first vertical slice (§7)

### 5.2 Out of Scope

- **Application-specific business logic.** This is owned by application teams **[Decision]**.
- Building or training foundation models **[Assumption]**: the platform consumes models and does not pretrain them.
- End-user product UIs for individual applications **[Assumption]**.
- External or customer-facing commercialization of the platform **[Assumption]**. The "tenants" are internal teams.
- Migrating all existing team infrastructure in the first phase **[Assumption]**.

### 5.3 Initial Workloads

These are **[Decision]**:

| Workload | Primary platform capabilities exercised |
|---|---|
| Enterprise knowledge assistant | LLM gateway, RAG, security (document-level access), observability |
| AI operations agent | Agent orchestration, MCP integrations, security (tool authorization), observability |
| Predictive maintenance | MLOps, Kubernetes, observability, FinOps |

The capability mapping above is the proposed expected fit **[Assumption]**. The detailed use cases will be written in `use-cases.md`.

---

## 6. Operating Model

### 6.1 Responsibility Split

These are **[Decision]**:

| Area | Platform team | Application teams |
|---|---|---|
| Shared AI infrastructure (gateway, RAG, MCP, MLOps, and so on) | Builds, operates, and supports it | Consumes it |
| Security and governance controls | Provides and enforces them | Complies with them; configures app-level policy |
| Observability and FinOps tooling | Provides it | Uses it; owns its app-level dashboards |
| Business logic, prompts, agents, domain data | Not responsible | Owns them |
| Application availability and quality | Provides the platform SLOs | Owns application outcomes |

### 6.2 Engagement Model (Proposed)

- **Self-service by default:** Onboarding, credentials, and quotas are available through tooling **[Assumption]**.
- **Consultative support** for novel workloads or exceptions **[Assumption]**.
- **Early-adopter partnership** with the teams that own the three initial workloads **[Assumption]**.

**[Open]** The funding model (central funding, chargeback, or showback), the platform team's size, and the support tiers are not yet decided.

---

## 7. First Vertical Slice

### 7.1 Flow

This is **[Decision]**:

```
Developer onboarding
        │
        ▼
Authentication / Authorization
        │
        ▼
LLM Gateway
        │
        ▼
Model inference
        │
        ▼
Usage and trace reporting
```

### 7.2 Purpose

The slice is meant to prove, end to end and in the thinnest form possible, that:

1. a new team can onboard itself and get credentials;
2. requests are authenticated, authorized, and attributed to a tenant;
3. the gateway routes requests to a model and returns a response;
4. each request produces usage (cost) and trace records that the team can see.

### 7.3 Explicitly Deferred from the Slice

RAG, agent orchestration, MCP, and MLOps are deferred to later increments **[Assumption]**.

---

## 8. Proposed Success Metrics

All values below are **[Target]**. They are proposals only and have not been measured or committed to. The full definitions will be written in `success-metrics.md`.

| Metric | Proposed target | Measurement notes |
|---|---|---|
| Developer onboarding time | Under 30 minutes | From the start of self-service onboarding to the first successful authenticated gateway request. **[Open]** Exact start and end events need definition. |
| Platform adoption | 80% of the 20 teams | **[Open]** "Adopted" needs a definition, for example production traffic through the gateway. A time horizon is also needed. |
| LLM gateway availability | 99.9% | **[Open]** The measurement window, what counts as a successful request, and how upstream provider outages are treated all need definition. |

**Baseline:** None exists. The current onboarding time, adoption, and availability of team-built gateways have not been measured.

---

## 9. Assumptions

| ID | Assumption | Validation approach |
|---|---|---|
| A1 | Duplication across teams causes material cost and risk | Discovery inventory of team-owned AI infrastructure |
| A2 | Teams will adopt a shared platform if it is easier than their current approach | Early-adopter feedback; adoption tracking |
| A3 | The three initial workloads are representative of broader demand | Use-case review across teams |
| A4 | A single gateway can meet the latency and availability needs of all initial workloads | Nonfunctional requirements analysis; load testing |
| A5 | Kubernetes is a suitable shared compute substrate for all initial workloads | Architecture review |
| A6 | Tenants are internal teams only | Stakeholder confirmation |
| A7 | Approved external model providers and/or self-hosted models will be available | Security and procurement review |
| A8 | Organizational sponsorship exists for the platform team | Executive confirmation |

---

## 10. Risks

Likelihood and impact are qualitative and still to be assessed.

| ID | Risk | Potential impact | Proposed mitigation |
|---|---|---|---|
| R1 | Low adoption: teams keep their own stacks | Duplication remains; the 80% target is missed | Paved-road usability, migration support, early-adopter partnerships |
| R2 | The gateway becomes a single point of failure | Outages affect every tenant at once | HA design, multi-provider routing, explicit SLOs, graceful degradation |
| R3 | Tenant isolation failure | Data or credentials leak between teams | Isolation by design, security review, testing (see `security-governance.md`) |
| R4 | Scope creep across ten core services | Delivery stalls before value is shown | Vertical-slice delivery; strict scope boundaries |
| R5 | Platform team becomes a bottleneck | Slow delivery for application teams | Self-service tooling; a clear operating model |
| R6 | Unclear cost attribution or funding | Disputes over spend; adoption is discouraged | FinOps metering from the first slice; an agreed funding model |
| R7 | Dependency on and changes by model providers | Breaking changes, pricing shifts, availability issues | Provider abstraction in the gateway; multi-provider support |
| R8 | Diverse workload needs (LLM, agents, classical ML) | The platform fits no workload well | Prioritize by initial workloads; extensible design |

---

## 11. Open Questions

| ID | Question | Suggested owner |
|---|---|---|
| Q1 | What are the current baselines for duplicated effort, spend, onboarding time, and incident rates? | Platform team / FinOps |
| Q2 | How is "adoption" defined, and by what date should 80% be reached? | Platform leadership |
| Q3 | How is 99.9% gateway availability measured, including treatment of provider outages? | Platform SRE |
| Q4 | What is the funding model: central, showback, or chargeback? | Finance / Executive sponsor |
| Q5 | Which model providers and hosting options are approved? | Security / Procurement |
| Q6 | What data classifications may flow through the platform, and what residency constraints apply? | Security / Legal / Compliance |
| Q7 | Is adoption expected or mandated for new AI workloads? | Executive sponsor |
| Q8 | How will existing team-built infrastructure be migrated or retired? | Platform team with application teams |
| Q9 | Which teams own the three initial workloads, and are they committed as early adopters? | Platform leadership |
| Q10 | What are the start and end events for measuring onboarding time? | Platform team / Developer experience |

---

## Related Documents

- `stakeholders.md`
- `use-cases.md`
- `functional-requirements.md`
- `nonfunctional-requirements.md`
- `security-governance.md`
- `success-metrics.md`
- `coverage-audit.md`
