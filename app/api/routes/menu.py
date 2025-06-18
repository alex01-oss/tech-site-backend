import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

from app.utils.cache import cache_set, cache_get

router = APIRouter(
    prefix="/api/menu",
    tags=["Menu"]
)


@router.get("", response_model=Dict[str, Any])
async def return_menu():
    try:
        cache_key = "menu_data"
        cached = await cache_get(cache_key)
        if cached:
            return cached

        with open('menu.json', 'r') as file:
            menu_data = json.load(file)

        await cache_set(cache_key, menu_data, ex=1800)

        return menu_data

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load menu data: {str(e)}"
        )
