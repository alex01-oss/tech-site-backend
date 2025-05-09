from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ProductGrindingWheels(Base):
    __tablename__ = 'product_grinding_wheels'

    code = Column(String, primary_key=True, index=True)
    shape = Column(String, ForeignKey('shape_img.shape'), nullable=False)
    dimensions = Column(String, nullable=False)
    name_bond = Column(String, ForeignKey('bond.name_bond'), nullable=False)
    grid_size = Column(String, nullable=False)

    cart_items = relationship("CartItem", back_populates="product")
    bond = relationship("Bond", back_populates="products")
    shape_info = relationship("ShapeImg", back_populates="products")

    equipment_codes = relationship(
        "EquipmentCode",
        primaryjoin="ProductGrindingWheels.code == EquipmentCode.code",
        back_populates="product"
    )
