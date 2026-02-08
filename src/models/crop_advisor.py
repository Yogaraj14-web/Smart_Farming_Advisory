# src/models/crop_advisor.py
"""Main advisory logic combining ML and weather data."""
from typing import Dict, Any
from src.models.weather_service import WeatherService
from src.models.ml_models import YieldPredictor
from config.settings import ML_MODEL_PATH


class CropAdvisor:
    """Main advisor class for farming recommendations."""

    def __init__(self):
        self.weather_service = WeatherService()
        self.yield_predictor = YieldPredictor(ML_MODEL_PATH)

    def predict_yield(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict crop yield for given farm parameters."""
        # TODO: Extract features, run model, format response
        pass

    def generate_advisory(self, farm_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate farming advisory recommendations."""
        # TODO: Combine weather + ML predictions for recommendations
        pass

    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get weather data for advisory."""
        return self.weather_service.get_current_weather(location)
