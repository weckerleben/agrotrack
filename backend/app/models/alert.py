from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, Boolean, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    silo_id = Column(Integer, ForeignKey("silos.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # temperature, humidity, volume, system
    severity = Column(String(50), nullable=False)  # low, medium, high, critical
    title = Column(String(255), nullable=False)
    description = Column(Text)
    value = Column(DECIMAL(10, 2))
    threshold = Column(DECIMAL(10, 2))
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    silo = relationship("Silo", back_populates="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<Alert(type={self.alert_type}, severity={self.severity}, resolved={self.is_resolved})>" 