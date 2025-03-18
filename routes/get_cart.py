import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from extensions import logger
from schemas.cart_wood_schema import CartWoodResponseSchema as WoodCart
from models.cart_wood import CartWoodItem
from extensions import cache

get_cart_bp = Blueprint('get_cart', __name__)

@cache.cached(timeout=5)
@get_cart_bp.route("/api/cart", methods=['GET'])
@jwt_required()
def get_cart():
    
    """
    Отримати кошик
    ---
    responses:
      200:
        description: Показати список товарів до замовлення
      500:
        description: Не вдалось показати кошик
    """
    
    try:
        auth_header = request.headers.get("Authorization")
        logger.info(f"Authorization header: {auth_header}")

        user_id = get_jwt_identity()
        logger.info(f"Extracted user ID: {user_id} (type: {type(user_id)})")

        cart_wood_items = CartWoodItem.query.filter_by(user_id=user_id).all()
        
        schema = WoodCart(many=True)
        result = schema.dump(cart_wood_items)

        return jsonify({"cart": result}), 200

    except Exception as e:
        logger.error(f"Error fetching cart: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Failed to fetch cart", "details": str(e)}), 500