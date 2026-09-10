"""
generate_dataset.py
--------------------
Generates a synthetic agricultural dataset for the Crop Planning,
Profitability & Forecasting MVP module.

Why synthetic data?
We don't have real historical farm/market data yet. Instead of hand-coding
formulas and calling it "ML", we build a data-generating process that encodes
realistic agronomic relationships (rainfall/temperature/soil suitability,
cost structure, crop-specific yield ranges, etc.) with random noise. Then we
train real regression models (Random Forest / Gradient Boosting) on this
data. This gives us an actual learned model whose behavior can later be
recalibrated with real data, instead of a disguised calculator.

Run:
    python ml/generate_dataset.py

Output:
    ml/data/agriculture_synthetic.csv
"""

import numpy as np
import pandas as pd
import os

# Fixed seed -> reproducible dataset
SEED = 42
rng = np.random.default_rng(SEED)

N_RECORDS = 12000

# ---------------------------------------------------------------------------
# 1. Reference tables: crop-specific "ideal" agronomic conditions & baselines
# ---------------------------------------------------------------------------
# These numbers are approximate, illustrative agronomic ranges (not sourced
# from a specific dataset) used purely to make the synthetic data internally
# consistent. They should be replaced with real regional agronomy data later.

CROPS = ["Rice", "Wheat", "Maize", "Cotton", "Tomato", "Potato", "Sugarcane", "Groundnut"]

CROP_PROFILE = {
    # crop: (base_yield_per_acre(quintals), yield_std, ideal_rainfall_mm,
    #        rainfall_tolerance, ideal_temp_c, temp_tolerance,
    #        ideal_ph, ph_tolerance, water_need(1-5), base_price_per_quintal(INR))
    "Rice":      dict(base_yield=22, yield_std=4, ideal_rain=1200, rain_tol=400, ideal_temp=27, temp_tol=5, ideal_ph=6.2, ph_tol=0.8, water_need=5, base_price=2100),
    "Wheat":     dict(base_yield=18, yield_std=3, ideal_rain=600,  rain_tol=250, ideal_temp=20, temp_tol=5, ideal_ph=6.8, ph_tol=0.8, water_need=3, base_price=2300),
    "Maize":     dict(base_yield=25, yield_std=5, ideal_rain=750,  rain_tol=300, ideal_temp=25, temp_tol=6, ideal_ph=6.0, ph_tol=0.9, water_need=3, base_price=1900),
    "Cotton":    dict(base_yield=8,  yield_std=2, ideal_rain=700,  rain_tol=300, ideal_temp=28, temp_tol=5, ideal_ph=7.0, ph_tol=1.0, water_need=3, base_price=6500),
    "Tomato":    dict(base_yield=90, yield_std=18,ideal_rain=550,  rain_tol=250, ideal_temp=23, temp_tol=5, ideal_ph=6.3, ph_tol=0.7, water_need=4, base_price=1400),
    "Potato":    dict(base_yield=80, yield_std=15,ideal_rain=500,  rain_tol=200, ideal_temp=18, temp_tol=5, ideal_ph=5.5, ph_tol=0.7, water_need=4, base_price=1200),
    "Sugarcane": dict(base_yield=350,yield_std=60,ideal_rain=1500, rain_tol=500, ideal_temp=27, temp_tol=5, ideal_ph=6.5, ph_tol=0.8, water_need=5, base_price=340),
    "Groundnut": dict(base_yield=12, yield_std=3, ideal_rain=600,  rain_tol=250, ideal_temp=26, temp_tol=5, ideal_ph=6.2, ph_tol=0.8, water_need=2, base_price=5800),
}

SOIL_TYPES = ["Alluvial", "Black", "Red", "Laterite", "Sandy", "Clay", "Loamy"]

