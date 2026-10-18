from src.data_quality import process_transactions


def run_pipeline(transactions, threshold=0.02):
    """Validate transactions and pause downstream processing on poor quality."""

    result = process_transactions(
        transactions,
        threshold=threshold,
    )
    
    if not transactions:
        return {
            "status": "PAUSED",
            "reason": "No transactions available to process.",
            "downstream_processed": False,
            "metrics": result,
        }

    if result["circuit_breaker_triggered"]:
        return {
            "status": "PAUSED",
            "reason": (
                f"Data-quality error rate "
                f"{result['error_rate'] * 100:.2f}% "
                f"reached the {threshold * 100:.2f}% threshold."
            ),
            "downstream_processed": False,
            "metrics": result,
        }

    return {
        "status": "RUNNING",
        "reason": "Data quality is within the permitted threshold.",
        "downstream_processed": True,
        "metrics": result,
    }