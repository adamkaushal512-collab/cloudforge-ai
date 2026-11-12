# CloudForge AI: Use Cases

| Field | Value |
|---|---|
| Document | Use Cases |
| Phase | 01: Enterprise Discovery |
| Status | Draft |
| Related | `platform-vision.md`, `stakeholders.md`, `functional-requirements.md`, `nonfunctional-requirements.md`, `security-governance.md`, `success-metrics.md` |

---

## 1. Purpose and Disclaimer

This document describes the three initial workloads that CloudForge AI must support. It also describes the first vertical slice that comes before them. For each workload, it covers:

- the business problem and the people who use it;
- the end-to-end workflow and the platform capabilities it needs;
- data, security, and tenant-isolation needs;
- failure handling;
- proposed metrics and acceptance criteria.

The workloads are the concrete test cases for the platform's requirements.

> **Disclaimer:** CloudForge is a fictional enterprise, and CloudForge AI is a fictional platform. This document is a planning artifact.
>
> - **No customer or stakeholder interviews have been conducted.**
> - **No baselines or results have been measured.**
> - **No stakeholder has approved these use cases.**
>
> The personas, workflows, and failure modes are design hypotheses to validate in discovery.

### Labels

The labels are the same as in `platform-vision.md` and `stakeholders.md`:

| Label | Meaning |
|---|---|
| **[Decision]** | An established decision for this program. It is treated as settled input, not as a measured fact. |
| **[Assumption]** | Believed to be true but not yet validated. |
| **[Target]** | A proposed goal. It is not measured or committed. |
| **[Open]** | An unresolved question that needs an owner and a decision. |

### References to Other Documents

- **Goals** G1–G6 and **vision questions** Q1–Q10 are defined in `platform-vision.md`.
- **Stakeholders** S01–S09, **acceptance criteria** AC-01 to AC-14, **conflicts** C1–C9, and **dependencies** D1–D9 are defined in `stakeholders.md`.
- **New IDs in this document:**
  - workloads: `UC-KA`, `UC-OA`, `UC-PM`;
  - vertical slice: `VS`;
  - acceptance criteria: `<id>-ACn`;
  - assumptions: `<id>-An`;
  - questions: `<id>-Qn`.

**Metric values:** Except where a value is already an established **[Target]**, this document names each metric but leaves its value **[Open]**. No baselines exist from which to set one responsibly (vision Q1).

---

## 2. Workload Summary

| ID | Workload | Workload type | Core capabilities (established) |
|---|---|---|---|
| UC-KA | Enterprise knowledge assistant | LLM + retrieval | LLM gateway, RAG, document-level access control, citations, observability **[Decision]** |
| UC-OA | AI operations agent | Agentic | Graph-based (LangGraph-style) agent orchestration, MCP tools, scoped authorization, human approval for sensitive operations, audit trails **[Decision]** |
| UC-PM | Predictive maintenance | Classical ML | ML training, feature pipelines, model registry, deployment, monitoring, drift detection **[Decision]** |

---

## 3. First Vertical Slice (VS)

### 3.1 Flow

The flow is **[Decision]**:

```
Developer onboarding → Authentication/Authorization → LLM gateway → Model inference → Usage and trace reporting
```

The slice is not a workload in its own right. It is the shared foundation that every LLM-based workload depends on. It is built first so that the thinnest end-to-end path is proven before RAG, agents, MCP, or MLOps are added (vision §7.3).

### 3.2 Steps

| Step | Actor | What happens | Output | Label |
|---|---|---|---|---|
| 1. Onboarding | AI developer (S01) | Registers the team as a tenant through self-service tooling; selects approved models; receives a quota and credentials | Tenant record, role bindings, scoped credential | [Decision] flow; [Assumption] detail |
| 2. AuthN/AuthZ | Platform identity | Authenticates the caller against the enterprise IdP or a service identity; authorizes tenant, role, and model access | Authenticated request context (tenant ID, principal, role) | [Decision] |
| 3. LLM gateway | Gateway | Applies policy (approved model, quota, rate limit) and routes to a provider or self-hosted model | Routed request with a trace ID | [Decision] |
| 4. Inference | Model provider or self-hosted model | Generates the response | Completion; token counts | [Decision] |
| 5. Usage and trace reporting | Observability + FinOps | Records tenant-attributed usage (tokens, cost estimate) and a trace (latency, status, model) | Usage record; trace visible to the tenant only | [Decision] |

