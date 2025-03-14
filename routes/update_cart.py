from flask import Blueprint

update_cart_bp = Blueprint('update_cart', __name__)

@update_cart_bp.route("/api/cart", methods=['PUT'])
def update_cart():
    
    """
    Оновити продукт
    ---
    responses:
      200:
        description: Змінити кількість товарів для замовлення
    """