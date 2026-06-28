# TalentFlow API (FastAPI + PostgreSQL)

A clean, modular FastAPI backend built to match the existing TalentFlow
frontend's API contract exactly (see `src/api/*.ts` and `src/types/index.ts`
in the frontend repo) — every endpoint, request shape, and response envelope
(`{ data, message, success }` / `{ data, total, page, per_page, total_pages }`)
mirrors what the frontend already expects, so no frontend code had to be
reshaped around the backend.

## Project layout

```
app/
  core/        settings (env vars) + JWT/password helpers
  db/          SQLAlchemy engine/session
  models/      SQLAlchemy ORM models (one file per domain)
  schemas/     Pydantic request/response schemas
  api/
    deps.py            shared auth dependencies
    v1/endpoints/      one router file per resource (auth, jobs, stages,
                       applications, interviews, analytics, candidates)
    v1/api.py          aggregates all routers under /api/v1
  main.py      FastAPI app + CORS
alembic/       migration scaffold (optional, see below)
init_db.py     quick "create all tables" script
seed.py        demo data (1 company, 1 recruiter, 1 candidate, 1 job)
```

## 1. Local setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then edit DATABASE_URL / SECRET_KEY
python init_db.py             # creates all tables
python seed.py                # optional: adds demo login data
uvicorn app.main:app --reload
```

API docs will be at `http://localhost:8000/docs`.

You need a real Postgres instance for `DATABASE_URL`. Easiest free options:
- **Neon** (neon.tech) — serverless Postgres, generous free tier, works well
  with serverless backends because it supports connection pooling over HTTP.
- **Supabase** (supabase.com) — free Postgres + connection pooler.
- Local Postgres via Docker: `docker run -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16`

## 2. Deploying the backend for free

**Important reality check on your stated plan:** Netlify and Vercel are
built for static sites + short-lived serverless functions. They do not run
a persistent server process, which is what a typical FastAPI + SQLAlchemy
app wants (a long-lived connection pool to Postgres). It *can* be made to
work on Vercel (see below), but you'll hit cold starts and connection-limit
issues on Postgres more easily than on a normal host.

### Recommended: Render (free tier, simplest, persistent server)
1. Push the `backend/` folder to a GitHub repo.
2. On render.com → New → Web Service → connect the repo, root directory `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   (the included `Procfile` already encodes this if Render auto-detects it)
5. Add environment variables: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
   (set this to your Netlify/Vercel frontend URL once you have it).
6. After first deploy, open the Render shell and run `python init_db.py`
   (and optionally `python seed.py`).

Render's free web services sleep after inactivity and wake on the next
request (a few seconds of cold-start delay) — fine for a portfolio/demo.

### Alternative: Vercel (if you want everything on one platform)
A `vercel.json` is included that points Vercel's Python builder at
`app/main.py`. Steps:
1. `vercel` CLI → run from the `backend/` folder → follow prompts.
2. Add the same environment variables in the Vercel dashboard.
3. Use Neon for the database — its pooled connection string handles
   serverless cold starts much better than a normal Postgres URL.

Limitations to expect: 10s execution limit on the free plan, and each
invocation may open a new DB connection unless you use Neon's pooler — fine
for demo traffic, not for production load.

## 3. Connecting the frontend

In the frontend project, set this env var (Vercel/Netlify dashboard, or
`.env` locally):

```
VITE_API_URL=https://your-backend-url.onrender.com/api/v1
```

The frontend's `src/api/config.ts` already reads `VITE_API_URL`, so no
frontend code changes are needed beyond that env var once the API contract
matches (which it now does).

## 4. CORS

`CORS_ORIGINS` in `.env` is a comma-separated list. Once you have your
Netlify/Vercel frontend URL, set:

```
CORS_ORIGINS=https://your-app.netlify.app,https://your-app.vercel.app,http://localhost:5173
```

## 5. Database schema changes going forward

Alembic is already configured (`alembic/env.py` points at `DATABASE_URL`
and the app's models). To generate a migration after changing a model:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```
