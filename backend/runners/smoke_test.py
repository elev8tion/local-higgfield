from __future__ import annotations

import json
import subprocess
from pathlib import Path

try:
    from backend.storage.paths import ensure_output_dir
except ModuleNotFoundError:
    from storage.paths import ensure_output_dir


ROOT = Path(__file__).resolve().parents[2]
ASSET_DIR = ensure_output_dir() / "assets"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def create_test_assets() -> tuple[Path, Path]:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    image_path = ASSET_DIR / "smoke-test.png"
    audio_path = ASSET_DIR / "smoke-test.wav"

    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=1024x1024:d=1",
            "-frames:v",
            "1",
            str(image_path),
        ]
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=880:duration=2",
            str(audio_path),
        ]
    )

    return image_path, audio_path


def write_payload(name: str, payload: dict) -> Path:
    payload_path = ensure_output_dir() / f"{name}.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    return payload_path


def verify_duration(path: Path) -> str:
    probe = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
    )
    return probe.stdout.strip()


def main() -> int:
    image_path, audio_path = create_test_assets()

    video_payload = write_payload(
        "smoke-video-animate-image",
        {
            "type": "video.animate_image",
            "prompt": "",
            "params": {"model": "local-video-animate-image", "resolution": "720p", "duration": 2},
            "input_assets": [{"kind": "image", "uri": f"/files/{image_path.name}", "role": "source_image"}],
        },
    )
    lipsync_payload = write_payload(
        "smoke-lipsync-image-audio",
        {
            "type": "lipsync.image_audio",
            "prompt": "",
            "params": {"model": "local-lipsync-image-audio", "resolution": "480p"},
            "input_assets": [
                {"kind": "image", "uri": f"/files/{image_path.name}", "role": "source_image"},
                {"kind": "audio", "uri": f"/files/{audio_path.name}", "role": "source_audio"},
            ],
        },
    )

    video_out = Path("/tmp/open-higgsfield-smoke-video.mp4")
    lipsync_out = Path("/tmp/open-higgsfield-smoke-lipsync.mp4")

    video = run(
        ["python3", "-m", "backend.runners.video_runner", "--payload", str(video_payload), "--output", str(video_out)]
    )
    lipsync = run(
        ["python3", "-m", "backend.runners.lipsync_runner", "--payload", str(lipsync_payload), "--output", str(lipsync_out)]
    )

    print(
        json.dumps(
            {
                "video_runner_exit": video.returncode,
                "lipsync_runner_exit": lipsync.returncode,
                "video_output_exists": video_out.exists(),
                "lipsync_output_exists": lipsync_out.exists(),
                "video_duration": verify_duration(video_out) if video_out.exists() else None,
                "lipsync_duration": verify_duration(lipsync_out) if lipsync_out.exists() else None,
            },
            indent=2,
        )
    )

    return 0 if video.returncode == 0 and lipsync.returncode == 0 and video_out.exists() and lipsync_out.exists() else 1


if __name__ == "__main__":
    raise SystemExit(main())
