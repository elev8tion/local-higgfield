from __future__ import annotations

from pathlib import Path


OUTPUT_DIR = Path("/tmp/open-higgsfield-ai")


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def job_output_path(job_id: str, extension: str = ".png") -> Path:
    return ensure_output_dir() / f"{job_id}{extension}"


def output_url_for_path(path: str | Path) -> str:
    return f"/outputs/{Path(path).name}"

