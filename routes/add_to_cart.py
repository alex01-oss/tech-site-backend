import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from extensions import db, logger
from models.cart import CartItem

add_to_cart_bp = Blueprint('add_to_cart', __name__)

@add_to_cart_bp.route("/api/cart", methods=['POST'])
@jwt_required()
def add_to_cart():
    """
    Додає товар у кошик (без оновлення кількості)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        article = data.get("article")
        title = data.get("title")
        price = data.get("price")
        currency = data.get("currency")

        logger.info(f"User ID: {user_id}")
        logger.info(f"Received data: {data}")

        if not article:
            logger.warning("Missing article in request")
            return jsonify({"error": "article is required"}), 400

        item = CartItem.query.filter_by(user_id=user_id, article=article).first()
        
        if item:
            logger.info("Item already in cart")
            return jsonify({"message": "item already in cart"}), 200

        new_item = CartItem(user_id=user_id, article=article, quantity=1, title=title, price=price, currency=currency)
        db.session.add(new_item)
        db.session.commit()
        logger.info("Item successfully added to cart!")

        return jsonify({"message": "item added to cart"}), 201

    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to add item", "details": str(e)}), 500
