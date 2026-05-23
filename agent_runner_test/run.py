import uvicorn

from agent_runner.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "agent_runner.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True,
    )
