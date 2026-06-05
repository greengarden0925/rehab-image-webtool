"""A 流程：直接生圖"""
from __future__ import annotations

import os
import time
from typing import Callable, Optional

from raw_generate import RAW_IMAGE_MODEL, generate_raw_image
from utils.i18n_prompts import wrap_direct_image_prompt


def run_pipeline_a(
    prompt: str,
    job_dir: str,
    api_key: str,
    locale: str = "zh-TW",
    on_event: Optional[Callable[[str, dict], None]] = None,
) -> dict:
    os.makedirs(job_dir, exist_ok=True)
    t0 = time.time()

    def emit(stage: str, data: dict) -> None:
        if on_event:
            on_event(stage, data)

    image_prompt = wrap_direct_image_prompt(prompt, locale)
    emit("direct_generate_start", {"model": RAW_IMAGE_MODEL})
    path = generate_raw_image(
        image_prompt,
        "raw",
        output_dir=job_dir,
        api_key=api_key,
        output_filename="a_raw.png",
    )
    filename = os.path.basename(path)
    duration = round(time.time() - t0, 1)
    emit("image_raw", {"filename": filename, "duration_sec": duration})
    note_key = "a_note"
    return {
        "final_image_filename": filename,
        "duration_sec": duration,
        "model": RAW_IMAGE_MODEL,
        "note_key": note_key,
        "locale": locale,
    }
