"""
API + PostgreSQL tests for POST /v1/models idempotency.

Tenant-isolation cases live in test_tenant_isolation.py.
"""

import threading

import pytest
from fastapi.testclient import TestClient

from cloudforge.api.schemas import ModelRegistrationRequest
from cloudforge.core.database import SessionLocal
from cloudforge.main import REGISTER_MODEL_OPERATION, app
from cloudforge.repositories.idempotency_repository import IdempotencyRepository
from cloudforge.repositories.model_repository import ModelRepository
from cloudforge.services.idempotency import compute_request_hash

pytestmark = [pytest.mark.api, pytest.mark.integration]


def test_without_key_preserves_original_behavior(client, tenants, db_counts, valid_payload):
    tenant = tenants.new()

    first = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant))
    second = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant))

    assert first.status_code == second.status_code == 201
    assert first.json() == {
        "message": "Model registered successfully",
        "model_name": "pytest-model",
        "provider": "bedrock",
    }
    assert "Idempotent-Replayed" not in first.headers
    # No key: every request creates a model, no records stored.
    assert db_counts.models(tenant) == 2
    assert db_counts.records(tenant) == 0


def test_new_key_creates_model_and_record(client, tenants, db_counts, valid_payload, new_key):
    tenant = tenants.new()
    key = new_key()

    resp = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant, key))

    assert resp.status_code == 201
    assert "Idempotent-Replayed" not in resp.headers
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1

    with SessionLocal() as session:
        record = IdempotencyRepository(session).get(tenant, REGISTER_MODEL_OPERATION, key)
        assert record is not None
        assert record.status_code == 201
        assert record.response_body == resp.json()
        assert record.request_hash == compute_request_hash(
            ModelRegistrationRequest(**valid_payload)
        )


def test_identical_replay_returns_stored_response(
    client, tenants, db_counts, valid_payload, new_key
):
    tenant = tenants.new()
    headers = tenants.headers(tenant, new_key())

    first = client.post("/v1/models", json=valid_payload, headers=headers)
    # Same payload with different JSON key order hashes identically.
    reordered = dict(reversed(list(valid_payload.items())))
    second = client.post("/v1/models", json=reordered, headers=headers)
    third = client.post("/v1/models", json=valid_payload, headers=headers)

    assert first.status_code == second.status_code == third.status_code == 201
    assert first.json() == second.json() == third.json()
    assert second.headers["Idempotent-Replayed"] == "true"
    assert third.headers["Idempotent-Replayed"] == "true"
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


def test_key_reuse_with_different_payload_returns_409(
    client, tenants, db_counts, valid_payload, new_key
):
    tenant = tenants.new()
    headers = tenants.headers(tenant, new_key())

    first = client.post("/v1/models", json=valid_payload, headers=headers)
    conflict = client.post(
        "/v1/models", json={**valid_payload, "max_tokens": 2048}, headers=headers
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert conflict.json() == {
        "detail": {
            "code": "idempotency_key_conflict",
            "message": "Idempotency-Key was already used with a different request payload",
        }
    }
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


@pytest.mark.parametrize(
    "bad_key",
    ["", "has space", "x" * 256, "semi;colon", "slash/key", "unicodé"],
)
def test_invalid_key_returns_structured_400(client, tenants, db_counts, valid_payload, bad_key):
    tenant = tenants.new()
    headers = [
        (name, value) for name, value in tenants.headers(tenant).items()
    ] + [("Idempotency-Key", bad_key.encode("utf-8"))]

    resp = client.post("/v1/models", json=valid_payload, headers=headers)

    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["code"] == "invalid_idempotency_key"
    assert isinstance(detail["message"], str) and detail["message"]
    assert db_counts.models(tenant) == 0
    assert db_counts.records(tenant) == 0


def test_max_length_key_is_accepted(client, tenants, db_counts, valid_payload):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models", json=valid_payload, headers=tenants.headers(tenant, "k" * 255)
    )

    assert resp.status_code == 201
    assert db_counts.records(tenant) == 1


def test_validation_runs_before_idempotency(client, tenants, db_counts, new_key):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        json={"model_name": "", "provider": "bedrock", "max_tokens": 1},
        headers=tenants.headers(tenant, new_key()),
    )

    # Invalid payloads never reserve a key.
    assert resp.status_code == 422
    assert db_counts.records(tenant) == 0


