import csv
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/filters",
    tags=["Products"]
)


@router.get("", response_model=List[Dict[str, Any]])
async def get_sidebar_filters():
    csv_path = Path(__file__).resolve().parents[3] / "data.csv"

    if not csv_path.exists():
        raise FileNotFoundError(f"File not found at the calculated path: {csv_path}")

    unique_bonds = set()
    unique_grid_sizes = set()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "name_bond" in row and row["name_bond"]:
                unique_bonds.add(row["name_bond"])
            if "grid_size" in row and row["grid_size"]:
                unique_grid_sizes.add(row["grid_size"])

    filters_menu: List[Dict[str, Any]] = [
        {
            "title": "Bond",
            "items": [
                {"text": bond_val, "type": "button", "searchType": "nameBond", "searchValue": bond_val}
                for bond_val in sorted(list(unique_bonds))
            ]
        },
        {
            "title": "Grid Size",
            "items": [
                {"text": grid_val, "type": "button", "searchType": "gridSize", "searchValue": grid_val}
                for grid_val in sorted(list(unique_grid_sizes))
            ]
        }
    ]

    return filters_menu
