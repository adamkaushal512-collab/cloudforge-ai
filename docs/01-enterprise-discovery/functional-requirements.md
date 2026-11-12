# CloudForge AI: Functional Requirements

| Field | Value |
|---|---|
| Document | Functional Requirements |
| Phase | 01: Enterprise Discovery |
| Status | Draft (not baselined, not approved) |
| Related | `platform-vision.md`, `stakeholders.md`, `use-cases.md`, `nonfunctional-requirements.md`, `security-governance.md`, `success-metrics.md`, `coverage-audit.md` |

---

## 1. Purpose and Disclaimer

This document states what CloudForge AI must do: its functional capabilities. The requirements are derived from three earlier documents:

- the platform vision;
- the stakeholder register;
- the three initial workloads and the first vertical slice.

How well the platform must perform is out of scope here. Availability, latency, scalability, and similar qualities are covered in `nonfunctional-requirements.md`.

> **Disclaimer:** CloudForge is a fictional enterprise. This document is a planning artifact.
>
> - **No stakeholder interviews have been conducted.**
> - **No production results exist.**
> - **No requirement has been approved or baselined.**
>
> Priorities and acceptance criteria are proposals for discovery review.

### 1.1 Labels

The labels are the same as in `platform-vision.md`, `stakeholders.md`, and `use-cases.md`:

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input, not as a measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal. It is not measured or committed. |
| **[Open]** | An unresolved question that needs an owner and a decision. |

**Default status of requirements:** Each requirement is a **proposal** unless labelled otherwise. Where a requirement restates an established decision, it is marked **[Decision]**. Priorities are **[Assumption]**: they are proposed, not agreed.

### 1.2 Conventions

- **"Shall"** marks a mandatory behavior of the requirement as written. Priority says how important the requirement is to the program.
- **Priority** follows MoSCoW, limited to the three levels used here:
  - **Must:** Required for the platform or for an initial workload to be viable.
  - **Should:** Important, but a workaround exists in the short term.
  - **Could:** Desirable; deferrable.
- **MVP:** "Yes" means the requirement is part of the first vertical slice (§5).
- **Phase** indicates the earliest workload that needs the requirement:
  - **VS:** first vertical slice
  - **KA:** knowledge assistant
  - **OA:** operations agent
  - **PM:** predictive maintenance
  - **Later:** after the initial workloads
- **References:**
  - G1–G6, A1–A8, R1–R8, Q1–Q10 are defined in `platform-vision.md`.
  - S01–S09, AC-01 to AC-14, C1–C9, D1–D9, SQ1–SQ11 are defined in `stakeholders.md`.
  - VS-ACn and UC-xx-ACn are defined in `use-cases.md`.

### 1.3 Terminology

| Term | Meaning in this document |
|---|---|
| **Tenant** | An application team: the unit of isolation, ownership, and cost attribution. Tenants are internal teams only (vision A6, **[Assumption]**). |
| **Project** | A workspace within a tenant, such as one application or environment. It owns credentials, quotas, and resources. |
| **Principal** | An authenticated human user or workload (service) identity. |
| **Sensitive operation** | An action requiring human approval **[Decision]**. Its exact definition is **[Open]** (SQ3). |
| **Platform admin** | A platform team member who operates shared services. |

### 1.4 Identity Provider Note

The requirements brief for this document specifies **Microsoft Entra ID over OIDC with RBAC**. This document treats that as **[Decision]**.

`stakeholders.md` SQ4 still records the identity provider as **[Open]**. That question should be updated to reflect this decision in a later revision. No other document has been changed.

---

## 2. Functional Scope Boundaries

### 2.1 In Scope

- The fourteen capability areas in §4, provided as **shared platform services** owned by the platform team **[Decision]**.
- APIs, SDKs, CLI, and tooling that application teams use to consume those services.
- The administrative functions that platform, Security, and FinOps roles need to operate and govern the services.

### 2.2 Ownership Boundary

The boundary below is **[Decision]**, with service-level detail in `stakeholders.md` §3.

| The platform shall provide… | The application team remains responsible for… |
|---|---|
| Gateway, routing, quotas, policy enforcement | Prompts, model selection within the approved catalog, response handling |
| Agent runtime, checkpointing, approval hooks | Agent graph design, task logic, outcome quality |
| MCP hosting, registry, governed invocation | Domain MCP servers they build and their correctness **[Assumption]** |
| RAG ingestion, indexing, ACL-filtered retrieval | Corpus selection, retrieval tuning, answer quality |
| MLOps infrastructure, registry, monitoring framework | Features, models, evaluation criteria, drift thresholds |
| Identity integration, tenant and role model | Assigning members to roles; end-user authorization inside their app |
| Metering, attribution, budget tooling | Staying within budget |

### 2.3 Out of Scope

These items are **[Assumption]** unless marked otherwise:

| Item | Reason |
|---|---|
| Application-specific business logic, prompts, and UIs | Owned by application teams **[Decision]** |
| Training or pretraining foundation models | The platform consumes models (vision §5.2) |
| External (non-CloudForge) tenants, public signup, billing of external customers | Tenants are internal (vision A6) |
| Automated migration of every existing team stack | Not in the first phase (vision §5.2); **[Open]** migration approach (vision Q8) |
| A general-purpose data platform or data lake | The platform consumes governed data sources; it does not replace data engineering |
| End-user chat UI for the knowledge assistant | Owned by the application team (UC-KA) |
| Downstream maintenance-scheduling systems | Owned by the PM application team (UC-PM) |
| Fine-tuning service for LLMs | Not required by the initial workloads; candidate for later **[Open]** |
| Multi-region active-active deployment | A nonfunctional/architecture concern; deferred to `nonfunctional-requirements.md` |

---

## 3. User Stories for Key Personas

The stories are **[Assumption]**: they are derived from the stakeholder register and use cases, not from interviews.

| ID | Persona | Story | Related FRs |
|---|---|---|---|
| US-01 | AI developer (S01) | As an AI developer, I want to onboard my team and make my first model call without filing a ticket, so I can start building within minutes. | FR-001–FR-004, FR-017, FR-079 |
| US-02 | AI developer (S01) | As an AI developer, I want one API for all approved models, so I don't integrate each provider myself. | FR-017, FR-020, FR-024 |
| US-03 | AI developer (S01) | As an AI developer, I want to see traces and usage for my project, so I can debug and control cost. | FR-034, FR-035, FR-037 |
| US-04 | AI developer (S01, UC-KA) | As an assistant developer, I want ACL-filtered retrieval with citations, so my app never exposes documents a user can't read. | FR-052–FR-057, FR-011 |
| US-05 | AI developer (S01, UC-OA) | As an agent developer, I want approval gates and scoped tools as platform features, so I don't build my own safety machinery. | FR-040–FR-050, FR-071 |
| US-06 | ML engineer (S02, UC-PM) | As an ML engineer, I want to train, register, deploy, and monitor a model through one standard pipeline, so I don't maintain a bespoke MLOps stack. | FR-059–FR-066 |
| US-07 | Security / IAM (S05) | As a security engineer, I want every action tied to an Entra ID identity and recorded in a tamper-evident audit log, so I can investigate and assure compliance. | FR-006–FR-010, FR-068, FR-069 |
| US-08 | Security / IAM (S05) | As an approver, I want to see an action's parameters, evidence, and trace before approving it, so I make informed decisions. | FR-071, FR-072 |
| US-09 | Data engineer / data owner (S06) | As a data owner, I want to approve which sources are ingested and have their permissions enforced, so my data isn't overexposed. | FR-052, FR-053, FR-055, FR-056 |
| US-10 | FinOps (S07) | As a FinOps analyst, I want all model and compute usage attributed to tenants and projects, so I can report and govern spend. | FR-031, FR-081–FR-085 |
| US-11 | SRE (S04) | As an SRE, I want errors classified as platform, provider, or tenant, so I can route incidents correctly. | FR-038, FR-034 |
| US-12 | Platform admin (S03) | As a platform admin, I want to add or disable providers, models, and MCP tools centrally, so governance changes take effect immediately. | FR-025, FR-027, FR-050, FR-044 |

