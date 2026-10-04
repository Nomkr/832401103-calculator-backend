# Calculator Backend

Backend service for a front-end/back-end separated calculator system. It
handles expression parsing and evaluation, input validation, error
handling, and persistence of calculation history.

## Overview

- The Android client talks to this service over HTTP APIs. The client only
  renders input and responses; all arithmetic runs here.
- Expression evaluation uses a hand-written recursive descent parser.
  `eval`/`exec` are intentionally not used.
- Scientific operators are supported: `√` (square root), `x²` (square),
  `x^y` (power), `%` (percent).

## Tech Stack

| Item | Technology |
|---|---|
| Language | Python 3.13 |
| Web framework | Flask 3.1 |
| Database | SQLite (stdlib `sqlite3`) |

## Requirements

- Python 3.9+ (developed on 3.13)
- Dependencies listed in `requirements.txt` (Flask, gunicorn)

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

The server listens on `http://0.0.0.0:5000` so the emulator or a phone can
reach it. Verify with `GET /api/health`.

## Configuration

- Port defaults to `5000`; override with the `PORT` environment variable.
- The database file `calculator.db` is created next to the module on first
  run. Set `CALCULATOR_DB_FILE` to place it on a persistent disk when
  deploying.
- `FLASK_DEBUG=1` enables debug mode for development.

## Database

The table is created automatically on startup (idempotent):

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Primary key, auto-increment |
| expression | TEXT | The expression entered by the user |
| result | TEXT | The computed result |
| created_at | TEXT | Timestamp (`YYYY-MM-DD HH:MM:SS`) |

## API

| Method | Path | Description |
|---|---|---|
| POST | `/api/calculate` | Evaluate an expression and store it in history |
| GET | `/api/history` | List history, newest first |
| DELETE | `/api/history/<id>` | Delete one record |
| DELETE | `/api/history` | Clear all history |
| GET | `/api/health` | Health check |

Example request:

```json
POST /api/calculate
{ "expression": "1+2*3" }
```

Success response:

```json
{ "success": true, "expression": "1+2*3", "result": 7 }
```

Error response:

```json
{ "success": false, "message": "Division by zero" }
```

## Live Verification

The deployed service is available at `https://nomkr.pythonanywhere.com`.
Run these read-only and calculation checks before a demonstration:

```bash
curl https://nomkr.pythonanywhere.com/api/health
curl -X POST https://nomkr.pythonanywhere.com/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression":"(1+2)*3"}'
curl https://nomkr.pythonanywhere.com/api/history
```

The health endpoint should return `{"status":"ok"}`. A successful calculate
request returns `{"success":true,...,"result":9}` and creates one history
record, which can then be viewed by the history request or removed through
the delete API.

## Testing

```bash
python -m unittest discover -v
```

Covers parser precedence, parentheses, decimals, unary signs, scientific
operators, invalid input, division by zero, and the Flask API
(persistence, query, delete, error responses).

## Deployment

The submitted backend is deployed on PythonAnywhere at
`https://nomkr.pythonanywhere.com`. The health endpoint is
`/api/health`; it currently returns HTTP 200. PythonAnywhere's persistent
user filesystem keeps the SQLite history file across web-app reloads.

The repository also contains a `Dockerfile` and `render.yaml` for local
verification or an alternative Docker-capable host. See `DEPLOYMENT.md` for
the PythonAnywhere WSGI configuration and the Docker check commands. Use
HTTPS in production and place SQLite on persistent storage.

## Project Structure

```
calculator_backend/
├── app.py                  # Entry point and routes (controller layer)
├── calculator.py           # Expression parsing and evaluation (service layer)
├── database.py             # SQLite operations (data layer)
├── test_calculator.py      # Parser regression tests
├── test_app.py             # API contract tests
├── requirements.txt        # Dependencies
├── Dockerfile              # Production image
├── render.yaml             # Render blueprint
├── DEPLOYMENT.md           # Deployment guide
├── README.md               # This file
└── codestyle.md            # Code style (PEP 8)
```
