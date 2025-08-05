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
    key_parts = [
        f"page_{params.page}",
        f"ipp_{params.items_per_page}",
        f"code_{params.search_code or ''}",
        f"shape_{params.search_shape or ''}",
        f"dims_{params.search_dimensions or ''}",
        f"machine_{params.search_machine or ''}",
        f"user_{user_id}",
        f"category_{params.category_id or ''}",
    ]
    if params.bond_ids:
        key_parts.append(f"bonds_{','.join(map(str, sorted(params.bond_ids)))}")
    if params.grid_size_ids:
        key_parts.append(f"grids_{','.join(map(str, sorted(params.grid_size_ids)))}")
    if params.mounting_ids:
        key_parts.append(f"mountings_{','.join(map(str, sorted(params.mounting_ids)))}")
    
    raw_key = ":".join(key_parts)
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"catalog:{hashed_key}"

def parse_query_params(
    page: int = Query(1, ge=1),
    items_per_page: int = Query(8, ge=1, le=100),
    search_code: Optional[str] = Query(None),
    search_shape: Optional[str] = Query(None),
    search_dimensions: Optional[str] = Query(None),
    search_machine: Optional[str] = Query(None),
    
    bond_ids: Optional[List[int]] = Query(None),
    grid_size_ids: Optional[List[int]] = Query(None),
    mounting_ids: Optional[List[int]] = Query(None),
    
    category_id: Optional[int] = Query(None, alias="category")
) -> CatalogQuerySchema:
    return CatalogQuerySchema(
        page=page,
        items_per_page=items_per_page,
        search_code=search_code,
        search_shape=search_shape,
        search_dimensions=search_dimensions,
        search_machine=search_machine,
        bond_ids=bond_ids,
        grid_size_ids=grid_size_ids,
        mounting_ids=mounting_ids,
        category_id=category_id,
    )