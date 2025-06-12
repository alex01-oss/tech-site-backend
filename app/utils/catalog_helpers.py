from backend.app.schemas.catalog_schema import CatalogItemSchema, CatalogQuerySchema
import hashlib


def build_catalog_item(item, is_in_cart: bool = False) -> CatalogItemSchema:
    return CatalogItemSchema(
        code=str(item.code),
        shape=str(item.shape),
        dimensions=str(item.dimensions),
        images=item.shape_info.img_url if item.shape_info else None,
        name_bond=str(item.name_bond),
        grid_size=str(item.grid_size),
        is_in_cart=is_in_cart,
    )


def make_cache_key(params: CatalogQuerySchema, user_id: int):
    raw_key = f"{params.page}:{params.items_per_page}:{params.search}:{params.search_type}:{params.name_bond}:{params.grid_size}:{user_id}"
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"catalog:{hashed_key}"
