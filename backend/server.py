from fastapi import FastAPI, HTTPException
from fastapi import File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

try:
    from backend.jobs.schemas import JobRequest, JobType
    from backend.jobs.store import InMemoryJobStore
    from backend.jobs.validation import JobValidationError, validate_job_request
    from backend.models.api import get_registry_summary, list_frontend_models
    from backend.models.registry import list_job_types
    from backend.scheduler.router import dispatch_job
    from backend.storage.assets import ensure_asset_dir, save_uploaded_asset
    from backend.storage.paths import ensure_output_dir
except ModuleNotFoundError:
    from jobs.schemas import JobRequest, JobType
    from jobs.store import InMemoryJobStore
    from jobs.validation import JobValidationError, validate_job_request
    from models.api import get_registry_summary, list_frontend_models
    from models.registry import list_job_types
    from scheduler.router import dispatch_job
    from storage.assets import ensure_asset_dir, save_uploaded_asset
    from storage.paths import ensure_output_dir

app = FastAPI()
job_store = InMemoryJobStore()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(ensure_output_dir())), name="outputs")
app.mount("/files", StaticFiles(directory=str(ensure_asset_dir())), name="files")


@app.get("/")
def root():
    return {"status": "backend running", "job_types": [item["type"] for item in list_job_types()]}


@app.get("/job-types")
def get_job_types():
    return {"job_types": list_job_types()}


@app.get("/models")
def get_models():
    return {
        "models": list_frontend_models(),
        "registry": get_registry_summary(),
    }


@app.post("/assets/upload")
async def upload_asset(
    file: UploadFile = File(...),
    kind: str = Form("file"),
    role: str | None = Form(None),
):
    content = await file.read()
    asset = save_uploaded_asset(file.filename or "upload.bin", content, kind=kind, role=role)
    return {"asset": asset.model_dump(mode="json")}


@app.post("/jobs")
def create_job(job: JobRequest):
    try:
        validate_job_request(job)
    except ValueError as exc:
        details = exc.details if isinstance(exc, JobValidationError) else {}
        raise HTTPException(
            status_code=400,
            detail={
                "message": str(exc),
                "details": details,
            },
        ) from exc

    record = job_store.create(job)

    if not dispatch_job(record.id, record.type, job_store):
        return {
            "job_id": record.id,
            "status": "queued",
            "warning": f"Job type {record.type.value} is registered but not implemented yet.",
        }

    return {"job_id": record.id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    record = job_store.get(job_id)
    if not record:
        return {"error": "job not found"}
    return record.model_dump(mode="json")


@app.get("/jobs/{job_id}/status")
def get_job_status(job_id: str):
    record = job_store.get(job_id)
    if not record:
        return {"error": "job not found"}
    return {
        "job_id": record.id,
        "type": record.type.value,
        "status": record.status.value,
        "error": record.error,
        "updated_at": record.updated_at,
    }


@app.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    record = job_store.get(job_id)
    if not record:
        return {"error": "job not found"}
    return {
        "job_id": record.id,
        "status": record.status.value,
        "result": record.result.model_dump(mode="json") if record.result else None,
        "error": record.error,
    }
