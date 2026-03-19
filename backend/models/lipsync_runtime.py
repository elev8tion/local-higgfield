from __future__ import annotations

try:
    from backend.jobs.schemas import JobRecord
    from backend.models.command_runtime import execute_media_job_via_command
except ModuleNotFoundError:
    from jobs.schemas import JobRecord
    from models.command_runtime import execute_media_job_via_command


def execute_lipsync_job(job_id: str, record: JobRecord):
    return execute_media_job_via_command(
        job_id=job_id,
        record=record,
        runtime_name="lipsync-runtime",
        command_env_var="OPEN_HIGGSFIELD_LIPSYNC_COMMAND",
    )
