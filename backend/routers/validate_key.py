from fastapi import APIRouter, Header, HTTPException, Query

from i18n.messages import normalize_locale
from schemas import ValidateKeyResponse

router = APIRouter(prefix="/api", tags=["auth"])


def _get_api_key(x_gemini_api_key: str | None) -> str:
    if not x_gemini_api_key or not x_gemini_api_key.strip():
        raise HTTPException(status_code=401, detail="請提供 X-Gemini-Api-Key")
    return x_gemini_api_key.strip()


@router.post("/validate-key", response_model=ValidateKeyResponse)
def validate_key(
    x_gemini_api_key: str | None = Header(default=None),
    locale: str = Query(default="zh-TW"),
):
    loc = normalize_locale(locale)
    key = _get_api_key(x_gemini_api_key)
    ok_msg = "金鑰有效" if loc == "zh-TW" else "API key is valid"
    bad_msg = "金鑰無效或無權限" if loc == "zh-TW" else "Invalid API key or insufficient permission"
    err_msg = "無法驗證金鑰，請稍後再試" if loc == "zh-TW" else "Could not validate key. Please try again."
    try:
        from google import genai

        client = genai.Client(api_key=key)
        for _i, _m in enumerate(client.models.list()):
            if _i >= 0:
                break
        return ValidateKeyResponse(valid=True, message=ok_msg)
    except Exception as e:
        msg = str(e)
        if "401" in msg or "403" in msg or "API_KEY" in msg.upper():
            return ValidateKeyResponse(valid=False, message=bad_msg)
        return ValidateKeyResponse(valid=False, message=err_msg)
