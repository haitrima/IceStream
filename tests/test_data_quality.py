import unittest

from src.data_quality import (
    validate_transaction,
    process_transactions,
)


def make_transaction(order_id=1):
    return {
        "order_id": order_id,
        "product": "Laptop",
        "sales_amount": 1200.00,
        "tax_amount": 120.00,
        "timestamp": "2026-10-16T10:00:00+00:00",
    }


class TestDataQuality(unittest.TestCase):

    def test_valid_transaction_passes(self):
        transaction = make_transaction()
        self.assertEqual(validate_transaction(transaction), [])

    def test_null_tax_amount_is_detected(self):
        transaction = make_transaction()
        transaction["tax_amount"] = None

        errors = validate_transaction(transaction)
        self.assertIn("Tax amount is null", errors)

    def test_unexpected_field_is_detected(self):
        transaction = make_transaction()
        transaction["unexpected_field"] = "SCHEMA_CHANGE"

        errors = validate_transaction(transaction)
        self.assertTrue(
            any("Unexpected fields" in error for error in errors)
        )

    def test_invalid_record_is_quarantined(self):
        transactions = [
            make_transaction(1),
            {**make_transaction(2), "tax_amount": None},
        ]

        result = process_transactions(transactions)

        self.assertEqual(result["valid_count"], 1)
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(len(result["quarantined_records"]), 1)
    
    def test_below_two_percent_threshold(self):
        transactions = [
            make_transaction(i)
            for i in range(1, 101)
        ]
        transactions[0]["tax_amount"] = None

        result = process_transactions(transactions)

        self.assertEqual(result["error_rate"], 0.01)
        self.assertFalse(result["circuit_breaker_triggered"])    

    def test_two_percent_threshold(self):
        transactions = [
            make_transaction(i)
            for i in range(1, 101)
        ]
        transactions[0]["tax_amount"] = None
        transactions[1]["tax_amount"] = None

        result = process_transactions(transactions)

        self.assertEqual(result["error_rate"], 0.02)
        self.assertTrue(result["circuit_breaker_triggered"])

    def test_above_two_percent_threshold(self):
        transactions = [
            make_transaction(i)
            for i in range(1, 101)
        ]

        for i in range(3):
            transactions[i]["tax_amount"] = None

        result = process_transactions(transactions)

        self.assertEqual(result["error_rate"], 0.03)
        self.assertTrue(result["circuit_breaker_triggered"])

if __name__ == "__main__":
    unittest.main()