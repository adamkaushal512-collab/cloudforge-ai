
from typing import Annotated
import asyncio
import time
from fastapi import BackgroundTasks
from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

# Database dependency
from cloudforge.api.dependencies import get_db

# Development authentication dependency
from cloudforge.api.auth import get_current_principal

# API request and response schemas
from cloudforge.api.schemas import (
    ModelRegistrationRequest,
    ModelRegistrationResponse,
)

# Identity and authorization
from cloudforge.core.security import (
    AuthenticatedPrincipal,
    require_role,
)

# PostgreSQL repositories
from cloudforge.repositories.idempotency_repository import (
    PENDING_STATUS_CODE,
    IdempotencyRepository,
)
from cloudforge.repositories.model_repository import ModelRepository

# Idempotency helpers
from cloudforge.services.idempotency import (
    InvalidIdempotencyKeyError,
    compute_request_hash,
    validate_idempotency_key,
)

# Scope for idempotency records created by POST /v1/models.
REGISTER_MODEL_OPERATION = "POST /v1/models"


app = FastAPI(
    title="CloudForge AI Platform",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


def _registration_response(model) -> dict[str, str]:
    """Build the public response body for a registered model."""
    return {
        "message": "Model registered successfully",
        "model_name": model.model_name,
        "provider": model.provider,
    }


@app.post(
    "/v1/models",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelRegistrationResponse,
)
def register_model(
    request: ModelRegistrationRequest,
    db: Annotated[Session, Depends(get_db)],
    principal: Annotated[
        AuthenticatedPrincipal,
        Depends(get_current_principal),
    ],
    response: Response,
    idempotency_key: Annotated[
        str | None,
        Header(alias="Idempotency-Key"),
    ] = None,
) -> dict[str, str]:
    """
    Register an AI model in PostgreSQL.

    Development authentication is simulated.
    The endpoint enforces application role checks
    and uses the principal's tenant context.

    An optional Idempotency-Key header makes retries safe:
    the same key and payload replay the stored response,
    and the same key with a different payload returns 409.
    """

    # Step 1: Check whether the user has permission
    # to register AI models.
    try:
        require_role(
            principal,
            ("platform-admin", "model-admin"),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        ) from exc

    # Step 2: Obtain tenant context from the principal.
    # Never trust an arbitrary tenant_id in the request body.
    tenant_id = principal.tenant_id

    # Step 3: Initialize the database repository.
    repository = ModelRepository(db)

    # Without an idempotency key, keep the original behavior.
    if idempotency_key is None:
        try:
            # Step 4: Create the tenant-scoped model.
            model = repository.create(
                tenant_id=tenant_id,
                model_name=request.model_name,
                provider=request.provider,
                max_tokens=request.max_tokens,
            )

            # Step 5: Commit the database transaction.
            db.commit()

            # Step 6: Return a successful API response.
            return _registration_response(model)

        except Exception:
            # Roll back if the database operation fails.
            db.rollback()
            raise

    return _register_model_idempotently(
        request=request,
        db=db,
        tenant_id=tenant_id,
        repository=repository,
        response=response,
        idempotency_key=idempotency_key,
    )


def _register_model_idempotently(
    request: ModelRegistrationRequest,
    db: Session,
    tenant_id: str,
    repository: ModelRepository,
    response: Response,
    idempotency_key: str,
) -> dict[str, str]:
    """
    Reserve the key, create the model, and store the response
    in one PostgreSQL transaction.

    Concurrent duplicates block on the unique constraint until
    the first transaction finishes, then replay its committed
    response (or take over the key if it rolled back).
    """

    try:
        validate_idempotency_key(idempotency_key)
    except InvalidIdempotencyKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_idempotency_key",
                "message": str(exc),
            },
        ) from exc

    request_hash = compute_request_hash(request)
    idempotency = IdempotencyRepository(db)

    try:
        reserved = idempotency.reserve(
            tenant_id=tenant_id,
            operation=REGISTER_MODEL_OPERATION,
            idempotency_key=idempotency_key,
            request_hash=request_hash,
        )

        if not reserved:
            # A committed record exists for this key.
            record = idempotency.get(
                tenant_id=tenant_id,
                operation=REGISTER_MODEL_OPERATION,
                idempotency_key=idempotency_key,
            )
            db.rollback()

            if record is None or record.status_code == PENDING_STATUS_CODE:
                # Defensive: never replay an incomplete record.
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "idempotency_request_in_progress",
                        "message": (
                            "A request with this Idempotency-Key "
                            "is still being processed; retry later"
                        ),
                    },
                )

            if record.request_hash != request_hash:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "idempotency_key_conflict",
                        "message": (
                            "Idempotency-Key was already used "
                            "with a different request payload"
                        ),
                    },
                )

            response.status_code = record.status_code
            response.headers["Idempotent-Replayed"] = "true"
            return record.response_body

        model = repository.create(
            tenant_id=tenant_id,
            model_name=request.model_name,
            provider=request.provider,
            max_tokens=request.max_tokens,
        )
        body = _registration_response(model)

        idempotency.complete(
            tenant_id=tenant_id,
            operation=REGISTER_MODEL_OPERATION,
            idempotency_key=idempotency_key,
            status_code=status.HTTP_201_CREATED,
            response_body=body,
        )

        # Reservation, model, and stored response commit together.
        db.commit()
        return body

    except Exception:
        # Roll back the reservation and model together.
        db.rollback()
        raise


@app.get("/v1/inference/demo")
async def demo_async_inference() -> dict[str, str]:
    """
    Demonstrate nonblocking asynchronous I/O.

    This simulates an external AI inference request.
    No actual AI provider is called.
    """

    # Yield control while simulating network latency.
    await asyncio.sleep(2)

    return {
        "model": "cloudforge-demo",
        "status": "completed",
    }
def process_demo_job(job_id: str) -> None:
    """
    Simulate background AI processing.

    This is a development demonstration only.
    """
    print(f"Job {job_id}: processing started")

    # Simulate a blocking operation.
    # FastAPI runs this synchronous background
    # function in a thread pool.
    time.sleep(3)

    print(f"Job {job_id}: processing completed")


@app.post("/v1/jobs/demo", status_code=202)
def submit_demo_job(
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """
    Accept a simulated AI job and schedule
    processing after the response is generated.
    """

    job_id = "demo-job-001"

    background_tasks.add_task(
        process_demo_job,
        job_id,
    )

    return {
        "job_id": job_id,
        "status": "accepted",
    }
