import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import EquipmentModel, EquipmentCode, Catalog, Producer, Shape
from app.utils.autocomplete_util import get_autocomplete_results

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix='/api/autocomplete',
    tags=['Autocomplete']
)


@router.get('/code', response_model=List[str])
async def autocomplete_code(
        q: str = Query(
            ...,
            min_length=1,
            max_length=5,
            description="Query string for product code autocomplete"
        ),
        db: Session = Depends(get_db)
):
    return get_autocomplete_results(db, Catalog.code, q)


@router.get('/shape', response_model=List[str])
async def autocomplete_shape(
        q: str = Query(
            ...,
            min_length=1,
            max_length=6,
            description="Query string for product shape autocomplete"
        ),
        db: Session = Depends(get_db)
):
    results = (
        db.query(Shape.shape)
        .join(Catalog, Catalog.shape_id == Shape.id)
        .filter(func.lower(Shape.shape).like(f'{q.lower()}%'))
        .distinct()
        .order_by(Shape.shape)
        .all()
    )
    return [r[0] for r in results]


@router.get('/dimensions', response_model=List[str])
async def autocomplete_dimensions(
        q: str = Query(
            ...,
            min_length=1,
            max_length=25,
            description="Query string for product dimensions autocomplete"
        ),
        db: Session = Depends(get_db)
):
    return get_autocomplete_results(db, Catalog.dimensions, q)


@router.get('/machine', response_model=List[str])
async def autocomplete_machine(
        q: str = Query(
            ...,
            min_length=1,
            description="Query string for product machine name autocomplete"
        ),
        db: Session = Depends(get_db)
):
    machine_query = (
        select(EquipmentModel.model.label("name"))
        .join(EquipmentCode, EquipmentCode.equipment_model_id == EquipmentModel.id)
        .join(Catalog, Catalog.id == EquipmentCode.catalog_id)
        .filter(func.lower(EquipmentModel.model).like(f"{q.lower()}%"))
        .distinct()
    )

    producer_query = (
        select(Producer.name_producer.label("name"))
        .join(EquipmentModel, EquipmentModel.producer_id == Producer.id)
        .join(EquipmentCode, EquipmentCode.equipment_model_id == EquipmentModel.id)
        .join(Catalog, Catalog.id == EquipmentCode.catalog_id)
        .filter(func.lower(Producer.name_producer).like(f"{q.lower()}%"))
        .distinct()
    )

    combined_query = machine_query.union(producer_query)

    subquery_alias = combined_query.subquery()

    results_query = (
        db.query(subquery_alias.c.name)
        .distinct()
        .order_by(subquery_alias.c.name)
        .limit(10)
    )

    results = results_query.all()

    return [r[0] for r in results]
