import json
from pathlib import Path

QUARANTINE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "quarantine.json"
)
def save_quarantined_records(records):
    """Save quarantined records without duplicating identical entries."""
    QUARANTINE_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing_records = []

    if QUARANTINE_FILE.exists():
        with QUARANTINE_FILE.open("r", encoding="utf-8") as file:
            existing_records = json.load(file)

    existing_keys = {
        json.dumps(item, sort_keys=True, default=str)
        for item in existing_records
    }

    for record in records:
        record_key = json.dumps(record, sort_keys=True, default=str)

        if record_key not in existing_keys:
            existing_records.append(record)
            existing_keys.add(record_key)

    with QUARANTINE_FILE.open("w", encoding="utf-8") as file:
        json.dump(existing_records, file, indent=4, default=str)



REQUIRED_FIELDS = {
    "order_id",
    "product",
    "sales_amount",
    "tax_amount",
    "timestamp",
}


def validate_transaction(transaction):
    """Return a list of data-quality problems."""
    errors = []

    # Check required fields.
    for field in REQUIRED_FIELDS:
        if field not in transaction:
            errors.append(f"Missing required field: {field}")

    # Check for missing tax amount.
    if "tax_amount" in transaction and transaction["tax_amount"] is None:
        errors.append("Tax amount is null")

        # Check that sales amount is numeric and non-negative.
    if "sales_amount" in transaction:
        sales = transaction["sales_amount"]

        if (
            isinstance(sales, bool)
            or not isinstance(sales, (int, float))
        ):
            errors.append("Sales amount must be numeric")
        elif sales < 0:
            errors.append("Sales amount cannot be negative")

    # Check that tax amount is numeric and non-negative.
    if "tax_amount" in transaction and transaction["tax_amount"] is not None:
        tax = transaction["tax_amount"]

        if (
            isinstance(tax, bool)
            or not isinstance(tax, (int, float))
        ):
            errors.append("Tax amount must be numeric")
        elif tax < 0:
            errors.append("Tax amount cannot be negative")

    # Check for unexpected fields.
    unexpected = set(transaction.keys()) - REQUIRED_FIELDS
    if unexpected:
        errors.append(
            f"Unexpected fields: {', '.join(sorted(unexpected))}"
        )

    return errors


def process_transactions(transactions, threshold=0.02):
    """Validate transactions and quarantine invalid records."""
    valid_records = []
    quarantined_records = []

    for transaction in transactions:
        errors = validate_transaction(transaction)

        if errors:
            quarantined_records.append({
                "record": transaction,
                "errors": errors,
            })
        else:
            valid_records.append(transaction)

    total = len(transactions)
    error_count = len(quarantined_records)
    error_rate = error_count / total if total else 0.0

    if quarantined_records:
        save_quarantined_records(quarantined_records)

    return {
        "total": total,
        "valid_count": len(valid_records),
        "error_count": error_count,
        "error_rate": error_rate,
        "circuit_breaker_triggered": (
            total > 0 and error_rate >= threshold
        ),
        "valid_records": valid_records,
        "quarantined_records": quarantined_records,
    }