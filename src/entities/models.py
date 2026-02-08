# src/entities/models.py
"""SQLAlchemy ORM models."""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.services.database import Base
from datetime import datetime


class Farm(Base):
    """Farm model."""
    __tablename__ = "farms"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    area_hectares = Column(Float, nullable=False)
    soil_type = Column(String(50), nullable=False)
    irrigation_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    advisories = relationship("Advisory", back_populates="farm")
    yield_records = relationship("YieldRecord", back_populates="farm")


class Advisory(Base):
    """Advisory model."""
    __tablename__ = "advisories"

    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id"))
    recommendation = Column(Text, nullable=False)
    warning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="advisories")


class YieldRecord(Base):
    """Yield prediction record model."""
    __tablename__ = "yield_records"

    id = Column(String(36), primary_key=True)
    farm_id = Column(String(36), ForeignKey("farms.id"))
    predicted_yield = Column(Float, nullable=False)
    actual_yield = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    farm = relationship("Farm", back_populates="yield_records")
