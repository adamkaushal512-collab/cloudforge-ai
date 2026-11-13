# CloudForge AI: AI Platform Integrations

| Field | Value |
|---|---|
| Document | AI Platform Integration Boundaries |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. Not implemented. |
| ADR | `adr/005-ai-integration-boundaries.md` |

---

## 1. Purpose

This document defines what each integrated framework or service **owns**, what it **must not** do, and its interface to the rest of the platform. The aim is to avoid overlapping responsibilities and unclear ownership.

All technology names are **[Proposed]** candidates. **None is deployed.**

---

## 2. Boundary Summary

| Integration | Owns | Must not | Interfaces | Phase 1 trace |
|---|---|---|---|---|
| **LangGraph** (agent runtime) | Agent graph execution; reasoning loop; per-run state and checkpoints; human-approval interrupts | Call models directly (it must use the gateway); call tools directly (it must use the MCP broker); make authorization decisions | Gateway API; MCP broker API; approval service; PostgreSQL checkpointer | FR-040–FR-045, UC-OA |
| **Temporal** (platform workflow engine) | Long-running, retryable *platform* workflows: RAG ingestion and re-sync; model promotion pipelines; approval timeout timers; scheduled jobs | Own an agent run's reasoning state (LangGraph owns it); hold secrets in workflow history | Activities call platform services with workload identity | FR-056, FR-062, FR-071 |
| **MCP** (broker + registry) | The registry (control plane); brokered invocation, scope checks, approval enforcement, and credential minting (data plane) | Execute unregistered tools; expose credentials to agents | MCP protocol to tool servers; policy PDP; approval service | FR-046–FR-050, SEC-050–SEC-056 |
| **RAG / OpenSearch** | Ingestion workers: connectors, chunking, ACL capture. Embedding through the gateway. Index storage. The retrieval service: ACL filtering and citations. | Accept tenant-supplied index names or filters that bypass ACLs; return chunks without ACL evaluation | Gateway (embeddings); OpenSearch k-NN and keyword APIs; retrieval API | FR-051–FR-058, SEC-046 |
| **MLflow / MLOps** | Experiment tracking; model registry and lineage; promotion state | Serve as the authorization source; store raw training data | MLflow APIs (tenant-scoped via a proxy **[Open]**); S3 artifacts; Temporal promotion workflow; EKS serving | FR-059–FR-066 |
| **Identity** (Entra ID + AWS IAM) | Human and workload authentication (Entra); AWS resource access via IAM roles with session tags | Be bypassed by any component | OIDC; EKS Pod Identity / IRSA | FR-006–FR-011, SEC-010–SEC-014 |
| **Observability** (OpenTelemetry + backend) | Traces, metrics, logs; correlation by trace ID | Store prompt or response content without opt-in; fail requests when unavailable | OTel SDK / collector; backend **[Open]** | FR-034–FR-039, NFR-030–NFR-034 |
| **FinOps** | Usage store; cost estimation; attribution; budgets; reconciliation | Block requests itself (enforcement belongs to the gateway quota) | Usage events; AWS CUR with split cost allocation; reports API | FR-081–FR-085, NFR-045–NFR-049 |

---

## 3. LangGraph vs Temporal: One Owner per Run

The boundary rule is **[Proposed]**: *each execution has exactly one durable-state owner.*

| Execution type | Owner | Reason |
|---|---|---|
| Agent run (UC-OA), including approval pauses | LangGraph checkpoints | FR-042 places checkpointing in the agent runtime. Interrupt and resume is native to the graph model. |
| Approval request lifecycle (timeouts, notifications) | Approval service, with timers in Temporal **[Proposed]** | Durable timers outside the agent; the approval record is the source of truth |
| Ingestion and re-sync, model promotion, scheduled jobs | Temporal | Long-running, retry-heavy, multi-step platform processes |

**Consequence:** Temporal is **not required for the vertical slice** **[Assumption]**. It becomes necessary for UC-KA ingestion at the earliest.

**Alternative:**

- **Option:** Run agent runs as Temporal workflows that wrap LangGraph steps.
- **Status:** Recorded and not chosen (ADR-005).

---

## 4. Cross-Cutting Rules

1. **Gateway-only model access:** Every model call, including embeddings and agent reasoning, goes through the gateway. Egress policy blocks direct Bedrock access from tenant namespaces (SEC-043).
2. **Broker-only tool access:** Agents reach tools only through the MCP broker.
3. **Untrusted content:** Retrieved chunks, tool outputs, and model outputs are passed as delimited data (SEC-045). Model output never feeds into authorization (SEC-020).
4. **Tenant context everywhere:** `tenant_id`, `project_id`, and `trace_id` are propagated through every integration.
5. **Identity for every component:** Every integration runs under its own workload identity (SEC-014).

---

## 5. Integration Readiness

| Integration | Needed by | Status |
|---|---|---|
| Identity, gateway, observability, FinOps usage | VS | Proposed; not built |
| OpenSearch, ingestion, retrieval, Temporal | UC-KA | Proposed; not built |
| LangGraph runtime, MCP broker, approval service | UC-OA | Proposed; not built |
| MLflow, training and serving | UC-PM | Proposed; not built |

---

## 6. Open Questions

| ID | Question |
|---|---|
| AR-Q19 | How will MLflow be made multi-tenant: a separate instance per tenant, or a shared instance behind an authorization proxy? |
| AR-Q20 | Temporal: self-hosted on EKS, or Temporal Cloud? (data residency, operations) |
| AR-Q21 | Which LangGraph checkpointer backend, and with what retention? (FR-Q6) |
| AR-Q22 | Does OpenSearch k-NN meet UC-KA retrieval latency with ACL filters? (NFR-011, UC-KA-A2) |
