import unittest

from src.pipeline import run_pipeline


def make_transaction(order_id):
    return {
        "order_id": order_id,
        "product": "Laptop",
        "sales_amount": 1200.00,
        "tax_amount": 120.00,
        "timestamp": "2026-10-16T10:00:00+00:00",
    }


class TestPipeline(unittest.TestCase):

    def test_pipeline_runs_below_threshold(self):
        transactions = [
            make_transaction(i) for i in range(1, 101)
        ]
        transactions[0]["tax_amount"] = None

        result = run_pipeline(transactions)

        self.assertEqual(result["status"], "RUNNING")
        self.assertTrue(result["downstream_processed"])

    def test_pipeline_pauses_at_threshold(self):
        transactions = [
            make_transaction(i) for i in range(1, 101)
        ]
        transactions[0]["tax_amount"] = None
        transactions[1]["tax_amount"] = None

        result = run_pipeline(transactions)

        self.assertEqual(result["status"], "PAUSED")
        self.assertFalse(result["downstream_processed"])

    def test_pipeline_pauses_above_threshold(self):
        transactions = [
            make_transaction(i) for i in range(1, 101)
        ]
        for i in range(3):
            transactions[i]["tax_amount"] = None

        result = run_pipeline(transactions)

        self.assertEqual(result["status"], "PAUSED")
        self.assertFalse(result["downstream_processed"])
        self.assertIn("2.00%", result["reason"])
    def test_pipeline_uses_custom_threshold(self):
        transactions = [
            make_transaction(i) for i in range(1, 101)
        ]

        for i in range(5):
            transactions[i]["tax_amount"] = None

        result = run_pipeline(transactions, threshold=0.10)

        self.assertEqual(result["status"], "RUNNING")
        self.assertFalse(result["metrics"]["circuit_breaker_triggered"])
    
        if __name__ == "__main__":
           unittest.main()