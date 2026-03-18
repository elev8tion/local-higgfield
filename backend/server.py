from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import uuid
import threading
import time

app = FastAPI()

app.mount("/outputs", StaticFiles(directory="/tmp"), name="outputs")

jobs = {}

class JobRequest(BaseModel):
    type: str
    prompt: str


def process_job(job_id):
    jobs[job_id]["status"] = "processing"
    time.sleep(2)

    from PIL import Image, ImageDraw

    # create fake generated image
    img = Image.new("RGB", (512, 512), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    text = jobs[job_id]["prompt"][:40]
    draw.text((20, 250), text, fill=(0, 255, 200))

    output_path = f"/tmp/{job_id}.png"
    img.save(output_path)

    jobs[job_id]["status"] = "completed"
    jobs[job_id]["result"] = {
        "output_path": output_path
    }


@app.get("/")
def root():
    return {"status": "backend running"}


@app.post("/jobs")
def create_job(job: JobRequest):
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "id": job_id,
        "type": job.type,
        "prompt": job.prompt,
        "status": "queued",
        "result": None
    }

    # start background worker thread
    thread = threading.Thread(target=process_job, args=(job_id,))
    thread.start()

    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    return jobs.get(job_id, {"error": "job not found"})
