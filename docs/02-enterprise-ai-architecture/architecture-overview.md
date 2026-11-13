# CloudForge AI: Architecture Overview

| Field | Value |
|---|---|
| Document | Architecture Overview |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. Not implemented, not reviewed, not approved. |
| Inputs | All documents in `docs/01-enterprise-discovery/` |
| Diagrams | `diagrams/02-enterprise-ai-architecture/c1-system-context.mmd`, `c2-container-architecture.mmd`, `c3-llm-gateway-components.mmd`, `ai-request-flow.mmd` |

---

## 1. Purpose and Status

This document describes the **proposed** target architecture for CloudForge AI. The architecture must:

- serve about 20 engineering teams **[Decision]**;
- support the first vertical slice and the three initial workloads: UC-KA (knowledge assistant), UC-OA (operations agent), and UC-PM (predictive maintenance) **[Decision]**;
- meet the Phase 1 requirements: FR-001–FR-085, NFR-001–NFR-078, and SEC-010–SEC-083.

> **Status of everything in this document:**
>
> - **Nothing has been built or deployed.**
> - **No performance, availability, or security test has been run.**
> - **No architecture review or stakeholder approval has taken place.**
> - **All ADRs are *Proposed*.**
>
> Named products are design candidates, not deployed components.

### 1.1 Labels

The labels are the same as in Phase 1:

| Label | Meaning |
|---|---|
| **[Decision]** | An established Phase 1 decision. |
| **[Proposed]** | An architecture choice recorded in a Proposed ADR. It awaits review. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal (from Phase 1). It is not measured. |
| **[Open]** | Unresolved. |

**[Proposed]** is added in Phase 2 to mark architecture choices. It does not upgrade any choice to a **[Decision]**.

---

## 2. Phase 1 Contradictions and New Inputs

These items come from comparing the Phase 2 brief with Phase 1. Phase 1 documents are not modified.

| ID | Item | Phase 1 position | Phase 2 handling |
|---|---|---|---|
| P2-C1 | Cloud and vendor stack (AWS, Amazon Bedrock, EKS, vLLM, OpenSearch, MLflow, Temporal, LangGraph, LiteLLM) | Not named. Providers are **[Open]** (vision Q5); orchestration framework **[Open]** (FR-Q9); only Kubernetes is assumed (vision A5). | Treated as **[Proposed]** candidates in ADRs. Each requires Security approval of providers (SEC-042, NFR-064). |
| P2-C2 | Temporal as a second durable-execution engine | FR-042 assigns run checkpointing to the agent runtime | Boundary rule: each run's state has exactly one owner (`ai-platform-integrations.md` §3, ADR-005) |
| P2-C3 | Identity provider | Entra ID is a **[Decision]** in FR and SEC, but `stakeholders.md` SQ4 still lists it as open (Phase 1 GAP-1) | Entra ID used; the Entra-to-AWS federation design is in `multi-tenancy-isolation.md` §3 |
| P2-C4 | Phase 1 audit Git status | The Phase 1 audit records "not a Git repository" (B-1, CC-8) | Now stale: Phase 1 is committed (`aea5c8c`). Recorded in the Phase 2 coverage audit. |
| P2-C5 | Phase 2 syllabus and 18-phase roadmap | Not in the repository (Phase 1 GAP-7) | Steps 2.1–2.8 are inferred from the deliverable list **[Assumption]** (`coverage-audit.md`) |

---

## 3. Architecture Principles

These principles are **[Proposed]**. Each one traces to Phase 1.

| # | Principle | Source |
|---|---|---|
| AP-1 | **One governed path to models.** All LLM and embedding traffic goes through the LLM gateway (ADR-001). | G1, G3; FR-017, FR-022 |
| AP-2 | **The control plane configures; the data plane executes.** The data plane keeps serving with last-known-good configuration when the control plane is down (ADR-002). | NFR-003, NFR-005, NFR-043 |
| AP-3 | **Pooled by default, siloed by classification.** Hybrid tenant isolation (ADR-003). | C3; SEC-030–SEC-037 |
| AP-4 | **Managed first.** Amazon Bedrock is the default model source. Self-hosted vLLM is added only when defined criteria are met (ADR-004). | Vision §5.2; R7 |
| AP-5 | **Deterministic authorization.** Policy is evaluated outside any model. An LLM recommendation is never an authorization decision. | SEC-020; `security-governance.md` §1.3 |
| AP-6 | **Explicit integration boundaries.** Each framework owns one responsibility (ADR-005). | FR-040–FR-066 |
| AP-7 | **Fail closed on security, fail open on telemetry.** | NFR-043 |
| AP-8 | **Attributable by construction.** Every request and every workload carries tenant and project identity end to end. | FR-012, FR-031, KPI-10 |

