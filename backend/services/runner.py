"""背景執行 Job"""
from __future__ import annotations

import os
import time
from typing import List

from i18n.messages import locale_label, normalize_locale, stage_to_log, t_log
from services.job_store import JobRecord, job_store
from services.pipeline_a import run_pipeline_a
from services.pipeline_b import run_pipeline_b


def _friendly_error(exc: Exception, locale: str) -> str:
    raw = str(exc)
    loc = normalize_locale(locale)
    lower = raw.lower()
    if "api key" in lower or "401" in lower or "403" in lower:
        reason = (
            "API 金鑰無效或已達配額上限"
            if loc == "zh-TW"
            else "Invalid API key or quota exceeded"
        )
    elif "quota" in lower or "rate" in lower:
        reason = (
            "API 呼叫次數或配額已用完，請稍後再試"
            if loc == "zh-TW"
            else "API quota or rate limit reached. Please try again later."
        )
    elif "timeout" in lower or "deadline" in lower:
        reason = (
            "連線逾時，請檢查網路後重試"
            if loc == "zh-TW"
            else "Connection timed out. Check your network and retry."
        )
    else:
        reason = (
            "圖片生成過程發生問題，請稍後再試"
            if loc == "zh-TW"
            else "Image generation encountered a problem. Please try again."
        )
    return reason


def _stage_record(
    pipeline: str,
    stage: str,
    event: str,
    data: dict,
    job_id: str,
    t0: float,
    locale: str,
) -> dict:
    elapsed_ms = int((time.time() - t0) * 1000)
    out = dict(data)
    for key in ("filename", "image_filename"):
        if key in out and out[key]:
            out["image_url"] = f"/api/jobs/{job_id}/assets/{out[key]}"
    log_info = stage_to_log(stage, locale, pipeline, out)
    return {
        "pipeline": pipeline,
        "stage": stage,
        "event": event,
        "data": out,
        "elapsed_ms": elapsed_ms,
        **log_info,
    }


def execute_job(job: JobRecord, api_key: str) -> None:
    job_store.mark_running(True)
    job_store.set_status(job, "running")
    t_job = time.time()
    loc = normalize_locale(job.locale)

    modes_label = "+".join(m.upper() for m in job.modes)
    job_store.append_log(
        job,
        {
            "log_key": "models_ready",
            "log_message": t_log(
                "models_ready", loc, locale_label=locale_label(loc)
            ),
            "log_params": {"locale_label": locale_label(loc)},
        },
    )
    job_store.append_log(
        job,
        {
            "log_key": "job_started",
            "log_message": t_log("job_started", loc, modes=modes_label),
            "log_params": {"modes": modes_label},
        },
    )

    try:
        modes: List[str] = list(job.modes)
        if "ab" in modes or "a+b" in modes:
            modes = ["a", "b"]

        if "a" in modes:
            job_store.append_log(
                job,
                {
                    "log_key": "pipeline_a_start",
                    "log_message": t_log("pipeline_a_start", loc, model="gemini-3-pro-image-preview"),
                    "log_params": {"model": "gemini-3-pro-image-preview"},
                    "pipeline": "a",
                },
            )

            def on_a(stage: str, data: dict) -> None:
                job_store.append_stage(
                    job,
                    _stage_record("a", stage, "stage_completed", data, job.id, t_job, loc),
                )

            job.result_a = run_pipeline_a(
                job.prompt, job.job_dir, api_key, locale=loc, on_event=on_a
            )
            job_store.append_log(
                job,
                {
                    "log_key": "pipeline_done",
                    "log_message": t_log("pipeline_done", loc, pipeline="A"),
                    "log_params": {"pipeline": "A"},
                    "pipeline": "a",
                },
            )

        if "b" in modes:
            job_store.append_log(
                job,
                {
                    "log_key": "pipeline_b_start",
                    "log_message": t_log("pipeline_b_start", loc),
                    "log_params": {},
                    "pipeline": "b",
                },
            )

            def on_b(stage: str, data: dict) -> None:
                job_store.append_stage(
                    job,
                    _stage_record("b", stage, "stage_completed", data, job.id, t_job, loc),
                )

            job.result_b = run_pipeline_b(
                job.prompt,
                job.job_dir,
                api_key,
                job.max_iterations,
                locale=loc,
                on_event=on_b,
            )
            job_store.append_log(
                job,
                {
                    "log_key": "pipeline_done",
                    "log_message": t_log("pipeline_done", loc, pipeline="B"),
                    "log_params": {"pipeline": "B"},
                    "pipeline": "b",
                },
            )

        job_store.set_status(job, "completed")
        job_store.append_log(
            job,
            {
                "log_key": "job_completed",
                "log_message": t_log("job_completed", loc),
                "log_params": {},
            },
        )
        job_store._broadcast(job, {"event": "done", "status": "completed"})
    except Exception as e:
        reason = _friendly_error(e, loc)
        job_store.set_status(job, "failed", reason)
        job_store.append_log(
            job,
            {
                "log_key": "job_failed",
                "log_message": t_log("job_failed", loc, reason=reason),
                "log_params": {"reason": reason},
            },
        )
        job_store._broadcast(job, {"event": "done", "status": "failed", "error": reason})
    finally:
        job_store.mark_running(False)


def start_job_background(job: JobRecord, api_key: str) -> None:
    import threading

    os.makedirs(job.job_dir, exist_ok=True)
    thread = threading.Thread(
        target=execute_job,
        args=(job, api_key),
        daemon=True,
    )
    thread.start()
