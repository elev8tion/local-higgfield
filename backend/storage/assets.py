from __future__ import annotations

from pathlib import Path
from uuid import uuid4

try:
    from backend.jobs.schemas import AssetRef
    from backend.storage.paths import ensure_output_dir
except ModuleNotFoundError:
    from jobs.schemas import AssetRef
    from storage.paths import ensure_output_dir


ASSET_DIR = ensure_output_dir() / "assets"


def ensure_asset_dir() -> Path:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    return ASSET_DIR


def _safe_suffix(filename: str) -> str:
    suffix = Path(filename).suffix
    return suffix if suffix else ""


def save_uploaded_asset(filename: str, content: bytes, kind: str, role: str | None = None) -> AssetRef:
    asset_id = str(uuid4())
    stored_name = f"{asset_id}{_safe_suffix(filename)}"
    path = ensure_asset_dir() / stored_name
    path.write_bytes(content)

    return AssetRef(
        kind=kind,
        uri=f"/files/{stored_name}",
        role=role,
        metadata={
            "asset_id": asset_id,
            "filename": filename,
            "path": str(path),
        },
    )
