# src/utils/validators.py
"""Input validation utilities."""
import re
from typing import Optional


def validate_location(location: str) -> bool:
    """Validate location string."""
    return bool(re.match(r"^[a-zA-Z\s,-]+$", location))


def validate_area(area: float) -> bool:
    """Validate farm area (positive number)."""
    return area > 0


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection."""
    return re.sub(r"[<>\"'&]", "", text.strip())


def validate_coordinates(lat: float, lon: float) -> Optional[str]:
    """Validate latitude/longitude coordinates."""
    if not (-90 <= lat <= 90):
        return "Invalid latitude"
    if not (-180 <= lon <= 180):
        return "Invalid longitude"
    return None
