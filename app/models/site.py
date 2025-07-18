from sqlalchemy import Column, BigInteger, String, Text, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Site(Base):
    """Site model representing physical locations."""
    
    __tablename__ = "sites"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(191), nullable=False, index=True)
    address = Column(Text, nullable=False)
    latitude = Column(Numeric(10, 6), nullable=True)
    longitude = Column(Numeric(10, 6), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    deleted = Column(Boolean, nullable=False, default=False, server_default='0')
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationship
    floors = relationship("Floor", back_populates="site")
    
    def __repr__(self):
        return f"<Site(id={self.id}, name='{self.name}', address='{self.address[:50]}...')>" 