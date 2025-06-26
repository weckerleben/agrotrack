from sqlalchemy import Column, Integer, String, DECIMAL, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Silo(Base):
    __tablename__ = "silos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    capacity_tons = Column(Integer, nullable=False)
    max_temperature = Column(DECIMAL(5, 2), default=30.0)
    max_humidity = Column(DECIMAL(5, 2), default=75.0)
    status = Column(String(50), default='active')  # active, inactive, maintenance
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    readings = relationship("SiloReading", back_populates="silo", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="silo", cascade="all, delete-orphan")
    logistics = relationship("Logistics", back_populates="silo")
    
    def __repr__(self):
        return f"<Silo(name={self.name}, location={self.location})>"

class SiloReading(Base):
    __tablename__ = "silo_readings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    silo_id = Column(Integer, ForeignKey("silos.id", ondelete="CASCADE"), nullable=False)
    temperature = Column(DECIMAL(5, 2), nullable=False)
    humidity = Column(DECIMAL(5, 2), nullable=False)
    volume_percent = Column(DECIMAL(5, 2), nullable=False)
    volume_tons = Column(DECIMAL(10, 2))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    silo = relationship("Silo", back_populates="readings")
    
    def __repr__(self):
        return f"<SiloReading(silo_id={self.silo_id}, temp={self.temperature}, humidity={self.humidity})>" 