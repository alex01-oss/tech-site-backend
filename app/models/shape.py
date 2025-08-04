from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.catalog import Catalog


class Shape(Base):
    __tablename__ = 'shape_img'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shape: Mapped[str] = mapped_column(String(255))
    img_url: Mapped[str] = mapped_column(String(255))

    catalog: Mapped[List["Catalog"]] = relationship(
        "Catalog", back_populates="shape"
    )