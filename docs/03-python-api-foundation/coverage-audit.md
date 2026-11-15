# CloudForge AI: Phase 3 Coverage Audit

| Field | Value |
|---|---|
| Document | Phase 3 Coverage Audit and Completion Record |
| Phase | 03: Python API Foundation |
| Audit date | 2026-11-15 |
| Auditor | Implementing author (self-audit). **Not an independent review.** |
| Baseline | `main` at `f8a0000` (PRs #2, #3, #4 merged) plus the Phase 3.8 changes in this branch |

---

## 1. Method and Limits

**Method:**

- Every claim below was checked against the repository at the baseline commit: source files, test files, `pyproject.toml`, and `.github/workflows/tests.yml`.
- Test results come from local runs and from GitHub Actions run logs.
- Database isolation was checked by snapshotting the development database (`ai_models` count and max id, `idempotency_records` count) before and after the test runs.

**Limits:**

- Local runs used macOS, Python 3.12.16, and PostgreSQL 17.12.
- CI runs on `ubuntu-latest`, Python 3.12, and PostgreSQL 17.
- No load, soak, or multi-replica testing was performed.
- No security review by a third party has taken place.

---

## 2. Architecture and Implemented Components

```
HTTP ─▶ FastAPI app (src/cloudforge/main.py)
          ├─ Pydantic schemas ............ api/schemas.py
          ├─ Auth dependency (simulated) . api/auth.py ─▶ core/security.py (principal, require_role)
          ├─ DB session per request ...... api/dependencies.py ─▶ core/database.py (engine, SessionLocal)
          ├─ Repositories ................ repositories/model_repository.py
          │                                repositories/idempotency_repository.py
          │                                repositories/models.py (AIModel, IdempotencyRecord)
          └─ Services .................... services/idempotency.py (key validation, SHA-256 hash)
                                           services/ai_provider.py (timeout, retry; not yet wired to an endpoint)
PostgreSQL ─ tables: ai_models, idempotency_records
```

| Concern | Implementation |
|---|---|
| Transactions | The caller owns the transaction. Repositories `flush()`, and endpoints `commit()` or `rollback()`. |
| Session lifecycle | One `Session` per request, from the `get_db` generator. Closing it rolls back any uncommitted work. |
| Tenant context | Always taken from the authenticated principal, never from the request body. |
| Configuration | `DATABASE_URL` environment variable. The default is local `cloudforge_db`, intended for development only. |

### Endpoints

| Method and path | Status | Behavior |
|---|---|---|
| `GET /health` | 200 | `{"status": "healthy"}` |
| `POST /v1/models` | 201 | Validates the body and requires the role `model-admin` or `platform-admin` (otherwise 403). Persists the model under the principal's tenant. Accepts an optional `Idempotency-Key` header. |
| `GET /v1/inference/demo` | 200 | Async demo endpoint. Awaits a simulated 2 s of latency and calls no real provider. |
| `POST /v1/jobs/demo` | 202 | Schedules `process_demo_job` through FastAPI `BackgroundTasks`. |

### Persistence

| Table | Key columns | Constraints |
|---|---|---|
| `ai_models` | `tenant_id`, `model_name`, `provider`, `max_tokens` | Primary key only |
| `idempotency_records` | `tenant_id`, `operation`, `idempotency_key`, `request_hash`, `response_body` (JSON), `status_code` | `UNIQUE (tenant_id, operation, idempotency_key)` |

There are **no migrations.** The tables are defined in SQLAlchemy models. The test suite creates them with `Base.metadata.create_all`.

---

## 3. Authentication Simulation — Limitations

- **JWT/OIDC is not implemented.** `get_current_principal` returns a hardcoded principal: `alice`, `tenant-retail`, `("model-admin",)`.
- **RBAC is real application logic over simulated identity.**
  - `require_role` matches roles exactly.
  - The endpoint returns 403 `{"detail": "Insufficient permissions"}` before any database write.
- **401 is unreachable over HTTP.** The code path exists, but the hardcoded principal is never empty, so it cannot trigger.
- **Tests do not exercise real identity.** They swap the dependency through `app.dependency_overrides`, using test-only headers (`X-Test-Tenant`, `X-Test-Roles`). These headers are **not** read by the application.

---

## 4. Async Operations and Background Jobs

- `GET /v1/inference/demo` does not block the event loop. A test verifies that 5 concurrent requests are all waiting at the same moment.
- `BackgroundTasks` run **in the same process, after the response is sent.** They are **not a durable or distributed queue**:
  - work is lost on a crash or restart;
  - nothing retries a failed job;
  - jobs have no visibility and are not shared across workers.
- Job output uses `print`; there is no structured logging.

---

## 5. Reliability and Idempotency

| Mechanism | Behavior |
|---|---|
| `execute_with_timeout` | Wraps a call in `asyncio.wait_for`. On timeout, the call is cancelled and the wrapper raises `AIProviderTimeoutError`, which is retryable. |
| `execute_with_retry` | Retries only `AIProviderTemporaryError` and its subclasses. Bounded attempts; exponential backoff capped at `max_delay`; full jitter. Re-raises the last error once attempts run out. Other errors propagate on the first attempt. |
| Idempotency key | Optional `Idempotency-Key` header: 1–255 characters, `[A-Za-z0-9._:-]`. An invalid key returns 400 `invalid_idempotency_key`. |
| Request hash | SHA-256 of the validated payload, serialized as canonical JSON. |
| New key | Reserve the key, create the model, and store the response in **one transaction**. |
| Same key, same payload | Replays the stored 201 response with `Idempotent-Replayed: true`. No new model is created. |
| Same key, different payload | 409 `idempotency_key_conflict` |
| Concurrent duplicates | `INSERT … ON CONFLICT DO NOTHING` on the unique constraint. The second request waits until the first commits (it then replays) or rolls back (it then takes over the key). A placeholder is never returned. |

The timeout and retry wrappers are tested, but **no endpoint uses them yet**. No real AI provider is integrated; `integrations/` is empty.

---

## 6. Testing, Coverage, and CI

| Metric | Value (local, 2026-11-15) |
|---|---|
| Tests collected and passed | **118 passed**, 0 failed |
| Test categories | `unit` 51 · `api` 54 · `integration` 61. Some tests carry more than one marker. |
| Coverage (statements and branches) | **98.39%**: 218 statements with 2 missed; 30 branches with 2 partial |
| Configured threshold | 90%, enforced in CI with `--cov-fail-under=90` |
| Uncovered lines | `api/auth.py:22` (the unreachable dev 401) and `services/ai_provider.py:79` (an unreachable guard after the retry loop) |
| Remaining warning | 1 Starlette deprecation notice: `httpx` with `TestClient` |

**Test database isolation:**

- `tests/conftest.py` replaces `DATABASE_URL` with `TEST_DATABASE_URL` (default `cloudforge_test`) before the engine is created.
- The run aborts unless the database name contains `test`.
- All test rows use `pytest-` tenants and are deleted after each test, with an extra sweep at session start and end.

**Verified on 2026-11-15:**

- The development database was unchanged: 5 models, max id 6, 0 idempotency records, both before and after the runs.
- The test database had 0 rows left over.
- The concurrency, blocking, rollback, and async-overlap tests passed in 15 consecutive repeated runs (Phase 3.7).

**GitHub Actions** (`.github/workflows/tests.yml`):

- Triggers: `pull_request` and pushes to `main`.
- Environment: Python 3.12 and a `postgres:17` service with throwaway credentials. No repository secrets are needed.
- Steps: `pip install -e ".[dev]"`, `compileall`, then pytest with coverage (term, HTML, and XML) and a 90% gate.
- The `htmlcov/` directory is uploaded as the `coverage-html` artifact.
- Observed runs:
  - `43672013103`: PR #4, success.
  - `43672103542`: push to `main` `f8a0000`, success, 118 passed, 98.39%.

`main` has **no branch protection**, so CI is not yet a required check.

Local commands are listed in `tests/README.md`.

---

## 7. Phase 3 Steps 3.1–3.8 → Evidence

| Step | Topic | Files | Tests | Status |
|---|---|---|---|---|
| 3.1 | Project structure and dependencies | `pyproject.toml` (hatchling; Python `>=3.12,<3.13`; FastAPI, SQLAlchemy 2, psycopg 3, Pydantic 2, uvicorn; dev: pytest, pytest-cov, httpx); `src/cloudforge/{api,core,repositories,services,integrations}` | Whole suite imports the package | Complete |
| 3.2 | FastAPI endpoints and Pydantic validation | `main.py`; `api/schemas.py` | `tests/api/test_models_api.py` | Complete |
| 3.3 | PostgreSQL persistence and repositories | `core/database.py`; `api/dependencies.py`; `repositories/models.py`; `repositories/model_repository.py` | `tests/integration/test_model_repository.py` | Complete; **no migrations** |
| 3.4 | Authentication-aware design and simulated RBAC | `api/auth.py`; `core/security.py`; role check in `main.py` | `tests/api/test_auth_rbac.py`; `tests/unit/test_security.py`; `tests/api/test_tenant_isolation.py` | Complete as a **simulation**; JWT/OIDC not implemented |
| 3.5 | Async operations and background jobs | `main.py` (`/v1/inference/demo`, `/v1/jobs/demo`, `process_demo_job`) | `tests/api/test_async_and_background.py` | Complete as demos; **no durable queue** |
| 3.6 | Timeout, retry, backoff, persistent idempotency | `services/ai_provider.py`; `services/idempotency.py`; `repositories/idempotency_repository.py`; `main.py` | `tests/unit/test_ai_provider.py`; `tests/unit/test_idempotency_helpers.py`; `tests/integration/test_idempotency_repository.py`; `tests/api/test_idempotency_api.py` | Complete; wrappers not yet wired to a real provider |
| 3.7 | Unit, integration, tenant isolation tests, and CI | `tests/conftest.py`; `tests/{unit,api,integration}/`; `tests/README.md`; `.github/workflows/tests.yml` | 118 tests; CI green | Complete |
| 3.8 | Final GitHub delivery and verification | This document; `scripts/` (manual smoke scripts made opt-in) | Full local and CI verification | Complete once the Phase 3.8 PR is merged |

### Delivery history

| PR | Content | Base | State | Merge commit |
|---|---|---|---|---|
| #2 | 3.1–3.3 FastAPI and PostgreSQL foundation | `main` | Merged 2026-11-14 | `e6da0b8` |
| #3 | 3.4–3.6 auth simulation, async demos, reliability, idempotency | `main` | Merged 2026-11-15 | `393064e` |
| #4 | 3.7 testing and CI | `main` | Merged 2026-11-15 | `f8a0000` |

PR #2 was merged before Phases 3.4–3.7 existed, and its head branch `phase-3-python-api-foundation` was later deleted. Phases 3.6 and 3.7 were therefore delivered directly to `main`, which serves as the Phase 3 integration branch. PR #2 has no CI checks because the workflow did not exist when it merged.

### Phase 3.8 review findings

| Finding | Severity | Resolution |
|---|---|---|
| Root-level `test_db_insert.py` and `test_repository.py` committed rows to the **development** database when executed, including when invoked through `pytest <file>`, which bypasses the test database guard. | Medium (data safety) | Moved to `scripts/dev_smoke_insert.py` and `scripts/dev_smoke_repository.py`. They now run only through `main()`, require `--confirm-dev-write`, and print the target URL with the password hidden. Their behavior is otherwise unchanged. |
| No secrets in Git history; no tracked caches, coverage files, or `.env` files | n/a | Verified with a history scan |
| `pip check` | n/a | No broken requirements |

---

## 8. Known Production Limitations

1. **Identity.** No JWT/OIDC, token validation, or tenant-membership lookup. The principal is hardcoded.
2. **Tenant isolation is application-level only.** There is no PostgreSQL row-level security (RLS), no per-tenant schemas, and no per-tenant credentials.
3. **No migrations.** Alembic is not set up, so schema changes are unmanaged.
4. **No durable job queue.** `BackgroundTasks` is in-process and best-effort.
5. **No real AI provider integration.** Timeout and retry are not yet applied to any live call. Retrying after a timeout may duplicate provider-side work.
6. **Idempotency hardening is pending:**
   - no lock timeout while a duplicate waits;
   - no record TTL or cleanup;
   - only successes are stored;
   - correctness assumes READ COMMITTED isolation.
7. **Observability.** No structured logging, metrics, or tracing; the background job uses `print`.
8. **Configuration.** `DATABASE_URL` falls back to a local development database. There is no settings validation and no secrets management.
9. **CI is advisory.** `main` has no branch protection or required checks.

---

## 9. Phase 4 Handoff

**Ready for Phase 4:**

- A packaged FastAPI service with tenant-scoped persistence and simulated RBAC.
- Transactional idempotency.
- Tested reliability primitives.
- 118 tests at 98% coverage.
- A green CI pipeline that runs against PostgreSQL 17.

**Inputs to Phase 4 and later phases.** These follow the fixed roadmap; this document does not reorder it.

- Replace `get_current_principal` with validated identity. The dependency-override seam and RBAC tests are in place to support this.
- Add Alembic migrations before any schema change.
- Wire `execute_with_timeout` and `execute_with_retry` into the first real provider client under `integrations/`.
- Make the `pytest` workflow a required check on `main`.
