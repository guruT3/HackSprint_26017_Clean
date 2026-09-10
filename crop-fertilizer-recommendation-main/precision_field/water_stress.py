from typing import Dict, Any, List
from .config import PrecisionConfig

class WaterStressEngine:
    """
    Transparent, explainable rule-based decision engine for satellite water-stress detection
    and targeted precision irrigation attention.
    """
    
    @staticmethod
    def evaluate_zone_stress(zone: Dict[str, Any], weather: Dict[str, Any] = None, soil: Dict[str, Any] = None, crop: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluates water stress evidence for a specific zone using multi-source input data.
        Returns indicator score (0-100), status classification, confidence level, reasons list, and recommendation.
        """
        ndvi = zone.get("ndvi", 0.60)
        ndmi = zone.get("ndmi", 0.25)
        spatial_anomaly = zone.get("spatial_anomaly", False)
        
        reasons = []
        stress_score = 0.0
        
        # 1. Satellite Vegetation Moisture Signal (NDMI - Weight 35%)
        if ndmi < PrecisionConfig.NDMI_STRESS_THRESHOLD:
            score_ndmi = min(1.0, (PrecisionConfig.NDMI_STRESS_THRESHOLD - ndmi) / 0.20) * 35.0
            stress_score += score_ndmi
            reasons.append(f"NDMI vegetation moisture signal ({ndmi:.2f}) is below reference threshold ({PrecisionConfig.NDMI_STRESS_THRESHOLD:.2f}).")
        
        # 2. Satellite Vegetation Vigor (NDVI - Weight 35%)
        if ndvi < PrecisionConfig.NDVI_STRESS_THRESHOLD:
            score_ndvi = min(1.0, (PrecisionConfig.NDVI_STRESS_THRESHOLD - ndvi) / 0.25) * 35.0
            stress_score += score_ndvi
            reasons.append(f"NDVI vegetation vigor ({ndvi:.2f}) is lower than expected healthy range ({PrecisionConfig.NDVI_STRESS_THRESHOLD:.2f}).")
            
        # 3. Relative Spatial Anomaly vs Neighboring Field Zones
        if spatial_anomaly:
            stress_score += 10.0
            median_ndvi = zone.get("field_median_ndvi", 0.60)
            reasons.append(f"Zone NDVI ({ndvi:.2f}) shows relative spatial drop compared to neighboring field median ({median_ndvi:.2f}).")

        # 4. Weather Evapotranspiration Demand (Weight 15%)
        if weather and weather.get("available"):
            rain = weather.get("recent_rainfall_mm", 10.0)
            temp = weather.get("max_temp_c", 30.0)
            if rain < 5.0 and temp > 34.0:
                stress_score += 15.0
                reasons.append(f"Recent rainfall ({rain}mm) is low under elevated temperature ({temp}°C), increasing crop water demand.")
            elif rain < 5.0:
                stress_score += 8.0
                reasons.append(f"Low recent rainfall ({rain}mm) observed over the past 7 days.")

        # 5. Soil Moisture Sensor/Estimate (Weight 10%)
        if soil and soil.get("available"):
            moisture = soil.get("soil_moisture_percent", 25.0)
            if moisture < 15.0:
                stress_score += 10.0
                reasons.append(f"Soil moisture estimate ({moisture}%) is near wilting point.")
            elif moisture < 20.0:
                stress_score += 5.0

        # 6. Crop Growth Stage Sensitivity (Weight 5%)
        if crop and crop.get("available"):
            stage = crop.get("growth_stage", "")
            if "Flowering" in stage or "Grain" in stage:
                stress_score += 5.0
                reasons.append(f"Crop is at critical '{stage}' growth stage with high water sensitivity.")

        final_score = float(round(min(100.0, stress_score), 1))
        
        # Classification
        if final_score >= 60.0:
            status = "Potential Water Stress"
            badge_color = "#e74c3c" # Red
            attention_level = "High Attention Required"
        elif final_score >= 35.0:
            status = "Attention Required"
            badge_color = "#f1c40f" # Yellow
            attention_level = "Moderate Attention"
        else:
            status = "Normal / Healthy"
            badge_color = "#2ecc71" # Green
            attention_level = "Normal Monitoring"

        # Determine Confidence Level based on available data sources
        sources_count = 1 + (1 if weather and weather.get("available") else 0) + (1 if soil and soil.get("available") else 0) + (1 if crop and crop.get("available") else 0)
        confidence = "High" if sources_count >= 3 else ("Medium" if sources_count == 2 else "Low")

        if not reasons:
            reasons.append("Vegetation moisture and vigor signals are within healthy baseline parameters across this zone.")

        recommendation = f"Inspect {zone['zone_name']} in person to verify soil moisture before making irrigation decisions." if final_score >= 35.0 else f"No immediate irrigation needed in {zone['zone_name']}. Continue standard field monitoring."

        return {
            "zone_id": zone["zone_id"],
            "zone_name": zone["zone_name"],
            "grid_code": zone["grid_code"],
            "status": status,
            "badge_color": badge_color,
            "stress_indicator_score": final_score,
            "attention_level": attention_level,
            "confidence": confidence,
            "ndvi": ndvi,
            "ndmi": ndmi,
            "reasons": reasons,
            "recommendation": recommendation
        }
