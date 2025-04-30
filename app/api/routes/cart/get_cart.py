from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.cart_schema import GetCartResponse, CartListResponse

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
            if not item.product:
                continue

            cart.append(GetCartResponse(
                product=item.product,
                quantity=item.product.quantity,
            ))

        return CartListResponse(cart=cart)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
