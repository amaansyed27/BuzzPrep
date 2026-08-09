import { Activity, Bot, Braces, CircleCheck, Network, SlidersHorizontal } from "lucide-react";
import { useEffect, useState } from "react";

const steps = [
  { label: "Scenario", detail: "Design retrieval under a 150 ms budget" },
  { label: "Action", detail: "Candidate changes retry and recall settings" },
  { label: "Evidence", detail: "Workspace actions join the explanation" },
  { label: "Adapt", detail: "Interviewer adds a stale-index constraint" },
];

export default function ProductSequence({ compact = false }: { compact?: boolean }) {
  const [active, setActive] = useState(0);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timer = window.setInterval(() => setActive((value) => (value + 1) % steps.length), 2200);
    return () => window.clearInterval(timer);
  }, []);

  return (
    <div className={`product-sequence ${compact ? "compact" : ""}`} aria-label="Adaptive prep sequence">
      <div className="sequence-topbar">
        <span><i /> LIVE PREP</span>
        <strong>Day 8 · Vector databases</strong>
        <em>2 / 8+ questions</em>
      </div>
      <div className="sequence-body">
        <aside>
          <span className="sequence-label">Challenge brief</span>
          <strong>Keep recall high without missing the latency target.</strong>
          <div className="sequence-meter"><span style={{ width: `${38 + active * 13}%` }} /></div>
          <small>{steps[active].label} / {steps[active].detail}</small>
        </aside>
        <section>
          <header><Network size={15} /> System canvas <span>3 actions tracked</span></header>
          <div className="mini-workspace">
            <button type="button" className={active >= 1 ? "active" : ""}><Braces size={15} /> Embed</button>
            <button type="button" className={active >= 2 ? "active" : ""}><Network size={15} /> Retrieve</button>
            <button type="button" className={active >= 3 ? "constraint" : ""}><Activity size={15} /> Rank</button>
          </div>
          <div className="mini-config">
            <span><SlidersHorizontal size={13} /> top-k <b>{active >= 1 ? "12" : "5"}</b></span>
            <span><CircleCheck size={13} /> bounded retry</span>
          </div>
        </section>
        <aside className="sequence-interviewer">
          <span className="sequence-label"><Bot size={13} /> Interviewer</span>
          <p>{active < 3
            ? "Walk me through the first trade-off you would make."
            : "The index is now stale. Which part of your design changes first, and why?"}</p>
          <div className="sequence-typing"><i /><i /><i /></div>
        </aside>
      </div>
      <div className="sequence-steps" aria-hidden="true">
        {steps.map((step, index) => (
          <span className={index === active ? "active" : index < active ? "done" : ""} key={step.label}>
            {String(index + 1).padStart(2, "0")} {step.label}
          </span>
        ))}
      </div>
    </div>
  );
}
