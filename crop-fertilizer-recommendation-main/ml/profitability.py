"""
profitability.py
------------------
Pure-Python financial calculations. Deliberately contains NO machine
learning - the ML models predict yield/price, and this module turns those
predictions (plus farmer-entered costs) into profitability numbers.
Kept separate so the math is transparent, testable, and auditable.
"""


def safe_div(numerator, denominator, default=0.0):
    """Division that never raises ZeroDivisionError."""
    try:
        if denominator in (0, 0.0, None):
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def calculate_total_cost(costs: dict) -> float:
    """costs: dict with seed_cost, fertilizer_cost, pesticide_cost,
    labour_cost, irrigation_cost, machinery_cost, other_cost (all per-acre),
    already scaled by farm area by the caller, OR pass per-acre costs and
    farm_area separately using calculate_total_cost_for_farm below."""
    keys = ["seed_cost", "fertilizer_cost", "pesticide_cost", "labour_cost",
            "irrigation_cost", "machinery_cost", "other_cost"]
    return float(sum(costs.get(k, 0) or 0 for k in keys))


def calculate_total_cost_for_farm(per_acre_costs: dict, farm_area: float) -> float:
    per_acre_total = calculate_total_cost(per_acre_costs)
    return per_acre_total * farm_area


def compute_profitability(
    predicted_yield_per_acre: float,
    farm_area: float,
    expected_market_price: float,
    per_acre_costs: dict,
) -> dict:
    """Core profitability calculation used by every crop plan / comparison.

    Returns a dict with all financial outputs, safe against
    division-by-zero (e.g. farm_area or market price = 0).
    """
    total_cost = calculate_total_cost_for_farm(per_acre_costs, farm_area)
    total_yield = predicted_yield_per_acre * farm_area
    revenue = total_yield * expected_market_price
    profit = revenue - total_cost
    profit_per_acre = safe_div(profit, farm_area)

    break_even_yield = safe_div(total_cost, expected_market_price)  # quintals needed to cover cost
    break_even_price = safe_div(total_cost, total_yield)            # price per quintal needed to cover cost
    roi_percent = safe_div(profit, total_cost) * 100

    return {
        "predicted_yield_per_acre": round(predicted_yield_per_acre, 2),
        "total_yield": round(total_yield, 2),
        "expected_market_price": round(expected_market_price, 2),
        "total_cost": round(total_cost, 2),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "profit_per_acre": round(profit_per_acre, 2),
        "break_even_yield": round(break_even_yield, 2),
        "break_even_price": round(break_even_price, 2),
        "roi_percent": round(roi_percent, 2),
    }


def generate_planning_insights(result: dict, per_acre_costs: dict) -> list:
    """Generates 3-5 human-readable insights from the calculated numbers.
    Pure string/number logic - no LLM involved, as required."""
    insights = []

    # Insight 1: biggest cost driver
    if per_acre_costs:
        biggest = max(per_acre_costs.items(), key=lambda kv: kv[1] or 0)
        label = biggest[0].replace("_cost", "").replace("_", " ").title()
        total_costs = sum(v or 0 for v in per_acre_costs.values())
        share = safe_div(biggest[1] or 0, total_costs) * 100
        if share > 0:
            insights.append(
                f"Your {label} cost accounts for roughly {share:.0f}% of total per-acre cultivation expenses."
            )

    # Insight 2: sensitivity to yield improvement
    profit = result.get("profit", 0)
    total_yield = result.get("total_yield", 0)
    price = result.get("expected_market_price", 0)
    extra_profit_10pct = 0.10 * total_yield * price
    insights.append(
        f"Increasing yield by 10% could raise estimated profit by approximately Rs. {extra_profit_10pct:,.0f}."
    )

    # Insight 3: market price vs break-even
    be_price = result.get("break_even_price", 0)
    if price and be_price:
        if price > be_price:
            margin = safe_div(price - be_price, be_price) * 100
            insights.append(
                f"The current market price is about {margin:.0f}% above the estimated break-even price, indicating a cushion against price drops."
            )
        else:
            insights.append(
                "The current market price is at or below the estimated break-even price - this plan carries margin risk."
            )

    # Insight 4: profitability verdict
    if profit > 0:
        insights.append(f"This plan is expected to be profitable, with an estimated ROI of {result.get('roi_percent', 0):.1f}%.")
    else:
        insights.append("This plan is currently projected to run at a loss based on the entered costs and expected price.")

    # Insight 5: break-even yield context
    be_yield = result.get("break_even_yield", 0)
    predicted_total_yield = result.get("total_yield", 0)
    if be_yield and predicted_total_yield:
        cushion = safe_div(predicted_total_yield - be_yield, be_yield) * 100
        insights.append(
            f"Predicted total yield is about {cushion:.0f}% {'above' if cushion >= 0 else 'below'} the break-even yield needed to cover costs."
        )

    return insights[:5]
