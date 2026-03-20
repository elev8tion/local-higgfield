from __future__ import annotations

import json
import os
import re
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from .common import ensure_parent, find_input_asset, load_payload, resolve_dimensions


PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}")
DEFAULT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "workflows" / "comfy"
PREFERRED_MEDIA_KEYS = ("videos", "gifs", "images")

WORKFLOW_ENV_BY_JOB_TYPE = {
    "video.generate": "OPEN_HIGGSFIELD_COMFY_VIDEO_GENERATE_WORKFLOW",
    "video.animate_image": "OPEN_HIGGSFIELD_COMFY_VIDEO_ANIMATE_IMAGE_WORKFLOW",
    "video.transform": "OPEN_HIGGSFIELD_COMFY_VIDEO_TRANSFORM_WORKFLOW",
    "lipsync.image_audio": "OPEN_HIGGSFIELD_COMFY_LIPSYNC_IMAGE_AUDIO_WORKFLOW",
    "lipsync.video_audio": "OPEN_HIGGSFIELD_COMFY_LIPSYNC_VIDEO_AUDIO_WORKFLOW",
}

DEFAULT_TEMPLATE_BY_JOB_TYPE = {
    "video.generate": "video.generate.json",
    "video.animate_image": "video.animate_image.json",
    "video.transform": "video.transform.json",
    "lipsync.image_audio": "lipsync.image_audio.json",
    "lipsync.video_audio": "lipsync.video_audio.json",
}


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    token = _env("OPEN_HIGGSFIELD_COMFY_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = dict(headers or {})
    data = None
    if body is not None:
        request_headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url, data=data, method=method, headers=request_headers)
    with urllib.request.urlopen(request, timeout=300) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        text = response.read().decode(charset)
    if not text.strip():
        return {}
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object from ComfyUI, got {type(payload).__name__}")
    return payload


def _download_file(url: str, output_path: str, headers: dict[str, str]) -> str:
    final_path = ensure_parent(output_path)
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=300) as response:
        final_path.write_bytes(response.read())
    return str(final_path)


def _job_context(payload: dict[str, Any], output_path: str) -> dict[str, Any]:
    params = payload.get("params", {}) if isinstance(payload.get("params"), dict) else {}
    resolution = str(params.get("resolution", "") or "").strip() or None
    aspect_ratio = str(params.get("aspectRatio", "") or params.get("aspect_ratio", "") or "").strip() or None
    width, height = resolve_dimensions(resolution, aspect_ratio)

    image_path = find_input_asset(payload, {"image"})
    video_path = find_input_asset(payload, {"video"})
    audio_path = find_input_asset(payload, {"audio"})

    output = Path(output_path)
    return {
        "job": payload,
        "job_id": payload.get("id", ""),
        "job_type": payload.get("type", ""),
        "prompt": payload.get("prompt", ""),
        "params": params,
        "assets": {
            "image_path": image_path or "",
            "video_path": video_path or "",
            "audio_path": audio_path or "",
            "comfy_image_name": "",
            "comfy_image_path": "",
            "comfy_video_name": "",
            "comfy_video_path": "",
            "comfy_audio_name": "",
            "comfy_audio_path": "",
        },
        "resolution": resolution or "",
        "aspect_ratio": aspect_ratio or "",
        "width": width,
        "height": height,
        "output": {
            "path": str(output),
            "filename": output.name,
            "stem": output.stem,
            "directory": str(output.parent),
        },
    }


