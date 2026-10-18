from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.transaction_generator import generate_transactions
from src.pipeline import run_pipeline

app = FastAPI(title="IceStream Observability API")

# Allow the local React development server to access this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "IceStream",
        "message": "Observability API is running",
    }


@app.get("/api/metrics")
def get_metrics():
    # Generate a repeatable sample batch for this dashboard request.
    transactions = generate_transactions(100)
    pipeline_result = run_pipeline(transactions)
    result = pipeline_result["metrics"]

    return {
        "total_transactions": result["total"],
        "valid_transactions": result["valid_count"],
        "quality_errors": result["error_count"],
        "error_rate_percent": round(result["error_rate"] * 100, 2),
        "quarantined_records": result["error_count"],
        "circuit_breaker_triggered": result["circuit_breaker_triggered"],
        "pipeline_status": pipeline_result["status"],
        "downstream_processed": pipeline_result["downstream_processed"],
        "pipeline_reason": pipeline_result["reason"],
        "threshold_percent": 2,
    }