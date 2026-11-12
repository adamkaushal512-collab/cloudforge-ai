# CloudForge AI: Stakeholders

| Field | Value |
|---|---|
| Document | Stakeholders |
| Phase | 01: Enterprise Discovery |
| Status | Draft |
| Related | `platform-vision.md`, `use-cases.md`, `functional-requirements.md`, `nonfunctional-requirements.md`, `security-governance.md`, `success-metrics.md` |

---

## 1. Purpose and Disclaimer

This document identifies the stakeholders of CloudForge AI and covers:

- what each stakeholder needs and what success means to them;
- how responsibility is divided between the platform team and application teams;
- who decides and who approves;
- where stakeholder interests conflict.

It is the stakeholder input to the requirements documents in this phase.

> **Disclaimer:** CloudForge is a fictional global technology enterprise, and CloudForge AI is a fictional platform. This document is a planning artifact.
>
> - **No stakeholder interviews have been conducted.**
> - **No baselines have been measured.**
> - **No stakeholder has signed off on anything in this document.**
>
> The needs, pain points, and success criteria below are informed by the established decisions and by typical enterprise patterns. They are hypotheses to validate in discovery, not findings.

### Labels

The labels are the same as in `platform-vision.md`:

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input, not as a measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal. It is not measured or committed. |
| **[Open]** | An unresolved question that needs an owner and a decision. |

### Established Inputs

These are **[Decision]**:

- About 20 engineering teams will consume the platform.
- The platform team owns the shared AI infrastructure. Application teams own application-specific business logic.
- The shared services are: LLM gateway, agent orchestration, MCP, RAG, MLOps, Kubernetes, identity, observability, FinOps, and self-service tooling.
- The initial workloads are: enterprise knowledge assistant, AI operations agent, and predictive maintenance.
- Developers need self-service access.
- Security requires least privilege, tenant isolation, audit logging, and approvals for sensitive operations.

The proposed goals are all **[Target]**:

- onboarding in under 30 minutes;
- adoption by 16 of the 20 teams (80%, consistent with `platform-vision.md`);
- 99.9% LLM gateway availability.

---

## 2. Stakeholder Register

The stakeholder groups are **[Decision]**. The needs, pain points, and success criteria in each row are **[Assumption]** until they are validated in discovery. Success criteria that contain numbers repeat the proposed **[Target]** values.

| ID | Stakeholder | Role | Key needs | Expected pain points today | Success criteria |
|---|---|---|---|---|---|
| S01 | **AI developers** (application teams) | Build LLM- and agent-based features into products, such as the knowledge assistant and the AI operations agent | Self-service onboarding; one API for many models; RAG and MCP building blocks; fast local-to-production path; clear docs | Rebuilding gateway, auth, and RAG plumbing; waiting on access tickets; inconsistent tooling across teams | First authenticated gateway request in under 30 minutes **[Target]**; no infrastructure code needed for common patterns |
| S02 | **ML engineers** (application teams) | Train, evaluate, and deploy classical ML models, such as predictive maintenance | Training compute, experiment tracking, model registry, deployment and monitoring pipelines | Bespoke MLOps stacks; difficult GPU or compute access; no standard model promotion path | Model goes from registry to serving through a standard pipeline; drift and performance are visible |
| S03 | **Platform engineers** (platform team) | Build and evolve the shared services | Clear scope; a reusable multi-tenant architecture; manageable support load; adoption signal | Fragmented team-specific stacks to replace; risk of becoming a ticket queue | Services are adopted by 16 of 20 teams **[Target]**; most requests are handled by self-service |
| S04 | **SRE** (platform team or central ops) | Run the reliability of platform services | SLOs, alerting, runbooks, capacity planning, safe deployment, dependency visibility | Many unmonitored team-built gateways; unclear on-call ownership; provider outages | LLM gateway at 99.9% availability **[Target]**; incidents are detected and attributed to platform or tenant |
| S05 | **Security / IAM** | Define and enforce identity, access, and security policy | Least privilege, tenant isolation, audit logging, approvals for sensitive operations **[Decision]**; secrets management; guardrails | Inconsistent controls per team; scattered credentials; incomplete audit trails | All platform access is identity-bound and audited; no cross-tenant access; sensitive operations are approval-gated |
| S06 | **Data engineers** | Provide and govern the data sources used for RAG and ML | Controlled ingestion; preservation of source access controls; lineage; data classification enforcement | Uncontrolled copies of data into team vector stores; unknown data usage | Each data source onboarded to RAG or MLOps has an owner, a classification, and enforced access |
| S07 | **FinOps / Finance** | Track, attribute, and govern AI and infrastructure spend | Usage metering per tenant and workload; budgets and alerts; showback or chargeback data | Spend spread across team accounts and provider bills; no attribution | Every gateway request and compute workload is attributable to a tenant |
| S08 | **Enterprise architects** | Ensure the platform fits enterprise standards and long-term direction | Reference architecture; standards alignment; extensibility; avoiding lock-in | Divergent designs across teams; hard-to-govern technology sprawl | Platform architecture is reviewed and adopted as the reference for AI workloads |
| S09 | **Engineering leadership** | Sponsor, fund, and prioritize the platform | Evidence of value; adoption; risk reduction; delivery predictability | Duplicated investment across about 20 teams; unclear AI risk posture | Measurable reduction in duplication **[Open: no baseline]**; 16 of 20 teams adopt **[Target]** |

