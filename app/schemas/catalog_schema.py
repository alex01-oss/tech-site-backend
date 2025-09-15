from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class CatalogQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=8, ge=1, le=12)

    search_code: Optional[str] = Field(default=None)
    search_shape: Optional[str] = Field(default=None)
    search_dimensions: Optional[str] = Field(default=None)
    search_machine: Optional[str] = Field(default=None)

    bond_ids: Optional[List[int]] = Field(default=None)
    grid_size_ids: Optional[List[int]] = Field(default=None)
    mounting_ids: Optional[List[int]] = Field(default=None)

    category_id: Optional[int] = None

    class Config:
        populate_by_name = True


class MountingSchema(BaseModel):
    mm: str
    model_config = ConfigDict(from_attributes=True)


class BondSchema(BaseModel):
    name_bond: str
    bond_description: str
    bond_cooling: str
    model_config = ConfigDict(from_attributes=True)


class EquipmentModelSchema(BaseModel):
    model: str
    name_producer: str
    model_config = ConfigDict(from_attributes=True)


class CatalogItemSchema(BaseModel):
    id: int
    code: str
    shape: str
    dimensions: str
    images: str
    name_bonds: Optional[List[str]] = None
    grid_size: Optional[str] = None
    mounting: Optional[MountingSchema]
    is_in_cart: bool = False
    model_config = ConfigDict(from_attributes=True)


class CatalogItemDetailedSchema(BaseModel):
    item: CatalogItemSchema
    bonds: Optional[List[BondSchema]] = None
    machines: Optional[List[EquipmentModelSchema]] = None
    mounting: Optional[MountingSchema] = None
    model_config = ConfigDict(from_attributes=True)


class CatalogResponseSchema(BaseModel):
    items: List[CatalogItemSchema]
    total_items: int
    total_pages: int
    current_page: int
    items_per_page: int
