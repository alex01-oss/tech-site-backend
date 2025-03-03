from flask import Blueprint

remove_from_cart_bp = Blueprint('remove_from_cart', __name__)

@remove_from_cart_bp.route("/api/cart", methods=['DELETE'])
def remove_from_cart():
    
    """
    Вилучити продукт
    ---
    responses:
      200:
        description: Видалити товар з кошику
    """
    
    