# How well each soil type generally suits each crop (0-1 multiplier on yield)
SOIL_SUITABILITY = {
    "Rice":      {"Alluvial": 1.0, "Clay": 0.95, "Black": 0.75, "Loamy": 0.85, "Red": 0.55, "Laterite": 0.5, "Sandy": 0.35},
    "Wheat":     {"Alluvial": 1.0, "Loamy": 0.9, "Black": 0.8, "Clay": 0.7, "Red": 0.6, "Sandy": 0.5, "Laterite": 0.45},
    "Maize":     {"Loamy": 1.0, "Alluvial": 0.9, "Red": 0.75, "Black": 0.7, "Sandy": 0.6, "Clay": 0.55, "Laterite": 0.5},
    "Cotton":    {"Black": 1.0, "Alluvial": 0.75, "Red": 0.65, "Loamy": 0.7, "Clay": 0.55, "Sandy": 0.45, "Laterite": 0.4},
    "Tomato":    {"Loamy": 1.0, "Alluvial": 0.9, "Red": 0.75, "Sandy": 0.65, "Black": 0.6, "Clay": 0.5, "Laterite": 0.5},
    "Potato":    {"Loamy": 1.0, "Sandy": 0.85, "Alluvial": 0.8, "Red": 0.6, "Black": 0.55, "Clay": 0.45, "Laterite": 0.45},
    "Sugarcane": {"Alluvial": 1.0, "Black": 0.85, "Loamy": 0.8, "Clay": 0.65, "Red": 0.55, "Sandy": 0.4, "Laterite": 0.4},
    "Groundnut": {"Sandy": 1.0, "Red": 0.85, "Loamy": 0.8, "Black": 0.6, "Alluvial": 0.65, "Clay": 0.45, "Laterite": 0.5},
}

SEASONS = ["Kharif", "Rabi", "Zaid"]
# Season suitability multiplier per crop (rough, illustrative)
SEASON_SUITABILITY = {
    "Rice":      {"Kharif": 1.0, "Rabi": 0.6, "Zaid": 0.5},
    "Wheat":     {"Kharif": 0.4, "Rabi": 1.0, "Zaid": 0.3},
    "Maize":     {"Kharif": 1.0, "Rabi": 0.8, "Zaid": 0.7},
    "Cotton":    {"Kharif": 1.0, "Rabi": 0.5, "Zaid": 0.4},
    "Tomato":    {"Kharif": 0.8, "Rabi": 1.0, "Zaid": 0.7},
    "Potato":    {"Kharif": 0.5, "Rabi": 1.0, "Zaid": 0.4},
    "Sugarcane": {"Kharif": 0.9, "Rabi": 0.7, "Zaid": 1.0},
    "Groundnut": {"Kharif": 1.0, "Rabi": 0.7, "Zaid": 0.8},
}

REGIONS = ["North", "South", "East", "West", "Central", "North-East"]


def gaussian_suitability(value, ideal, tolerance):
    """Returns a 0-1 score peaking at 1.0 when value == ideal, decaying with distance.
    Extreme deviations (too high or too low) are penalized -> models the fact that
    both drought and flooding, or too-hot/too-cold, reduce yield."""
    z = (value - ideal) / tolerance
    return float(np.exp(-0.5 * z ** 2))


