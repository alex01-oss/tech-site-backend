import logging
from typing import Generator

from app.core.database import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        try:
            db.close()
        except Exception as e:
            logging.error(f"Error while closing DB session: {e}")
            raise