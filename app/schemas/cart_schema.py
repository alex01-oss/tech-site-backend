from typing import Optional, List

from pydantic import BaseModel, constr, conint


class CartItemRequest(BaseModel):
    code: str
    shape: str
    dimensions: str
    images: str

class CartAddedResponse(BaseModel):
    message: str

class CartRemoveRequest(BaseModel):
    code: str

class CartRemovedResponse(BaseModel):
    message: str

# in soon
class CartUpdate(BaseModel):
    code: constr(strip_whitespace=True, min_length=1)
    quantity: conint(gt=0)

class CartResponse(BaseModel):
    user_id: int
    code: constr(strip_whitespace=True, min_length=1)
    shape: Optional[str]
    dimensions: Optional[str]
    images: Optional[str]
    quantity: int

    class Config:
        from_attributes = True

class CartListResponse(BaseModel):
    cart: List[CartResponse]