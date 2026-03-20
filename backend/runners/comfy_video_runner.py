from __future__ import annotations

import argparse
import json

from .comfy_media_runner import execute_comfy_media_runner


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Open Higgsfield video jobs against a ComfyUI worker")
    parser.add_argument("--payload", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    result = execute_comfy_media_runner(
        payload_path=args.payload,
        output_path=args.output,
        runtime_name="comfy-video-runner",
        asset_kind="video",
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
