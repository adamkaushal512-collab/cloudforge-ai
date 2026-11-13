# CloudForge AI: Architecture Tradeoffs, Risks, and Validation

| Field | Value |
|---|---|
| Document | Architecture Tradeoffs |
| Phase | 02: Enterprise AI Architecture |
| Status | Proposed. No validation performed. |

---

## 1. ADR Register

| ADR | Title | Status | Decision (summary) |
|---|---|---|---|
| 001 | Centralized LLM gateway | **Proposed** | All model traffic passes through one multi-tenant gateway that owns authN/authZ, quotas, routing, and metering. LiteLLM is a candidate implementation aid. |
| 002 | Control-plane / data-plane separation | **Proposed** | The data plane runs on signed config snapshots, with bounded staleness and no synchronous control-plane dependency. |
| 003 | Hybrid tenant isolation | **Proposed** | Pooled by default; siloed resources for the Restricted tier. |
| 004 | Managed-first model serving | **Proposed** | Bedrock first; vLLM on EKS only when criteria are met. |
| 005 | AI integration boundaries | **Proposed** | One owner per responsibility. LangGraph owns agent runs; Temporal owns platform workflows. Gateway-only model access; broker-only tool access. |

**None of these ADRs is Accepted.**

---

## 2. Key Tradeoffs

| # | Tradeoff | Chosen direction | Cost of the choice | Phase 1 link |
|---|---|---|---|---|
| TO-1 | Central gateway vs per-team SDK access | Central gateway | A potential single point of failure and an extra network hop | C4, R2 |
| TO-2 | Live config lookups vs cached snapshots | Snapshots | Bounded staleness, so revocation is delayed by up to the staleness window | NFR-025, NFR-043 |
| TO-3 | Pooled vs siloed tenancy | Hybrid | Two operating models to maintain | C3 |
| TO-4 | Managed vs self-hosted models | Managed first | Bedrock quotas, model availability, and per-token cost at high volume | R7, vision Q5 |
| TO-5 | Build vs adopt a gateway framework (LiteLLM) | Undecided; evaluate | Adopting risks loss of control; building costs effort | ADR-001 |
| TO-6 | One durable engine vs LangGraph + Temporal | Two engines with strict ownership | Two technologies to operate | FR-042, SA5 |
| TO-7 | Rate-limit store failure: fail closed vs open | **[Open]** (AR-Q8) | Availability vs spend control | NFR-043 |
| TO-8 | Audit outage blocks all inference vs sensitive operations only | **[Open]** (NFR-Q8) | Availability vs assurance | FR-073 |
| TO-9 | OpenSearch (managed) vs a dedicated vector DB | OpenSearch | May be less specialized for vector workloads; ACL-filter performance unverified | UC-KA-A2 |

---

## 3. Architecture Risks

All risks are unassessed: likelihood and impact are **[Open]**.

| ID | Risk | Mitigation | Validation |
|---|---|---|---|
| ARR-1 | The gateway misses p95 < 200 ms **[Target]** | Local authN/authZ, async telemetry | NFR-013 load test (not run) |
| ARR-2 | Bedrock quotas are insufficient for peak or noisy tenants | Quota partitioning, provisioned throughput, failover | Quota review; load test with simulated limits |
| ARR-3 | Snapshot staleness allows revoked credentials | Short staleness cap; fail closed past the cap | Revocation timing test |
| ARR-4 | Pooled OpenSearch leaks across tenants through a query bug | Server-side index selection; negative tests | Cross-tenant suite |
| ARR-5 | Two orchestration engines increase operating load for a small team | Defer Temporal until UC-KA; consider Temporal Cloud | Capacity review (SR6) |
| ARR-6 | LiteLLM adoption introduces supply-chain or behavioral risk | Evaluation criteria (`llm-gateway-model-serving.md` §5) | Spike + security review |
| ARR-7 | MLflow lacks native multi-tenancy | Authorization proxy, or an instance per tenant | Spike (AR-Q19) |
| ARR-8 | GPU capacity is unavailable for vLLM | Managed-first; vLLM optional | n/a until triggered |
| ARR-9 | Phase 2 scope is misaligned with the undocumented 18-phase roadmap | Add the roadmap to the repository | Roadmap review |

---

## 4. Validation Plan

All items below are planned. **No item has been executed.**

| ID | Validation | Validates | Exit criterion |
|---|---|---|---|
| V-1 | Gateway prototype + load test (mock provider, 100 concurrent) | ADR-001, ADR-002, NFR-007, NFR-013 | p95 gateway-added < 200 ms; error rate < 0.1% **[Target]** |
| V-2 | Control-plane outage fault injection | ADR-002 | Data plane serves on the snapshot; fails closed past the staleness cap |
| V-3 | Cross-tenant isolation suite on a pooled cluster | ADR-003, SEC-036 | 0 unexpected allows **[Target]** |
| V-4 | Bedrock integration spike via PrivateLink, IAM-only | ADR-004 | Inference and embeddings work with no static keys; quotas documented |
| V-5 | LiteLLM evaluation against the criteria | ADR-001 (TO-5) | Written evaluation; decision recorded |
| V-6 | OpenSearch ACL-filtered retrieval spike | ADR-005, NFR-011 | Zero leakage; latency recorded (target **[Open]**) |
| V-7 | LangGraph interrupt/resume with the approval service | ADR-005, FR-042, SEC-050 | Resume without repeated tool calls; no execution without approval |
| V-8 | Architecture review by EA and Security | All ADRs; Phase 1 AC-13 | ADRs moved to Accepted or revised |
