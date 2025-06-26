from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class LogisticsBase(BaseModel):
    truck_id: str
    driver_name: str
    route: str
    origin: str
    destination: str
    status: Optional[str] = 'pending'
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    cargo_weight: Optional[Decimal] = None
    silo_id: Optional[int] = None

class LogisticsCreate(LogisticsBase):
    pass

class LogisticsUpdate(BaseModel):
    truck_id: Optional[str] = None
    driver_name: Optional[str] = None
    route: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    status: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    cargo_weight: Optional[Decimal] = None
    silo_id: Optional[int] = None

class Logistics(LogisticsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LogisticsTrackingBase(BaseModel):
    latitude: Decimal
    longitude: Decimal
    speed: Optional[Decimal] = None
    heading: Optional[Decimal] = None

class LogisticsTrackingCreate(LogisticsTrackingBase):
    logistics_id: UUID

class LogisticsTracking(LogisticsTrackingBase):
    id: UUID
    logistics_id: UUID
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)

class LogisticsWithTracking(Logistics):
    tracking: List[LogisticsTracking] = []
    latest_tracking: Optional[LogisticsTracking] = None 