from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .common import copy_video_output


def create_mock_server(port: int = 0) -> ThreadingHTTPServer:
    root = Path("/tmp/open-higgsfield-mock-comfy")
    root.mkdir(parents=True, exist_ok=True)
    prompts: dict[str, dict] = {}
    counter = {"value": 0}

    class MockComfyHandler(BaseHTTPRequestHandler):
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
            if parsed.path != "/prompt":
                self._write_json(404, {"error": "not found"})
                return

            content_length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(content_length).decode("utf-8") or "{}")
            prompt = body.get("prompt", {})
            if not isinstance(prompt, dict):
                self._write_json(400, {"error": "prompt must be object"})
                return

            counter["value"] += 1
            prompt_id = f"mock-prompt-{counter['value']}"
            output_name = f"{prompt_id}.mp4"
            output_path = root / output_name
            copy_video_output(str(output_path))

            output_node_id = "save_video"
            if "save_video" not in prompt and prompt:
                output_node_id = next(iter(prompt.keys()))

            prompts[prompt_id] = {
                prompt_id: {
                    "prompt_id": prompt_id,
                    "outputs": {
                        output_node_id: {
                            "videos": [
                                {
                                    "filename": output_name,
                                    "subfolder": "",
                                    "type": "output",
                                }
                            ]
                        }
                    },
                    "status": {"status_str": "success", "completed": True},
                }
            }
            self._write_json(200, {"prompt_id": prompt_id, "number": counter["value"], "node_errors": {}})

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/history/"):
                prompt_id = parsed.path.rsplit("/", 1)[-1]
                payload = prompts.get(prompt_id, {})
                self._write_json(200, payload)
                return

            if parsed.path == "/view":
                params = parse_qs(parsed.query)
                filename = params.get("filename", [""])[0]
                file_path = root / filename
                if not filename or not file_path.exists():
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

    return ThreadingHTTPServer(("127.0.0.1", port), MockComfyHandler)


def run_in_thread(port: int = 0) -> tuple[ThreadingHTTPServer, threading.Thread]:
    server = create_mock_server(port=port)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
