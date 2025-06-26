from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class AlertBase(BaseModel):
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None

class AlertCreate(AlertBase):
    silo_id: int

class AlertUpdate(BaseModel):
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Decimal] = None
    threshold: Optional[Decimal] = None
    is_resolved: Optional[bool] = None

class Alert(AlertBase):
    id: UUID
    silo_id: int
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[UUID] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True) 