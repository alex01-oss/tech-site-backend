from typing import List, TYPE_CHECKING

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.catalog import Catalog


class Mounting(Base):
    __tablename__ = 'mounting'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mm: Mapped[str] = mapped_column(String(10))
    inch: Mapped[str] = mapped_column(String(10))

    catalog: Mapped[List["Catalog"]] = relationship(
        "Catalog", back_populates="mounting"
    )
