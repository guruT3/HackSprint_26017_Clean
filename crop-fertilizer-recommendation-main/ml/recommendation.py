"""
recommendation.py
-------------------
Crop recommendation + comparison + risk scoring.

For a given farm's conditions, this module runs the trained yield & price
models for a set of candidate crops, computes profitability for each
(using profitability.py), estimates a risk score, and combines everything
into a single weighted score to recommend the top crops.

final_score =
    0.40 * profitability_score +
    0.25 * yield_score +
    0.20 * crop_suitability_score +
    0.15 * risk_score(inverted, higher = safer)

All component scores are normalized to 0-1 before combining.
"""

import numpy as np
import pandas as pd

from ml.profitability import compute_profitability, safe_div
from ml.generate_dataset import CROP_PROFILE, SOIL_SUITABILITY, SEASON_SUITABILITY, gaussian_suitability

CANDIDATE_CROPS = list(CROP_PROFILE.keys())


def _crop_suitability_score(crop, soil_type, season, rainfall, temperature, soil_ph):
    """0-1 score describing how agronomically suitable a crop is for the
    given field conditions, independent of cost/price."""
    profile = CROP_PROFILE[crop]
    rain_suit = gaussian_suitability(rainfall, profile["ideal_rain"], profile["rain_tol"])
    temp_suit = gaussian_suitability(temperature, profile["ideal_temp"], profile["temp_tol"])
    ph_suit = gaussian_suitability(soil_ph, profile["ideal_ph"], profile["ph_tol"])
    soil_suit = SOIL_SUITABILITY[crop].get(soil_type, 0.5)
    season_suit = SEASON_SUITABILITY[crop].get(season, 0.5)

    return float(0.30 * rain_suit + 0.25 * temp_suit + 0.15 * ph_suit +
                 0.20 * soil_suit + 0.10 * season_suit)


def estimate_risk(
    crop,
    suitability_score,
    expected_market_price,
    total_cost,
    farm_area,
    irrigation,
):
    """Returns (risk_label, risk_score_0_100). Higher risk_score = riskier.

    This is a simple, explainable heuristic combining:
      - agronomic suitability (poor suitability -> yield uncertainty)
      - market price volatility assumption per crop type (illustrative)
      - cost level relative to farm size (higher cost = higher exposure)
      - irrigation availability (No irrigation = higher weather dependency)
    It is NOT a statistical/financial risk model - it is indicative only.
    """
    # Crop-level illustrative price-volatility assumption (0-1, higher = more volatile)
    PRICE_VOLATILITY = {
        "Rice": 0.25, "Wheat": 0.2, "Maize": 0.3, "Cotton": 0.5,
        "Tomato": 0.7, "Potato": 0.6, "Sugarcane": 0.2, "Groundnut": 0.4,
    }
    price_risk = PRICE_VOLATILITY.get(crop, 0.4)

    yield_uncertainty = 1 - suitability_score  # poor fit -> more uncertain yield
    weather_dependency = 0.3 if irrigation == "Yes" else 0.65

    cost_per_acre = safe_div(total_cost, farm_area)
    # Normalize cost exposure against a rough reference of Rs. 25,000/acre
    cost_exposure = float(np.clip(cost_per_acre / 25000.0, 0, 1.5)) / 1.5

    risk_score_0_1 = (
        0.35 * yield_uncertainty +
        0.30 * price_risk +
        0.20 * weather_dependency +
        0.15 * cost_exposure
    )
    risk_score_0_100 = round(float(np.clip(risk_score_0_1 * 100, 0, 100)), 1)

    if risk_score_0_100 < 35:
        label = "Low"
    elif risk_score_0_100 < 65:
        label = "Medium"
    else:
        label = "High"

    return label, risk_score_0_100


def _normalize(values):
    """Min-max normalize a list of numbers to 0-1. Handles flat/degenerate cases."""
    arr = np.array(values, dtype=float)
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return [0.5 for _ in values]
    return list((arr - lo) / (hi - lo))


