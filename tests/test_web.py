import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from tests.test_agent import FakeTemanUmkmClient


class WebTest(unittest.TestCase):
    def setUp(self) -> None:
        app = create_app(client_factory=FakeTemanUmkmClient, auto_login=False)
        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_chat_adds_items_to_session_cart(self) -> None:
        response = self.client.post(
            "/chat",
            json={"session_id": "kasir-1", "message": "beli kopi dan gula"},
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["session_id"], "kasir-1")
        self.assertIn("- Kopi x1", body["reply"])
        self.assertIn("- Gula x1", body["reply"])

        cart_response = self.client.post(
            "/chat",
            json={"session_id": "kasir-1", "message": "cart"},
        )

        self.assertEqual(cart_response.status_code, 200)
        self.assertIn("- Kopi x1", cart_response.json()["reply"])
        self.assertIn("- Gula x1", cart_response.json()["reply"])

    def test_chat_keeps_sessions_separate(self) -> None:
        self.client.post(
            "/chat",
            json={"session_id": "kasir-1", "message": "beli kopi"},
        )

        response = self.client.post(
            "/chat",
            json={"session_id": "kasir-2", "message": "cart"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["reply"], "AI: Cart masih kosong.")

    def test_chat_validates_empty_message(self) -> None:
        response = self.client.post(
            "/chat",
            json={"session_id": "kasir-1", "message": ""},
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
