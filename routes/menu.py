import json
from flask import Blueprint, jsonify
from extensions import cache

menu_bp = Blueprint('menu', __name__)

@cache.cached(timeout=60)
@menu_bp.route("/api/menu", methods=['GET'])
def return_menu():
    try:
        with open('config/menu.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({"error": f"Failed to load menu data: {str(e)}"}), 500
