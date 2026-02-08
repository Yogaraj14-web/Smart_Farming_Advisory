# src/api/schemas.py
"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class FarmInput(BaseModel):
    """Input schema for farm data."""
    farm_id: Optional[str] = None
    location: str
    area_hectares: float
    soil_type: str
    crop_type: str
    planting_date: datetime
    irrigation_type: str


class WeatherInput(BaseModel):
    """Input schema for weather-based advisory."""
    location: str
    forecast_days: int = 7


class YieldPrediction(BaseModel):
    """Response schema for yield prediction."""
    predicted_yield: float
    confidence: float
    units: str = "tonnes/hectare"


class AdvisoryResponse(BaseModel):
    """Response schema for advisory."""
    recommendations: List[str]
    warnings: List[str]
    optimal_actions: List[str]
