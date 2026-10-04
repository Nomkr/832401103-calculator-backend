"""Small HTTP contract tests for the Flask API."""

import os
import tempfile
import unittest
from unittest.mock import patch

import database
from app import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.old_db_file = database.DB_FILE
        self.temp_dir = tempfile.TemporaryDirectory()
        database.DB_FILE = os.path.join(self.temp_dir.name, "test.db")
        database.init_db()
        self.client = app.test_client()

    def tearDown(self):
        database.DB_FILE = self.old_db_file
        self.temp_dir.cleanup()

    def test_calculate_persists_and_can_delete(self):
        response = self.client.post("/api/calculate", json={"expression": "2+3*4"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"], 14)

        history = self.client.get("/api/history").get_json()["history"]
        self.assertEqual(len(history), 1)
        history_id = history[0]["id"]

        self.assertEqual(self.client.delete(f"/api/history/{history_id}").status_code, 200)
        self.assertEqual(self.client.get("/api/history").get_json()["history"], [])
        self.assertEqual(self.client.delete("/api/history/999").status_code, 404)

    def test_health_and_clear_history(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

        self.client.post("/api/calculate", json={"expression": "1+1"})
        response = self.client.delete("/api/history")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])
        self.assertEqual(self.client.get("/api/history").get_json()["history"], [])

    def test_unknown_api_returns_json(self):
        response = self.client.get("/api/does-not-exist")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.get_json()["success"])

    def test_unicode_operators_are_supported(self):
        response = self.client.post("/api/calculate", json={"expression": "6÷2×3"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["result"], 9)

    def test_unexpected_api_error_is_json(self):
        with patch.object(database, "add_history", side_effect=RuntimeError("disk error")):
            response = self.client.post("/api/calculate", json={"expression": "1+1"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.get_json()["message"], "Internal server error")

    def test_bad_request_is_json(self):
        response = self.client.post("/api/calculate", json={"expression": 3})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.get_json()["success"])

    def test_invalid_expression_is_client_error(self):
        for expression in ("*2", "/2", "1+"):
            with self.subTest(expression=expression):
                response = self.client.post(
                    "/api/calculate", json={"expression": expression}
                )
                self.assertEqual(response.status_code, 400)
                self.assertFalse(response.get_json()["success"])


if __name__ == "__main__":
    unittest.main()
