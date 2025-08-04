from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.producer import Producer
    from app.models.equipment_code import EquipmentCode


class EquipmentModel(Base):
    __tablename__ = 'equipment_model'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(50))

    producer_id: Mapped[int] = mapped_column(Integer, ForeignKey('producer_name.id'))

    producer: Mapped["Producer"] = relationship(
        "Producer", back_populates="equipment_models"
    )

    equipment_codes: Mapped[List["EquipmentCode"]] = relationship(
        "EquipmentCode", back_populates="equipment_model"
    )
