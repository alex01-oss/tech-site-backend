from pydantic import BaseModel
from typing import Any, TypeVar, Type
from app.core.encryption import encryption_service

T = TypeVar('T', bound=BaseModel)

class EncryptedBaseModel(BaseModel):
    @classmethod
    def model_validate_with_decrypt(cls: Type[T], obj: Any) -> T:
        data = {}
        for field_name, field_info in cls.model_fields.items():
            if hasattr(obj, field_name):
                value = getattr(obj, field_name)
                if isinstance(field_info.annotation, (str, type(None))) and 'encrypted' in field_info.json_schema_extra.get('tags', []):
                    data[field_name] = encryption_service.decrypt_data(value)
                else:
                    data[field_name] = value
            else:
                raise ValueError(f"Object does not have attribute '{field_name}'")
        return cls.model_validate(data)