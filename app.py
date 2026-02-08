# app.py
"""
Flask REST API for Smart Farming Advisory System.

Endpoints:
- POST /predict: Get fertilizer recommendation without saving
- POST /submit-data: Get recommendation and save to database
- GET /history: Fetch recent prediction records
"""
import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import services
from model.predictor import FertilizerPredictor
from services.weather_service import get_weather_for_farming
from db.database import (
    insert_sensor_data,
    insert_weather_log,
    insert_prediction,
    get_prediction_history
)


# =============================================================================
# CONFIGURATION
# =============================================================================

app = Flask(__name__)

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Enable CORS to allow requests from React frontend running on port 5173
# This is required because frontend and backend run on different ports
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize ML predictor (load once at startup)
try:
    predictor = FertilizerPredictor()
    logger.info("ML model loaded successfully")
except FileNotFoundError as e:
    logger.warning(f"ML model not found: {e}")
    predictor = None


# =============================================================================
# WEATHER CODE MAPPING
# =============================================================================

# Map weather descriptions to ML model weather codes
# ML expects: 0=dry_hot, 1=dry_cool, 2=humid_hot, 3=humid_cool, 4=normal
WEATHER_CODE_MAP = {
    "Rain": {
        "temperature_celsius": lambda t: 2 if t > 25 else 3
    },
    "Clear": {
        "temperature_celsius": lambda t: 0 if t > 25 else 1
    }
}


def weather_to_code(weather_data: dict) -> int:
    """
    Convert weather API response to ML model weather code.

    Args:
        weather_data: Response from get_weather_for_farming()

    Returns:
        Weather code (0-4) for ML model
    """
    condition = weather_data.get("condition", "Clear")
    temperature = weather_data.get("temperature_celsius", 25)

    # Default to normal (4) if condition is unknown
    if condition == "Rain":
        return 2 if temperature > 25 else 3
    else:
        return 0 if temperature > 25 else 1


# =============================================================================
# INPUT VALIDATION
# =============================================================================

