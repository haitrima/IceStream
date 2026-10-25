import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


class TestAPI(unittest.TestCase):

    @patch("src.api.generate_transactions")
    def test_metrics_endpoint_returns_expected_fields(
        self, mock_generate
    ):
        mock_generate.return_value = [
            {
                "order_id": 1,
                "product": "Laptop",
                "sales_amount": 1200.00,
                "tax_amount": 120.00,
                "timestamp": "2026-10-16T10:00:00+00:00",
            }
        ]

        response = client.get("/api/metrics")

        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("total_transactions", data)
        self.assertIn("valid_transactions", data)
        self.assertIn("quality_errors", data)
        self.assertIn("pipeline_status", data)
        self.assertIn("error_rate_percent", data)
        self.assertIn("circuit_breaker_triggered", data)

    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_returns_records(self, mock_file):
        mock_file.exists.return_value = False

        response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"total_records": 0, "records": []},
        )
    
    @patch("src.api.QUARANTINE_FILE")
    def test_quarantine_endpoint_returns_records(self, mock_file):
        mock_file.exists.return_value = True
        mock_file.open.return_value.__enter__.return_value.read.return_value = "[]"

        with patch("builtins.open", unittest.mock.mock_open(read_data="[]")):
            response = client.get("/api/quarantine")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("total_records", data)
        self.assertIn("records", data)

if __name__ == "__main__":
    unittest.main()