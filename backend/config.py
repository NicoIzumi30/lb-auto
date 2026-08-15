import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_env() -> None:
    path = BASE_DIR / ".env"
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

FONNTE_TOKEN = os.getenv("FONNTE_TOKEN", "")
FONNTE_ENABLED = os.getenv("FONNTE_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://127.0.0.1:8000")
