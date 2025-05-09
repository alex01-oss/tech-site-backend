from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.cart_schema import GetCartResponse, CartListResponse
from app.schemas.catalog_schema import CatalogItemSchema

get_cart_router = APIRouter()


@get_cart_router.get("/api/cart", response_model=CartListResponse)
async def get_cart(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    try:
        cart_items = db.query(CartItem).filter_by(user_id=user.id).all()

        cart = []
        for item in cart_items:
            product = item.product
            if not product:
                continue

            image_url = product.shape_info.img_url if product.shape_info else None

            cart.append(GetCartResponse(
                product=CatalogItemSchema(
                    code=product.code,
                    shape=product.shape,
                    dimensions=product.dimensions,
                    images=image_url,
                    name_bond=product.name_bond,
                    grid_size=product.grid_size,
                    is_in_cart=True
                ),
                quantity=str(item.quantity),
            ))

        return CartListResponse(cart=cart)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