**Workload owners:** S01 and S02 include the owners of the three initial workloads. **[Open]** We don't yet know which teams own each workload or whether they have committed to be early adopters (`platform-vision.md` Q9).

---

## 3. Ownership Boundaries: Platform Team vs Application Teams

The split of shared infrastructure to the platform team and business logic to application teams is **[Decision]**. The detail at the service level is **[Assumption]**.

| Service / area | Platform team owns | Application team owns |
|---|---|---|
| **LLM gateway** | Provider integration, routing, quotas, credential isolation, policy enforcement, gateway SLO | Prompts, model choice within approved options, handling of responses |
| **Agent orchestration** | Runtime, execution sandboxing, tool-call policy hooks, tracing | Agent design, task logic, tool selection, outcome quality |
| **MCP** | MCP hosting, registry, authentication, and authorization for tool access | Domain-specific MCP servers they build and their correctness **[Assumption]** |
| **RAG** | Ingestion framework, embedding and indexing services, retrieval APIs, access-control enforcement | Corpus selection, chunking choices and retrieval tuning, answer quality |
| **MLOps** | Training and serving infrastructure, model registry, pipelines, monitoring framework | Features, models, evaluation criteria, model performance |
| **Kubernetes** | Clusters, namespaces per tenant, base policies, upgrades | Workload manifests and configuration within the guardrails |
| **Identity** | Platform identity integration, tenant and role model, service identities | Assigning team members to roles; their application's end-user authorization |
| **Observability** | Trace, metric, and log pipelines; platform dashboards; retention | App-level dashboards, alerts, and SLOs |
| **FinOps** | Metering, attribution, budget tooling, reports | Staying within budget; optimizing their own usage |
| **Self-service tooling** | Portal, CLI, templates, docs, onboarding flow | Using the tooling; giving feedback |
| **Incidents** | Platform-service incidents | Application incidents, including those caused by business logic or prompts |

**Grey areas, all [Open]:**

- Who owns the safety of model outputs and guardrail tuning: the platform default or the app override?
- Who supports shared MCP servers built by one team but used by others?
- Who owns end-to-end quality when a failure crosses platform and app boundaries, such as poor retrieval?

---

## 4. RACI Matrix

Key: **R** = Responsible, **A** = Accountable (exactly one per row), **C** = Consulted, **I** = Informed.

All of the assignments below are **[Assumption]**. They are a proposal for discovery review, and no stakeholder has agreed to them.

Column abbreviations:

| Abbreviation | Stakeholder |
|---|---|
| PE | Platform engineering |
| SRE | SRE |
| SEC | Security / IAM |
| APP | Application teams (AI developers and ML engineers) |
| DE | Data engineering |
| FIN | FinOps / Finance |
| EA | Enterprise architecture |
| EL | Engineering leadership |

