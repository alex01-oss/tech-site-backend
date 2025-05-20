from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.core.security import get_current_user_optional
from app.models import ProductGrindingWheels, EquipmentCode, EquipmentModel, Bond
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.catalog_schema import EquipmentModelSchema, CatalogItemDetailedSchema, CatalogItemSchema

get_catalog_item_router = APIRouter()


@get_catalog_item_router.get("/api/catalog/{code}", response_model=CatalogItemDetailedSchema)
async def get_cart(
        code: str,
        db: Session = Depends(get_db),
        user: Optional[User] = Depends(get_current_user_optional)
):
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

    return CatalogItemDetailedSchema(
        item=product,
        bond=bond,
        machines=machines
    )
