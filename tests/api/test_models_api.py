"""HTTP contract tests for /health and POST /v1/models."""

import pytest

pytestmark = pytest.mark.api


def test_health_returns_healthy(dev_auth_client):
    resp = dev_auth_client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


@pytest.mark.integration
@pytest.mark.parametrize("provider", ["bedrock", "vllm"])
def test_register_model_success(client, tenants, db_counts, provider):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        json={"model_name": "llama-guard", "provider": provider, "max_tokens": 8192},
        headers=tenants.headers(tenant),
    )

    assert resp.status_code == 201
    assert resp.headers["content-type"].startswith("application/json")
    assert resp.json() == {
        "message": "Model registered successfully",
        "model_name": "llama-guard",
        "provider": provider,
    }
    assert db_counts.models(tenant) == 1


@pytest.mark.integration
@pytest.mark.parametrize(
    ("payload", "loc", "error_type"),
    [
        ({"provider": "bedrock", "max_tokens": 1}, ["body", "model_name"], "missing"),
        ({"model_name": "m", "max_tokens": 1}, ["body", "provider"], "missing"),
        ({"model_name": "m", "provider": "bedrock"}, ["body", "max_tokens"], "missing"),
        ({"model_name": "", "provider": "bedrock", "max_tokens": 1},
         ["body", "model_name"], "string_too_short"),
        ({"model_name": "x" * 101, "provider": "bedrock", "max_tokens": 1},
         ["body", "model_name"], "string_too_long"),
        ({"model_name": "m", "provider": "openai", "max_tokens": 1},
         ["body", "provider"], "literal_error"),
        ({"model_name": "m", "provider": "bedrock", "max_tokens": 0},
         ["body", "max_tokens"], "greater_than_equal"),
        ({"model_name": "m", "provider": "bedrock", "max_tokens": 8193},
         ["body", "max_tokens"], "less_than_equal"),
        # strict=True: numeric strings and floats are rejected.
        ({"model_name": "m", "provider": "bedrock", "max_tokens": "100"},
         ["body", "max_tokens"], "int_type"),
        ({"model_name": "m", "provider": "bedrock", "max_tokens": 1.5},
         ["body", "max_tokens"], "int_type"),
    ],
)
def test_register_model_validation_errors(client, tenants, db_counts, payload, loc, error_type):
    tenant = tenants.new()

    resp = client.post("/v1/models", json=payload, headers=tenants.headers(tenant))

    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["loc"] == loc and e["type"] == error_type for e in errors), errors
    assert db_counts.models(tenant) == 0


@pytest.mark.integration
def test_register_model_rejects_malformed_json(client, tenants, db_counts):
    tenant = tenants.new()

    resp = client.post(
        "/v1/models",
        content=b'{"model_name": ',
        headers={**tenants.headers(tenant), "Content-Type": "application/json"},
    )

    assert resp.status_code == 422
    assert resp.json()["detail"][0]["type"] == "json_invalid"
    assert db_counts.models(tenant) == 0


@pytest.mark.integration
def test_register_model_rejects_non_object_body(client, tenants, db_counts):
    tenant = tenants.new()

    resp = client.post("/v1/models", json=["not", "an", "object"], headers=tenants.headers(tenant))

    assert resp.status_code == 422
    assert db_counts.models(tenant) == 0


def test_unknown_route_returns_404(dev_auth_client):
    resp = dev_auth_client.get("/v1/does-not-exist")

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Not Found"}


def test_wrong_method_returns_405(dev_auth_client):
    resp = dev_auth_client.get("/v1/models")

    assert resp.status_code == 405
