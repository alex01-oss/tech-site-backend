from pydantic import EmailStr
from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, nullable=False, index=True)
    email: EmailStr = Column(String, unique=True, nullable=False, index=True)
    password_hash: str = Column(String, nullable=False)
    
    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )
