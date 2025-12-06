import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestSuggestionsRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_get_suggestions(self):
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/suggestions", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

if __name__ == "__main__":
    unittest.main()