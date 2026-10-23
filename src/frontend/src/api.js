async function readResponse(response) {
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export async function createRun(runRequest) {
  const response = await fetch("/api/runs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(runRequest),
  });
  return readResponse(response);
}

export async function getRun(runId) {
  const response = await fetch(`/api/runs/${encodeURIComponent(runId)}`);
  return readResponse(response);
}
