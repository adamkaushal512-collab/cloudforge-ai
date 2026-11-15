from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON, UniqueConstraint


# Base class for SQLAlchemy ORM models.
class Base(DeclarativeBase):
    pass


# Python class mapped to the ai_models database table.
class AIModel(Base):
    __tablename__ = "ai_models"

    # Unique identifier for each registration.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    # Identifies the engineering team that owns the model.
    tenant_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Name of the AI model.
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Example: bedrock or vllm.
    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Maximum allowed output tokens.
    max_tokens: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
class IdempotencyRecord(Base):
    """
    Stores the result of a previously processed API request.
    """

    __tablename__ = "idempotency_records"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "operation",
            "idempotency_key",
            name="uq_idempotency_tenant_operation_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    tenant_id: Mapped[str] = mapped_column(nullable=False)

    operation: Mapped[str] = mapped_column(nullable=False)

    idempotency_key: Mapped[str] = mapped_column(nullable=False)

    request_hash: Mapped[str] = mapped_column(nullable=False)

    response_body: Mapped[dict] = mapped_column(JSON, nullable=False)

    status_code: Mapped[int] = mapped_column(nullable=False)