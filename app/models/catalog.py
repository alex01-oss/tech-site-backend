from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.shape import Shape
    from app.models.grid_size import GridSize
    from app.models.categories import Categories
    from app.models.mounting import Mounting
    from app.models.bond_to_code import BondToCode
    from app.models.equipment_code import EquipmentCode


class Catalog(Base):
    __tablename__ = 'catalog'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10))
    dimensions: Mapped[str] = mapped_column(String(50))

    shape_id: Mapped[int] = mapped_column(Integer, ForeignKey('shape_img.id'))
    grid_size_id: Mapped[int] = mapped_column(Integer, ForeignKey('grid_size.id'))
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))
    mounting_id: Mapped[int] = mapped_column(Integer, ForeignKey('mounting.id'), nullable=True)

    shape: Mapped["Shape"] = relationship("Shape", back_populates="catalog")
    grid_size: Mapped["GridSize"] = relationship("GridSize", back_populates="catalog")
    category: Mapped["Categories"] = relationship("Categories", back_populates="catalog")
    mounting: Mapped["Mounting"] = relationship("Mounting", back_populates="catalog")

    cart_items = relationship("CartItem", back_populates="catalog")

    bond_to_codes: Mapped[List["BondToCode"]] = relationship(
        "BondToCode", back_populates="catalog"
    )

    equipment_codes: Mapped[List["EquipmentCode"]] = relationship(
        "EquipmentCode", back_populates="catalog"
    )
