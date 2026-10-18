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

if __name__ == "__main__":
    unittest.main()