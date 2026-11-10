from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.transaction_generator import generate_transactions
from src.pipeline import run_pipeline

import json
import os
from datetime import datetime
from pathlib import Path

app = FastAPI(title="IceStream Observability API")

QUARANTINE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "quarantine.json"
)

ERROR_HISTORY_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "error_history.json"
)

TEMP_ERROR_HISTORY_FILE = ERROR_HISTORY_FILE.with_suffix(".tmp")

def save_error_history(error_rate_percent):
    ERROR_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    if ERROR_HISTORY_FILE.exists():
        try:
            with ERROR_HISTORY_FILE.open("r", encoding="utf-8") as file:
                history = json.load(file)
        except (json.JSONDecodeError, OSError):
            return
    else:
        history = []

    if not isinstance(history, list):
        return

    history.append({
        "timestamp": datetime.now().astimezone().isoformat(),
        "error_rate_percent": error_rate_percent,
    })

    with TEMP_ERROR_HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=4)
        file.flush()
        os.fsync(file.fileno())

    os.replace(TEMP_ERROR_HISTORY_FILE, ERROR_HISTORY_FILE)

def get_quarantine_count():
    if not QUARANTINE_FILE.exists():
        return 0

    try:
        with QUARANTINE_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)

        return len(records) if isinstance(records, list) else 0

    except (json.JSONDecodeError, OSError):
        return 0

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
    error_rate_percent = round(result["error_rate"] * 100, 2)
    save_error_history(error_rate_percent)


    return {
        "total_transactions": result["total"],
        "valid_transactions": result["valid_count"],
        "quality_errors": result["error_count"],
        "error_rate_percent": error_rate_percent,
        "quarantined_records": get_quarantine_count(),
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
    if not isinstance(records, list):
        return {
            "total_records": 0,
            "records": [],
        }

    return {
        "total_records": len(records),
        "records": records,
    }

@app.get("/api/error-history")
def get_error_history():
    if not ERROR_HISTORY_FILE.exists():
        return {
            "total_records": 0,
            "history": [],
        }

    try:
        with ERROR_HISTORY_FILE.open("r", encoding="utf-8") as file:
            history = json.load(file)
    except (json.JSONDecodeError, OSError):
        return {
            "total_records": 0,
            "history": [],
            "error": "Unable to read error history.",
        }

    if not isinstance(history, list):
        return {
            "total_records": 0,
            "history": [],
        }

    return {
        "total_records": len(history),
        "history": history,
    }