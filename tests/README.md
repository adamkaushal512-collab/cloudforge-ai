# CloudForge AI test suite

## Categories

Every test carries at least one marker; collection fails otherwise
(`--strict-markers` plus a check in `conftest.py`).

| Marker | Directory | Purpose | Needs PostgreSQL |
|---|---|---|---|
| `unit` | `tests/unit/` | Pure logic: retry/timeout wrappers, idempotency key validation and hashing, RBAC helper. Fast and deterministic. | No |
| `api` | `tests/api/` | HTTP contract through FastAPI `TestClient` / `httpx.ASGITransport`: status codes, response bodies, validation errors, RBAC, async and background endpoints. | Only if also `integration` |
| `integration` | `tests/integration/` and DB-backed API tests | Real PostgreSQL: repository create and read, commit and rollback, unique constraints, idempotency persistence, concurrency, tenant isolation. | Yes |

A test can have more than one marker. For example, the idempotency API tests are `api` and `integration`.
The collection check rejects any test that uses the `database` fixture without the `integration` marker.

## Fixtures (`tests/conftest.py`)

| Fixture | Provides |
|---|---|
| `database` (session) | Ensures the schema exists in the test DB and deletes leftover `pytest-*` rows at session start and end. |
| `db_session` | SQLAlchemy session that is rolled back after the test. |
| `db_counts` | `models(tenant)` / `records(tenant)` committed row counts from a fresh session. |
| `tenants` | `new()` gives a unique `pytest-…` tenant, and `headers(tenant, key, roles)` builds the auth headers. Each test's tenants' rows are deleted afterwards. |
| `auth_override` / `client` | Replaces `get_current_principal` through `app.dependency_overrides` with a principal read from `X-Test-Tenant` / `X-Test-Roles` / `X-Test-User`. These headers exist only in tests. |
| `dev_auth_client` | `TestClient` with the app's real (simulated) auth. Only for endpoints that write no tenant data. |
| `valid_payload`, `new_key` | A valid registration body and unique `Idempotency-Key` values. |

### Database safety

- Tests never use `DATABASE_URL`. `conftest.py` overwrites it with
  `TEST_DATABASE_URL` (default `postgresql+psycopg:///cloudforge_test`)
  before the application creates its engine.
- The run aborts unless the database name contains `test`.
- All test data uses tenant IDs beginning with `pytest-`, and cleanup deletes only those rows.

## Running locally

```bash
createdb cloudforge_test            # once
pip install -e ".[dev]"

python -m pytest -q                         # full suite
python -m pytest -q -m unit                 # no database needed
python -m pytest -q -m "not integration"    # unit + non-DB API tests
python -m pytest -q -m integration          # PostgreSQL tests only

# Coverage (terminal + htmlcov/index.html)
python -m pytest --cov=cloudforge --cov-report=term-missing --cov-report=html

# Different test database
TEST_DATABASE_URL=postgresql+psycopg://user:pass@host:5432/cloudforge_test python -m pytest -q
```

## CI

`.github/workflows/tests.yml` runs on pull requests and on pushes to `main`. It uses Python 3.12 and a
PostgreSQL 17 service container with throwaway credentials, so no secrets are needed. The run fails if coverage drops
below 90%, and it uploads `htmlcov/` as the `coverage-html` artifact.

## Known limitations of what these tests prove

- **Authentication.** JWT/OIDC is not implemented. `get_current_principal` returns a hardcoded
  development principal, and the tests replace it with dependency overrides. RBAC tests check only
  the application role check. HTTP 401 is not tested over HTTP, because the development dependency
  cannot produce it.
- **Tenant isolation.** The tests check the application boundaries only: the tenant comes from the
  principal, repository reads filter by tenant, and idempotency records are scoped by tenant. There is
  no PostgreSQL row-level security and no per-tenant schema or credentials.
- **Background jobs.** FastAPI `BackgroundTasks` run in the same process after the response.
  They are not a durable or distributed queue: work is lost on a crash or restart, and nothing retries it.
- **Concurrency.** The concurrency tests run threads within one process against one PostgreSQL
  instance. They do not cover multiple app replicas, connection-pool exhaustion or lock timeouts.
