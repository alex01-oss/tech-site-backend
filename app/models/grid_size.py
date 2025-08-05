from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.catalog import Catalog


class GridSize(Base):
    __tablename__ = 'grid_size'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    grid_size: Mapped[str] = mapped_column(String(50))

    catalog: Mapped[List["Catalog"]] = relationship(
        "Catalog", back_populates="grid_size"
    )