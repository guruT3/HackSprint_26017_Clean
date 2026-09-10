import unittest
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Flask
from farmer_collaboration.services import CollaborationService
from farmer_collaboration.routes import farmer_collaboration_bp, init_farmer_collaboration

class TestFarmerCollaboration(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = "test_secret_key"
        init_farmer_collaboration(self.app)
        self.client = self.app.test_client()

    def test_global_search(self):
        """Test global search across products, posts, farmers, and mandis."""
        results = CollaborationService.global_search("Paddy")
        self.assertGreater(results["total_results"], 0)
        self.assertGreater(len(results["listings"]), 0)

    def test_rule_based_ai_recommendation(self):
        """Test matching engine scores based on category, district, and quantity."""
        req = {"category": "Seeds", "location": "Bargarh, Odisha", "quantity": 100}
        matches = CollaborationService.match_requirement_with_sellers(req)
        self.assertIsInstance(matches, list)
        if len(matches) > 0:
            self.assertGreaterEqual(matches[0]["match_score"], 40)

    def test_blueprint_routes(self):
        """Test Flask blueprint HTTP GET endpoints."""
        endpoints = [
            '/farmer-connect',
            '/farmer-connect/community',
            '/farmer-connect/marketplace',
            '/farmer-connect/requirements',
            '/farmer-connect/mandi',
            '/farmer-connect/notifications',
            '/farmer-connect/admin'
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Failed on endpoint: {ep}")

if __name__ == '__main__':
    unittest.main()
