import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask
from precision_field.zoning import FieldZoningEngine
from precision_field.processor import PrecisionProcessor
from precision_field.water_stress import WaterStressEngine
from precision_field.routes import precision_field_bp, init_precision_field

class TestPrecisionFieldModule(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__, template_folder=os.path.join(project_root, 'templates'))
        self.app.secret_key = "test_secret_key"
        @self.app.route('/')
        def look(): return "Home"
        @self.app.route('/login')
        def login(): return "Login"
        @self.app.route('/about')
        def about(): return "About"
        @self.app.route('/new_predict')
        def new_predict(): return "Predict"
        @self.app.route('/dashboard')
        def dashboard(): return "Dashboard"
        
        init_precision_field(self.app)
        self.client = self.app.test_client()



    def test_zoning_grid_generation(self):
        """Test spatial grid zoning generation (3x3 grid = 9 sub-zones)"""
        bbox = [77.206, 28.610, 77.212, 28.616]
        z_data = FieldZoningEngine.generate_zones(bbox, rows=3, cols=3, field_id="field_test")
        
        self.assertEqual(z_data["total_zones"], 9)
        self.assertEqual(z_data["grid_resolution"], "3x3")
        self.assertEqual(z_data["zones"][0]["grid_code"], "A1")
        self.assertIn("centroid", z_data["zones"][0])

    def test_ndmi_ndvi_calculations(self):
        """Test Sentinel-2 band math for NDVI and NDMI"""
        ndvi = PrecisionProcessor.calculate_ndvi(b04_red=0.10, b08_nir=0.60)
        # (0.60 - 0.10)/(0.60 + 0.10) = 0.50/0.70 = 0.714
        self.assertAlmostEqual(ndvi, 0.714, places=2)

        ndmi = PrecisionProcessor.calculate_ndmi(b08_nir=0.60, b11_swir=0.30)
        # (0.60 - 0.30)/(0.60 + 0.30) = 0.30/0.90 = 0.333
        self.assertAlmostEqual(ndmi, 0.333, places=2)

    def test_explainable_water_stress_engine(self):
        """Test rule-based water stress evaluation and reasons output"""
        zone = {"zone_id": "z8", "zone_name": "Zone 8", "grid_code": "C2", "ndvi": 0.35, "ndmi": 0.08, "spatial_anomaly": True}
        weather = {"available": True, "recent_rainfall_mm": 1.5, "max_temp_c": 37.0}
        
        res = WaterStressEngine.evaluate_zone_stress(zone, weather=weather)
        
        self.assertIn(res["status"], ["Potential Water Stress", "Attention Required"])
        self.assertGreaterEqual(res["stress_indicator_score"], 50.0)
        self.assertGreater(len(res["reasons"]), 0)

    def test_blueprint_api_endpoints(self):
        """Test Flask HTTP endpoints"""
        res_zones = self.client.get('/api/precision/fields/field_001/zones?lat=28.6139&lng=77.2090')
        self.assertEqual(res_zones.status_code, 200)

        res_diag = self.client.get('/api/precision/fields/field_001/water-stress?lat=28.6139&lng=77.2090')
        self.assertEqual(res_diag.status_code, 200)

        res_dash = self.client.get('/precision-field-dashboard')
        self.assertEqual(res_dash.status_code, 200)

if __name__ == '__main__':
    unittest.main()
