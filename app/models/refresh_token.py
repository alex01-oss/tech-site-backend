from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    refresh_token = Column(String)
    created_at = Column(DateTime)

    user = relationship('User', back_populates='refresh_tokens')