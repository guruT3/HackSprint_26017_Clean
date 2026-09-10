"""
train_models.py
-----------------
Trains Model A (yield prediction) and Model B (market price prediction)
on the synthetic dataset, evaluates them, and saves the fitted pipelines
(preprocessing + model together) as .pkl files.

Run:
    python ml/train_models.py

Requires:
    ml/data/agriculture_synthetic.csv  (run generate_dataset.py first)

Outputs:
    ml/models/yield_model.pkl
    ml/models/price_model.pkl
    ml/models/metrics.json
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from ml.preprocessing import build_preprocessor, ALL_FEATURES
except ImportError:
    # Allows running directly as `python ml/train_models.py` from project root
    from preprocessing import build_preprocessor, ALL_FEATURES

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "agriculture_synthetic.csv")
MODELS_DIR = os.path.join(BASE_DIR, "models")

RANDOM_STATE = 42


def evaluate(name, y_true, y_pred):
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    print(f"\n{name}")
    print(f"MAE:  {mae:.3f}")
    print(f"RMSE: {rmse:.3f}")
    print(f"R2:   {r2:.3f}")
    return {"mae": mae, "rmse": rmse, "r2": r2}


def train_yield_model(df):
    X = df[ALL_FEATURES]
    y = df["yield_per_acre"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", build_preprocessor()),
        ("model", RandomForestRegressor(
            n_estimators=300, max_depth=14, min_samples_leaf=3,
            random_state=RANDOM_STATE, n_jobs=-1
        )),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    metrics = evaluate("Yield Model (Random Forest)", y_test, preds)
    return pipeline, metrics


def train_price_model(df):
    X = df[ALL_FEATURES]
    y = df["expected_market_price"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )

    # MVP note: trained on synthetic data only. Structure supports swapping
    # in real historical mandi/market-price data later without changing the
    # rest of the pipeline (see forecast.py for the time-series extension).
    pipeline = Pipeline(steps=[
        ("preprocessor", build_preprocessor()),
        ("model", GradientBoostingRegressor(
            n_estimators=250, max_depth=4, learning_rate=0.05,
            random_state=RANDOM_STATE
        )),
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    metrics = evaluate("Price Model (Gradient Boosting) [MVP - synthetic data]", y_test, preds)
    return pipeline, metrics


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"{DATA_PATH} not found. Run `python ml/generate_dataset.py` first."
        )

    df = pd.read_csv(DATA_PATH)
    os.makedirs(MODELS_DIR, exist_ok=True)

    yield_pipeline, yield_metrics = train_yield_model(df)
    price_pipeline, price_metrics = train_price_model(df)

    joblib.dump(yield_pipeline, os.path.join(MODELS_DIR, "yield_model.pkl"))
    joblib.dump(price_pipeline, os.path.join(MODELS_DIR, "price_model.pkl"))

    metrics = {"yield_model": yield_metrics, "price_model": price_metrics}
    with open(os.path.join(MODELS_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("\nSaved models to:", MODELS_DIR)
    print("Saved evaluation metrics to metrics.json")


if __name__ == "__main__":
    main()
