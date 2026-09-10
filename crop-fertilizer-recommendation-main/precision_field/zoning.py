import math

class FieldZoningEngine:
    """
    Divides a farm field boundary polygon into discrete spatial analysis sub-zones (e.g. 3x3 grid),
    calculating centroid coordinates, area, and bounding boxes for targeted precision management.
    """
    
    @staticmethod
    def generate_zones(bbox, rows=3, cols=3, field_id="field_01"):
        """
        Generates a grid of spatial zones over the field bounding box [min_lng, min_lat, max_lng, max_lat].
        Returns a list of dict objects representing each individual sub-zone.
        """
        min_lng, min_lat, max_lng, max_lat = bbox
        
        d_lat = (max_lat - min_lat) / rows
        d_lng = (max_lng - min_lng) / cols
        
        # Estimate total field area in acres (approximate 1 deg lat ~ 111km)
        lat_m = (max_lat - min_lat) * 111000
        lng_m = (max_lng - min_lng) * (111000 * math.cos(math.radians((min_lat + max_lat) / 2)))
        total_acres = round((lat_m * lng_m) / 4046.86, 2)
        zone_acreage = round(total_acres / (rows * cols), 2)
        
        zones = []
        zone_counter = 1
        
        row_labels = ['A', 'B', 'C', 'D', 'E']
        
        for r in range(rows):
            for c in range(cols):
                z_min_lat = min_lat + (rows - 1 - r) * d_lat
                z_max_lat = z_min_lat + d_lat
                z_min_lng = min_lng + c * d_lng
                z_max_lng = z_min_lng + d_lng
                
                centroid_lat = round((z_min_lat + z_max_lat) / 2.0, 6)
                centroid_lng = round((z_min_lng + z_max_lng) / 2.0, 6)
                
                label_row = row_labels[r] if r < len(row_labels) else f"R{r+1}"
                grid_code = f"{label_row}{c+1}"
                zone_name = f"Zone {zone_counter}"
                
                zone_polygon = {
                    "type": "Polygon",
                    "coordinates": [[
                        [round(z_min_lng, 6), round(z_min_lat, 6)],
                        [round(z_max_lng, 6), round(z_min_lat, 6)],
                        [round(z_max_lng, 6), round(z_max_lat, 6)],
                        [round(z_min_lng, 6), round(z_max_lat, 6)],
                        [round(z_min_lng, 6), round(z_min_lat, 6)]
                    ]]
                }
                
                zones.append({
                    "zone_id": f"{field_id}_z{zone_counter}",
                    "zone_number": zone_counter,
                    "grid_code": grid_code,
                    "zone_name": zone_name,
                    "row": r + 1,
                    "col": c + 1,
                    "area_acres": zone_acreage,
                    "centroid": {"lat": centroid_lat, "lng": centroid_lng},
                    "bbox": [round(z_min_lng, 6), round(z_min_lat, 6), round(z_max_lng, 6), round(z_max_lat, 6)],
                    "geometry": zone_polygon
                })
                zone_counter += 1
                
        return {
            "field_id": str(field_id),
            "total_area_acres": total_acres,
            "grid_resolution": f"{rows}x{cols}",
            "total_zones": len(zones),
            "zones": zones
        }
