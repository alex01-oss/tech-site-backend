from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class ProducerName(Base):
    __tablename__ = 'producer_name'

    id = Column(Integer, primary_key=True)
    name_producer = Column(String, nullable=False, unique=True, index=True)

    equipment_models = relationship("EquipmentModel", back_populates="producer")
