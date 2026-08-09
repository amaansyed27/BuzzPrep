import type {
  CandidateRecord,
  ContinueInterviewRequest,
  ErrorResponse,
  InterviewResponse,
} from "./apiTypes";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
const INTERVIEW_URL = `${API_BASE_URL}/api/interview`;
const REQUEST_TIMEOUT_MS = 60_000;

function fallbackError(code: string, message: string): ErrorResponse {
  return { error: { code, message, details: null } };
}

async function parseError(response: Response): Promise<ErrorResponse> {
  try {
    const body = (await response.json()) as Partial<ErrorResponse>;
    if (body.error?.message) return body as ErrorResponse;
  } catch {
    // The server may have returned an HTML proxy or platform error.
  }
  return fallbackError("http_error", `BuzzPrep API returned HTTP ${response.status}.`);
}

function normalizeRequestError(error: unknown): ErrorResponse {
  if (typeof error === "object" && error !== null && "error" in error) {
    return error as ErrorResponse;
  }
  if (error instanceof DOMException && error.name === "AbortError") {
    return fallbackError(
      "request_timeout",
      "The interviewer took too long to respond. Your answer was not added locally; try again when the service is ready.",
    );
  }
  return fallbackError(
    "network_error",
    "BuzzPrep could not reach the interview API. Check the backend and try again.",
  );
}

async function postInterview(payload: Record<string, unknown>): Promise<InterviewResponse> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch(INTERVIEW_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!response.ok) throw await parseError(response);
    return (await response.json()) as InterviewResponse;
  } catch (error) {
    throw normalizeRequestError(error);
  } finally {
    window.clearTimeout(timeout);
  }
}

export function startSession(sessionId: string, candidate: CandidateRecord) {
  return postInterview({ sessionId, candidate });
}

export function continueSession(request: ContinueInterviewRequest) {
  return postInterview(request);
}
