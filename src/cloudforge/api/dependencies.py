from collections.abc import Generator

from sqlalchemy.orm import Session

from cloudforge.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per API request."""

    # Create a session for this request.
    with SessionLocal() as session:
        # FastAPI injects this session into the endpoint.
        yield session

    # The context manager closes the session.
    # Any uncommitted transaction is rolled back.