| # | Activity | PE | SRE | SEC | APP | DE | FIN | EA | EL |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Platform vision, roadmap, and prioritization | R | C | C | C | C | C | C | **A** |
| 2 | Platform reference architecture | R | C | C | C | C | I | **A** | I |
| 3 | Build and operate shared services | **A/R** | R | C | I | C | I | C | I |
| 4 | LLM gateway availability SLO (99.9% **[Target]**) | R | **A** | I | I | – | I | I | I |
| 5 | Tenant onboarding (self-service flow) | **A/R** | I | C | R | – | I | – | I |
| 6 | Identity, tenant, and role model | R | I | **A** | C | – | – | C | I |
| 7 | Approval of sensitive operations | R | I | **A** | R (requests) | C | – | – | I |
| 8 | Audit logging and retention | R | C | **A** | I | – | – | – | I |
| 9 | Approved model and provider list | C | C | **A** | C | – | C | C | I |
| 10 | Data source onboarding to RAG or MLOps | R | – | C | C | **A** | – | – | – |
| 11 | Application business logic, prompts, and agents | I | – | C | **A/R** | C | – | – | – |
| 12 | Model training, evaluation, and promotion | C | – | C | **A/R** | C | – | – | – |
| 13 | Usage metering and cost attribution | R | I | – | I | – | **A** | – | I |
| 14 | Budgets and showback or chargeback policy | C | – | – | C | – | R | – | **A** |
| 15 | Platform incident response | R | **A** | C | I | – | – | – | I |
| 16 | Application incident response | C | C | C | **A/R** | – | – | – | – |
| 17 | Platform success metrics and reporting | **A/R** | C | C | I | – | C | – | I |

**Notes:**

- Row 3 uses **A/R** to mean that platform engineering is both accountable and responsible.
- Row 7: application teams raise the requests, Security/IAM approves them, and the platform enforces the approval.
- Rows 9 and 14 depend on the open questions in `platform-vision.md` Q5 (approved providers) and Q4 (funding model).

---

## 5. Stakeholder Conflicts and Architectural Tradeoffs

All conflicts below are **[Assumption]**: they are expected tensions, not observed disputes. The proposed resolutions are **[Open]** until the decision authority in §6 accepts them.

| ID | Conflict | Stakeholders | Tradeoff | Proposed direction |
|---|---|---|---|---|
| C1 | **Self-service speed vs least privilege and approvals** | S01, S02 vs S05 | Onboarding in under 30 minutes **[Target]** conflicts with manual approval gates | Tiered access: auto-provision low-risk defaults (approved models, non-sensitive data); require approval only for sensitive operations. **[Open]** "Sensitive operation" needs a definition. |
| C2 | **Model choice flexibility vs approved-provider governance** | S01 vs S05, S08 | Developers want the newest models; security wants a vetted list | Gateway enforces an approved catalog with a fast-track review path |
| C3 | **Shared infrastructure (efficiency) vs tenant isolation (security)** | S03, S07 vs S05 | Shared clusters and indexes reduce cost but widen the blast radius | Logical isolation by default; dedicated resources for higher data classifications. **[Open]** Classification thresholds are not yet set. |
| C4 | **Gateway as a central control point vs a single point of failure** | S05, S07 vs S04, S01 | Centralization enables policy and metering but couples all tenants | HA, multi-provider routing, per-tenant rate limits, graceful degradation (see `platform-vision.md` R2) |
| C5 | **Standardization vs team autonomy** | S08, S03 vs S01, S02 | Paved road vs existing team stacks | Paved road, not a mandate (vision principle); clear extension points. **[Open]** Mandate or opt-in (vision Q7)? |
| C6 | **Full observability vs data privacy** | S04 vs S05, S06 | Full prompt and response tracing aids debugging but may capture sensitive data | Metadata traces by default; content capture is opt-in with redaction and retention limits |
| C7 | **Cost control vs experimentation** | S07 vs S01, S02 | Hard budgets may block exploration | Soft budgets with alerts first; hard caps are configurable per tenant |
| C8 | **Platform roadmap breadth vs depth** | S01, S02 (each wanting its service first) vs S03 | Ten services compete for priority | Vertical-slice delivery; prioritize by the initial workloads |
| C9 | **RAG source access controls vs retrieval simplicity** | S06, S05 vs S01 | Preserving document-level permissions adds complexity and latency | Enforce source ACLs at retrieval; this is a non-negotiable for the enterprise knowledge assistant **[Assumption]** |

---

## 6. Decision and Approval Authority

This authority model is **[Assumption]**. It is a proposed governance model, and no body has been formed and no authority has been delegated.

