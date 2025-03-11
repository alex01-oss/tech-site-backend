import json
import time
from flask import Blueprint, jsonify
from extensions import cache

menu_bp = Blueprint('menu', __name__)

@cache.cached(timeout=60)
@menu_bp.route("/api/menu", methods=['GET'])
def return_menu():
    
    """
    Отримати меню
    ---
    responses:
      200:
        description: Список меню
      500:
        description: Не вдалося завантажити меню
    """
    
    try:
        # with open('config/config.json', 'r') as file:
        with open('config/menu.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({"error": f"Failed to load menu data: {str(e)}"}), 500
