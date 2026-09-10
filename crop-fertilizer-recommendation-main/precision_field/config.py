import os

class PrecisionConfig:
    """Configuration settings for Precision Field Zoning & Water-Stress Module."""
    
    # Grid Zoning Resolution (Rows x Columns)
    DEFAULT_ZONE_ROWS = int(os.getenv("PRECISION_ZONE_ROWS", "3"))
    DEFAULT_ZONE_COLS = int(os.getenv("PRECISION_ZONE_COLS", "3"))
    
    # Satellite Band Thresholds
    NDVI_STRESS_THRESHOLD = float(os.getenv("NDVI_STRESS_THRESHOLD", "0.45"))
    NDMI_STRESS_THRESHOLD = float(os.getenv("NDMI_STRESS_THRESHOLD", "0.15"))
    
    # Relative Anomaly Threshold (% drop compared to neighboring zones)
    SPATIAL_ANOMALY_THRESHOLD = float(os.getenv("SPATIAL_ANOMALY_THRESHOLD", "0.15"))
    
    # Evidence Weights for Water Stress Indicator Score (Total 100%)
    WEIGHTS = {
        "satellite_ndvi": 0.35, # Vegetation vigor
        "satellite_ndmi": 0.35, # Vegetation moisture signal
        "weather_demand": 0.15, # Rain deficit & temperature ET demand
        "soil_moisture": 0.10,  # Field moisture if available
        "crop_sensitivity": 0.05# Crop growth stage sensitivity
    }
    
    CACHE_TIMEOUT = int(os.getenv("PRECISION_CACHE_TIMEOUT", "86400"))
