from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.equipment_model import EquipmentModel


class Producer(Base):
    __tablename__ = 'producer_name'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_producer: Mapped[str] = mapped_column(String(50))

    equipment_models: Mapped[List["EquipmentModel"]] = relationship(
        "EquipmentModel", back_populates="producer"
    )