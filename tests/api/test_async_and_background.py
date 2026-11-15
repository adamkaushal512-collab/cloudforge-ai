"""
Tests for the async inference demo and background job demo.

NOTE: FastAPI BackgroundTasks run in the same process after the
response is sent. They are not durable: a crash or restart loses
queued work, there are no retries, and nothing is distributed
across workers. Production jobs need a durable queue.
"""

import asyncio

import httpx
import pytest

from cloudforge import main
from cloudforge.main import app, process_demo_job

DEMO_RESPONSE = {"model": "cloudforge-demo", "status": "completed"}
_real_sleep = asyncio.sleep


@pytest.mark.api
def test_async_inference_demo_end_to_end(dev_auth_client):
    # Real 2s simulated latency, exercised once.
    resp = dev_auth_client.get("/v1/inference/demo")

    assert resp.status_code == 200
    assert resp.json() == DEMO_RESPONSE


@pytest.mark.api
def test_async_inference_requests_overlap(monkeypatch):
    """
    Deterministic concurrency check (no timing assertions): every
    request must be suspended in its await at the same time, which
    is only possible if the endpoint does not block the event loop.
    """

    concurrent = 5
    in_flight = 0
    peak = 0
    all_waiting = asyncio.Event()

    async def tracking_sleep(delay, *args, **kwargs):
        nonlocal in_flight, peak
        if delay != 2:
            # Leave framework-internal sleeps untouched.
            return await _real_sleep(delay, *args, **kwargs)
        in_flight += 1
        peak = max(peak, in_flight)
        if in_flight == concurrent:
            all_waiting.set()
        await asyncio.wait_for(all_waiting.wait(), timeout=5)
        in_flight -= 1

    monkeypatch.setattr(main.asyncio, "sleep", tracking_sleep)

    async def run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            return await asyncio.gather(
                *(ac.get("/v1/inference/demo") for _ in range(concurrent))
            )

    responses = asyncio.run(run())

    assert [r.status_code for r in responses] == [200] * concurrent
    assert all(r.json() == DEMO_RESPONSE for r in responses)
    assert peak == concurrent


@pytest.mark.api
def test_background_job_submission_schedules_task(dev_auth_client, monkeypatch):
    executed: list[str] = []
    monkeypatch.setattr(main, "process_demo_job", lambda job_id: executed.append(job_id))

    resp = dev_auth_client.post("/v1/jobs/demo")

    assert resp.status_code == 202
    assert resp.json() == {"job_id": "demo-job-001", "status": "accepted"}
    # TestClient runs background tasks before returning.
    assert executed == ["demo-job-001"]


@pytest.mark.unit
def test_process_demo_job_logs_start_and_completion(monkeypatch, capsys):
    sleeps: list[float] = []
    monkeypatch.setattr(main.time, "sleep", lambda seconds: sleeps.append(seconds))

    process_demo_job("job-42")

    assert sleeps == [3]
    assert capsys.readouterr().out.splitlines() == [
        "Job job-42: processing started",
        "Job job-42: processing completed",
    ]
