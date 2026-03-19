from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from shutil import copyfile

try:
    from backend.storage.assets import ensure_asset_dir
except ModuleNotFoundError:
    from storage.assets import ensure_asset_dir


DEMO_VIDEO_PATH = Path(__file__).resolve().parents[2] / "docs" / "assets" / "demo.mp4"
DEFAULT_FPS = 24
RESOLUTION_PRESETS = {
    "360p": (640, 360),
    "480p": (854, 480),
    "540p": (960, 540),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
}


def load_payload(payload_path: str) -> dict:
    return json.loads(Path(payload_path).read_text(encoding="utf-8"))


def find_input_asset(payload: dict, allowed_kinds: set[str]) -> str | None:
    for asset in payload.get("input_assets", []):
        if asset.get("kind") not in allowed_kinds:
            continue
        uri = asset.get("uri", "")
        if uri.startswith("/files/"):
            relative_path = uri[len("/files/") :]
            candidate = ensure_asset_dir() / relative_path
            if candidate.exists():
                return str(candidate)
    return None


def ffmpeg_available() -> bool:
    return bool(os.getenv("PATH")) and any(
        Path(path, "ffmpeg").exists() for path in os.getenv("PATH", "").split(os.pathsep)
    )


def resolve_dimensions(resolution: str | None, aspect_ratio: str | None) -> tuple[int, int]:
    if resolution in RESOLUTION_PRESETS:
        base_width, base_height = RESOLUTION_PRESETS[resolution]
    else:
        base_width, base_height = RESOLUTION_PRESETS["720p"]

    if not aspect_ratio or ":" not in aspect_ratio:
        return base_width, base_height

    width_ratio, height_ratio = aspect_ratio.split(":", 1)
    try:
        width_ratio_value = int(width_ratio)
        height_ratio_value = int(height_ratio)
    except ValueError:
        return base_width, base_height

    if width_ratio_value <= 0 or height_ratio_value <= 0:
        return base_width, base_height

    target_height = base_height
    target_width = int(round(target_height * width_ratio_value / height_ratio_value))
    if target_width % 2:
        target_width += 1
    if target_height % 2:
        target_height += 1
    return target_width, target_height


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ffmpeg", "-y", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def ffmpeg_or_fallback(args: list[str], output_path: str, fallback_source_path: str | None = None) -> dict:
    if not ffmpeg_available():
        return {
            "mode": "fallback-copy",
            "output_path": copy_video_output(output_path, fallback_source_path),
            "stderr_tail": "ffmpeg not available",
        }

    completed = run_ffmpeg(args)
    if completed.returncode != 0:
        return {
            "mode": "fallback-copy",
            "output_path": copy_video_output(output_path, fallback_source_path),
            "stderr_tail": completed.stderr[-2000:],
        }

    return {
        "mode": "ffmpeg",
        "output_path": output_path,
        "stderr_tail": completed.stderr[-2000:],
    }


def ensure_parent(path: str) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def copy_video_output(output_path: str, source_path: str | None = None) -> str:
    final_path = ensure_parent(output_path)
    copyfile(source_path or DEMO_VIDEO_PATH, final_path)
    return str(final_path)