def _stage_comfy_inputs(context: dict[str, Any]) -> None:
    input_dir = Path(_env("OPEN_HIGGSFIELD_COMFY_INPUT_DIR", "/workspace/ComfyUI/input"))
    input_dir.mkdir(parents=True, exist_ok=True)

    assets = context.get("assets", {})
    if not isinstance(assets, dict):
        return

    job_id = str(context.get("job_id", "") or context.get("output", {}).get("stem", "") or "job")
    safe_job_id = re.sub(r"[^a-zA-Z0-9._-]+", "_", job_id).strip("_") or "job"

    for kind in ("image", "video", "audio"):
        source = str(assets.get(f"{kind}_path", "") or "").strip()
        if not source:
            continue

        source_path = Path(source)
        if not source_path.exists():
            continue

        suffix = source_path.suffix or {
            "image": ".png",
            "video": ".mp4",
            "audio": ".wav",
        }[kind]
        staged_name = f"open_higgsfield_{safe_job_id}_{kind}{suffix}"
        staged_path = input_dir / staged_name
        if source_path.resolve() != staged_path.resolve():
            shutil.copy2(source_path, staged_path)
        assets[f"comfy_{kind}_name"] = staged_name
        assets[f"comfy_{kind}_path"] = str(staged_path)


def _lookup(context: dict[str, Any], key: str) -> Any:
    current: Any = context
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return ""
    return current


def _render_string(template: str, context: dict[str, Any]) -> Any:
    exact = PLACEHOLDER_PATTERN.fullmatch(template)
    if exact:
        return _lookup(context, exact.group(1))

    def replace(match: re.Match[str]) -> str:
        value = _lookup(context, match.group(1))
        if value is None:
            return ""
        return str(value)

    return PLACEHOLDER_PATTERN.sub(replace, template)


