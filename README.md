# Running the project (backend + frontend)

## Prerequisites
- Python 3.11+
- Node.js + npm

## 1) Start the backend (FastAPI)
From the project root:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(32))"
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **API**: `http://127.0.0.1:8000`
- **Swagger docs**: `http://127.0.0.1:8000/docs`
- In production, set a persistent `SECRET_KEY` of at least 32 characters and configure `CORS_ORIGINS` to the frontend's exact origin(s). Development generates a temporary signing key if none is set; tokens are invalidated when the backend restarts.

## 2) Start the frontend (React)
In a new terminal:

```bash
cd frontend
npm install
npm start
```

- **UI**: `http://localhost:3000`

## Notes / Troubleshooting
- The frontend dev server proxies `/api/*` to `http://localhost:8000` (see `frontend/package.json`), so the backend must run on **port 8000**.
- If you changed ports, set `REACT_APP_API_URL` before starting the frontend (example):

```bash
set REACT_APP_API_URL=http://127.0.0.1:8000/api
npm start
```

## 3) Run backend tests

```powershell
python -m unittest discover -s tests -v
```

## Project behavior and limitations

- Offers and resumes are private to the authenticated user. Resume uploads accept text-based PDFs up to 5 MB.
- The recommendation engine is a **hybrid prototype**: the satisfaction score uses the bundled trained regression model; salary growth, workload, savings, and switching estimates use explicit rules. Skill matching uses extracted skill overlap and TF-IDF text similarity when a resume is available.
- The bundled dataset and model are for demonstration and evaluation, not a guarantee of real-world career or salary outcomes. Review the project documentation before presenting model results.
- Register your own account in the UI. No demo user is seeded automatically.
