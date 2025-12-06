import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestStationsRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_nearby_stations(self):
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/stations/nearby?latitude=37.7749&longitude=-122.4194", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == "__main__":
    unittest.main()