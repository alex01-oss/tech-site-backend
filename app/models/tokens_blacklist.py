from sqlalchemy import Column, DateTime, Integer, String
from app.core.database import Base


class TokenBlacklist(Base):
    __tablename__ = "blacklisted_tokens"
    
    id = Column(Integer, primary_key=True)
    jti = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)