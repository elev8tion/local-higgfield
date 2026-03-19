from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .common import copy_video_output


def create_mock_server(port: int = 0) -> ThreadingHTTPServer:
    root = Path("/tmp/open-higgsfield-mock-remote")
    root.mkdir(parents=True, exist_ok=True)
    jobs: dict[str, dict] = {}
    counter = {"value": 0}

    class MockRemoteHandler(BaseHTTPRequestHandler):
        def _write_json(self, status_code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:
            return

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path not in {"/video/jobs", "/lipsync/jobs"}:
                self._write_json(404, {"error": "not found"})
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8") or "{}")

            counter["value"] += 1
            job_id = f"mock-job-{counter['value']}"
            output_name = f"{job_id}.mp4"
            output_path = root / output_name
            copy_video_output(str(output_path))

            job_type = payload.get("type", "")
            if parsed.path == "/video/jobs":
                runtime = "mock-remote-video"
            else:
                runtime = "mock-remote-lipsync"

            jobs[job_id] = {
                "job_id": job_id,
                "status": "completed",
                "result": {
                    "output_url": f"http://127.0.0.1:{self.server.server_port}/outputs/{output_name}",
                    "assets": [
                        {
                            "kind": "video",
                            "uri": f"http://127.0.0.1:{self.server.server_port}/outputs/{output_name}",
                            "role": "primary_output",
                            "metadata": {"runtime": runtime},
                        }
                    ],
                },
                "runtime": runtime,
                "job_type": job_type,
            }
            self._write_json(
                200,
                {
                    "job_id": job_id,
                    "status": "completed",
                    "output_url": f"http://127.0.0.1:{self.server.server_port}/outputs/{output_name}",
                    "runtime": runtime,
                    "job_type": job_type,
                },
            )

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/video/jobs/") or parsed.path.startswith("/lipsync/jobs/"):
                job_id = parsed.path.rsplit("/", 1)[-1]
                payload = jobs.get(job_id)
                if not payload:
                    self._write_json(404, {"error": "job not found"})
                    return
                self._write_json(200, payload)
                return

            if parsed.path.startswith("/outputs/"):
                filename = parsed.path.rsplit("/", 1)[-1]
                file_path = root / filename
                if not file_path.exists():
                    self.send_response(404)
                    self.end_headers()
                    return
                content = file_path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

            self._write_json(404, {"error": "not found"})

    return ThreadingHTTPServer(("127.0.0.1", port), MockRemoteHandler)


def run_in_thread(port: int = 0) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = create_mock_server(port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
