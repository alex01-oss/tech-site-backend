from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.catalog_item import CatalogItem
from app.models.user import User
from app.schemas.cart_schema import CartResponse, CartRequest

add_router = APIRouter()

@add_router.post("/api/cart", response_model=CartResponse)
async def add_to_cart(
    item: CartRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if not item.code:
            raise HTTPException(status_code=400, detail="Article is empty")

        catalog_item = db.query(CatalogItem).filter_by(code=item.code).first()
        if not catalog_item:
            raise HTTPException(status_code=404, detail="Product not found in catalog")

        existing_item = db.query(CartItem).filter_by(user_id=user.id, product_code=item.code).first()
        if existing_item:
            return {"message": "item already in cart"}

        new_item = CartItem(
            user_id=user.id,
            product_code=item.code,
            quantity=1,
        )
        db.add(new_item)
        db.commit()

        return {"message": "item added to cart"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
