import unittest
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np

from flask import Flask
from ndvi_module.processor import NDVIProcessor

from ndvi_module.utils import validate_geometry, safe_divide
from ndvi_module.service import SentinelSatelliteService
from ndvi_module.routes import ndvi_bp, init_ndvi_module

class TestNDVIModule(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        init_ndvi_module(self.app)
        self.client = self.app.test_client()

    def test_ndvi_band_math(self):
        """Test core NDVI formula = (B08 - B04) / (B08 + B04)"""
        b04_red = np.array([[0.1, 0.2], [0.3, 0.4]])
        b08_nir = np.array([[0.6, 0.7], [0.3, 0.8]])
        
        ndvi = NDVIProcessor.calculate_ndvi_array(b04_red, b08_nir)
        
        # Pixel (0,0): (0.6 - 0.1) / (0.6 + 0.1) = 0.5 / 0.7 = 0.714
        self.assertAlmostEqual(ndvi[0, 0], 0.7142857, places=5)
        # Pixel (1,0): (0.3 - 0.3) / (0.3 + 0.3) = 0.0
        self.assertAlmostEqual(ndvi[1, 0], 0.0, places=5)

    def test_zero_denominator_safe_divide(self):
        """Test math safety with 0 division and NaNs"""
        res = safe_divide(np.array([1.0, 0.0]), np.array([0.0, 0.0]), fill_value=0.0)
        self.assertEqual(res[0], 0.0)
        self.assertEqual(res[1], 0.0)

    def test_geometry_validation(self):
        """Test Polygon and Point GeoJSON validation"""
        valid_poly = {
            "type": "Polygon",
            "coordinates": [[[77.20, 28.60], [77.21, 28.60], [77.21, 28.61], [77.20, 28.61], [77.20, 28.60]]]
        }
        is_valid, gtype, bbox, err = validate_geometry(valid_poly)
        self.assertTrue(is_valid)
        self.assertEqual(gtype, "Polygon")
        self.assertEqual(bbox, [77.20, 28.60, 77.21, 28.61])

        valid_point = {"type": "Point", "coordinates": [77.209, 28.613]}
        is_valid, gtype, bbox, err = validate_geometry(valid_point)
        self.assertTrue(is_valid)
        self.assertEqual(gtype, "Point")

        is_valid, gtype, bbox, err = validate_geometry(None)
        self.assertFalse(is_valid)

    def test_ndvi_statistics_calculation(self):
        """Test spatial statistics calculations and health distributions"""
        ndvi_array = np.array([[0.7, 0.8], [0.4, 0.1]])
        stats = NDVIProcessor.compute_statistics(ndvi_array)
        
        self.assertEqual(stats["mean_ndvi"], 0.5)
        self.assertEqual(stats["max_ndvi"], 0.8)
        self.assertEqual(stats["min_ndvi"], 0.1)
        self.assertEqual(stats["healthy_percent"], 50.0)   # 0.7, 0.8 >= 0.60
        self.assertEqual(stats["moderate_percent"], 25.0)  # 0.4 in [0.30, 0.60)
        self.assertEqual(stats["low_ndvi_percent"], 25.0)  # 0.1 < 0.30

    def test_api_routes(self):
        """Test Flask blueprint REST endpoints"""
        res = self.client.get('/api/satellite/fields/field_test/ndvi?lat=28.6139&lng=77.2090')
        # Returns 200 (if demo/configured) or 530 (unconfigured error)
        self.assertIn(res.status_code, [200, 503])

        dashboard_res = self.client.get('/satellite/ndvi-dashboard')
        self.assertEqual(dashboard_res.status_code, 200)

if __name__ == '__main__':
    unittest.main()
