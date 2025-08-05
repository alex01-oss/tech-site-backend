from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Categories

router = APIRouter(
    prefix='/api/categories',
    tags=['Categories']
)


@router.get("", response_model=List[str])
async def get_categories(
        db: Session = Depends(get_db)
):
    category_names = db.query(Categories.name).all()

    return [name for name, in category_names]