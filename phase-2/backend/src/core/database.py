"""
Database configuration and session management using SQLModel.
Provides database engine and session creation utilities.
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from .config import settings


# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before using them
    pool_size=5,          # Connection pool size
    max_overflow=10,      # Max overflow connections
)


def create_db_and_tables():
    """
    Create all database tables defined by SQLModel models.
    Should be called on application startup.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    Automatically commits on success and rolls back on error.

    Yields:
        Session: SQLModel database session

    Example:
        @app.get("/items")
        def read_items(session: Session = Depends(get_session)):
            items = session.exec(select(Item)).all()
            return items
    """
    with Session(engine) as session:
        yield session
