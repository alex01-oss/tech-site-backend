from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.dependencies import get_db
from app.models import ProductGrindingWheels, EquipmentCode, EquipmentModel, Bond
from app.schemas.catalog_schema import EquipmentModelSchema, CatalogItemDetailedSchema, CatalogItemSchema

get_catalog_item_router = APIRouter()


@get_catalog_item_router.get("/api/catalog/{code}", response_model=CatalogItemDetailedSchema)
async def get_cart(
        code: str,
        db: Session = Depends(get_db)
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

    product = CatalogItemSchema(
        code=str(item.code),
        shape=str(item.shape),
        dimensions=str(item.dimensions),
        images=item.shape_info.img_url if item.shape_info else None,
        name_bond=str(item.name_bond),
        grid_size=str(item.grid_size),
    )

    return CatalogItemDetailedSchema(
        item=product,
        bond=bond,
        machines=machines
    )
