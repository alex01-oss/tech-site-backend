import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException
from app.utils.cache import redis_client


router = APIRouter(
    prefix="/api/menu",
    tags=["Menu"]
)

@router.get("", response_model=Dict[str, Any])
async def return_menu():
    try:
        
        cache_key = "menu_data"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        with open('menu.json', 'r') as file:
            menu_data = json.load(file)
            
        redis_client.set(cache_key, json.dumps(menu_data), ex=3600)
        
        return menu_data
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load menu data: {str(e)}"
        )
