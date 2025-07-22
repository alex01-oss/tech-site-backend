from app.schemas.catalog_schema import CatalogItemSchema, CatalogQuerySchema
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
    )
    hashed_key = hashlib.md5(raw_key.encode()).hexdigest()
    return f"catalog:{hashed_key}"