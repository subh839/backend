import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestCarsRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_add_car(self):
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post("/cars/", json={
            "make": "Tesla",
            "model": "Model S",
            "year": 2022
        }, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

if __name__ == "__main__":
    unittest.main()