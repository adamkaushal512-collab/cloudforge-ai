"""
Manual smoke check: insert and read back one AIModel via the ORM.

COMMITS a row to DATABASE_URL (default: local cloudforge_db).
Not part of the pytest suite. Usage:

    python scripts/dev_smoke_insert.py --confirm-dev-write
"""

from sqlalchemy import select

from _dev_guard import require_write_confirmation


def main() -> None:
    require_write_confirmation(__doc__)

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


if __name__ == "__main__":
    main()
