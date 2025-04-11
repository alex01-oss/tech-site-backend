from sqlalchemy import Column, String, Text

from app.core.database import Base


class CatalogItem(Base):
    __tablename__ = 'catalog'

    code: str = Column(String, nullable=False, primary_key=True, index=True)
    shape: str = Column(String, nullable=False)
    dimensions: str = Column(String, nullable=False)
    images: str = Column(Text, nullable=False)