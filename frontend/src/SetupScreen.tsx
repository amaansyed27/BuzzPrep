import { ArrowRight, Search, ShieldCheck, Sparkles } from "lucide-react";
import { useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import type { CandidateRecord } from "./apiTypes";
import { candidates } from "./data/candidates";
import { useInterviewStore } from "./useInterviewStore";

const initials = (name: string) =>
  name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

function signalSummary(candidate: CandidateRecord) {
  const revisit = candidate.missions.filter(
    (mission) => mission.skipped || mission.passed === false || (mission.attempts ?? 0) >= 3,
  ).length;
  return `${candidate.signals.missionsCompleted} completed · ${revisit} areas to revisit`;
}

export default function SetupScreen() {
  const [selectedId, setSelectedId] = useState(candidates[0]?.member.id ?? "");
  const [query, setQuery] = useState("");
  const prepareInterview = useInterviewStore((state) => state.prepareInterview);
  const location = useLocation();
  const navigate = useNavigate();
  const demo = location.pathname.startsWith("/demo");
  const selected =
    candidates.find((candidate) => candidate.member.id === selectedId) ?? candidates[0];
  const filteredCandidates = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return candidates;
    return candidates.filter((candidate) =>
      `${candidate.member.name} ${candidate.member.jobRole}`.toLowerCase().includes(normalized),
    );
  }, [query]);

  function beginInterview() {
    if (!selected) return;
    const sessionId = crypto.randomUUID();
    prepareInterview(selected, sessionId);
    navigate(demo ? `/demo/${sessionId}/readiness` : `/prep/${sessionId}/readiness`);
  }

  if (!selected) return <main className="setup-screen">No supplied candidates were found.</main>;

  return (
    <main className="setup-screen">
      <header className="setup-topbar">
        <Link className="brand-lockup" to="/" aria-label="BuzzPrep home">
          <span className="brand-mark">B</span>
          <span>BUZZPREP</span>
        </Link>
        <span className="demo-badge"><ShieldCheck size={14} /> {demo ? "Public demo" : "New authenticated prep"}</span>
      </header>

      <section className="setup-layout" id="main-setup">
        <div className="setup-intro">
          <p className="eyebrow"><Sparkles size={14} /> Adaptive technical interview</p>
          <h1>Show how you think.<br /><span>Not just what you say.</span></h1>
          <p className="setup-lede">
            BuzzPrep watches real workspace decisions, pairs them with your explanation,
            and changes the next challenge from the evidence.
          </p>
          <div className="experience-line" aria-label="Interview flow">
            <span>Choose a candidate</span><i />
            <span>Work the challenge</span><i />
            <span>Defend the trade-off</span>
          </div>
        </div>

        <section className="candidate-picker" aria-labelledby="candidate-picker-title">
          <div className="candidate-picker-heading">
            <div>
              <p className="step-label">01 / Candidate setup</p>
              <h2 id="candidate-picker-title">Select a cohort profile</h2>
            </div>
            <label className="candidate-search">
              <Search size={15} aria-hidden="true" />
              <span className="sr-only">Search candidates</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search name or role"
              />
            </label>
          </div>

          <div className="candidate-picker-body">
            <div className="candidate-list" role="listbox" aria-label="Supplied candidates">
              {filteredCandidates.map((candidate) => (
                <button
                  role="option"
                  aria-selected={candidate.member.id === selected.member.id}
                  className={candidate.member.id === selected.member.id ? "selected" : ""}
                  key={candidate.member.id}
                  onClick={() => setSelectedId(candidate.member.id)}
                >
                  <span className="candidate-avatar">{initials(candidate.member.name)}</span>
                  <span>
                    <strong>{candidate.member.name}</strong>
                    <small>{candidate.member.jobRole}</small>
                  </span>
                  <em>{candidate.member.yearsExperience}y</em>
                </button>
              ))}
              {filteredCandidates.length === 0 && (
                <p className="empty-list">No candidate matches that search.</p>
              )}
            </div>

            <div className="candidate-preview">
              <div className="candidate-preview-head">
                <span className="candidate-avatar large">{initials(selected.member.name)}</span>
                <div>
                  <span className="candidate-id">{selected.member.id}</span>
                  <h3>{selected.member.name}</h3>
                  <p>{selected.member.jobRole}</p>
                </div>
              </div>
              <dl className="profile-facts">
                <div><dt>Experience</dt><dd>{selected.member.yearsExperience} years</dd></div>
                <div><dt>Education</dt><dd>{selected.member.education ?? "Not supplied"}</dd></div>
                <div><dt>Curriculum</dt><dd>{signalSummary(selected)}</dd></div>
              </dl>
              <div className="topic-preview">
                <span>Curriculum signal</span>
                <div>
                  {selected.missions.slice(0, 4).map((mission) => (
                    <span key={mission.day}>D{mission.day} · {mission.title}</span>
                  ))}
                </div>
              </div>
              <button className="start-button" onClick={beginInterview}>
                <span>Continue to readiness</span>
                <ArrowRight size={19} aria-hidden="true" />
              </button>
              <p className="privacy-note">Uses the exact supplied candidate record. The challenge starts after a short readiness check.</p>
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}
