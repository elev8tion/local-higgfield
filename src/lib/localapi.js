const API_BASE_URL = "http://localhost:8000";

function inferAssetsFromParams(params = {}) {
  const inferredAssets = [];

  if (params.image_url) {
    inferredAssets.push({ kind: "image", uri: params.image_url, role: "source_image" });
  }

  if (params.video_url) {
    inferredAssets.push({ kind: "video", uri: params.video_url, role: "source_video" });
  }

  if (params.audio_url) {
    inferredAssets.push({ kind: "audio", uri: params.audio_url, role: "source_audio" });
  }

  return inferredAssets;
}

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await res.json();
  if (!res.ok) {
    const message = data?.detail?.message || data?.error || `Request failed: ${res.status}`;
    const error = new Error(message);
    error.status = res.status;
    error.data = data;
    throw error;
  }

  return data;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

// Backward-compatible helper for the existing ImageStudio flow.
export async function createJob(prompt, type = "image") {
  return request("/jobs", {
    method: "POST",
    body: JSON.stringify({ type, prompt }),
  });
}

export async function createTypedJob({
  type,
  prompt = "",
  params = {},
  input_assets = [],
}) {
  const mergedInputAssets = [...input_assets, ...inferAssetsFromParams(params)];
  return request("/jobs", {
    method: "POST",
    body: JSON.stringify({
      type,
      prompt,
      params,
      input_assets: mergedInputAssets,
    }),
  });
}

export async function getJob(jobId) {
  return request(`/jobs/${jobId}`);
}

export async function getJobStatus(jobId) {
  return request(`/jobs/${jobId}/status`);
}

export async function getJobResult(jobId) {
  return request(`/jobs/${jobId}/result`);
}

export async function listJobTypes() {
  return request("/job-types");
}

export async function listBackendModels() {
  return request("/models");
}

export async function uploadAsset(file, { kind = "file", role = null } = {}) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("kind", kind);
  if (role) {
    formData.append("role", role);
  }

  const res = await fetch(`${API_BASE_URL}/assets/upload`, {
    method: "POST",
    body: formData,
  });

  return res.json();
}

export function resolveJobResultUrl(job) {
  if (job?.result?.output_url) {
    return `${API_BASE_URL}${job.result.output_url}`;
  }
  if (job?.result?.output_path) {
    return `${API_BASE_URL}/outputs/${job.result.output_path.split("/").pop()}`;
  }
  return null;
}

export async function waitForJobCompletion(jobId, { intervalMs = 1500, maxAttempts = 240 } = {}) {
  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const job = await getJob(jobId);
    if (job.status === "completed") {
      return job;
    }
    if (job.status === "failed" || job.status === "cancelled") {
      throw new Error(job.error || `Job ${job.status}`);
    }
    await new Promise((resolve) => setTimeout(resolve, intervalMs));
  }
  throw new Error("Job timed out");
}
