import unittest

from src.transaction_generator import (
    generate_transaction,
    generate_transactions,
)


class TestTransactionGenerator(unittest.TestCase):

    def test_generates_requested_number(self):
        transactions = generate_transactions(20)
        self.assertEqual(len(transactions), 20)

    def test_required_fields_exist(self):
        transaction = generate_transaction(1)

        required_fields = {
            "order_id",
            "product",
            "sales_amount",
            "tax_amount",
            "timestamp",
        }

        self.assertTrue(required_fields.issubset(transaction.keys()))

    def test_sales_amount_is_positive(self):
        transaction = generate_transaction(1)

        self.assertGreater(transaction["sales_amount"], 0)

    def test_order_id_is_preserved(self):
        transaction = generate_transaction(123)

        self.assertEqual(transaction["order_id"], 123)

    def test_generated_amounts_are_non_negative(self):
        transactions = generate_transactions(100)

        for transaction in transactions:
            self.assertGreater(transaction["sales_amount"], 0)

            if transaction["tax_amount"] is not None:
                self.assertGreater(transaction["tax_amount"], 0)

if __name__ == "__main__":
    unittest.main()