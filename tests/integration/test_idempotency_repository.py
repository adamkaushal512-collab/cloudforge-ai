"""PostgreSQL integration tests for IdempotencyRepository."""

import pytest
from sqlalchemy.exc import IntegrityError

from cloudforge.core.database import SessionLocal
from cloudforge.repositories.idempotency_repository import (
    PENDING_STATUS_CODE,
    IdempotencyRepository,
)
from cloudforge.repositories.models import IdempotencyRecord

pytestmark = pytest.mark.integration

OPERATION = "pytest-operation"
BODY = {"message": "ok"}


def test_reserve_complete_and_get(tenants, db_counts, new_key):
    tenant = tenants.new()
    key = new_key()

    with SessionLocal() as session:
        repo = IdempotencyRepository(session)
        assert repo.reserve(tenant, OPERATION, key, "hash-1") is True

        pending = repo.get(tenant, OPERATION, key)
        assert pending is not None
        assert pending.status_code == PENDING_STATUS_CODE

        repo.complete(tenant, OPERATION, key, 201, BODY)
        session.commit()

    with SessionLocal() as session:
        record = IdempotencyRepository(session).get(tenant, OPERATION, key)
        assert record is not None
        assert record.request_hash == "hash-1"
        assert record.status_code == 201
        assert record.response_body == BODY

    assert db_counts.records(tenant) == 1


def test_reserve_returns_false_for_committed_key(tenants, db_counts, new_key):
    tenant = tenants.new()
    key = new_key()

    with SessionLocal() as session:
        repo = IdempotencyRepository(session)
        repo.reserve(tenant, OPERATION, key, "hash-1")
        repo.complete(tenant, OPERATION, key, 201, BODY)
        session.commit()

    with SessionLocal() as session:
        # ON CONFLICT DO NOTHING: no exception, transaction usable.
        assert IdempotencyRepository(session).reserve(tenant, OPERATION, key, "hash-2") is False
        session.rollback()

    assert db_counts.records(tenant) == 1


def test_same_key_is_scoped_by_tenant_and_operation(tenants, db_counts, new_key):
    tenant_a = tenants.new("a")
    tenant_b = tenants.new("b")
    key = new_key()

    with SessionLocal() as session:
        repo = IdempotencyRepository(session)
        assert repo.reserve(tenant_a, OPERATION, key, "h") is True
        assert repo.reserve(tenant_b, OPERATION, key, "h") is True
        assert repo.reserve(tenant_a, "other-operation", key, "h") is True
        session.commit()

        # Tenant-scoped lookups do not cross tenants.
        assert repo.get(tenant_a, OPERATION, key).tenant_id == tenant_a
        assert repo.get(tenant_b, OPERATION, key).tenant_id == tenant_b
        assert repo.get(tenants.new("c"), OPERATION, key) is None

    assert db_counts.records(tenant_a) == 2
    assert db_counts.records(tenant_b) == 1


def test_uncommitted_reservation_is_invisible_to_other_sessions(tenants, new_key):
    tenant = tenants.new()
    key = new_key()

    with SessionLocal() as holder:
        assert IdempotencyRepository(holder).reserve(tenant, OPERATION, key, "h") is True

        with SessionLocal() as observer:
            # A pending placeholder is never observable elsewhere.
            assert IdempotencyRepository(observer).get(tenant, OPERATION, key) is None

        holder.rollback()


def test_rolled_back_reservation_frees_the_key(tenants, db_counts, new_key):
    tenant = tenants.new()
    key = new_key()

    with SessionLocal() as session:
        IdempotencyRepository(session).reserve(tenant, OPERATION, key, "h")
        session.rollback()

    assert db_counts.records(tenant) == 0

    with SessionLocal() as session:
        assert IdempotencyRepository(session).reserve(tenant, OPERATION, key, "h") is True
        session.rollback()


def test_complete_without_reservation_raises(tenants, new_key):
    with SessionLocal() as session:
        with pytest.raises(RuntimeError):
            IdempotencyRepository(session).complete(tenants.new(), OPERATION, new_key(), 201, BODY)
        session.rollback()


def test_complete_twice_raises(tenants, new_key):
    tenant = tenants.new()
    key = new_key()

    with SessionLocal() as session:
        repo = IdempotencyRepository(session)
        repo.reserve(tenant, OPERATION, key, "h")
        repo.complete(tenant, OPERATION, key, 201, BODY)
        with pytest.raises(RuntimeError):
            repo.complete(tenant, OPERATION, key, 201, {"message": "overwrite"})
        session.rollback()


def test_database_enforces_unique_constraint(tenants, new_key):
    tenant = tenants.new()
    key = new_key()

    def record():
        return IdempotencyRecord(
            tenant_id=tenant,
            operation=OPERATION,
            idempotency_key=key,
            request_hash="h",
            response_body=BODY,
            status_code=201,
        )

    with SessionLocal() as session:
        session.add(record())
        session.flush()
        session.add(record())
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()