---

## 4. System Context (C1)

**Diagram:** `diagrams/02-enterprise-ai-architecture/c1-system-context.mmd`

| Element | Type | Relationship to CloudForge AI |
|---|---|---|
| AI developer / ML engineer (S01, S02) | Person | Onboards, builds and deploys workloads, views usage and traces |
| Employee end user | Person | Uses tenant applications such as the knowledge assistant. Never calls the platform directly. |
| Approver / Security (S05) | Person | Approves sensitive operations; administers policy |
| Platform operator / SRE (S03, S04) | Person | Operates the platform |
| FinOps analyst (S07) | Person | Consumes usage and cost reports |
| Tenant applications | Software system (internal) | Call platform APIs with workload identity |
| Microsoft Entra ID | External system | Authenticates users and workloads (OIDC) **[Decision]** |
| Amazon Bedrock | External system | Managed model inference **[Proposed]** |
| Enterprise data sources | External system | Content for RAG ingestion (FR-052) |
| Operational systems | External system | Targets of MCP tools (UC-OA) |
| Telemetry / sensor sources | External system | Inputs for UC-PM |
| Enterprise SIEM | External system | Receives security events **[Assumption]** (SEC-Q9) |
| AWS billing (Cost and Usage Report) | External system | Source of infrastructure cost for attribution **[Proposed]** |

---

## 5. Container View (C2)

**Diagram:** `diagrams/02-enterprise-ai-architecture/c2-container-architecture.mmd`

All rows are **[Proposed]**. Implementation status for every row: **not built**.

| Plane | Container | Responsibility | Candidate technology | Phase 1 trace |
|---|---|---|---|---|
| Control | Developer portal and CLI | Self-service onboarding, projects, catalog, usage | Web app + CLI | FR-001–FR-004, FR-076, FR-077 |
| Control | Control-plane API | Tenants, projects, credentials, entitlements, quotas, catalog, policy, MCP registry, source registry | Containerized service on EKS | FR-002, FR-014, FR-024–FR-027, FR-046, FR-051 |
| Control | Approval service | Approval requests, decisions, timeouts | Service on EKS | FR-071, FR-072 |
| Control | Config distribution | Publishes versioned, signed config and policy bundles to the data plane | Service + S3 / object store | NFR-043, ADR-002 |
| Control | Control-plane database | Authoritative tenant, project, and config state | Amazon Aurora PostgreSQL **[Assumption]** | NFR-035 |
| Data | LLM gateway | Inference and embeddings APIs, authN/authZ, quotas, routing, metering | Custom service; LiteLLM is a *candidate* library or proxy (ADR-001) | FR-017–FR-031 |
| Data | Rate-limit store | Distributed counters for rate limits and quotas | Amazon ElastiCache (Redis-compatible) **[Assumption]** | FR-029, FR-030 |
| Data | Self-hosted model serving (optional) | Open-weight models | vLLM on EKS GPU nodes (ADR-004) | FR-020 |
| Data | Agent runtime | Executes agent graphs, checkpoints, approval interrupts | LangGraph workers on EKS; checkpoint store in PostgreSQL | FR-040–FR-045 |
| Data | MCP broker | Governed tool invocation, scope checks, credential minting | Service on EKS | FR-046–FR-050 |
| Data | Platform workflow engine | Long-running platform workflows: ingestion, re-sync, model promotion, approval timers | Temporal (self-hosted or Temporal Cloud) **[Open]** (ADR-005) | FR-056, FR-062, FR-071 |
| Data | RAG ingestion workers | Connectors, chunking, embedding (via gateway), ACL capture | Workers on EKS | FR-051–FR-054 |
| Data | Retrieval service | ACL-filtered retrieval with citations | Service on EKS | FR-055, FR-057 |
| Data | Vector / search store | Tenant indexes, k-NN and keyword search | Amazon OpenSearch Service | FR-054 |
| Data | MLOps services | Experiment tracking, model registry | MLflow on EKS with S3 artifacts **[Proposed]** | FR-059–FR-062 |
| Data | Training and model-serving workloads | Tenant training jobs, batch scoring, online endpoints | EKS jobs and deployments **[Proposed]** | FR-060, FR-063 |
| Shared | Usage pipeline | Durable usage events to the usage store | Stream or queue (Kinesis or SQS **[Open]**) → usage database | FR-031, NFR-005 |
| Shared | Observability pipeline | Traces, metrics, logs | OpenTelemetry collector → backend **[Open]** | FR-034, NFR-030 |
| Shared | Audit store | Append-only, tamper-evident audit records | S3 with Object Lock **[Assumption]** | FR-069, SEC-071 |
| Shared | Secrets and keys | Secrets and encryption keys | AWS Secrets Manager, AWS KMS | NFR-023, NFR-024 |

