from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class CatalogQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=8, ge=1, le=100)
    search: str = ""
    search_type: Optional[Literal["code", "shape", "dimensions", "machine"]] = "code"
    name_bond: Optional[str] = None
    grid_size: Optional[str] = None


class BondSchema(BaseModel):
    name_bond: str
    bond_description: str
    bond_cooling: str

    class Config:
        from_attributes = True


class EquipmentModelSchema(BaseModel):
    name_equipment: str
    name_producer: str

    class Config:
        from_attributes = True


class CatalogItemSchema(BaseModel):
    code: str
    shape: Optional[str] = None
    dimensions: Optional[str] = None
    images: Optional[str] = None
    name_bond: Optional[str] = None
    grid_size: Optional[str] = None
    is_in_cart: bool = False

    class Config:
        from_attributes = True

class CatalogItemDetailedSchema(BaseModel):
    item: CatalogItemSchema
    bond: Optional[BondSchema]
    machines: List[EquipmentModelSchema] = []


class CatalogResponseSchema(BaseModel):
    items: List[CatalogItemSchema]
    total_items: int
    total_pages: int
    current_page: int
    items_per_page: int
