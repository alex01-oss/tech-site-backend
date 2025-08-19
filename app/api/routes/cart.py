import logging

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from starlette import status

from app.api.dependencies import get_db
from app.core.security import get_current_user
from app.models import User, Catalog
from app.models.bond_to_code import BondToCode
from app.models.cart_item import CartItem
from app.schemas.cart_schema import CartListResponse, CartRequest, CartResponse, GetCartResponse, \
    UpdateCartItemRequest
from app.schemas.catalog_schema import CatalogItemSchema, MountingSchema

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
    logger.info(f"Fetching cart for user: {user.id}")

    cart_items = db.query(CartItem).options(
        joinedload(CartItem.catalog)
            .joinedload(Catalog.shape),
        joinedload(CartItem.catalog)
            .joinedload(Catalog.grid_size),
        joinedload(CartItem.catalog)
            .joinedload(Catalog.mounting),
        joinedload(CartItem.catalog)
            .joinedload(Catalog.bond_to_codes)
            .joinedload(BondToCode.bond)
    ).filter_by(user_id=user.id).all()

    cart = []
    for item in cart_items:
        product = item.catalog
        if not product:
            logger.warning(f"Product with id {item.product_id} not found for cart item {item.id}")
            continue

        name_bonds = [btc.bond.name_bond for btc in product.bond_to_codes]

        product_schema = CatalogItemSchema(
            id=int(product.id),
            code=str(product.code),
            shape=product.shape.shape,
            dimensions=str(product.dimensions),
            images=product.shape.img_url,
            grid_size=product.grid_size.grid_size,
            mounting=MountingSchema(
                mm=product.mounting.mm,
                inch=product.mounting.inch
            ) if product.mounting else None,
            is_in_cart=True,
            name_bonds=name_bonds
        )

        cart.append(GetCartResponse(
            product=product_schema,
            quantity=item.quantity,
        ))

    return CartListResponse(cart=cart)


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
        item: CartRequest,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not item.product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID is empty")

    catalog_item = db.query(Catalog).filter_by(id=item.product_id).first()
    if not catalog_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found in catalog")

    existing_item = db.query(CartItem).filter_by(user_id=user.id, product_id=item.product_id).first()
    if existing_item:
        logger.info(f"User {user.id} attempted to add existing item {item.product_id} to cart.")
        return CartResponse(message="Item already in cart")

    new_item = CartItem(
        user_id=user.id,
        product_id=item.product_id,
        quantity=1,
    )
    db.add(new_item)
    db.commit()

    logger.info(f"User {user.id} added new item {item.product_id} to cart.")
    return CartResponse(message="Item added to cart")


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_from_cart(
        item_id: int,
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if not item_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item ID is empty")

    item = db.query(CartItem).filter_by(user_id=user.id, product_id=item_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    db.delete(item)
    db.commit()
    logger.info(f"User {user.id} removed item {item_id} from cart.")

    return CartResponse(message="Successfully removed from cart")


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
        item_id: int,
        data: UpdateCartItemRequest,
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    item = db.query(CartItem).filter_by(user_id=user.id, product_id=item_id).first()

    if data.quantity == 0:
        if item:
            db.delete(item)
            db.commit()
            logger.info(f"User {user.id} removed item {item_id} from cart by setting quantity to 0.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    if item:
        item.quantity = data.quantity
        logger.info(f"User {user.id} updated quantity for item {item_id} to {data.quantity}.")
    else:
        item = CartItem(
            user_id=user.id,
            product_id=item_id,
            quantity=data.quantity
        )
        db.add(item)
        logger.info(f"User {user.id} added new item {item_id} with quantity {data.quantity} to cart.")

    db.commit()
    db.refresh(item)
    return CartResponse(message="Successfully updated cart")


@router.get("/count", response_model=int)
async def get_cart_count(
        db: Session = Depends(get_db),
        user: User = Depends(get_current_user)
):
    total_quantity = db.query(
        func.coalesce(func.sum(CartItem.quantity), 0)
    ).filter_by(user_id=user.id).scalar()

    return total_quantity
