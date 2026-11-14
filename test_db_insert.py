from sqlalchemy import select

from cloudforge.core.database import SessionLocal
from cloudforge.repositories.models import AIModel

# Open a database session.
with SessionLocal() as session:

    # Create an AI model registration.
    model = AIModel(
        tenant_id="tenant-demo",
        model_name="claude-sonnet-demo",
        provider="bedrock",
        max_tokens=4096,
    )

    # Stage the object for insertion.
    session.add(model)

    # Commit the transaction to PostgreSQL.
    session.commit()

    # Retrieve the generated primary key.
    session.refresh(model)
    model_id = model.id

    print("Inserted model ID:", model_id)

    # Query the saved record using SQLAlchemy.
    statement = select(AIModel).where(AIModel.id == model_id)
    saved_model = session.scalar(statement)

    if saved_model is None:
        raise RuntimeError("Inserted model was not found")

    print("Tenant:", saved_model.tenant_id)
    print("Model:", saved_model.model_name)
    print("Provider:", saved_model.provider)
    print("Max tokens:", saved_model.max_tokens)
