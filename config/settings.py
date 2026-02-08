# config/settings.py
"""Environment variables and configuration loader."""
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL")  # Neon DB PostgreSQL connection string

# OpenWeather API
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Application
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# ML Models
ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "ml_models/crop_yield_model.pkl")
