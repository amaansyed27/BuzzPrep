import React from "react";
import { useInterviewStore } from "./useInterviewStore";
import { formatShort } from "./utils_format";

export default function Topbar() {
  const sessionId = useInterviewStore((s) => s.sessionId);
  const started = useInterviewStore((s) => s.started);

  return (
    <header className="topbar premium-topbar">
      <div>
        <p className="eyebrow">BuzzPrep</p>
        <h1>Interview IDE</h1>
      </div>

      <div className="topbar-right">
        <div className={`status-pill ${started ? "connected" : "idle"}`}>
          {started ? "Connected" : "Not started"}
        </div>
        <div className="session-id" aria-live="polite">{sessionId ? formatShort(sessionId) : "—"}</div>
      </div>
    </header>
  );
}
