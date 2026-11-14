from cloudforge.core.database import SessionLocal
from cloudforge.repositories.model_repository import ModelRepository

# Open a database session.
with SessionLocal() as session:

    # Pass the session into our repository.
    repository = ModelRepository(session)

    # Create a new AI model registration.
    model = repository.create(
        tenant_id="tenant-demo",
        model_name="cloudforge-test-model",
        provider="bedrock",
        max_tokens=2048,
    )

    # flush() in the repository assigns the database ID.
    model_id = model.id

    # The caller controls the transaction.
    session.commit()

    print("Created model ID:", model_id)

    # Retrieve the model for the correct tenant.
    saved_model = repository.get_by_id(
        tenant_id="tenant-demo",
        model_id=model_id,
    )

    assert saved_model is not None
    print("Retrieved model:", saved_model.model_name)

    # Check tenant isolation.
    other_tenant_model = repository.get_by_id(
        tenant_id="tenant-other",
        model_id=model_id,
    )

    assert other_tenant_model is None
    print("Cross-tenant lookup blocked:", other_tenant_model is None)
