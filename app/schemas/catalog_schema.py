from typing import List, Optional, Literal

from pydantic import BaseModel, Field


class CatalogQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    items_per_page: int = Field(default=8, ge=1)
    search: str = ""
    search_type: Optional[Literal["code", "shape", "dimensions", "equipment"]] = "code"
    name_bond: Optional[str] = None
    grid_size: Optional[str] = None


class CatalogItemSchema(BaseModel):
    code: str
    shape: Optional[str] = None
    dimensions: Optional[str] = None
    name_bond: Optional[str] = None
    grid_size: Optional[str] = None
    is_in_cart: bool = False

    class Config:
        from_attributes = True


class CatalogResponseSchema(BaseModel):
    items: List[CatalogItemSchema]
    total_items: int
    total_pages: int
    current_page: int
    items_per_page: int
