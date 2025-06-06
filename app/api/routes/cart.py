from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.product_grinding_wheels import ProductGrindingWheels
from app.models.user import User
from app.schemas.cart_schema import CartListResponse, CartRequest, CartResponse, GetCartResponse, UpdateCartItemRequest
from sqlalchemy.orm import Session

from app.schemas.catalog_schema import CatalogItemSchema


router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"]
)


@router.get("", response_model=CartListResponse)
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


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
        item: CartRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
        if not item.code:
            raise HTTPException(status_code=400, detail="Article is empty")

        catalog_item = db.query(ProductGrindingWheels).filter_by(code=item.code).first()
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


@router.delete("/items/{code}", response_model=CartResponse)
async def remove_from_cart(
        code: str,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    try:
      if not code:
        raise HTTPException(status_code=400, detail="Article is empty")
      
      item = db.query(CartItem).filter_by(user_id=user.id, product_code=code).first()
      
      if not item:
        raise HTTPException(status_code=404, detail="Item not found")
      
      db.delete(item)
      db.commit()
      
      return CartResponse(
        message="Successfully removed from cart",
      )
        
    except Exception:
      db.rollback()
      raise HTTPException(status_code=400, detail="Failed to remove item")


@router.put("items/{code}", response_model=CartResponse)
async def update_cart_item(
    code: str,
    data: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(CartItem).filter_by(user_id=user.id, product_code=code).first()

    if data.quantity == 0:
        if item:
            db.delete(item)
            db.commit()
        raise HTTPException(status_code=204, detail="Item removed from cart")

    if item:
        item.quantity = data.quantity
    else:
        item = CartItem(
            user_id=user.id,
            product_code=code,
            quantity=data.quantity
        )
        db.add(item)

    db.commit()
    db.refresh(item)
    return item