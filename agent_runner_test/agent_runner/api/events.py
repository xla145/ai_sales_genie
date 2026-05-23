import asyncio
import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from agent_runner.db.session import get_db_session
from agent_runner.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["events"])
event_service = EventService()


@router.get("/{run_id}")
async def list_events(
    run_id: str,
    after_id: int = Query(default=0, ge=0),
    limit: int = Query(default=200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
):
    events = await event_service.list_events(db, run_id=run_id, after_id=after_id, limit=limit)
    return {"run_id": run_id, "events": events}


@router.get("/{run_id}/stream")
async def stream_events(
    run_id: str,
    after_id: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    async def event_generator():
        cursor = after_id
        while True:
            events = await event_service.list_events(db, run_id=run_id, after_id=cursor, limit=200)
            if events:
                for event in events:
                    cursor = max(cursor, event["id"])
                    yield f"id: {event['id']}\nevent: {event['event_type']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
