import traceback
from flask import Flask, json, jsonify, request
from flasgger import Swagger
from flask_caching import Cache
from flask_cors import CORS
from marshmallow import ValidationError
# import pandas as pd
import math

from logs.config import setup_logging
from schemas.query_schema import CatalogQuerySchema

from flask_sqlalchemy import SQLAlchemy
from schemas.tool_schema import Tool

app = Flask(__name__)
CORS(app)

ITEMS_PER_PAGE = 10

swagger = Swagger(app)

logger = setup_logging()

app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# postgres
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost/construction'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

@app.route("/api/menu", methods=['GET'])
def return_menu():
    """
    Отримати меню
    ---
    responses:
      200:
        description: Список меню
    """
    try:
        with open('config/config.json', 'r') as file:
            menu_data = json.load(file)
        return jsonify(menu_data)
    except Exception as e:
        return jsonify({"error": f"Failed to load menu data: {str(e)}"}), 500

@app.route("/api/catalog", methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def return_products():
    """
    Отримати каталог товарів
    ---
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
        description: Номер сторінки
      - name: search
        in: query
        type: string
        description: Пошуковий запит
      - name: search_type
        in: query
        type: string
        enum: [name, brand, specs]
        default: name
        description: Тип пошуку
    responses:
      200:
        description: Каталог товарів
    """
    
    schema = CatalogQuerySchema()

    try:
        args = schema.load(request.args)
    except ValidationError as err:
        logger.error(f"Validation error: {err.messages}")
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    page = args.get('page', 1)
    items_per_page = args.get('items_per_page', ITEMS_PER_PAGE)
    search_type = args.get('search_type', 'name').lower()
    search_query = args.get('search', '').lower()

    try:
        logger.info(f'Request for catalog received. Page: {page}, Items per page: {items_per_page}')
        
        query = db.session.query(Tool)
    
        # search types
        if search_query:
            if search_type == 'name':
                query = query.filter(Tool.Name.like(f"%{search_query}%"))
            elif search_type == 'brand':
                query = query.filter(Tool.Type.like(f"%{search_query}%"))
            elif search_type == 'specs':
                query = query.filter(
                    (Tool.Value_param1.like(f"%{search_query}%")) |
                    (Tool.Value_param2.like(f"%{search_query}%")) |
                    (Tool.Value_param3.like(f"%{search_query}%")) |
                    (Tool.Value_param4.like(f"%{search_query}%")))

        total_items = query.count()
        total_pages = math.ceil(total_items / items_per_page)
        offset = (page - 1) * items_per_page
        tools = query.offset(offset).limit(items_per_page).all()
        
        items = [tool.__dict__ for tool in tools]
        for item in items:
            item.pop('_sa_instance_state') 

        logger.info(f"Successfully fetched {len(items)} items.")
        
        return jsonify({
            'items': items,
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items_per_page': items_per_page 
        })

    except Exception as e:
        # Log more detailed information about the error
        logger.error(f"Error occurred: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({"error": "Failed to load catalog data", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)