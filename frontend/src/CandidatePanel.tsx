import { Braces, Check, Circle, UserRound } from "lucide-react";
import { useInterviewStore } from "./useInterviewStore";

export default function CandidatePanel() {
  const candidate = useInterviewStore((state) => state.candidate);
  const challenge = useInterviewStore((state) => state.challenge);
  const progress = useInterviewStore((state) => state.progress);
  const coveredAreas = useInterviewStore((state) => state.coveredAreas);

  if (!candidate) return null;

  return (
    <aside className="session-rail">
      <section className="rail-section candidate-identity">
        <span className="rail-label"><UserRound size={13} /> Candidate</span>
        <strong>{candidate.member.name}</strong>
        <p>{candidate.member.jobRole} · {candidate.member.yearsExperience}y</p>
      </section>

      <section className="rail-section progress-section">
        <span className="rail-label">Minimum progress</span>
        <label>
          <span>Questions <b>{progress?.questionsAsked ?? 0} / {progress?.minimumQuestions ?? 8}+</b></span>
          <progress value={progress?.questionsAsked ?? 0} max={progress?.minimumQuestions ?? 8} />
        </label>
        <label>
          <span>Days covered <b>{progress?.daysCovered ?? 0} / {progress?.minimumDays ?? 4}+</b></span>
          <progress value={progress?.daysCovered ?? 0} max={progress?.minimumDays ?? 4} />
        </label>
      </section>

      <section className="rail-section covered-section">
        <span className="rail-label">Covered areas</span>
        <ol>
          {coveredAreas.map((area) => (
            <li key={area.day}>
              <Check size={13} aria-hidden="true" />
              <span><b>Day {area.day}</b>{area.topic}</span>
            </li>
          ))}
          {coveredAreas.length < (progress?.minimumDays ?? 4) && (
            <li className="pending-area"><Circle size={10} /><span>More curriculum evidence required</span></li>
          )}
        </ol>
      </section>

      <section className="rail-section challenge-brief">
        <span className="rail-label"><Braces size={13} /> Challenge brief</span>
        <div className="day-token">DAY {challenge?.curriculumDay ?? "—"}</div>
        <h2>{challenge?.topic ?? "Preparing challenge"}</h2>
        <p>{challenge?.challengeSummary ?? "The interviewer is selecting a practical task."}</p>
        <div className="challenge-tags">
          <span>{challenge?.difficulty ?? "adaptive"}</span>
          <span>{challenge?.questionKind.replaceAll("_", " ") ?? "initial"}</span>
        </div>
      </section>
    </aside>
  );
}
