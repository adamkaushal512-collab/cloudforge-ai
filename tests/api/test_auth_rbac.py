"""
Authentication and RBAC tests for POST /v1/models.

IMPORTANT: CloudForge does not yet implement JWT/OIDC. The
application's get_current_principal returns a hardcoded
development principal. These tests replace it with test
principals via app.dependency_overrides and verify only the
application-level role check (require_role) and tenant
derivation. They do not test real identity verification.

HTTP 401 is not tested over HTTP: the development dependency
always returns a populated principal, so its 401 branch is not
reachable through the API.
"""

import pytest

pytestmark = [pytest.mark.api, pytest.mark.integration]

FORBIDDEN = {"detail": "Insufficient permissions"}


@pytest.mark.parametrize(
    "roles",
    [
        ("model-admin",),
        ("platform-admin",),
        ("viewer", "model-admin"),
        ("platform-admin", "model-admin"),
    ],
)
def test_allowed_roles_can_register(client, tenants, db_counts, valid_payload, roles):
    tenant = tenants.new()

    resp = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant, roles=roles))

    assert resp.status_code == 201
    assert db_counts.models(tenant) == 1


@pytest.mark.parametrize(
    "roles",
    [
        (),
        ("viewer",),
        ("model-viewer", "tenant-admin"),
        # Role matching is exact: no case folding or prefix match.
        ("Model-Admin",),
        ("model-admin-readonly",),
        ("platform",),
    ],
)
def test_denied_roles_get_403_and_write_nothing(client, tenants, db_counts, valid_payload, roles):
    tenant = tenants.new()

    resp = client.post("/v1/models", json=valid_payload, headers=tenants.headers(tenant, roles=roles))

    assert resp.status_code == 403
    assert resp.json() == FORBIDDEN
    assert db_counts.models(tenant) == 0


def test_denied_role_with_idempotency_key_writes_no_record(
    client, tenants, db_counts, valid_payload, new_key
):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        json=valid_payload,
        headers=tenants.headers(tenant, new_key(), roles=("viewer",)),
    )

    # Authorization is checked before the key is reserved.
    assert resp.status_code == 403
    assert db_counts.models(tenant) == 0
    assert db_counts.records(tenant) == 0


def test_rbac_runs_after_validation(client, tenants, db_counts):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        json={"model_name": ""},
        headers=tenants.headers(tenant, roles=("viewer",)),
    )

    # FastAPI validates the body before the endpoint's role check.
    assert resp.status_code == 422
    assert db_counts.models(tenant) == 0

