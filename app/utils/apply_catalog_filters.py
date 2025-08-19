from typing import Any

from sqlalchemy import func

from app.models.bond_to_code import BondToCode
from app.models.catalog import Catalog
from app.models.equipment_code import EquipmentCode
from app.models.equipment_model import EquipmentModel
from app.models.shape import Shape

def apply_catalog_filters(query: Any, search_params: dict):
    if search_params.get('category_id'):
        query = query.filter(Catalog.category_id == search_params['category_id'])
        
    if search_params.get('search_code'):
        query = query.filter(func.lower(Catalog.code).like(f"%{search_params['search_code'].lower()}%"))
        
    if search_params.get('search_shape'):
        query = query.join(Catalog.shape).filter(func.lower(Shape.shape).like(f"%{search_params['search_shape'].lower()}%"))
    
    if search_params.get('search_dimensions'):
        query = query.filter(func.lower(Catalog.dimensions).like(f"%{search_params['search_dimensions'].lower()}%"))
    
    if search_params.get('search_machine'):
        query = query.join(Catalog.equipment_codes) \
            .join(EquipmentCode.equipment_model) \
            .filter(func.lower(EquipmentModel.model).like(f"%{search_params['search_machine'].lower()}%"))
            
    if search_params.get('bond_ids'):
        query = query.join(Catalog.bond_to_codes).filter(BondToCode.bond_id.in_(search_params['bond_ids']))

    if search_params.get('grid_size_ids'):
        query = query.filter(Catalog.grid_size_id.in_(search_params['grid_size_ids']))

    if search_params.get('mounting_ids'):
        query = query.filter(Catalog.mounting_id.in_(search_params['mounting_ids']))
            
    return query