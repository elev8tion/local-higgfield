from __future__ import annotations

from threading import Thread

try:
    from backend.jobs.schemas import JobType
    from backend.jobs.store import InMemoryJobStore
    from backend.workers.image_worker import process_image_job
    from backend.workers.lipsync_worker import process_lipsync_job
    from backend.workers.video_worker import process_video_job
except ModuleNotFoundError:
    from jobs.schemas import JobType
    from jobs.store import InMemoryJobStore
    from workers.image_worker import process_image_job
    from workers.lipsync_worker import process_lipsync_job
    from workers.video_worker import process_video_job


def dispatch_job(job_id: str, job_type: JobType, store: InMemoryJobStore) -> bool:
    if job_type in {JobType.IMAGE_GENERATE, JobType.IMAGE_TRANSFORM}:
        Thread(target=process_image_job, args=(job_id, store), daemon=True).start()
        return True
    if job_type in {JobType.VIDEO_GENERATE, JobType.VIDEO_ANIMATE_IMAGE, JobType.VIDEO_TRANSFORM}:
        Thread(target=process_video_job, args=(job_id, store), daemon=True).start()
        return True
    if job_type in {JobType.LIPSYNC_IMAGE_AUDIO, JobType.LIPSYNC_VIDEO_AUDIO}:
        Thread(target=process_lipsync_job, args=(job_id, store), daemon=True).start()
        return True
    return False
