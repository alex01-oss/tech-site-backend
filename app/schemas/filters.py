from typing import List

from pydantic import BaseModel, ConfigDict


class FilterItemSchema(BaseModel):
    name: str

class FilterResponseSchema(BaseModel):
    bonds: List[FilterItemSchema]
    grids: List[FilterItemSchema]
    mountings: List[FilterItemSchema]
    model_config = ConfigDict(from_attributes=True)