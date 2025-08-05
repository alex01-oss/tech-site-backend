from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import Bond, GridSize, Mounting
from app.schemas.filters import FilterResponseSchema, FilterItemSchema

router = APIRouter(
    prefix="/api/filters",
    tags=["Products"]
)


@router.get("", response_model=FilterResponseSchema)
async def get_sidebar_filters(
        db: Session = Depends(get_db)
):
    bonds = db.query(Bond.id, Bond.name_bond.label('name')).all()
    grids = db.query(GridSize.id, GridSize.grid_size.label('name')).all()
    mountings = db.query(Mounting.id, Mounting.mm.label('name')).all()

    return FilterResponseSchema(
        bonds=[FilterItemSchema(name=b.name) for b in bonds],
        grids=[FilterItemSchema(name=g.name) for g in grids],
        mountings=[FilterItemSchema( name=m.name) for m in mountings]
    )
