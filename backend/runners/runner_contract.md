# Runner Contract

This document defines the command-runner contract used by the backend media runtimes.

## Invocation

The backend expands these placeholders into the configured command:

- `{job_id}`
- `{payload_path}`
- `{output_path}`

Current default commands are configured in:

- `backend/models/runtime_config.env`
- `python3 -m backend.models.use_runtime_profile <profile>` can switch the active config

## Payload

`{payload_path}` points to a JSON-serialized `JobRecord` with:

- `id`
- `type`
- `prompt`
- `params`
- `input_assets`
- `created_at`
- `updated_at`

The runner should treat `input_assets` as the source of truth for uploaded media inputs.

## Required behavior

The runner must:

1. Read the payload JSON.
2. Produce the primary output file at `{output_path}`.
3. Exit with code `0` on success, non-zero on failure.

If the command exits successfully but does not create the output file, the backend will treat the job as failed.

## Optional structured stdout

If the runner prints a JSON object on its last stdout line, the backend will parse it and merge that into job result metadata.

Supported keys:

- `runtime`
- `mode`
- `job_type`
- `asset_kind`
- `resolution`
- `duration`
- `input_source`
- `assets`

Example:

```json
{
  "runtime": "video-runner",
  "mode": "ffmpeg",
  "job_type": "video.animate_image",
  "asset_kind": "video",
  "resolution": "1280x720",
  "duration": 2
}
```

`assets` may contain additional result assets:

```json
{
  "assets": [
    {
      "kind": "image",
      "uri": "/outputs/preview.png",
      "role": "preview_frame",
      "metadata": {
        "frame_index": 0
      }
    }
  ]
}
```

## Current default runners

- `python3 -m backend.runners.video_runner`
- `python3 -m backend.runners.lipsync_runner`

These are transitional local runners. A real GPU-backed runtime should preserve this contract so the backend API stays stable while the execution layer changes.

## Remote bridge runners

The repo also includes HTTP bridge runners:

- `python3 -m backend.runners.remote_video_runner`
- `python3 -m backend.runners.remote_lipsync_runner`

These runners:

1. POST the payload JSON to a configured remote endpoint.
2. Either read an immediate `output_url` from the response or poll a status endpoint until completion.
3. Download the resulting media file into `{output_path}`.
4. Print structured JSON metadata on stdout for the backend to merge into the job result.

Remote runner env vars:

- `OPEN_HIGGSFIELD_REMOTE_VIDEO_SUBMIT_URL`
- `OPEN_HIGGSFIELD_REMOTE_VIDEO_STATUS_URL_TEMPLATE`
- `OPEN_HIGGSFIELD_REMOTE_VIDEO_TOKEN`
- `OPEN_HIGGSFIELD_REMOTE_VIDEO_POLL_INTERVAL`
- `OPEN_HIGGSFIELD_REMOTE_VIDEO_MAX_ATTEMPTS`
- `OPEN_HIGGSFIELD_REMOTE_LIPSYNC_SUBMIT_URL`
- `OPEN_HIGGSFIELD_REMOTE_LIPSYNC_STATUS_URL_TEMPLATE`
- `OPEN_HIGGSFIELD_REMOTE_LIPSYNC_TOKEN`
- `OPEN_HIGGSFIELD_REMOTE_LIPSYNC_POLL_INTERVAL`
- `OPEN_HIGGSFIELD_REMOTE_LIPSYNC_MAX_ATTEMPTS`

Available built-in profiles:

- `local_ffmpeg`
- `remote_bridge`
