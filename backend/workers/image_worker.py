from __future__ import annotations

try:
    from backend.jobs.schemas import AssetRef, JobResult, JobStatus, JobType
    from backend.jobs.store import InMemoryJobStore
    from backend.storage.paths import job_output_path, output_url_for_path
except ModuleNotFoundError:
    from jobs.schemas import AssetRef, JobResult, JobStatus, JobType
    from jobs.store import InMemoryJobStore
    from storage.paths import job_output_path, output_url_for_path


def process_image_job(job_id: str, store: InMemoryJobStore) -> None:
    record = store.get(job_id)
    if not record:
        return

    if record.type not in {JobType.IMAGE_GENERATE, JobType.IMAGE_TRANSFORM}:
        store.set_status(job_id, JobStatus.FAILED, f"Unsupported image job type: {record.type}")
        return

    store.set_status(job_id, JobStatus.PROCESSING, error=None)

    try:
        from diffusers import AutoPipelineForText2Image
        import torch

        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            variant="fp16" if torch.cuda.is_available() else None,
        )

        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

        image = pipe(
            prompt=record.prompt,
            num_inference_steps=1,
            guidance_scale=0.0,
        ).images[0]

        output_path = job_output_path(job_id)
        image.save(output_path)

        result = JobResult(
            output_path=str(output_path),
            output_url=output_url_for_path(output_path),
            assets=[
                AssetRef(
                    kind="image",
                    uri=output_url_for_path(output_path),
                    role="primary_output",
                    metadata={"path": str(output_path)},
                )
            ],
        )
        store.set_result(job_id, result)
    except Exception as exc:
        store.set_status(job_id, JobStatus.FAILED, str(exc))
