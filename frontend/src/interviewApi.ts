import type { InterviewResponse, ErrorResponse } from "./apiTypes";

async function parseError(response: Response): Promise<ErrorResponse> {
  try {
    const body = await response.json();
    return body as ErrorResponse;
  } catch (e) {
    return { error: { code: "unknown_error", message: `HTTP ${response.status}`, details: null } };
  }
}

export async function startSession(sessionId: string, candidate: Record<string, unknown>) {
  const res = await fetch("/api/interview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, candidate }),
  });

  if (!res.ok) {
    const err = await parseError(res);
    throw err;
  }

  const data = (await res.json()) as InterviewResponse;
  return data;
}

export async function sendMessage(sessionId: string, message: string) {
  const res = await fetch("/api/interview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, message }),
  });

  if (!res.ok) {
    const err = await parseError(res);
    throw err;
  }

  const data = (await res.json()) as InterviewResponse;
  return data;
}
