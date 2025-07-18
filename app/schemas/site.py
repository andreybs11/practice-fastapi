from pydantic import BaseModel, Field
from typing import Optional, List, Annotated
from datetime import datetime
from decimal import Decimal


class SiteBase(BaseModel):
    """Base Site schema with common fields."""
    name: str = Field(..., min_length=1, max_length=191, description="Site name")
    address: str = Field(..., min_length=1, description="Site address")
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180, description="Longitude coordinate")


class SiteCreate(SiteBase):
    """Schema for creating a new site."""
    pass


class SiteUpdate(BaseModel):
    """Schema for updating site information."""
    name: Optional[str] = Field(None, min_length=1, max_length=191)
    address: Optional[str] = Field(None, min_length=1)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)


class SiteInDB(SiteBase):
    """Schema for site data in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted: bool
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Site(SiteBase):
    """Schema for site response (without soft delete info)."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Temporarily comment out the complex relationship schema
# class SiteWithFloors(Site):
#     """Schema for site response including floors."""
#     floors: List[Annotated['Floor', Field(description="Floor objects")]] = []
#     
#     class Config:
#         from_attributes = True 