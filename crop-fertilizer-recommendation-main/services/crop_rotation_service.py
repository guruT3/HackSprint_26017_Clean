"""
services/crop_rotation_service.py
-----------------------------------
Agronomic Crop Rotation & Multi-Factor Recommendation Engine.

Evaluates crop rotation options based on:
1. Soil suitability (30%)
2. Rotation benefit (25%) - e.g. Legume after Cereal, Root depth variation, pest/disease break
3. Water suitability (15%)
4. Season suitability (15%)
5. Weather suitability (10%)
6. Nutrient compatibility (5%)

Detects continuous cropping risks (e.g., Wheat -> Wheat -> Wheat).
Provides explainable scoring and transparent reasons.
"""

from typing import Dict, List, Any, Optional

# Validated agronomic crop profile dataset
CROP_DATABASE: Dict[str, Dict[str, Any]] = {
    "Chickpea": {
        "family": "Legume (Fabaceae)",
        "nitrogen_fixing": True,
        "nitrogen_demand": "Low",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "Moderate",
        "water_requirement": "Low",  # 1-5 scale: 2
        "water_scale": 2,
        "root_depth": "Deep",
        "ideal_ph_min": 6.0,
        "ideal_ph_max": 8.0,
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Loamy", "Alluvial", "Black", "Sandy"],
        "rotation_benefit_after": ["Wheat", "Rice", "Maize", "Cotton"],
        "disease_break_for": ["Poaceae"],
        "description": "Biological nitrogen fixation, deep root system, breaks continuous cereal pest cycles."
    },
    "Groundnut": {
        "family": "Legume (Fabaceae)",
        "nitrogen_fixing": True,
        "nitrogen_demand": "Low",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "Moderate",
        "water_requirement": "Low/Moderate",
        "water_scale": 2,
        "root_depth": "Medium",
        "ideal_ph_min": 5.5,
        "ideal_ph_max": 7.0,
        "suitable_seasons": ["Kharif", "Zaid"],
        "suitable_soils": ["Sandy", "Loamy", "Red", "Alluvial"],
        "rotation_benefit_after": ["Wheat", "Rice", "Maize"],
        "disease_break_for": ["Poaceae"],
        "description": "Leguminous crop enriching soil nitrogen while producing oilseed crop."
    },
    "Moong / Pulses": {
        "family": "Legume (Fabaceae)",
        "nitrogen_fixing": True,
        "nitrogen_demand": "Low",
        "phosphorus_demand": "Low",
        "potassium_demand": "Low",
        "water_requirement": "Low",
        "water_scale": 1,
        "root_depth": "Medium",
        "ideal_ph_min": 6.2,
        "ideal_ph_max": 7.5,
        "suitable_seasons": ["Zaid", "Kharif"],
        "suitable_soils": ["Loamy", "Alluvial", "Sandy", "Red"],
        "rotation_benefit_after": ["Wheat", "Rice", "Potato"],
        "disease_break_for": ["Poaceae", "Solanaceae"],
        "description": "Short duration pulse crop ideal for crop rotation between main seasons."
    },
    "Mustard": {
        "family": "Crucifer (Brassicaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "Moderate",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "Low",
        "water_requirement": "Low",
        "water_scale": 2,
        "root_depth": "Deep",
        "ideal_ph_min": 6.0,
        "ideal_ph_max": 7.5,
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Loamy", "Alluvial", "Sandy"],
        "rotation_benefit_after": ["Rice", "Cotton", "Maize"],
        "disease_break_for": ["Poaceae", "Legume"],
        "description": "Bio-fumigant effect in soil, low water requirement, deep taproot structure."
    },
    "Wheat": {
        "family": "Cereal (Poaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "High",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "Moderate",
        "water_requirement": "Moderate",
        "water_scale": 3,
        "root_depth": "Medium",
        "ideal_ph_min": 6.0,
        "ideal_ph_max": 7.5,
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Alluvial", "Loamy", "Black", "Clay"],
        "rotation_benefit_after": ["Chickpea", "Groundnut", "Soybean", "Moong / Pulses"],
        "disease_break_for": ["Fabaceae"],
        "description": "Staple rabi cereal crop that benefits greatly following leguminous nitrogen fixers."
    },
    "Maize": {
        "family": "Cereal (Poaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "High",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "High",
        "water_requirement": "Moderate",
        "water_scale": 3,
        "root_depth": "Medium",
        "ideal_ph_min": 5.8,
        "ideal_ph_max": 7.2,
        "suitable_seasons": ["Kharif", "Rabi", "Zaid"],
        "suitable_soils": ["Loamy", "Alluvial", "Red", "Black"],
        "rotation_benefit_after": ["Chickpea", "Groundnut", "Mustard"],
        "disease_break_for": ["Fabaceae"],
        "description": "Versatile cereal crop with moderate water demand."
    },
    "Rice": {
        "family": "Cereal (Poaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "High",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "High",
        "water_requirement": "High",
        "water_scale": 5,
        "root_depth": "Shallow",
        "ideal_ph_min": 5.5,
        "ideal_ph_max": 7.0,
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Alluvial", "Clay", "Loamy", "Black"],
        "rotation_benefit_after": ["Chickpea", "Groundnut", "Mustard"],
        "disease_break_for": ["Fabaceae"],
        "description": "High-water kharif cereal requiring adequate irrigation or rainfall."
    },
    "Cotton": {
        "family": "Fiber (Malvaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "High",
        "phosphorus_demand": "Moderate",
        "potassium_demand": "High",
        "water_requirement": "Moderate",
        "water_scale": 3,
        "root_depth": "Deep",
        "ideal_ph_min": 6.0,
        "ideal_ph_max": 8.0,
        "suitable_seasons": ["Kharif"],
        "suitable_soils": ["Black", "Alluvial", "Loamy"],
        "rotation_benefit_after": ["Wheat", "Chickpea", "Groundnut"],
        "disease_break_for": ["Poaceae"],
        "description": "Deep-rooted fiber commercial crop ideal for black and alluvial soils."
    },
    "Potato": {
        "family": "Tuber (Solanaceae)",
        "nitrogen_fixing": False,
        "nitrogen_demand": "High",
        "phosphorus_demand": "High",
        "potassium_demand": "High",
        "water_requirement": "Moderate",
        "water_scale": 3,
        "root_depth": "Shallow",
        "ideal_ph_min": 5.2,
        "ideal_ph_max": 6.5,
        "suitable_seasons": ["Rabi"],
        "suitable_soils": ["Loamy", "Sandy", "Alluvial"],
        "rotation_benefit_after": ["Rice", "Moong / Pulses", "Maize"],
        "disease_break_for": ["Poaceae"],
        "description": "High-value short duration tuber requiring loose, well-drained soil."
    }
}


