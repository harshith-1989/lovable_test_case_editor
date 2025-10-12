# 🧠 TCS Vulnerability Testcases API

A **secure, production-ready Flask + MongoDB REST API** for managing standardized vulnerability test cases (LLM / Web / Mobile / API platforms).

---

## 🚀 Features

- CRUD operations for vulnerability test cases
- Platform & validation enforcement (LLM, Web, Mobile, API)
- Automatic normalization of `"Automated"` field (`yes/no` → boolean)
- Unique index on `vuln_id`
- OpenAPI / Swagger UI (`/apidocs/`)
- Docker & Docker Compose setup
- Proper error handling and response codes
- Modular structure following Flask best practices

---

## 🗂️ Project Structure

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
│  └─ testcase_schema.py
├─ utils/
│  └─ db.py
├─ api/
│  └─ routes.py
└─ sample/
   └─ test_cases.json
```

---

## ⚙️ Environment Configuration (`.env.example`)

```bash
MONGO_URI=mongodb://mongo:27017
DB_NAME=tcs_vuln_db
COLLECTION_NAME=vuln_testcases
FLASK_ENV=production
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

Copy to `.env` and update as required.

---

## 🧩 Validation Rules

| Field | Type | Required | Description |
|-------|------|-----------|--------------|
| `vuln_id` | `string` | ✅ | Unique identifier (primary key) |
| `vuln_name` | `string` | ✅ | Vulnerability name |
| `platform` | `enum` | ✅ | One of `LLM`, `web`, `mobile`, `API` |
| `analysis_type` | `string` | ❌ | Type of analysis |
| `owasp_ref` | `string` | ❌ | OWASP reference |
| `compliance` | `string` | ❌ | Compliance framework |
| `vuln_abstract` | `string` | ❌ | Abstract/summary |
| `description` | `string` | ❌ | Detailed description |
| `recommendation` | `string` | ❌ | Mitigation steps |
| `example` | `string` | ❌ | Example payload |
| `cvss_score` | `float` | ❌ | 0.0 – 10.0 |
| `Automated` | `bool / "yes"/"no"` | ❌ | Normalized to boolean |

---

## 🐳 Docker & Compose Setup

### Build & Run

```bash
docker-compose up --build
```

### Initialize DB with Sample Data

```bash
docker-compose exec app python setup_db.py
```

### URLs

| Resource | URL |
|-----------|-----|
| API Base | http://localhost:5000/api/v1/test_cases |
| Swagger UI | http://localhost:5000/apidocs/ |
| Health Check | http://localhost:5000/health |

---

## ⚡ Local Setup (Without Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_db.py
python app.py
```

---

## 🧭 Endpoints Summary

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/api/v1/test_cases?platform=<platform>` | Read all or platform-specific test cases |
| `POST` | `/api/v1/test_cases` | Add single or multiple test cases |
| `PUT` | `/api/v1/test_cases` | Update one or multiple test cases |
| `DELETE` | `/api/v1/test_cases` | Delete one or multiple test cases |
| `GET` | `/health` | App + DB health check |

---

## 🧪 cURL Test Suite

All examples assume:  
`BASE_URL=http://localhost:5000/api/v1/test_cases`

---

### 🩺 1️⃣ Health Check

```bash
curl -X GET http://localhost:5000/health
```

✅ **Expected:**
```json
{"status":"ok"}
```

---

### 🔍 2️⃣ Read Test Cases

**Get all**
```bash
curl -X GET $BASE_URL
```

**Filter by platform**
```bash
curl -X GET "$BASE_URL?platform=LLM"
```

✅ **Expected:**
```json
{
  "test_cases": [
    {
      "_id": {"$oid": "670abcd..."},
      "vuln_id": "TCS_LLM_1",
      "vuln_name": "Prompt Injection",
      "platform": "LLM",
      "Automated": true
    }
  ]
}
```

---

### ➕ 3️⃣ Add Test Case(s)

**Single**
```bash
curl -X POST $BASE_URL   -H "Content-Type: application/json"   -d '{
    "vuln_id": "TCS_LLM_100",
    "vuln_name": "Prompt Injection",
    "platform": "LLM",
    "analysis_type": "Dynamic Analysis",
    "Automated": "yes"
  }'
```

✅ **Response:**
```json
{"inserted":1,"vuln_id":"TCS_LLM_100"}
```