---

## 4. Functional Requirements

### 4.1 Developer Self-Service Onboarding and Project Creation

#### FR-001: Self-service tenant registration
- **Requirement:** The platform shall allow an authenticated user to register a new tenant (team) through self-service tooling, without manual platform team intervention for the default access tier.
- **Rationale:** Self-service access is required **[Decision]**. Removing ticket queues supports G2 and the onboarding target.
- **Trace:** S01, S03; AC-01; VS step 1, VS-AC1; G2; C1
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. An authenticated user can create a tenant with a name, an owning group, and a cost centre, with no platform team action.
  2. The creating user is assigned the tenant admin role.
  3. Tenant creation is audit logged (FR-068).
- **Dependencies / assumptions:** FR-006, FR-008. Security accepts an auto-provisioned default tier (SA3, VS-A2) **[Assumption]**. **[Open]** Who may create tenants: any employee, or only members of designated groups?

#### FR-002: Project creation within a tenant
- **Requirement:** The platform shall allow tenant admins and developers to create projects within their tenant. Each project has its own credentials, quotas, and resources.
- **Rationale:** Projects separate applications and environments within one team, and enable finer attribution.
- **Trace:** S01, S07; VS step 1; G4
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. A project can be created with a name and an environment label, such as dev or prod.
  2. Resources, credentials, and usage are scoped to the project and the tenant.
  3. Projects in one tenant are not visible to other tenants.
- **Dependencies / assumptions:** FR-012. **[Open]** Is environment a project attribute, or a separate construct?

#### FR-003: Scoped credential issuance
- **Requirement:** The platform shall issue project-scoped credentials for programmatic access, limited to that project's entitlements, with a configurable expiry.
- **Rationale:** Developers need working credentials immediately. Least privilege requires them to be scoped and expiring **[Decision]**.
- **Trace:** S01, S05; VS-AC1, VS-AC4; AC-07
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. A project member can generate a credential that works only for that project.
  2. A credential is rejected after expiry or revocation.
  3. The secret value is shown once and never retrievable afterwards.
  4. Issuance and revocation are audit logged.
- **Dependencies / assumptions:** FR-007, FR-010. **[Open]** Should static API keys be allowed, or only OIDC workload identities? (FR-Q2)

#### FR-004: Guided first request
- **Requirement:** The platform shall provide a guided onboarding flow ending in a verified first successful gateway request, and shall record the onboarding start and completion events.
- **Rationale:** The flow enables the onboarding-time target, under 30 minutes **[Target]**, and makes it measurable.
- **Trace:** S01; AC-01; VS-AC2; vision Q10
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. The flow produces a runnable sample request using the user's new credential.
  2. Start and end timestamps are recorded per tenant.
  3. The time to first successful request is reportable.
- **Dependencies / assumptions:** FR-017, FR-079. **[Open]** Exact start and end event definitions (vision Q10).

#### FR-005: Tenant and project offboarding
- **Requirement:** The platform shall allow tenant admins to deactivate projects and tenants, revoking all credentials and stopping metering, while retaining audit and usage records per retention policy.
- **Rationale:** Prevents orphaned credentials and spend; supports least privilege.
- **Trace:** S05, S07; AC-07
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. After deactivation, all project credentials are rejected.
  2. Audit and usage history remain available to authorized roles.
- **Dependencies / assumptions:** FR-069. **[Open]** Retention periods.

### 4.2 Enterprise Authentication and Authorization

#### FR-006: Human authentication via Entra ID (OIDC)
- **Requirement:** The platform shall authenticate human users through Microsoft Entra ID using OpenID Connect for all portal, CLI, and API access.
- **Rationale:** Enterprise identity is a prerequisite for least privilege and audit **[Decision]**, per §1.4.
- **Trace:** S05; AC-07; VS step 2; D1; G3
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Users sign in with Entra ID; no local platform passwords exist.
  2. Disabled Entra ID accounts lose access within the token lifetime.
  3. Failed authentications are logged.
- **Dependencies / assumptions:** An Entra ID app registration and tenant configuration are available (D1) **[Assumption]**. **[Open]** Whether MFA and conditional access are enforced by Entra policy or also by the platform.

#### FR-007: Workload authentication
- **Requirement:** The platform shall authenticate non-human callers using OIDC-based workload identities, such as Entra ID service principals or Kubernetes workload identity federation, and/or project-scoped credentials (FR-003).
- **Rationale:** Applications, agents, and pipelines call the platform without a human present.
- **Trace:** S01, S05; AC-07; VS-AC3
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. A registered workload identity can obtain access to its project only.
  2. Requests without a valid identity are rejected with an authentication error and logged.
- **Dependencies / assumptions:** FR-006. **[Open]** FR-Q2.

#### FR-008: Role-based access control
- **Requirement:** The platform shall enforce RBAC with, at minimum, these roles, each scoped to a tenant or project unless platform-wide:
  - platform admin;
  - security admin;
  - tenant admin;
  - developer;
  - viewer;
  - approver;
  - FinOps analyst;
  - auditor.
- **Rationale:** Least privilege **[Decision]**; distinct duties for approval and audit.
- **Trace:** S05; AC-07; stakeholders §4
- **Priority:** Must · **MVP:** Yes (platform admin, tenant admin, developer, viewer) · **Phase:** VS (remaining roles by OA)
- **Acceptance criteria:**
  1. Each API operation maps to a required permission.
  2. A viewer cannot create credentials or modify resources.
  3. A developer in Tenant A has no permissions in Tenant B.
  4. Role assignments and changes are audit logged.
- **Dependencies / assumptions:** The role set is **[Assumption]**, pending Security review.

#### FR-009: Group-based role assignment
- **Requirement:** The platform shall support binding roles to Entra ID groups, so that membership changes in Entra ID are reflected in platform access.
- **Rationale:** Reduces manual access administration; keeps access aligned with the organizational source of truth.
- **Trace:** S05, S03
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Removing a user from a bound group removes their platform permissions within a defined period. **[Open]** Sync interval.
- **Dependencies / assumptions:** Entra ID group claims or Graph API access **[Assumption]**.

#### FR-010: Deny-by-default authorization enforcement
- **Requirement:** The platform shall authorize every API request against the caller's tenant, project, and role, and shall deny any request not explicitly permitted.
- **Rationale:** Least privilege and tenant isolation **[Decision]**.
- **Trace:** S05; AC-07, AC-08; VS-AC3, VS-AC4
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Automated negative tests confirm that unauthorized operations return an authorization error for every public API.
  2. Denials are logged with the principal and the requested resource.
- **Dependencies / assumptions:** FR-008.

#### FR-011: End-user identity propagation
- **Requirement:** The platform shall accept and validate end-user identity forwarded by an application, using a delegated (on-behalf-of) or equivalent mechanism, so that downstream services can authorize against the end user, not only the application.
- **Rationale:** Document-level access control in RAG must evaluate the end user's permissions **[Decision]** (UC-KA). The agent must not exceed the initiating user's privileges (UC-OA).
- **Trace:** S05, S06; AC-11; UC-KA-AC1; UC-OA §5.5
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Retrieval and tool calls made on behalf of a user carry a verifiable user identity.
  2. A forged or missing user identity results in denial (fail closed).
- **Dependencies / assumptions:** Entra ID on-behalf-of flow, or equivalent, is permitted **[Assumption]**.

### 4.3 Multi-Tenant Isolation and Project Management

#### FR-012: Tenant scoping of all resources
- **Requirement:** The platform shall associate every resource with exactly one owning tenant and project. Resources include credentials, quotas, traces, usage records, indexes, agents, MCP registrations, models, and endpoints.
- **Rationale:** Multi-tenant by default (vision §3.3); basis for isolation and attribution.
- **Trace:** S05, S07; AC-08, AC-12; G3, G4
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. No resource can be created without a tenant and project.
  2. Listing APIs return only resources in tenants the caller can access.
- **Dependencies / assumptions:** FR-002.

