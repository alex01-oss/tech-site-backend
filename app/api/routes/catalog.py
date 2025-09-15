import logging
import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload, selectinload

from app.api.dependencies import get_db
from app.core.security import get_current_user_optional
from app.models import (Catalog, EquipmentCode, CartItem, User, BondToCode)
from app.models.equipment_model import EquipmentModel
from app.schemas.catalog_schema import (CatalogQuerySchema, CatalogResponseSchema, CatalogItemDetailedSchema,
                                        EquipmentModelSchema, BondSchema, CatalogItemSchema, MountingSchema)
from app.utils.cache import cache_get, cache_set
from app.utils.catalog_helpers import make_cache_key, parse_query_params
from app.utils.apply_catalog_filters import apply_catalog_filters

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/catalog",
    tags=["Catalog"]
)


@router.get("", response_model=CatalogResponseSchema, response_model_exclude_none=True)
async def get_catalog_items(
        query_params: CatalogQuerySchema = Depends(parse_query_params),
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    logger.info(f"Received catalog request with query_params: {query_params}")

    cache_key = make_cache_key(query_params, user.id if user else 0)
    cached = await cache_get(cache_key)

    if cached:
        logger.info(f"Returning cached catalog response for key: {cache_key}")
        return cached

    base_query = db.query(Catalog).options(
        joinedload(Catalog.shape),
        joinedload(Catalog.grid_size),
        joinedload(Catalog.mounting),
        selectinload(Catalog.bond_to_codes).joinedload(BondToCode.bond),
        selectinload(Catalog.equipment_codes).joinedload(EquipmentCode.equipment_model)
    )
    
    search_params = {
        'category_id': query_params.category_id,
        'search_code': query_params.search_code,
        'search_shape': query_params.search_shape,
        'search_dimensions': query_params.search_dimensions,
        'search_machine': query_params.search_machine,
        'bond_ids': query_params.bond_ids,
        'grid_size_ids': query_params.grid_size_ids,
        'mounting_ids': query_params.mounting_ids,
    }

    final_query = apply_catalog_filters(base_query, search_params).distinct()
    sorted_query = final_query.order_by(Catalog.id.asc())

    total_items = sorted_query.count()
    total_pages = math.ceil(total_items / query_params.items_per_page) or 1
    offset = (query_params.page - 1) * query_params.items_per_page
    catalog_items = sorted_query.offset(offset).limit(query_params.items_per_page).all()

    cart_product_ids = set()
    if user:
        cart_items = db.query(CartItem.product_id).filter_by(user_id=user.id).all()
        cart_product_ids = {item.product_id for item in cart_items}

    items = [
        CatalogItemSchema(
            id=int(item.id),
            code=str(item.code),
            shape=item.shape.shape,
            dimensions=str(item.dimensions),
            images=item.shape.img_url,
            grid_size=item.grid_size.grid_size,
            mounting=MountingSchema(mm=item.mounting.mm) if item.mounting else None,
            is_in_cart=item.id in cart_product_ids,
            name_bonds=[btc.bond.name_bond for btc in item.bond_to_codes]
        )
        for item in catalog_items
    ]

    response = CatalogResponseSchema(
        items=items,
        total_items=total_items,
        total_pages=total_pages,
        current_page=query_params.page,
        items_per_page=query_params.items_per_page
    )

    await cache_set(cache_key, response.model_dump(), ex=300)
    return response


@router.get("/{item_id}", response_model=CatalogItemDetailedSchema, response_model_exclude_none=True)
async def get_catalog_item(
        item_id: int,
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    cache_key = f"catalog_data:{item_id}"
    cached = await cache_get(cache_key)
    if cached:
        return CatalogItemDetailedSchema(**cached)

    query = db.query(Catalog).options(
        joinedload(Catalog.shape),
        joinedload(Catalog.mounting),
        joinedload(Catalog.grid_size),
        selectinload(Catalog.bond_to_codes).joinedload(BondToCode.bond),
        selectinload(Catalog.equipment_codes)
            .joinedload(EquipmentCode.equipment_model)
            .joinedload(EquipmentModel.producer),
    ).filter(Catalog.id == item_id)
    
    is_in_cart = False
    
    if user:
        query = query.outerjoin(
            CartItem,
            and_(CartItem.product_id == Catalog.id, CartItem.user_id == user.id)
        ).add_columns(CartItem.id.label('cart_item_id'))
        
        result = query.first()
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        
        item, cart_item_id = result
        is_in_cart = cart_item_id is not None
    else:
        item = query.first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

    machines = [
        EquipmentModelSchema(
            model=ec.equipment_model.model,
            name_producer=ec.equipment_model.producer.name_producer
        )
        for ec in item.equipment_codes
    ]

    bonds = [BondSchema.model_validate(btc.bond) for btc in item.bond_to_codes]
    mounting = MountingSchema.model_validate(item.mounting) if item.mounting else None

    product = CatalogItemSchema(
        id=int(item.id),
        code=str(item.code),
        shape=item.shape.shape,
        dimensions=str(item.dimensions),
        images=item.shape.img_url,
        grid_size=item.grid_size.grid_size,
        mounting=mounting,
        is_in_cart=is_in_cart
    )

    response = CatalogItemDetailedSchema(
        item=product,
        bonds=bonds,
        machines=machines,
        mounting=mounting
    )

    await cache_set(cache_key, response.model_dump(), ex=600)
    return response