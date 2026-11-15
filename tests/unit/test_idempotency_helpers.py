"""Unit tests for idempotency key validation and request hashing."""

import hashlib

import pytest

from cloudforge.api.schemas import ModelRegistrationRequest
from cloudforge.services.idempotency import (
    MAX_IDEMPOTENCY_KEY_LENGTH,
    InvalidIdempotencyKeyError,
    compute_request_hash,
    validate_idempotency_key,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "key",
    [
        "a",
        "3f2b8c1e-9d4a-4c55-8a3e-0b9e7f6d1c2a",
        "01HV6Z9N4QK8Y2R7M3T5W1X0AB",
        "order:2026-11-14.retry_1",
        "k" * MAX_IDEMPOTENCY_KEY_LENGTH,
    ],
)
def test_valid_keys_are_returned_unchanged(key):
    assert validate_idempotency_key(key) == key


@pytest.mark.parametrize(
    "key",
    ["", " ", " leading", "trailing ", "tab\tkey", "new\nline", "a/b", "a;b",
     "quote'", "<script>", "ключ", "k" * (MAX_IDEMPOTENCY_KEY_LENGTH + 1)],
)
def test_invalid_keys_raise(key):
    with pytest.raises(InvalidIdempotencyKeyError):
        validate_idempotency_key(key)


def test_invalid_key_error_is_value_error():
    assert issubclass(InvalidIdempotencyKeyError, ValueError)


def _request(**overrides):
    data = {"model_name": "m", "provider": "bedrock", "max_tokens": 10}
    return ModelRegistrationRequest(**{**data, **overrides})


def test_hash_is_sha256_of_canonical_json():
    expected = hashlib.sha256(
        b'{"max_tokens":10,"model_name":"m","provider":"bedrock"}'
    ).hexdigest()

    assert compute_request_hash(_request()) == expected


def test_hash_is_deterministic_and_order_independent():
    a = ModelRegistrationRequest.model_validate(
        {"model_name": "m", "provider": "bedrock", "max_tokens": 10}
    )
    b = ModelRegistrationRequest.model_validate(
        {"max_tokens": 10, "provider": "bedrock", "model_name": "m"}
    )

    assert compute_request_hash(a) == compute_request_hash(b)
    assert compute_request_hash(a) == compute_request_hash(a)


@pytest.mark.parametrize(
    "change",
    [{"model_name": "n"}, {"provider": "vllm"}, {"max_tokens": 11}],
)
def test_hash_changes_with_any_field(change):
    assert compute_request_hash(_request()) != compute_request_hash(_request(**change))


def test_hash_handles_unicode():
    digest = compute_request_hash(_request(model_name="模型"))

    assert len(digest) == 64
    assert digest != compute_request_hash(_request(model_name="model"))
