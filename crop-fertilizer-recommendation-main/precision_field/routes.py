from flask import Blueprint, request, jsonify, render_template
from .zoning import FieldZoningEngine
from .processor import PrecisionProcessor
from .water_stress import WaterStressEngine
from .schemas import PrecisionSchema
from .adapters import (
    DefaultSatelliteProvider, DefaultSoilProvider,
    DefaultWeatherProvider, DefaultCropProvider
)

precision_field_bp = Blueprint(
    'precision_field',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/precision-static'
)

# Global adapters (pluggable by host app)
satellite_provider = DefaultSatelliteProvider()
soil_provider = DefaultSoilProvider()
weather_provider = DefaultWeatherProvider()
crop_provider = DefaultCropProvider()

def init_precision_field(app, sat_prov=None, soil_prov=None, wx_prov=None, crop_prov=None):
    """Host application registration function."""
    global satellite_provider, soil_provider, weather_provider, crop_provider
    if sat_prov: satellite_provider = sat_prov
    if soil_prov: soil_provider = soil_prov
    if wx_prov: weather_provider = wx_prov
    if crop_prov: crop_provider = crop_prov
    
    app.register_blueprint(precision_field_bp)
    print("[+] Precision Field Zoning & Water-Stress Detection Module successfully registered.")


@precision_field_bp.route('/api/precision/fields/<field_id>/zones', methods=['GET'])
def get_field_zones(field_id):
    """
    REST API: Divides field into spatial zones (default 3x3 grid) and computes satellite NDMI/NDVI index stats per zone.
    """
    lat = request.args.get('lat', default=28.6139, type=float)
    lng = request.args.get('lng', default=77.2090, type=float)
    rows = request.args.get('rows', default=3, type=int)
    cols = request.args.get('cols', default=3, type=int)

    # Calculate bounding box approx 300m x 300m around field center
    d_lat = 0.003
    d_lng = 0.003
    bbox = [round(lng - d_lng, 6), round(lat - d_lat, 6), round(lng + d_lng, 6), round(lat + d_lat, 6)]

    # 1. Generate Field Spatial Zones
    zoning_result = FieldZoningEngine.generate_zones(bbox, rows=rows, cols=cols, field_id=field_id)

    # 2. Fetch Multi-Source Data via Adapters
    weather_data = weather_provider.get_weather_data(lat, lng)
    soil_data = soil_provider.get_soil_data(lat, lng)
    crop_data = crop_provider.get_crop_data(field_id)

    zone_evaluations = []
    zone_list_for_anomaly = []

    for z in zoning_result["zones"]:
        sat_data = satellite_provider.get_zone_satellite_data(z["zone_id"], z["bbox"])
        z["ndvi"] = sat_data.get("ndvi", 0.60)
        z["ndmi"] = sat_data.get("ndmi", 0.25)
        zone_list_for_anomaly.append(z)

    # 3. Detect Spatial Anomalies vs Neighboring Zones
    PrecisionProcessor.detect_spatial_anomalies(zone_list_for_anomaly)

    # 4. Evaluate Water Stress for each Zone
    for z in zoning_result["zones"]:
        eval_info = WaterStressEngine.evaluate_zone_stress(z, weather=weather_data, soil=soil_data, crop=crop_data)
        zone_evaluations.append(eval_info)

    formatted = PrecisionSchema.format_zones_response(zoning_result, zone_evaluations)
    return jsonify(formatted), 200


@precision_field_bp.route('/api/precision/fields/<field_id>/water-stress', methods=['GET'])
def get_water_stress_diagnostic(field_id):
    """
    REST API: Full explainable water-stress diagnostic report for a farm field.
    """
    lat = request.args.get('lat', default=28.6139, type=float)
    lng = request.args.get('lng', default=77.2090, type=float)

    # Fetch spatial zones and run evaluation
    zones_response, status_code = get_field_zones(field_id)
    data = zones_response.get_json()["data"]

    strained_zones = [z for z in data["zones"] if z["status"] != "Normal / Healthy"]

    return jsonify({
        "status": "success",
        "diagnostic_summary": {
            "field_id": field_id,
            "overall_status": data["overall_status"],
            "total_zones": data["total_zones"],
            "flagged_zones_count": len(strained_zones),
            "data_sources": {
                "satellite": True,
                "weather": True,
                "soil": True,
                "crop": True
            },
            "attention_zones": strained_zones
        }
    }), 200


@precision_field_bp.route('/precision-field-dashboard', methods=['GET'])
def precision_dashboard_view():
    """
    HTML Dashboard Route for Precision Field Zoning & Water-Stress Monitor.
    """
    return render_template('precision_field.html')
