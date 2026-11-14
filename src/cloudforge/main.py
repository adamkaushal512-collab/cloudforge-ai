from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from cloudforge.api.dependencies import get_db
from cloudforge.api.schemas import (
    ModelRegistrationRequest,
    ModelRegistrationResponse,
)
from cloudforge.repositories.model_repository import ModelRepository

app = FastAPI(
    title="CloudForge AI Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post(
    "/v1/models",
    status_code=201,
    response_model=ModelRegistrationResponse,
)
def register_model(
    request: ModelRegistrationRequest,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """Register an AI model in PostgreSQL."""

    repository = ModelRepository(db)

    # Temporary development tenant.
    # Authentication will supply this in Phase 3.4.
    tenant_id = "tenant-demo"

    try:
        model = repository.create(
            tenant_id=tenant_id,
            model_name=request.model_name,
            provider=request.provider,
            max_tokens=request.max_tokens,
        )

        # Commit the transaction before returning success.
        db.commit()

        return {
            "message": "Model registered successfully",
            "model_name": model.model_name,
            "provider": model.provider,
        }

    except Exception:
        db.rollback()
        raise
