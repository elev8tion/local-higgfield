from __future__ import annotations

from pathlib import Path
from shutil import copyfile

try:
    from backend.jobs.schemas import AssetRef, JobRecord, JobResult
    from backend.storage.paths import job_output_path, output_url_for_path
except ModuleNotFoundError:
    from jobs.schemas import AssetRef, JobRecord, JobResult
    from storage.paths import job_output_path, output_url_for_path


DEMO_VIDEO_PATH = Path(__file__).resolve().parents[2] / "docs" / "assets" / "demo.mp4"


def build_placeholder_video_result(job_id: str, record: JobRecord, runtime_name: str) -> JobResult:
    output_path = job_output_path(job_id, ".mp4")
    copyfile(DEMO_VIDEO_PATH, output_path)
    output_url = output_url_for_path(output_path)

    return JobResult(
        output_path=str(output_path),
        output_url=output_url,
        assets=[
            AssetRef(
                kind="video",
                uri=output_url,
                role="primary_output",
                metadata={
                    "path": str(output_path),
                    "placeholder": True,
                    "runtime": runtime_name,
                    "source": str(DEMO_VIDEO_PATH),
                    "requested_model": record.params.get("model"),
                },
            )
        ],
        metadata={
            "placeholder": True,
            "runtime": runtime_name,
            "job_type": record.type.value,
        },
    )

