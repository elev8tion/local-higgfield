from __future__ import annotations

import os

try:
    from backend.jobs.schemas import JobType
except ModuleNotFoundError:
    from jobs.schemas import JobType


JOB_TYPE_REGISTRY = {
    JobType.IMAGE_GENERATE: {
        "implemented": True,
        "worker": "image_worker",
        "label": "Text to Image",
        "description": "Generate an image from a text prompt.",
        "category": "image",
        "contract": {
            "prompt_required": True,
            "accepted_asset_kinds": [],
            "required_asset_kinds": [],
            "min_input_assets": 0,
            "max_input_assets": 0,
        },
        "runtime": {
            "mode": "native",
            "configured": True,
            "placeholder_fallback": False,
            "command_env_var": None,
        },
    },
    JobType.IMAGE_TRANSFORM: {
        "implemented": True,
        "worker": "image_worker",
        "label": "Image to Image",
        "description": "Transform one or more input images using prompt-driven generation.",
        "category": "image",
        "contract": {
            "prompt_required": False,
            "accepted_asset_kinds": ["image"],
            "required_asset_kinds": ["image"],
            "min_input_assets": 1,
            "max_input_assets": 8,
        },
        "runtime": {
            "mode": "native",
            "configured": True,
            "placeholder_fallback": False,
            "command_env_var": None,
        },
    },
    JobType.VIDEO_GENERATE: {
        "implemented": True,
        "worker": "video_worker",
        "label": "Text to Video",
        "description": "Generate a video from a text prompt.",
        "category": "video",
        "contract": {
            "prompt_required": True,
            "accepted_asset_kinds": [],
            "required_asset_kinds": [],
            "min_input_assets": 0,
            "max_input_assets": 0,
        },
        "runtime": {
            "mode": "command",
            "configured": False,
            "placeholder_fallback": True,
            "command_env_var": "OPEN_HIGGSFIELD_VIDEO_COMMAND",
        },
    },
    JobType.VIDEO_ANIMATE_IMAGE: {
        "implemented": True,
        "worker": "video_worker",
        "label": "Image to Video",
        "description": "Animate an input image into a video.",
        "category": "video",
        "contract": {
            "prompt_required": False,
            "accepted_asset_kinds": ["image"],
            "required_asset_kinds": ["image"],
            "min_input_assets": 1,
            "max_input_assets": 1,
        },
        "runtime": {
            "mode": "command",
            "configured": False,
            "placeholder_fallback": True,
            "command_env_var": "OPEN_HIGGSFIELD_VIDEO_COMMAND",
        },
    },
    JobType.VIDEO_TRANSFORM: {
        "implemented": True,
        "worker": "video_worker",
        "label": "Video to Video",
        "description": "Transform a source video into a derived output.",
        "category": "video",
        "contract": {
            "prompt_required": False,
            "accepted_asset_kinds": ["video"],
            "required_asset_kinds": ["video"],
            "min_input_assets": 1,
            "max_input_assets": 1,
        },
        "runtime": {
            "mode": "command",
            "configured": False,
            "placeholder_fallback": True,
            "command_env_var": "OPEN_HIGGSFIELD_VIDEO_COMMAND",
        },
    },
    JobType.LIPSYNC_IMAGE_AUDIO: {
        "implemented": True,
        "worker": "lipsync_worker",
        "label": "Image + Audio Lip Sync",
        "description": "Drive a portrait image using an audio source.",
        "category": "lipsync",
        "contract": {
            "prompt_required": False,
            "accepted_asset_kinds": ["image", "audio"],
            "required_asset_kinds": ["image", "audio"],
            "min_input_assets": 2,
            "max_input_assets": 2,
        },
        "runtime": {
            "mode": "command",
            "configured": False,
            "placeholder_fallback": True,
            "command_env_var": "OPEN_HIGGSFIELD_LIPSYNC_COMMAND",
        },
    },
    JobType.LIPSYNC_VIDEO_AUDIO: {
        "implemented": True,
        "worker": "lipsync_worker",
        "label": "Video + Audio Lip Sync",
        "description": "Drive an existing video using an audio source.",
        "category": "lipsync",
        "contract": {
            "prompt_required": False,
            "accepted_asset_kinds": ["video", "audio"],
            "required_asset_kinds": ["video", "audio"],
            "min_input_assets": 2,
            "max_input_assets": 2,
        },
        "runtime": {
            "mode": "command",
            "configured": False,
            "placeholder_fallback": True,
            "command_env_var": "OPEN_HIGGSFIELD_LIPSYNC_COMMAND",
        },
    },
}


def _with_runtime_status(metadata: dict) -> dict:
    runtime = dict(metadata.get("runtime", {}))
    command_env_var = runtime.get("command_env_var")
    if command_env_var:
        runtime["configured"] = bool(os.getenv(command_env_var, "").strip())
    return {**metadata, "runtime": runtime}


def get_job_type_metadata(job_type: JobType) -> dict:
    return _with_runtime_status(JOB_TYPE_REGISTRY[job_type])


def list_job_types() -> list[dict[str, str | bool]]:
    return [
        {"type": job_type.value, **get_job_type_metadata(job_type)}
        for job_type, metadata in JOB_TYPE_REGISTRY.items()
    ]
