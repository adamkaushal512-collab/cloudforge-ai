from cloudforge.core.database import SessionLocal
from cloudforge.repositories.model_repository import ModelRepository


def test_create_and_retrieve_model():
    # Open a database session and transaction.
    with SessionLocal() as session:
        repository = ModelRepository(session)

        try:
            model = repository.create(
                tenant_id="tenant-test",
                model_name="pytest-model",
                provider="bedrock",
                max_tokens=1024,
            )

            model_id = model.id

            # Verify the correct tenant can retrieve the model.
            saved = repository.get_by_id(
                tenant_id="tenant-test",
                model_id=model_id,
            )

            assert saved is not None
            assert saved.model_name == "pytest-model"
            assert saved.max_tokens == 1024

            # Verify a different tenant cannot retrieve it.
            other = repository.get_by_id(
                tenant_id="tenant-other",
                model_id=model_id,
            )

            assert other is None

        finally:
            # Keep the test from permanently adding a record.
            session.rollback()
