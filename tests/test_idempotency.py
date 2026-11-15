"""
Integration tests for POST /v1/models idempotency.

These run against the PostgreSQL database configured by
DATABASE_URL. Every test uses unique tenant identifiers and
deletes its own rows afterwards.
"""

import threading
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from cloudforge.api.auth import get_current_principal
from cloudforge.api.schemas import ModelRegistrationRequest
from cloudforge.core.database import SessionLocal
from cloudforge.core.security import AuthenticatedPrincipal
from cloudforge.main import REGISTER_MODEL_OPERATION, app
from cloudforge.repositories.idempotency_repository import (
    IdempotencyRepository,
)
from cloudforge.repositories.model_repository import ModelRepository
from cloudforge.repositories.models import AIModel, IdempotencyRecord
from cloudforge.services.idempotency import compute_request_hash

PAYLOAD = {
    "model_name": "idem-model",
    "provider": "bedrock",
    "max_tokens": 1024,
}


# ---------------------------------------------------------------- helpers


def count_models(tenant_id: str) -> int:
    with SessionLocal() as session:
        return session.scalar(
            select(func.count())
            .select_from(AIModel)
            .where(AIModel.tenant_id == tenant_id)
        )


def count_records(tenant_id: str) -> int:
    with SessionLocal() as session:
        return session.scalar(
            select(func.count())
            .select_from(IdempotencyRecord)
            .where(IdempotencyRecord.tenant_id == tenant_id)
        )


class TenantFactory:
    """Creates unique tenants and authenticates requests as them."""

    def __init__(self) -> None:
        self.created: list[str] = []
        self._run = uuid.uuid4().hex[:12]

    def new(self, label: str = "t") -> str:
        tenant_id = f"pytest-idem-{self._run}-{label}"
        self.created.append(tenant_id)
        return tenant_id

    @staticmethod
    def headers(tenant_id: str, key: str | None = None) -> dict[str, str]:
        headers = {"X-Test-Tenant": tenant_id}
        if key is not None:
            headers["Idempotency-Key"] = key
        return headers


@pytest.fixture
def tenants():
    factory = TenantFactory()

    # Test-only principal: tenant chosen per request via a
    # test header, so tenant isolation can be exercised.
    from fastapi import Request

    def principal_override(request: Request) -> AuthenticatedPrincipal:
        return AuthenticatedPrincipal(
            user_id="pytest",
            tenant_id=request.headers["X-Test-Tenant"],
            roles=("model-admin",),
        )

    app.dependency_overrides[get_current_principal] = principal_override
    try:
        yield factory
    finally:
        app.dependency_overrides.pop(get_current_principal, None)
        with SessionLocal() as session:
            session.execute(
                delete(IdempotencyRecord).where(
                    IdempotencyRecord.tenant_id.in_(factory.created)
                )
            )
            session.execute(
                delete(AIModel).where(AIModel.tenant_id.in_(factory.created))
            )
            session.commit()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def new_key() -> str:
    return f"key-{uuid.uuid4()}"


# ------------------------------------------------------------------ tests


def test_without_key_preserves_original_behavior(tenants, client):
    tenant = tenants.new()

    first = client.post("/v1/models", json=PAYLOAD, headers=tenants.headers(tenant))
    second = client.post("/v1/models", json=PAYLOAD, headers=tenants.headers(tenant))

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json() == {
        "message": "Model registered successfully",
        "model_name": "idem-model",
        "provider": "bedrock",
    }
    assert "Idempotent-Replayed" not in first.headers
    # No key: every request creates a model, no records stored.
    assert count_models(tenant) == 2
    assert count_records(tenant) == 0


def test_new_key_creates_model_and_record(tenants, client):
    tenant = tenants.new()
    key = new_key()

    resp = client.post("/v1/models", json=PAYLOAD, headers=tenants.headers(tenant, key))

    assert resp.status_code == 201
    assert resp.json()["model_name"] == "idem-model"
    assert "Idempotent-Replayed" not in resp.headers
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1

    with SessionLocal() as session:
        record = IdempotencyRepository(session).get(tenant, REGISTER_MODEL_OPERATION, key)
        assert record is not None
        assert record.status_code == 201
        assert record.response_body == resp.json()
        assert record.request_hash == compute_request_hash(
            ModelRegistrationRequest(**PAYLOAD)
        )


def test_identical_replay_returns_stored_response(tenants, client):
    tenant = tenants.new()
    key = new_key()
    headers = tenants.headers(tenant, key)

    first = client.post("/v1/models", json=PAYLOAD, headers=headers)
    # Same payload with different JSON key order hashes identically.
    reordered = dict(reversed(list(PAYLOAD.items())))
    second = client.post("/v1/models", json=reordered, headers=headers)
    third = client.post("/v1/models", json=PAYLOAD, headers=headers)

    assert first.status_code == second.status_code == third.status_code == 201
    assert first.json() == second.json() == third.json()
    assert second.headers["Idempotent-Replayed"] == "true"
    assert third.headers["Idempotent-Replayed"] == "true"
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1


def test_key_reuse_with_different_payload_returns_409(tenants, client):
    tenant = tenants.new()
    key = new_key()
    headers = tenants.headers(tenant, key)

    first = client.post("/v1/models", json=PAYLOAD, headers=headers)
    conflict = client.post(
        "/v1/models",
        json={**PAYLOAD, "max_tokens": 2048},
        headers=headers,
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json()["detail"]["code"] == "idempotency_key_conflict"
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1


@pytest.mark.parametrize(
    "bad_key",
    ["", "has space", "x" * 256, "semi;colon", "slash/key", "unicodé"],
)
def test_invalid_key_returns_structured_400(tenants, client, bad_key):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        json=PAYLOAD,
        headers={"X-Test-Tenant": tenant, "Idempotency-Key": bad_key}
        if bad_key.isascii()
        else [("X-Test-Tenant", tenant), ("Idempotency-Key", bad_key.encode())],
    )

    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "invalid_idempotency_key"
    assert isinstance(detail["message"], str) and detail["message"]
    assert count_models(tenant) == 0
    assert count_records(tenant) == 0


