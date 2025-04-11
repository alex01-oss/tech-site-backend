from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.cart_schema import CartItemRequest, CartAddedResponse

add_router = APIRouter()

@add_router.post("/api/cart", response_model=CartAddedResponse)
async def add_to_cart(
    item: CartItemRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not item.code:
            raise HTTPException(status_code=400, detail="Article is empty")

        existing_item = db.query(CartItem).filter_by(user_id=user.id, code=item.code).first()
        
        if existing_item:
            return {"message": "item already in cart"}

        new_item = CartItem(
            user_id=user.id,
            code=item.code,
            shape=item.shape,
            dimensions=item.dimensions,
            quantity=1,
            images=item.images
        )

        db.add(new_item)
        db.commit()

        return {"message": "item added to cart"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
