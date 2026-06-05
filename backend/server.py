"""
Webtool FastAPI 後端
啟動：cd Webtool/backend && uvicorn server:app --reload --port 8000
"""
import deps  # noqa: F401 — WEBTOOL_MODE + sys.path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import assets, examples, jobs, validate_key

app = FastAPI(
    title="復健圖生成 Webtool",
    description="A 直接生成 vs B 審查迭代 — BYOK",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(validate_key.router)
app.include_router(jobs.router)
app.include_router(assets.router)
app.include_router(examples.router)


@app.get("/api/health")
def health():
    return {"ok": True, "webtool_mode": True}
