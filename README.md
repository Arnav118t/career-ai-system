# Running the project (backend + frontend)

## Prerequisites
- Python 3.14+
- Node.js + npm

## 1) Start the backend (FastAPI)
From the project root:

```bash
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **API**: `http://127.0.0.1:8000`
- **Swagger docs**: `http://127.0.0.1:8000/docs`

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