#### FR-013: Cross-tenant access prevention
- **Requirement:** The platform shall prevent any principal from reading, modifying, or invoking another tenant's resources, unless they were explicitly shared through FR-015 or the principal holds a platform-wide role.
- **Rationale:** A tenant isolation failure is a top risk (vision R3).
- **Trace:** S05; AC-08; VS-AC4, UC-KA-AC1, UC-OA-AC2, UC-PM-AC5
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. An automated cross-tenant test suite attempts access to every resource type using another tenant's credentials, and all attempts are denied.
  2. Platform-wide role access to tenant data is audit logged.
- **Dependencies / assumptions:** FR-010, FR-012.

#### FR-014: Project membership and settings management
- **Requirement:** The platform shall allow tenant admins to manage project members, roles, entitled models, quotas (within tenant limits), and settings.
- **Rationale:** Self-service administration without platform team tickets (vision §3.3).
- **Trace:** S01, S03
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. A tenant admin can add and remove members and change their roles.
  2. A tenant admin cannot raise project quotas above the tenant limit.
- **Dependencies / assumptions:** FR-008, FR-030.

#### FR-015: Explicit cross-tenant sharing
- **Requirement:** The platform shall allow a resource owner to share specific resources with named tenants, subject to policy. Shareable resources include MCP servers and RAG indexes.
- **Rationale:** Some resources, such as shared operational MCP tools, may serve several teams (stakeholders §3 grey areas).
- **Trace:** S01, S05; UC-OA §5.5
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. Shared access is visible to both tenants and revocable by the owner.
  2. Every share and every use of a share is audit logged.
- **Dependencies / assumptions:** **[Open]** Which resource types are shareable, and whether sharing requires Security approval.

#### FR-016: Compute isolation for tenant workloads
- **Requirement:** The platform shall run tenant-deployed workloads in isolated compute boundaries with per-tenant resource quotas. Tenant workloads include agent runtimes, MCP servers, training jobs, and model endpoints.
- **Rationale:** Tenant isolation **[Decision]**; noisy-neighbour control.
- **Trace:** S04, S05; AC-08; UC-PM §6.5
- **Priority:** Must · **MVP:** No · **Phase:** OA / PM
- **Acceptance criteria:**
  1. Tenant workloads cannot reach another tenant's workloads or storage by default.
  2. Exceeding a resource quota prevents scheduling, rather than starving other tenants.
- **Dependencies / assumptions:** Kubernetes namespace-based isolation is sufficient for initial data classifications (vision A5, C3) **[Assumption]**.

### 4.4 LLM Gateway APIs and Model Routing

#### FR-017: Unified inference API
- **Requirement:** The platform shall expose a single, provider-agnostic API for chat and completion inference across all approved models.
- **Rationale:** Removes duplicated gateway implementations (G1); one API for many models (S01 need).
- **Trace:** S01; AC-02; VS step 3; UC-KA-AC5; G1, G2
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. The same request schema works across at least two approved models from different providers (or deployments).
  2. Responses include token counts and the trace ID.
- **Dependencies / assumptions:** At least one approved provider or self-hosted model (vision A7) **[Assumption]**. **[Open]** Whether to adopt an existing de facto API schema for compatibility (FR-Q3).

#### FR-018: Embeddings API
- **Requirement:** The platform shall expose an embeddings API through the gateway, with the same authentication, policy, metering, and tracing as inference.
- **Rationale:** UC-KA ingestion and retrieval require embeddings.
- **Trace:** UC-KA §4.2; AC-02
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Embedding requests are authenticated, metered, and traced like inference requests.
- **Dependencies / assumptions:** FR-017.

#### FR-019: Streaming responses
- **Requirement:** The platform shall support streamed inference responses where the underlying model supports streaming.
- **Rationale:** Interactive use cases (UC-KA) need incremental output.
- **Trace:** S01; UC-KA
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. A streaming request returns incremental chunks.
  2. Usage is still recorded accurately when the stream completes or is interrupted.
- **Dependencies / assumptions:** FR-031.

#### FR-020: Model routing by logical alias
- **Requirement:** The platform shall route each request to a provider deployment based on a logical model identifier from the catalog, independent of provider-specific endpoints.
- **Rationale:** Decouples applications from providers; mitigates provider changes (vision R7).
- **Trace:** S01, S08; G1; R7
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Changing a model alias's target deployment requires no application change.
  2. Requests for unknown aliases are rejected.
- **Dependencies / assumptions:** FR-024.

#### FR-021: Failover routing
- **Requirement:** The platform shall support configurable failover from a primary deployment to one or more approved alternates, when the primary is unavailable or returns retryable errors.
- **Rationale:** Mitigates the gateway as a single point of failure and provider outages (vision R2, C4). Supports the 99.9% availability **[Target]**.
- **Trace:** S04; AC-05; UC-KA §4.6
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. With the primary deployment made unavailable in test, requests succeed via the configured alternate.
  2. The trace records which deployment served the request.
- **Dependencies / assumptions:** More than one approved deployment exists. Failover never routes to a model the tenant isn't entitled to (FR-026).

#### FR-022: Pre-routing policy enforcement
- **Requirement:** Before forwarding a request, the gateway shall enforce:
  - authentication;
  - tenant model entitlement;
  - quota and rate limits;
  - request size limits;
  - applicable security policies (FR-067).
- **Rationale:** The gateway is the central control point (C4); requests for non-approved models must be rejected.
- **Trace:** S05; VS-AC3; AC-07
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Requests violating any check are rejected with a distinct, documented error code, and are logged.
  2. No rejected request reaches a provider.
- **Dependencies / assumptions:** FR-010, FR-026, FR-029, FR-030.

#### FR-023: Provider credential isolation
- **Requirement:** The platform shall hold provider credentials centrally and shall never expose them to tenants, clients, or traces.
- **Rationale:** Prevents credential sprawl (S05 pain point); enables central governance.
- **Trace:** S05; AC-07, AC-08
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. No API, log, or trace returns provider credential material.
  2. Provider credentials are stored in a secrets manager and rotated without tenant impact.
- **Dependencies / assumptions:** A secrets management service **[Assumption]**.

### 4.5 Model Catalog and Provider Management

#### FR-024: Model catalog
- **Requirement:** The platform shall maintain a catalog of models available through the gateway. Each entry records:
  - the logical ID;
  - the provider and deployment;
  - capabilities (chat, embeddings, streaming);
  - context limits;
  - pricing reference;
  - approved data classifications;
  - lifecycle state.
- **Rationale:** Gives developers discoverable approved options; gives Security a governed list (C2).
- **Trace:** S01, S05, S07; AC-02; vision Q5
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Developers can list models they are entitled to via the API, CLI, or portal.
  2. Each entry shows its lifecycle state and permitted data classifications.
- **Dependencies / assumptions:** **[Open]** The approved providers (vision Q5) and data classifications (vision Q6).

#### FR-025: Model approval lifecycle
- **Requirement:** The platform shall manage the model lifecycle states proposed → approved → deprecated → retired. Only security admins may approve models, and only approved models are routable.
- **Rationale:** An approved model and provider list owned by Security (stakeholders RACI row 9).
- **Trace:** S05, S08; C2; AC-07
- **Priority:** Must · **MVP:** Yes (approved/retired only) · **Phase:** VS (full lifecycle by KA)
- **Acceptance criteria:**
  1. A model in the proposed or retired state cannot receive traffic.
  2. State transitions record the actor and the reason in the audit log.
- **Dependencies / assumptions:** FR-008, FR-068. **[Open]** Fast-track review process (C2).

#### FR-026: Tenant model entitlements
- **Requirement:** The platform shall allow entitlement of specific approved models to specific tenants or projects. The default entitlement set applies at onboarding.
- **Rationale:** Supports tiered access (C1) and data-classification restrictions.
- **Trace:** S05, S01; C1
- **Priority:** Should · **MVP:** Yes (default set only) · **Phase:** VS
- **Acceptance criteria:**
  1. A project can call only entitled models.
  2. Entitlement changes take effect without redeploying applications.
- **Dependencies / assumptions:** FR-024. **[Open]** Who grants non-default entitlements.