def test_max_length_key_is_accepted(tenants, client):
    tenant = tenants.new()
    key = "k" * 255

    resp = client.post("/v1/models", json=PAYLOAD, headers=tenants.headers(tenant, key))

    assert resp.status_code == 201
    assert count_records(tenant) == 1


def test_same_key_is_isolated_per_tenant(tenants, client):
    tenant_a = tenants.new("a")
    tenant_b = tenants.new("b")
    key = new_key()

    resp_a = client.post("/v1/models", json=PAYLOAD, headers=tenants.headers(tenant_a, key))
    # Different payload under the same key, but another tenant:
    # must not conflict with or replay tenant A's record.
    resp_b = client.post(
        "/v1/models",
        json={**PAYLOAD, "model_name": "tenant-b-model"},
        headers=tenants.headers(tenant_b, key),
    )

    assert resp_a.status_code == 201
    assert resp_b.status_code == 201
    assert "Idempotent-Replayed" not in resp_b.headers
    assert resp_b.json()["model_name"] == "tenant-b-model"
    assert count_models(tenant_a) == 1
    assert count_models(tenant_b) == 1
    assert count_records(tenant_a) == 1
    assert count_records(tenant_b) == 1


def test_failure_after_reservation_rolls_back_everything(
    tenants, client, monkeypatch
):
    tenant = tenants.new()
    key = new_key()
    headers = tenants.headers(tenant, key)

    original_create = ModelRepository.create

    def failing_create(self, **kwargs):
        # The INSERT reaches PostgreSQL, then the request fails.
        original_create(self, **kwargs)
        raise RuntimeError("simulated failure after model insert")

    monkeypatch.setattr(ModelRepository, "create", failing_create)
    failed = client.post("/v1/models", json=PAYLOAD, headers=headers)

    assert failed.status_code == 500
    # Reservation and model insert were rolled back together.
    assert count_models(tenant) == 0
    assert count_records(tenant) == 0

    # The key is reusable once the failure is resolved.
    monkeypatch.setattr(ModelRepository, "create", original_create)
    retry = client.post("/v1/models", json=PAYLOAD, headers=headers)

    assert retry.status_code == 201
    assert "Idempotent-Replayed" not in retry.headers
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1


def test_concurrent_duplicate_requests_create_one_model(tenants):
    tenant = tenants.new()
    key = new_key()
    workers = 8
    barrier = threading.Barrier(workers)
    results: list = [None] * workers

    def send(index: int) -> None:
        local_client = TestClient(app, raise_server_exceptions=False)
        barrier.wait()
        results[index] = local_client.post(
            "/v1/models",
            json=PAYLOAD,
            headers=tenants.headers(tenant, key),
        )

    threads = [threading.Thread(target=send, args=(i,)) for i in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()

    assert all(r is not None and r.status_code == 201 for r in results)
    bodies = {tuple(sorted(r.json().items())) for r in results}
    assert len(bodies) == 1
    originals = [r for r in results if "Idempotent-Replayed" not in r.headers]
    assert len(originals) == 1
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1


def _hold_reservation_then(tenants, finish):
    """
    Hold an uncommitted reservation in a separate session, send
    a duplicate request, verify it blocks, then call finish().
    """

    tenant = tenants.new()
    key = new_key()
    request_hash = compute_request_hash(ModelRegistrationRequest(**PAYLOAD))
    result: dict = {}

    def send() -> None:
        local_client = TestClient(app, raise_server_exceptions=False)
        result["response"] = local_client.post(
            "/v1/models",
            json=PAYLOAD,
            headers=tenants.headers(tenant, key),
        )

    with SessionLocal() as holder:
        try:
            assert IdempotencyRepository(holder).reserve(
                tenant, REGISTER_MODEL_OPERATION, key, request_hash
            )
            holder.flush()

            thread = threading.Thread(target=send)
            thread.start()
            thread.join(timeout=1.0)
            # The duplicate waits on the unique index; it must not
            # return a placeholder while the holder is in flight.
            assert thread.is_alive()
            assert "response" not in result

            finish(holder, tenant, key)
        finally:
            # Releases the lock if an assertion failed above.
            holder.rollback()

    thread.join(timeout=30)
    assert not thread.is_alive()
    return tenant, result["response"]


def test_blocked_duplicate_replays_after_first_commits(tenants):
    def commit_first(holder, tenant, key):
        model = ModelRepository(holder).create(tenant_id=tenant, **PAYLOAD)
        IdempotencyRepository(holder).complete(
            tenant,
            REGISTER_MODEL_OPERATION,
            key,
            201,
            {
                "message": "Model registered successfully",
                "model_name": model.model_name,
                "provider": model.provider,
            },
        )
        holder.commit()

    tenant, resp = _hold_reservation_then(tenants, commit_first)

    assert resp.status_code == 201
    assert resp.headers["Idempotent-Replayed"] == "true"
    assert resp.json()["model_name"] == "idem-model"
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1


def test_blocked_duplicate_takes_over_after_first_rolls_back(tenants):
    def roll_back_first(holder, tenant, key):
        holder.rollback()

    tenant, resp = _hold_reservation_then(tenants, roll_back_first)

    # The waiter recovered: it claimed the key and did the work.
    assert resp.status_code == 201
    assert "Idempotent-Replayed" not in resp.headers
    assert count_models(tenant) == 1
    assert count_records(tenant) == 1
