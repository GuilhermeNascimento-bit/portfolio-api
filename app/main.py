from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.middleware.metrics import MetricsMiddleware
from app.routes import github, stats

app = FastAPI(title="Portifolio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://guilhermenascimento-bit.github.io",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.add_middleware(MetricsMiddleware)

app.include_router(github.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "portifolio-api"}
