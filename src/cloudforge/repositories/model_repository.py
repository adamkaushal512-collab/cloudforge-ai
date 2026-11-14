from sqlalchemy import select
from sqlalchemy.orm import Session

from cloudforge.repositories.models import AIModel


class ModelRepository:
    """Database operations for CloudForge AI models."""

    def __init__(self, session: Session):
        # Use the session supplied by the caller.
        self.session = session

    def create(
        self,
        tenant_id: str,
        model_name: str,
        provider: str,
        max_tokens: int,
    ) -> AIModel:
        """Insert a new model registration."""

        model = AIModel(
            tenant_id=tenant_id,
            model_name=model_name,
            provider=provider,
            max_tokens=max_tokens,
        )

        self.session.add(model)

        # Flush sends the INSERT without committing.
        # The service or caller owns the transaction.
        self.session.flush()

        return model

    def get_by_id(
        self,
        tenant_id: str,
        model_id: int,
    ) -> AIModel | None:
        """Find a model belonging to a specific tenant."""

        statement = select(AIModel).where(
            AIModel.id == model_id,
            AIModel.tenant_id == tenant_id,
        )

        return self.session.scalar(statement)