#### FR-027: Provider management
- **Requirement:** The platform shall allow platform admins to register, configure, health-check, and disable model providers and deployments.
- **Rationale:** Central provider governance; rapid response to provider incidents (R7).
- **Trace:** S03, S04
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Disabling a deployment stops traffic to it within a defined period.
  2. Health status is visible to platform admins.
- **Dependencies / assumptions:** FR-023.

#### FR-028: Deprecation notification
- **Requirement:** The platform shall notify affected tenants when a model they use is deprecated, including the retirement date and the recommended replacement.
- **Rationale:** Avoids breaking applications when providers retire models (R7).
- **Trace:** S01; R7
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Tenants with recent usage of a deprecated model receive a notification.
  2. The catalog shows the retirement date.
- **Dependencies / assumptions:** FR-031 (usage data identifies affected tenants).

### 4.6 Rate Limits, Quotas, and Tenant Usage Metering

#### FR-029: Rate limiting
- **Requirement:** The platform shall enforce configurable request-rate and token-rate limits per project and per tenant.
- **Rationale:** Protects shared capacity and provider limits; contains runaway clients (C4).
- **Trace:** S04, S07; VS-AC3
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Requests exceeding a limit receive a rate-limit error with retry guidance.
  2. One project exceeding its limit does not affect other projects' accepted requests.
- **Dependencies / assumptions:** Default limit values **[Open]**.

#### FR-030: Token quotas
- **Requirement:** The platform shall enforce token quotas per project and tenant over a configurable period.
- **Rationale:** Cost governance (S07); prevents unbounded spend.
- **Trace:** S07; UC-KA §4.6
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Requests that would exceed an exhausted quota are rejected with a quota error.
  2. Quota consumption is visible to the tenant.
- **Dependencies / assumptions:** FR-031. **[Open]** Hard versus soft enforcement defaults (C7).

#### FR-031: Per-request usage metering
- **Requirement:** The platform shall record a usage record for every gateway request, successful or failed, containing:
  - tenant, project, and principal;
  - model and deployment;
  - input and output tokens;
  - status;
  - timestamp;
  - trace ID.
- **Rationale:** Basis for attribution, quotas, and reporting **[Decision]** (VS step 5).
- **Trace:** S07; AC-12; VS-AC5; G4
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Reconciliation of gateway request logs to usage records for a test period shows that every request has exactly one usage record.
  2. Usage records are tenant-scoped (FR-013).
- **Dependencies / assumptions:** FR-034.

#### FR-032: Quota increase requests
- **Requirement:** The platform shall allow tenant admins to request quota increases through self-service, routed to the designated approver.
- **Rationale:** Avoids ad-hoc tickets; keeps an audit trail of approvals.
- **Trace:** S01, S07
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. Requests and decisions are recorded.
  2. Approved increases apply automatically.
- **Dependencies / assumptions:** FR-071.

#### FR-033: Quota threshold notifications
- **Requirement:** The platform shall notify tenant admins when usage crosses configurable thresholds of quota, such as 80% and 100%.
- **Rationale:** Prevents surprise rejections (UC-KA §4.6).
- **Trace:** S01, S07
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Crossing a configured threshold produces a notification to tenant admins.
- **Dependencies / assumptions:** FR-030. Threshold defaults **[Open]**.

### 4.7 Request Tracing, Logs, and Usage Reporting

#### FR-034: Trace ID generation and propagation
- **Requirement:** The platform shall assign a trace ID to every request entering a platform service, accept caller-supplied trace context, and propagate it across gateway, retrieval, agent, and tool calls.
- **Rationale:** End-to-end observability (vision §3.3); incident attribution (AC-06).
- **Trace:** S04; AC-06; VS-AC5; UC-KA-AC4; UC-OA-AC7
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Every response includes the trace ID.
  2. In UC-OA, all LLM, tool, and approval steps of a run share one trace ID.
- **Dependencies / assumptions:** Use of an open tracing standard such as OpenTelemetry **[Assumption]**.

#### FR-035: Tenant-scoped trace records
- **Requirement:** The platform shall store trace records containing timing, status, model, deployment, token counts, and error details, and shall make them visible only to the owning tenant and authorized platform roles.
- **Rationale:** Developers debug their own workloads (US-03); isolation (AC-08).
- **Trace:** S01, S04, S05; VS-AC4, VS-AC5
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. A tenant can query its traces by trace ID and time range.
  2. Another tenant's query returns no results.
- **Dependencies / assumptions:** FR-013. **[Open]** Trace retention period.

#### FR-036: Opt-in content capture with redaction
- **Requirement:** The platform shall store prompt and response content in traces only when the tenant opts in and policy permits. When stored, content is redacted per configured rules and governed by a retention limit.
- **Rationale:** Balances debugging with privacy (C6).
- **Trace:** S04, S05, S06; C6; SQ8
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. By default, traces contain metadata only.
  2. With opt-in enabled, content appears redacted per the configured rules.
  3. Content is deleted after the retention limit.
- **Dependencies / assumptions:** **[Open]** Whether content capture is permitted at all (SQ8, UC-Q4).

#### FR-037: Usage reporting
- **Requirement:** The platform shall provide usage reports per tenant and project, by model, time period, and principal, through an API and a user interface.
- **Rationale:** Usage and trace reporting is the final step of the vertical slice **[Decision]**.
- **Trace:** S01, S07, S09; AC-12, AC-14; VS step 5
- **Priority:** Must · **MVP:** Yes (API, plus CLI or minimal UI) · **Phase:** VS
- **Acceptance criteria:**
  1. Report totals match the underlying usage records for the selected period.
  2. Tenants see only their own usage.
- **Dependencies / assumptions:** FR-031. **[Open]** Report latency, for example near real time or daily.

#### FR-038: Error classification
- **Requirement:** The platform shall classify failed requests as platform, provider, or tenant (client) errors in traces and metrics.
- **Rationale:** Distinguishing platform incidents from tenant and provider incidents (AC-06); availability measurement (vision Q3).
- **Trace:** S04; AC-05, AC-06
- **Priority:** Should · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Each failed request carries exactly one error class.
  2. Classification rules are documented.
- **Dependencies / assumptions:** The availability definition (vision Q3) depends on this.

#### FR-039: Telemetry export
- **Requirement:** The platform shall allow tenants to export their traces and metrics to approved observability tools via a standard protocol.
- **Rationale:** Teams may keep existing dashboards (S01, S04).
- **Trace:** S04
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. An export configured for a tenant includes only that tenant's telemetry.
- **Dependencies / assumptions:** FR-034.

### 4.8 Agent Orchestration and Execution Lifecycle

#### FR-040: Agent definition and deployment
- **Requirement:** The platform shall allow tenants to define agents as stateful graphs of steps, such as LLM calls, tool calls, conditional branches, and human-approval interrupts, and to deploy versioned agent definitions to the platform runtime.
- **Rationale:** LangGraph-style orchestration is required by UC-OA **[Decision]**. The framework choice is **[Open]** (UC-OA-Q4).
- **Trace:** S01; UC-OA §5.3; G6
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A versioned agent definition can be deployed and invoked by an authorized principal.
  2. Previous versions remain available for rollback.
- **Dependencies / assumptions:** FR-016, FR-017.

#### FR-041: Run lifecycle management
- **Requirement:** The platform shall manage agent runs through defined states: created, running, awaiting approval, completed, failed, cancelled, and expired. It shall expose each run's state and history to authorized principals.
- **Rationale:** Operators and approvers need visibility; runs must be resumable and terminable.
- **Trace:** S01, S04; UC-OA-AC4
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. Each run reports its current state.
  2. Every state transition is recorded with a timestamp and cause.
- **Dependencies / assumptions:** FR-042.

#### FR-042: Checkpointing and resume
- **Requirement:** The platform shall persist agent run state at each step, and shall resume a run from its last checkpoint after an approval decision or a recoverable failure.
- **Rationale:** Approval pauses and LLM outages must not lose work (UC-OA §5.6).
- **Trace:** UC-OA-AC4; UC-OA §5.6
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A run paused for approval resumes from the same step after approval, without repeating completed tool calls.
  2. A run interrupted by a simulated runtime restart resumes from its checkpoint.
