import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, and_, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import ProductGrindingWheels, EquipmentModel, EquipmentCode, ProducerName


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
    try:
        results = (
            db.query(distinct(ProductGrindingWheels.code))
            .filter(func.lower(ProductGrindingWheels.code).like(f'%{q.lower()}%'))
            .order_by(ProductGrindingWheels.code)
            .limit(10)
            .all()
        )
        return [r[0] for r in results]
    except Exception as e:
        logging.error(f"Error in autocomplete_code: {e}", exc_info=True)
        return []


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
    try:
        results = (
            db.query(distinct(ProductGrindingWheels.shape))
            .filter(func.lower(ProductGrindingWheels.shape).like(f'%{q.lower()}%'))
            .order_by(ProductGrindingWheels.shape)
            .limit(10)
            .all()
        )
        return [r[0] for r in results]
    except Exception as e:
        logging.error(f"Error in autocomplete_code: {e}", exc_info=True)
        return []


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
    try:
        results = (
            db.query(distinct(ProductGrindingWheels.dimensions))
            .filter(func.lower(ProductGrindingWheels.dimensions).like(f'%{q.lower()}%'))
            .order_by(ProductGrindingWheels.dimensions)
            .limit(10)
            .all()
        )
        return [r[0] for r in results]
    except Exception as e:
        logging.error(f"Error in autocomplete_code: {e}", exc_info=True)
        return []


@router.get('/machine', response_model=List[str])
async def autocomplete_machine(
        q: str = Query(
            ...,
            min_length=1,
            description="Query string for product machine name autocomplete"
        ),
        db: Session = Depends(get_db)
):
    try:
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
    except Exception as e:
        logging.error(f"Error in autocomplete_code: {e}", exc_info=True)
        return []
