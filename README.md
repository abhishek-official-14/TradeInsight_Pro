# TradeInsight Pro - Production SaaS Stack

TradeInsight Pro ships as a full-stack SaaS template:
- **Backend**: FastAPI + SQLAlchemy + Celery
- **Frontend**: React + Vite
- **Infra**: PostgreSQL + Redis + Docker Compose
- **Deployment Targets**: Railway (backend) + Vercel (frontend)

## 1) Project Structure

```text
.
├── backend/
│   ├── app/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── .env.example
├── docker-compose.yml
└── .env.example
```

## 2) Local Setup Guide

### Prerequisites
- Docker + Docker Compose
- (Optional) Python 3.12 and Node 20 for non-container development

### Quick Start (all services)

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

Services:
- Frontend: `http://localhost:4173`
- Backend API: `http://localhost:8000`
- Backend health check: `http://localhost:8000/health`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

## 3) Backend (FastAPI + Celery)

### Production behavior already included
- Centralized settings via `pydantic-settings`
- Structured access logging middleware
- Error handling middleware
- Token + subscription middleware
- Celery worker + beat services connected to Redis

### Environment variables (backend)
Use `backend/.env` and keep all required values populated:

```env
APP_NAME=TradeInsight Pro
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://<user>:<password>@<host>:5432/<db>
REDIS_URL=redis://<host>:6379/0
JWT_SECRET_KEY=<32+ char random secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CELERY_BROKER_URL=redis://<host>:6379/1
CELERY_RESULT_BACKEND=redis://<host>:6379/2
RAZORPAY_KEY_ID=<key id>
RAZORPAY_KEY_SECRET=<secret>
RAZORPAY_WEBHOOK_SECRET=<webhook secret>
SUBSCRIPTION_DURATION_DAYS=30
TELEGRAM_BOT_TOKEN=<optional>
TELEGRAM_CHAT_ID=<optional>
```

## 4) Frontend (React + Vite)

### Required environment
Set in `frontend/.env`:

```env
VITE_APP_NAME=TradeInsight Pro
VITE_API_BASE_URL=https://<backend-domain>/api/v1
```

## 5) Railway Deployment (Backend)

1. Create a new Railway project for `backend/`.
2. Add PostgreSQL and Redis plugins/services in Railway.
3. Set backend service root directory to `backend`.
4. Railway start command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Add all environment variables from `backend/.env.example`.
6. Replace local service URLs with Railway URLs:
   - `DATABASE_URL` from Railway Postgres
   - `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` from Railway Redis
7. Deploy and verify:
   - `GET /health` returns `{"status":"ok"}`

> For Celery in production, deploy additional Railway services from the same repo with commands:
- Worker: `celery -A app.tasks.celery_app.celery_app worker --loglevel=info`
- Beat: `celery -A app.tasks.celery_app.celery_app beat --loglevel=info`

## 6) Vercel Deployment (Frontend)

1. Import this repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Build command: `npm run build`.
4. Output directory: `dist`.
5. Add environment variable:
   - `VITE_API_BASE_URL=https://<railway-backend-domain>/api/v1`
6. Deploy.

The included `frontend/vercel.json` rewrites all routes to `index.html` for React Router.

## 7) Docker Notes

- Root `docker-compose.yml` orchestrates frontend, backend, worker, beat, postgres, and redis.
- `backend/docker-compose.yml` remains available for backend-only workflows.
- Frontend image is an optimized multi-stage build served by Nginx.

## 8) Sample .env files

- Root sample: `.env.example`
- Backend sample: `backend/.env.example`
- Frontend sample: `frontend/.env.example`

Copy and adjust all three before local or cloud deployment.
