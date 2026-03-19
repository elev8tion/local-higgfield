from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .common import ensure_parent, load_payload


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _headers(token_env_var: str | None = None) -> dict[str, str]:
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token_env_var:
        token = _env(token_env_var)
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def _request_json(url: str, *, method: str = "GET", body: dict | None = None, headers: dict | None = None) -> dict:
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    with urllib.request.urlopen(request, timeout=120) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        payload = response.read().decode(charset)
        if not payload.strip():
            return {}
        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise RuntimeError(f"Expected JSON object from remote runner endpoint, got: {type(parsed).__name__}")
        return parsed


def _download_to_path(url: str, output_path: str, headers: dict | None = None) -> str:
    final_path = ensure_parent(output_path)
    request = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(request, timeout=300) as response:
        final_path.write_bytes(response.read())
    return str(final_path)


def _extract_output_url(payload: dict) -> str | None:
    if payload.get("output_url"):
        return payload["output_url"]

    result = payload.get("result")
    if isinstance(result, dict):
        if result.get("output_url"):
            return result["output_url"]
        assets = result.get("assets")
        if isinstance(assets, list):
            for asset in assets:
                if isinstance(asset, dict) and asset.get("uri"):
                    return asset["uri"]

    assets = payload.get("assets")
    if isinstance(assets, list):
        for asset in assets:
            if isinstance(asset, dict) and asset.get("uri"):
                return asset["uri"]

    return None


def _extract_status_url(payload: dict, template: str | None) -> str | None:
    for key in ("status_url", "poll_url"):
        if payload.get(key):
            return payload[key]

    remote_job_id = payload.get("job_id") or payload.get("id")
    if template and remote_job_id:
        return template.format(job_id=remote_job_id)
    return None


def _join_url(base_url: str, maybe_relative: str) -> str:
    if maybe_relative.startswith("http://") or maybe_relative.startswith("https://"):
        return maybe_relative
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", maybe_relative.lstrip("/"))


def _poll_until_complete(
    *,
    status_url: str,
    headers: dict[str, str],
    poll_interval: float,
    max_attempts: int,
) -> dict:
    for _ in range(max_attempts):
        payload = _request_json(status_url, headers=headers)
        status = str(payload.get("status", "")).lower()
        if status in {"completed", "complete", "succeeded", "success"}:
            return payload
        if status in {"failed", "cancelled", "canceled", "error"}:
            raise RuntimeError(payload.get("error") or f"Remote job failed with status: {status}")
        time.sleep(poll_interval)
    raise RuntimeError(f"Remote job did not complete after {max_attempts} polling attempts")


def execute_remote_media_runner(
    *,
    payload_path: str,
    output_path: str,
    runtime_name: str,
    submit_url_env_var: str,
    token_env_var: str | None = None,
    status_url_template_env_var: str | None = None,
    poll_interval_env_var: str | None = None,
    max_attempts_env_var: str | None = None,
) -> dict:
    payload = load_payload(payload_path)
    submit_url = _env(submit_url_env_var)
    if not submit_url:
        raise RuntimeError(f"{runtime_name} is not configured: missing {submit_url_env_var}")

    headers = _headers(token_env_var)
    submit_response = _request_json(submit_url, method="POST", body=payload, headers=headers)

    output_url = _extract_output_url(submit_response)
    final_response = submit_response

    if not output_url:
        status_url_template = _env(status_url_template_env_var) if status_url_template_env_var else ""
        status_url = _extract_status_url(submit_response, status_url_template or None)
        if not status_url:
            raise RuntimeError(f"{runtime_name} submit response did not contain output or polling information")

        submit_base = submit_url
        status_url = _join_url(submit_base, status_url)
        poll_interval = float(_env(poll_interval_env_var, "2.0")) if poll_interval_env_var else 2.0
        max_attempts = int(_env(max_attempts_env_var, "300")) if max_attempts_env_var else 300
        final_response = _poll_until_complete(
            status_url=status_url,
            headers=headers,
            poll_interval=poll_interval,
            max_attempts=max_attempts,
        )
        output_url = _extract_output_url(final_response)

    if not output_url:
        raise RuntimeError(f"{runtime_name} completed without an output URL")

    output_url = _join_url(submit_url, output_url)
    written_output = _download_to_path(output_url, output_path, headers=headers)

    return {
        "runtime": runtime_name,
        "mode": "remote-http",
        "job_type": payload.get("type"),
        "asset_kind": "video",
        "output_path": written_output,
        "remote_submit_url": submit_url,
        "remote_output_url": output_url,
        "remote_response": final_response,
    }