### 3.3 Acceptance Criteria

| ID | Criterion | Traces to |
|---|---|---|
| VS-AC1 | A new team completes onboarding and receives a working credential without filing a ticket | AC-01, G2 |
| VS-AC2 | Time from starting onboarding to the first successful authenticated gateway request is under 30 minutes **[Target]**. **[Open]** The start and end events need definition (vision Q10). | AC-01 |
| VS-AC3 | Unauthenticated requests, and requests for non-approved models, are rejected and logged | AC-07, AC-09 |
| VS-AC4 | Tenant A cannot use Tenant B's credentials, quota, usage records, or traces | AC-08 |
| VS-AC5 | Every successful and failed request yields a tenant-attributed usage record and trace | AC-06, AC-12 |
| VS-AC6 | Gateway availability is measured against 99.9% **[Target]** using a definition agreed in vision Q3 | AC-05 |

### 3.4 Slice Assumptions and Open Questions

- **VS-A1 [Assumption]:** At least one approved model provider or self-hosted model is available when the slice is built (vision A7).
- **VS-A2 [Assumption]:** Security accepts auto-provisioning of a low-risk default tier (stakeholders C1, SA3).
- **VS-Q1 [Open]:** Does the slice include a cost estimate per request, or only token counts?
- **VS-Q2 [Open]:** Is a developer portal required, or is CLI/API onboarding enough for the slice?

---

## 4. UC-KA: Enterprise Knowledge Assistant

### 4.1 Business Problem and Personas

**Problem [Assumption]:** Employees struggle to find accurate, current answers across fragmented internal knowledge, such as wikis, policies, runbooks, and engineering docs. Several teams may be building separate assistants on their own RAG stacks (vision §2.1). Duplicated retrieval infrastructure risks inconsistent access control, which can surface documents to users who should not see them.

**Personas [Assumption]:**

| Persona | Description | Goal |
|---|---|---|
| Employee end user | Any authenticated CloudForge employee | Gets a correct, cited answer only from documents they are permitted to read |
| Assistant developer (S01) | Builds the assistant on the platform | Composes the gateway and RAG without building infrastructure |
| Content / data owner (S06) | Owns source repositories | Ensures their content is indexed with the correct access controls |

### 4.2 Trigger and Workflow

**Trigger:** An end user submits a natural-language question through the assistant's UI or an integrated chat tool. The UI is owned by the application team.

**Ingestion path (runs ahead of time):**

1. A data owner approves a source (stakeholders D4).
2. The platform RAG ingestion pulls the content, along with its **source ACL metadata** and classification.
3. The content is chunked, embedded through the gateway, and indexed in the tenant's index.
4. Re-sync happens on a schedule or on change, which keeps ACLs and content current. **[Open]** Sync frequency.

**Query path:**

