import {
  ArrowRight,
  BookOpenCheck,
  CalendarClock,
  CircleCheck,
  Clock3,
  History,
  LoaderCircle,
  Play,
  Plus,
  RotateCcw,
  Target,
  TriangleAlert,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import type { ErrorResponse, InterviewHistoryItem } from "../apiTypes";
import { useAuth } from "../auth/AuthProvider";
import ProductNav from "../components/ProductNav";
import { getInterviewHistory } from "../interviewApi";

function formatDate(value?: string | null) {
  if (!value) return "—";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(value));
}

function PrepRow({ prep }: { prep: InterviewHistoryItem }) {
  const completed = prep.status === "completed";
  return (
    <article className="prep-row">
      <div className={`prep-status ${completed ? "completed" : "active"}`}>
        {completed ? <CircleCheck size={16} /> : <Play size={15} />}
      </div>
      <div className="prep-person"><strong>{prep.candidateName}</strong><span>{prep.candidateRole}</span></div>
      <div><small>Status</small><strong>{completed ? "Completed" : "In progress"}</strong></div>
      <div><small>Questions</small><strong>{prep.questionsAsked} / 8+</strong></div>
      <div><small>Days</small><strong>{prep.daysCovered} / 4+</strong></div>
      <div><small>Last activity</small><strong>{formatDate(prep.lastActivity)}</strong></div>
      <Link to={completed ? `/results/${prep.sessionId}` : `/prep/${prep.sessionId}`}>
        {completed ? "View feedback" : "Resume"} <ArrowRight size={15} />
      </Link>
    </article>
  );
}

export default function DashboardPage({ fullHistory = false }: { fullHistory?: boolean }) {
  const { session, user } = useAuth();
  const [interviews, setInterviews] = useState<InterviewHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!session?.access_token) return;
    let active = true;
    setLoading(true);
    setError(null);
    void getInterviewHistory(session.access_token)
      .then((response) => { if (active) setInterviews(response.interviews); })
      .catch((requestError: ErrorResponse) => { if (active) setError(requestError); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [refreshKey, session?.access_token]);

  const metrics = useMemo(() => {
    const completed = interviews.filter((item) => item.status === "completed");
    const active = interviews.filter((item) => item.status === "active");
    return {
      completed: completed.length,
      active: active.length,
      areas: interviews.reduce((sum, item) => sum + item.daysCovered, 0),
      latest: completed[0]?.completedAt ?? null,
    };
  }, [interviews]);

  const visibleInterviews = fullHistory ? interviews : interviews.slice(0, 5);
  const firstName = user?.email?.split("@")[0] ?? "candidate";

  return (
    <main className="dashboard-page">
      <ProductNav />
      <section className="dashboard-shell">
        <header className="dashboard-heading">
          <div><span>{fullHistory ? "PREP ARCHIVE" : "YOUR PREP WORKSPACE"}</span><h1>{fullHistory ? "Prep history" : `Ready for the next constraint, ${firstName}?`}</h1><p>{fullHistory ? "Every saved session and evidence-based result." : "Start a new prep or continue an active technical workspace."}</p></div>
          <Link className="dashboard-primary" to="/prep/new"><Plus size={17} /> Start new prep</Link>
        </header>

        {!fullHistory ? (
          <section className="dashboard-overview" aria-label="Interview overview">
            <article><CircleCheck size={18} /><span>Completed preps</span><strong>{metrics.completed}</strong><small>Saved feedback</small></article>
            <article><Clock3 size={18} /><span>Active preps</span><strong>{metrics.active}</strong><small>Ready to resume</small></article>
            <article><Target size={18} /><span>Areas practiced</span><strong>{metrics.areas}</strong><small>Curriculum days covered</small></article>
            <article><CalendarClock size={18} /><span>Latest completion</span><strong className="date-value">{formatDate(metrics.latest)}</strong><small>Most recent result</small></article>
          </section>
        ) : null}

        <section className="recent-preps">
          <header>
            <div><History size={16} /><span>{fullHistory ? "All preps" : "Recent preps"}</span></div>
            {!fullHistory && interviews.length > 5 ? <Link to="/history">View all <ArrowRight size={14} /></Link> : null}
          </header>
          {loading ? (
            <div className="dashboard-state"><LoaderCircle className="spin" size={24} /><strong>Loading real prep history…</strong></div>
          ) : error ? (
            <div className="dashboard-state error"><TriangleAlert size={24} /><strong>History is unavailable.</strong><p>{error.error.message}</p><button type="button" onClick={() => setRefreshKey((value) => value + 1)}><RotateCcw size={14} /> Retry</button></div>
          ) : visibleInterviews.length ? (
            <div className="prep-list">{visibleInterviews.map((prep) => <PrepRow prep={prep} key={prep.sessionId} />)}</div>
          ) : (
            <div className="dashboard-empty">
              <span><BookOpenCheck size={28} /></span>
              <small>NO PREP EVIDENCE YET</small>
              <h2>Your first workspace is ready.</h2>
              <p>Choose a supplied candidate profile, complete the readiness check, and start an adaptive prep across multiple curriculum areas.</p>
              <Link to="/prep/new">Start your first prep <ArrowRight size={16} /></Link>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}
