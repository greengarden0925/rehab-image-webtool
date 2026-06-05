"""記憶體 Job 狀態與 SSE 事件佇列"""
from __future__ import annotations

import asyncio
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

JobStatus = Literal["pending", "running", "completed", "failed", "cancelled"]


@dataclass
class JobRecord:
    id: str
    prompt: str
    modes: List[str]
    max_iterations: int
    status: JobStatus = "pending"
    error: Optional[str] = None
    stages: List[Dict[str, Any]] = field(default_factory=list)
    result_a: Optional[Dict[str, Any]] = None
    result_b: Optional[Dict[str, Any]] = None
    job_dir: str = ""
    locale: str = "zh-TW"
    logs: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    _subscribers: List[asyncio.Queue] = field(default_factory=list, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "modes": self.modes,
            "max_iterations": self.max_iterations,
            "status": self.status,
            "error": self.error,
            "stages": self.stages,
            "result_a": self.result_a,
            "result_b": self.result_b,
            "job_dir": self.job_dir,
            "locale": self.locale,
            "logs": self.logs,
            "created_at": self.created_at,
        }


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._run_lock = threading.Lock()
        self._running = False

    def create(
        self,
        prompt: str,
        modes: List[str],
        max_iterations: int,
        job_dir: str,
    ) -> JobRecord:
        job_id = str(uuid.uuid4())
        rec = JobRecord(
            id=job_id,
            prompt=prompt,
            modes=modes,
            max_iterations=max_iterations,
            job_dir=job_dir,
        )
        self._jobs[job_id] = rec
        return rec

    def get(self, job_id: str) -> Optional[JobRecord]:
        return self._jobs.get(job_id)

    def can_start(self) -> bool:
        with self._run_lock:
            return not self._running

    def mark_running(self, running: bool) -> None:
        with self._run_lock:
            self._running = running

    def append_log(self, job: JobRecord, entry: Dict[str, Any]) -> None:
        with job._lock:
            entry = {**entry, "ts": time.time()}
            job.logs.append(entry)
        self._broadcast(job, {"event": "log", **entry})

    def append_stage(self, job: JobRecord, stage: Dict[str, Any]) -> None:
        with job._lock:
            job.stages.append(stage)
        self._broadcast(job, {"event": "stage", **stage})
        if stage.get("log_message"):
            self.append_log(
                job,
                {
                    "log_key": stage.get("log_key", ""),
                    "log_message": stage["log_message"],
                    "log_params": stage.get("log_params", {}),
                    "pipeline": stage.get("pipeline"),
                    "stage": stage.get("stage"),
                },
            )

    def set_status(self, job: JobRecord, status: JobStatus, error: Optional[str] = None) -> None:
        job.status = status
        if error:
            job.error = error
        self._broadcast(job, {"event": "status", "status": status, "error": error})

    def subscribe(self, job: JobRecord) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        job._subscribers.append(q)
        return q

    def unsubscribe(self, job: JobRecord, q: asyncio.Queue) -> None:
        try:
            job._subscribers.remove(q)
        except ValueError:
            pass

    def _broadcast(self, job: JobRecord, payload: dict) -> None:
        payload = {**payload, "job_id": job.id}
        for q in list(job._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass


job_store = JobStore()
