"""
services/soil_service.py
-------------------------
Modular Soil Intelligence Service.

Data Priority:
1. Laboratory Soil Test (Farmer entered)
2. IoT Sensor Data
3. Local Verified Dataset
4. Regional Soil Dataset (ISRIC SoilGrids)

Does NOT invent soil data if unavailable.
"""

import requests
from typing import Dict, Any, Optional


def _parse_numeric(val: Any, min_val: float = 0, max_val: Optional[float] = None) -> Optional[float]:
    if val in (None, ""):
        return None
    try:
        num = float(val)
        if num != num or num in (float("inf"), float("-inf")):
            return None
        if num < min_val:
            return None
        if max_val is not None and num > max_val:
            return None
        return num
    except (TypeError, ValueError):
        return None


def get_regional_soil_information(latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
    """Fetch regional soil estimates from public ISRIC SoilGrids API."""
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
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()

        def _get_layer_val(layer_name):
            for layer in payload.get("properties", {}).get("layers", []):
                if layer.get("name") == layer_name:
                    depths = layer.get("depths", [])
                    if depths:
                        return depths[0].get("values", {}).get("mean")
            return None

        ph_raw = _get_layer_val("phh2o")
        n_raw = _get_layer_val("nitrogen")
        soc_raw = _get_layer_val("soc")
        clay_raw = _get_layer_val("clay")
        sand_raw = _get_layer_val("sand")
        silt_raw = _get_layer_val("silt")

        has_data = any(v is not None for v in (ph_raw, n_raw, soc_raw, clay_raw, sand_raw, silt_raw))
        if not has_data:
            return None

        texture = None
        soil_type = None
        if clay_raw is not None and sand_raw is not None and silt_raw is not None:
            c = clay_raw / 10.0
            s = sand_raw / 10.0
            si = silt_raw / 10.0
            texture = f"Clay {c:.1f}%, Sand {s:.1f}%, Silt {si:.1f}%"

            # Basic USDA texture triangle heuristic for soil_type display
            if c >= 40:
                soil_type = "Clay"
            elif s >= 50:
                soil_type = "Sandy"
            elif si >= 50:
                soil_type = "Silt"
            else:
                soil_type = "Loamy"

        return {
            "type": soil_type,
            "texture": texture,
            "ph": round(ph_raw / 10.0, 2) if ph_raw is not None else None,
            "nitrogen": round(n_raw / 100.0, 2) if n_raw is not None else None,
            "phosphorus": None,
            "potassium": None,
            "organic_carbon": round(soc_raw / 10.0, 2) if soc_raw is not None else None,
            "ec": None,
            "source": "Regional Soil Dataset (SoilGrids 250m)",
            "confidence": "Medium",
            "available": True,
            "is_estimate": True,
            "notice": "This is a regional estimate. For field-level accuracy, use a laboratory soil test."
        }
    except Exception:
        return None


def get_soil_information(
    latitude: float,
    longitude: float,
    soil_test: Optional[Dict[str, Any]] = None,
    iot_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Retrieve soil profile based on hierarchy of data sources:
    1. Laboratory Soil Test (Farmer entered)
    2. IoT Sensor Data
    3. Regional Soil Dataset
    """
    # Priority 1: Laboratory Soil Test
    if soil_test and isinstance(soil_test, dict):
        parsed_test = {
            "ph": _parse_numeric(soil_test.get("ph"), 0, 14),
            "nitrogen": _parse_numeric(soil_test.get("nitrogen")),
            "phosphorus": _parse_numeric(soil_test.get("phosphorus")),
            "potassium": _parse_numeric(soil_test.get("potassium")),
            "organic_carbon": _parse_numeric(soil_test.get("organic_carbon")),
            "ec": _parse_numeric(soil_test.get("ec")),
            "soil_type": soil_test.get("soil_type") or soil_test.get("type"),
            "texture": soil_test.get("texture"),
        }
        if any(v is not None for v in parsed_test.values()):
            return {
                "type": parsed_test["soil_type"] or "Custom Field Test",
                "texture": parsed_test["texture"] or "Tested Sample",
                "ph": parsed_test["ph"],
                "nitrogen": parsed_test["nitrogen"],
                "phosphorus": parsed_test["phosphorus"],
                "potassium": parsed_test["potassium"],
                "organic_carbon": parsed_test["organic_carbon"],
                "ec": parsed_test["ec"],
                "source": "Farmer Soil Test (Laboratory)",
                "confidence": "High",
                "available": True,
                "is_estimate": False,
                "notice": "Verified field test values applied."
            }

    # Priority 2: IoT Sensor Data
    if iot_data and isinstance(iot_data, dict):
        parsed_iot = {
            "ph": _parse_numeric(iot_data.get("ph"), 0, 14),
            "nitrogen": _parse_numeric(iot_data.get("nitrogen")),
            "phosphorus": _parse_numeric(iot_data.get("phosphorus")),
            "potassium": _parse_numeric(iot_data.get("potassium")),
            "organic_carbon": _parse_numeric(iot_data.get("organic_carbon")),
            "ec": _parse_numeric(iot_data.get("ec")),
        }
        if any(v is not None for v in parsed_iot.values()):
            return {
                "type": iot_data.get("type") or "Sensor Field",
                "texture": iot_data.get("texture") or "Real-time Telemetry",
                "ph": parsed_iot["ph"],
                "nitrogen": parsed_iot["nitrogen"],
                "phosphorus": parsed_iot["phosphorus"],
                "potassium": parsed_iot["potassium"],
                "organic_carbon": parsed_iot["organic_carbon"],
                "ec": parsed_iot["ec"],
                "source": "IoT Sensor Data",
                "confidence": "High",
                "available": True,
                "is_estimate": False,
                "notice": "Real-time sensor measurement."
            }

    # Priority 3: Regional Geospatial Soil Dataset
    regional_info = get_regional_soil_information(latitude, longitude)
    if regional_info:
        return regional_info

    # Default fallback: Information Unavailable
    return {
        "type": None,
        "texture": None,
        "ph": None,
        "nitrogen": None,
        "phosphorus": None,
        "potassium": None,
        "organic_carbon": None,
        "ec": None,
        "source": "Unavailable",
        "confidence": "Low",
        "available": False,
        "is_estimate": True,
        "notice": "Soil information is currently unavailable for these coordinates. Please enter laboratory soil test values."
    }
