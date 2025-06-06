import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, logger
from app.api.dependencies import get_db
from app.core.security import get_current_user_optional
from app.models.bond import Bond
from app.models.cart_item import CartItem
from app.models.equipment_code import EquipmentCode
from app.models.equipment_model import EquipmentModel
from app.models.product_grinding_wheels import ProductGrindingWheels
from app.models.user import User
from app.schemas.catalog_schema import CatalogItemDetailedSchema, CatalogItemSchema, CatalogQuerySchema, CatalogResponseSchema, EquipmentModelSchema
from sqlalchemy.orm import Session, joinedload
from app.utils.cache import cache_get, cache_set


router = APIRouter(
    prefix="/api/catalog",
    tags=["Authorization"]
)


@router.get("", response_model=CatalogResponseSchema)
async def get_catalog_items(
        query_params: CatalogQuerySchema = Depends(),
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        cache_key = f"catalog:{query_params.page}:{user.id if user else 0}"
        cached = cache_get(cache_key)
        if cached:
            return cached

        query = db.query(ProductGrindingWheels).options(
            joinedload(ProductGrindingWheels.bond),
            joinedload(ProductGrindingWheels.shape_info)
        )

        if query_params.search:
            search_query = query_params.search.lower()

            if query_params.search_type == 'code':
                query = query.filter(ProductGrindingWheels.code.ilike(f"%{search_query}%"))

            elif query_params.search_type == 'shape':
                query = query.filter(ProductGrindingWheels.shape.ilike(f"%{search_query}%"))

            elif query_params.search_type == 'dimensions':
                query = query.filter(ProductGrindingWheels.dimensions.ilike(f"%{search_query}%"))

            elif query_params.search_type == 'machine':
                query = query.join(EquipmentCode, EquipmentCode.code == ProductGrindingWheels.code) \
                    .join(EquipmentModel, EquipmentCode.name_equipment == EquipmentModel.name_equipment) \
                    .filter(EquipmentModel.name_equipment.ilike(f"%{search_query}%"))

        if query_params.name_bond:
            query = query.filter(ProductGrindingWheels.name_bond == query_params.name_bond)

        if query_params.grid_size:
            query = query.filter(ProductGrindingWheels.grid_size == query_params.grid_size)

        total_items = query.count()
        total_pages = math.ceil(total_items / query_params.items_per_page) if total_items > 0 else 1
        offset = (query_params.page - 1) * query_params.items_per_page
        catalog_items = query.offset(offset).limit(query_params.items_per_page).all()

        cart_product_codes = set()
        if user:
            cart_items = db.query(CartItem.product_code).filter_by(user_id=user.id).all()
            cart_product_codes = {item.product_code for item in cart_items}

        items = []
        for item in catalog_items:
            is_in_cart = item.code in cart_product_codes if user else False
            image_url = item.shape_info.img_url if item.shape_info else None

            catalog_item = CatalogItemSchema(
                code=str(item.code),
                shape=str(item.shape),
                dimensions=str(item.dimensions),
                images=image_url,
                name_bond=str(item.name_bond),
                grid_size=str(item.grid_size),
                is_in_cart=is_in_cart
            )

            items.append(catalog_item)

        response = CatalogResponseSchema(
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=query_params.page,
            items_per_page=query_params.items_per_page
        )

        return response

    except Exception as e:
        import traceback
        error_msg = f"Failed to load catalog data: {str(e)}\nTraceback: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_msg)
    
    
@router.get("/{code}", response_model=CatalogItemDetailedSchema)
async def get_catalog_item(
    code: str,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        cache_key = f"catalog_data:{code}"
        cached_data = cache_get(cache_key)
        if cached_data:
            return CatalogItemDetailedSchema(**cached_data)

        item = db.query(ProductGrindingWheels).options(
            joinedload(ProductGrindingWheels.equipment_codes)
            .joinedload(EquipmentCode.equipment_model)
            .joinedload(EquipmentModel.producer),
            joinedload(ProductGrindingWheels.shape_info)
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

        bond = db.query(Bond).filter(Bond.name_bond == item.name_bond).first()
        image_url = item.shape_info.img_url if item.shape_info else None

        is_in_cart = False
        if user:
            cart_item = db.query(CartItem.product_code).filter_by(user_id=user.id, product_code=code).first()
            is_in_cart = cart_item is not None

        product = CatalogItemSchema(
            code=str(item.code),
            shape=str(item.shape),
            dimensions=str(item.dimensions),
            images=image_url,
            name_bond=str(item.name_bond),
            grid_size=str(item.grid_size),
            is_in_cart=is_in_cart
        )

        response = CatalogItemDetailedSchema(
            item=product,
            bond=bond,
            machines=machines
        )

        cache_set(cache_key, response.dict())
        return response

    except Exception as e:
        logger.error(f"Error in get_catalog_item: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")