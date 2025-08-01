from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, UTC

from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    jti = Column(String, unique=True, index=True, nullable=False)
    refresh_token = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime, default=datetime.now(UTC), onupdate=datetime.now(UTC), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    device_info = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)

    user = relationship('User', back_populates='refresh_tokens')

    def __repr__(self):
        return f"<RefreshToken user_id={self.user_id} jti={self.jti}>"