import json
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

menu_router = APIRouter()

@menu_router.get("/api/menu", response_model=Dict[str, Any])
async def return_menu():
    try:
        with open('menu.json', 'r') as file:
            menu_data = json.load(file)
        return menu_data
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to load menu data: {str(e)}"
        )