- **Dependencies / assumptions:** Durable state store **[Assumption]**.

#### FR-043: Run limits
- **Requirement:** The platform shall enforce configurable per-run limits on steps, tokens, tool calls, and wall-clock time, and shall terminate runs exceeding any limit.
- **Rationale:** Prevents loops and runaway cost (UC-OA §5.6).
- **Trace:** S07; UC-OA-AC5
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A test agent designed to loop is terminated at the configured limit.
  2. The termination reason is recorded.
- **Dependencies / assumptions:** Default limits **[Open]**.

#### FR-044: Run cancellation and agent disablement
- **Requirement:** The platform shall allow authorized principals to cancel individual runs. It shall allow platform or security admins to disable an agent immediately, which prevents new runs and cancels active ones.
- **Rationale:** Kill switch (UC-OA §5.5).
- **Trace:** S05; UC-OA-AC6
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. After disablement, new invocations are rejected and active runs move to cancelled within a defined period.
  2. The action is audit logged.
- **Dependencies / assumptions:** FR-068.

#### FR-045: Run triggers
- **Requirement:** The platform shall support agent runs initiated by an authenticated user request. It shall support runs initiated by events or alerts only where policy explicitly permits.
- **Rationale:** UC-OA triggers include operator requests and alerts. Autonomous triggering is **[Open]** (UC-OA-Q3).
- **Trace:** UC-OA §5.2
- **Priority:** Must (user-initiated) / Could (event-initiated) · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. User-initiated runs record the initiating user.
  2. Event-initiated runs are rejected unless enabled by policy for that agent.
- **Dependencies / assumptions:** FR-067.

### 4.9 MCP Server Registry and Governed Tool Access

#### FR-046: MCP server registry
- **Requirement:** The platform shall maintain a registry of MCP servers. Each entry records:
  - owner tenant;
  - version;
  - endpoint or hosted deployment;
  - exposed tools;
  - each tool's classification.
- **Rationale:** Governed, discoverable tool integrations replace per-team MCP duplication (vision §2.1).
- **Trace:** S01, S05; UC-OA §5.3; G1
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A tenant can register an MCP server and list registered servers it can access.
  2. Unregistered servers cannot be invoked through the platform.
- **Dependencies / assumptions:** **[Open]** Who owns shared MCP servers (UC-OA-Q5).

#### FR-047: Tool classification and scopes
- **Requirement:** The platform shall require each registered tool to carry:
  - an access classification of read, write, or sensitive;
  - the authorization scope(s) required to invoke it.
- **Rationale:** Scoped authorization and approval of sensitive operations **[Decision]**.
- **Trace:** S05; UC-OA-AC1, UC-OA-AC2; SQ3
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. Registration fails without a classification and scope.
  2. Only security admins can downgrade a tool's classification.
- **Dependencies / assumptions:** **[Open]** The definition of "sensitive" (SQ3).

#### FR-048: Governed tool invocation
- **Requirement:** The platform shall broker every agent-to-tool invocation. For each one, it shall verify:
  - the agent's identity;
  - the tenant;
  - the granted scopes;
  - the initiating user's permissions (FR-011).

  It shall route sensitive tools through the approval workflow (FR-071) before execution.
- **Rationale:** Central enforcement prevents unscoped tool access.
- **Trace:** S05; UC-OA-AC1, UC-OA-AC2; AC-07, AC-10
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. An out-of-scope tool call is denied and logged.
  2. A sensitive tool call without a recorded approval never executes (negative test).
- **Dependencies / assumptions:** FR-047, FR-071.

#### FR-049: Short-lived tool credentials
- **Requirement:** The platform shall execute tool calls using short-lived credentials scoped to the specific invocation, or to the narrowest available scope.
- **Rationale:** Least privilege; limits the blast radius of compromised agents (UC-OA §5.5).
- **Trace:** S05; AC-07
- **Priority:** Should · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. Credentials used for a tool call expire within a defined period and cannot be retrieved by agent code.
- **Dependencies / assumptions:** Target systems support short-lived or delegated credentials (UC-OA-A1) **[Assumption]**.

#### FR-050: Tool and server disablement
- **Requirement:** The platform shall allow security and platform admins, and the owning tenant admin, to disable an MCP server or an individual tool immediately.
- **Rationale:** Kill switch for compromised or faulty tools.
- **Trace:** S05; UC-OA-AC6
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. Calls to a disabled tool are rejected within a defined period.
  2. Disablement is audit logged.
- **Dependencies / assumptions:** FR-068.

### 4.10 RAG Ingestion, Indexing, Retrieval, and Document-Level Access Control

#### FR-051: Governed source registration
- **Requirement:** The platform shall ingest content only from sources that are registered with an owner, a data classification, and a recorded data-owner approval.
- **Rationale:** Prevents uncontrolled copies of data (S06 pain point).
- **Trace:** S06, S05; D4; UC-KA §4.2
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Ingestion from a source without a recorded approval is blocked.
  2. Source registration is audit logged.
- **Dependencies / assumptions:** **[Open]** Permitted classifications (vision Q6).

#### FR-052: Ingestion connectors
- **Requirement:** The platform shall provide connectors to ingest documents from approved source systems.
- **Rationale:** Shared ingestion replaces per-team pipelines (G1).
- **Trace:** S01, S06; UC-KA §4.2
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Content from a registered source is ingested with its metadata (source ID, URI, title, last modified).
- **Dependencies / assumptions:** **[Open]** Initial source systems (UC-KA-Q1).

#### FR-053: ACL metadata capture
- **Requirement:** During ingestion, the platform shall capture each document's access-control metadata, map it to Entra ID principals and groups, and store it with every derived chunk.
- **Rationale:** Document-level access control **[Decision]**.
- **Trace:** S05, S06; AC-11; UC-KA-AC1, UC-KA-AC3
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Each indexed chunk has resolvable ACL metadata.
  2. A document whose ACL cannot be resolved is not indexed as retrievable (fail closed).
- **Dependencies / assumptions:** Source systems expose ACLs (UC-KA-A1) **[Assumption]**.

#### FR-054: Chunking, embedding, and tenant indexing
- **Requirement:** The platform shall chunk ingested content, embed it via the gateway (FR-018), and store it in an index owned by the tenant. Chunking parameters are configurable.
- **Rationale:** Shared indexing infrastructure; tenant isolation.
- **Trace:** S01; UC-KA §4.2; AC-08
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Indexes are scoped to one tenant.
  2. Embedding usage is metered to that tenant.
  3. Chunking configuration is versioned.
- **Dependencies / assumptions:** FR-012, FR-018, FR-031.

#### FR-055: Permission-filtered retrieval
- **Requirement:** The platform shall expose a retrieval API that returns only chunks the requesting end user is permitted to read, evaluated at query time before results are returned.
- **Rationale:** Document-level access control **[Decision]**. Filtering must happen before content reaches the model (UC-KA §4.5).
- **Trace:** S05, S06; AC-11; UC-KA-AC1; C9
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. In a test corpus with users of differing permissions, each user receives only permitted chunks, with zero leakage.
  2. Requests without an end-user identity are denied.
- **Dependencies / assumptions:** FR-011, FR-053. Filtering latency is acceptable (UC-KA-A2) **[Assumption]**.

#### FR-056: Incremental re-sync and permission propagation
- **Requirement:** The platform shall re-synchronize sources on a schedule or on change. It shall update content and ACLs, and remove deleted documents.
- **Rationale:** Revoked permissions must take effect (UC-KA §4.5).
- **Trace:** S06, S05; UC-KA-Q2
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. A permission revoked at the source is enforced in retrieval within the agreed lag.
  2. A document deleted at the source is no longer retrievable after the next sync.
- **Dependencies / assumptions:** **[Open]** Maximum permission-revocation lag (UC-KA-Q2).

