from typing import Any, Dict, List, Optional
from fastapi import Depends, APIRouter, Query
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Bond, GridSize, Mounting
from app.models.bond_to_code import BondToCode
from app.models.catalog import Catalog
from app.schemas.data_schema import CategorySchema, FilterResponseSchema
from app.models.categories import Categories

router = APIRouter(
    prefix="/api",
    tags=["Products"]
)


@router.get("/filters", response_model=FilterResponseSchema, response_model_exclude_none=True)
async def get_sidebar_filters(
        db: Session = Depends(get_db),
        category_id: Optional[int] = Query(None)
):
    bond_query = db.query(Bond).join(BondToCode, Bond.id == BondToCode.bond_id).join(Catalog, Catalog.id == BondToCode.code_id)
    if category_id:
        bond_query = bond_query.filter(Catalog.category_id == category_id)
    bonds = bond_query.distinct().order_by(Bond.name_bond).all()

    response_data: Dict[str, Any] = {
        "bonds": bonds,
    }

    if category_id != 2:
        grid_query = db.query(GridSize).join(Catalog, Catalog.grid_size_id == GridSize.id)
        if category_id:
            grid_query = grid_query.filter(Catalog.category_id == category_id)
        grids = grid_query.distinct().order_by(GridSize.grid_size).all()
        response_data["grids"] = grids
    
    if category_id != 1:
        mounting_query = db.query(Mounting).join(Catalog, Catalog.mounting_id == Mounting.id)
        if category_id:
            mounting_query = mounting_query.filter(Catalog.category_id == category_id)
        mountings = mounting_query.distinct().order_by(Mounting.mm).all()
        response_data["mountings"] = mountings

    return FilterResponseSchema(**response_data)

@router.get("/categories", response_model=List[CategorySchema])
async def get_categories(
        db: Session = Depends(get_db)
):
    categories = db.query(Categories).all()
    return categories