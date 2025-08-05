from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Bond, GridSize, Mounting
from app.schemas.data_schema import CategorySchema, FilterResponseSchema
from app.models.categories import Categories

router = APIRouter(
    prefix="/api",
    tags=["Products"]
)


@router.get("/filters", response_model=FilterResponseSchema)
async def get_sidebar_filters(
        db: Session = Depends(get_db)
):
    bonds = db.query(Bond).all()
    grids = db.query(GridSize).all()
    mountings = db.query(Mounting).all()

    return FilterResponseSchema(
        bonds=bonds,
        grids=grids,
        mountings=mountings
    )

@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(
        db: Session = Depends(get_db)
):
    categories = db.query(Categories).all()
    return categories