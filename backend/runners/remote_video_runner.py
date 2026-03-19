from __future__ import annotations

import argparse
import json

from .remote_media_runner import execute_remote_media_runner


def main() -> int:
    parser = argparse.ArgumentParser(description="Open Higgsfield remote video bridge runner")
    parser.add_argument("--payload", required=True, help="Path to a job payload JSON file")
    parser.add_argument("--output", required=True, help="Path to write the output media file")
    args = parser.parse_args()

    result = execute_remote_media_runner(
        payload_path=args.payload,
        output_path=args.output,
        runtime_name="remote-video-runner",
        submit_url_env_var="OPEN_HIGGSFIELD_REMOTE_VIDEO_SUBMIT_URL",
        token_env_var="OPEN_HIGGSFIELD_REMOTE_VIDEO_TOKEN",
        status_url_template_env_var="OPEN_HIGGSFIELD_REMOTE_VIDEO_STATUS_URL_TEMPLATE",
        poll_interval_env_var="OPEN_HIGGSFIELD_REMOTE_VIDEO_POLL_INTERVAL",
        max_attempts_env_var="OPEN_HIGGSFIELD_REMOTE_VIDEO_MAX_ATTEMPTS",
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
