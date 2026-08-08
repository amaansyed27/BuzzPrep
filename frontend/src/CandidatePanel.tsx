import React from "react";
import { Play } from "lucide-react";
import { startSession as apiStart } from "./interviewApi";
import { useInterviewStore } from "./useInterviewStore";

export default function CandidatePanel() {
  const sessionId = useInterviewStore((s) => s.sessionId);
  const started = useInterviewStore((s) => s.started);
  const busy = useInterviewStore((s) => s.busy);
  const setBusy = useInterviewStore((s) => s.setBusy);
  const setStarted = useInterviewStore((s) => s.setStarted);
  const pushMessage = useInterviewStore((s) => s.pushMessage);
  const setError = useInterviewStore((s) => s.setError);

  async function startDemo() {
    if (!sessionId || busy || started) return;
    setBusy(true);
    try {
      const resp = await apiStart(sessionId, { member: { name: "Demo Candidate" } });
      pushMessage({ role: "interviewer", text: resp.reply });
      setStarted(true);
    } catch (err) {
      // err is ErrorResponse from backend or network exception
      setError((err as any) ?? { error: { code: "client_error", message: "Connection error", details: null } });
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="panel candidate-panel">
      <p className="panel-kicker">Interview</p>
      <h2>Adaptive technical workspace</h2>
      <p className="muted">
        The workspace selects tasks and evaluates conversation + workspace actions. Start the demo session to verify the frontend→API flow.
      </p>

      <dl className="session-meta">
        <div>
          <dt>Session</dt>
          <dd>{sessionId ? sessionId.slice(0, 8) : "—"}</dd>
        </div>
        <div>
          <dt>State</dt>
          <dd>{started ? "Demo started" : "Not started"}</dd>
        </div>
      </dl>

      <button className="primary-button" onClick={startDemo} disabled={started || busy} aria-disabled={started || busy}>
        <Play size={14} />
        {started ? "Demo started" : busy ? "Starting…" : "Start demo session"}
      </button>
    </aside>
  );
}
