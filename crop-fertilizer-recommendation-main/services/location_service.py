"""Location and soil lookup helpers for the smart farm prediction page."""

import requests


class LocationValidationError(ValueError):
    """Raised when a client sends invalid farm coordinates."""


def _number(value, field_name):
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise LocationValidationError(f"{field_name} must be a number.") from exc

    if number != number or number in (float("inf"), float("-inf")):
        raise LocationValidationError(f"{field_name} must be finite.")
    return number


def validate_coordinates(latitude, longitude, accuracy=None):
    """Validate GPS values received from the browser."""
    latitude = _number(latitude, "Latitude")
    longitude = _number(longitude, "Longitude")

    if not -90 <= latitude <= 90:
        raise LocationValidationError("Latitude must be between -90 and 90.")
    if not -180 <= longitude <= 180:
        raise LocationValidationError("Longitude must be between -180 and 180.")

    if accuracy is not None:
        accuracy = _number(accuracy, "Accuracy")
        if accuracy <= 0:
            raise LocationValidationError("Accuracy must be positive.")

    return latitude, longitude, accuracy


def reverse_geocode(latitude, longitude):
    """Return an approximate address using public Nominatim, when available."""
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": latitude,
                "lon": longitude,
                "format": "jsonv2",
                "zoom": 10,
            },
            headers={"User-Agent": "AgriMitra/1.0 farm-location"},
            timeout=5,
        )
        response.raise_for_status()
        address = response.json().get("address", {})
        return {
            "village": address.get("village") or address.get("town") or address.get("city"),
            "district": address.get("county") or address.get("state_district"),
            "state": address.get("state"),
            "country": address.get("country"),
        }
    except (requests.RequestException, ValueError, TypeError):
        return {}


def _soil_test_value(soil_test, key, minimum=0, maximum=None):
    value = soil_test.get(key) if isinstance(soil_test, dict) else None
    if value in (None, ""):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if value < minimum or (maximum is not None and value > maximum):
        return None
    return value


def _soilgrids_value(payload, layer_name):
    for layer in payload.get("properties", {}).get("layers", []):
        if layer.get("name") != layer_name:
            continue
        depths = layer.get("depths", [])
        if not depths:
            return None
        return depths[0].get("values", {}).get("mean")
    return None


def get_regional_soil_information(latitude, longitude):
    """Fetch shallow regional soil estimates from the public SoilGrids API."""
    try:
        response = requests.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params=[
                ("lon", longitude),
                ("lat", latitude),
                ("property", "phh2o"),
                ("property", "nitrogen"),
                ("property", "soc"),
                ("property", "clay"),
                ("property", "sand"),
                ("property", "silt"),
                ("depth", "0-5cm"),
                ("value", "mean"),
            ],
            headers={"User-Agent": "AgriMitra/1.0 soil-intelligence"},
            timeout=4,
        )
        response.raise_for_status()
        payload = response.json()
        ph = _soilgrids_value(payload, "phh2o")
        nitrogen = _soilgrids_value(payload, "nitrogen")
        organic_carbon = _soilgrids_value(payload, "soc")
        clay = _soilgrids_value(payload, "clay")
        sand = _soilgrids_value(payload, "sand")
        silt = _soilgrids_value(payload, "silt")
        available = any(value is not None for value in (ph, nitrogen, organic_carbon, clay, sand, silt))
        if not available:
            return None
        texture = None
        if clay is not None and sand is not None and silt is not None:
            texture = f"Clay {clay / 10:.1f}%, Sand {sand / 10:.1f}%, Silt {silt / 10:.1f}%"
        return {
            "type": None,
            "texture": texture,
            "ph": round(ph / 10, 2) if ph is not None else None,
            "nitrogen": round(nitrogen / 100, 2) if nitrogen is not None else None,
            "phosphorus": None,
            "potassium": None,
            "organic_carbon": round(organic_carbon / 10, 2) if organic_carbon is not None else None,
            "ec": None,
            "source": "SoilGrids regional dataset (0-5 cm estimate)",
            "confidence": "medium",
            "available": True,
        }
    except (requests.RequestException, ValueError, TypeError, KeyError):
        return None


from services.soil_service import get_soil_information, get_regional_soil_information


def process_farm_location(latitude, longitude, accuracy=None, soil_test=None, iot_data=None):
    """Validate coordinates and collect best-effort address and soil data."""
    latitude, longitude, accuracy = validate_coordinates(latitude, longitude, accuracy)
    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
        },
        "address": reverse_geocode(latitude, longitude),
        "soil": get_soil_information(latitude, longitude, soil_test, iot_data),
    }

