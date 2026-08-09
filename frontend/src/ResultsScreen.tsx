import { ArrowRight, CheckCircle2, Gauge, RefreshCw, Target, TriangleAlert } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "./auth/AuthProvider";
import { useInterviewStore } from "./useInterviewStore";
import { useWorkspaceStore } from "./workspace/store";

function ResultList({
  items,
  empty,
}: {
  items: string[];
  empty: string;
}) {
  if (items.length === 0) return <p className="empty-result">{empty}</p>;
  return (
    <ul>
      {items.map((item, index) => (
        <li key={`${index}-${item}`}><span>{index + 1}</span><p>{item}</p></li>
      ))}
    </ul>
  );
}

export default function ResultsScreen() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const demo = location.pathname.startsWith("/demo/");
  const candidate = useInterviewStore((state) => state.candidate);
  const feedback = useInterviewStore((state) => state.feedback);
  const progress = useInterviewStore((state) => state.progress);
  const sessionId = useInterviewStore((state) => state.sessionId);
  const restart = useInterviewStore((state) => state.restart);

  function startAnother() {
    useWorkspaceStore.getState().resetWorkspace();
    restart();
    navigate(demo ? "/demo/setup" : "/prep/new");
  }

  return (
    <main className="results-screen">
      <header className="setup-topbar results-topbar">
        <div className="brand-lockup compact"><span className="brand-mark">B</span><span>BUZZPREP</span></div>
        <span className="session-chip">Session {sessionId?.slice(0, 8)}</span>
      </header>

      <section className="results-hero">
        <div className="result-status-icon"><CheckCircle2 size={28} /></div>
        <p className="eyebrow">Interview complete</p>
        <h1>{candidate?.member.name}, here’s the evidence-based readout.</h1>
        <p>{feedback?.summary ?? "The interview completed, but no summary was returned."}</p>
        <div className="result-progress">
          <span><Gauge size={15} /><b>{progress?.questionsAsked ?? 0}</b> questions completed</span>
          <span><Target size={15} /><b>{progress?.daysCovered ?? 0}</b> curriculum days covered</span>
        </div>
      </section>

      <section className="results-grid">
        <article className="result-column strengths">
          <header><CheckCircle2 size={18} /><div><small>Signal 01</small><h2>Strengths demonstrated</h2></div></header>
          <ResultList items={feedback?.strengths ?? []} empty="No strengths were returned for this session." />
        </article>
        <article className="result-column gaps">
          <header><TriangleAlert size={18} /><div><small>Signal 02</small><h2>Gaps to close</h2></div></header>
          <ResultList items={feedback?.gaps ?? []} empty="No material gaps were returned for this session." />
        </article>
        <article className="result-column next">
          <header><ArrowRight size={18} /><div><small>Signal 03</small><h2>What to do next</h2></div></header>
          <ResultList items={feedback?.next ?? []} empty="No next steps were returned for this session." />
        </article>
      </section>

      <footer className="results-footer">
        <div><strong>BuzzPrep watched the work, not just the words.</strong><span>Feedback combines answers with auditable workspace actions.</span></div>
        <div className="results-actions">
          {user && !demo ? <button type="button" onClick={() => navigate("/dashboard")}>Back to dashboard</button> : null}
          <button onClick={startAnother}><RefreshCw size={15} /> Start another prep</button>
        </div>
      </footer>
    </main>
  );
}
