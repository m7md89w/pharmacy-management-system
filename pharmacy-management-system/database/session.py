import os
import sqlite3

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


# ==================================================
# DATABASE URL
# ==================================================
# Compute an absolute path to pharmacy.db so the app works regardless
# of the working directory it is launched from.

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DB_PATH = os.path.join(_BASE_DIR, "pharmacy.db")

DATABASE_URL: str = os.environ.get("DATABASE_URL") or f"sqlite:///{_DEFAULT_DB_PATH}"


# ==================================================
# ENGINE
# ==================================================

_connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    # Required for SQLite in a multi-threaded Flask server.
    _connect_args["check_same_thread"] = False

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,  # Automatically discard stale connections.
)


# ==================================================
# FOREIGN KEY ENFORCEMENT (SQLite only)
# ==================================================

@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record  # noqa: ARG001
) -> None:
    """Enable FK constraints for every new SQLite connection."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# ==================================================
# SESSION FACTORY
# ==================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    Dependency-injection generator for database sessions.
    Usage example (Flask):
        db = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()