from typing import Any

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session


def get_autocomplete_results(db: Session, column: Any, q: str):
    results = (
        db.query(distinct(column))
        .filter(func.lower(column).like(f'%{q.lower()}%'))
        .order_by(column)
        .limit(10)
        .all()
    )
    return [r[0] for r in results]