def validate_predict_input(data: dict) -> tuple[bool, str]:
    """
    Validate input data for prediction endpoints.

    Args:
        data: Request JSON data

    Returns:
        (is_valid, error_message)
    """
    required_fields = ["nitrogen", "phosphorus", "potassium", "leaf_color", "city"]

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate numeric ranges
    try:
        nitrogen = float(data["nitrogen"])
        phosphorus = float(data["phosphorus"])
        potassium = float(data["potassium"])

        if nitrogen < 0 or phosphorus < 0 or potassium < 0:
            return False, "Nutrient values cannot be negative"

        leaf_color = int(data["leaf_color"])
        if not (0 <= leaf_color <= 5):
            return False, "leaf_color must be between 0 and 5"

    except (TypeError, ValueError) as e:
        return False, f"Invalid data type: {e}"

    return True, ""


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route("/predict", methods=["POST"])
def predict():
    """
    Get fertilizer recommendation without saving to database.

    Request Body:
        {
            "nitrogen": float,
            "phosphorus": float,
            "potassium": float,
            "leaf_color": int (0-5),
            "city": string
        }

    Returns:
        {
            "recommendation": string,
            "confidence": float,
            "weather": dict,
            "input_summary": dict
        }
    """
    # Check if ML model is loaded
    if predictor is None:
        return jsonify({"error": "ML model not loaded"}), 500

    # Validate input
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    is_valid, error = validate_predict_input(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    try:
        logger.info(f"Processing prediction request for city: {data['city']}")

        # Fetch weather data
        weather = get_weather_for_farming(data["city"])
        logger.info(f"Weather fetched: {weather['condition']}, {weather['temperature_celsius']}°C")

        # Convert weather to ML code
        weather_code = weather_to_code(weather)

        # Get ML prediction
        result = predictor.predict(
            nitrogen=float(data["nitrogen"]),
            phosphorus=float(data["phosphorus"]),
            potassium=float(data["potassium"]),
            leaf_color=int(data["leaf_color"]),
            weather=weather_code
        )

        # Build response (remove raw explanation, keep structured data)
        response = {
            "recommendation": result["recommendation"],
            "confidence": result["confidence"],
            "weather": {
                "city": weather["city"],
                "condition": weather["condition"],
                "rain_expected": weather["rain_expected"],
                "temperature_celsius": weather["temperature_celsius"],
                "humidity_percent": weather["humidity_percent"]
            },
            "input_summary": result["input_summary"]
        }

        logger.info(f"Prediction complete: {result['recommendation']} ({result['confidence']:.1%})")
        return jsonify(response), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/submit-data", methods=["POST"])
def submit_data():
    """
    Get recommendation and save sensor data, weather, and prediction to database.

    Request Body:
        {
            "nitrogen": float,
            "phosphorus": float,
            "potassium": float,
            "leaf_color": int (0-5),
            "city": string,
            "user_id": int (optional, defaults to 1)
        }

    Returns:
        {
            "recommendation": string,
            "confidence": float,
            "weather": dict,
            "saved": bool,
            "prediction_id": int
        }
    """
    # Check if ML model is loaded
    if predictor is None:
        return jsonify({"error": "ML model not loaded"}), 500

    # Validate input
    data = request.get_json()
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    is_valid, error = validate_predict_input(data)
    if not is_valid:
        return jsonify({"error": error}), 400

    user_id = int(data.get("user_id", 1))  # Default to user 1

    try:
        logger.info(f"Submitting data for user {user_id}, city: {data['city']}")

        # Fetch weather data
        weather = get_weather_for_farming(data["city"])
        logger.info(f"Weather: {weather['condition']}")

        # Convert weather to ML code
        weather_code = weather_to_code(weather)

        # Get ML prediction
        result = predictor.predict(
            nitrogen=float(data["nitrogen"]),
            phosphorus=float(data["phosphorus"]),
            potassium=float(data["potassium"]),
            leaf_color=int(data["leaf_color"]),
            weather=weather_code
        )

        # Store in database
        try:
            # Insert sensor data
            sensor_id = insert_sensor_data(
                user_id=user_id,
                soil_moisture=None,
                air_temperature=weather["temperature_celsius"],
                air_humidity=weather["humidity_percent"],
                sensor_id=f"api-{data['city']}"
            )
            logger.info(f"Sensor data saved (id: {sensor_id})")

            # Insert weather log
            weather_id = insert_weather_log(
                user_id=user_id,
                location=data["city"],
                temperature=weather["temperature_celsius"],
                humidity=weather["humidity_percent"],
                weather_condition=weather["condition"]
            )
            logger.info(f"Weather log saved (id: {weather_id})")

            # Insert prediction
            prediction_id = insert_prediction(
                user_id=user_id,
                sensor_data_id=sensor_id,
                weather_log_id=weather_id,
                predicted_yield=None,
                confidence_score=result["confidence"],
                recommendation=result["recommendation"],
                crop_type=None,
                model_version="1.0",
                prediction_type="fertilizer"
            )
            logger.info(f"Prediction saved (id: {prediction_id})")

            saved = True

        except Exception as db_error:
            logger.error(f"Database error: {db_error}", exc_info=True)
            saved = False
            prediction_id = None

        # Build response
        response = {
            "recommendation": result["recommendation"],
            "confidence": result["confidence"],
            "weather": {
                "city": weather["city"],
                "condition": weather["condition"],
                "rain_expected": weather["rain_expected"],
                "temperature_celsius": weather["temperature_celsius"],
                "humidity_percent": weather["humidity_percent"]
            },
            "saved": saved,
            "prediction_id": prediction_id
        }

        logger.info(f"Submit complete: {result['recommendation']}, saved: {saved}")
        return jsonify(response), 200

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Submit error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/history", methods=["GET"])
def history():
    """
    Fetch recent prediction history from database.

    Query Parameters:
        - user_id: Filter by user (optional, default: 1)
        - limit: Max records (optional, default: 50)
        - prediction_type: Filter by type (optional)

    Returns:
        List of prediction records with sensor and weather data
    """
    user_id = int(request.args.get("user_id", 1))
    limit = int(request.args.get("limit", 50))
    prediction_type = request.args.get("prediction_type")

    try:
        logger.info(f"Fetching history for user {user_id}")

        predictions = get_prediction_history(
            user_id=user_id,
            prediction_type=prediction_type,
            limit=limit
        )

        logger.info(f"Found {len(predictions)} records")
        return jsonify({
            "count": len(predictions),
            "predictions": predictions
        }), 200

    except Exception as e:
        logger.error(f"History error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": predictor is not None,
        "endpoints": ["/predict", "/submit-data", "/history", "/health"]
    }), 200


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() == "true"

    logger.info(f"Starting Smart Farming API on port {port}")
    logger.info(f"CORS enabled for: http://localhost:5173, http://127.0.0.1:5173")
    app.run(host="0.0.0.0", port=port, debug=debug)
