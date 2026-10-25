from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.transaction_generator import generate_transactions
from src.pipeline import run_pipeline

import json
from pathlib import Path

app = FastAPI(title="IceStream Observability API")

QUARANTINE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "quarantine.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
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

@app.get("/api/quarantine")
def get_quarantine_records():
    if not QUARANTINE_FILE.exists():
        return {
            "total_records": 0,
            "records": [],
        }

    try:
        with QUARANTINE_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except (json.JSONDecodeError, OSError):
        return {
            "total_records": 0,
            "records": [],
            "error": "Unable to read quarantine records.",
        }

    return {
        "total_records": len(records),
        "records": records,
    }