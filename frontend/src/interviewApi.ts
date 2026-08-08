import type { InterviewResponse, ErrorResponse } from "./apiTypes";
import { useInterviewStore } from "./useInterviewStore";

async function parseError(response: Response): Promise<ErrorResponse> {
  try {
    const body = await response.json();
    return body as ErrorResponse;
  } catch (e) {
    return { error: { code: "unknown_error", message: `HTTP ${response.status}`, details: null } };
  }
}

function networkErrorToErrorResponse(err: unknown): ErrorResponse {
  const message = err instanceof Error ? err.message : String(err);
  return { error: { code: "network_error", message, details: null } };
}

export async function startSession(sessionId: string, candidate: Record<string, unknown>) {
  // Clear previous errors before making a request
  try {
    useInterviewStore.getState().setError(null);
  } catch (_) {}

  try {
    const res = await fetch("/api/interview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, candidate }),
    });

    if (!res.ok) {
      const err = await parseError(res);
      // surface typed error
      throw err;
    }

    const data = (await res.json()) as InterviewResponse;
    // clear any previous error after success
    useInterviewStore.getState().setError(null);
    return data;
  } catch (err) {
    // Normalize network / unexpected errors into ErrorResponse
    const normalized = (err && (err as ErrorResponse).error) ? (err as ErrorResponse) : networkErrorToErrorResponse(err);
    // store the error for UI
    try { useInterviewStore.getState().setError(normalized); } catch (_) {}
    throw normalized;
  }
}

export async function sendMessage(sessionId: string, message: string) {
  // Clear previous errors before making a request
  try {
    useInterviewStore.getState().setError(null);
  } catch (_) {}

  try {
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
    // clear any previous error after success
    useInterviewStore.getState().setError(null);
    return data;
  } catch (err) {
    const normalized = (err && (err as ErrorResponse).error) ? (err as ErrorResponse) : networkErrorToErrorResponse(err);
    try { useInterviewStore.getState().setError(normalized); } catch (_) {}
    throw normalized;
  }
}
