"""
forecast.py
------------
Basic time-series forecasting for price or yield, given a short history the
farmer enters (e.g. last 3-6 years of price or yield values).

MVP approach: Linear Regression on the period index. This is intentionally
simple and transparent for a small number of historical points. The
function signature is designed so a more advanced model (Random Forest /
Gradient Boosting on engineered lag features, or eventually a proper
time-series model) can be swapped in later once more historical periods
of real data are available.
"""

import numpy as np
from sklearn.linear_model import LinearRegression


def forecast_next_periods(history_values, periods_ahead=3):
    """history_values: list of past values in chronological order, e.g.
    [1800, 1950, 2050, 2150] representing Year 1..Year 4.

    Returns dict with:
      - forecast: list of predicted future values
      - trend: "increasing" / "decreasing" / "stable"
      - slope: the fitted linear trend per period
      - r2: how well a straight line fits the given history (0-1)
    """
    history_values = [float(v) for v in history_values if v is not None]

    if len(history_values) < 2:
        return {
            "forecast": [],
            "trend": "insufficient_data",
            "slope": 0.0,
            "r2": 0.0,
            "note": "At least 2 historical values are needed to forecast a trend.",
        }

    X = np.arange(len(history_values)).reshape(-1, 1)
    y = np.array(history_values)

    model = LinearRegression()
    model.fit(X, y)

    r2 = float(model.score(X, y)) if len(history_values) > 2 else None

    future_X = np.arange(len(history_values), len(history_values) + periods_ahead).reshape(-1, 1)
    forecast_values = model.predict(future_X)
    # Prevent nonsensical negative prices/yields
    forecast_values = [round(max(0.0, float(v)), 2) for v in forecast_values]

    slope = float(model.coef_[0])
    if abs(slope) < 0.01 * (np.mean(y) + 1e-6):
        trend = "stable"
    elif slope > 0:
        trend = "increasing"
    else:
        trend = "decreasing"

    return {
        "forecast": forecast_values,
        "trend": trend,
        "slope": round(slope, 3),
        "r2": round(r2, 3) if r2 is not None else None,
        "note": "Forecast is a simple linear trend extrapolation from the values provided; treat as indicative only.",
    }
