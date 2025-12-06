import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestTripsRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_trip_history(self):
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/trips/history", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == "__main__":
    unittest.main()