from fastapi import FastAPI

from agent_runner.api.projects import router as projects_router
from agent_runner.api.runs import router as runs_router
from agent_runner.api.events import router as events_router

app = FastAPI(title="Agent Runner Test", version="0.1.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(projects_router)
app.include_router(runs_router)
app.include_router(events_router)