def test_failure_after_reservation_rolls_back_everything(
    client, tenants, db_counts, valid_payload, new_key, monkeypatch
):
    tenant = tenants.new()
    headers = tenants.headers(tenant, new_key())
    original_create = ModelRepository.create

    def failing_create(self, **kwargs):
        # The INSERT reaches PostgreSQL, then the request fails.
        original_create(self, **kwargs)
        raise RuntimeError("simulated failure after model insert")

    monkeypatch.setattr(ModelRepository, "create", failing_create)
    failed = client.post("/v1/models", json=valid_payload, headers=headers)

    assert failed.status_code == 500
    # Reservation and model insert were rolled back together.
    assert db_counts.models(tenant) == 0
    assert db_counts.records(tenant) == 0

    # The key is reusable once the failure is resolved.
    monkeypatch.setattr(ModelRepository, "create", original_create)
    retry = client.post("/v1/models", json=valid_payload, headers=headers)

    assert retry.status_code == 201
    assert "Idempotent-Replayed" not in retry.headers
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


def test_concurrent_duplicate_requests_create_one_model(
    auth_override, tenants, db_counts, valid_payload, new_key
):
    tenant = tenants.new()
    key = new_key()
    workers = 8
    barrier = threading.Barrier(workers)
    results: list = [None] * workers

    def send(index: int) -> None:
        local_client = TestClient(app, raise_server_exceptions=False)
        barrier.wait()
        results[index] = local_client.post(
            "/v1/models", json=valid_payload, headers=tenants.headers(tenant, key)
        )

    threads = [threading.Thread(target=send, args=(i,)) for i in range(workers)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
        assert not thread.is_alive()

    assert all(r is not None and r.status_code == 201 for r in results)
    assert len({tuple(sorted(r.json().items())) for r in results}) == 1
    originals = [r for r in results if "Idempotent-Replayed" not in r.headers]
    assert len(originals) == 1
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


def _hold_reservation_then(tenants, payload, key, finish):
    """
    Hold an uncommitted reservation in a separate session, send a
    duplicate request, verify it blocks, then call finish().
    """

    tenant = tenants.new()
    request_hash = compute_request_hash(ModelRegistrationRequest(**payload))
    result: dict = {}

    def send() -> None:
        local_client = TestClient(app, raise_server_exceptions=False)
        result["response"] = local_client.post(
            "/v1/models", json=payload, headers=tenants.headers(tenant, key)
        )

    with SessionLocal() as holder:
        try:
            assert IdempotencyRepository(holder).reserve(
                tenant, REGISTER_MODEL_OPERATION, key, request_hash
            )

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


def test_blocked_duplicate_replays_after_first_commits(
    auth_override, tenants, db_counts, valid_payload, new_key
):
    def commit_first(holder, tenant, key):
        model = ModelRepository(holder).create(tenant_id=tenant, **valid_payload)
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

    tenant, resp = _hold_reservation_then(tenants, valid_payload, new_key(), commit_first)

    assert resp.status_code == 201
    assert resp.headers["Idempotent-Replayed"] == "true"
    assert resp.json()["model_name"] == "pytest-model"
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


def test_blocked_duplicate_takes_over_after_first_rolls_back(
    auth_override, tenants, db_counts, valid_payload, new_key
):
    def roll_back_first(holder, tenant, key):
        holder.rollback()

    tenant, resp = _hold_reservation_then(tenants, valid_payload, new_key(), roll_back_first)

    # The waiter recovered: it claimed the key and did the work.
    assert resp.status_code == 201
    assert "Idempotent-Replayed" not in resp.headers
    assert db_counts.models(tenant) == 1
    assert db_counts.records(tenant) == 1


def test_failure_without_key_rolls_back_model(
    client, tenants, db_counts, valid_payload, monkeypatch
):
    tenant = tenants.new()
    original_create = ModelRepository.create

    def failing_create(self, **kwargs):
        original_create(self, **kwargs)
        raise RuntimeError("simulated failure after model insert")

    monkeypatch.setattr(ModelRepository, "create", failing_create)
    resp = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant))

    assert resp.status_code == 500
    assert db_counts.models(tenant) == 0


def test_unreplayable_existing_record_returns_in_progress_409(
    client, tenants, db_counts, valid_payload, new_key, monkeypatch
):
    """Defensive path: never replay a missing or pending record."""

    tenant = tenants.new()
    # Simulate a conflict whose committed record cannot be read back.
    monkeypatch.setattr(IdempotencyRepository, "reserve", lambda self, *a, **k: False)

    resp = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant, new_key()))

    assert resp.status_code == 409
    assert resp.json()["detail"]["code"] == "idempotency_request_in_progress"
    assert db_counts.models(tenant) == 0
    assert db_counts.records(tenant) == 0
