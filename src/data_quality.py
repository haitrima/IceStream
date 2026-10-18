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