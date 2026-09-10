"""
crop_planner_routes.py
------------------------
Flask route(s) for the AI Crop Planning, Profitability & Forecasting module.

HOW TO INTEGRATE INTO YOUR EXISTING APP:

  from crop_planner_routes import register_crop_planner
  register_crop_planner(app)

This keeps your existing app.py untouched apart from those two lines -
no existing routes, templates or static files are modified.

Do NOT put model training code in the request path: models are trained
offline via `python ml/train_models.py` and simply loaded here with joblib.
"""

import os
import joblib
from flask import render_template, request, jsonify,session



from ml.recommendation import (
    compare_crops, top_recommendations, recommendation_reasons, CANDIDATE_CROPS,
)
from ml.profitability import generate_planning_insights
from ml.forecast import forecast_next_periods

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "ml", "models")

_yield_model = None
_price_model = None


def _load_models():
    """Lazy-load models once and cache them (avoids reloading on every request)."""
    global _yield_model, _price_model
    if _yield_model is None or _price_model is None:
        yield_path = os.path.join(MODELS_DIR, "yield_model.pkl")
        price_path = os.path.join(MODELS_DIR, "price_model.pkl")
        if not (os.path.exists(yield_path) and os.path.exists(price_path)):
            raise FileNotFoundError(
                "Trained models not found. Run `python ml/train_models.py` first "
                "(after `python ml/generate_dataset.py`)."
            )
        _yield_model = joblib.load(yield_path)
        _price_model = joblib.load(price_path)
    return _yield_model, _price_model


REQUIRED_FIELDS = [
    "farm_area", "soil_type", "irrigation", "season",
    "seed_cost", "fertilizer_cost", "pesticide_cost", "labour_cost",
    "irrigation_cost", "machinery_cost", "other_cost", "market_price",
]

OPTIONAL_FIELDS_DEFAULTS = {
    "region": "East",
    "rainfall": 900.0,
    "temperature": 25.0,
    "soil_ph": 6.5,
    "soil_moisture": 40.0,
    "previous_yield": 15.0,
    "farming_experience": 5,
    "previous_crop": "",
}


def _parse_form(form):
    """Validates required fields and applies sensible defaults for optional
    ones. Raises ValueError with a user-facing message on bad input."""
    errors = []
    data = {}

    for field in REQUIRED_FIELDS:
        raw = form.get(field, "").strip()
        if raw == "":
            errors.append(f"'{field.replace('_', ' ')}' is required.")
            continue
        data[field] = raw

    if errors:
        raise ValueError(" ".join(errors))

    # Type conversion for numeric required fields
    numeric_required = [
        "farm_area", "seed_cost", "fertilizer_cost", "pesticide_cost",
        "labour_cost", "irrigation_cost", "machinery_cost", "other_cost",
        "market_price",
    ]
    for field in numeric_required:
        try:
            data[field] = float(data[field])
        except (TypeError, ValueError):
            raise ValueError(f"'{field.replace('_', ' ')}' must be a number.")

    if data["farm_area"] <= 0:
        raise ValueError("Farm area must be greater than zero.")

    # Optional fields with defaults
    for field, default in OPTIONAL_FIELDS_DEFAULTS.items():
        raw = form.get(field, "").strip() if isinstance(form.get(field, ""), str) else form.get(field, "")
        if raw == "" or raw is None:
            data[field] = default
        else:
            if isinstance(default, (int, float)):
                try:
                    data[field] = float(raw)
                except (TypeError, ValueError):
                    data[field] = default
            else:
                data[field] = raw

    # Crop name (used for the "your selected crop" primary result)
    data["crop"] = form.get("crop", "").strip() or "Rice"

    return data


def _build_farm_input(data):
    """Maps parsed form data into the feature dict expected by the ML
    models (see ml/preprocessing.py ALL_FEATURES)."""
    return dict(
        farm_area=data["farm_area"],
        soil_type=data["soil_type"],
        irrigation=data["irrigation"],
        season=data["season"],
        region=data.get("region", "East"),
        rainfall=data.get("rainfall", 900.0),
        temperature=data.get("temperature", 25.0),
        soil_ph=data.get("soil_ph", 6.5),
        soil_moisture=data.get("soil_moisture", 40.0),
        seed_cost=data["seed_cost"],
        fertilizer_cost=data["fertilizer_cost"],
        pesticide_cost=data["pesticide_cost"],
        labour_cost=data["labour_cost"],
        irrigation_cost=data["irrigation_cost"],
        machinery_cost=data["machinery_cost"],
        other_cost=data["other_cost"],
        previous_yield=data.get("previous_yield", 15.0),
        farming_experience=int(data.get("farming_experience", 5)),
    )


