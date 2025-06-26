from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import Alert as AlertSchema, AlertCreate, AlertUpdate

logger = structlog.get_logger()
router = APIRouter()

@router.get("/", response_model=List[AlertSchema])
async def read_alerts(
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    is_resolved: Optional[bool] = None,
    silo_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve alerts with optional filtering
    """
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    if silo_id:
        query = query.filter(Alert.silo_id == silo_id)
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    return alerts

@router.post("/", response_model=AlertSchema)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new alert
    """
    db_alert = Alert(**alert.model_dump())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    logger.info("Alert created", 
                alert_id=str(db_alert.id),
                silo_id=alert.silo_id,
                alert_type=alert.alert_type,
                severity=alert.severity,
                created_by=str(current_user.id))
    
    return db_alert

@router.get("/{alert_id}", response_model=AlertSchema)
async def read_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get alert by ID
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return alert

@router.put("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_id: str,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update alert
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_data = alert_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    db.commit()
    db.refresh(alert)
    
    logger.info("Alert updated", alert_id=alert_id, updated_by=str(current_user.id))
    
    return alert

@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mark alert as resolved
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert.is_resolved:
        raise HTTPException(status_code=400, detail="Alert is already resolved")
    
    alert.is_resolved = True
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = current_user.id
    
    db.commit()
    db.refresh(alert)
    
    logger.info("Alert resolved", alert_id=alert_id, resolved_by=str(current_user.id))
    
    return {"message": "Alert resolved successfully", "alert": alert}

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    Delete alert (admin only)
    """
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    
    logger.info("Alert deleted", alert_id=alert_id, deleted_by=str(current_user.id))
    
    return {"message": "Alert deleted successfully"}

@router.get("/silo/{silo_id}", response_model=List[AlertSchema])
async def read_silo_alerts(
    silo_id: int,
    skip: int = 0,
    limit: int = 100,
    is_resolved: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all alerts for a specific silo
    """
    query = db.query(Alert).filter(Alert.silo_id == silo_id)
    
    if is_resolved is not None:
        query = query.filter(Alert.is_resolved == is_resolved)
    
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    return alerts 