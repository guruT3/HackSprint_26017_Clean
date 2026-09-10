class PrecisionSchema:
    """Formatters and serializers for Precision Zoning & Water Stress API endpoints."""
    
    @staticmethod
    def format_zones_response(zoning_data, zone_evaluations):
        eval_map = {e["zone_id"]: e for e in zone_evaluations}
        
        formatted_zones = []
        for z in zoning_data["zones"]:
            eval_info = eval_map.get(z["zone_id"], {})
            formatted_zones.append({
                "zone_id": z["zone_id"],
                "zone_name": z["zone_name"],
                "grid_code": z["grid_code"],
                "area_acres": z["area_acres"],
                "centroid": z["centroid"],
                "bbox": z["bbox"],
                "geometry": z["geometry"],
                "ndvi": z.get("ndvi"),
                "ndmi": z.get("ndmi"),
                "status": eval_info.get("status", "Normal"),
                "badge_color": eval_info.get("badge_color", "#2ecc71"),
                "stress_indicator_score": eval_info.get("stress_indicator_score", 0.0),
                "confidence": eval_info.get("confidence", "Medium"),
                "reasons": eval_info.get("reasons", []),
                "recommendation": eval_info.get("recommendation", "")
            })

        # Count summary statuses
        normal_count = sum(1 for z in formatted_zones if z["status"] == "Normal / Healthy")
        attention_count = sum(1 for z in formatted_zones if z["status"] == "Attention Required")
        stress_count = sum(1 for z in formatted_zones if z["status"] == "Potential Water Stress")

        overall_status = "Potential Stress Detected" if stress_count > 0 else ("Attention Required" if attention_count > 0 else "Field Healthy")

        return {
            "status": "success",
            "data": {
                "field_id": zoning_data["field_id"],
                "total_area_acres": zoning_data["total_area_acres"],
                "grid_resolution": zoning_data["grid_resolution"],
                "total_zones": zoning_data["total_zones"],
                "overall_status": overall_status,
                "summary_counts": {
                    "normal": normal_count,
                    "attention": attention_count,
                    "potential_stress": stress_count
                },
                "zones": formatted_zones
            }
        }
