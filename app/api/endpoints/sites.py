from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.site import Site
from app.models.floor import Floor
from app.schemas.site import SiteCreate, SiteUpdate, Site as SiteSchema

router = APIRouter()


@router.get("/", response_model=List[SiteSchema])
def get_sites(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    include_deleted: bool = Query(False, description="Include soft-deleted sites"),
    db: Session = Depends(get_db)
):
    """Get all sites with pagination and optional soft-deleted inclusion."""
    query = db.query(Site)
    
    if not include_deleted:
        query = query.filter(Site.deleted == False)
    
    sites = query.offset(skip).limit(limit).all()
    return sites


@router.get("/{site_id}", response_model=SiteSchema)
def get_site(site_id: int, db: Session = Depends(get_db)):
    """Get a specific site by ID."""
    site = db.query(Site).filter(Site.id == site_id, Site.deleted == False).first()
    if site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    return site


# Temporarily comment out the complex relationship endpoint
# @router.get("/{site_id}/with-floors", response_model=SiteWithFloors)
# def get_site_with_floors(site_id: int, db: Session = Depends(get_db)):
#     """Get a specific site with its floors."""
#     site = db.query(Site).options(
#         joinedload(Site.floors).filter(Floor.deleted == False)
#     ).filter(Site.id == site_id, Site.deleted == False).first()
#     
#     if site is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Site not found"
#         )
#     return site


@router.post("/", response_model=SiteSchema, status_code=status.HTTP_201_CREATED)
def create_site(site: SiteCreate, db: Session = Depends(get_db)):
    """Create a new site."""
    # Check if site with same name already exists (case-insensitive)
    existing_site = db.query(Site).filter(
        Site.name.ilike(site.name),
        Site.deleted == False
    ).first()
    
    if existing_site:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Site with this name already exists"
        )
    
    db_site = Site(**site.dict())
    # Set timestamps explicitly for compatibility with existing database
    db_site.created_at = datetime.utcnow()
    db_site.updated_at = datetime.utcnow()
    db.add(db_site)
    db.commit()
    db.refresh(db_site)
    return db_site


@router.put("/{site_id}", response_model=SiteSchema)
def update_site(site_id: int, site_update: SiteUpdate, db: Session = Depends(get_db)):
    """Update a site's information."""
    db_site = db.query(Site).filter(Site.id == site_id, Site.deleted == False).first()
    if db_site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    # Check name uniqueness if name is being updated
    if site_update.name and site_update.name != db_site.name:
        existing_site = db.query(Site).filter(
            Site.name.ilike(site_update.name),
            Site.id != site_id,
            Site.deleted == False
        ).first()
        
        if existing_site:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site with this name already exists"
            )
    
    # Update fields if provided
    update_data = site_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_site, field, value)
    
    db_site.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_site)
    return db_site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_site(site_id: int, hard_delete: bool = Query(False, description="Permanently delete the site"), db: Session = Depends(get_db)):
    """Delete a site (soft delete by default, hard delete if specified)."""
    db_site = db.query(Site).filter(Site.id == site_id, Site.deleted == False).first()
    if db_site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    
    if hard_delete:
        # Check if site has floors
        floors_count = db.query(Floor).filter(Floor.site_id == site_id, Floor.deleted == False).count()
        if floors_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete site with {floors_count} active floors. Delete floors first or use soft delete."
            )
        db.delete(db_site)
    else:
        # Soft delete
        db_site.deleted = True
        db_site.deleted_at = datetime.utcnow()
        db_site.updated_at = datetime.utcnow()
    
    db.commit()
    return None


@router.post("/{site_id}/restore", response_model=SiteSchema)
def restore_site(site_id: int, db: Session = Depends(get_db)):
    """Restore a soft-deleted site."""
    db_site = db.query(Site).filter(Site.id == site_id, Site.deleted == True).first()
    if db_site is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Soft-deleted site not found"
        )
    
    db_site.deleted = False
    db_site.deleted_at = None
    db_site.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_site)
    return db_site 