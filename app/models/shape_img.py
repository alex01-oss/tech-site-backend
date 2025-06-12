from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class ShapeImg(Base):
    __tablename__ = 'shape_img'

    id = Column(Integer, primary_key=True)
    shape = Column(String, nullable=False, unique=True, index=True)
    img_url = Column(String, nullable=False)

    products = relationship("ProductGrindingWheels", back_populates="shape_info")
