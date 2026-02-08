# db/__init__.py
"""Database package for Smart Farming Advisory System."""
from db.database import (
    get_connection,
    get_cursor,
    insert_sensor_data,
    get_sensor_history,
    insert_weather_log,
    get_weather_history,
    insert_prediction,
    get_prediction_history,
    get_latest_prediction,
    get_user_by_id
)

__all__ = [
    "get_connection",
    "get_cursor",
    "insert_sensor_data",
    "get_sensor_history",
    "insert_weather_log",
    "get_weather_history",
    "insert_prediction",
    "get_prediction_history",
    "get_latest_prediction",
    "get_user_by_id"
]
