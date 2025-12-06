import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestAuthRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_register_user(self):
        response = self.client.post("/auth/register", json={
            "email": "testuser@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertIn("user_id", response.json())

    def test_login_user(self):
        # Assuming the user is already registered
        response = self.client.post("/auth/login", data={
            "username": "testuser@example.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())
        self.assertIn("token_type", response.json())

    def test_get_current_user(self):
        # Assuming the user is logged in and we have a valid token
        token = "example_valid_token"
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("/auth/me", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.json())
        self.assertIn("is_active", response.json())

if __name__ == "__main__":
    unittest.main()