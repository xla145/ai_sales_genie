from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from app.models.run import RunStatus, SubtaskRun


class SubagentPool:
    async def run(
        self,
        subtasks: list[SubtaskRun],
        worker_count: int,
        worker: Callable[[SubtaskRun], Awaitable[dict]],
    ) -> list[SubtaskRun]:
        if not subtasks:
            return []

        queue: asyncio.Queue[SubtaskRun | None] = asyncio.Queue()
        for subtask in subtasks:
            await queue.put(subtask)

        actual_workers = max(1, min(worker_count, len(subtasks)))
        for _ in range(actual_workers):
            await queue.put(None)

        async def consume() -> None:
            while True:
                item = await queue.get()
                try:
                    if item is None:
                        return
                    try:
                        item.result_summary = await worker(item)
                        item.status = RunStatus.SUCCESS
                    except Exception as exc:
                        item.status = RunStatus.FAILED
                        item.error_message = str(exc)
                finally:
                    queue.task_done()

        consumers = [asyncio.create_task(consume()) for _ in range(actual_workers)]
        await queue.join()
        await asyncio.gather(*consumers)
        return subtasks
