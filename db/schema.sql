-- db/schema.sql
-- Database schema for Smart Farming Advisory System
-- PostgreSQL (Neon DB compatible)

-- Drop existing tables if they exist (for fresh setup)
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS weather_logs CASCADE;
DROP TABLE IF EXISTS sensor_data CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
-- Stores farmer/user account information
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    farm_location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sensor_data table
-- Stores IoT sensor readings from farm equipment
-- Captures: soil moisture, temperature, humidity, pH levels
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Sensor readings
    soil_moisture DECIMAL(5,2),          -- Percentage 0-100
    air_temperature DECIMAL(5,2),       -- Celsius
    air_humidity DECIMAL(5,2),           -- Percentage 0-100
    soil_temperature DECIMAL(5,2),      -- Celsius
    soil_ph DECIMAL(4,2),               -- pH scale 0-14
    light_intensity DECIMAL(10,2),      -- Lux
    -- Metadata
    sensor_id VARCHAR(100),              -- IoT device identifier
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create weather_logs table
-- Stores historical weather data fetched from OpenWeather API
-- Used for analytics and advisory generation
CREATE TABLE weather_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- Location data
    location VARCHAR(255) NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    -- Weather data from OpenWeather API
    temperature DECIMAL(5,2),           -- Celsius
    feels_like DECIMAL(5,2),             -- Celsius
    humidity DECIMAL(5,2),               -- Percentage
    pressure DECIMAL(6,2),               -- hPa
    wind_speed DECIMAL(6,2),             -- m/s
    wind_direction INTEGER,              -- Degrees 0-360
    cloud_cover INTEGER,                 -- Percentage 0-100
    visibility INTEGER,                  -- Meters
    weather_condition VARCHAR(100),      -- e.g., "Clear", "Rain"
    weather_description TEXT,            -- e.g., "light rain"
    sunrise TIME,
    sunset TIME,
    -- API metadata
    api_response JSONB,                  -- Full API response for debugging
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create predictions table
-- Stores ML model predictions for crop yield and advisories
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sensor_data_id INTEGER REFERENCES sensor_data(id),
    weather_log_id INTEGER REFERENCES weather_logs(id),
    -- Prediction results
    predicted_yield DECIMAL(10,2),       -- tonnes/hectare
    confidence_score DECIMAL(4,3),       -- 0.0 to 1.0
    -- Advisory details
    recommendation TEXT,                  -- Farming advice
    crop_type VARCHAR(100),
    -- Metadata
    model_version VARCHAR(50),
    prediction_type VARCHAR(50),         -- 'yield', 'disease', 'irrigation'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
-- Index on sensor_data for time-based queries
CREATE INDEX idx_sensor_data_user_time 
ON sensor_data(user_id, recorded_at DESC);

-- Index on weather_logs for location-based queries
CREATE INDEX idx_weather_logs_location 
ON weather_logs(location, fetched_at DESC);

-- Index on predictions for user history queries
CREATE INDEX idx_predictions_user_time 
ON predictions(user_id, created_at DESC);

-- Index on predictions for model version tracking
CREATE INDEX idx_predictions_model 
ON predictions(model_version, created_at DESC);
