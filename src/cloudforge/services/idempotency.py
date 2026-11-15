import hashlib
import json
import re

from pydantic import BaseModel

MAX_IDEMPOTENCY_KEY_LENGTH = 255

# Printable, header-safe characters. Covers UUIDs, ULIDs,
# and common client-generated key formats.
_KEY_PATTERN = re.compile(r"^[A-Za-z0-9._:\-]+$")


class InvalidIdempotencyKeyError(ValueError):
    """Raised when a client supplies a malformed idempotency key."""


def validate_idempotency_key(key: str) -> str:
    """Return the key unchanged if valid, otherwise raise."""

    if not key:
        raise InvalidIdempotencyKeyError(
            "Idempotency-Key must not be empty"
        )

    if len(key) > MAX_IDEMPOTENCY_KEY_LENGTH:
        raise InvalidIdempotencyKeyError(
            "Idempotency-Key must be at most "
            f"{MAX_IDEMPOTENCY_KEY_LENGTH} characters"
        )

    if not _KEY_PATTERN.fullmatch(key):
        raise InvalidIdempotencyKeyError(
            "Idempotency-Key may contain only letters, digits, "
            "'.', '_', ':' and '-'"
        )

    return key


def compute_request_hash(payload: BaseModel) -> str:
    """
    Deterministic SHA-256 of a validated request payload.

    Uses the validated model (not raw bytes), so field order
    and whitespace in the client's JSON do not affect the hash.
    """

    canonical = json.dumps(
        payload.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