---

## 6. Deployment Topology

The topology below is **[Proposed]**:

- **Region:** One AWS region, with at least two Availability Zones (NFR-004). Multi-region DR is **[Open]** (NFR-Q3).
- **Accounts:** Separate AWS accounts for the platform control plane, the data plane, and audit/log archive. Restricted-tier tenants may get dedicated accounts **[Proposed]** (ADR-003).
- **EKS clusters:** One per environment (dev, staging, prod) for the pooled tier. Tenant namespaces sit inside each cluster. Node pools are separated for platform services, general tenant workloads, and GPU workloads.
- **Networking:** Private subnets only for workloads. Amazon Bedrock, S3, Secrets Manager, KMS, and OpenSearch are reached through VPC endpoints (SEC-043). Egress to the internet goes through an allowlisting proxy.

---

## 7. How the Architecture Serves the Workloads

| Workload | Path through containers | Key ADRs |
|---|---|---|
| **VS** | Portal/CLI → control-plane API (onboard) → tenant app → LLM gateway → Bedrock → usage pipeline + traces | 001, 002, 003, 004 |
| **UC-KA** | Ingestion workers (Temporal workflows) → gateway embeddings → OpenSearch; app → retrieval service (ACL filter) → gateway → Bedrock | 001, 003, 005 |
| **UC-OA** | App → agent runtime (LangGraph) → gateway (reasoning) and MCP broker (tools) → approval service (sensitive) → operational systems | 001, 002, 005 |
| **UC-PM** | Feature pipelines and training jobs on EKS → MLflow tracking and registry → promotion workflow → EKS serving; drift monitoring | 003, 005 |

---

## 8. Capacity Assumptions Used for Sizing

All figures come from Phase 1 and are **[Target]** or hypothetical.

- **Gateway:** sized for the 100-concurrent-request test target (KPI-09, NFR-013).
- **Hypothetical early load:** about 0.116 requests/s on average and about 12 concurrent at peak, from `success-metrics.md` §5.1 (hypothetical, not a forecast).
- **Bedrock:** per-account, per-region quotas apply. Quota headroom must be confirmed before launch **[Open]** (NFR-070).

---

## 9. Open Architecture Questions

| ID | Question | Related |
|---|---|---|
| AR-Q1 | Single region or multi-region DR; RTO/RPO values | NFR-Q2, NFR-Q3 |
| AR-Q2 | Policy engine for the embedded PDP (candidates: OPA/Rego, AWS Cedar) | FR-Q7, SEC-Q3 |
| AR-Q3 | Observability backend (candidates: Amazon Managed Prometheus/Grafana + X-Ray, CloudWatch, a third-party vendor) | NFR-030 |
| AR-Q4 | Temporal: self-hosted or Temporal Cloud; whether it is needed before UC-KA | ADR-005 |
| AR-Q5 | Usage pipeline: Kinesis or SQS | FR-031 |
| AR-Q6 | Which Bedrock models are approved, and in which regions | vision Q5, Q6 |
| AR-Q7 | Model-serving runtime for UC-PM (plain Deployments, KServe, or SageMaker) | FR-063 |
