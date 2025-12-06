import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestDashboardRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_dashboard_stats(self):
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/dashboard/stats", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("trips", response.json())

if __name__ == "__main__":
    unittest.main()