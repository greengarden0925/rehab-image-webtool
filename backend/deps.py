"""專案路徑與環境設定（須在 import config / agents 前執行）"""
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent
ROOT = BACKEND.parents[1]
WEBTOOL = BACKEND.parent

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

os.environ.setdefault("WEBTOOL_MODE", "1")

RUNTIME_JOBS = WEBTOOL / "runtime" / "jobs"
RUNTIME_JOBS.mkdir(parents=True, exist_ok=True)
