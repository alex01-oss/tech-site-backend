import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import ProductGrindingWheels, EquipmentModel, EquipmentCode, ProducerName
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
    return get_autocomplete_results(db, ProductGrindingWheels.code, q)


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
    return get_autocomplete_results(db, ProductGrindingWheels.shape, q)


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
    return get_autocomplete_results(db, ProductGrindingWheels.dimensions, q)


@router.get('/machine', response_model=List[str])
async def autocomplete_machine(
        q: str = Query(
            ...,
            min_length=1,
            description="Query string for product machine name autocomplete"
        ),
        db: Session = Depends(get_db)
):
    machine_select = (
        select(EquipmentModel.name_equipment.label("name"))
        .join(EquipmentCode, and_(EquipmentCode.name_equipment == EquipmentModel.name_equipment))
        .join(ProductGrindingWheels, and_(EquipmentCode.code == ProductGrindingWheels.code))
        .filter(func.lower(EquipmentModel.name_equipment).like(f"{q.lower()}%"))
    )

    producer_select = (
        select(ProducerName.name_producer.label("name"))
        .join(EquipmentModel, and_(ProducerName.name_producer == EquipmentModel.name_producer))
        .join(EquipmentCode, and_(EquipmentCode.name_equipment == EquipmentModel.name_equipment))
        .join(ProductGrindingWheels, and_(EquipmentCode.code == ProductGrindingWheels.code))
        .filter(func.lower(ProducerName.name_producer).like(f"{q.lower()}%"))
    )

    combined_select = machine_select.union(producer_select)

    subquery_alias = combined_select.subquery()

    results_query = (
        db.query(subquery_alias.c.name)
        .distinct()
        .order_by(subquery_alias.c.name)
        .limit(10)
    )

    results = results_query.all()

    return [r[0] for r in results]
