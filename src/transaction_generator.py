import random
from datetime import datetime, timezone


def generate_transaction(order_id: int) -> dict:
    """Generate one checkout transaction with occasional bad data."""

    transaction = {
        "order_id": order_id,
        "product": random.choice(
            ["Laptop", "Phone", "Headphones", "Monitor"]
        ),
        "sales_amount": round(random.uniform(100, 5000), 2),
        "tax_amount": round(random.uniform(5, 500), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Deliberately inject data-quality errors.
    error = random.random()

    if error < 0.05:
        transaction["tax_amount"] = None
    elif error < 0.07:
        transaction["unexpected_field"] = "SCHEMA_CHANGE"

    return transaction


def generate_transactions(count: int = 100) -> list[dict]:
    """Generate a batch of checkout transactions."""

    return [
        generate_transaction(order_id)
        for order_id in range(1, count + 1)
    ]


if __name__ == "__main__":
    transactions = generate_transactions(20)

    for transaction in transactions:
        print(transaction)

    print(f"\nTotal transactions generated: {len(transactions)}")