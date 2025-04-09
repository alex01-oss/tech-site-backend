from schemas.catalog_schema import CatalogQuerySchema
from flask import Blueprint, request, jsonify
from models.catalog_item import CatalogItem
from extensions import db, cache, logger
from marshmallow import ValidationError

import traceback
import math

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route("/api/catalog", methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def return_products():
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
        
        query = db.session.query(CatalogItem)

        if search_query:
            if search_type == 'code':
                query = query.filter(CatalogItem.code.ilike(f"%{search_query}%"))
            elif search_type == 'shape':
                query = query.filter(CatalogItem.shape.ilike(f"%{search_query}%"))
            elif search_type == 'dimensions':
                query = query.filter(CatalogItem.dimensions.ilike(f"%{search_query}%"))

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