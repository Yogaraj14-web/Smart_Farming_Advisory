# db/database.py
"""
Database operations for Smart Farming Advisory System.

Uses psycopg2 for PostgreSQL (Neon DB) with environment variable for connection.
All credentials are loaded from environment variables - no hardcoded values.
"""
import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any
from datetime import datetime, date


# ============================================================================
# CONNECTION MANAGEMENT
# ============================================================================

def get_connection():
    """
    Create and return a PostgreSQL database connection.
    
    Uses DATABASE_URL environment variable in format:
    postgresql://username:password@host:port/database
    
    Returns:
        psycopg2.connection: Active database connection
        
    Raises:
        psycopg2.Error: If connection fails
    """
    # Load connection string from environment variable
    # Format: postgresql://user:pass@host:5432/dbname
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    try:
        # Establish connection with auto-commit for simple queries
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.Error as e:
        raise psycopg2.Error(f"Failed to connect to database: {e}")


def get_cursor(dict_cursor: bool = False):
    """
    Get a database cursor with optional dictionary-style access.
    
    Args:
        dict_cursor: If True, returns RealDictCursor for column-name access
        
    Returns:
        Tuple of (connection, cursor)
    """
    conn = get_connection()
    cursor_type = RealDictCursor if dict_cursor else None
    cur = conn.cursor(cursor_factory=cursor_type)
    return conn, cur


# ============================================================================
# SENSOR DATA OPERATIONS
# ============================================================================

