import { SlidersHorizontal, ToggleLeft, ToggleRight } from "lucide-react";
import { useWorkspaceStore } from "../../workspace/store";
import type { ChallengeRendererProps } from "../types";

export default function ConfigurationLab({ definition }: ChallengeRendererProps) {
  const config = useWorkspaceStore((state) => state.config);
  const configure = useWorkspaceStore((state) => state.configure);
  const submit = useWorkspaceStore((state) => state.submit);

  const architecture = String(config.architecture ?? "hybrid");
  const timeout = Number(config.timeout_ms ?? 1500);
  const topK = Number(config.top_k ?? 5);
  const retryEnabled = Boolean(config.retry_enabled ?? true);

  return (
    <div className="configuration-renderer">
      <div className="config-intro">
        <SlidersHorizontal size={18} aria-hidden="true" />
        <div>
          <strong>Make the operating trade-offs explicit</strong>
          <p>Each change is preserved as candidate evidence.</p>
        </div>
      </div>

      <fieldset className="choice-grid">
        <legend>Architecture</legend>
        {definition.configChoices.map((choice) => (
          <label
            className={`choice-card ${architecture === choice.value ? "selected" : ""}`}
            key={choice.value}
          >
            <input
              type="radio"
              name="architecture"
              value={choice.value}
              checked={architecture === choice.value}
              onChange={() => configure("architecture", choice.value)}
            />
            <span>
              <strong>{choice.label}</strong>
              <small>{choice.detail}</small>
            </span>
          </label>
        ))}
      </fieldset>

      <div className="range-grid">
        <label>
          <span>
            Timeout budget <output>{timeout} ms</output>
          </span>
          <input
            type="range"
            min="100"
            max="5000"
            step="100"
            value={timeout}
            onChange={(event) => configure("timeout_ms", Number(event.target.value))}
          />
        </label>
        <label>
          <span>
            Retrieval depth <output>top {topK}</output>
          </span>
          <input
            type="range"
            min="1"
            max="20"
            value={topK}
            onChange={(event) => configure("top_k", Number(event.target.value))}
          />
        </label>
      </div>

      <button
        className={`toggle-row ${retryEnabled ? "enabled" : ""}`}
        role="switch"
        aria-checked={retryEnabled}
        onClick={() => configure("retry_enabled", !retryEnabled)}
      >
        {retryEnabled ? <ToggleRight aria-hidden="true" /> : <ToggleLeft aria-hidden="true" />}
        <span>
          <strong>Bounded retry</strong>
          <small>Retry transient failures only; surface invalid requests immediately.</small>
        </span>
      </button>

      <div className="config-footer">
        <span>{Object.keys(config).length} configuration values tracked</span>
        <button
          className="workspace-primary-button"
          onClick={() =>
            submit(`${definition.id}-configuration`, {
              architecture,
              timeout_ms: timeout,
              top_k: topK,
              retry_enabled: retryEnabled,
            })
          }
        >
          Attach configuration
        </button>
      </div>
    </div>
  );
}
