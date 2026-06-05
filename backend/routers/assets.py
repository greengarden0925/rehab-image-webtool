import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from deps import RUNTIME_JOBS
from services.job_store import job_store

router = APIRouter(prefix="/api/jobs", tags=["assets"])


@router.get("/{job_id}/assets/{filename}")
def get_asset(job_id: str, filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="非法檔名")

    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job 不存在")

    job_dir = Path(job.job_dir).resolve()
    file_path = (job_dir / filename).resolve()

    if not str(file_path).startswith(str(job_dir)):
        raise HTTPException(status_code=400, detail="非法路徑")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="檔案不存在")

    media_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(file_path, media_type=media_type or "application/octet-stream")
