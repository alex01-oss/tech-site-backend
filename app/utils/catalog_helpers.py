from typing import List, Optional
from fastapi import Query
from app.schemas.catalog_schema import CatalogItemSchema, CatalogQuerySchema
import hashlib


def build_catalog_item(item, is_in_cart: bool = False) -> CatalogItemSchema:
    return CatalogItemSchema(
        code=str(item.code),
        shape=str(item.shape),
        dimensions=str(item.dimensions),
        images=item.shape_info.img_url if item.shape_info else None,
        name_bonds=List(item.name_bonds),
        grid_size=str(item.grid_size),
        is_in_cart=is_in_cart,
    )


def make_cache_key(params: CatalogQuerySchema, user_id: int):
    raw_key = (
        f"{params.page}:"
        f"{params.items_per_page}:"
        f"code_{params.search_code or ''}:"
        f"shape_{params.search_shape or ''}:"
        f"dimensions_{params.search_dimensions or ''}:"
        f"machine_{params.search_machine or ''}:"
        f"bond_{params.name_bond or ''}:"
        f"grid_{params.grid_size or ''}:"
        f"user_{user_id}"
        f"category_{params.category_name or ''}"
    )
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"catalog:{hashed_key}"

def parse_query_params(
    page: int = Query(1, ge=1),
    items_per_page: int = Query(8, ge=1, le=100),
    search_code: Optional[str] = Query(None),
    search_shape: Optional[str] = Query(None),
    search_dimensions: Optional[str] = Query(None),
    search_machine: Optional[str] = Query(None),
    name_bond: Optional[List[str]] = Query(None),
    grid_size: Optional[List[str]] = Query(None),
    category_name: Optional[str] = None
) -> CatalogQuerySchema:
    return CatalogQuerySchema(
        page=page,
        items_per_page=items_per_page,
        search_code=search_code,
        search_shape=search_shape,
        search_dimensions=search_dimensions,
        search_machine=search_machine,
        name_bond=name_bond,
        grid_size=grid_size,
        category_name=category_name,
    )