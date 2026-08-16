"""PySchool — FastAPI application entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .seed import seed
from .routers import paths, assessment, lessons, dashboard, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="PySchool API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(paths.router, prefix="/api", tags=["paths"])
app.include_router(assessment.router, prefix="/api", tags=["assessment"])
app.include_router(lessons.router, prefix="/api", tags=["lessons"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "PySchool"}
