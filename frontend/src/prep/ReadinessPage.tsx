import { ArrowLeft, ArrowRight, Check, CircleDot, LoaderCircle, MonitorUp, ShieldCheck, Wifi } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import type { ErrorResponse } from "../apiTypes";
import { useAuth } from "../auth/AuthProvider";
import { startSession } from "../interviewApi";
import { useInterviewStore } from "../useInterviewStore";
import DesktopRequirement from "./DesktopRequirement";
import { useDesktopCapability } from "./useDesktopCapability";

const checks = [
  [MonitorUp, "Desktop or laptop", "A larger workspace and precise pointer are required."],
  [Wifi, "Stable connection", "Each answer is evaluated before the next challenge appears."],
  [CircleDot, "Stay on this tab", "Focus changes are recorded as neutral integrity telemetry."],
  [ShieldCheck, "Fullscreen recommended", "Workspace actions may be recorded as interview evidence."],
] satisfies Array<[LucideIcon, string, string]>;

export default function ReadinessPage() {
  const { sessionId = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const demo = location.pathname.startsWith("/demo/");
  const desktop = useDesktopCapability();
  const candidate = useInterviewStore((state) => state.candidate);
  const preparedSessionId = useInterviewStore((state) => state.sessionId);
  const startInterview = useInterviewStore((state) => state.startInterview);
  const { session } = useAuth();
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ErrorResponse | null>(null);

  if (!desktop) return <DesktopRequirement backTo={demo ? "/demo/setup" : "/dashboard"} />;
  if (!candidate || preparedSessionId !== sessionId) {
    return (
      <main className="readiness-missing">
        <h1>Select a candidate before starting.</h1>
        <Link to={demo ? "/demo/setup" : "/prep/new"}>Choose a profile</Link>
      </main>
    );
  }

  async function begin() {
    if (!candidate || busy || !ready) return;
    setBusy(true);
    setError(null);
    try {
      const response = await startSession(sessionId, candidate, demo ? null : session?.access_token);
      startInterview(candidate, sessionId, response);
      navigate(demo ? `/demo/${sessionId}` : `/prep/${sessionId}`);
    } catch (requestError) {
      setError(requestError as ErrorResponse);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="readiness-page">
      <header><Link className="brand-lockup" to="/"><span>BuzzPrep</span></Link><span>PREP READINESS</span></header>
      <section>
        <div className="readiness-copy">
          <Link to={demo ? "/demo/setup" : "/prep/new"}><ArrowLeft size={15} /> Change candidate</Link>
          <small>SESSION {sessionId.slice(0, 8)}</small>
          <h1>Set up a focused technical session.</h1>
          <p>You’re preparing an adaptive interview for <strong>{candidate.member.name}</strong>, {candidate.member.jobRole}. The first challenge will use their real curriculum history.</p>
          <div className="readiness-candidate"><span>{candidate.member.name.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span><div><strong>{candidate.member.name}</strong><p>{candidate.member.yearsExperience} years · {candidate.signals.missionsCompleted} missions completed</p></div></div>
        </div>
        <div className="readiness-checks">
          <header><span>BEFORE YOU START</span><strong>About 20–30 minutes</strong></header>
          {checks.map(([Icon, title, copy]) => (
            <article key={String(title)}><Icon size={18} /><div><strong>{title}</strong><p>{copy}</p></div><Check size={16} /></article>
          ))}
          <label className="readiness-confirm"><input type="checkbox" checked={ready} onChange={(event) => setReady(event.target.checked)} /><span><Check size={14} /></span><p>I understand how focus and workspace evidence are recorded.</p></label>
          {error ? <div className="readiness-error" role="alert">{error.error.message}</div> : null}
          <button type="button" className="readiness-start" onClick={() => void begin()} disabled={!ready || busy}>{busy ? <><LoaderCircle className="spin" size={17} /> Preparing first challenge…</> : <>Enter focused prep <ArrowRight size={17} /></>}</button>
          <p className="readiness-privacy">No webcam, passive microphone recording, screen recording, or biometric monitoring. Voice input runs only when you press the mic.</p>
        </div>
      </section>
    </main>
  );
}
