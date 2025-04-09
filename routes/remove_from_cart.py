import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models.cart_item import CartItem
from extensions import logger, db

remove_from_cart_bp = Blueprint('remove_from_cart', __name__)

@remove_from_cart_bp.route("/api/cart", methods=['DELETE'])
@jwt_required()
def remove_from_cart():
    try:
      user_id = get_jwt_identity()
      data = request.get_json()
      code = data.get("code")
      
      if not code:
        logger.warning("missing article in request")
        return jsonify({"error": "article is required"}), 400
      
      item = CartItem.query.filter_by(user_id=user_id, code=code).first()
      
      if not item:
        logger.info("item not found in cart")
        return jsonify({"error": "item not found in cart"}), 404
      
      db.session.delete(item)
      db.session.commit()
      
      logger.info(f"item with {code} removed from cart")
      return jsonify({"message": "item deleted from cart"}), 200
        
    except Exception as e:
      logger.error(f"error deleting item from cart, {str(e)}")
      logger.error(traceback.format_exc())
      return jsonify({"error": "failed to remove item", "details": str(e)}), 500
