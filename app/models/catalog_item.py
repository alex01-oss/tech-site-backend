from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class CatalogItem(Base):
    __tablename__ = 'catalog'

    code = Column(String, nullable=False, primary_key=True, index=True)
    shape = Column(String, nullable=False)
    dimensions = Column(String, nullable=False)
    images = Column(Text, nullable=False)

    cart_items = relationship("CartItem", back_populates="product")
