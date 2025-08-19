from typing import Any, Optional

from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.catalog import Catalog


def get_autocomplete_results(
    db: Session,
    column: Any,
    q: str,
    category_id: Optional[int] = None
):
    query = db.query(distinct(column)) \
        .filter(func.lower(column).like(f'%{q.lower()}%'))
        
    if category_id:
        query = query.join(Catalog, Catalog.id == column.foreign_keys[0].parent) \
                     .filter(Catalog.category_id == category_id)

    results = query.order_by(column).limit(10).all()
    return [r[0] for r in results]