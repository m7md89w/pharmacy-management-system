import sqlite3

from sqlalchemy import (
    create_engine,
    event
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base
)

DATABASE_URL = "sqlite:///pharmacy.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


@event.listens_for(
    engine,
    "connect"
)
def enable_sqlite_foreign_keys(
    dbapi_connection,
    connection_record
):
    if isinstance(
        dbapi_connection,
        sqlite3.Connection
    ):
        cursor = dbapi_connection.cursor()
        cursor.execute(
            "PRAGMA foreign_keys=ON"
        )
        cursor.close()


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()