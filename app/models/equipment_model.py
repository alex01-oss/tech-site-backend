from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class EquipmentModel(Base):
    __tablename__ = 'equipment_model'

    id = Column(Integer, primary_key=True)
    name_equipment = Column(String, nullable=False, unique=True, index=True)
    name_producer = Column(String, ForeignKey('producer_name.name_producer'), nullable=False)

    equipment_codes = relationship("EquipmentCode", back_populates="equipment_model")
    producer = relationship("ProducerName", back_populates="equipment_models")
