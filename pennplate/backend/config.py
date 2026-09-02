from __future__ import annotations

import os
from pathlib import Path


class ConfigError(RuntimeError):
    pass


def load_env_file(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Config:
    def __init__(self) -> None:
        load_env_file()
        self.supabase_url = os.environ.get("SUPABASE_URL", "").rstrip("/")
        self.supabase_service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

    def require_supabase(self) -> None:
        if not self.supabase_url or not self.supabase_service_role_key:
            raise ConfigError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
