from sqlalchemy import Column, BigInteger, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Floor(Base):
    """Floor model representing floors within sites."""
    
    __tablename__ = "floors"
    
    id = Column(BigInteger, primary_key=True, index=True)
    site_id = Column(BigInteger, ForeignKey('sites.id'), nullable=False, index=True)
    number = Column(Float, nullable=False)
    name = Column(String(191), nullable=False)
    plan = Column(String(500), nullable=True)
    deleted = Column(Boolean, nullable=False, default=False, server_default='0')
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    site = relationship("Site", back_populates="floors")
    
    def __repr__(self):
        return f"<Floor(id={self.id}, site_id={self.site_id}, number={self.number}, name='{self.name}')>" 