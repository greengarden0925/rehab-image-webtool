import json
from pathlib import Path

from fastapi import APIRouter, Query

from i18n.messages import normalize_locale

router = APIRouter(prefix="/api", tags=["examples"])

SAMPLES_PATH = Path(__file__).resolve().parents[2] / "samples" / "example_prompts.json"


@router.get("/examples")
def list_examples(locale: str = Query(default="zh-TW")):
    loc = normalize_locale(locale)
    if not SAMPLES_PATH.is_file():
        return {"examples": [], "locale": loc}
    with open(SAMPLES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    raw = data.get("examples", [])
    examples = []
    for ex in raw:
        title = ex.get("title")
        text = ex.get("text")
        if isinstance(title, dict):
            title = title.get(loc) or title.get("zh-TW", "")
        if isinstance(text, dict):
            text = text.get(loc) or text.get("zh-TW", "")
        examples.append({"id": ex["id"], "title": title, "text": text})
    return {"examples": examples, "locale": loc}
