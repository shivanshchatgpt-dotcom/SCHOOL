"""PySchool — FastAPI application entrypoint."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .db import init_db
from .seed import seed
from .routers import paths, assessment, lessons, dashboard, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="PySchool API", version="0.1.0", lifespan=lifespan)

# MVP-safe CORS: explicit dev origins instead of "*" with credentials.
# Override with PYSCHOOL_CORS_ORIGINS="https://a.example,https://b.example" in
# deployment. Wildcard-with-credentials is not a valid browser combination and
# was an audit finding.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_cors_origins = [
    origin.strip()
    for origin in os.environ.get("PYSCHOOL_CORS_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paths.router, prefix="/api", tags=["paths"])
app.include_router(assessment.router, prefix="/api", tags=["assessment"])
app.include_router(lessons.router, prefix="/api", tags=["lessons"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/", include_in_schema=False)
def frontend_redirect():
    frontend_url = os.environ.get("PYSCHOOL_FRONTEND_URL", "http://127.0.0.1:5173/")
    return RedirectResponse(url=frontend_url)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "PySchool"}
