"""後端語言資源（圖片提示詞、審查、log key）— 與前端 i18n key 對齊"""

from __future__ import annotations

from typing import Any

SUPPORTED_LOCALES = ("zh-TW", "en")
DEFAULT_LOCALE = "zh-TW"


def normalize_locale(locale: str | None) -> str:
    if not locale:
        return DEFAULT_LOCALE
    loc = locale.strip()
    if loc.lower() in ("en", "en-us", "english"):
        return "en"
    return "zh-TW"


IMAGE_STYLE: dict[str, str] = {
    "zh-TW": """[固定風格要求]
請嚴格遵守以下要求，確保圖片風格一致：

1. **整體風格**：專業醫療教育風格，清晰易懂，適合臨床復健教材。
2. **視覺呈現**：簡潔圖示與箭頭標示動作方向；高對比色彩；乾淨背景。
3. **文字標籤**：使用繁體中文，無錯字，字體清晰可讀，醫學術語準確。
4. **動作呈現**：姿勢符合解剖與醫學標準；必要時正確與錯誤動作並列；步驟清楚。
5. **整體品質**：視覺元素統一，適合醫療教育用途。""",
    "en": """[Fixed Style Requirements]
Strictly follow these requirements for a consistent image style:

1. **Overall style**: Professional medical education style, clear and suitable for clinical rehabilitation materials.
2. **Visual presentation**: Concise icons and arrows for movement; high contrast; clean background.
3. **Text labels**: Use English only, no spelling errors, readable font size, accurate medical terms.
4. **Movement depiction**: Anatomically correct postures; correct vs incorrect side-by-side when applicable; clear steps.
5. **Overall quality**: Cohesive visual elements suitable for medical education.""",
}

IMAGE_LABEL_RULE: dict[str, str] = {
    "zh-TW": (
        "[語言要求] 圖片中所有文字標註、動作標籤、步驟說明、標題與註解必須使用繁體中文。"
        "除必要之醫學專有名詞（如拉丁學名）外，不得混用英文。"
    ),
    "en": (
        "[Language Requirement] All text labels, action captions, step descriptions, titles, "
        "and annotations in the image must be in English. Do not mix Chinese unless a proper "
        "medical term requires it."
    ),
}

# log_key → { locale: template }；與前端 logs.* 對齊
LOG_MESSAGES: dict[str, dict[str, str]] = {
    "job_started": {
        "zh-TW": "已接收輸入，開始執行 {modes} 流程。",
        "en": "Input received. Starting {modes} pipeline(s).",
    },
    "pipeline_a_start": {
        "zh-TW": "A 流程：使用原文直接生成圖片（模型 {model}）。",
        "en": "Pipeline A: Generating image directly from your text (model {model}).",
    },
    "pipeline_b_start": {
        "zh-TW": "B 流程：將先產生圖片提示詞，再生成並審查圖片。",
        "en": "Pipeline B: Generating image prompt, then image generation and review.",
    },
    "prompt_generating": {
        "zh-TW": "正在產生圖片提示詞…",
        "en": "Generating image prompt…",
    },
    "prompt_ready": {
        "zh-TW": "圖片提示詞已產生。",
        "en": "Image prompt is ready.",
    },
    "image_generating": {
        "zh-TW": "正在生成圖片{version_label}…",
        "en": "Generating image{version_label}…",
    },
    "image_done": {
        "zh-TW": "圖片{version_label}生成完成（{duration}s）。",
        "en": "Image{version_label} generated ({duration}s).",
    },
    "review_running": {
        "zh-TW": "正在審查圖片（第 {iteration} 輪）…",
        "en": "Reviewing image (round {iteration})…",
    },
    "review_passed": {
        "zh-TW": "第 {iteration} 輪審查通過。",
        "en": "Review round {iteration} passed.",
    },
    "review_failed": {
        "zh-TW": "第 {iteration} 輪審查未通過，準備修正。",
        "en": "Review round {iteration} did not pass. Preparing refinement.",
    },
    "refine_start": {
        "zh-TW": "依審查意見修正並重新生成 v{version}…",
        "en": "Refining and regenerating v{version} based on review feedback…",
    },
    "pipeline_done": {
        "zh-TW": "{pipeline} 流程完成。",
        "en": "{pipeline} pipeline completed.",
    },
    "job_completed": {
        "zh-TW": "全部流程已完成。",
        "en": "All pipelines completed.",
    },
    "job_failed": {
        "zh-TW": "執行失敗：{reason}",
        "en": "Run failed: {reason}",
    },
    "models_ready": {
        "zh-TW": "已載入模型設定（語言：{locale_label}）。",
        "en": "Model configuration loaded (language: {locale_label}).",
    },
}

STAGE_LOG_KEY: dict[str, str] = {
    "prompt_generated_start": "prompt_generating",
    "prompt_generated": "prompt_ready",
    "direct_generate_start": "pipeline_a_start",
    "image_v1": "image_done",
    "image_v2": "image_done",
    "image_v3": "image_done",
    "image_raw": "image_done",
    "review_1": "review_running",
    "review_2": "review_running",
    "review_3": "review_running",
    "refine_start": "refine_start",
    "finished": "pipeline_done",
}


def t_log(key: str, locale: str, **params: Any) -> str:
    loc = normalize_locale(locale)
    templates = LOG_MESSAGES.get(key, {})
    template = templates.get(loc) or templates.get("zh-TW") or key
    try:
        return template.format(**params)
    except KeyError:
        return template


def stage_to_log(stage: str, locale: str, pipeline: str, data: dict | None = None) -> dict:
    """回傳 { log_key, log_message, log_params }"""
    data = data or {}
    loc = normalize_locale(locale)
    pipeline_label = "A" if pipeline == "a" else "B"

    if stage.startswith("review_"):
        iteration = stage.split("_")[-1]
        log_key = "review_running"
        msg = t_log(log_key, loc, iteration=iteration)
        if data.get("passed") is True:
            msg = t_log("review_passed", loc, iteration=iteration)
        elif data.get("passed") is False:
            msg = t_log("review_failed", loc, iteration=iteration)
        return {"log_key": log_key, "log_message": msg, "log_params": {"iteration": iteration}}

    log_key = STAGE_LOG_KEY.get(stage, "pipeline_done")
    params: dict[str, Any] = {"pipeline": pipeline_label}

    if stage.startswith("image_v"):
        ver = stage.replace("image_v", "")
        params["version_label"] = f" v{ver}" if loc == "en" else f" v{ver}"
        params["duration"] = data.get("duration_sec", "—")
        if stage == "image_raw":
            params["version_label"] = ""
    elif stage == "direct_generate_start":
        params["model"] = data.get("model", "")
    elif stage == "refine_start":
        params["version"] = data.get("next_version", "")
    elif stage == "finished":
        pass
    elif stage == "image_raw":
        params["version_label"] = ""
        params["duration"] = data.get("duration_sec", "—")

    msg = t_log(log_key, loc, **params)
    return {"log_key": log_key, "log_message": msg, "log_params": params}


def locale_label(locale: str) -> str:
    return "繁體中文" if normalize_locale(locale) == "zh-TW" else "English"
