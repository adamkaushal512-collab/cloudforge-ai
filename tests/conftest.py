"""
Shared pytest fixtures for CloudForge AI.

Database safety
---------------
Tests never touch the development database. Before any
``cloudforge`` module is imported, ``DATABASE_URL`` is replaced
with ``TEST_DATABASE_URL`` (default: local ``cloudforge_test``),
and the run aborts if the target database name does not contain
"test". All rows written by tests use tenant IDs starting with
``pytest-`` and are deleted per test, with a sweep at session
start and end for rows left by interrupted runs.

Authentication
--------------
The application's ``get_current_principal`` is a development
simulation (no JWT/OIDC). API tests replace it through
``app.dependency_overrides`` with a principal built from test-only
request headers, so each request (including requests from worker
threads) can choose its tenant and roles.
"""

import os
import uuid

# Must run before cloudforge.core.database creates its engine.
DEFAULT_TEST_DATABASE_URL = "postgresql+psycopg:///cloudforge_test"
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest  # noqa: E402
from fastapi import Request  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import delete, func, select  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402

from cloudforge.api.auth import get_current_principal  # noqa: E402
from cloudforge.core.database import SessionLocal, engine  # noqa: E402
from cloudforge.core.security import AuthenticatedPrincipal  # noqa: E402
from cloudforge.main import app  # noqa: E402
from cloudforge.repositories.models import (  # noqa: E402
    AIModel,
    Base,
    IdempotencyRecord,
)

TEST_TENANT_PREFIX = "pytest-"
TEST_TENANT_HEADER = "X-Test-Tenant"
TEST_ROLES_HEADER = "X-Test-Roles"
TEST_USER_HEADER = "X-Test-User"

CATEGORY_MARKERS = {"unit", "api", "integration"}

VALID_PAYLOAD = {
    "model_name": "pytest-model",
    "provider": "bedrock",
    "max_tokens": 1024,
}


# ------------------------------------------------------------ pytest hooks


def pytest_configure(config):
    database_name = make_url(TEST_DATABASE_URL).database or ""
    if "test" not in database_name:
        raise pytest.UsageError(
            f"Refusing to run tests against database {database_name!r}: "
            "TEST_DATABASE_URL must point to a dedicated test database "
            "whose name contains 'test'."
        )


def pytest_collection_modifyitems(config, items):
    """Every test needs a category; DB tests must be 'integration'."""

    problems = []
    for item in items:
        markers = {m.name for m in item.iter_markers()}
        if not markers & CATEGORY_MARKERS:
            problems.append(f"{item.nodeid}: missing unit/api/integration marker")
        if "database" in item.fixturenames and "integration" not in markers:
            problems.append(f"{item.nodeid}: uses PostgreSQL but is not marked integration")
    if problems:
        raise pytest.UsageError("Test categorization errors:\n" + "\n".join(problems))


# ---------------------------------------------------------------- database


def _delete_test_rows(tenant_filter) -> None:
    with SessionLocal() as session:
        session.execute(delete(IdempotencyRecord).where(tenant_filter(IdempotencyRecord.tenant_id)))
        session.execute(delete(AIModel).where(tenant_filter(AIModel.tenant_id)))
        session.commit()


def _sweep_all_test_tenants() -> None:
    _delete_test_rows(lambda column: column.startswith(TEST_TENANT_PREFIX))


@pytest.fixture(scope="session")
def database():
    """Ensure the schema exists in the test database; sweep test rows."""

    Base.metadata.create_all(engine)
    _sweep_all_test_tenants()
    yield engine
    _sweep_all_test_tenants()


@pytest.fixture
def db_session(database):
    """A session whose uncommitted work is rolled back after the test."""

    with SessionLocal() as session:
        try:
            yield session
        finally:
            session.rollback()


class DbCounts:
    """Row counts read through a fresh session (sees committed data only)."""

    @staticmethod
    def models(tenant_id: str) -> int:
        with SessionLocal() as session:
            return session.scalar(
                select(func.count()).select_from(AIModel).where(AIModel.tenant_id == tenant_id)
            )

    @staticmethod
    def records(tenant_id: str) -> int:
        with SessionLocal() as session:
            return session.scalar(
                select(func.count())
                .select_from(IdempotencyRecord)
                .where(IdempotencyRecord.tenant_id == tenant_id)
            )


@pytest.fixture
def db_counts(database) -> DbCounts:
    return DbCounts()


# ----------------------------------------------------------------- tenants


class TenantFactory:
    """Creates unique tenant IDs and builds test auth headers."""

    def __init__(self) -> None:
        self.created: list[str] = []
        self._run = uuid.uuid4().hex[:10]

    def new(self, label: str = "t") -> str:
        tenant_id = f"{TEST_TENANT_PREFIX}{self._run}-{len(self.created)}-{label}"
        self.created.append(tenant_id)
        return tenant_id

    @staticmethod
    def headers(
        tenant_id: str,
        key: str | None = None,
        roles: tuple[str, ...] | None = None,
        user_id: str = "pytest-user",
    ) -> dict[str, str]:
        headers = {TEST_TENANT_HEADER: tenant_id, TEST_USER_HEADER: user_id}
        if roles is not None:
            headers[TEST_ROLES_HEADER] = ",".join(roles)
        if key is not None:
            headers["Idempotency-Key"] = key
        return headers


@pytest.fixture
def tenants(database):
    """Unique tenants for this test; their rows are deleted afterwards."""

    factory = TenantFactory()
    try:
        yield factory
    finally:
        if factory.created:
            _delete_test_rows(lambda column: column.in_(factory.created))


# ------------------------------------------------------------ auth and HTTP


def _principal_from_test_headers(request: Request) -> AuthenticatedPrincipal:
    """Test-only replacement for the development auth dependency."""

    tenant_id = request.headers.get(TEST_TENANT_HEADER)
    if tenant_id is None:
        raise RuntimeError(f"Test request is missing the {TEST_TENANT_HEADER} header")

    roles_header = request.headers.get(TEST_ROLES_HEADER, "model-admin")
    return AuthenticatedPrincipal(
        user_id=request.headers.get(TEST_USER_HEADER, "pytest-user"),
        tenant_id=tenant_id,
        roles=tuple(role for role in roles_header.split(",") if role),
    )


@pytest.fixture
def auth_override():
    """Authenticate requests from test headers via dependency override."""

    app.dependency_overrides[get_current_principal] = _principal_from_test_headers
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_current_principal, None)


@pytest.fixture
def client(auth_override) -> TestClient:
    """TestClient with test-header auth; server errors become HTTP 500."""

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def dev_auth_client() -> TestClient:
    """
    TestClient using the application's real (simulated) auth.

    Only for endpoints that do not write tenant data: the dev
    principal's tenant is not a pytest- tenant and is not cleaned up.
    """

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def valid_payload() -> dict:
    return dict(VALID_PAYLOAD)


@pytest.fixture
def new_key():
    """Factory for unique, valid Idempotency-Key values."""

    return lambda: f"key-{uuid.uuid4()}"
