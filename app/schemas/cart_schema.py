from typing import List

from pydantic import BaseModel, Field

from app.schemas.catalog_schema import CatalogItemSchema


class CartRequest(BaseModel):
    product_id: int


class CartResponse(BaseModel):
    message: str


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(..., ge=1)


class GetCartResponse(BaseModel):
    product: CatalogItemSchema
    quantity: str

    class Config:
        from_attributes = True


class CartListResponse(BaseModel):
    cart: List[GetCartResponse]
