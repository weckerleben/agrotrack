from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.silo import Silo, SiloReading
from app.models.alert import Alert
from app.models.logistics import Logistics

logger = structlog.get_logger()
router = APIRouter()

@router.get("/kpis")
async def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get key performance indicators for the dashboard
    """
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    
    # Total silos
    total_silos = db.query(func.count(Silo.id)).scalar()
    active_silos = db.query(func.count(Silo.id)).filter(Silo.status == 'active').scalar()
    
    # Total capacity and current volume
    total_capacity = db.query(func.sum(Silo.capacity_tons)).scalar() or 0
    
    # Current volume from latest readings
    latest_readings_subquery = db.query(
        SiloReading.silo_id,
        func.max(SiloReading.timestamp).label('latest_timestamp')
    ).group_by(SiloReading.silo_id).subquery()
    
    current_volume = db.query(func.sum(SiloReading.volume_tons)).join(
        latest_readings_subquery,
        and_(
            SiloReading.silo_id == latest_readings_subquery.c.silo_id,
            SiloReading.timestamp == latest_readings_subquery.c.latest_timestamp
        )
    ).scalar() or 0
    
    # Average temperature and humidity from last 24 hours
    recent_stats = db.query(
        func.avg(SiloReading.temperature).label('avg_temperature'),
        func.avg(SiloReading.humidity).label('avg_humidity'),
        func.count(SiloReading.id).label('total_readings')
    ).filter(SiloReading.timestamp >= yesterday).first()
    
    # Active alerts
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.is_resolved == False).scalar()
    critical_alerts = db.query(func.count(Alert.id)).filter(
        and_(Alert.is_resolved == False, Alert.severity == 'critical')
    ).scalar()
    
    # Logistics statistics
    total_logistics = db.query(func.count(Logistics.id)).scalar()
    in_transit = db.query(func.count(Logistics.id)).filter(Logistics.status == 'in_transit').scalar()
    delivered_today = db.query(func.count(Logistics.id)).filter(
        and_(
            Logistics.status == 'delivered',
            Logistics.actual_arrival >= yesterday
        )
    ).scalar()
    
    # Recent alerts (last 7 days)
    recent_alerts = db.query(func.count(Alert.id)).filter(Alert.created_at >= week_ago).scalar()
    
    return {
        "silos": {
            "total": total_silos,
            "active": active_silos,
            "capacity_utilization": round((current_volume / total_capacity * 100), 2) if total_capacity > 0 else 0,
            "total_capacity_tons": float(total_capacity),
            "current_volume_tons": float(current_volume)
        },
        "readings": {
            "average_temperature": round(float(recent_stats.avg_temperature), 2) if recent_stats.avg_temperature else 0,
            "average_humidity": round(float(recent_stats.avg_humidity), 2) if recent_stats.avg_humidity else 0,
            "total_readings_24h": recent_stats.total_readings or 0
        },
        "alerts": {
            "active": active_alerts,
            "critical": critical_alerts,
            "recent_7_days": recent_alerts
        },
        "logistics": {
            "total": total_logistics,
            "in_transit": in_transit,
            "delivered_today": delivered_today
        },
        "timestamp": now.isoformat()
    }

@router.get("/trends")
async def get_dashboard_trends(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get trend data for charts
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily temperature and humidity trends
    daily_trends = db.query(
        func.date(SiloReading.timestamp).label('date'),
        func.avg(SiloReading.temperature).label('avg_temperature'),
        func.avg(SiloReading.humidity).label('avg_humidity'),
        func.avg(SiloReading.volume_percent).label('avg_volume_percent')
    ).filter(
        SiloReading.timestamp >= start_date
    ).group_by(
        func.date(SiloReading.timestamp)
    ).order_by(
        func.date(SiloReading.timestamp)
    ).all()
    
    # Daily alert counts
    daily_alerts = db.query(
        func.date(Alert.created_at).label('date'),
        func.count(Alert.id).label('alert_count'),
        func.count(func.nullif(Alert.severity == 'critical', False)).label('critical_count')
    ).filter(
        Alert.created_at >= start_date
    ).group_by(
        func.date(Alert.created_at)
    ).order_by(
        func.date(Alert.created_at)
    ).all()
    
    # Format trends data
    temperature_trend = [
        {
            "date": trend.date.isoformat(),
            "temperature": round(float(trend.avg_temperature), 2),
            "humidity": round(float(trend.avg_humidity), 2),
            "volume_percent": round(float(trend.avg_volume_percent), 2)
        }
        for trend in daily_trends
    ]
    
    alerts_trend = [
        {
            "date": alert.date.isoformat(),
            "total_alerts": alert.alert_count,
            "critical_alerts": alert.critical_count or 0
        }
        for alert in daily_alerts
    ]
    
    return {
        "temperature_humidity": temperature_trend,
        "alerts": alerts_trend,
        "period_days": days
    }

@router.get("/silo-status")
async def get_silo_status_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """
    Get status summary for all silos
    """
    silos = db.query(Silo).filter(Silo.status == 'active').all()
    
    result = []
    for silo in silos:
        # Get latest reading
        latest_reading = db.query(SiloReading).filter(
            SiloReading.silo_id == silo.id
        ).order_by(desc(SiloReading.timestamp)).first()
        
        # Get active alerts count
        active_alerts_count = db.query(func.count(Alert.id)).filter(
            and_(
                Alert.silo_id == silo.id,
                Alert.is_resolved == False
            )
        ).scalar()
        
        # Determine status based on thresholds
        status = "normal"
        if latest_reading:
            if (latest_reading.temperature > silo.max_temperature or 
                latest_reading.humidity > silo.max_humidity):
                status = "warning"
            if active_alerts_count > 0:
                # Check if any critical alerts
                critical_alerts = db.query(func.count(Alert.id)).filter(
                    and_(
                        Alert.silo_id == silo.id,
                        Alert.is_resolved == False,
                        Alert.severity == 'critical'
                    )
                ).scalar()
                if critical_alerts > 0:
                    status = "critical"
                elif status != "critical":
                    status = "warning"
        
        result.append({
            "silo_id": silo.id,
            "name": silo.name,
            "location": silo.location,
            "status": status,
            "capacity_tons": silo.capacity_tons,
            "current_volume_tons": float(latest_reading.volume_tons) if latest_reading and latest_reading.volume_tons else 0,
            "volume_percent": float(latest_reading.volume_percent) if latest_reading else 0,
            "temperature": float(latest_reading.temperature) if latest_reading else 0,
            "humidity": float(latest_reading.humidity) if latest_reading else 0,
            "active_alerts": active_alerts_count,
            "last_reading": latest_reading.timestamp.isoformat() if latest_reading else None
        })
    
    return result

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get recent system activity
    """
    # Recent alerts
    recent_alerts = db.query(Alert).order_by(desc(Alert.created_at)).limit(limit).all()
    
    # Recent logistics updates
    recent_logistics = db.query(Logistics).order_by(desc(Logistics.updated_at)).limit(limit).all()
    
    # Format activity data
    alerts_activity = [
        {
            "type": "alert",
            "id": str(alert.id),
            "title": alert.title,
            "severity": alert.severity,
            "silo_id": alert.silo_id,
            "created_at": alert.created_at.isoformat(),
            "is_resolved": alert.is_resolved
        }
        for alert in recent_alerts
    ]
    
    logistics_activity = [
        {
            "type": "logistics",
            "id": str(logistics.id),
            "truck_id": logistics.truck_id,
            "status": logistics.status,
            "route": logistics.route,
            "updated_at": logistics.updated_at.isoformat()
        }
        for logistics in recent_logistics
    ]
    
    return {
        "alerts": alerts_activity,
        "logistics": logistics_activity
    } 