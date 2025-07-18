from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.floor import Floor
from app.models.site import Site
from app.schemas.floor import FloorCreate, FloorUpdate, Floor as FloorSchema

router = APIRouter()


@router.get("/", response_model=List[FloorSchema])
def get_floors(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    site_id: Optional[int] = Query(None, gt=0, description="Filter by site ID"),
    include_deleted: bool = Query(False, description="Include soft-deleted floors"),
    db: Session = Depends(get_db)
):
    """Get all floors with pagination, optional site filtering, and soft-deleted inclusion."""
    query = db.query(Floor)
    
    if site_id:
        query = query.filter(Floor.site_id == site_id)
    
    if not include_deleted:
        query = query.filter(Floor.deleted == False)
    
    floors = query.offset(skip).limit(limit).all()
    return floors


@router.get("/{floor_id}", response_model=FloorSchema)
def get_floor(floor_id: int, db: Session = Depends(get_db)):
    """Get a specific floor by ID."""
    floor = db.query(Floor).filter(Floor.id == floor_id, Floor.deleted == False).first()
    if floor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floor not found"
        )
    return floor


# Temporarily comment out the complex relationship endpoint
# @router.get("/{floor_id}/with-site", response_model=FloorWithSite)
# def get_floor_with_site(floor_id: int, db: Session = Depends(get_db)):
#     """Get a specific floor with its site information."""
#     floor = db.query(Floor).options(
#         joinedload(Floor.site)
#     ).filter(Floor.id == floor_id, Floor.deleted == False).first()
#     
#     if floor is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Floor not found"
#         )
#     return floor


@router.post("/", response_model=FloorSchema, status_code=status.HTTP_201_CREATED)
def create_floor(floor: FloorCreate, db: Session = Depends(get_db)):
    """Create a new floor."""
    # Check if site exists and is not deleted
    site = db.query(Site).filter(Site.id == floor.site_id, Site.deleted == False).first()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site not found or is deleted"
        )
    
    # Check if floor with same number already exists in the site
    existing_floor = db.query(Floor).filter(
        Floor.site_id == floor.site_id,
        Floor.number == floor.number,
        Floor.deleted == False
    ).first()
    
    if existing_floor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Floor with this number already exists in this site"
        )
    
    db_floor = Floor(**floor.dict())
    # Set timestamps explicitly for compatibility with existing database
    db_floor.created_at = datetime.utcnow()
    db_floor.updated_at = datetime.utcnow()
    db.add(db_floor)
    db.commit()
    db.refresh(db_floor)
    return db_floor


@router.put("/{floor_id}", response_model=FloorSchema)
def update_floor(floor_id: int, floor_update: FloorUpdate, db: Session = Depends(get_db)):
    """Update a floor's information."""
    db_floor = db.query(Floor).filter(Floor.id == floor_id, Floor.deleted == False).first()
    if db_floor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floor not found"
        )
    
    # Check if site exists if site_id is being updated
    if floor_update.site_id and floor_update.site_id != db_floor.site_id:
        site = db.query(Site).filter(Site.id == floor_update.site_id, Site.deleted == False).first()
        if site is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site not found or is deleted"
            )
    
    # Check number uniqueness if number is being updated
    if floor_update.number is not None and floor_update.number != db_floor.number:
        target_site_id = floor_update.site_id if floor_update.site_id else db_floor.site_id
        existing_floor = db.query(Floor).filter(
            Floor.site_id == target_site_id,
            Floor.number == floor_update.number,
            Floor.id != floor_id,
            Floor.deleted == False
        ).first()
        
        if existing_floor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Floor with this number already exists in this site"
            )
    
    # Update fields if provided
    update_data = floor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_floor, field, value)
    
    db_floor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_floor)
    return db_floor


@router.delete("/{floor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_floor(floor_id: int, hard_delete: bool = Query(False, description="Permanently delete the floor"), db: Session = Depends(get_db)):
    """Delete a floor (soft delete by default, hard delete if specified)."""
    db_floor = db.query(Floor).filter(Floor.id == floor_id, Floor.deleted == False).first()
    if db_floor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Floor not found"
        )
    
    if hard_delete:
        db.delete(db_floor)
    else:
        # Soft delete
        db_floor.deleted = True
        db_floor.deleted_at = datetime.utcnow()
        db_floor.updated_at = datetime.utcnow()
    
    db.commit()
    return None


@router.post("/{floor_id}/restore", response_model=FloorSchema)
def restore_floor(floor_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted floor."""
    db_floor = db.query(Floor).filter(Floor.id == floor_id, Floor.deleted == True).first()
    if db_floor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soft-deleted floor not found"
        )
    
    # Check if site still exists and is not deleted
    site = db.query(Site).filter(Site.id == db_floor.site_id, Site.deleted == False).first()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot restore floor: parent site is deleted"
        )
    
    # Check if floor number is still available
    existing_floor = db.query(Floor).filter(
        Floor.site_id == db_floor.site_id,
        Floor.number == db_floor.number,
        Floor.id != floor_id,
        Floor.deleted == False
    ).first()
    
    if existing_floor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot restore floor: floor number is already taken"
        )
    
    db_floor.deleted = False
    db_floor.deleted_at = None
    db_floor.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_floor)
    return db_floor 