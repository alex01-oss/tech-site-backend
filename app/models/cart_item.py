from sqlalchemy import Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class CartItem(Base):
    __tablename__ = 'cart'
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    code: str = Column(String, nullable=False)
    shape: str = Column(String, nullable=False)
    dimensions: str = Column(String, nullable=False)
    quantity: int = Column(Integer, default=1)
    images: str = Column(Text, nullable=False)
    
    user = relationship("User", back_populates="cart_items")