| Decision type | Proposed decision owner | Must consult | Escalation |
|---|---|---|---|
| Platform scope, roadmap, priorities | Engineering leadership | Platform eng, EA, app team reps | Executive sponsor **[Open]** |
| Reference architecture and technology choices | Enterprise architecture | Platform eng, SRE, Security | Engineering leadership |
| Security policy, tenant isolation model, IAM | Security / IAM | Platform eng, EA | CISO-equivalent **[Open]** |
| Sensitive operation approvals (per request) | Security / IAM (or a delegated approver) | Requesting app team, data owner | Security leadership |
| Approved model and provider catalog | Security / IAM | EA, FinOps, app teams | Engineering leadership |
| Platform SLOs and error budgets | SRE | Platform eng, app teams | Engineering leadership |
| Data source onboarding and classification | Data owner via data engineering | Security | Data governance body **[Open]** |
| Funding, budgets, chargeback model | Engineering leadership with Finance | FinOps, platform eng | Executive sponsor |
| Application design and business logic | Application team | Platform eng (for platform fit) | Application team's leadership |
| Exceptions to platform standards | Enterprise architecture | Security, platform eng | Engineering leadership |

**[Open]** Is a standing forum, such as an AI Platform Steering Group, needed? If so, who sits on it and how often does it meet?

---

## 7. Cross-Team Dependencies and Risks

### 7.1 Dependencies

All dependencies below are **[Assumption]**.

| ID | Dependent | Depends on | Dependency |
|---|---|---|---|
| D1 | All platform services | Security / IAM | Enterprise identity provider integration and the tenant and role model |
| D2 | First vertical slice | Security / IAM, Platform eng | AuthN/AuthZ before any gateway traffic (vision §7) |
| D3 | LLM gateway | Security, Procurement | Approved model providers and credentials (vision Q5) |
| D4 | RAG / knowledge assistant | Data engineering, data owners | Classified, access-controlled source data |
| D5 | AI operations agent | SRE / operations tooling owners | MCP access to operational systems with scoped permissions |
| D6 | Predictive maintenance | Data engineering, ML engineers | Sensor or telemetry data pipelines; MLOps services |
| D7 | Usage reporting | FinOps | Attribution model and cost data from providers |
| D8 | All shared services | SRE | Kubernetes platform, observability pipelines, on-call |
| D9 | Adoption target | Application teams, Engineering leadership | Team capacity to migrate; leadership prioritization |

### 7.2 Risks

These stakeholder risks add to `platform-vision.md` R1–R8. Likelihood and impact are qualitative and not yet assessed.

| ID | Risk | Affected stakeholders | Proposed mitigation |
|---|---|---|---|
| SR1 | Security approval latency makes the 30-minute onboarding target impossible | S01, S05 | Tiered access (C1); pre-approved default tier |
| SR2 | Application teams lack capacity to migrate off existing stacks | S01, S02, S09 | Migration support; demonstrate value with early adopters first |
| SR3 | Unclear grey-area ownership (§3) causes incidents to fall between teams | S04, S01 | Explicit runbooks and RACI ratification |
| SR4 | Data owners are unavailable or unwilling to approve RAG sources | S06, S01 | Engage data owners early; start with low-sensitivity corpora |
| SR5 | No executive sponsor or funding decision | S09, S03 | Confirm sponsorship (vision A8) before scaling past the first slice |
| SR6 | Platform team is too small for ten services and about 20 tenants | S03, S04 | Scope to the vertical slice; self-service investment |
| SR7 | Stakeholders reject proposed RACI and authority assignments | All | Validate through discovery sessions before requirements baseline |

---

## 8. Discovery Questions and Unresolved Assumptions

### 8.1 Discovery Questions

All questions below are **[Open]**.

| ID | Question | Directed to |
|---|---|---|
| SQ1 | Which teams own each initial workload, and will they commit as early adopters? | Engineering leadership |
| SQ2 | What infrastructure does each of the ~20 teams currently run (gateway, RAG, MCP, monitoring, deployment)? | Application teams |
| SQ3 | What qualifies as a "sensitive operation" requiring approval, and what approval turnaround is acceptable? | Security / IAM |
| SQ4 | Which enterprise identity provider and role model must the platform integrate with? | Security / IAM |
| SQ5 | What data classifications exist, and which may be used for RAG, prompts, or training? | Data engineering, Security |
| SQ6 | Which operational systems will the AI operations agent need to access, and with what permissions? | SRE, Security |
| SQ7 | What data sources and compute does predictive maintenance require? | ML engineers, Data engineering |
| SQ8 | Is prompt and response content allowed in traces, and under what retention? | Security, SRE |
| SQ9 | What attribution granularity does Finance need: team, workload, or user? | FinOps |
| SQ10 | Who is the executive sponsor, and which body ratifies decisions in §6? | Engineering leadership |
| SQ11 | How is "adoption" defined for the 16-of-20 target, and by when? (vision Q2) | Engineering leadership, Platform eng |

