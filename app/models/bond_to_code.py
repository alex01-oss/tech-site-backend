from typing import TYPE_CHECKING

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.catalog import Catalog
    from app.models.bond import Bond


class BondToCode(Base):
    __tablename__ = 'bond_to_code'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code_id: Mapped[int] = mapped_column(Integer, ForeignKey('catalog.id'))
    bond_id: Mapped[int] = mapped_column(Integer, ForeignKey('bond.id'))

    catalog: Mapped["Catalog"] = relationship(
        "Catalog", back_populates="bond_to_codes"
    )
    bond: Mapped["Bond"] = relationship(
        "Bond", back_populates="bond_to_codes"
    )
