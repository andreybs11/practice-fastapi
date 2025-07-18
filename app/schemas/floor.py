from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime


class FloorBase(BaseModel):
    """Base Floor schema with common fields."""
    site_id: int = Field(..., gt=0, description="ID of the parent site")
    number: float = Field(..., description="Floor number")
    name: str = Field(..., min_length=1, max_length=191, description="Floor name")
    plan: Optional[str] = Field(None, max_length=500, description="Floor plan URL or path")


class FloorCreate(FloorBase):
    """Schema for creating a new floor."""
    pass


class FloorUpdate(BaseModel):
    """Schema for updating floor information."""
    site_id: Optional[int] = Field(None, gt=0)
    number: Optional[float] = None
    name: Optional[str] = Field(None, min_length=1, max_length=191)
    plan: Optional[str] = Field(None, max_length=500)


class FloorInDB(FloorBase):
    """Schema for floor data in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    deleted: bool
    deleted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Floor(FloorBase):
    """Schema for floor response (without soft delete info)."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Temporarily comment out the complex relationship schema
# class FloorWithSite(Floor):
#     """Schema for floor response including site information."""
#     site: Optional[Annotated['Site', Field(description="Site object")]] = None
#     
#     class Config:
#         from_attributes = True 