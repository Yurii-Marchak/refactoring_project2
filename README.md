# SubOptima Platform

![CI](https://github.com/Yurii-Marchak/refactoring_project2/actions/workflows/ci-pipeline.yml/badge.svg)
![CD](https://github.com/Yurii-Marchak/refactoring_project2/actions/workflows/deploy.yml/badge.svg)
![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=Yurii-Marchak_refactoring_project2&metric=alert_status)
![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Yurii-Marchak_refactoring_project2&metric=coverage)

Educational subscription optimization project built with `FastAPI`, `MongoDB`, and a `Jinja2` frontend. The platform supports service cataloging, subscription management, user feedback collection, and intelligent analytics using Fuzzy Logic to generate cost-saving recommendations.

## Highlights
- Hexagonal Architecture (Ports and Adapters)
- Two storage modes: `in_memory` (for fast CI testing) and `mongodb` (production)
- Intelligent analytics using Fuzzy Logic (Utility Score calculation)
- Service catalog and user subscription lifecycle management
- Interactive Web UI with Chart.js visualizations
- Comprehensive Unit, Integration, and Edge Case testing
- GitHub Actions CI/CD with automatic SonarCloud analysis

## Stack
- Python 3.11
- FastAPI
- MongoDB / PyMongo
- Pydantic v2
- Jinja2 + Bootstrap 5 + Chart.js
- Pytest + pytest-cov + mongomock
- GitHub Actions
- SonarQube / SonarCloud ready pipeline

## Repository Structure
```text
src/
  models/
  routers/
  schemas/
  services/
    ports/
    use_cases/
  storage/
    in_memory/
    mongodb/
  templates/
  static/
tests/
  api/
  models/
  storage/
  use_cases/
  utils/
docs/
  diagrams/
  spec/
.github/workflows/

## Local Backend Run

PowerShell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn src.main:app --reload
Example local database URL (if using MongoDB mode):

Фрагмент коду
STORAGE_TYPE=mongodb
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=suboptima_db
Swagger API Documentation:

http://127.0.0.1:8000/docs

Web Interface:

http://127.0.0.1:8000/web/

Testing and Reports
Run tests with XML and HTML coverage output:

PowerShell
pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html --junitxml=pytest-report.xml tests/
Generated outputs:

coverage.xml

pytest-report.xml

htmlcov/

CI uploads these artifacts after every commit so they can be downloaded from the workflow run.

SonarQube / SonarCloud
The repository is configured for SonarCloud. The CI pipeline includes steps to upload coverage reports and evaluate the Quality Gate.
To enable Sonar in GitHub Actions, the following secrets are configured:

SONAR_TOKEN

SONAR_HOST_URL (set to https://sonarcloud.io)

Documentation
Requirements

Architecture

Database

API

Frontend Guide

Deployment

Testing

Quality

Security Notes
Pydantic V2 request validation

Strict domain isolation (DTOs vs Domain Models)

Environment-based configuration (Storage types toggle)

Secure cookie transmission configuration for Web UI

Architecture Notes
The codebase explicitly uses:

Hexagonal Architecture (Ports and Adapters) for persistence isolation

Dependency Injection (FastAPI Depends) for injecting repositories into Use Cases

Strategy/Factory pattern for Database environment switching

Quality Goals
Coverage target: 80%+ (Currently 120+ tests)

Expanded unit and integration suite for edge cases and Fuzzy Logic math validation

XML and HTML reports in CI artifacts

Sonar Quality Gate support in pipeline