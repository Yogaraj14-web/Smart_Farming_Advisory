# config/constants.py
"""Application constants."""

# Crop Types
CROP_TYPES = ["wheat", "rice", "corn", "soybean", "cotton", "sugarcane"]

# Soil Types
SOIL_TYPES = ["clay", "sandy", "loamy", "silty", "peaty", "chalky"]

# Irrigation Thresholds (mm per day)
IRRIGATION_THRESHOLDS = {
    "wheat": 5.0,
    "rice": 8.0,
    "corn": 6.0,
    "soybean": 5.5,
    "cotton": 7.0,
    "sugarcane": 6.5,
}

# Temperature Ranges (Celsius) for Optimal Growth
TEMP_RANGES = {
    "wheat": (10, 25),
    "rice": (20, 35),
    "corn": (18, 32),
    "soybean": (15, 30),
    "cotton": (20, 35),
    "sugarcane": (24, 35),
}