#### FR-057: Citation metadata
- **Requirement:** The platform shall return citation metadata (document ID, title, URI, and location within the document) with each retrieved chunk.
- **Rationale:** Citations are required for UC-KA **[Decision]**.
- **Trace:** UC-KA-AC2
- **Priority:** Must · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Every retrieval result includes citation metadata that resolves to the source document.
- **Dependencies / assumptions:** FR-052.

#### FR-058: Source purge
- **Requirement:** The platform shall allow a data owner or tenant admin to purge a source and all its derived chunks and embeddings from an index.
- **Rationale:** Data governance; withdrawal of approval.
- **Trace:** S06
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. After a purge, no chunks from the source are retrievable or present in the index.
  2. The purge is audit logged.
- **Dependencies / assumptions:** FR-068.

### 4.11 MLOps: Experiment Tracking, Model Registry, and Deployment

#### FR-059: Experiment tracking
- **Requirement:** The platform shall record, for each training run:
  - parameters;
  - metrics;
  - artifacts;
  - code version;
  - data version.

  Records are scoped to the tenant and project.
- **Rationale:** Reproducibility and lineage (UC-PM §6.2).
- **Trace:** S02; AC-03; UC-PM-AC4
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. Each training run has a retrievable record with parameters, metrics, code version, and data version.
- **Dependencies / assumptions:** FR-012.

#### FR-060: Training job execution
- **Requirement:** The platform shall allow tenants to submit training jobs to platform compute, with requested resources (CPU, memory, and, if approved, GPU) within tenant quotas.
- **Rationale:** Replaces bespoke training infrastructure (S02 pain point).
- **Trace:** S02; UC-PM §6.2; UC-PM-AC1
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. A submitted job runs in the tenant's compute boundary.
  2. Job logs are available to the tenant.
  3. Jobs exceeding quota are queued or rejected.
- **Dependencies / assumptions:** FR-016. **[Open]** GPU need (UC-PM-Q4).

#### FR-061: Model registry with lineage
- **Requirement:** The platform shall provide a model registry that versions model artifacts and links each version to its training run, data version, code version, and evaluation metrics.
- **Rationale:** Lineage and audit (UC-PM §6.5).
- **Trace:** S02, S05; AC-03, AC-09; UC-PM-AC4
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. Every registered version links to its lineage.
  2. Registry entries are tenant-scoped.
- **Dependencies / assumptions:** FR-059.

#### FR-062: Model promotion workflow
- **Requirement:** The platform shall support promotion states (for example: candidate, staging, production, archived), with a configurable evaluation gate and an optional approval (FR-071).
- **Rationale:** Prevents regressed models reaching production (UC-PM §6.6).
- **Trace:** S02, S05; UC-PM-AC4; UC-PM-Q3
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. A model failing the configured evaluation gate cannot be promoted to production.
  2. Each promotion records the promoter.
- **Dependencies / assumptions:** **[Open]** Whether promotion is a sensitive operation (UC-Q3).

#### FR-063: Model deployment
- **Requirement:** The platform shall deploy registered model versions as batch scoring jobs and/or authenticated online endpoints.
- **Rationale:** UC-PM requires predictions delivered to downstream systems.
- **Trace:** S02; UC-PM-AC1
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. A registered version can be deployed through the platform.
  2. Online endpoints reject unauthenticated callers.
- **Dependencies / assumptions:** **[Open]** Batch versus online requirement (UC-PM-Q2).

#### FR-064: Model monitoring and drift detection
- **Requirement:** The platform shall monitor deployed models for service health, input data drift, and prediction drift. It shall alert the owning tenant when configured thresholds are exceeded.
- **Rationale:** Drift detection is required **[Decision]** (UC-PM).
- **Trace:** S02, S04; UC-PM-AC2
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. Injected synthetic drift beyond the threshold produces an alert to the owning tenant.
- **Dependencies / assumptions:** Tenant-defined thresholds (stakeholders §3).

#### FR-065: Model rollback
- **Requirement:** The platform shall allow an authorized user to roll back a deployment to a previous registry version.
- **Rationale:** Recovery from a bad promotion or drift (UC-PM §6.6).
- **Trace:** UC-PM-AC3
- **Priority:** Must · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. Rollback restores the previous version's predictions.
  2. Rollback is recorded in the audit log.
- **Dependencies / assumptions:** FR-061, FR-063.

#### FR-066: Feature pipelines
- **Requirement:** The platform shall provide a framework for defining scheduled feature pipelines whose outputs are versioned and usable consistently for training and serving.
- **Rationale:** UC-PM requires feature pipelines **[Decision]**. Whether a full feature store is needed is **[Open]** (UC-PM-A3).
- **Trace:** S02, S06; UC-PM §6.2
- **Priority:** Should · **MVP:** No · **Phase:** PM
- **Acceptance criteria:**
  1. A feature pipeline run produces a versioned output referenced by training runs (FR-059).
- **Dependencies / assumptions:** Telemetry sources available (D6).

### 4.12 Security Policies, Audit Logging, and Human Approvals

#### FR-067: Central policy management
- **Requirement:** The platform shall allow security admins to define policies that platform services enforce. Policies cover:
  - model and data-classification compatibility;
  - permitted triggers;
  - tool classifications requiring approval;
  - content capture.
- **Rationale:** Secure and governed by default (vision §3.3); consistent controls (G3).
- **Trace:** S05; G3; AC-07
- **Priority:** Must · **MVP:** Yes (model access policy only) · **Phase:** VS (other policy types by KA/OA)
- **Acceptance criteria:**
  1. Policy changes take effect without redeploying platform services.
  2. Policy changes are versioned and audit logged.
- **Dependencies / assumptions:** **[Open]** Policy engine choice.

#### FR-068: Audit logging
- **Requirement:** The platform shall record audit events for all security-relevant actions, including:
  - authentication failures;
  - authorization denials;
  - credential issuance and revocation;
  - role changes;
  - tenant and project lifecycle;
  - model and provider changes;
  - policy changes;
  - approvals;
  - sensitive operations;
  - platform-admin access to tenant data.
- **Rationale:** Audit logging is required **[Decision]**.
- **Trace:** S05; AC-09; VS-AC3; UC-OA-AC3; UC-PM-AC4
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Each event type in the list produces an audit record with actor, tenant, action, target, timestamp, outcome, and trace ID.
- **Dependencies / assumptions:** The complete event list is to be confirmed in `security-governance.md`.

#### FR-069: Tamper-evident audit storage and retention
- **Requirement:** The platform shall store audit records in tamper-evident, append-only storage. Tenants and platform admins cannot alter or delete the records, and they are retained for the defined retention period.
- **Rationale:** Accountability; tamper-evident audit trail for UC-OA (UC-OA §5.5).
- **Trace:** S05; AC-09; UC-OA-AC3
- **Priority:** Must · **MVP:** Yes (append-only) · **Phase:** VS (tamper evidence by OA)
- **Acceptance criteria:**
  1. Attempts to modify or delete audit records are rejected.
  2. Integrity verification detects altered records.
- **Dependencies / assumptions:** **[Open]** Retention period (AC-09).

#### FR-070: Audit access
- **Requirement:** The platform shall let auditors query audit records across tenants, and let tenant admins query records for their own tenant only.
- **Rationale:** Investigation and compliance support.
- **Trace:** S05; AC-09
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Auditor queries return cross-tenant results.
  2. Tenant admin queries return only their own tenant's records.
- **Dependencies / assumptions:** FR-008.

#### FR-071: Human approval workflow
- **Requirement:** The platform shall provide an approval workflow for sensitive operations. The workflow:
  - creates a request containing the action, parameters, evidence, initiator, and trace link;
  - notifies eligible approvers;
  - records an approve or reject decision with a reason;
  - expires the request after a configurable timeout, with no action taken.
- **Rationale:** Approval of sensitive operations is required **[Decision]**.
- **Trace:** S05; AC-10; UC-OA-AC1; FR-048, FR-062
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A sensitive operation proceeds only after an approve decision.
  2. Reject and timeout result in no execution.
  3. All decisions are audit logged.
- **Dependencies / assumptions:** **[Open]** The definition of sensitive operations (SQ3) and the notification channels.

