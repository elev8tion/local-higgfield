from __future__ import annotations

import argparse
import json

from .common import DEFAULT_FPS, ffmpeg_or_fallback, find_input_asset, load_payload, resolve_dimensions


def run(payload_path: str, output_path: str) -> dict:
    payload = load_payload(payload_path)
    params = payload.get("params", {})
    job_type = payload.get("type")
    width, height = resolve_dimensions(params.get("resolution"), "16:9")

    if job_type == "lipsync.image_audio":
        source_image = find_input_asset(payload, {"image"})
        source_audio = find_input_asset(payload, {"audio"})
        if not source_image or not source_audio:
            raise RuntimeError("lipsync.image_audio runner requires both image and audio assets")
        ffmpeg_result = ffmpeg_or_fallback(
            [
                "-loop",
                "1",
                "-framerate",
                str(DEFAULT_FPS),
                "-i",
                source_image,
                "-i",
                source_audio,
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},fps={DEFAULT_FPS},format=yuv420p",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                output_path,
            ],
            output_path,
        )
        input_source = source_image
    elif job_type == "lipsync.video_audio":
        source_video = find_input_asset(payload, {"video"})
        source_audio = find_input_asset(payload, {"audio"})
        if not source_video or not source_audio:
            raise RuntimeError("lipsync.video_audio runner requires both video and audio assets")
        ffmpeg_result = ffmpeg_or_fallback(
            [
                "-i",
                source_video,
                "-i",
                source_audio,
                "-map",
                "0:v:0",
                "-map",
                "1:a:0",
                "-vf",
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black,fps={DEFAULT_FPS}",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-shortest",
                output_path,
            ],
            output_path,
            source_video,
        )
        input_source = source_video
    else:
        raise RuntimeError(f"Unsupported lipsync runner job type: {job_type}")

    return {
        "runtime": "lipsync-runner",
        "job_type": job_type,
        "mode": ffmpeg_result["mode"],
        "input_source": input_source,
        "resolution": f"{width}x{height}",
        "output_path": ffmpeg_result["output_path"],
        "stderr_tail": ffmpeg_result["stderr_tail"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Open Higgsfield local lipsync runner")
    parser.add_argument("--payload", required=True, help="Path to a job payload JSON file")
    parser.add_argument("--output", required=True, help="Path to write the output media file")
    args = parser.parse_args()

    result = run(args.payload, args.output)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
