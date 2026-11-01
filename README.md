# IceStream: Real-Time Lakehouse Observability

## Overview

IceStream is a data-quality monitoring project that simulates observability for an e-commerce checkout data pipeline. It generates synthetic transactions, detects invalid records, quarantines data-quality failures, and simulates a circuit breaker that pauses downstream processing when the error rate reaches a configured threshold.

## Key Features

- Synthetic checkout transaction generation
- Required-field and data-type validation
- Detection of null tax amounts
- Detection of unexpected schema fields
- Quarantine of invalid transactions
- Configurable data-quality threshold
- Simulated pipeline pause and downstream processing decisions
- FastAPI backend and REST endpoints
- React and Vite monitoring dashboard
- Automated tests using pytest

## Technology Stack

- Python
- FastAPI
- React
- Vite
- pytest and unittest.mock
- Git and GitHub

## Project Structure

```text
IceStream/
├── src/
│   ├── api.py
│   ├── data_quality.py
│   ├── pipeline.py
│   └── transaction_generator.py
├── tests/
├── data/
│   └── quarantine.json
├── frontend/
├── README.md
└── .gitignore
```

## Run Locally

### 1. Activate the virtual environment

From the project root in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Start the backend

```powershell
python -m uvicorn src.api:app --reload --port 8000
```

The API is normally available at:

- API root: http://127.0.0.1:8000/
- Metrics: http://127.0.0.1:8000/api/metrics
- Quarantine: http://127.0.0.1:8000/api/quarantine

**Note:** Each request to `/api/metrics` generates a new synthetic transaction batch and may add new invalid records to the quarantine file. Avoid repeatedly refreshing this endpoint when you do not need new test data.

### 3. Run the tests

Open a second terminal in the project root, activate the virtual environment if needed, and run:

```powershell
python -m pytest
```

### 4. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite.

## Current Scope and Limitations

This project currently demonstrates synthetic transaction generation, data-quality validation, quarantine, API-based metrics, and simulated circuit-breaker decisions.

A fully integrated Kafka, Flink, and Apache Iceberg pipeline is not yet implemented. The current pipeline is a simulation rather than a production streaming lakehouse.

## Author

Rima Hait