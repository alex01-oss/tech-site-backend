import math
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.core.security import get_current_user_optional
from app.models import (ProductGrindingWheels, EquipmentModel, EquipmentCode, CartItem, User)
from app.schemas.catalog_schema import (CatalogQuerySchema, CatalogResponseSchema, CatalogItemDetailedSchema, EquipmentModelSchema)
from app.utils.cache import cache_get, cache_set
from app.utils.catalog_helpers import build_catalog_item, make_cache_key

router = APIRouter(
    prefix="/api/catalog",
    tags=["Catalog"]
)

@router.get("", response_model=CatalogResponseSchema)
async def get_catalog_items(
    query_params: CatalogQuerySchema = Depends(),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        cache_key = make_cache_key(query_params, user.id if user else 0)
        cached = await cache_get(cache_key)

        if cached:
            return cached

        query = db.query(ProductGrindingWheels).options(
            joinedload(ProductGrindingWheels.bond),
            joinedload(ProductGrindingWheels.shape_info)
        )

        if query_params.search_code:
            query = query.filter(ProductGrindingWheels.code.ilike(f"%{query_params.search_code.lower()}%"))

        if query_params.search_shape:
            query = query.filter(ProductGrindingWheels.shape.ilike(f"%{query_params.search_shape.lower()}%"))

        if query_params.search_dimensions:
            query = query.filter(ProductGrindingWheels.dimensions.ilike(f"%{query_params.search_dimensions.lower()}%"))

        if query_params.search_machine:
            query = query.join(EquipmentCode, EquipmentCode.code == ProductGrindingWheels.code) \
                         .join(EquipmentModel, EquipmentCode.name_equipment == EquipmentModel.name_equipment) \
                         .filter(EquipmentModel.name_equipment.ilike(f"%{query_params.search_machine.lower()}%"))

        if query_params.name_bond:
            query = query.filter(ProductGrindingWheels.name_bond == query_params.name_bond)

        if query_params.grid_size:
            query = query.filter(ProductGrindingWheels.grid_size == query_params.grid_size)

        total_items = query.count()
        total_pages = math.ceil(total_items / query_params.items_per_page) or 1
        offset = (query_params.page - 1) * query_params.items_per_page
        catalog_items = query.offset(offset).limit(query_params.items_per_page).all()

        cart_product_codes = set()
        if user:
            cart_items = db.query(CartItem.product_code).filter_by(user_id=user.id).all()
            cart_product_codes = {item.product_code for item in cart_items}

        items = [build_catalog_item(item, item.code in cart_product_codes) for item in catalog_items]
        
        response = CatalogResponseSchema(
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=query_params.page,
            items_per_page=query_params.items_per_page
        )

        await cache_set(cache_key, response.model_dump(), ex=300)
        return response

    except Exception as e:
        print(f"Error in get_catalog_items: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load catalog data: {str(e)}\nTraceback: {traceback.format_exc()}"
        )


@router.get("/{code}", response_model=CatalogItemDetailedSchema)
async def get_catalog_item(
        code: str,
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        cache_key = f"catalog_data:{code}"
        cached = await cache_get(cache_key)
        if cached:
            return CatalogItemDetailedSchema(**cached)

        item = db.query(ProductGrindingWheels).options(
            joinedload(ProductGrindingWheels.equipment_codes)
            .joinedload(EquipmentCode.equipment_model)
            .joinedload(EquipmentModel.producer),
            joinedload(ProductGrindingWheels.shape_info),
            joinedload(ProductGrindingWheels.bond)
        ).filter(ProductGrindingWheels.code == code).first()

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        machines = [
            EquipmentModelSchema(
                name_equipment=ec.equipment_model.name_equipment,
                name_producer=ec.equipment_model.producer.name_producer
            )
            for ec in item.equipment_codes
        ]

        is_in_cart = False
        if user:
            cart_item = db.query(CartItem).filter_by(user_id=user.id, product_code=code).first()
            is_in_cart = cart_item is not None

        product = build_catalog_item(item, is_in_cart)

        response = CatalogItemDetailedSchema(
            item=product,
            bond=item.bond,
            machines=machines
        )

        await cache_set(cache_key, response.model_dump(), ex=600)
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in get_catalog_item: {str(e)}\nTraceback: {traceback.format_exc()}"
        )