from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.user import User
from app.schemas.cart_schema import CartRequest, CartResponse

remove_router = APIRouter()

@remove_router.delete("/api/cart", response_model=CartResponse)
async def remove_from_cart(
        item: CartRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
      if not item.code:
        raise HTTPException(status_code=400, detail="Article is empty")
      
      item = db.query(CartItem).filter_by(user_id=user.id, product_code=item.code).first()
      
      if not item:
        raise HTTPException(status_code=404, detail="Item not found")
      
      db.delete(item)
      db.commit()
      
      return {"message": "item deleted from cart"}
        
    except Exception:
      db.rollback()
      raise HTTPException(status_code=400, detail="Failed to remove item")
