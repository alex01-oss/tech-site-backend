import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from starlette import status

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models.cart_item import CartItem
from app.models.product_grinding_wheels import ProductGrindingWheels
from app.models.user import User
from app.schemas.cart_schema import CartListResponse, CartRequest, CartResponse, GetCartResponse, \
    UpdateCartItemRequest
from sqlalchemy.orm import Session

from app.schemas.catalog_schema import CatalogItemSchema
from sqlalchemy import func

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/cart",
    tags=["Cart"]
)


@router.get("", response_model=CartListResponse)
async def get_cart(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter_by(user_id=user.id).all()

    cart = []
    for item in cart_items:
        product = item.product
        if not product:
            logger.warning(f"Product with code {item.product_code} not found for user {user.id} in cart.")
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


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
        item: CartRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not item.code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Article is empty")

    catalog_item = db.query(ProductGrindingWheels).filter_by(code=item.code).first()
    if not catalog_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found in catalog")

    existing_item = db.query(CartItem).filter_by(user_id=user.id, product_code=item.code).first()
    if existing_item:
        logger.info(f"User {user.id} attempted to add existing item {item.code} to cart.")
        return CartResponse(message="Item already in cart")

    new_item = CartItem(
        user_id=user.id,
        product_code=item.code,
        quantity=1,
    )
    db.add(new_item)
    db.commit()

    logger.info(f"User {user.id} added new item {item.code} to cart.")
    return CartResponse(message="Item added to cart")


@router.delete("/items/{code}", response_model=CartResponse)
async def remove_from_cart(
        code: str,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article is empty")

    item = db.query(CartItem).filter_by(user_id=user.id, product_code=code).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()
    logger.info(f"User {user.id} removed item {code} from cart.")

    return CartResponse(message="Successfully removed from cart")


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
            logger.info(f"User {user.id} removed item {code} from cart by setting quantity to 0.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if item:
        item.quantity = data.quantity
        logger.info(f"User {user.id} updated quantity for item {code} to {data.quantity}.")
    else:
        item = CartItem(
            user_id=user.id,
            product_code=code,
            quantity=data.quantity
        )
        db.add(item)
        logger.info(f"User {user.id} added new item {code} with quantity {data.quantity} to cart.")

    db.commit()
    db.refresh(item)
    return item


@router.get("/count", response_model=int)
async def get_cart_count(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    total_quantity = db.query(
        func.coalesce(func.sum(CartItem.quantity), 0)
    ).filter_by(user_id=user.id).scalar()

    return total_quantity
