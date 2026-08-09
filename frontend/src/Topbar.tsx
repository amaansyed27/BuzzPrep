import { CircleDot, Clock3 } from "lucide-react";
import { useInterviewStore } from "./useInterviewStore";

export default function Topbar() {
  const candidate = useInterviewStore((state) => state.candidate);
  const challenge = useInterviewStore((state) => state.challenge);
  const progress = useInterviewStore((state) => state.progress);
  const sessionId = useInterviewStore((state) => state.sessionId);

  return (
    <header className="interview-topbar">
      <div className="brand-lockup compact">
        <span className="brand-mark">B</span>
        <span>BUZZPREP</span>
      </div>
      <div className="topbar-context">
        <span className="live-indicator"><CircleDot size={14} /> LIVE INTERVIEW</span>
        <strong>{candidate?.member.name}</strong>
        <span>{candidate?.member.jobRole}</span>
      </div>
      <div className="topbar-current">
        <small>CURRENT AREA</small>
        <strong>{challenge ? `Day ${challenge.curriculumDay} · ${challenge.topic}` : "Preparing challenge"}</strong>
      </div>
      <div className="topbar-progress">
        <span><b>{progress?.questionsAsked ?? 0}</b> / {progress?.minimumQuestions ?? 8}+ questions</span>
        <span><b>{progress?.daysCovered ?? 0}</b> / {progress?.minimumDays ?? 4}+ days</span>
      </div>
      <div className="session-chip" title={sessionId ?? undefined}>
        <Clock3 size={14} aria-hidden="true" /> {sessionId?.slice(0, 8)}
      </div>
    </header>
  );
}
