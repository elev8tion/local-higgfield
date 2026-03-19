from __future__ import annotations

try:
    from backend.jobs.schemas import JobType
    from backend.models.registry import get_job_type_metadata
except ModuleNotFoundError:
    from jobs.schemas import JobType
    from models.registry import get_job_type_metadata


FRONTEND_MODEL_CAPABILITIES = {
    JobType.IMAGE_GENERATE: {
        "id": "local-image-generate",
        "name": "Local Image Generate",
        "inputs": {
            "prompt": {"type": "string", "required": True},
            "aspect_ratio": {"type": "string", "required": False},
            "resolution": {"type": "string", "required": False},
        },
    },
    JobType.IMAGE_TRANSFORM: {
        "id": "local-image-transform",
        "name": "Local Image Transform",
        "inputs": {
            "prompt": {"type": "string", "required": False},
            "input_assets": {"type": "image[]", "required": True},
        },
    },
    JobType.VIDEO_GENERATE: {
        "id": "local-video-generate",
        "name": "Local Video Generate",
        "inputs": {
            "prompt": {"type": "string", "required": True},
        },
    },
    JobType.VIDEO_ANIMATE_IMAGE: {
        "id": "local-video-animate-image",
        "name": "Local Image to Video",
        "inputs": {
            "prompt": {"type": "string", "required": False},
            "input_assets": {"type": "image[]", "required": True},
        },
    },
    JobType.VIDEO_TRANSFORM: {
        "id": "local-video-transform",
        "name": "Local Video Transform",
        "inputs": {
            "input_assets": {"type": "video[]", "required": True},
        },
    },
    JobType.LIPSYNC_IMAGE_AUDIO: {
        "id": "local-lipsync-image-audio",
        "name": "Local Image + Audio Lip Sync",
        "inputs": {
            "input_assets": {"type": "image[]|audio[]", "required": True},
        },
    },
    JobType.LIPSYNC_VIDEO_AUDIO: {
        "id": "local-lipsync-video-audio",
        "name": "Local Video + Audio Lip Sync",
        "inputs": {
            "input_assets": {"type": "video[]|audio[]", "required": True},
        },
    },
}


def list_frontend_models() -> list[dict]:
    return [
        {
            **FRONTEND_MODEL_CAPABILITIES[job_type],
            "job_type": job_type.value,
            "implemented": metadata["implemented"],
            "category": metadata["category"],
            "runtime": metadata["runtime"],
            "contract": metadata["contract"],
        }
        for job_type in JobType
        for metadata in [get_job_type_metadata(job_type)]
    ]


def get_registry_summary() -> list[dict]:
    return [
        {"job_type": job_type.value, **get_job_type_metadata(job_type)}
        for job_type in JobType
    ]
