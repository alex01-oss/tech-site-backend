import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models import EquipmentModel, EquipmentCode, Catalog, Producer, Shape
from app.utils.apply_catalog_filters import apply_catalog_filters

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
        db: Session = Depends(get_db),
        category_id: Optional[int] = Query(None),
        search_shape: Optional[str] = Query(None),
        search_dimensions: Optional[str] = Query(None),
        search_machine: Optional[str] = Query(None),
        bond_ids: Optional[list[str]] = Query(None),
        grid_size_ids: Optional[list[str]] = Query(None),
        mounting_ids: Optional[list[str]] = Query(None),
):
    base_query = select(Catalog.code).distinct().filter(func.lower(Catalog.code).like(f'%{q.lower()}%'))
    
    search_params = {
        'category_id': category_id,
        'search_shape': search_shape,
        'search_dimensions': search_dimensions,
        'search_machine': search_machine,
        'bond_ids': bond_ids,
        'grid_size_ids': grid_size_ids,
        'mounting_ids': mounting_ids
    }
    query = apply_catalog_filters(base_query, search_params)
    results = db.scalars(query.order_by(Catalog.code).limit(10)).all()
    return list(results)


@router.get('/shape', response_model=List[str])
async def autocomplete_shape(
        q: str = Query(
            ...,
            min_length=0,
            max_length=6,
            description="Query string for product shape autocomplete",
        ),
        db: Session = Depends(get_db),
        category_id: Optional[int] = Query(None),
        search_code: Optional[str] = Query(None),
        search_dimensions: Optional[str] = Query(None),
        search_machine: Optional[str] = Query(None),
        bond_ids: Optional[list[str]] = Query(None),
        grid_size_ids: Optional[list[str]] = Query(None),
        mounting_ids: Optional[list[str]] = Query(None),
):
    base_query = select(Shape.shape) \
        .join(Catalog, Catalog.shape_id == Shape.id) \
        .filter(func.lower(Shape.shape).like(f'{q.lower()}%'))

    search_params = {
        'category_id': category_id,
        'search_code': search_code,
        'search_dimensions': search_dimensions,
        'search_machine': search_machine,
        'bond_ids': bond_ids,
        'grid_size_ids': grid_size_ids,
        'mounting_ids': mounting_ids
    }

    query = apply_catalog_filters(base_query, search_params)
    results = db.scalars(query.distinct().order_by(Shape.shape).limit(10)).all()
    return list(results)


@router.get('/dimensions', response_model=List[str])
async def autocomplete_dimensions(
        q: str = Query(
            ...,
            min_length=1,
            max_length=25,
            description="Query string for product dimensions autocomplete"
        ),
        db: Session = Depends(get_db),
        category_id: Optional[int] = Query(None),
        search_code: Optional[str] = Query(None),
        search_shape: Optional[str] = Query(None),
        search_machine: Optional[str] = Query(None),
        bond_ids: Optional[list[str]] = Query(None),
        grid_size_ids: Optional[list[str]] = Query(None),
        mounting_ids: Optional[list[str]] = Query(None),
):
    base_query = select(Catalog.dimensions).distinct().filter(func.lower(Catalog.dimensions).like(f'%{q.lower()}%'))

    search_params = {
        'category_id': category_id,
        'search_code': search_code,
        'search_shape': search_shape,
        'search_machine': search_machine,
        'bond_ids': bond_ids,
        'grid_size_ids': grid_size_ids,
        'mounting_ids': mounting_ids
    }

    query = apply_catalog_filters(base_query, search_params)
    results = db.scalars(query.order_by(Catalog.dimensions).limit(10)).all()
    return list(results)


@router.get('/machine', response_model=List[str])
async def autocomplete_machine(
        q: str = Query(
            ...,
            min_length=1,
            description="Query string for product machine name autocomplete"
        ),
        db: Session = Depends(get_db),
        category_id: Optional[int] = Query(None),
        search_code: Optional[str] = Query(None),
        search_shape: Optional[str] = Query(None),
        search_dimensions: Optional[str] = Query(None),
        bond_ids: Optional[list[str]] = Query(None),
        grid_size_ids: Optional[list[str]] = Query(None),
        mounting_ids: Optional[list[str]] = Query(None),
):
    base_query = select(Catalog)
    
    search_params = {
        'category_id': category_id,
        'search_code': search_code,
        'search_shape': search_shape,
        'search_dimensions': search_dimensions,
        'bond_ids': bond_ids,
        'grid_size_ids': grid_size_ids,
        'mounting_ids': mounting_ids
    }
    
    filtered_query = apply_catalog_filters(base_query, search_params)
    
    catalog_ids = filtered_query.with_only_columns(Catalog.id).distinct().subquery()
    
    machine_query = (
        select(EquipmentModel.model.label("name"))
        .join(EquipmentCode, EquipmentCode.equipment_model_id == EquipmentModel.id)
        .filter(and_(
            EquipmentCode.catalog_id.in_(select(catalog_ids)),
            func.lower(EquipmentModel.model).like(f"{q.lower()}%")
        ))
        .distinct()
    )

    producer_query = (
        select(Producer.name_producer.label("name"))
        .join(EquipmentModel, EquipmentModel.producer_id == Producer.id)
        .join(EquipmentCode, EquipmentCode.equipment_model_id == EquipmentModel.id)
        .filter(and_(
            EquipmentCode.catalog_id.in_(select(catalog_ids)),
            func.lower(Producer.name_producer).like(f"{q.lower()}%")
        ))
        .distinct()
    )

    combined_query = machine_query.union(producer_query)
    results = db.scalars(combined_query.order_by("name").limit(10)).all()
    return list(results)