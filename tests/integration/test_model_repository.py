"""PostgreSQL integration tests for ModelRepository."""

import pytest

from cloudforge.core.database import SessionLocal
from cloudforge.repositories.model_repository import ModelRepository

pytestmark = pytest.mark.integration


def test_create_and_retrieve_model(db_session, tenants):
    tenant = tenants.new()
    repository = ModelRepository(db_session)

    model = repository.create(
        tenant_id=tenant,
        model_name="pytest-model",
        provider="bedrock",
        max_tokens=1024,
    )

    # flush() inside create() assigns the primary key.
    assert model.id is not None

    saved = repository.get_by_id(tenant_id=tenant, model_id=model.id)
    assert saved is not None
    assert saved.model_name == "pytest-model"
    assert saved.provider == "bedrock"
    assert saved.max_tokens == 1024


def test_get_by_id_returns_none_for_unknown_id(db_session, tenants):
    tenant = tenants.new()
    repository = ModelRepository(db_session)

    assert repository.get_by_id(tenant_id=tenant, model_id=-1) is None


def test_committed_model_persists_across_sessions(tenants, db_counts):
    tenant = tenants.new()

    with SessionLocal() as writer:
        model = ModelRepository(writer).create(
            tenant_id=tenant, model_name="persisted", provider="vllm", max_tokens=512
        )
        writer.commit()
        model_id = model.id

    with SessionLocal() as reader:
        saved = ModelRepository(reader).get_by_id(tenant_id=tenant, model_id=model_id)
        assert saved is not None
        assert saved.model_name == "persisted"
        assert saved.provider == "vllm"

    assert db_counts.models(tenant) == 1


def test_rolled_back_model_is_not_persisted(tenants, db_counts):
    tenant = tenants.new()

    with SessionLocal() as writer:
        model = ModelRepository(writer).create(
            tenant_id=tenant, model_name="discarded", provider="bedrock", max_tokens=1
        )
        model_id = model.id
        writer.rollback()

    with SessionLocal() as reader:
        assert ModelRepository(reader).get_by_id(tenant_id=tenant, model_id=model_id) is None

    assert db_counts.models(tenant) == 0


def test_flushed_but_uncommitted_model_is_invisible_to_other_sessions(tenants, db_counts):
    tenant = tenants.new()

    with SessionLocal() as writer:
        ModelRepository(writer).create(
            tenant_id=tenant, model_name="in-flight", provider="bedrock", max_tokens=1
        )
        # READ COMMITTED: other sessions cannot see the flushed row.
        assert db_counts.models(tenant) == 0
        writer.rollback()

    assert db_counts.models(tenant) == 0
