# TCS Vulnerability Testcases API

Flask + MongoDB REST API for managing vulnerability test cases.

## Features
- CRUD endpoints for `test_cases` collection (platform-filtered reads).
- Validation via `marshmallow` (platform enum, cvss range, Automated normalization).
- Swagger/OpenAPI docs (Flasgger) at `/apidocs/`.
- Docker + docker-compose for local deployment.
- Unique index on `vuln_id`.

## Project structure
```
tcs-vuln-api/
├─ app.py
├─ setup_db.py
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ .env.example
├─ README.md
├─ schemas/
│  ├─ __init__.py
│  └─ testcase_schema.py
├─ utils/
│  ├─ __init__.py
│  └─ db.py
├─ api/
│  ├─ __init__.py
│  └─ routes.py
└─ sample/
   └─ test_cases.json  
```

## Setup (local, without Docker)
1. Copy `.env.example` -> `.env` and set values (or set env vars directly).
2. Create a Python venv and install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
3. Ensure MongoDB is running and accessible via MONGO_URI.
4. Create indexes & optionally load sample:
```bash
python setup_db.py
```
5.Run app:
```bash
python app.py
```
Visit Swagger UI at: http://localhost:5000/apidocs/

## Setup with Docker (recommended for quick local testing)
```bash
docker-compose up --build
```

## Wait for services to become healthy
```bash
docker-compose exec app python setup_db.py
```

App will be available at http://localhost:5000. 
Swagger UI: http://localhost:5000/apidocs/.

## Endpoints
```
1. GET /api/v1/test_cases?platform=<platform> — list testcases (platform optional)
2. POST /api/v1/test_cases — add one or many testcases
3. PUT /api/v1/test_cases — update one or many (partial updates)
4. DELETE /api/v1/test_cases — delete by vuln_ids
```
## Payload examples

Add multiple:
```
{
  "test_cases": [
    {"vuln_id":"TCS_LLM_1","vuln_name":"Prompt Injection","platform":"LLM","Automated":"yes"},
    {"vuln_id":"TCS_WEB_1","vuln_name":"XSS","platform":"web","Automated": false}
  ]
}
```

Update:
```
{
  "vuln_id": "TCS_LLM_1",
  "recommendation": "Use robust input validation"
}
```

Delete:
```
{"vuln_ids": ["TCS_LLM_1","TCS_WEB_1"]}
```

## Validation rules
```
vuln_id (string) — REQUIRED and unique

vuln_name (string) — REQUIRED

platform — REQUIRED, one of: LLM, web, mobile, API (case-insensitive)

Automated — optional; accepts boolean or "yes"/"no" strings (normalized to boolean in DB)

cvss_score — optional numeric 0.0 — 10.0
```

## Security / production notes

```
Do NOT expose MongoDB without authentication in production.

Add API authentication (API keys / JWT), rate-limiting, request size limits.

Use a secrets manager for DB URIs and credentials.

Add HTTPS (reverse proxy) and logging/monitoring.

Next improvements

Add unit + integration tests (pytest + mongomock)

Add role-based auth and rate-limiting

Add CI pipeline and container scanning
```