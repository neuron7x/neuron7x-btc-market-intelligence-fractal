import asyncio
import json
import os
import time
from pathlib import Path

import httpx
from httpx import ASGITransport

from btcmi.api import app

R = Path(__file__).resolve().parents[2]


async def _load_test() -> tuple[float, int]:
    payload = json.loads((R / "examples" / "intraday.json").read_text())

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        request_count = 20
        durations: list[float] = []

        async def call_api() -> None:
            start = time.perf_counter()
            resp = await client.post("/run", json=payload)
            resp.raise_for_status()
            durations.append(time.perf_counter() - start)

        stop = asyncio.Event()

        async def ticker() -> int:
            ticks = 0
            while not stop.is_set():
                ticks += 1
                await asyncio.sleep(0.05)
            return ticks

        request_tasks = [asyncio.create_task(call_api()) for _ in range(request_count)]
        ticker_task = asyncio.create_task(ticker())

        await asyncio.gather(*request_tasks)
        stop.set()
        ticks = await ticker_task

    avg = sum(durations) / len(durations)
    assert ticks > 1, "event loop was blocked during requests"
    return avg, request_count


def test_api_load_event_loop_not_blocked() -> None:
    avg, request_count = asyncio.run(_load_test())
    if os.environ.get("UPDATE_PERF_BASELINE") == "1":
        baseline_path = R / "docs" / "api_load_baseline.json"
        baseline_path.write_text(
            json.dumps({"avg_response_time": avg, "requests": request_count}, indent=2)
        )
    else:
        print(f"Average response time: {avg:.4f}s over {request_count} requests")
