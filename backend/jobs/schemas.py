from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class JobType(str, Enum):
    IMAGE_GENERATE = "image.generate"
    IMAGE_TRANSFORM = "image.transform"
    VIDEO_GENERATE = "video.generate"
    VIDEO_ANIMATE_IMAGE = "video.animate_image"
    VIDEO_TRANSFORM = "video.transform"
    LIPSYNC_IMAGE_AUDIO = "lipsync.image_audio"
    LIPSYNC_VIDEO_AUDIO = "lipsync.video_audio"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


LEGACY_TYPE_ALIASES = {
    "image": JobType.IMAGE_GENERATE,
    "image.generate": JobType.IMAGE_GENERATE,
    "image.transform": JobType.IMAGE_TRANSFORM,
    "video.generate": JobType.VIDEO_GENERATE,
    "video.animate_image": JobType.VIDEO_ANIMATE_IMAGE,
    "video.transform": JobType.VIDEO_TRANSFORM,
    "lipsync.image_audio": JobType.LIPSYNC_IMAGE_AUDIO,
    "lipsync.video_audio": JobType.LIPSYNC_VIDEO_AUDIO,
}


class AssetRef(BaseModel):
    kind: str
    uri: str
    role: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobResult(BaseModel):
    output_path: str | None = None
    output_url: str | None = None
    assets: list[AssetRef] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobRequest(BaseModel):
    type: str = "image"
    prompt: str = ""
    params: dict[str, Any] = Field(default_factory=dict)
    input_assets: list[AssetRef] = Field(default_factory=list)

    def normalized_type(self) -> JobType:
        try:
            return LEGACY_TYPE_ALIASES[self.type]
        except KeyError as exc:
            raise ValueError(f"Unsupported job type: {self.type}") from exc


class JobRecord(BaseModel):
    id: str
    type: JobType
    prompt: str = ""
    status: JobStatus
    params: dict[str, Any] = Field(default_factory=dict)
    input_assets: list[AssetRef] = Field(default_factory=list)
    result: JobResult | None = None
    error: str | None = None
    created_at: str
    updated_at: str

