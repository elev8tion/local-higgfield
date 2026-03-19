from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

try:
    from backend.jobs.schemas import AssetRef, JobRecord, JobResult
    from backend.models.runtime_config import load_runtime_config
    from backend.models.runtime_common import build_placeholder_video_result
    from backend.storage.paths import ensure_output_dir, job_output_path, output_url_for_path
except ModuleNotFoundError:
    from jobs.schemas import AssetRef, JobRecord, JobResult
    from models.runtime_config import load_runtime_config
    from models.runtime_common import build_placeholder_video_result
    from storage.paths import ensure_output_dir, job_output_path, output_url_for_path


def _write_payload(job_id: str, record: JobRecord) -> Path:
    work_dir = ensure_output_dir() / "runtime_payloads"
    work_dir.mkdir(parents=True, exist_ok=True)
    payload_path = work_dir / f"{job_id}.json"
    payload_path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
    return payload_path


def _build_command(command_template: str, *, job_id: str, payload_path: Path, output_path: Path) -> str:
    return command_template.format(
        job_id=job_id,
        payload_path=str(payload_path),
        output_path=str(output_path),
    )


def _parse_runner_metadata(stdout: str) -> dict:
    for line in reversed(stdout.splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def _build_result(
    output_path: Path,
    runtime_name: str,
    record: JobRecord,
    stdout: str,
    stderr: str,
    runner_metadata: dict,
) -> JobResult:
    output_url = output_url_for_path(output_path)
    asset_kind = runner_metadata.get("asset_kind", "video")
    return JobResult(
        output_path=str(output_path),
        output_url=output_url,
        assets=[
            AssetRef(
                kind=asset_kind,
                uri=output_url,
                role="primary_output",
                metadata={
                    "path": str(output_path),
                    "runtime": runtime_name,
                    "requested_model": record.params.get("model"),
                    **{k: v for k, v in runner_metadata.items() if k not in {"assets", "asset_kind"}},
                },
            )
        ]
        + [
            AssetRef(
                kind=asset.get("kind", asset_kind),
                uri=asset.get("uri", output_url),
                role=asset.get("role"),
                metadata=asset.get("metadata", {}),
            )
            for asset in runner_metadata.get("assets", [])
            if isinstance(asset, dict)
        ],
        metadata={
            "runtime": runtime_name,
            "execution_mode": "configured_command",
            "job_type": record.type.value,
            "stdout_tail": stdout[-2000:],
            "stderr_tail": stderr[-2000:],
            "runner": runner_metadata,
        },
    )


def execute_media_job_via_command(
    *,
    job_id: str,
    record: JobRecord,
    runtime_name: str,
    command_env_var: str,
    output_extension: str = ".mp4",
):
    load_runtime_config()
    command_template = os.getenv(command_env_var, "").strip()
    if not command_template:
        return build_placeholder_video_result(job_id, record, runtime_name=f"{runtime_name}-placeholder")

    payload_path = _write_payload(job_id, record)
    output_path = job_output_path(job_id, output_extension)
    command = _build_command(
        command_template,
        job_id=job_id,
        payload_path=payload_path,
        output_path=output_path,
    )

    completed = subprocess.run(
        command,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            f"{runtime_name} command failed with exit code {completed.returncode}: {completed.stderr[-500:]}"
        )

    if not output_path.exists():
        raise RuntimeError(
            f"{runtime_name} command completed but did not create output file at {output_path}"
        )

    runner_metadata = _parse_runner_metadata(completed.stdout)
    return _build_result(output_path, runtime_name, record, completed.stdout, completed.stderr, runner_metadata)
