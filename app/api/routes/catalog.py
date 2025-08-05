import logging
import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.core.security import get_current_user_optional
from app.models import (Catalog, EquipmentModel, EquipmentCode, CartItem, User, BondToCode, Shape)
from app.schemas.catalog_schema import (CatalogQuerySchema, CatalogResponseSchema, CatalogItemDetailedSchema,
                                        EquipmentModelSchema, BondSchema, CatalogItemSchema, MountingSchema)
from app.utils.cache import cache_get, cache_set
from app.utils.catalog_helpers import make_cache_key, parse_query_params

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/catalog",
    tags=["Catalog"]
)


@router.get("", response_model=CatalogResponseSchema)
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

    query = db.query(Catalog).options(
        joinedload(Catalog.shape),
        joinedload(Catalog.grid_size),
        joinedload(Catalog.category),
        joinedload(Catalog.mounting),
        joinedload(Catalog.equipment_codes)
            .joinedload(EquipmentCode.equipment_model)
            .joinedload(EquipmentModel.producer),
        joinedload(Catalog.bond_to_codes)
            .joinedload(BondToCode.bond)
    )

    if query_params.search_code:
        query = query.filter(func.lower(Catalog.code).like(f"%{query_params.search_code.lower()}%"))

    if query_params.search_shape:
        query = query.join(Catalog.shape).filter(func.lower(Shape.shape).like(f"%{query_params.search_shape.lower()}%"))

    if query_params.search_dimensions:
        query = query.filter(func.lower(Catalog.dimensions).like(f"%{query_params.search_dimensions.lower()}%"))

    if query_params.search_machine:
        query = query.join(Catalog.equipment_codes) \
            .join(EquipmentCode.equipment_model) \
            .filter(func.lower(EquipmentModel.model).like(f"%{query_params.search_machine.lower()}%"))

    if query_params.bond_ids:
        query = query.join(Catalog.bond_to_codes).filter(BondToCode.bond_id.in_(query_params.bond_ids))

    if query_params.grid_size_ids:
        query = query.filter(Catalog.grid_size_id.in_(query_params.grid_size_ids))

    if query_params.mounting_ids:
        query = query.filter(Catalog.mounting_id.in_(query_params.mounting_ids))

    if query_params.category_id:
        query = query.filter(Catalog.category_id == query_params.category_id)

    query = query.distinct()

    total_items = query.count()
    total_pages = math.ceil(total_items / query_params.items_per_page) or 1
    offset = (query_params.page - 1) * query_params.items_per_page
    catalog_items = query.offset(offset).limit(query_params.items_per_page).all()

    cart_product_ids = set()
    if user:
        cart_items = db.query(CartItem.product_id).filter_by(user_id=user.id).all()
        cart_product_ids = {item.product_id for item in cart_items}

    items = [
        CatalogItemSchema(
            code=str(item.code),
            shape=item.shape.shape,
            dimensions=str(item.dimensions),
            images=item.shape.img_url,
            grid_size=item.grid_size.grid_size,
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


@router.get("/{item_id}", response_model=CatalogItemDetailedSchema)
async def get_catalog_item(
        item_id: int,
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    cache_key = f"catalog_data:{item_id}"
    cached = await cache_get(cache_key)
    if cached:
        return CatalogItemDetailedSchema(**cached)

    item = db.query(Catalog).options(
        joinedload(Catalog.mounting),
        joinedload(Catalog.equipment_codes)
            .joinedload(EquipmentCode.equipment_model),
        joinedload(Catalog.bond_to_codes)
            .joinedload(BondToCode.bond),
        joinedload(Catalog.shape),
        joinedload(Catalog.grid_size)
    ).filter(Catalog.id == item_id).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    is_in_cart = False
    if user:
        cart_item = db.query(CartItem).filter_by(user_id=user.id, product_id=item_id).first()
        is_in_cart = cart_item is not None

    machines = [
        EquipmentModelSchema(
            model=ec.equipment_model.model,
            name_producer=ec.equipment_model.producer.name_producer
        )
        for ec in item.equipment_codes
    ]

    bonds = [BondSchema.model_validate(btc.bond) for btc in item.bond_to_codes]

    product = CatalogItemSchema(
        code=str(item.code),
        shape=item.shape.shape,
        dimensions=str(item.dimensions),
        images=item.shape.img_url,
        grid_size=item.grid_size.grid_size,
        is_in_cart=is_in_cart,
    )

    response = CatalogItemDetailedSchema(
        item=product,
        bonds=bonds,
        machines=machines,
        mounting=MountingSchema.model_validate(item.mounting) if item.mounting else None
    )

    await cache_set(cache_key, response.model_dump(), ex=600)
    return response