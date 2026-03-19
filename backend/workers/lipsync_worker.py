from __future__ import annotations

try:
    from backend.jobs.schemas import JobStatus, JobType
    from backend.jobs.store import InMemoryJobStore
    from backend.models.lipsync_runtime import execute_lipsync_job
except ModuleNotFoundError:
    from jobs.schemas import JobStatus, JobType
    from jobs.store import InMemoryJobStore
    from models.lipsync_runtime import execute_lipsync_job


def process_lipsync_job(job_id: str, store: InMemoryJobStore) -> None:
    record = store.get(job_id)
    if not record:
        return

    if record.type not in {JobType.LIPSYNC_IMAGE_AUDIO, JobType.LIPSYNC_VIDEO_AUDIO}:
        store.set_status(job_id, JobStatus.FAILED, f"Unsupported lipsync job type: {record.type}")
        return

    store.set_status(job_id, JobStatus.PROCESSING, error=None)

    try:
        result = execute_lipsync_job(job_id, record)
        store.set_result(job_id, result)
    except Exception as exc:
        store.set_status(job_id, JobStatus.FAILED, str(exc))
