import { AlertTriangle, Layers3 } from "lucide-react";
import { Suspense, useEffect, useMemo, useState } from "react";
import WorkspaceToolbar from "../WorkspaceToolbar";
import RendererErrorBoundary from "../RendererErrorBoundary";
import { useInterviewStore } from "../useInterviewStore";
import { useWorkspaceStore } from "../workspace/store";
import {
  CHALLENGE_RENDERER_REGISTRY,
  createChallengeDefinition,
} from "./registry";

export default function ChallengeWorkspace() {
  const challenge = useInterviewStore((state) => state.challenge);
  const initializeChallenge = useWorkspaceStore((state) => state.initializeChallenge);
  const definition = useMemo(
    () => (challenge ? createChallengeDefinition(challenge) : null),
    [challenge],
  );
  const [activeInteraction, setActiveInteraction] = useState<string | null>(null);
  const [initializedId, setInitializedId] = useState<string | null>(null);

  useEffect(() => {
    if (!definition) return;
    initializeChallenge(definition.initialWorkspace);
    setActiveInteraction(definition.modes[0]?.interactionType ?? null);
    setInitializedId(definition.id);
  }, [definition, initializeChallenge]);

  if (!definition || initializedId !== definition.id) {
    return (
      <section className="challenge-workspace loading-workspace" aria-busy="true">
        <span className="workspace-loader" />
        <strong>Preparing your evidence workspace…</strong>
      </section>
    );
  }

  const activeMode =
    definition.modes.find((mode) => mode.interactionType === activeInteraction) ??
    definition.modes[0];
  const Renderer = activeMode
    ? CHALLENGE_RENDERER_REGISTRY[activeMode.renderer]
    : CHALLENGE_RENDERER_REGISTRY.inspection;
  const isInjected = ["follow_up", "deeper", "diagnostic"].includes(
    definition.metadata.questionKind,
  );

  return (
    <section className="challenge-workspace" aria-labelledby="workspace-title">
      <header className="workspace-heading">
        <div>
          <p><Layers3 size={14} aria-hidden="true" /> Interactive workspace</p>
          <h1 id="workspace-title">{activeMode?.label ?? "Evidence workspace"}</h1>
        </div>
        <WorkspaceToolbar />
      </header>

      <div className={`constraint-banner ${isInjected ? "injected" : ""}`}>
        <AlertTriangle size={16} aria-hidden="true" />
        <div>
          <strong>{isInjected ? "New constraint" : "Scenario constraint"}</strong>
          <span>{definition.constraint}</span>
        </div>
      </div>

      <div className="workspace-brief-line">
        <p>{definition.brief}</p>
        <span>Actions are sent with your explanation</span>
      </div>

      {definition.modes.length > 1 && (
        <div className="renderer-tabs" role="tablist" aria-label="Challenge interaction modes">
          {definition.modes.map((mode) => (
            <button
              key={mode.interactionType}
              role="tab"
              aria-selected={mode.interactionType === activeMode?.interactionType}
              className={mode.interactionType === activeMode?.interactionType ? "active" : ""}
              onClick={() => setActiveInteraction(mode.interactionType)}
            >
              {mode.label}
            </button>
          ))}
        </div>
      )}

      <div className="renderer-stage">
        <RendererErrorBoundary resetKey={`${definition.id}-${activeMode?.interactionType}`}>
          <Suspense fallback={<div className="renderer-loading">Loading editor tools…</div>}>
            <Renderer definition={definition} interactionType={activeMode?.interactionType ?? ""} />
          </Suspense>
        </RendererErrorBoundary>
      </div>
    </section>
  );
}
