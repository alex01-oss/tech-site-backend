from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.catalog import Catalog
    from app.models.equipment_model import EquipmentModel


class EquipmentCode(Base):
    __tablename__ = 'equipment_code'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    equipment_model_id: Mapped[int] = mapped_column(Integer, ForeignKey('equipment_model.id'))
    catalog_id: Mapped[int] = mapped_column(Integer, ForeignKey('catalog.id'))

    equipment_model: Mapped["EquipmentModel"] = relationship(
        "EquipmentModel", back_populates="equipment_codes"
    )
    catalog: Mapped["Catalog"] = relationship(
        "Catalog", back_populates="equipment_codes"
    )
