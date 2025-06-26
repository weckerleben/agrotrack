from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class SiloBase(BaseModel):
    name: str
    location: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    capacity_tons: int
    max_temperature: Optional[Decimal] = Decimal('30.0')
    max_humidity: Optional[Decimal] = Decimal('75.0')
    status: Optional[str] = 'active'

class SiloCreate(SiloBase):
    pass

class SiloUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    capacity_tons: Optional[int] = None
    max_temperature: Optional[Decimal] = None
    max_humidity: Optional[Decimal] = None
    status: Optional[str] = None

class Silo(SiloBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SiloReadingBase(BaseModel):
    temperature: Decimal
    humidity: Decimal
    volume_percent: Decimal
    volume_tons: Optional[Decimal] = None

class SiloReadingCreate(SiloReadingBase):
    silo_id: int

class SiloReadingInput(SiloReadingBase):
    """Schema for API input when silo_id is in URL path"""
    pass

class SiloReading(SiloReadingBase):
    id: UUID
    silo_id: int
    timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SiloWithLatestReading(Silo):
    latest_reading: Optional[SiloReading] = None
    readings_count: int = 0
    average_temperature: Optional[Decimal] = None
    average_humidity: Optional[Decimal] = None
    current_volume_tons: Optional[Decimal] = None 