def check_continuous_cropping(previous_crop: str, history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Check if the same crop or crop family has been grown repeatedly."""
    if not previous_crop:
        return {"detected": False, "message": ""}

    prev_clean = previous_crop.strip().capitalize()
    history_crops = []
    if history and isinstance(history, list):
        for item in history:
            if isinstance(item, dict) and item.get("crop"):
                history_crops.append(item["crop"].strip().capitalize())
            elif isinstance(item, str):
                history_crops.append(item.strip().capitalize())

    # Include previous crop in sequence
    full_sequence = history_crops + [prev_clean]

    repeat_count = 1
    for i in range(len(full_sequence) - 2, -1, -1):
        if full_sequence[i] == prev_clean:
            repeat_count += 1
        else:
            break

    if repeat_count >= 2:
        return {
            "detected": True,
            "crop": prev_clean,
            "repeat_count": repeat_count,
            "message": (
                f"⚠ Continuous cropping detected ({prev_clean} grown {repeat_count} times in sequence). "
                "Growing the same crop repeatedly depletes specific soil nutrients and increases "
                "pest and disease build-up. We strongly recommend rotating to a compatible secondary family."
            )
        }

    return {"detected": False, "message": ""}


def evaluate_crop_rotation(
    crop_name: str,
    previous_crop: str,
    soil_profile: Dict[str, Any],
    season: Optional[str] = None,
    irrigation: Optional[str] = None,
    weather: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Score a single candidate rotation crop (0-100) and generate explanations."""
    data = CROP_DATABASE.get(crop_name)
    if not data:
        return {"crop": crop_name, "score": 0, "reasons": []}

    prev_crop_clean = (previous_crop or "").strip().capitalize()
    prev_data = CROP_DATABASE.get(prev_crop_clean, {})

    reasons: List[str] = []
    warnings: List[str] = []

    # 1. Soil Suitability (30%)
    soil_score = 75  # Default baseline
    user_soil_type = (soil_profile.get("type") or soil_profile.get("soil_type") or "").strip().capitalize()
    user_ph = soil_profile.get("ph")

    if user_soil_type:
        if user_soil_type in data["suitable_soils"]:
            soil_score += 20
            reasons.append(f"[+] Well suited for {user_soil_type} soil conditions.")
        else:
            soil_score -= 15

    if user_ph is not None:
        ph_min = data["ideal_ph_min"]
        ph_max = data["ideal_ph_max"]
        if ph_min <= user_ph <= ph_max:
            soil_score += 15
            reasons.append(f"[+] Soil pH {user_ph} is within ideal range ({ph_min} - {ph_max}).")
        else:
            soil_score -= 20
            warnings.append(f"Soil pH {user_ph} is outside ideal range ({ph_min} - {ph_max}).")

    soil_score = max(0, min(100, soil_score))

    # 2. Rotation Benefit (25%)
    rotation_score = 60
    if prev_crop_clean:
        if crop_name == prev_crop_clean:
            rotation_score = 20
            warnings.append(f"Same crop as previous season ({prev_crop_clean}). High risk of pest buildup.")
        else:
            # Check family change
            prev_family = prev_data.get("family", "")
            curr_family = data["family"]
            if prev_family and curr_family and prev_family != curr_family:
                rotation_score += 25
                reasons.append(f"[+] Provides crop family diversification ({curr_family} after {prev_family}).")

            # Check Legume N-fixer benefit
            if data["nitrogen_fixing"] and not prev_data.get("nitrogen_fixing"):
                rotation_score += 25
                reasons.append("[+] Biological nitrogen fixation enriches soil fertility for future crops.")

            # Check root depth variation
            prev_root = prev_data.get("root_depth")
            curr_root = data["root_depth"]
            if prev_root and curr_root and prev_root != curr_root:
                rotation_score += 15
                reasons.append(f"[+] Root depth variation ({curr_root} root following {prev_root} root) improves soil structure.")

            if prev_crop_clean in data["rotation_benefit_after"]:
                rotation_score += 15
                reasons.append(f"[+] Proven agronomic rotation succession after {prev_crop_clean}.")

    rotation_score = max(0, min(100, rotation_score))

    # 3. Water Suitability (15%)
    water_score = 80
    irrigation_norm = (irrigation or "Yes").strip().capitalize()
    water_scale = data["water_scale"]

    if irrigation_norm in ["No", "None", "Rainfed"]:
        if water_scale <= 2:
            water_score = 95
            reasons.append("[+] Low water requirement matches rainfed/un-irrigated field condition.")
        elif water_scale >= 4:
            water_score = 30
            warnings.append("High water requirement crop is risky without reliable irrigation.")
    else:
        if water_scale >= 4:
            water_score = 90
            reasons.append("[+] Adequate irrigation supports high-yield water requirement.")
        else:
            water_score = 85
            reasons.append("[+] Water requirement matches irrigation availability.")

    water_score = max(0, min(100, water_score))

    # 4. Season Suitability (15%)
    season_score = 70
    season_norm = (season or "").strip().capitalize()
    if season_norm:
        if season_norm in data["suitable_seasons"]:
            season_score = 95
            reasons.append(f"[+] Optimal growing window for {season_norm} season.")
        else:
            season_score = 40
            warnings.append(f"Sub-optimal season placement for {season_norm}.")

    # 5. Weather Suitability (10%)
    weather_score = 75
    if weather and isinstance(weather, dict):
        temp = weather.get("temperature")
        if temp is not None:
            if 15 <= temp <= 35:
                weather_score += 15
                reasons.append(f"[+] Temperature conditions ({temp}°C) favor crop growth.")

    weather_score = max(0, min(100, weather_score))

    # 6. Nutrient Compatibility (5%)
    nutrient_score = 75
    soil_n = soil_profile.get("nitrogen")
    if soil_n is not None:
        if soil_n < 30 and data["nitrogen_fixing"]:
            nutrient_score = 95
            reasons.append("[+] Low soil nitrogen level ideal for legume N-fixer placement.")


    nutrient_score = max(0, min(100, nutrient_score))

    # Calculate overall weighted score
    overall_score = round(
        0.30 * soil_score +
        0.25 * rotation_score +
        0.15 * water_score +
        0.15 * season_score +
        0.10 * weather_score +
        0.05 * nutrient_score
    )

    return {
        "crop": crop_name,
        "family": data["family"],
        "overall_score": overall_score,
        "scores": {
            "soil_suitability": round(soil_score),
            "rotation_benefit": round(rotation_score),
            "water_suitability": round(water_score),
            "season_suitability": round(season_score),
            "weather_suitability": round(weather_score),
            "nutrient_compatibility": round(nutrient_score),
        },
        "reasons": reasons,
        "warnings": warnings,
        "description": data["description"],
    }


def recommend_next_crop(
    previous_crop: str,
    soil_profile: Dict[str, Any],
    season: Optional[str] = None,
    irrigation: Optional[str] = None,
    weather: Optional[Dict[str, Any]] = None,
    history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Master function: Evaluate candidate rotation crops, rank by score,
    detect continuous cropping, and return structured recommendations.
    """
    continuous_check = check_continuous_cropping(previous_crop, history)

    results = []
    for crop_name in CROP_DATABASE:
        res = evaluate_crop_rotation(
            crop_name=crop_name,
            previous_crop=previous_crop,
            soil_profile=soil_profile,
            season=season,
            irrigation=irrigation,
            weather=weather,
            history=history
        )
        results.append(res)

    # Sort descending by overall_score
    results.sort(key=lambda x: x["overall_score"], reverse=True)

    best = results[0] if results else None

    return {
        "success": True,
        "previous_crop": previous_crop,
        "continuous_cropping_warning": continuous_check,
        "recommended_crop": best["crop"] if best else None,
        "top_score": best["overall_score"] if best else 0,
        "recommendations": results[:4],  # Top 4 choices
        "all_options": results
    }