1. The user authenticates; the app forwards the user identity (not only the app's service identity) to the platform.
2. The RAG retrieval API searches the tenant index **filtered by the user's document permissions**.
3. The app builds a prompt from the permitted chunks and calls the LLM gateway.
4. The model generates an answer. The app returns the answer with **citations** linking to source documents.
5. Usage and a trace are recorded: retrieval latency, document IDs retrieved, model, tokens, and tenant.
6. Optionally, the user gives feedback (helpful / not helpful), which is attached to the trace.

### 4.3 Platform Capabilities and Dependencies

| Capability | Use | Owner (per stakeholders §3) |
|---|---|---|
| Identity | End-user identity propagation; tenant and service identity | Platform |
| LLM gateway | Embedding and generation calls | Platform |
| RAG | Ingestion connectors, embedding, indexing, ACL-filtered retrieval | Platform (app tunes corpus and retrieval) |
| Observability | Traces covering retrieval and generation | Platform (app owns dashboards) |
| FinOps | Attribution of embedding and generation tokens | Platform |
| Self-service tooling | Onboarding; RAG configuration | Platform |

**Dependencies:** VS (all of it); D1, D3, D4; data owner approvals; source-system ACL APIs **[Assumption]**.

### 4.4 Data Inputs and Outputs

| Direction | Data | Classification |
|---|---|---|
| Input | Source documents and their ACL metadata | Varies; **[Open]** which classifications are allowed (vision Q6, SQ5) |
| Input | User question, user identity | Internal; may contain sensitive content |
| Output | Generated answer with citations (document ID, title, link) | Inherits the highest classification of the cited sources **[Assumption]** |
| Output | Usage records, traces, feedback | Internal; **[Open]** whether prompt and answer text is stored (SQ8) |

### 4.5 Security and Tenant-Isolation Requirements

- **Document-level access control [Decision]:** Retrieval returns only chunks the requesting user may read in the source system. The filter is applied at retrieval time, before content reaches the model (stakeholders C9, AC-11).
- **Tenant isolation:** Each tenant's indexes, embeddings, and traces are inaccessible to other tenants (AC-08).
- **Permission freshness:** Revoked source permissions take effect in the index within a defined window. **[Open]** Maximum acceptable lag.
- **No retrieval through the model:** The model receives only permitted chunks, so it cannot disclose content the user could not otherwise see **[Assumption]**: this depends on correct filtering upstream.
- **Prompt injection from documents:** Content in indexed documents must be treated as untrusted input **[Assumption]**. **[Open]** Guardrail approach.
- **Audit:** Each query records the user, the tenant, and the document IDs retrieved (AC-09).

### 4.6 Failure Modes and Fallback

| Failure | Impact | Fallback behavior |
|---|---|---|
| Model provider unavailable | No answers | Gateway fails over to an alternate approved model **[Assumption]**; otherwise a clear "temporarily unavailable" message, never an uncited guess |
| Retrieval service unavailable | No grounding | Refuse to answer rather than answer ungrounded **[Assumption]** |
| ACL metadata missing or stale for a document | Possible over-exposure | **Fail closed**: exclude the document from results |
| No relevant documents found | Risk of hallucination | Say that no supported answer was found; suggest sources |
| Answer cites a document incorrectly | Loss of trust | Citation validation (cited IDs must be in the retrieved set) **[Assumption]**; user feedback captured |
| Quota exhausted | Requests rejected | Clear quota error to the app; FinOps alert to the tenant |

### 4.7 Proposed Success Metrics

These are **[Target]** metrics. Their values are **[Open]**.

| Metric | Definition (draft) |
|---|---|
| Unauthorized document exposure | Count of answers citing documents the user cannot access. **Expected target: zero** (proposed) |
| Citation coverage | Percentage of answers that include at least one valid citation |
| Answer helpfulness | Percentage of rated answers marked helpful |
| End-to-end latency | p95 latency from question to answer |
| Cost per answer | Average attributed tokens and cost per query |

### 4.8 Acceptance Criteria

| ID | Criterion | Traces to |
|---|---|---|
| UC-KA-AC1 | Retrieval returns only documents the requesting user can access in the source system, verified by tests with users of different permissions | AC-11, AC-08 |
| UC-KA-AC2 | Every answer derived from retrieved content includes citations that resolve to source documents in the retrieved set | G5 |
| UC-KA-AC3 | Documents with missing or unresolvable ACLs are not retrievable | AC-11 |
| UC-KA-AC4 | Each query produces a trace that links retrieval and generation, plus a tenant-attributed usage record | AC-06, AC-12 |
| UC-KA-AC5 | The assistant team builds on platform RAG and gateway APIs without deploying its own vector store or gateway | AC-02, G1 |
| UC-KA-AC6 | When retrieval or the model is unavailable, the assistant returns an explicit error, never an ungrounded answer | G3 |

### 4.9 Assumptions and Open Questions

- **UC-KA-A1 [Assumption]:** Source systems expose ACLs that the platform can read and map to enterprise identities.
- **UC-KA-A2 [Assumption]:** Filtering by ACL at retrieval time is feasible within acceptable latency.
- **UC-KA-A3 [Assumption]:** Initial sources can be limited to low-sensitivity corpora (stakeholders SR4).
- **UC-KA-Q1 [Open]:** Which source systems are in scope first?
- **UC-KA-Q2 [Open]:** What is the maximum acceptable lag for permission revocation?
- **UC-KA-Q3 [Open]:** Is conversation history retained, and for how long?
- **UC-KA-Q4 [Open]:** Who evaluates answer quality, and how? Options include offline eval sets and human review.

---

## 5. UC-OA: AI Operations Agent

### 5.1 Business Problem and Personas

**Problem [Assumption]:** Operators and SREs spend significant time on repetitive diagnosis and remediation across many systems. An agent could gather diagnostics and propose or perform remediations. However, an agent with broad tool access poses serious risk if its permissions are not scoped and its actions are not approved and audited.

**Personas [Assumption]:**

| Persona | Description | Goal |
|---|---|---|
| Operator / on-call engineer | Uses the agent during incidents or routine ops | Faster diagnosis; safe, approved remediation |
| Approver (S05 or a delegated service owner) | Approves sensitive actions | Sees exactly what will happen and why before approving |
| Agent developer (S01) | Builds the agent's graph and tools | Composes orchestration, MCP, and approvals from platform primitives |
| Auditor / Security (S05) | Reviews agent activity | Has a complete, tamper-evident record of agent decisions and actions |

### 5.2 Trigger and Workflow

**Triggers:** An operator request, such as "why is service X degraded?", or an alert or event delivered to the agent **[Assumption]**. **[Open]** Are autonomous, alert-triggered runs allowed?

**Workflow:**

1. **Start the run.** The trigger starts an agent run in the platform orchestration runtime. The run carries the initiating identity, which is a user or service, plus the tenant.
2. **Plan.** The graph's planning node calls the LLM through the gateway to decide which tools to call next.
3. **Read-only tools.** Diagnostic tools are invoked through **MCP** with credentials **scoped** to the agent's role and tenant. Examples are log queries, metrics, and configuration reads.
4. **State.** The agent stores intermediate state and checkpoints in the orchestration runtime, so runs can be resumed and inspected.
5. **Propose an action.** If a remediation is warranted, the agent drafts an action, such as a restart, scale, rollback, or config change, with its rationale and expected impact.
6. **Approval gate.** Actions classified as **sensitive** pause the run and create an approval request **[Decision]**. The approver sees the action, its parameters, the evidence, and the trace.
7. **Execute.** On approval, the action executes through MCP using a scoped, short-lived credential. On rejection or timeout, the run ends without acting.
8. **Report.** The agent reports the outcome to the operator.
9. **Audit.** Every step is recorded in the audit trail **[Decision]**: LLM calls, tool calls, approvals, and results.

### 5.3 Platform Capabilities and Dependencies

| Capability | Use | Owner |
|---|---|---|
| Agent orchestration (graph-based, stateful, checkpointed) | Executes the agent graph; pause and resume for approval | Platform runtime; app owns the graph |
| MCP | Tool hosting and registry; authenticated tool invocation | Platform hosts; app or operations teams build domain tools **[Assumption]** |
| Identity / authorization | Agent service identity; per-tool scopes; user delegation | Platform + Security |
| Approval workflow | Pause, notify, approve or reject, timeout | Platform; Security defines policy |
| Audit logging | Immutable record of decisions and actions | Platform; Security defines retention |
| LLM gateway | Planning and reasoning calls | Platform |
| Observability | Run-level traces across LLM and tool calls | Platform |
| FinOps | Attribution per run and per tenant | Platform |

**Dependencies:** VS; D1, D3, D5; definition of sensitive operations (SQ3); operational systems exposing APIs that MCP servers can wrap (SQ6).

**Framework [Open]:** "LangGraph-style" means graph-based, stateful orchestration with checkpoints and human-in-the-loop interrupts. Whether the platform adopts LangGraph itself or an equivalent is undecided.

### 5.4 Data Inputs and Outputs

| Direction | Data | Notes |
|---|---|---|
| Input | Operator request or alert payload | May include incident details |
| Input | Tool results (logs, metrics, configs) | May contain secrets or personal data in logs. **[Open]** Redaction approach |
| Output | Diagnosis summary, proposed actions | Shown to the operator |
| Output | Executed actions on target systems | Change to production state |
| Output | Approval records, audit trail, traces, usage | Retained per audit policy **[Open]** |

### 5.5 Security and Tenant-Isolation Requirements

- **Scoped authorization [Decision]:**
  - Each tool call uses the minimum permission needed.
  - Read and write tools are separately scoped.
  - Credentials are short-lived **[Assumption]**.
- **Human approval for sensitive operations [Decision]:**
  - The agent cannot execute a sensitive operation without a recorded approval (AC-10).
  - The approver must not be the agent itself.
  - **[Open]** Whether the initiating operator may self-approve.
- **No privilege escalation:** The agent cannot act with more privilege than the lesser of its own role and the initiating user's role **[Assumption]**.
- **Tenant isolation:** An agent can invoke only MCP tools registered to, or explicitly shared with, its tenant. It cannot target another tenant's resources (AC-08).
- **Audit trails [Decision]:** Each run records the initiator, the LLM inputs and outputs (or their hashes, per data policy), the tool calls with parameters, approvals (who and when), and outcomes. The audit trail is tamper-evident **[Assumption]** (AC-09).
- **Prompt injection via tool output:** Tool results are untrusted input. A sensitive action is never approved implicitly because of content returned by a tool **[Assumption]**.
- **Kill switch:** Security or the platform can disable an agent or a tool immediately **[Assumption]**.

### 5.6 Failure Modes and Fallback

| Failure | Impact | Fallback behavior |
|---|---|---|
| LLM unavailable mid-run | Run stalls | Checkpoint the state; resume or fail the run cleanly; tell the operator |
| Tool call fails or times out | Incomplete diagnosis | Retry with limits; report partial findings; never guess the results |
| Approval not given within the timeout | Action pending | Expire the request; take no action; tell the operator **[Assumption]** |
| Agent proposes an incorrect or harmful action | Production risk | Approval gate; policy checks on action parameters; dry-run where supported **[Assumption]** |
| Agent loops or exceeds its budget | Cost or rate exhaustion | Step and token limits per run; terminate and report |
| Audit log write fails | Loss of accountability | **Fail closed**: block sensitive actions while auditing is unavailable |
| Action partially succeeds | Inconsistent state | Report the exact state; rollback where the tool supports it **[Assumption]** |

### 5.7 Proposed Success Metrics

These are **[Target]** metrics. Their values are **[Open]**.

| Metric | Definition (draft) |
|---|---|
| Unapproved sensitive actions | Count of sensitive actions executed without approval. **Expected target: zero** (proposed) |
| Audit completeness | Percentage of runs with a complete audit trail |
| Diagnosis usefulness | Percentage of runs that operators rate useful |
| Time to diagnosis | Time from trigger to diagnosis summary. **[Open]** No baseline exists for comparison |
| Approval turnaround | Time from approval request to decision |
| Cost per run | Attributed LLM and tool cost per run |

### 5.8 Acceptance Criteria

| ID | Criterion | Traces to |
|---|---|---|
| UC-OA-AC1 | A sensitive action cannot execute without a recorded approval from an authorized approver (verified by negative tests) | AC-10 |
| UC-OA-AC2 | Each MCP tool call is authorized against a scope bound to the agent's identity and tenant; out-of-scope calls are denied and logged | AC-07, AC-08 |
| UC-OA-AC3 | Each run produces an audit trail containing the initiator, the tool calls, approvals, and outcomes | AC-09 |
| UC-OA-AC4 | A run paused for approval can be resumed or terminated without losing state | G6 |
| UC-OA-AC5 | Per-run step and token limits stop runaway runs | AC-12, G4 |
| UC-OA-AC6 | An agent or tool can be disabled immediately by an authorized platform or security role | G3 |
| UC-OA-AC7 | Run traces link LLM calls, tool calls, and approvals under a single trace ID | AC-06 |

### 5.9 Assumptions and Open Questions

- **UC-OA-A1 [Assumption]:** Target operational systems have APIs that can be safely wrapped as MCP tools with fine-grained scopes.
- **UC-OA-A2 [Assumption]:** The first release can be limited to read-only diagnostics plus a small set of approved remediations.
- **UC-OA-A3 [Assumption]:** Approvers are available within incident timeframes.
- **UC-OA-Q1 [Open]:** What actions count as "sensitive"? (SQ3)
- **UC-OA-Q2 [Open]:** May the initiating operator approve their own request?
- **UC-OA-Q3 [Open]:** Are autonomous, alert-triggered runs allowed, or must a human always initiate?
- **UC-OA-Q4 [Open]:** Will the platform use LangGraph itself, or an equivalent orchestration framework?
- **UC-OA-Q5 [Open]:** Who builds and owns MCP servers for shared operational systems? (stakeholders §3 grey areas)

---

## 6. UC-PM: Predictive Maintenance

### 6.1 Business Problem and Personas

**Problem [Assumption]:** Unplanned equipment or infrastructure failures cause downtime and costly reactive repairs. Models trained on telemetry could predict failures early enough to schedule maintenance. Teams that build such models today may run bespoke training, deployment, and monitoring stacks (vision §2.1).

**[Open]:** What assets are maintained? Examples include physical equipment, data-center hardware, and fleet devices. The domain affects data sources and latency requirements.

**Personas [Assumption]:**

| Persona | Description | Goal |
|---|---|---|
| ML engineer (S02) | Builds and maintains failure-prediction models | A standard path from features to training to registry to serving to monitoring |
| Data engineer (S06) | Provides telemetry and maintenance-history pipelines | Reliable, governed feature data |
| Maintenance planner / operator | Consumes predictions | Timely, trustworthy risk scores to schedule work |

### 6.2 Trigger and Workflow

**Triggers:**

- **Training:** scheduled retraining, or retraining triggered by drift.
- **Inference:** batch scoring on a schedule, or online scoring on new telemetry. **[Open]** Which modes are required?

**Workflow:**

1. **Features.** Telemetry and maintenance history are ingested by data pipelines. Feature pipelines compute features and store them for training and serving **[Assumption]**: a feature store is needed.
2. **Training.** The ML engineer launches training on platform compute (Kubernetes; GPU or CPU as needed). Experiments, parameters, and metrics are tracked.
3. **Evaluation.** The candidate model is evaluated against holdout data and the current production model.
4. **Registration.** The model is registered in the **model registry** with lineage: data version, code version, metrics.
5. **Promotion.** Promotion to production follows a defined path, such as staging → production. **[Open]** Who approves?
6. **Deployment.** The model is deployed as a batch job or an online endpoint.
7. **Prediction.** Predictions, meaning risk scores per asset, are delivered to downstream maintenance systems. Those systems are owned by the application team.
8. **Monitoring.** The model is monitored for service health, prediction distribution, and **data/concept drift**.
9. **Retraining.** Drift beyond a threshold raises an alert and/or triggers retraining. The new candidate goes through steps 3–6 again.

### 6.3 Platform Capabilities and Dependencies

| Capability | Use | Owner |
|---|---|---|
| Feature pipelines | Feature computation and storage | Platform framework; app owns feature logic |
| ML training | Compute and job orchestration; experiment tracking | Platform |
| Model registry | Versioning, lineage, promotion states | Platform |
| Deployment | Batch and/or online serving | Platform |
| Monitoring and drift detection | Health, data drift, prediction drift, alerts | Platform framework; app sets thresholds |
| Kubernetes | Compute substrate | Platform |
| Identity / authorization | Access to data, registry, and endpoints | Platform + Security |
| FinOps | Attribution of training and serving compute | Platform |

**LLM gateway:** UC-PM does not depend on it for its core workflow **[Assumption]**. This makes UC-PM the main test of vision goal G6 for non-LLM workloads.

**Dependencies:** D1, D6, D8; telemetry sources; compute availability (including GPU) **[Open]**.

### 6.4 Data Inputs and Outputs

| Direction | Data | Notes |
|---|---|---|
| Input | Sensor and telemetry time series | **[Open]** Volume, frequency, and source systems |
| Input | Maintenance and failure history (labels) | **[Assumption]** Enough labelled failure events exist |
| Output | Trained model artifacts with lineage metadata | Stored in the registry |
| Output | Risk scores or failure predictions per asset | Consumed by maintenance systems |
| Output | Monitoring metrics and drift reports | Visible to the owning tenant |

### 6.5 Security and Tenant-Isolation Requirements

- **Tenant isolation:** Each tenant's training data, features, registry entries, models, and endpoints are accessible only to that tenant unless explicitly shared (AC-08).
- **Least privilege:** Training jobs read only the datasets granted to them. Serving endpoints require authenticated callers (AC-07).
- **Promotion control:** Promoting a model to production is an auditable action. **[Open]** Is it a "sensitive operation" requiring approval?
- **Lineage and audit:** It must be possible to trace each production model back to its data, code, and approver (AC-09).
- **Compute isolation:** Tenant workloads run in isolated namespaces with resource quotas **[Assumption]**.

### 6.6 Failure Modes and Fallback

| Failure | Impact | Fallback behavior |
|---|---|---|
| Serving endpoint unavailable | No new predictions | Downstream systems fall back to the last known scores or to rule-based thresholds and scheduled maintenance **[Assumption]** |
| Telemetry pipeline delayed or broken | Stale or missing features | Flag predictions as stale; do not score on incomplete features; alert |
| Drift detected | Degraded accuracy | Alert the owners; trigger retraining; optionally roll back to the previous model version |
| Training job fails | No new model | Keep the current production model; alert the ML engineer |
| Regressed model promoted | Bad predictions | Evaluation gate before promotion; rollback through the registry |
| Insufficient compute or GPU | Training delayed | Queue with priority; quotas per tenant **[Open]** |

### 6.7 Proposed Success Metrics

These are **[Target]** metrics. Their values are **[Open]**.

| Metric | Definition (draft) |
|---|---|
| Model quality | Precision and recall (or a domain-appropriate metric) for failure prediction on holdout data |
| Lead time | How far before a failure a correct prediction is issued |
| Drift detection time | Time from drift onset to alert |
| Time to production | Time from model registration to production deployment via the platform pipeline |
| Rollback time | Time to restore the previous model version |
| Compute cost attribution | Percentage of training and serving cost attributed to the tenant |

### 6.8 Acceptance Criteria

| ID | Criterion | Traces to |
|---|---|---|
| UC-PM-AC1 | A model can be trained, registered with lineage, deployed, and monitored using platform services only | AC-03, G6 |
| UC-PM-AC2 | Drift beyond a configured threshold produces an alert to the owning tenant | AC-03, G5 |
| UC-PM-AC3 | A production model can be rolled back to a previous registry version | AC-03 |
| UC-PM-AC4 | Each production model is traceable to its data version, code version, metrics, and promoter | AC-09 |
| UC-PM-AC5 | Tenant data, models, and endpoints are inaccessible to other tenants | AC-08 |
| UC-PM-AC6 | Training and serving compute is attributed to the tenant | AC-12 |

### 6.9 Assumptions and Open Questions

- **UC-PM-A1 [Assumption]:** Sufficient historical failure data exists to train useful models.
- **UC-PM-A2 [Assumption]:** Kubernetes-based training and serving meets the workload's compute needs (vision A5).
- **UC-PM-A3 [Assumption]:** A feature store is required. Plain pipelines into storage may suffice for the first release.
- **UC-PM-Q1 [Open]:** What asset domain is this, and what are the telemetry sources?
- **UC-PM-Q2 [Open]:** Is the workload batch, online, or both? What latency is required?
- **UC-PM-Q3 [Open]:** Who approves promotion to production?
- **UC-PM-Q4 [Open]:** Is GPU compute required?

---

## 7. Comparative Workload Matrix

The capability rows are **[Decision]** where they appear in the established workload definitions. The rest of the matrix is **[Assumption]**.

**Key:**

- ● core requirement
- ◐ supporting requirement
- ○ not required (or minimal)

| Dimension | VS | UC-KA | UC-OA | UC-PM |
|---|---|---|---|---|
| Developer onboarding / self-service | ● | ● | ● | ● |
| Identity / AuthN / AuthZ | ● | ● (end-user propagation) | ● (scoped tool auth) | ● |
| LLM gateway | ● | ● | ● | ○ |
| RAG | ○ | ● | ◐ (runbook lookup, optional) | ○ |
| Agent orchestration | ○ | ○ | ● | ○ |
| MCP | ○ | ○ | ● | ○ |
| Human approval workflow | ○ | ○ | ● | ◐ (model promotion, **[Open]**) |
| MLOps (training, registry, serving, drift) | ○ | ○ | ○ | ● |
| Observability / tracing | ● | ● | ● | ● |
| Audit trail | ◐ | ● | ● (critical) | ● |
| FinOps attribution | ● | ● | ● | ● |
| Kubernetes | ● | ● | ● | ● (heavy compute) |
| Primary risk | Onboarding friction | Unauthorized document exposure | Unsafe autonomous action | Silent model degradation |
| Writes to production systems? | No | No | **Yes** | Indirect (predictions) |
| Data sensitivity | Low–Medium **[Open]** | Medium–High **[Open]** | High (operational access) | Medium **[Open]** |
| Main stakeholders | S01, S05, S07 | S01, S05, S06 | S01, S04, S05 | S02, S06, S04 |
| Vision goals exercised | G2, G3, G4, G5 | G1, G3, G5 | G3, G5, G6 | G1, G6 |

---

## 8. Prioritization Rationale

The order below is **[Assumption]**. It is a proposal for review, not an approved roadmap.

| Order | Item | Rationale |
|---|---|---|
| 1 | **VS: First vertical slice** | **[Decision]** It is the foundation for UC-KA and UC-OA. It proves onboarding, identity, gateway, and attribution: the controls every later workload inherits. It exercises all three established targets (onboarding time, adoption readiness, gateway availability). |
| 2 | **UC-KA: Enterprise knowledge assistant** | Adds the fewest new capabilities to the slice (RAG + citations). Read-only, so lower operational risk than UC-OA. Validates document-level access control early, which is a high-value security control (C9). Likely broad applicability across teams **[Assumption]**. |
| 3 | **UC-OA: AI operations agent** | Needs the most new security machinery (scoped MCP authorization, approval workflow, tamper-evident audit). Writes to production, so it should build on proven identity, gateway, and audit foundations. Can start read-only (UC-OA-A2) before enabling approved remediations. |
| 4 | **UC-PM: Predictive maintenance** | Uses a largely separate capability set (MLOps) with little reuse from the LLM path. It is still essential to proving G6. **[Open]** It could run in parallel with UC-KA or UC-OA if separate platform capacity exists (stakeholders SR6). |

**Factors that could change this order, all [Open]:**

- business urgency of a particular workload;
- readiness of the workload's owning team (vision Q9);
- availability of data owners (SR4);
- Security's definition of sensitive operations (SQ3).

---

## 9. Cross-Workload Open Questions

| ID | Question | Related |
|---|---|---|
| UC-Q1 | Which teams own each workload, and have they committed as early adopters? | vision Q9, SQ1 |
| UC-Q2 | What data classifications are permitted for each workload? | vision Q6, SQ5 |
| UC-Q3 | What is the shared definition of "sensitive operation" across UC-OA (actions) and UC-PM (promotion)? | SQ3 |
| UC-Q4 | Is prompt and response content stored in traces, and with what redaction and retention? | SQ8, C6 |
| UC-Q5 | Will the three workloads share one platform environment from the start, or begin in separate early-adopter environments? | vision R4 |
| UC-Q6 | How will workload-level quality metrics be evaluated, and who owns them? | stakeholders §3 grey areas |

---

## 10. Traceability Summary

| Stakeholder AC (`stakeholders.md`) | Covered by |
|---|---|
| AC-01 (onboarding < 30 min) | VS-AC1, VS-AC2 |
| AC-02 (single gateway API) | UC-KA-AC5 |
| AC-03 (MLOps pipeline) | UC-PM-AC1, AC2, AC3 |
| AC-05 (gateway 99.9%) | VS-AC6 |
| AC-06 (incident attribution via traces) | VS-AC5, UC-KA-AC4, UC-OA-AC7 |
| AC-07 (identity and least privilege) | VS-AC3, UC-OA-AC2 |
| AC-08 (tenant isolation) | VS-AC4, UC-KA-AC1, UC-OA-AC2, UC-PM-AC5 |
| AC-09 (audit logging) | VS-AC3, UC-OA-AC3, UC-PM-AC4 |
| AC-10 (approval for sensitive ops) | UC-OA-AC1 |
| AC-11 (RAG honors source ACLs) | UC-KA-AC1, UC-KA-AC3 |
| AC-12 (usage attribution) | VS-AC5, UC-OA-AC5, UC-PM-AC6 |

AC-04, AC-13, and AC-14 (adoption, architecture review, leadership reporting) are platform-level criteria. No single workload covers them. They will be covered in `success-metrics.md` and later architecture work. The full cross-document check is in `coverage-audit.md`.
