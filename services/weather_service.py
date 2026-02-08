# services/weather_service.py
"""
Weather Service for OpenWeather API Integration.

Fetches live weather data and returns simplified conditions for farming decisions.
"""
from dotenv import load_dotenv
import os

load_dotenv()

import os
import requests
from typing import Dict, Any
from datetime import datetime


# =============================================================================
# CONFIGURATION
# =============================================================================

# API key loaded from environment variable
# Set OPENWEATHER_API_KEY in your .env file
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# OpenWeather API endpoints
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# =============================================================================
# SIMPLIFIED WEATHER CONDITIONS
# =============================================================================

# Map OpenWeather condition codes to simplified farming conditions
# Grouped by precipitation likelihood for irrigation decisions

RAIN_CONDITIONS = {
    "Rain": [500, 501, 502, 503, 504, 511, 520, 521, 522, 531],
    "Drizzle": [300, 301, 302, 310, 311, 312, 313, 314, 321],
    "Thunderstorm": [200, 201, 202, 210, 211, 212, 221, 230, 231, 232],
}

CLEAR_CONDITIONS = {
    "Clear": [800],
}

CLOUD_CONDITIONS = {
    "Cloudy": [801, 802, 803, 804],
}


# =============================================================================
# SIMPLIFIED CONDITION MAPPING
# =============================================================================

def get_simplified_condition(condition_code: int, description: str) -> str:
    """
    Map OpenWeather condition code to simplified farming condition.
    
    Args:
        condition_code: OpenWeather API condition code
        description: Weather description string
        
    Returns:
        Simplified condition: "Rain" or "Clear"
    """
    # Check if it's any precipitation condition
    for category, codes in RAIN_CONDITIONS.items():
        if condition_code in codes:
            return "Rain"
    
    # Check for cloudy conditions (affects farming but not precipitation)
    for category, codes in CLOUD_CONDITIONS.items():
        if condition_code in codes:
            return "Clear"
    
    # Default to Clear for unknown codes
    return "Clear"


# =============================================================================
# API CALL FUNCTIONS
# =============================================================================

def get_current_weather(city: str) -> Dict[str, Any]:
    """
    Fetch current weather for a city using OpenWeather API.
    
    Args:
        city: City name (e.g., "Mumbai", "Delhi,IN")
        
    Returns:
        Dictionary with simplified weather data
        
    Raises:
        ValueError: If API key is missing or city is invalid
        requests.RequestException: If API call fails
    """
    # Validate API key
    if not API_KEY:
        raise ValueError(
            "OPENWEATHER_API_KEY environment variable not set. "
            "Get your free API key from https://openweathermap.org/api"
        )
    
    # Validate input
    if not city or not city.strip():
        raise ValueError("City name cannot be empty")
    
    # Prepare API request parameters
    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(CURRENT_WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            raise ValueError("Invalid API key. Please check your OPENWEATHER_API_KEY")
        elif response.status_code == 404:
            raise ValueError(f"City not found: '{city}'. Please check the spelling.")
        else:
            raise requests.RequestException(f"HTTP Error: {e}")
    
    except requests.exceptions.ConnectionError:
        raise requests.RequestException(
            "Failed to connect to OpenWeather API. Check your internet connection."
        )
    
    except requests.exceptions.Timeout:
        raise requests.RequestException(
            "Request timed out. Please try again."
        )
    
    # Parse response
    data = response.json()
    
    # Extract relevant fields
    weather = data.get("weather", [{}])[0]
    condition_code = weather.get("id", 0)
    description = weather.get("description", "")
    
    # Get simplified condition
    simplified_condition = get_simplified_condition(condition_code, description)
    
    # Build result dictionary
    result = {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", ""),
        "timestamp": datetime.now().isoformat(),
        "temperature_celsius": data.get("main", {}).get("temp"),
        "feels_like_celsius": data.get("main", {}).get("feels_like"),
        "humidity_percent": data.get("main", {}).get("humidity"),
        "pressure_hpa": data.get("main", {}).get("pressure"),
        "wind_speed_mps": data.get("wind", {}).get("speed"),
        "condition": simplified_condition,
        "condition_description": description,
        "original_condition_code": condition_code
    }
    
    return result


def get_weather_for_farming(city: str) -> Dict[str, Any]:
    """
    Fetch weather data optimized for farming decisions.
    
    Simplified wrapper that returns only essential farming-related fields.
    
    Args:
        city: City name
        
    Returns:
        Dictionary with farming-relevant weather data
    """
    # Get full weather data
    weather = get_current_weather(city)
    
    # Return simplified farming-specific output
    return {
        "city": weather["city"],
        "temperature_celsius": weather["temperature_celsius"],
        "humidity_percent": weather["humidity_percent"],
        "rain_expected": weather["condition"] == "Rain",
        "condition": weather["condition"],
        "timestamp": weather["timestamp"]
    }


def get_forecast(city: str, days: int = 3) -> list:
    """
    Fetch weather forecast for specified number of days.
    
    Args:
        city: City name
        days: Number of forecast days (max 5 for free tier)
        
    Returns:
        List of daily weather summaries
    """
    if not API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable not set")
    
    if not (1 <= days <= 5):
        raise ValueError("days must be between 1 and 5")
    
    params = {
        "q": city.strip(),
        "appid": API_KEY,
        "units": "metric",
        "cnt": days * 8
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        response.raise_for_status()
    
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to fetch forecast: {e}")
    
    data = response.json()
    forecasts = []
    
    for item in data.get("list", []):
        dt = item.get("dt_txt", "")
        weather = item.get("weather", [{}])[0]
        condition_code = weather.get("id", 0)
        description = weather.get("description", "")
        
        simplified = get_simplified_condition(condition_code, description)
        
        forecasts.append({
            "datetime": dt,
            "temperature_celsius": item.get("main", {}).get("temp"),
            "humidity_percent": item.get("main", {}).get("humidity"),
            "rain_expected": simplified == "Rain",
            "condition": simplified
        })
    
    return forecasts


# =============================================================================
# EXAMPLE USAGE / TESTING
# =============================================================================

def main():
    """Test weather service with sample city."""
    print("=" * 50)
    print("Weather Service Test")
    print("=" * 50)
    
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set.")
        print("Set it in .env file: OPENWEATHER_API_KEY=your_key")
        return
    
    test_cities = ["Vellore", "Chennai", "Srivilliputtur"]
    
    for city in test_cities:
        print(f"\n--- {city} ---")
        try:
            weather = get_weather_for_farming(city)
            print(f"Condition: {weather['condition']}")
            print(f"Rain Expected: {weather['rain_expected']}")
            print(f"Temp: {weather['temperature_celsius']}°C")
            print(f"Humidity: {weather['humidity_percent']}%")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
