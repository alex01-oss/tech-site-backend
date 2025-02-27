import math
import traceback
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from extensions import db, cache, logger
from schemas.tool_schema import Tool
from schemas.query_schema import CatalogQuerySchema

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route("/api/catalog", methods=['GET'])
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
    items_per_page = args.get('items_per_page', 10)
    search_type = args.get('search_type', 'name').lower()
    search_query = args.get('search', '').lower()

    try:
        logger.info(f'Request for catalog received. Page: {page}, Items per page: {items_per_page}')
        
        query = db.session.query(Tool)

        if search_query:
            if search_type == 'name':
                query = query.filter(Tool.Title.ilike(f"%{search_query}%"))
            elif search_type == 'brand':
                query = query.filter(Tool.Category.ilike(f"%{search_query}%"))
            elif search_type == 'specs':
                query = query.filter(
                    (Tool.Value_param1.ilike(f"%{search_query}%")) |
                    (Tool.Value_param2.ilike(f"%{search_query}%")) |
                    (Tool.Value_param3.ilike(f"%{search_query}%")) |
                    (Tool.Value_param4.ilike(f"%{search_query}%"))
                )

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
        logger.error(f"Error occurred: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": "Failed to load catalog data", "details": str(e)}), 500