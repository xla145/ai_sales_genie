from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.deps import build_service_container
from app.api.orchestration import router as workflow_router
from app.api.projects import router as projects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.services = build_service_container()
    yield


app = FastAPI(title="Hermes Validation Backend", lifespan=lifespan)
app.include_router(projects_router)
app.include_router(workflow_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
