import math

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.catalog_item import CatalogItem
from app.schemas.catalog_schema import CatalogQuery, CatalogResponse, CatalogItemSchema

catalog_router = APIRouter()

@catalog_router.get("/api/catalog", response_model=CatalogResponse)
async def return_products(
        query_params: CatalogQuery = Depends(),
        db: Session = Depends(get_db)
):
    try:
        query = db.query(CatalogItem)

        if query_params.search:
            search_query = query_params.search.lower()
            if query_params.search_type == 'code':
                query = query.filter(CatalogItem.code.ilike(f"%{search_query}%"))
            elif query_params.search_type == 'shape':
                query = query.filter(CatalogItem.shape.ilike(f"%{search_query}%"))
            elif query_params.search_type == 'dimensions':
                query = query.filter(CatalogItem.dimensions.ilike(f"%{search_query}%"))

        total_items = query.count()
        total_pages = math.ceil(total_items / query_params.items_per_page)
        offset = (query_params.page - 1) * query_params.items_per_page
        catalog_items = query.offset(offset).limit(query_params.items_per_page).all()

        items = [CatalogItemSchema(
            code=str(item.code),
            shape=str(item.shape),
            dimensions=str(item.dimensions),
            images=str(item.images)
        ) for item in catalog_items]

        return CatalogResponse(
            items=items,
            total_items=total_items,
            total_pages=total_pages,
            current_page=query_params.page,
            items_per_page=query_params.items_per_page
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load catalog data: {str(e)}")