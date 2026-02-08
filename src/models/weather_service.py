# src/models/weather_service.py
"""OpenWeather API integration."""
import requests
from config.settings import OPENWEATHER_API_KEY, OPENWEATHER_BASE_URL


class WeatherService:
    """Service for fetching weather data."""

    def __init__(self):
        self.api_key = OPENWEATHER_API_KEY
        self.base_url = OPENWEATHER_BASE_URL

    def get_current_weather(self, location: str) -> dict:
        """Fetch current weather for a location."""
        # TODO: Implement API call with error handling
        pass

    def get_forecast(self, location: str, days: int = 7) -> list:
        """Fetch weather forecast."""
        # TODO: Implement forecast API call
        pass

    def get_agricultural_metrics(self, location: str) -> dict:
        """Get weather metrics relevant for farming."""
        # TODO: Extract ET0, precipitation, etc.
        pass