def insert_sensor_data(
    user_id: int,
    soil_moisture: float,
    air_temperature: float,
    air_humidity: float,
    soil_temperature: Optional[float] = None,
    soil_ph: Optional[float] = None,
    light_intensity: Optional[float] = None,
    sensor_id: Optional[str] = None,
    recorded_at: Optional[datetime] = None
) -> int:
    """
    Insert a new sensor reading into the database.
    
    Args:
        user_id: Foreign key to users table
        soil_moisture: Soil moisture percentage (0-100)
        air_temperature: Air temperature in Celsius
        air_humidity: Humidity percentage (0-100)
        soil_temperature: Soil temperature in Celsius
        soil_ph: Soil pH level (0-14)
        light_intensity: Light intensity in Lux
        sensor_id: IoT device identifier
        recorded_at: Timestamp of reading (defaults to now)
        
    Returns:
        int: ID of the inserted sensor data record
    """
    conn, cur = get_cursor()
    
    try:
        # SQL INSERT query for sensor data
        query = """
            INSERT INTO sensor_data (
                user_id, soil_moisture, air_temperature, air_humidity,
                soil_temperature, soil_ph, light_intensity, sensor_id, recorded_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
        """
        
        # Execute with parameterized query to prevent SQL injection
        cur.execute(query, (
            user_id, soil_moisture, air_temperature, air_humidity,
            soil_temperature, soil_ph, light_intensity, sensor_id, recorded_at
        ))
        
        # Get the generated ID
        sensor_id = cur.fetchone()[0]
        conn.commit()
        
        return sensor_id
        
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_sensor_history(
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Fetch historical sensor data for a user.
    
    Args:
        user_id: Filter by user
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of records to return
        
    Returns:
        List of sensor data records as dictionaries
    """
    conn, cur = get_cursor(dict_cursor=True)
    
    try:
        # Base query with optional date filtering
        query = """
            SELECT 
                id, user_id, soil_moisture, air_temperature, air_humidity,
                soil_temperature, soil_ph, light_intensity, sensor_id, recorded_at
            FROM sensor_data
            WHERE user_id = %s
        """
        
        params = [user_id]
        
        # Add date range conditions if provided
        if start_date:
            query += " AND recorded_at >= %s"
            params.append(start_date)
        if end_date:
            query += " AND recorded_at <= %s"
            params.append(end_date)
        
        # Order by most recent first and limit results
        query += " ORDER BY recorded_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        # Convert RealDictRow to regular dict
        return [dict(row) for row in rows]
        
    finally:
        cur.close()
        conn.close()


# ============================================================================
# WEATHER LOG OPERATIONS
# ============================================================================

def insert_weather_log(
    user_id: int,
    location: str,
    temperature: float,
    humidity: float,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    feels_like: Optional[float] = None,
    pressure: Optional[float] = None,
    wind_speed: Optional[float] = None,
    wind_direction: Optional[int] = None,
    cloud_cover: Optional[int] = None,
    visibility: Optional[int] = None,
    weather_condition: Optional[str] = None,
    weather_description: Optional[str] = None,
    sunrise: Optional[time] = None,
    sunset: Optional[time] = None,
    api_response: Optional[Dict] = None,
    fetched_at: Optional[datetime] = None
) -> int:
    """
    Insert a weather log entry from OpenWeather API response.
    
    Args:
        user_id: Foreign key to users table
        location: Location name or coordinates
        temperature: Current temperature in Celsius
        humidity: Humidity percentage
        latitude: Geographic latitude
        longitude: Geographic longitude
        feels_like: Feels-like temperature
        pressure: Atmospheric pressure in hPa
        wind_speed: Wind speed in m/s
        wind_direction: Wind direction in degrees
        cloud_cover: Cloud cover percentage
        visibility: Visibility in meters
        weather_condition: Main weather condition (e.g., "Clear")
        weather_description: Detailed description
        sunrise: Sunrise time
        sunset: Sunset time
        api_response: Full API response as JSON
        fetched_at: Timestamp of fetch (defaults to now)
        
    Returns:
        int: ID of the inserted weather log
    """
    conn, cur = get_cursor()
    
    try:
        # Convert api_response dict to JSON string for storage
        api_response_json = json.dumps(api_response) if api_response else None
        
        query = """
            INSERT INTO weather_logs (
                user_id, location, latitude, longitude, temperature, feels_like,
                humidity, pressure, wind_speed, wind_direction, cloud_cover,
                visibility, weather_condition, weather_description, sunrise, sunset,
                api_response, fetched_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
        """
        
        cur.execute(query, (
            user_id, location, latitude, longitude, temperature, feels_like,
            humidity, pressure, wind_speed, wind_direction, cloud_cover,
            visibility, weather_condition, weather_description, sunrise, sunset,
            api_response_json, fetched_at
        ))
        
        weather_id = cur.fetchone()[0]
        conn.commit()
        
        return weather_id
        
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_weather_history(
    user_id: int,
    location: Optional[str] = None,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    Fetch weather log history for a user.
    
    Args:
        user_id: Filter by user
        location: Optional location filter
        days: Number of days of history to retrieve
        
    Returns:
        List of weather log records as dictionaries
    """
    conn, cur = get_cursor(dict_cursor=True)
    
    try:
        query = """
            SELECT 
                id, user_id, location, latitude, longitude, temperature,
                humidity, pressure, wind_speed, weather_condition, fetched_at
            FROM weather_logs
            WHERE user_id = %s
                AND fetched_at >= NOW() - INTERVAL '%s days'
        """
        
        params = [user_id, days]
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        query += " ORDER BY fetched_at DESC"
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        return [dict(row) for row in rows]
        
    finally:
        cur.close()
        conn.close()


# ============================================================================
# PREDICTION OPERATIONS
# ============================================================================

def insert_prediction(
    user_id: int,
    predicted_yield: float,
    confidence_score: float,
    recommendation: str,
    sensor_data_id: Optional[int] = None,
    weather_log_id: Optional[int] = None,
    crop_type: Optional[str] = None,
    model_version: str = "1.0",
    prediction_type: str = "yield"
) -> int:
    """
    Insert a new prediction record from ML model.
    
    Args:
        user_id: Foreign key to users table
        predicted_yield: Predicted yield in tonnes/hectare
        confidence_score: Model confidence (0.0 to 1.0)
        recommendation: Farming recommendation text
        sensor_data_id: Optional link to sensor data
        weather_log_id: Optional link to weather log
        crop_type: Type of crop being predicted
        model_version: Version of ML model used
        prediction_type: Type of prediction (yield, disease, irrigation)
        
    Returns:
        int: ID of the inserted prediction
    """
    conn, cur = get_cursor()
    
    try:
        query = """
            INSERT INTO predictions (
                user_id, sensor_data_id, weather_log_id, predicted_yield,
                confidence_score, recommendation, crop_type, model_version,
                prediction_type
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING id;
        """
        
        cur.execute(query, (
            user_id, sensor_data_id, weather_log_id, predicted_yield,
            confidence_score, recommendation, crop_type, model_version,
            prediction_type
        ))
        
        prediction_id = cur.fetchone()[0]
        conn.commit()
        
        return prediction_id
        
    except psycopg2.Error as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def get_prediction_history(
    user_id: int,
    prediction_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Fetch prediction history for a user.
    
    Args:
        user_id: Filter by user
        prediction_type: Optional filter by prediction type
        limit: Maximum records to return
        
    Returns:
        List of prediction records as dictionaries
    """
    conn, cur = get_cursor(dict_cursor=True)
    
    try:
        query = """
            SELECT 
                p.id, p.user_id, p.predicted_yield, p.confidence_score,
                p.recommendation, p.crop_type, p.model_version, p.prediction_type,
                p.created_at, s.soil_moisture, s.air_temperature,
                w.temperature as weather_temp, w.humidity as weather_humidity
            FROM predictions p
            LEFT JOIN sensor_data s ON p.sensor_data_id = s.id
            LEFT JOIN weather_logs w ON p.weather_log_id = w.id
            WHERE p.user_id = %s
        """
        
        params = [user_id]
        
        if prediction_type:
            query += " AND p.prediction_type = %s"
            params.append(prediction_type)
        
        query += " ORDER BY p.created_at DESC LIMIT %s"
        params.append(limit)
        
        cur.execute(query, params)
        rows = cur.fetchall()
        
        return [dict(row) for row in rows]
        
    finally:
        cur.close()
        conn.close()


def get_latest_prediction(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch the most recent prediction for a user.
    
    Args:
        user_id: Filter by user
        
    Returns:
        Latest prediction record or None if no predictions exist
    """
    conn, cur = get_cursor(dict_cursor=True)
    
    try:
        # Get the most recent prediction with joined sensor and weather data
        query = """
            SELECT 
                p.id, p.predicted_yield, p.confidence_score, p.recommendation,
                p.crop_type, p.model_version, p.prediction_type, p.created_at,
                s.soil_moisture, s.air_temperature, s.air_humidity,
                w.temperature as weather_temp, w.humidity as weather_humidity,
                w.weather_condition
            FROM predictions p
            LEFT JOIN sensor_data s ON p.sensor_data_id = s.id
            LEFT JOIN weather_logs w ON p.weather_log_id = w.id
            WHERE p.user_id = %s
            ORDER BY p.created_at DESC
            LIMIT 1;
        """
        
        cur.execute(query, (user_id,))
        row = cur.fetchone()
        
        return dict(row) if row else None
        
    finally:
        cur.close()
        conn.close()


# ============================================================================
# USER OPERATIONS (Optional Helpers)
# ============================================================================

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch user by ID.
    
    Args:
        user_id: User's ID
        
    Returns:
        User record or None if not found
    """
    conn, cur = get_cursor(dict_cursor=True)
    
    try:
        query = """
            SELECT id, username, email, full_name, farm_location, created_at
            FROM users
            WHERE id = %s;
        """
        
        cur.execute(query, (user_id,))
        row = cur.fetchone()
        
        return dict(row) if row else None
        
    finally:
        cur.close()
        conn.close()
