Portfolio API The backend behind my portfolio. A small FastAPI service that serves my GitHub data to the site, caches it in Redis, and tracks its own request metrics. Live API: https://portfolio-api-1t2s.onrender.com · Interactive docs: https://portfolio-api-1t2s.onrender.com/docs

Hosted on Render's free plan: the first request after a period of inactivity can take up to a minute while the server wakes up. Endpoints Method Path Returns GET / Health check GET /github Public repo count, followers and my 6 most recently updated repositories GET /stats Requests in the last 24 hours and average response time How it works GitHub integration: fetches profile and repository data from the GitHub REST API, with an optional token to raise rate limits. Redis cache: GitHub responses are cached for 5 minutes, so the site loads fast and stays well within GitHub's rate limits. Metrics middleware: a custom Starlette middleware counts every request in hourly buckets (expiring after 25 hours) and stores the last 200 response times. Graceful degradation: if Redis is unavailable, the API keeps working without the cache and logs a warning instead of failing. CORS: only my portfolio domain (and localhost for development) can call the API. Tech stack Area Technology Framework FastAPI, Uvicorn Cache & metrics Redis (Upstash) Config pydantic-settings, environment variables Testing pytest, FastAPI TestClient, unittest.mock Deployment Render Tests 13 automated tests cover the health check, GitHub caching (cache hit, cache miss, Redis down, GitHub errors) and stats calculation, with Redis and GitHub mocked.

pytest
Running locally

git clone https://github.com/GuilhermeNascimento-bit/portfolio-api.git
cd portfolio-api

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # fill in your GitHub token and Redis URL
uvicorn app.main:app --reload
Then open http://localhost:8000/docs. Project structure

app/
├── main.py            # app setup, CORS, routers
├── config.py          # settings from environment variables
├── routes/            # /github and /stats endpoints
├── services/          # GitHub client and Redis connection
└── middleware/        # request metrics
tests/                 # pytest suite with mocked Redis and GitHub
Author Guilherme do Nascimento Bezerra · Portfolio · LinkedIn · GitHub
