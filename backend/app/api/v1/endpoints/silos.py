from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user, require_roles
from app.models.user import User
from app.models.silo import Silo, SiloReading
from app.schemas.silo import (
    Silo as SiloSchema, 
    SiloCreate, 
    SiloUpdate, 
    SiloReading as SiloReadingSchema,
    SiloReadingCreate,
    SiloReadingInput,
    SiloWithLatestReading
)

logger = structlog.get_logger()
router = APIRouter()

@router.get("/", response_model=List[SiloWithLatestReading])
async def read_silos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve silos with latest readings
    """
    query = db.query(Silo)
    
    if status:
        query = query.filter(Silo.status == status)
    
    silos = query.offset(skip).limit(limit).all()
    
    result = []
    for silo in silos:
        # Get latest reading
        latest_reading = db.query(SiloReading).filter(
            SiloReading.silo_id == silo.id
        ).order_by(desc(SiloReading.timestamp)).first()
        
        # Get aggregated data from last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        stats = db.query(
            func.count(SiloReading.id).label('readings_count'),
            func.avg(SiloReading.temperature).label('avg_temperature'),
            func.avg(SiloReading.humidity).label('avg_humidity')
        ).filter(
            and_(
                SiloReading.silo_id == silo.id,
                SiloReading.timestamp >= yesterday
            )
        ).first()
        
        silo_dict = {
            **silo.__dict__,
            "latest_reading": latest_reading,
            "readings_count": stats.readings_count or 0,
            "average_temperature": stats.avg_temperature,
            "average_humidity": stats.avg_humidity,
            "current_volume_tons": latest_reading.volume_tons if latest_reading else None
        }
        
        result.append(silo_dict)
    
    return result

@router.post("/", response_model=SiloSchema)
async def create_silo(
    silo: SiloCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "operator"]))
):
    """
    Create new silo
    """
    db_silo = Silo(**silo.model_dump())
    db.add(db_silo)
    db.commit()
    db.refresh(db_silo)
    
    logger.info("Silo created", silo_id=db_silo.id, name=db_silo.name, created_by=str(current_user.id))
    
    return db_silo

@router.get("/{silo_id}", response_model=SiloWithLatestReading)
async def read_silo(
    silo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get silo by ID with latest reading
    """
    silo = db.query(Silo).filter(Silo.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    # Get latest reading
    latest_reading = db.query(SiloReading).filter(
        SiloReading.silo_id == silo_id
    ).order_by(desc(SiloReading.timestamp)).first()
    
    # Get aggregated data from last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    stats = db.query(
        func.count(SiloReading.id).label('readings_count'),
        func.avg(SiloReading.temperature).label('avg_temperature'),
        func.avg(SiloReading.humidity).label('avg_humidity')
    ).filter(
        and_(
            SiloReading.silo_id == silo_id,
            SiloReading.timestamp >= yesterday
        )
    ).first()
    
    silo_dict = {
        **silo.__dict__,
        "latest_reading": latest_reading,
        "readings_count": stats.readings_count or 0,
        "average_temperature": stats.avg_temperature,
        "average_humidity": stats.avg_humidity,
        "current_volume_tons": latest_reading.volume_tons if latest_reading else None
    }
    
    return silo_dict

@router.put("/{silo_id}", response_model=SiloSchema)
async def update_silo(
    silo_id: int,
    silo_update: SiloUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "operator"]))
):
    """
    Update silo
    """
    silo = db.query(Silo).filter(Silo.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    update_data = silo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(silo, field, value)
    
    db.commit()
    db.refresh(silo)
    
    logger.info("Silo updated", silo_id=silo_id, updated_by=str(current_user.id))
    
    return silo

@router.delete("/{silo_id}")
async def delete_silo(
    silo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin"]))
):
    """
    Delete silo (admin only)
    """
    silo = db.query(Silo).filter(Silo.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    db.delete(silo)
    db.commit()
    
    logger.info("Silo deleted", silo_id=silo_id, deleted_by=str(current_user.id))
    
    return {"message": "Silo deleted successfully"}

@router.get("/{silo_id}/readings", response_model=List[SiloReadingSchema])
async def read_silo_readings(
    silo_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get silo readings with optional date filtering
    """
    # Verify silo exists
    silo = db.query(Silo).filter(Silo.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    query = db.query(SiloReading).filter(SiloReading.silo_id == silo_id)
    
    if start_date:
        query = query.filter(SiloReading.timestamp >= start_date)
    if end_date:
        query = query.filter(SiloReading.timestamp <= end_date)
    
    readings = query.order_by(desc(SiloReading.timestamp)).offset(skip).limit(limit).all()
    
    return readings

@router.post("/{silo_id}/readings", response_model=SiloReadingSchema)
async def create_silo_reading(
    silo_id: int,
    reading: SiloReadingInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new silo reading (typically called by IoT devices or simulators)
    """
    # Verify silo exists
    silo = db.query(Silo).filter(Silo.id == silo_id).first()
    if not silo:
        raise HTTPException(status_code=404, detail="Silo not found")
    
    # Calculate volume in tons if not provided
    reading_data = reading.model_dump()
    if not reading_data.get('volume_tons') and silo.capacity_tons:
        reading_data['volume_tons'] = (silo.capacity_tons * reading.volume_percent) / 100
    
    db_reading = SiloReading(
        silo_id=silo_id,
        **reading_data
    )
    
    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)
    
    logger.info("Silo reading created", 
                silo_id=silo_id, 
                temperature=float(reading.temperature),
                humidity=float(reading.humidity),
                volume_percent=float(reading.volume_percent))
    
    return db_reading 