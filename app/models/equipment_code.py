from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class EquipmentCode(Base):
    __tablename__ = 'equipment_code'

    name_equipment = Column(String, ForeignKey('equipment_model.name_equipment'), nullable=False, primary_key=True)
    code = Column(String, ForeignKey('product_grinding_wheels.code'), nullable=False, primary_key=True, index=True)

    product = relationship(
        "ProductGrindingWheels",
        primaryjoin="EquipmentCode.code == ProductGrindingWheels.code",
        back_populates="equipment_codes"
    )

    equipment_model = relationship("EquipmentModel", back_populates="equipment_codes")
