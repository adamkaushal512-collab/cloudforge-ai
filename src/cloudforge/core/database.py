import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local development default.
# Production must supply a secure DATABASE_URL.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg:///cloudforge_db",
)

# Create SQLAlchemy's database engine.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Factory for creating database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)