### 8.2 Unresolved Assumptions

| ID | Assumption | Validation approach |
|---|---|---|
| SA1 | The stakeholder needs and pain points in §2 reflect real concerns | Discovery interviews (not yet conducted) |
| SA2 | The RACI in §4 is acceptable to all parties | RACI review sessions |
| SA3 | Security will accept tiered, auto-provisioned access for low-risk use | Security policy review |
| SA4 | Application teams are willing to give up owning infrastructure | Early-adopter feedback; adoption tracking |
| SA5 | One platform team can serve LLM, agentic, and classical ML stakeholders | Capacity planning; roadmap review |
| SA6 | Data owners will allow source data into shared RAG services | Data governance review |

---

## 9. Stakeholder Acceptance Criteria and Traceability

The acceptance criteria are **[Assumption]**: they are proposed, and no stakeholder has agreed to them. Numeric values are **[Target]**.

Traceability refers to the goals in `platform-vision.md` (G1–G6). Requirement IDs in `functional-requirements.md` (FR) and `nonfunctional-requirements.md` (NFR) have not been assigned yet. The "Requirement area" column names the area each criterion should trace to once IDs exist **[Open]**.

| AC ID | Stakeholder | Acceptance criterion | Vision goal | Requirement area (IDs TBD) |
|---|---|---|---|---|
| AC-01 | S01 AI developers | A new team completes self-service onboarding and makes a first authenticated gateway request in under 30 minutes **[Target]** | G2 | FR: onboarding, developer tooling; NFR: usability |
| AC-02 | S01 AI developers | A single gateway API gives access to all approved models | G1, G2 | FR: LLM gateway |
| AC-03 | S02 ML engineers | A model can be registered, deployed, and monitored through standard MLOps pipelines | G1, G6 | FR: MLOps |
| AC-04 | S03 Platform eng | 16 of 20 teams adopt the platform **[Target]**; definition of adoption **[Open]** | G1 | Success metrics |
| AC-05 | S04 SRE | LLM gateway meets 99.9% availability **[Target]** with defined measurement (vision Q3) | G5 | NFR: availability, reliability |
| AC-06 | S04 SRE | Platform incidents can be distinguished from tenant and provider incidents using traces | G5 | FR: observability; NFR: operability |
| AC-07 | S05 Security / IAM | Every platform action is tied to an authenticated identity and least-privilege role | G3 | FR: identity / authorization; security-governance |
| AC-08 | S05 Security / IAM | No tenant can read another tenant's data, credentials, or traces | G3 | NFR: tenant isolation; security-governance |
| AC-09 | S05 Security / IAM | All security-relevant actions are audit logged with defined retention **[Open]** | G3 | FR: audit; security-governance |
| AC-10 | S05 Security / IAM | Sensitive operations cannot proceed without a recorded approval | G3 | FR: approval workflow; security-governance |
| AC-11 | S06 Data engineers | RAG retrieval honors source-system access controls | G3, G6 | FR: RAG; security-governance |
| AC-12 | S07 FinOps | Each gateway request and workload is attributed to a tenant in usage reports | G4 | FR: FinOps metering, usage reporting |
| AC-13 | S08 Enterprise architects | Platform architecture is documented and reviewed against enterprise standards | G1, G6 | Architecture (later phase) |
| AC-14 | S09 Engineering leadership | Platform reports adoption, availability, onboarding time, and cost against targets | G1–G5 | Success metrics |

### Coverage Check

| Stakeholder | Acceptance criteria |
|---|---|
| S01 | AC-01, AC-02 |
| S02 | AC-03 |
| S03 | AC-04 |
| S04 | AC-05, AC-06 |
| S05 | AC-07 to AC-10 |
| S06 | AC-11 |
| S07 | AC-12 |
| S08 | AC-13 |
| S09 | AC-14 |

Every register stakeholder has at least one criterion. The full cross-document traceability audit will happen in `coverage-audit.md`.
