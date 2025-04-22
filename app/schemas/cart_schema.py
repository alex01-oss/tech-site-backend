from typing import List

from pydantic import BaseModel, constr, conint

from app.schemas.catalog_schema import CatalogItemSchema


class CartRequest(BaseModel):
    code: str


class CartResponse(BaseModel):
    message: str


# in soon
class CartUpdate(BaseModel):
    code: constr(strip_whitespace=True, min_length=1)
    quantity: conint(gt=0)


class GetCartResponse(BaseModel):
    product: CatalogItemSchema
    quantity: int

    class Config:
        from_attributes = True


class CartListResponse(BaseModel):
    cart: List[GetCartResponse]
