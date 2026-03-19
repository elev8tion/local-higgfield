from __future__ import annotations

import argparse
import json

from .common import (
    DEFAULT_FPS,
    copy_video_output,
    ffmpeg_or_fallback,
    find_input_asset,
    load_payload,
    resolve_dimensions,
)


def _duration_for(payload: dict) -> int:
    try:
        return max(1, int(payload.get("params", {}).get("duration", 5)))
    except (TypeError, ValueError):
        return 5


def run(payload_path: str, output_path: str) -> dict:
    payload = load_payload(payload_path)
    params = payload.get("params", {})
    job_type = payload.get("type")
    duration = _duration_for(payload)
    width, height = resolve_dimensions(params.get("resolution"), params.get("aspect_ratio"))

    if job_type == "video.generate":
        ffmpeg_result = ffmpeg_or_fallback(
            [
                "-f",
                "lavfi",
                "-i",
                f"testsrc2=size={width}x{height}:rate={DEFAULT_FPS}",
                "-t",
                str(duration),
                "-pix_fmt",
                "yuv420p",
                output_path,
            ],
            output_path,
        )
    elif job_type == "video.animate_image":
        source_image = find_input_asset(payload, {"image"})
        if not source_image:
            raise RuntimeError("video.animate_image runner did not receive a source image")
        ffmpeg_result = ffmpeg_or_fallback(
            [
                "-loop",
                "1",
                "-framerate",
                str(DEFAULT_FPS),
                "-i",
                source_image,
                "-t",
                str(duration),
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={DEFAULT_FPS},format=yuv420p",
                "-pix_fmt",
                "yuv420p",
                output_path,
            ],
            output_path,
        )
    elif job_type == "video.transform":
        source_video = find_input_asset(payload, {"video"})
        if not source_video:
            raise RuntimeError("video.transform runner did not receive a source video")
        ffmpeg_result = ffmpeg_or_fallback(
            [
                "-i",
                source_video,
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps={DEFAULT_FPS}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                output_path,
            ],
            output_path,
            source_video,
        )
    else:
        source_path = find_input_asset(payload, {"video"})
        written_output = copy_video_output(output_path, source_path)
        return {
            "runtime": "video-runner",
            "job_type": job_type,
            "mode": "fallback-copy",
            "input_source": source_path or "demo.mp4",
            "output_path": written_output,
        }

    return {
        "runtime": "video-runner",
        "job_type": job_type,
        "mode": ffmpeg_result["mode"],
        "resolution": f"{width}x{height}",
        "duration": duration,
        "output_path": ffmpeg_result["output_path"],
        "stderr_tail": ffmpeg_result["stderr_tail"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Open Higgsfield local video runner")
    parser.add_argument("--payload", required=True, help="Path to a job payload JSON file")
    parser.add_argument("--output", required=True, help="Path to write the output media file")
    args = parser.parse_args()

    result = run(args.payload, args.output)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
