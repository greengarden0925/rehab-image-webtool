"""B 流程：審查迭代"""
from __future__ import annotations

import os
import time
from typing import Callable, Optional

from main import RehabilitationImageGenerator  # noqa: E402


def run_pipeline_b(
    prompt: str,
    job_dir: str,
    api_key: str,
    max_iterations: int,
    locale: str = "zh-TW",
    on_event: Optional[Callable[[str, dict], None]] = None,
) -> dict:
    os.makedirs(job_dir, exist_ok=True)
    t0 = time.time()

    def wrapped_callback(stage: str, data: dict) -> None:
        if on_event:
            on_event(stage, dict(data))

    generator = RehabilitationImageGenerator(
        api_key=api_key,
        output_dir=job_dir,
        max_iterations=max_iterations,
        locale=locale,
    )
    result = generator.generate(
        prompt,
        output_prefix="b",
        progress_callback=wrapped_callback,
    )
    result["duration_sec"] = round(time.time() - t0, 1)
    result["final_image_filename"] = os.path.basename(result["final_image_path"])
    result["locale"] = locale
    return result
