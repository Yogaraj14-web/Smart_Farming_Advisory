# src/api/routes.py
"""Flask route definitions."""
from flask import Blueprint, jsonify, request
from src.models.crop_advisor import CropAdvisor

advisory_bp = Blueprint("advisory", __name__)
advisor = CropAdvisor()


@advisory_bp.route("/predict", methods=["POST"])
def predict_yield():
    """Predict crop yield based on farm parameters."""
    data = request.get_json()
    # TODO: Validate input with Pydantic schema
    prediction = advisor.predict_yield(data)
    return jsonify(prediction)


@advisory_bp.route("/advisory", methods=["POST"])
def get_advisory():
    """Get farming advisory recommendations."""
    data = request.get_json()
    advisory = advisor.generate_advisory(data)
    return jsonify(advisory)


@advisory_bp.route("/weather/<location>", methods=["GET"])
def get_weather(location):
    """Get current weather for a location."""
    weather = advisor.get_weather(location)
    return jsonify(weather)
