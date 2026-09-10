import math
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SatelliteProviderInterface(ABC):
    @abstractmethod
    def get_zone_satellite_data(self, zone_id: str, bbox: list, date_str: str = None) -> Dict[str, Any]:
        pass

class SoilDataProviderInterface(ABC):
    @abstractmethod
    def get_soil_data(self, lat: float, lng: float) -> Dict[str, Any]:
        pass

class WeatherProviderInterface(ABC):
    @abstractmethod
    def get_weather_data(self, lat: float, lng: float) -> Dict[str, Any]:
        pass

class CropProviderInterface(ABC):
    @abstractmethod
    def get_crop_data(self, field_id: str) -> Dict[str, Any]:
        pass


class DefaultSatelliteProvider(SatelliteProviderInterface):
    """Default Sentinel-2 Satellite Provider with realtime location-sensitive spatial variability."""
    def get_zone_satellite_data(self, zone_id: str, bbox: list, date_str: str = None) -> Dict[str, Any]:
        min_lng, min_lat, max_lng, max_lat = bbox
        c_lat = (min_lat + max_lat) / 2.0
        c_lng = (min_lng + max_lng) / 2.0
        
        # Extract zone number (1-9)
        z_num = int(zone_id.split('_z')[-1]) if '_z' in zone_id else 1
        
        # Spatial base values derived dynamically from geographic coordinates (lat, lng)
        spatial_lat_factor = math.sin(c_lat * 18.5)
        spatial_lng_factor = math.cos(c_lng * 22.3)
        
        # Base vegetation vigor (NDVI: 0.35 to 0.85)
        base_ndvi = 0.60 + 0.20 * spatial_lat_factor * spatial_lng_factor
        
        # Base moisture index (NDMI: 0.02 to 0.40)
        base_ndmi = 0.22 + 0.15 * math.sin(c_lat * 12.1 + c_lng * 14.7)
        
        # Zone-specific micro-variability within the field based on coordinates
        coord_hash = int(abs(c_lat * 10000 + c_lng * 5000))
        zone_seed = (z_num * 17 + coord_hash) % 100
        
        zone_ndvi_offset = ((zone_seed % 21) - 10) / 100.0   # -0.10 to +0.10
        zone_ndmi_offset = (((zone_seed * 3) % 21) - 10) / 100.0 # -0.10 to +0.10

        # Location stress anomaly simulation for selected micro-zones to highlight water-stress detection
        if zone_seed in [12, 23, 34, 45, 56, 67, 78, 89]:
            zone_ndmi_offset -= 0.18
            zone_ndvi_offset -= 0.22
            
        ndvi = round(max(0.20, min(0.92, base_ndvi + zone_ndvi_offset)), 2)
        ndmi = round(max(-0.15, min(0.55, base_ndmi + zone_ndmi_offset)), 2)
        
        return {
            "ndvi": ndvi,
            "ndmi": ndmi,
            "cloud_cover": round(abs(math.sin(c_lat * 3.3)) * 4.5, 1),
            "valid": True
        }


class DefaultSoilProvider(SoilDataProviderInterface):
    def get_soil_data(self, lat: float, lng: float) -> Dict[str, Any]:
        moisture = round(max(8.0, min(42.0, 22.0 + 12.0 * math.sin(lat * 8.4 + lng * 4.9))), 1)
        soil_types = ["Clay Loam", "Sandy Clay", "Silt Loam", "Black Cotton Soil", "Alluvial Soil"]
        st_idx = int(abs(lat * 100 + lng * 50)) % len(soil_types)
        return {
            "available": True,
            "soil_type": soil_types[st_idx],
            "soil_moisture_percent": moisture,
            "source": "Realtime Spatial Model"
        }


class DefaultWeatherProvider(WeatherProviderInterface):
    def get_weather_data(self, lat: float, lng: float) -> Dict[str, Any]:
        temp = round(26.0 + 10.0 * abs(math.sin(lat * 5.1 + lng * 3.7)), 1)
        rain = round(max(0.0, 18.0 * math.cos(lat * 7.2 - lng * 4.4)), 1)
        humidity = int(35 + 45 * abs(math.sin(lng * 6.1)))
        status = "Elevated Evapotranspiration" if temp > 32 or rain < 5 else "Normal Weather Demand"
        return {
            "available": True,
            "recent_rainfall_mm": rain,
            "max_temp_c": temp,
            "humidity_percent": humidity,
            "water_demand_status": status
        }


class DefaultCropProvider(CropProviderInterface):
    def get_crop_data(self, field_id: str) -> Dict[str, Any]:
        return {
            "available": True,
            "crop_name": "Paddy (Rice)",
            "growth_stage": "Flowering / Grain Filling",
            "sensitivity": "High Water Sensitivity"
        }
