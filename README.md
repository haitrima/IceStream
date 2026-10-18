IceStream: Real-Time Lakehouse Observability

Overview

IceStream is a data-quality monitoring project designed to detect invalid records in an e-commerce checkout data pipeline. It identifies missing tax amounts and unexpected schema fields, quarantines invalid transactions, and simulates a circuit breaker that pauses downstream processing when the error rate reaches a configured threshold.

Key Features

Synthetic checkout transaction generation

Data-quality validation

Detection of null tax amounts

Detection of unexpected schema fields

Quarantine of invalid records

Configurable error-rate threshold

Simulated pipeline pause and resume decision

FastAPI backend

React and Vite frontend

Automated unit tests

Technology Stack

Python

FastAPI

React

Vite

Git and GitHub

Python unittest

Project Structure

src/ — transaction generation, validation, pipeline logic, and API

tests/ — automated tests

frontend/ — web dashboard

.gitignore — excludes unnecessary and sensitive files

Run Locally

1. Start the backend

From the project root, activate your Python virtual environment and run:
python -m uvicorn src.api:app --reload 
The API will normally be available at http://127.0.0.1:8000.

2. Run the tests

From the project root:
python -m unittest discover -s tests -v 

3. Start the frontend

Open a second terminal:
cd frontend npm install npm run dev 
Open the local URL displayed by Vite in your terminal.

Current Scope

The project currently demonstrates synthetic transaction generation, validation, quarantine, and simulated circuit-breaker decisions. A fully integrated Kafka, Flink, and Apache Iceberg pipeline is not yet implemented.

Author

Rima Hait
