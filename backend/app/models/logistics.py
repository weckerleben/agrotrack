from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Logistics(Base):
    __tablename__ = "logistics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    truck_id = Column(String(100), nullable=False)
    driver_name = Column(String(255), nullable=False)
    route = Column(String(255), nullable=False)
    origin = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    status = Column(String(50), default='pending')  # pending, in_transit, delivered, cancelled
    estimated_arrival = Column(DateTime(timezone=True))
    actual_arrival = Column(DateTime(timezone=True))
    cargo_weight = Column(DECIMAL(10, 2))
    silo_id = Column(Integer, ForeignKey("silos.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    silo = relationship("Silo", back_populates="logistics")
    tracking = relationship("LogisticsTracking", back_populates="logistics", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Logistics(truck_id={self.truck_id}, status={self.status})>"

class LogisticsTracking(Base):
    __tablename__ = "logistics_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    logistics_id = Column(UUID(as_uuid=True), ForeignKey("logistics.id", ondelete="CASCADE"), nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    speed = Column(DECIMAL(5, 2))
    heading = Column(DECIMAL(5, 2))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    logistics = relationship("Logistics", back_populates="tracking")
    
    def __repr__(self):
        return f"<LogisticsTracking(logistics_id={self.logistics_id}, lat={self.latitude}, lng={self.longitude})>" 