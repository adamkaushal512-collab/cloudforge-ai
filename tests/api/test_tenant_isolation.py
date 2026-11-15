"""
Multi-tenant isolation tests at the application boundary.

Scope: these verify that tenant context comes from the
authenticated principal, that tenant-scoped repository reads
filter by tenant, and that idempotency records are tenant-scoped.
They do NOT verify database-level isolation (no PostgreSQL RLS,
no per-tenant schemas or credentials exist yet), and the
principal itself is a development simulation.
"""

import pytest
from sqlalchemy import select

from cloudforge.core.database import SessionLocal
from cloudforge.repositories.model_repository import ModelRepository
from cloudforge.repositories.models import AIModel

pytestmark = [pytest.mark.api, pytest.mark.integration]


def _only_model_id(tenant_id: str) -> int:
    with SessionLocal() as session:
        ids = session.scalars(select(AIModel.id).where(AIModel.tenant_id == tenant_id)).all()
    assert len(ids) == 1
    return ids[0]


def test_tenant_cannot_read_another_tenants_model(client, tenants, valid_payload):
    tenant_a = tenants.new("a")
    tenant_b = tenants.new("b")
    client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant_a))
    model_id = _only_model_id(tenant_a)

    with SessionLocal() as session:
        repo = ModelRepository(session)
        assert repo.get_by_id(tenant_id=tenant_a, model_id=model_id) is not None
        # Negative: correct ID, wrong tenant.
        assert repo.get_by_id(tenant_id=tenant_b, model_id=model_id) is None
        # Negative: empty / wildcard-looking tenant values match nothing.
        assert repo.get_by_id(tenant_id="", model_id=model_id) is None
        assert repo.get_by_id(tenant_id="%", model_id=model_id) is None
        assert repo.get_by_id(tenant_id=f"{tenant_a}' OR '1'='1", model_id=model_id) is None


def test_tenant_id_in_request_body_is_ignored(client, tenants, db_counts, valid_payload):
    attacker = tenants.new("attacker")
    victim = tenants.new("victim")

    resp = client.post(
        "/v1/models",
        json={**valid_payload, "tenant_id": victim},
        headers=tenants.headers(attacker),
    )

    # The model is owned by the authenticated tenant, not the body's.
    assert resp.status_code == 201
    assert "tenant_id" not in resp.json()
    assert db_counts.models(attacker) == 1
    assert db_counts.models(victim) == 0


def test_idempotency_key_is_isolated_per_tenant(client, tenants, db_counts, valid_payload, new_key):
    tenant_a = tenants.new("a")
    tenant_b = tenants.new("b")
    key = new_key()

    resp_a = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant_a, key))
    # Different payload, same key, other tenant: no 409 from A's record.
    resp_b = client.post(
        "/v1/models",
        json={**valid_payload, "model_name": "tenant-b-model"},
        headers=tenants.headers(tenant_b, key),
    )

    assert resp_a.status_code == resp_b.status_code == 201
    assert "Idempotent-Replayed" not in resp_b.headers
    assert resp_b.json()["model_name"] == "tenant-b-model"
    assert db_counts.models(tenant_a) == db_counts.models(tenant_b) == 1
    assert db_counts.records(tenant_a) == db_counts.records(tenant_b) == 1


def test_identical_request_does_not_replay_across_tenants(
    client, tenants, db_counts, valid_payload, new_key
):
    tenant_a = tenants.new("a")
    tenant_b = tenants.new("b")
    key = new_key()

    client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant_a, key))
    resp_b = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant_b, key))

    # Negative: tenant B must not receive tenant A's stored response.
    assert resp_b.status_code == 201
    assert "Idempotent-Replayed" not in resp_b.headers
    assert db_counts.models(tenant_b) == 1
    assert db_counts.records(tenant_b) == 1
