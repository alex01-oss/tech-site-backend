from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.core.database import Base


class Bond(Base):
    __tablename__ = 'bond'

    id = Column(Integer, primary_key=True)
    name_bond = Column(String, nullable=False, unique=True, index=True)
    bond_description = Column(String, nullable=False)
    bond_cooling = Column(String, nullable=False)

    products = relationship("ProductGrindingWheels", back_populates="bond")
