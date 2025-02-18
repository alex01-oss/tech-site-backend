from flask import Flask, json, jsonify, request
from flasgger import Swagger
from flask_caching import Cache
from flask_cors import CORS
from marshmallow import ValidationError
import pandas as pd
import math

from logs.config import setup_logging
from schemas.schema import CatalogQuerySchema

app = Flask(__name__)
CORS(app)

ITEMS_PER_PAGE = 8

swagger = Swagger(app)
logger = setup_logging()

app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

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
        return jsonify({"error": "Invalid input", "details": err.messages}), 400

    page = args.get('page', 1)
    items_per_page = args.get('items_per_page', ITEMS_PER_PAGE)
    search_type = args.get('search_type', 'name').lower()
    search_query = args.get('search', '').lower()


    try:
        logger.info('Request for catalog received')
        
        df = pd.read_excel('construction.xlsx')
        
        specs_columns = ['Value_param2', 'Value_param3', 'Value_param4', 'Value_param5']
        for col in specs_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)
    
        # search types
        if search_query:
            if search_type == 'name':
                df = df[df["Name"].fillna('').str.lower().str.contains(search_query)]
            elif search_type == 'brand':
                df = df[df["Type"].fillna('').str.lower().str.contains(search_query) |
                       df["Line"].fillna('').str.lower().str.contains(search_query)]
            elif search_type == 'specs':
                specs_mask = pd.Series(False, index=df.index)
                for col in specs_columns:
                    if col in df.columns:
                        specs_mask |= df[col].fillna('').str.lower().str.contains(search_query, na=False)
                df = df[specs_mask]
        
        total_items = len(df)
        total_pages = math.ceil(total_items / items_per_page)

        offset = (page - 1) * items_per_page
        df_page = df.iloc[offset:offset + items_per_page]
        items = json.loads(df_page.to_json(orient="records"))

        return jsonify({
            'items': items,
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'items_per_page': items_per_page 
        })

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        print(f"Error in return_products: {str(e)}")
        return jsonify({"error": f"Failed to load catalog data: {str(e)}"}), 500        

if __name__ == "__main__":
    app.run(debug=True, port=8080)