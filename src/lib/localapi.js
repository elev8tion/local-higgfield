export async function createJob(prompt, type = "image") {
  const res = await fetch("http://localhost:8000/jobs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      type,
      prompt,
    }),
  });

  return res.json();
}

export async function getJob(jobId) {
  const res = await fetch(`http://localhost:8000/jobs/${jobId}`);
  return res.json();
}
