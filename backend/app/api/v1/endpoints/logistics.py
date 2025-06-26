from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.user import User
from app.models.logistics import Logistics, LogisticsTracking
from app.schemas.logistics import (
    Logistics as LogisticsSchema, 
    LogisticsCreate, 
    LogisticsUpdate,
    LogisticsTracking as LogisticsTrackingSchema,
    LogisticsTrackingCreate,
    LogisticsWithTracking
)

logger = structlog.get_logger()
router = APIRouter()

@router.get("/", response_model=List[LogisticsWithTracking])
async def read_logistics(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve logistics entries with tracking data
    """
    query = db.query(Logistics)
    
    if status:
        query = query.filter(Logistics.status == status)
    
    logistics_entries = query.order_by(desc(Logistics.created_at)).offset(skip).limit(limit).all()
    
    result = []
    for logistics in logistics_entries:
        # Get all tracking data
        tracking_data = db.query(LogisticsTracking).filter(
            LogisticsTracking.logistics_id == logistics.id
        ).order_by(desc(LogisticsTracking.timestamp)).all()
        
        # Get latest tracking
        latest_tracking = tracking_data[0] if tracking_data else None
        
        logistics_dict = {
            **logistics.__dict__,
            "tracking": tracking_data,
            "latest_tracking": latest_tracking
        }
        
        result.append(logistics_dict)
    
    return result

@router.post("/", response_model=LogisticsSchema)
async def create_logistics(
    logistics: LogisticsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "logistics"]))
):
    """
    Create new logistics entry
    """
    db_logistics = Logistics(**logistics.model_dump())
    db.add(db_logistics)
    db.commit()
    db.refresh(db_logistics)
    
    logger.info("Logistics entry created", 
                logistics_id=str(db_logistics.id),
                truck_id=db_logistics.truck_id,
                route=db_logistics.route,
                created_by=str(current_user.id))
    
    return db_logistics

@router.get("/{logistics_id}", response_model=LogisticsWithTracking)
async def read_logistics_entry(
    logistics_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get logistics entry by ID with tracking data
    """
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    # Get all tracking data
    tracking_data = db.query(LogisticsTracking).filter(
        LogisticsTracking.logistics_id == logistics_id
    ).order_by(desc(LogisticsTracking.timestamp)).all()
    
    # Get latest tracking
    latest_tracking = tracking_data[0] if tracking_data else None
    
    logistics_dict = {
        **logistics.__dict__,
        "tracking": tracking_data,
        "latest_tracking": latest_tracking
    }
    
    return logistics_dict

@router.put("/{logistics_id}", response_model=LogisticsSchema)
async def update_logistics(
    logistics_id: str,
    logistics_update: LogisticsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "logistics"]))
):
    """
    Update logistics entry
    """
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    update_data = logistics_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(logistics, field, value)
    
    db.commit()
    db.refresh(logistics)
    
    logger.info("Logistics entry updated", logistics_id=logistics_id, updated_by=str(current_user.id))
    
    return logistics

@router.delete("/{logistics_id}")
async def delete_logistics(
    logistics_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    Delete logistics entry (admin only)
    """
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    db.delete(logistics)
    db.commit()
    
    logger.info("Logistics entry deleted", logistics_id=logistics_id, deleted_by=str(current_user.id))
    
    return {"message": "Logistics entry deleted successfully"}

@router.post("/{logistics_id}/tracking", response_model=LogisticsTrackingSchema)
async def create_tracking_update(
    logistics_id: str,
    tracking: LogisticsTrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add tracking update for logistics entry
    """
    # Verify logistics entry exists
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    db_tracking = LogisticsTracking(
        logistics_id=logistics_id,
        **tracking.model_dump()
    )
    
    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)
    
    logger.info("Tracking update created", 
                logistics_id=logistics_id,
                latitude=float(tracking.latitude),
                longitude=float(tracking.longitude))
    
    return db_tracking

@router.get("/{logistics_id}/tracking", response_model=List[LogisticsTrackingSchema])
async def read_tracking_updates(
    logistics_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get tracking updates for logistics entry
    """
    # Verify logistics entry exists
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    tracking_updates = db.query(LogisticsTracking).filter(
        LogisticsTracking.logistics_id == logistics_id
    ).order_by(desc(LogisticsTracking.timestamp)).offset(skip).limit(limit).all()
    
    return tracking_updates

@router.put("/{logistics_id}/status")
async def update_logistics_status(
    logistics_id: str,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "logistics"]))
):
    """
    Update logistics status
    """
    if status not in ["pending", "in_transit", "delivered", "cancelled"]:
        raise HTTPException(
            status_code=400, 
            detail="Invalid status. Must be one of: pending, in_transit, delivered, cancelled"
        )
    
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="Logistics entry not found")
    
    old_status = logistics.status
    logistics.status = status
    
    if status == "delivered":
        logistics.actual_arrival = datetime.utcnow()
    
    db.commit()
    db.refresh(logistics)
    
    logger.info("Logistics status updated", 
                logistics_id=logistics_id,
                old_status=old_status,
                new_status=status,
                updated_by=str(current_user.id))
    
    return {"message": f"Status updated to {status}", "logistics": logistics} 