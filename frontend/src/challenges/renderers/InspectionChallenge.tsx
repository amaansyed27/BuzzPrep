import { Activity, AlertTriangle, CheckCircle2, Play, Radio } from "lucide-react";
import { useState } from "react";
import { useWorkspaceStore } from "../../workspace/store";
import type { ChallengeRendererProps } from "../types";

const logRows = [
  { time: "10:42:18.120", level: "INFO", text: "request accepted · trace=bp-481" },
  { time: "10:42:18.244", level: "WARN", text: "retrieval result age=17m · source=catalog" },
  { time: "10:42:18.391", level: "ERROR", text: "tool deadline exceeded · attempt=2/2" },
  { time: "10:42:18.406", level: "INFO", text: "fallback selected · confidence=0.61" },
];

const hypotheses = [
  ["stale-cache", "Stale retrieval cache"],
  ["retry-amplification", "Retry amplification"],
  ["missing-validation", "Missing evidence validation"],
] as const;

export default function InspectionChallenge({
  definition,
  interactionType,
}: ChallengeRendererProps) {
  const configure = useWorkspaceStore((state) => state.configure);
  const run = useWorkspaceStore((state) => state.run);
  const submit = useWorkspaceStore((state) => state.submit);
  const config = useWorkspaceStore((state) => state.config);
  const [suiteRan, setSuiteRan] = useState(false);
  const hypothesis = String(config.diagnosis ?? "");
  const isTestMode = interactionType === "test_evaluation_runner";

  function runSuite() {
    run(isTestMode ? "evaluation-suite" : "diagnostic-trace");
    setSuiteRan(true);
  }

  return (
    <div className="inspection-renderer">
      <section className="telemetry-panel" aria-label="Scenario telemetry">
        <div className="telemetry-heading">
          <span>
            <Radio size={15} aria-hidden="true" /> Live scenario trace
          </span>
          <span className="trace-id">BP-481</span>
        </div>
        <div className="metric-strip">
          <div><span>p95 latency</span><strong>1.84 s</strong><em className="bad">+62%</em></div>
          <div><span>Error rate</span><strong>7.3%</strong><em className="bad">+5.1</em></div>
          <div><span>Grounded</span><strong>81%</strong><em className="warn">−9%</em></div>
        </div>
        <div className="log-table" role="table" aria-label="Application logs">
          {logRows.map((row) => (
            <div className="log-row" role="row" key={`${row.time}-${row.level}`}>
              <code>{row.time}</code>
              <span className={`log-level ${row.level.toLowerCase()}`}>{row.level}</span>
              <code>{row.text}</code>
            </div>
          ))}
        </div>
      </section>

      <aside className="diagnosis-panel">
        <div className="tool-section-heading">
          <Activity size={15} aria-hidden="true" /> Working diagnosis
        </div>
        <p className="muted compact-copy">
          Select the strongest hypothesis, inspect the signal, then attach your decision.
        </p>
        <div className="hypothesis-list">
          {hypotheses.map(([value, label]) => (
            <button
              key={value}
              className={hypothesis === value ? "selected" : ""}
              onClick={() => configure("diagnosis", value)}
            >
              {hypothesis === value ? (
                <CheckCircle2 size={15} aria-hidden="true" />
              ) : (
                <AlertTriangle size={15} aria-hidden="true" />
              )}
              {label}
            </button>
          ))}
        </div>
        <button className="quiet-button full-width" onClick={runSuite}>
          <Play size={14} aria-hidden="true" />
          {isTestMode ? "Run fixed evaluation" : "Inspect trace"}
        </button>
        <div className={`suite-result ${suiteRan ? "visible" : ""}`} aria-live="polite">
          {suiteRan
            ? "Recorded: 2 fixed checks passed, stale-source assertion failed. This is a provided simulation, not arbitrary execution."
            : "No diagnostic action recorded yet."}
        </div>
        <button
          className="workspace-primary-button full-width"
          disabled={!hypothesis}
          onClick={() =>
            submit(`${definition.id}-diagnosis`, {
              hypothesis,
              traceId: "BP-481",
              suiteRan,
            })
          }
        >
          Attach diagnosis
        </button>
      </aside>
    </div>
  );
}
