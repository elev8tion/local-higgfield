from __future__ import annotations

try:
    from backend.jobs.schemas import JobRequest
    from backend.models.registry import get_job_type_metadata
except ModuleNotFoundError:
    from jobs.schemas import JobRequest
    from models.registry import get_job_type_metadata


class JobValidationError(ValueError):
    def __init__(self, message: str, *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


def validate_job_request(job: JobRequest) -> None:
    job_type = job.normalized_type()
    metadata = get_job_type_metadata(job_type)
    contract = metadata.get("contract", {})

    prompt_required = contract.get("prompt_required", False)
    prompt = (job.prompt or "").strip()
    if prompt_required and not prompt:
        raise JobValidationError(
            f"{job_type.value} requires a prompt.",
            details={"field": "prompt", "reason": "required"},
        )

    input_assets = job.input_assets or []
    min_input_assets = contract.get("min_input_assets")
    max_input_assets = contract.get("max_input_assets")

    if min_input_assets is not None and len(input_assets) < min_input_assets:
        raise JobValidationError(
            f"{job_type.value} requires at least {min_input_assets} input asset(s).",
            details={
                "field": "input_assets",
                "reason": "too_few",
                "minimum": min_input_assets,
                "received": len(input_assets),
            },
        )

    if max_input_assets is not None and len(input_assets) > max_input_assets:
        raise JobValidationError(
            f"{job_type.value} accepts at most {max_input_assets} input asset(s).",
            details={
                "field": "input_assets",
                "reason": "too_many",
                "maximum": max_input_assets,
                "received": len(input_assets),
            },
        )

    accepted_asset_kinds = set(contract.get("accepted_asset_kinds", []))
    if accepted_asset_kinds:
        invalid_kinds = sorted({asset.kind for asset in input_assets if asset.kind not in accepted_asset_kinds})
        if invalid_kinds:
            raise JobValidationError(
                f"{job_type.value} does not accept asset kind(s): {', '.join(invalid_kinds)}.",
                details={
                    "field": "input_assets",
                    "reason": "invalid_kind",
                    "accepted_kinds": sorted(accepted_asset_kinds),
                    "received_kinds": invalid_kinds,
                },
            )

    required_asset_kinds = set(contract.get("required_asset_kinds", []))
    if required_asset_kinds:
        available_kinds = {asset.kind for asset in input_assets}
        missing_kinds = sorted(required_asset_kinds - available_kinds)
        if missing_kinds:
            raise JobValidationError(
                f"{job_type.value} requires asset kind(s): {', '.join(missing_kinds)}.",
                details={
                    "field": "input_assets",
                    "reason": "missing_kind",
                    "missing_kinds": missing_kinds,
                },
            )
