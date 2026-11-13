# CloudForge AI: Multi-Tenancy and Isolation

| Field | Value |
|---|---|
| Document | Multi-Tenancy and Isolation Architecture |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. Not implemented. |
| ADR | `adr/003-hybrid-tenant-isolation.md` |

---

## 1. Purpose

This document defines how tenants (teams) and projects are isolated across identity, data, compute, secrets, network, and cost attribution. It implements the Phase 1 isolation requirements: FR-012, FR-013, FR-016, NFR-017–NFR-021, and SEC-030–SEC-037.

**Nothing here is implemented or tested.** Labels are as in `architecture-overview.md` §1.1.

---

## 2. Isolation Tiers (Hybrid Model)

The tiers are **[Proposed]** (ADR-003).

| Tier | Intended for | Model |
|---|---|---|
| **Standard (pooled)** | The default for all tenants; data classifications up to a threshold **[Open]** (vision Q6) | Shared EKS cluster, shared gateway, shared OpenSearch domain. Isolation is logical: namespaces, IAM ABAC, per-tenant indexes, policy. |
| **Restricted (siloed resources)** | Tenants or projects handling higher classifications, or required by Security | Shared gateway and control plane, but dedicated node pools, a dedicated OpenSearch domain, per-tenant KMS keys, and optionally a dedicated AWS account |

**Tier assignment:**

- Security / IAM assigns the tier through policy (`stakeholders.md` C3).
- Moving a tenant from Standard to Restricted is a **sensitive operation** **[Assumption]**.

---

## 3. Isolation by Layer

### 3.1 Identity

All items are **[Proposed]**.

- **Humans:** Entra ID OIDC **[Decision]**. Platform tenant and role bindings map Entra groups to platform roles (FR-008, FR-009).
- **Tenant workloads calling the platform:** Entra ID workload identities, or project credentials (FR-Q2). Every token is validated for issuer, audience, expiry, and the project claim (SEC-012).
- **Platform and tenant workloads calling AWS:**
  - EKS Pod Identity or IRSA maps each service account to an IAM role.
  - Roles carry **session tags** (`tenant_id`, `project_id`, `tier`).
  - IAM policies use ABAC conditions on those tags for S3, Secrets Manager, and KMS.
- **Entra to AWS federation:** Platform services authorize on Entra-issued claims. AWS access is always through IAM roles bound to Kubernetes service accounts. **Tenants never hold AWS credentials directly.**

### 3.2 Data

| Store | Standard tier | Restricted tier | Enforcement |
|---|---|---|---|
| S3 (artifacts, documents, buffers) | Per-tenant prefixes | Per-tenant bucket, per-tenant KMS key | IAM ABAC on `tenant_id`; bucket policies |
| OpenSearch (RAG) | Index per tenant (and per project, **[Open]**) on a shared domain; fine-grained access control | Dedicated domain | Retrieval service injects the tenant index and ACL filter; no tenant-supplied index names |
| Control-plane DB | Row-level tenant column; tenant scoping in every query path | Same | Service-layer scoping plus automated cross-tenant tests (SEC-036) |
| Agent checkpoints | Tenant-scoped schema or key prefix | Dedicated schema **[Open]** | Agent runtime identity |
| Usage, traces, logs | Tagged by tenant; query APIs filter by tenant | Same | SEC-033, SEC-034 |
| Audit | Central append-only store; tenant-filtered views | Same | SEC-071 |

### 3.3 Compute

- **Namespaces:** One per tenant project, with ResourceQuota and LimitRange. Pod Security Standards are set to `restricted` (SEC-030).
- **Node pools:** Karpenter (candidate) node pools for platform, standard tenants, GPU, and restricted tenants. Restricted pools use taints and tolerations, and are not shared.
- **Priority classes:** interactive > batch > training (NFR-071).
- **Admission policy:** Rejects privileged pods, pods without resource requests, and images that are unsigned or unverified (SEC-081).

### 3.4 Secrets

- **Storage:** AWS Secrets Manager, with paths namespaced by tenant and project. Read by the External Secrets Operator (candidate) scoped to the tenant namespace.
- **Provider credentials:** Exist only in the gateway's namespace and IAM role. Bedrock is accessed through IAM, with no static keys (SEC-041).
- **MCP tool credentials:** Minted per invocation by the MCP broker, and never mounted into agent pods (SEC-053).

### 3.5 Network

- **Default deny:** Kubernetes NetworkPolicies deny traffic between tenant namespaces by default. Enforcement uses the VPC CNI network policy agent or Cilium **[Open]**.
- **Ingress:** Tenant pods may reach platform service endpoints only: gateway, retrieval, MCP broker, and MLflow.
- **AWS services:** Reached via VPC interface or gateway endpoints, with endpoint policies limiting access to the platform's accounts and resources.
- **Internet egress:** Denied by default. An allowlisting egress proxy handles approved destinations, including MCP target systems (SEC-043).

### 3.6 Cost Attribution

| Cost | Attribution mechanism | Granularity |
|---|---|---|
| Gateway tokens (Bedrock, vLLM) | Usage events with tenant, project, model, and tokens (FR-031); priced from the catalog (FR-081) | Per request |
| Bedrock invoices | Reconciled against usage records (NFR-045). Per-tenant Bedrock application inference profiles with cost-allocation tags are a candidate **[Assumption]**: verify feature fit. | Per tenant (if adopted) |
| EKS compute (CPU and GPU) | Kubernetes labels `tenant`/`project`, with AWS split cost allocation data for EKS **[Proposed]** | Per namespace / pod |
| OpenSearch | Pooled: allocated by index size and query count **[Open]**. Restricted: direct (dedicated domain). | Per tenant |
| S3, KMS, Secrets Manager | Tags / prefixes | Per tenant |
| Shared platform overhead | Reported separately; allocation **[Open]** (FR-Q11) | Platform |

---

## 4. Noisy-Neighbour Controls

These controls are **[Proposed]**:

- per-tenant and per-project rate and token limits in the gateway (FR-029, FR-030);
- per-tenant concurrency caps (NFR-018);
- partitioning of Bedrock quota by tenant allocation (NFR-021);
- Kubernetes quotas and priority classes (NFR-019, NFR-071).

**Verification:** The noisy-neighbour test (NFR-017) is planned. **It has not been run.**

---

## 5. Isolation Verification Plan

| Check | Method | Requirement | Status |
|---|---|---|---|
| Cross-tenant API access denied | Automated suite in CI | SEC-036, NFR-020 | Not started |
| Cross-namespace network denied | Network policy test pods | SEC-030 | Not started |
| IAM ABAC blocks cross-tenant S3 and Secrets | IAM policy simulation + integration tests | SEC-032 | Not started |
| OpenSearch cross-index queries impossible via the retrieval API | Negative tests | SEC-031 | Not started |
| Noisy neighbour | Load test | NFR-017 | Not started |

---

## 6. Open Questions

| ID | Question |
|---|---|
| AR-Q11 | What classification threshold triggers the Restricted tier? (vision Q6, SEC-Q6) |
| AR-Q12 | Is the OpenSearch index per tenant or per project? Index-count limits at about 20 tenants × projects need checking. |
| AR-Q13 | Do Restricted tenants need dedicated AWS accounts, or only dedicated resources? |
| AR-Q14 | Network policy enforcement: VPC CNI or Cilium? |
