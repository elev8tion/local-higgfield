from __future__ import annotations

import os
from pathlib import Path


_CONFIG_LOADED = False


def _parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]

    return key, value


def load_runtime_config() -> None:
    global _CONFIG_LOADED
    if _CONFIG_LOADED:
        return

    search_paths = [
        Path(__file__).resolve().with_name("runtime_config.env"),
        Path(__file__).resolve().parents[1] / ".env",
    ]

    for path in search_paths:
        if not path.exists():
            continue

        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = _parse_env_line(line)
            if not parsed:
                continue
            key, value = parsed
            os.environ.setdefault(key, value)

    _CONFIG_LOADED = True