def _render(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return _render_string(value, context)
    if isinstance(value, list):
        return [_render(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render(item, context) for key, item in value.items()}
    return value


def _workflow_template_path(job_type: str) -> Path:
    env_var = WORKFLOW_ENV_BY_JOB_TYPE.get(job_type)
    configured = _env(env_var) if env_var else ""
    if configured:
        return Path(configured)

    default_name = DEFAULT_TEMPLATE_BY_JOB_TYPE.get(job_type)
    if not default_name:
        raise RuntimeError(f"No Comfy workflow template mapping for job type {job_type}")
    return DEFAULT_TEMPLATE_ROOT / default_name


def _load_workflow_template(job_type: str) -> tuple[dict[str, Any], list[str] | None]:
    template_path = _workflow_template_path(job_type)
    if not template_path.exists():
        raise RuntimeError(
            f"Missing Comfy workflow template for {job_type}: {template_path}. "
            "Set the matching OPEN_HIGGSFIELD_COMFY_*_WORKFLOW env var to an exported Comfy API workflow JSON."
        )
    raw = json.loads(template_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "prompt" in raw and isinstance(raw["prompt"], dict):
        metadata = raw.get("metadata", {})
        output_nodes = metadata.get("output_node_ids") if isinstance(metadata, dict) else None
        return raw["prompt"], output_nodes if isinstance(output_nodes, list) else None
    if isinstance(raw, dict):
        metadata = raw.get("metadata", {})
        output_nodes = metadata.get("output_node_ids") if isinstance(metadata, dict) else None
        prompt = {key: value for key, value in raw.items() if key != "metadata"}
        return prompt, output_nodes if isinstance(output_nodes, list) else None
    raise RuntimeError(f"Unsupported Comfy workflow template shape at {template_path}")


def _join_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _submit_prompt(base_url: str, prompt: dict[str, Any], headers: dict[str, str]) -> str:
    response = _request_json(
        _join_url(base_url, "/prompt"),
        method="POST",
        body={"prompt": prompt},
        headers=headers,
    )
    prompt_id = str(response.get("prompt_id", "")).strip()
    if not prompt_id:
        raise RuntimeError(f"ComfyUI submit response did not include prompt_id: {response}")
    return prompt_id


def _extract_history_entry(history_payload: dict[str, Any], prompt_id: str) -> dict[str, Any] | None:
    if prompt_id in history_payload and isinstance(history_payload[prompt_id], dict):
        return history_payload[prompt_id]
    if history_payload.get("prompt_id") == prompt_id:
        return history_payload
    return None


def _poll_history(base_url: str, prompt_id: str, headers: dict[str, str]) -> dict[str, Any]:
    poll_interval = float(_env("OPEN_HIGGSFIELD_COMFY_POLL_INTERVAL", "2.0"))
    max_attempts = int(_env("OPEN_HIGGSFIELD_COMFY_MAX_ATTEMPTS", "300"))
    history_url = _join_url(base_url, f"/history/{prompt_id}")

    for _ in range(max_attempts):
        payload = _request_json(history_url, headers=headers)
        entry = _extract_history_entry(payload, prompt_id)
        if entry and isinstance(entry.get("outputs"), dict) and entry["outputs"]:
            return entry
        time.sleep(poll_interval)

    raise RuntimeError(f"ComfyUI prompt {prompt_id} did not complete after {max_attempts} polls")


def _first_output_file(outputs: dict[str, Any], output_node_ids: list[str] | None) -> dict[str, Any] | None:
    node_ids = output_node_ids or list(outputs.keys())
    for node_id in node_ids:
        node_output = outputs.get(node_id, {})
        if not isinstance(node_output, dict):
            continue
        for key in PREFERRED_MEDIA_KEYS:
            items = node_output.get(key)
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and item.get("filename"):
                        result = dict(item)
                        result["_media_key"] = key
                        result["_node_id"] = node_id
                        return result
    return None


def _view_url(base_url: str, file_payload: dict[str, Any]) -> str:
    query = urllib.parse.urlencode(
        {
            "filename": file_payload.get("filename", ""),
            "subfolder": file_payload.get("subfolder", ""),
            "type": file_payload.get("type", "output"),
        }
    )
    return _join_url(base_url, f"/view?{query}")


def execute_comfy_media_runner(
    *,
    payload_path: str,
    output_path: str,
    runtime_name: str,
    asset_kind: str = "video",
) -> dict[str, Any]:
    base_url = _env("OPEN_HIGGSFIELD_COMFY_BASE_URL")
    if not base_url:
        raise RuntimeError("Missing OPEN_HIGGSFIELD_COMFY_BASE_URL for ComfyUI runner")

    payload = load_payload(payload_path)
    job_type = str(payload.get("type", "")).strip()
    if not job_type:
        raise RuntimeError("Runner payload is missing job type")

    workflow_template, output_node_ids = _load_workflow_template(job_type)
    context = _job_context(payload, output_path)
    _stage_comfy_inputs(context)
    prompt = _render(workflow_template, context)
    if not isinstance(prompt, dict):
        raise RuntimeError("Rendered Comfy workflow prompt must be a JSON object")

    headers = _headers()
    prompt_id = _submit_prompt(base_url, prompt, headers)
    history_entry = _poll_history(base_url, prompt_id, headers)
    outputs = history_entry.get("outputs")
    if not isinstance(outputs, dict):
        raise RuntimeError(f"ComfyUI history did not contain outputs for prompt {prompt_id}")

    output_file = _first_output_file(outputs, output_node_ids)
    if not output_file:
        raise RuntimeError(f"ComfyUI history completed without downloadable media for prompt {prompt_id}")

    download_url = _view_url(base_url, output_file)
    written_output = _download_file(download_url, output_path, headers)

    return {
        "runtime": runtime_name,
        "mode": "comfy-http",
        "job_type": job_type,
        "asset_kind": asset_kind,
        "output_path": written_output,
        "remote_prompt_id": prompt_id,
        "remote_base_url": base_url,
        "remote_output_url": download_url,
        "workflow_env_var": WORKFLOW_ENV_BY_JOB_TYPE.get(job_type),
        "history": {
            "status": "completed",
            "node_id": output_file.get("_node_id"),
            "media_key": output_file.get("_media_key"),
            "filename": output_file.get("filename"),
            "subfolder": output_file.get("subfolder", ""),
        },
    }
