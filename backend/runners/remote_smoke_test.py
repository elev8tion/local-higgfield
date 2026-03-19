from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from .mock_remote_service import run_in_thread


def run(cmd: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True, env=env)


def write_payload(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def main() -> int:
    server, _thread = run_in_thread()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        payload_dir = Path("/tmp/open-higgsfield-remote-smoke")
        payload_dir.mkdir(parents=True, exist_ok=True)

        video_payload = payload_dir / "video.json"
        lipsync_payload = payload_dir / "lipsync.json"
        video_output = payload_dir / "video.mp4"
        lipsync_output = payload_dir / "lipsync.mp4"

        write_payload(
            video_payload,
            {"type": "video.generate", "prompt": "test", "params": {"model": "remote-video-test"}, "input_assets": []},
        )
        write_payload(
            lipsync_payload,
            {
                "type": "lipsync.video_audio",
                "prompt": "",
                "params": {"model": "remote-lipsync-test"},
                "input_assets": [],
            },
        )

        env = dict(os.environ)
        env.update(
            {
                "OPEN_HIGGSFIELD_REMOTE_VIDEO_SUBMIT_URL": f"{base_url}/video/jobs",
                "OPEN_HIGGSFIELD_REMOTE_LIPSYNC_SUBMIT_URL": f"{base_url}/lipsync/jobs",
            }
        )

        video = run(
            [
                "python3",
                "-m",
                "backend.runners.remote_video_runner",
                "--payload",
                str(video_payload),
                "--output",
                str(video_output),
            ],
            env=env,
        )
        lipsync = run(
            [
                "python3",
                "-m",
                "backend.runners.remote_lipsync_runner",
                "--payload",
                str(lipsync_payload),
                "--output",
                str(lipsync_output),
            ],
            env=env,
        )

        print(
            json.dumps(
                {
                    "video_exit": video.returncode,
                    "lipsync_exit": lipsync.returncode,
                    "video_output_exists": video_output.exists(),
                    "lipsync_output_exists": lipsync_output.exists(),
                    "video_stdout_tail": video.stdout[-400:],
                    "lipsync_stdout_tail": lipsync.stdout[-400:],
                },
                indent=2,
            )
        )

        return 0 if video.returncode == 0 and lipsync.returncode == 0 and video_output.exists() and lipsync_output.exists() else 1
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    raise SystemExit(main())
