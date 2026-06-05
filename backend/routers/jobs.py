import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse

from deps import RUNTIME_JOBS
from schemas import CreateJobRequest
from services.job_store import job_store
from services.runner import start_job_background

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _get_api_key(x_gemini_api_key: str | None) -> str:
    if not x_gemini_api_key or not x_gemini_api_key.strip():
        raise HTTPException(status_code=401, detail="請提供 X-Gemini-Api-Key")
    return x_gemini_api_key.strip()


@router.post("")
def create_job(
    body: CreateJobRequest,
    x_gemini_api_key: str | None = Header(default=None),
):
    if not body.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt 不可為空")

    if not job_store.can_start():
        raise HTTPException(
            status_code=429,
            detail="目前已有進行中的生成工作，請稍後再試",
        )

    api_key = _get_api_key(x_gemini_api_key)
    modes = body.modes if body.modes else ["a", "b"]
    job = job_store.create(
        prompt=body.prompt.strip(),
        modes=modes,
        max_iterations=body.max_iterations,
        job_dir="",
    )
    job.locale = body.locale
    job_dir = str((RUNTIME_JOBS / job.id).resolve())
    job.job_dir = job_dir

    start_job_background(job, api_key)
    return {"job_id": job.id, "status": job.status}


@router.get("/{job_id}")
def get_job(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job 不存在")
    return job.to_dict()


@router.get("/{job_id}/events")
async def job_events(job_id: str):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job 不存在")

    queue = job_store.subscribe(job)

    async def event_generator():
        try:
            for log_entry in job.logs:
                yield f"data: {json.dumps({'event': 'log', **log_entry}, ensure_ascii=False)}\n\n"
            for stage in job.stages:
                yield f"data: {json.dumps(stage, ensure_ascii=False)}\n\n"
            while job.status in ("pending", "running"):
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    if payload.get("event") == "done":
                        break
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'event': 'heartbeat'})}\n\n"
            yield f"data: {json.dumps({'event': 'done', 'status': job.status})}\n\n"
        finally:
            job_store.unsubscribe(job, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete("/{job_id}")
def delete_job(job_id: str):
    import shutil

    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job 不存在")
    if job.job_dir:
        p = Path(job.job_dir)
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    return {"deleted": job_id}
