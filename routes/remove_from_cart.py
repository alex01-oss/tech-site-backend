import traceback
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
# from models.cart import CartItem
from models.cart_wood import CartWoodItem
from extensions import logger, db

remove_from_cart_bp = Blueprint('remove_from_cart', __name__)

@remove_from_cart_bp.route("/api/cart", methods=['DELETE'])
@jwt_required()
def remove_from_cart():
    
    """
    Вилучити продукт
    ---
    responses:
      200:
        description: Видалено товар з кошику
      400:
        description: Відсутній артикул
      404:
        description: Товар не знайдено
      500:
        description: Не вдалося видалити товар
    """
    
    try:
      user_id = get_jwt_identity()
      data = request.get_json()
      
      # article = data.get("article")
      code = data.get("code")
      
      # if not article:
      if not code:
        
        logger.warning("missing article in request")
        return jsonify({"error": "article is required"}), 400
      
      # item = CartItem.query.filter_by(user_id=user_id, article=article).first()
      item = CartWoodItem.query.filter_by(user_id=user_id, code=code).first()
      
      if not item:
        logger.info("item not found in cart")
        return jsonify({"error": "item not found in cart"}), 404
      
      db.session.delete(item)
      db.session.commit()
      
      # logger.info(f"item with {article} removed from cart")
      logger.info(f"item with {code} removed from cart")
      
      return jsonify({"message": "item deleted from cart"}), 200
        
    except Exception as e:
      logger.error(f"error deleting item from cart, {str(e)}")
      logger.error(traceback.format_exc())
      return jsonify({"error": "failed to remove item", "details": str(e)}), 500