**Multiple**
```bash
curl -X POST $BASE_URL   -H "Content-Type: application/json"   -d '{
    "test_cases": [
      {
        "vuln_id": "TCS_WEB_101",
        "vuln_name": "Cross-Site Scripting",
        "platform": "web",
        "Automated": "no"
      },
      {
        "vuln_id": "TCS_API_102",
        "vuln_name": "Broken Object Level Authorization",
        "platform": "API",
        "Automated": true
      }
    ]
  }'
```

✅ **Response:**
```json
{"inserted":2}
```

---

### 🛠️ 4️⃣ Update Test Case(s)

**Single**
```bash
curl -X PUT $BASE_URL   -H "Content-Type: application/json"   -d '{
    "vuln_id": "TCS_LLM_100",
    "recommendation": "Use robust input validation and prompt isolation.",
    "Automated": "no"
  }'
```

✅ **Response:**
```json
{"updated":1,"not_found":[]}
```

**Multiple**
```bash
curl -X PUT $BASE_URL   -H "Content-Type: application/json"   -d '{
    "test_cases": [
      {
        "vuln_id": "TCS_WEB_101",
        "cvss_score": 7.5,
        "Automated": true
      },
      {
        "vuln_id": "TCS_API_102",
        "recommendation": "Ensure API-level authorization checks are enforced."
      }
    ]
  }'
```

✅ **Response:**
```json
{"updated":2,"not_found":[]}
```

---

### 🗑️ 5️⃣ Delete Test Case(s)

**Multiple**
```bash
curl -X DELETE $BASE_URL   -H "Content-Type: application/json"   -d '{"vuln_ids": ["TCS_LLM_100", "TCS_WEB_101"]}'
```

✅ **Response:**
```json
{"deleted_count":2}
```

**Single**
```bash
curl -X DELETE $BASE_URL   -H "Content-Type: application/json"   -d '{"vuln_id": "TCS_API_102"}'
```

✅ **Response:**
```json
{"deleted_count":1}
```

---

### ⚠️ 6️⃣ Validation Tests

**Missing `vuln_id`**
```bash
curl -X POST $BASE_URL   -H "Content-Type: application/json"   -d '{"vuln_name": "Prompt Injection","platform": "LLM"}'
```

✅ **Response:**
```json
{"error":"Validation failed","message":"{'vuln_id': ['Missing data for required field.']}"}
```

**Invalid Platform**
```bash
curl -X POST $BASE_URL   -H "Content-Type: application/json"   -d '{"vuln_id":"TCS_XX_999","vuln_name":"Invalid platform test","platform":"Serverless"}'
```

✅ **Response:**
```json
{"error":"Validation failed","message":"{'platform': ['platform must be one of ['LLM', 'web', 'mobile', 'API']]'}"}
```

---

## 🔬 Quick Demo Loop

```bash
# Add
curl -X POST $BASE_URL -H "Content-Type: application/json"   -d '{"vuln_id":"TCS_LLM_DEMO","vuln_name":"Prompt Injection","platform":"LLM","Automated":"yes"}'

# Read
curl -X GET "$BASE_URL?platform=LLM"

# Update
curl -X PUT $BASE_URL -H "Content-Type: application/json"   -d '{"vuln_id":"TCS_LLM_DEMO","recommendation":"Updated from curl demo"}'

# Delete
curl -X DELETE $BASE_URL -H "Content-Type: application/json"   -d '{"vuln_id":"TCS_LLM_DEMO"}'
```

---

## 📘 Swagger / OpenAPI Docs

Visit the interactive documentation at:  
👉 **[http://localhost:5000/apidocs/](http://localhost:5000/apidocs/)**

You can run, inspect, and export API calls directly from the browser.

---

## 🛡️ Security & Production Notes

- **Never** expose MongoDB without authentication.
- Use environment variables or a secret manager for credentials.
- Run behind HTTPS / reverse proxy (Nginx / Traefik).
- Add rate-limiting (`Flask-Limiter`) & authentication (JWT or API key).
- Enable request logging and monitoring (Fluentd / ELK / CloudWatch).

---

## 🧰 Future Enhancements

- ✅ Unit & Integration Tests (pytest + mongomock)
- ✅ Role-Based Authentication (API Keys / JWT)
- ✅ CI/CD Pipeline (GitHub Actions / GitLab CI)
- ✅ Auto-generated OpenAPI 3.0 YAML
- ✅ Enhanced schema validation + field-level auditing

---

## 🧾 License
MIT © 2025 TCS Security Engineering Demo
