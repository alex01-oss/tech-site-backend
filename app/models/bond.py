from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.bond_to_code import BondToCode


class Bond(Base):
    __tablename__ = 'bond'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_bond: Mapped[str] = mapped_column(String(50))
    bond_description: Mapped[str] = mapped_column(Text)
    bond_cooling: Mapped[str] = mapped_column(Text)

    bond_to_codes: Mapped[List["BondToCode"]] = relationship(
        "BondToCode", back_populates="bond"
    )