#### FR-072: Separation of duties
- **Requirement:** The platform shall prevent the initiating agent, and, unless policy allows otherwise, the initiating user, from approving their own sensitive operation request.
- **Rationale:** Approval must be independent (UC-OA §5.5).
- **Trace:** S05; UC-OA-Q2
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. A self-approval attempt is rejected when policy forbids it.
  2. Agents can never approve.
- **Dependencies / assumptions:** **[Open]** Self-approval policy (UC-OA-Q2).

#### FR-073: Fail closed on audit unavailability
- **Requirement:** The platform shall block sensitive operations whenever audit records cannot be durably written.
- **Rationale:** No unaudited sensitive actions (UC-OA §5.6).
- **Trace:** S05; UC-OA-AC1, UC-OA-AC3
- **Priority:** Must · **MVP:** No · **Phase:** OA
- **Acceptance criteria:**
  1. With the audit sink made unavailable in test, sensitive operations are rejected.
- **Dependencies / assumptions:** FR-068.

#### FR-074: Content guardrail hooks
- **Requirement:** The gateway shall support configurable guardrail checks on inputs and outputs, with policy-defined actions (allow, redact, block). Example checks are prompt-injection detection and sensitive-data detection.
- **Rationale:** Indexed documents and tool outputs are untrusted input (UC-KA §4.5, UC-OA §5.5).
- **Trace:** S05; C6
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. A configured guardrail blocks or redacts matching test content.
  2. The decision is recorded in the trace.
- **Dependencies / assumptions:** **[Open]** Guardrail approach and ownership of tuning (stakeholders §3 grey areas).

### 4.13 Deployment Templates, SDKs, and Developer Tooling

#### FR-075: Client SDK
- **Requirement:** The platform shall provide a client SDK covering authentication, gateway inference, embeddings, retrieval, and trace propagation.
- **Rationale:** Reduces integration effort; supports the onboarding **[Target]**.
- **Trace:** S01; AC-01; G2
- **Priority:** Should · **MVP:** Yes (gateway and authentication only) · **Phase:** VS
- **Acceptance criteria:**
  1. The quickstart (FR-079) can be completed using the SDK.
  2. The SDK propagates trace context automatically.
- **Dependencies / assumptions:** **[Open]** Initial SDK languages (FR-Q4).

#### FR-076: Command-line interface
- **Requirement:** The platform shall provide a CLI for login (Entra ID), tenant and project creation, credential management, model listing, and usage queries.
- **Rationale:** Self-service without a portal (VS-Q2).
- **Trace:** S01; VS-Q2
- **Priority:** Should · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. Every onboarding step in FR-001–FR-004 can be completed with the CLI.
- **Dependencies / assumptions:** FR-006.

#### FR-077: Developer portal
- **Requirement:** The platform shall provide a web portal for onboarding, project management, the model catalog, usage, and traces.
- **Rationale:** Discoverability for less CLI-oriented users.
- **Trace:** S01, S07; VS-Q2
- **Priority:** Should · **MVP:** No (CLI and API suffice for MVP, **[Open]** VS-Q2) · **Phase:** KA
- **Acceptance criteria:**
  1. Portal functions mirror the CLI and API, and enforce the same authorization.
- **Dependencies / assumptions:** FR-006, FR-010.

#### FR-078: Deployment templates
- **Requirement:** The platform shall provide versioned templates for common workload patterns: a RAG application, an agent with MCP tools, and an ML training/serving pipeline. Templates are pre-wired to platform identity, observability, and metering.
- **Rationale:** A paved road (vision §3.3); faster delivery of the initial workloads (G2).
- **Trace:** S01, S02; G1, G2
- **Priority:** Should · **MVP:** No · **Phase:** KA / OA / PM respectively
- **Acceptance criteria:**
  1. A project created from a template produces a working, traced, metered sample workload without manual infrastructure setup.
- **Dependencies / assumptions:** FR-016, FR-034.

#### FR-079: Documentation and quickstarts
- **Requirement:** The platform shall publish documentation covering onboarding, APIs, error codes, quotas, and security responsibilities, plus a quickstart for the vertical slice.
- **Rationale:** Self-service depends on documentation; supports the onboarding **[Target]**.
- **Trace:** S01; AC-01; VS-AC2
- **Priority:** Must · **MVP:** Yes · **Phase:** VS
- **Acceptance criteria:**
  1. A developer unfamiliar with the platform can complete the quickstart using only the documentation. This is validated in usability testing, not yet performed.
- **Dependencies / assumptions:** FR-004.

#### FR-080: Non-production sandbox
- **Requirement:** The platform shall provide a sandbox entitlement tier with low quotas and only non-sensitive models and data, for experimentation.
- **Rationale:** Experimentation without budget risk (C7); a low-risk default tier (C1).
- **Trace:** S01, S07; C1, C7
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. Sandbox projects cannot access models or data above the sandbox classification.
- **Dependencies / assumptions:** FR-026, FR-067.

### 4.14 Cost Attribution and Budget Management

#### FR-081: Per-request cost estimation
- **Requirement:** The platform shall compute an estimated cost for each gateway request from its token usage and the catalog's pricing reference, and shall store it with the usage record.
- **Rationale:** Cost visibility (G4); FinOps metering from the first slice (vision R6).
- **Trace:** S07; AC-12; VS-Q1
- **Priority:** Should · **MVP:** **[Open]** (VS-Q1) · **Phase:** VS / KA
- **Acceptance criteria:**
  1. Each usage record includes an estimated cost.
  2. Pricing-reference changes apply prospectively and are versioned.
- **Dependencies / assumptions:** FR-024, FR-031. Estimates are not invoices **[Assumption]**.

#### FR-082: Compute cost attribution
- **Requirement:** The platform shall attribute compute consumption to the owning tenant and project. This covers agent runtime, MCP hosting, training jobs, model serving, and indexing.
- **Rationale:** Every workload must be attributable (AC-12); UC-PM is compute-heavy.
- **Trace:** S07; AC-12; UC-PM-AC6
- **Priority:** Must · **MVP:** No · **Phase:** OA / PM
- **Acceptance criteria:**
  1. Compute usage reports allocate at least the agreed percentage of attributable compute to tenants. **[Open]** Target value; shared overhead treatment.
- **Dependencies / assumptions:** FR-016.

#### FR-083: Budgets and alerts
- **Requirement:** The platform shall allow FinOps and tenant admins to set budgets per tenant or project, and shall alert at configurable thresholds.
- **Rationale:** Cost governance (S07); soft budgets first (C7).
- **Trace:** S07; C7
- **Priority:** Should · **MVP:** No · **Phase:** KA
- **Acceptance criteria:**
  1. Crossing a budget threshold produces an alert to configured recipients.
- **Dependencies / assumptions:** FR-081, FR-082.

#### FR-084: Optional hard budget caps
- **Requirement:** The platform shall allow a hard cap to be configured per tenant or project. When a cap is reached, new billable requests are blocked until the cap is raised or the period resets.
- **Rationale:** Some tenants may require strict limits (C7).
- **Trace:** S07; C7
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. With a hard cap reached, billable requests are rejected with a budget error.
- **Dependencies / assumptions:** FR-083.

#### FR-085: Showback and chargeback export
- **Requirement:** The platform shall export attributed usage and cost data per tenant, project, and cost centre for finance processes.
- **Rationale:** Supports whichever funding model is chosen (vision Q4).
- **Trace:** S07, S09; vision Q4; AC-14
- **Priority:** Could · **MVP:** No · **Phase:** Later
- **Acceptance criteria:**
  1. The export totals reconcile with platform usage reports for the same period.
- **Dependencies / assumptions:** **[Open]** Funding model (vision Q4).

---

## 5. First Vertical Slice: MVP Requirements

**Flow [Decision]:**

```
Developer onboarding → AuthN/AuthZ → LLM gateway → inference → usage and trace reporting
```

The MVP is the set of requirements marked **MVP: Yes**. RAG, agents, MCP, and MLOps are excluded from the slice (vision §7.3, **[Assumption]**).