def register_crop_planner(app, db, TaskCompletion):   # accept as params


    """Attach the Crop Planner and task-completion routes."""

    @app.route("/crop-planner", methods=["GET", "POST"])
    def crop_planner():

        # Get logged-in username from session
        username = session.get("username")

        # Get tasks already completed by this user
        completed_tasks = []

        if username:
            completed_tasks = [
                task.task_id
                for task in TaskCompletion.query.filter_by(
                    username=username,
                    completed=True
                ).all()
            ]

        # ---------------------------------------------------------
        # GET: Show Crop Planner
        # ---------------------------------------------------------
        if request.method == "GET":

            return render_template(
                "crop_planner.html",
                crops=CANDIDATE_CROPS,
                username=username,
                completed_tasks=completed_tasks
            )

        # ---------------------------------------------------------
        # POST: Run ML + Profitability Pipeline
        # ---------------------------------------------------------
        try:

            data = _parse_form(request.form)

        except ValueError as e:

            return render_template(
                "crop_planner.html",
                crops=CANDIDATE_CROPS,
                username=username,
                completed_tasks=completed_tasks,
                error=str(e)
            ), 400

        try:

            yield_model, price_model = _load_models()

        except FileNotFoundError as e:

            return render_template(
                "crop_planner.html",
                crops=CANDIDATE_CROPS,
                username=username,
                completed_tasks=completed_tasks,
                error=str(e)
            ), 500

        # Build farm input
        farm_input = _build_farm_input(data)

        # ---------------------------------------------------------
        # Selected comparison crops
        # ---------------------------------------------------------
        selected_crops = request.form.getlist("compare_crops") or [
            "Rice",
            "Wheat",
            "Maize",
            "Cotton",
            "Tomato",
            "Potato"
        ]

        selected_crops = [
            c for c in selected_crops
            if c in CANDIDATE_CROPS
        ] or CANDIDATE_CROPS

        # ---------------------------------------------------------
        # Compare crops
        # ---------------------------------------------------------
        comparison_results = compare_crops(
            yield_model,
            price_model,
            farm_input,
            crops=selected_crops
        )

        # ---------------------------------------------------------
        # Top 3 recommendations
        # ---------------------------------------------------------
        top3 = top_recommendations(
            comparison_results,
            n=3
        )

        best_overall = top3[0] if top3 else None

        # ---------------------------------------------------------
        # Best profit
        # ---------------------------------------------------------
        best_profit = (
            max(
                comparison_results,
                key=lambda r: r["profit"]
            )
            if comparison_results
            else None
        )

        # ---------------------------------------------------------
        # Best ROI
        # ---------------------------------------------------------
        best_roi = (
            max(
                comparison_results,
                key=lambda r: r["roi_percent"]
            )
            if comparison_results
            else None
        )

        # ---------------------------------------------------------
        # Lowest risk
        # ---------------------------------------------------------
        lowest_risk = (
            min(
                comparison_results,
                key=lambda r: r["risk_score"]
            )
            if comparison_results
            else None
        )

        # ---------------------------------------------------------
        # Primary crop selected by farmer
        # ---------------------------------------------------------
        primary_result = next(
            (
                r for r in comparison_results
                if r["crop"] == data["crop"]
            ),
            comparison_results[0]
            if comparison_results
            else None
        )

        # ---------------------------------------------------------
        # Per-acre costs
        # ---------------------------------------------------------
        per_acre_costs = {

            "seed_cost": data["seed_cost"],

            "fertilizer_cost": data["fertilizer_cost"],

            "pesticide_cost": data["pesticide_cost"],

            "labour_cost": data["labour_cost"],

            "irrigation_cost": data["irrigation_cost"],

            "machinery_cost": data["machinery_cost"],

            "other_cost": data["other_cost"],
        }

        # ---------------------------------------------------------
        # Planning insights
        # ---------------------------------------------------------
        insights = (
            generate_planning_insights(
                primary_result,
                per_acre_costs
            )
            if primary_result
            else []
        )

        # ---------------------------------------------------------
        # Price forecasting
        # ---------------------------------------------------------
        history_raw = request.form.get(
            "price_history",
            ""
        ).strip()

        forecast_result = None

        if history_raw:

            try:

                history_values = [
                    float(v.strip())
                    for v in history_raw.split(",")
                    if v.strip()
                ]

                forecast_result = forecast_next_periods(
                    history_values,
                    periods_ahead=3
                )

            except ValueError:

                forecast_result = {
                    "trend": "invalid_input",
                    "forecast": [],
                    "note": (
                        "Could not parse historical values. "
                        "Use comma-separated numbers."
                    )
                }

        # ---------------------------------------------------------
        # Recommendation reasons
        # ---------------------------------------------------------
        recommend_reasons = (
            recommendation_reasons(best_overall)
            if best_overall
            else []
        )

        # ---------------------------------------------------------
        # Return Crop Planner
        # ---------------------------------------------------------
        return render_template(

            "crop_planner.html",

            crops=CANDIDATE_CROPS,

            submitted=True,

            # User session information
            username=username,

            # Completed 7-day tasks
            completed_tasks=completed_tasks,

            # Existing crop planner data
            farm_input=farm_input,

            primary_result=primary_result,

            comparison_results=comparison_results,

            top3=top3,

            best_overall=best_overall,

            best_profit=best_profit,

            best_roi=best_roi,

            lowest_risk=lowest_risk,

            insights=insights,

            forecast_result=forecast_result,

            recommend_reasons=recommend_reasons,

            selected_crops=selected_crops
        )

    # =============================================================
    # TASK COMPLETION ROUTE
    # =============================================================

   

    # =============================================================
    # CROP PLANNER API
    # =============================================================

    @app.route("/api/crop-planner", methods=["POST"])
    def crop_planner_api():

        """
        JSON API variant of the same crop-planning pipeline.
        """

        try:

            data = _parse_form(
                request.form or
                request.json or
                {}
            )

            yield_model, price_model = _load_models()

            farm_input = _build_farm_input(data)

            selected_crops = (
                request.form.getlist("compare_crops")
                if request.form
                else (request.json or {}).get(
                    "compare_crops"
                )
            ) or CANDIDATE_CROPS

            selected_crops = [
                c for c in selected_crops
                if c in CANDIDATE_CROPS
            ] or CANDIDATE_CROPS

            results = compare_crops(

                yield_model,

                price_model,

                farm_input,

                crops=selected_crops
            )

            return jsonify({

                "success": True,

                "results": results,

                "top3": top_recommendations(
                    results,
                    3
                )
            })

        except ValueError as e:

            return jsonify({

                "success": False,

                "error": str(e)

            }), 400

        except FileNotFoundError as e:

            return jsonify({

                "success": False,

                "error": str(e)

            }), 500