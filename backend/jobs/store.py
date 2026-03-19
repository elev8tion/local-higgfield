from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from .schemas import JobRecord, JobRequest, JobResult, JobStatus


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}
        self._lock = Lock()

    def create(self, request: JobRequest) -> JobRecord:
        timestamp = utc_now_iso()
        record = JobRecord(
            id=str(uuid4()),
            type=request.normalized_type(),
            prompt=request.prompt,
            status=JobStatus.QUEUED,
            params=request.params,
            input_assets=request.input_assets,
            created_at=timestamp,
            updated_at=timestamp,
        )
        with self._lock:
            self._jobs[record.id] = record
        return record

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._jobs.get(job_id)

    def set_status(self, job_id: str, status: JobStatus, error: str | None = None) -> JobRecord | None:
        with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.status = status
            record.updated_at = utc_now_iso()
            if error is not None:
                record.error = error
            return record

    def set_result(self, job_id: str, result: JobResult) -> JobRecord | None:
        with self._lock:
            record = self._jobs.get(job_id)
            if not record:
                return None
            record.result = result
            record.error = None
            record.status = JobStatus.COMPLETED
            record.updated_at = utc_now_iso()
            return record