| Slice step | MVP requirements |
|---|---|
| 1. Developer onboarding | FR-001, FR-002, FR-003, FR-004, FR-075 (gateway and authentication only), FR-076, FR-079 |
| 2. AuthN / AuthZ | FR-006, FR-007, FR-008 (core roles), FR-010, FR-012, FR-013 |
| 3. LLM gateway | FR-017, FR-020, FR-022, FR-023, FR-024, FR-025 (approved/retired), FR-026 (default set), FR-027, FR-029, FR-030, FR-067 (model access policy) |
| 4. Model inference | FR-017, FR-020 (routing to an approved deployment) |
| 5. Usage and trace reporting | FR-031, FR-034, FR-035, FR-037, FR-038, FR-068, FR-069 (append-only) |
| Pending decision | FR-081 (cost estimate per request, VS-Q1) |

### 5.1 MVP Exit Criteria

The exit criteria are **[Target]**, mapped to `use-cases.md` §3.3.

| Exit criterion | Verified by |
|---|---|
| VS-AC1: Self-service onboarding without tickets | FR-001, FR-003 acceptance tests |
| VS-AC2: First request in under 30 minutes **[Target]** | FR-004 timing record; definition per vision Q10 |
| VS-AC3: Unauthenticated and non-approved-model requests rejected and logged | FR-007, FR-010, FR-022, FR-068 |
| VS-AC4: Cross-tenant isolation | FR-013 cross-tenant test suite |
| VS-AC5: Usage record and trace for every request | FR-031 reconciliation, FR-034, FR-035 |
| VS-AC6: Gateway availability measured against 99.9% **[Target]** | FR-038 (enables measurement); the measurement itself is defined in `nonfunctional-requirements.md` |

---

## 6. Requirement Traceability Matrix

### 6.1 Stakeholder Acceptance Criteria → Functional Requirements

| Stakeholder AC (`stakeholders.md`) | Functional requirements |
|---|---|
| AC-01: Onboarding < 30 min **[Target]** | FR-001, FR-002, FR-003, FR-004, FR-075, FR-076, FR-079 |
| AC-02: Single gateway API | FR-017, FR-018, FR-020, FR-024 |
| AC-03: Standard MLOps pipeline | FR-059–FR-066 |
| AC-04: 16 of 20 teams adopt **[Target]** | Not directly functional; enabled by FR-078 and FR-079, measured in `success-metrics.md` |
| AC-05: Gateway 99.9% **[Target]** | FR-021, FR-038 (functional enablers); primarily `nonfunctional-requirements.md` |
| AC-06: Incident attribution via traces | FR-034, FR-035, FR-038 |
| AC-07: Identity and least privilege | FR-003, FR-006–FR-011, FR-022, FR-023, FR-049, FR-067 |
| AC-08: Tenant isolation | FR-012, FR-013, FR-016, FR-035, FR-054 |
| AC-09: Audit logging | FR-061, FR-068, FR-069, FR-070 |
| AC-10: Approval for sensitive operations | FR-047, FR-048, FR-071, FR-072, FR-073 |
| AC-11: RAG honors source ACLs | FR-011, FR-053, FR-055, FR-056 |
| AC-12: Usage attribution | FR-031, FR-037, FR-054, FR-081, FR-082 |
| AC-13: Architecture reviewed | Not functional; later architecture phase |
| AC-14: Leadership reporting | FR-037, FR-085; `success-metrics.md` |

### 6.2 Use-Case Acceptance Criteria → Functional Requirements

| Use-case AC (`use-cases.md`) | Functional requirements |
|---|---|
| VS-AC1 | FR-001, FR-003 |
| VS-AC2 | FR-004, FR-079 |
| VS-AC3 | FR-007, FR-010, FR-022, FR-068 |
| VS-AC4 | FR-013, FR-035 |
| VS-AC5 | FR-031, FR-034, FR-035 |
| VS-AC6 | FR-038 (+ NFR) |
| UC-KA-AC1 | FR-011, FR-053, FR-055 |
| UC-KA-AC2 | FR-057 |
| UC-KA-AC3 | FR-053 |
| UC-KA-AC4 | FR-031, FR-034 |
| UC-KA-AC5 | FR-017, FR-018, FR-054, FR-055 |
| UC-KA-AC6 | FR-021, FR-055. App-level refusal behavior is owned by the application team |
| UC-OA-AC1 | FR-047, FR-048, FR-071, FR-073 |
| UC-OA-AC2 | FR-047, FR-048, FR-013 |
| UC-OA-AC3 | FR-068, FR-069 |
| UC-OA-AC4 | FR-041, FR-042 |
| UC-OA-AC5 | FR-043 |
| UC-OA-AC6 | FR-044, FR-050 |
| UC-OA-AC7 | FR-034 |
| UC-PM-AC1 | FR-059, FR-060, FR-061, FR-063 |
| UC-PM-AC2 | FR-064 |
| UC-PM-AC3 | FR-065 |
| UC-PM-AC4 | FR-059, FR-061, FR-062 |
| UC-PM-AC5 | FR-013, FR-016 |
| UC-PM-AC6 | FR-082 |

### 6.3 Requirements by Vision Goal

| Goal (`platform-vision.md`) | Primary requirement areas |
|---|---|
| G1 Reduce duplication | 4.4 Gateway, 4.9 MCP, 4.10 RAG, 4.11 MLOps, 4.13 Templates |
| G2 Accelerate delivery | 4.1 Onboarding, 4.13 Tooling |
| G3 Standardize security and governance | 4.2 Identity, 4.3 Isolation, 4.5 Catalog, 4.12 Security |
| G4 Cost transparency | 4.6 Metering, 4.14 Cost |
| G5 Unified observability | 4.7 Tracing and reporting |
| G6 Diverse workloads | 4.8 Agents, 4.10 RAG, 4.11 MLOps |

### 6.4 Priority Summary

| Priority | Count | Notes |
|---|---|---|
| Must | 58 | Includes FR-045, which is Must for user-initiated runs only (event-initiated runs are Could) |
| Should | 21 | |
| Could | 6 | |
| **Total** | **85** | MVP: 31 requirements marked "Yes" (several partial); FR-081 pending VS-Q1 |

The counts are a draft. Verification belongs to `coverage-audit.md`.

---

## 7. Open Questions

| ID | Question | Related | Suggested owner |
|---|---|---|---|
| FR-Q1 | Who may create tenants: any authenticated employee, or only designated groups? | FR-001 | Security / IAM |
| FR-Q2 | Are static, project-scoped API keys permitted, or only OIDC workload identities? | FR-003, FR-007 | Security / IAM |
| FR-Q3 | Should the gateway API adopt an existing widely used schema for client compatibility? | FR-017 | Platform eng, EA |
| FR-Q4 | Which SDK languages come first? | FR-075 | Platform eng with app teams |
| FR-Q5 | What is the full definition of "sensitive operation" across agent actions, model promotion, and quota changes? | FR-047, FR-062, FR-071; SQ3 | Security / IAM |
| FR-Q6 | What are the retention periods for audit records, traces, usage records, and captured content? | FR-035, FR-036, FR-069; AC-09 | Security, Legal |
| FR-Q7 | Which policy engine or approach implements FR-067? | FR-067 | Platform eng, Security |
| FR-Q8 | What is the maximum acceptable permission-revocation lag for RAG? | FR-056; UC-KA-Q2 | Security, Data owners |
| FR-Q9 | Is the orchestration runtime LangGraph itself or an equivalent? | FR-040; UC-OA-Q4 | Platform eng, EA |
| FR-Q10 | Is the per-request cost estimate part of the MVP? | FR-081; VS-Q1 | FinOps, Platform eng |
| FR-Q11 | How are shared platform overhead costs allocated to tenants? | FR-082; vision Q4 | FinOps |
| FR-Q12 | Should `stakeholders.md` SQ4 be updated to reflect the Entra ID/OIDC decision recorded in §1.4? | §1.4 | Document owner |

Additional open items from earlier documents remain unresolved and affect these requirements: vision Q3, Q5, Q6, Q10; SQ3, SQ8; UC-OA-Q2, UC-OA-Q3, UC-PM-Q2, UC-PM-Q4.
