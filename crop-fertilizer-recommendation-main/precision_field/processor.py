import numpy as np

class PrecisionProcessor:
    """
    Computes Sentinel-2 band indices (NDVI & NDMI) and relative spatial anomalies across field zones.
    """
    
    @staticmethod
    def calculate_ndvi(b04_red, b08_nir):
        """NDVI = (B08 - B04) / (B08 + B04)"""
        denom = b08_nir + b04_red
        if denom == 0:
            return 0.0
        val = (b08_nir - b04_red) / denom
        return round(float(np.clip(val, -1.0, 1.0)), 3)

    @staticmethod
    def calculate_ndmi(b08_nir, b11_swir):
        """
        NDMI = (B08 - B11) / (B08 + B11)
        Represents vegetation moisture content (NIR vs SWIR).
        Note: NDMI indicates vegetation moisture signal, not direct soil probe measurements.
        """
        denom = b08_nir + b11_swir
        if denom == 0:
            return 0.0
        val = (b08_nir - b11_swir) / denom
        return round(float(np.clip(val, -1.0, 1.0)), 3)

    @staticmethod
    def detect_spatial_anomalies(zone_stats_list):
        """
        Detects relative spatial anomalies by comparing each zone's NDVI and NDMI
        against the median values of neighboring zones across the field.
        """
        if not zone_stats_list:
            return zone_stats_list

        all_ndvis = [z["ndvi"] for z in zone_stats_list if "ndvi" in z]
        all_ndmis = [z["ndmi"] for z in zone_stats_list if "ndmi" in z]

        median_ndvi = float(np.median(all_ndvis)) if all_ndvis else 0.60
        median_ndmi = float(np.median(all_ndmis)) if all_ndmis else 0.25

        for z in zone_stats_list:
            ndvi_diff = median_ndvi - z["ndvi"]
            ndmi_diff = median_ndmi - z["ndmi"]

            # Flag spatial anomaly if zone is >= 0.15 lower than field median
            z["spatial_anomaly"] = (ndvi_diff >= 0.15) or (ndmi_diff >= 0.15)
            z["field_median_ndvi"] = round(median_ndvi, 3)
            z["field_median_ndmi"] = round(median_ndmi, 3)

        return zone_stats_list