def evaluate_crop(
    crop,
    yield_model,
    price_model,
    farm_input: dict,
):
    """Runs both models for a single candidate crop and returns yield,
    price, profitability, suitability and risk for it."""
    row = dict(farm_input)
    row["crop"] = crop
    df_row = pd.DataFrame([row])

    predicted_yield = float(yield_model.predict(df_row)[0])
    predicted_price = float(price_model.predict(df_row)[0])

    per_acre_costs = {
        "seed_cost": farm_input.get("seed_cost", 0),
        "fertilizer_cost": farm_input.get("fertilizer_cost", 0),
        "pesticide_cost": farm_input.get("pesticide_cost", 0),
        "labour_cost": farm_input.get("labour_cost", 0),
        "irrigation_cost": farm_input.get("irrigation_cost", 0),
        "machinery_cost": farm_input.get("machinery_cost", 0),
        "other_cost": farm_input.get("other_cost", 0),
    }

    profitability = compute_profitability(
        predicted_yield_per_acre=predicted_yield,
        farm_area=farm_input.get("farm_area", 1),
        expected_market_price=predicted_price,
        per_acre_costs=per_acre_costs,
    )

    suitability = _crop_suitability_score(
        crop, farm_input.get("soil_type"), farm_input.get("season"),
        farm_input.get("rainfall"), farm_input.get("temperature"),
        farm_input.get("soil_ph"),
    )

    risk_label, risk_score = estimate_risk(
        crop, suitability, predicted_price, profitability["total_cost"],
        farm_input.get("farm_area", 1), farm_input.get("irrigation"),
    )

    return {
        "crop": crop,
        "suitability_score": round(suitability, 3),
        "risk_label": risk_label,
        "risk_score": risk_score,
        **profitability,
    }


def compare_crops(yield_model, price_model, farm_input: dict, crops=None):
    """Evaluates a list of crops (default: all candidate crops) for the given
    farm conditions and returns a list of result dicts, each carrying a
    combined final_score, sorted by profit descending."""
    crops = crops or CANDIDATE_CROPS
    results = [evaluate_crop(c, yield_model, price_model, farm_input) for c in crops]

    # Normalize component scores across the candidate set (0-1)
    profits = [r["profit"] for r in results]
    yields = [r["predicted_yield_per_acre"] for r in results]
    suitabilities = [r["suitability_score"] for r in results]
    risks = [r["risk_score"] for r in results]  # higher = riskier

    profit_scores = _normalize(profits)
    yield_scores = _normalize(yields)
    suitability_scores = _normalize(suitabilities)
    risk_scores_inverted = [1 - s for s in _normalize(risks)]  # higher = safer

    for r, p_s, y_s, su_s, ri_s in zip(results, profit_scores, yield_scores, suitability_scores, risk_scores_inverted):
        r["final_score"] = round(
            0.40 * p_s + 0.25 * y_s + 0.20 * su_s + 0.15 * ri_s, 4
        )

    results.sort(key=lambda r: r["profit"], reverse=True)
    return results


def top_recommendations(results, n=3):
    """Returns top-n crops sorted by combined final_score (not profit alone)."""
    ranked = sorted(results, key=lambda r: r["final_score"], reverse=True)
    return ranked[:n]


def recommendation_reasons(result: dict) -> list:
    """Generates short bullet-point reasons for why a crop was recommended."""
    reasons = []
    if result["suitability_score"] >= 0.7:
        reasons.append("Suitable soil and climate conditions for this crop")
    elif result["suitability_score"] >= 0.5:
        reasons.append("Reasonably suitable soil and climate conditions")

    if result["predicted_yield_per_acre"] > 0:
        reasons.append("Good expected yield based on entered farm conditions")

    if result["roi_percent"] > 20:
        reasons.append("Favorable expected return on cultivation cost")

    if result["risk_label"] == "Low":
        reasons.append("Lower estimated risk compared to alternatives")

    if not reasons:
        reasons.append("Best overall balance of profit, yield, suitability and risk among compared crops")

    return reasons[:4]
