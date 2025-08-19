from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BondFilterSchema(BaseModel):
    id: int
    name_bond: str
    model_config = ConfigDict(from_attributes=True)

class GridFilterSchema(BaseModel):
    id: int
    grid_size: str
    model_config = ConfigDict(from_attributes=True)

class MountingFilterSchema(BaseModel):
    id: int
    mm: str
    inch: str
    model_config = ConfigDict(from_attributes=True)

class FilterResponseSchema(BaseModel):
    bonds: List[BondFilterSchema]
    grids: Optional[List[GridFilterSchema]] = None
    mountings: Optional[List[MountingFilterSchema]] = None

class CategorySchema(BaseModel):
    id: int
    name: str
    img_url: str
    model_config = ConfigDict(from_attributes=True)