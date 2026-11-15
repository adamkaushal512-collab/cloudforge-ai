from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from cloudforge.repositories.models import IdempotencyRecord

# Status code stored while a reservation is still inside its
# creating transaction. Because reserve, work, and complete all
# happen in one transaction, other sessions never observe this
# value under READ COMMITTED isolation.
PENDING_STATUS_CODE = 0


class IdempotencyRepository:
    """Database operations for tenant-scoped idempotency records."""

    def __init__(self, session: Session):
        # The caller owns the transaction boundaries.
        self.session = session

    def reserve(
        self,
        tenant_id: str,
        operation: str,
        idempotency_key: str,
        request_hash: str,
    ) -> bool:
        """
        Try to claim a key inside the current transaction.

        Returns True when this transaction now owns the key.
        Returns False when a committed record already exists.

        If another transaction holds an uncommitted reservation
        for the same key, PostgreSQL blocks this INSERT on the
        unique index until that transaction commits (returns False)
        or rolls back (this reservation succeeds).
        """

        statement = (
            pg_insert(IdempotencyRecord)
            .values(
                tenant_id=tenant_id,
                operation=operation,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                response_body={},
                status_code=PENDING_STATUS_CODE,
            )
            .on_conflict_do_nothing(
                constraint="uq_idempotency_tenant_operation_key",
            )
            .returning(IdempotencyRecord.id)
        )

        return self.session.execute(statement).scalar_one_or_none() is not None

    def get(
        self,
        tenant_id: str,
        operation: str,
        idempotency_key: str,
    ) -> IdempotencyRecord | None:
        """Find a record within a tenant and operation scope."""

        statement = select(IdempotencyRecord).where(
            IdempotencyRecord.tenant_id == tenant_id,
            IdempotencyRecord.operation == operation,
            IdempotencyRecord.idempotency_key == idempotency_key,
        )

        return self.session.scalar(statement)

    def complete(
        self,
        tenant_id: str,
        operation: str,
        idempotency_key: str,
        status_code: int,
        response_body: dict[str, Any],
    ) -> None:
        """Store the final response for a reserved key."""

        statement = (
            update(IdempotencyRecord)
            .where(
                IdempotencyRecord.tenant_id == tenant_id,
                IdempotencyRecord.operation == operation,
                IdempotencyRecord.idempotency_key == idempotency_key,
                IdempotencyRecord.status_code == PENDING_STATUS_CODE,
            )
            .values(
                status_code=status_code,
                response_body=response_body,
            )
        )

        result = self.session.execute(statement)

        if result.rowcount != 1:
            raise RuntimeError(
                "Idempotency reservation missing or already completed"
            )