def generate_row(i):
    crop = rng.choice(CROPS)
    profile = CROP_PROFILE[crop]
    soil = rng.choice(SOIL_TYPES)
    season = rng.choice(SEASONS)
    region = rng.choice(REGIONS)
    irrigation = rng.choice(["Yes", "No"], p=[0.65, 0.35])

    farm_area = float(np.round(rng.uniform(0.5, 20), 2))  # acres

    # Environmental factors, centered loosely around each crop's ideal with noise
    rainfall = max(50, rng.normal(profile["ideal_rain"], profile["rain_tol"] * 0.9))
    temperature = float(np.clip(rng.normal(profile["ideal_temp"], profile["temp_tol"]), 5, 45))
    soil_ph = float(np.clip(rng.normal(profile["ideal_ph"], profile["ph_tol"]), 4.0, 9.0))
    soil_moisture = float(np.clip(rng.normal(45 if irrigation == "Yes" else 30, 12), 5, 95))  # percent

    # Suitability scores
    rain_suit = gaussian_suitability(rainfall, profile["ideal_rain"], profile["rain_tol"])
    temp_suit = gaussian_suitability(temperature, profile["ideal_temp"], profile["temp_tol"])
    ph_suit = gaussian_suitability(soil_ph, profile["ideal_ph"], profile["ph_tol"])
    soil_suit = SOIL_SUITABILITY[crop].get(soil, 0.5)
    season_suit = SEASON_SUITABILITY[crop].get(season, 0.5)

    # Irrigation stabilizes yield, especially for water-hungry crops, and
    # partially compensates for rainfall shortfall
    irrigation_boost = 1.0
    if irrigation == "Yes":
        irrigation_boost = 1.0 + 0.03 * profile["water_need"]
        rain_suit = min(1.0, rain_suit + 0.15)
    else:
        irrigation_boost = 1.0 - 0.02 * profile["water_need"]

    # Farming experience improves yield slightly (better agronomic practice)
    farming_experience = int(np.clip(rng.normal(8, 6), 0, 40))
    experience_boost = 1.0 + min(0.15, farming_experience * 0.005)

    # Previous yield (used as an input feature; correlated with true potential)
    previous_yield = max(0.5, profile["base_yield"] * rng.uniform(0.6, 1.0) + rng.normal(0, profile["yield_std"] * 0.3))

    # Combine suitability multipliers (weighted) into an overall suitability factor
    overall_suit = (0.30 * rain_suit + 0.25 * temp_suit + 0.15 * ph_suit +
                     0.20 * soil_suit + 0.10 * season_suit)

    noise = rng.normal(1.0, 0.08)  # +/- random field variation
    yield_per_acre = max(0.2, profile["base_yield"] * overall_suit * irrigation_boost *
                          experience_boost * noise)

    # --- Costs (INR per acre-equivalent scale, scaled by farm area later) ---
    seed_cost = max(200, rng.normal(2500 if crop in ("Sugarcane",) else 1500, 400))
    fertilizer_cost = max(300, rng.normal(3500, 700))
    pesticide_cost = max(100, rng.normal(1800, 500))
    labour_cost = max(500, rng.normal(4500, 900))
    irrigation_cost = max(0, rng.normal(2500 if irrigation == "Yes" else 500, 500))
    machinery_cost = max(200, rng.normal(2000, 600))
    other_cost = max(100, rng.normal(1000, 300))

    # --- Market price: base price with regional/seasonal/random variation ---
    expected_market_price = max(50, profile["base_price"] * rng.uniform(0.85, 1.2) +
                                 rng.normal(0, profile["base_price"] * 0.05))

    return dict(
        crop=crop,
        farm_area=farm_area,
        soil_type=soil,
        irrigation=irrigation,
        season=season,
        region=region,
        rainfall=round(rainfall, 1),
        temperature=round(temperature, 1),
        soil_ph=round(soil_ph, 2),
        soil_moisture=round(soil_moisture, 1),
        seed_cost=round(seed_cost, 2),
        fertilizer_cost=round(fertilizer_cost, 2),
        pesticide_cost=round(pesticide_cost, 2),
        labour_cost=round(labour_cost, 2),
        irrigation_cost=round(irrigation_cost, 2),
        machinery_cost=round(machinery_cost, 2),
        other_cost=round(other_cost, 2),
        previous_yield=round(previous_yield, 2),
        farming_experience=farming_experience,
        yield_per_acre=round(yield_per_acre, 2),
        expected_market_price=round(expected_market_price, 2),
    )


def build_dataset(n=N_RECORDS):
    rows = [generate_row(i) for i in range(n)]
    df = pd.DataFrame(rows)

    # Derived financial columns (per-acre costs scaled by farm area for totals)
    per_acre_cost_cols = ["seed_cost", "fertilizer_cost", "pesticide_cost",
                           "labour_cost", "irrigation_cost", "machinery_cost", "other_cost"]
    df["total_cost"] = df[per_acre_cost_cols].sum(axis=1) * df["farm_area"]
    df["total_yield"] = df["yield_per_acre"] * df["farm_area"]
    df["revenue"] = df["total_yield"] * df["expected_market_price"]
    df["profit"] = df["revenue"] - df["total_cost"]
    df["profit_per_acre"] = df["profit"] / df["farm_area"]

    return df


if __name__ == "__main__":
    df = build_dataset()
    out_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "agriculture_synthetic.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} synthetic records -> {out_path}")
    print(df.describe(include="all").T[["count", "mean"]] if False else df.head())
