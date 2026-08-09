import { lazy, type ComponentType } from "react";
import type { ChallengeMetadata } from "../apiTypes";
import type { WorkspaceEdge, WorkspaceNode } from "../workspace/types";
import ConfigurationLab from "./renderers/ConfigurationLab";
import InspectionChallenge from "./renderers/InspectionChallenge";
import SystemCanvas from "./renderers/SystemCanvas";
import type {
  ChallengeDefinition,
  ChallengeMode,
  ChallengeRendererProps,
  EditorMode,
  RendererKind,
} from "./types";

const EditorChallenge = lazy(() => import("./renderers/EditorChallenge"));

const RENDERER_BY_INTERACTION: Record<string, RendererKind> = {
  system_canvas: "canvas",
  configuration_lab: "configuration",
  prompt_schema_editor: "editor",
  code_config_repair: "editor",
  data_workbench: "inspection",
  logs_metrics_explorer: "inspection",
  test_evaluation_runner: "inspection",
  incident_simulator: "inspection",
  architecture_critique: "inspection",
};

const MODE_LABELS: Record<string, string> = {
  system_canvas: "System canvas",
  configuration_lab: "Configuration lab",
  prompt_schema_editor: "Prompt + schema",
  code_config_repair: "Code repair",
  data_workbench: "Data workbench",
  logs_metrics_explorer: "Logs + metrics",
  test_evaluation_runner: "Test runner",
  incident_simulator: "Incident room",
  architecture_critique: "Design review",
};

export const CHALLENGE_RENDERER_REGISTRY: Record<
  RendererKind,
  ComponentType<ChallengeRendererProps>
> = {
  canvas: SystemCanvas,
  editor: EditorChallenge,
  configuration: ConfigurationLab,
  inspection: InspectionChallenge,
};

const slugify = (value: string) =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 48);

const constraints = [
  "Latency budget is now 150 ms. Keep the design explainable under load.",
  "One dependency now returns stale results. Preserve the current work and isolate the failure.",
  "Traffic increased 10x. Revisit the bottleneck without discarding your earlier evidence.",
  "A downstream tool times out intermittently. Add a bounded failure path.",
  "Sensitive data appears in one request. Make the smallest safe correction.",
];

function editorModes(topic: string): EditorMode[] {
  const topicComment = topic.replace(/\*\//g, "");
  return [
    {
      id: "code",
      label: "Code",
      language: "python",
      content: `async def handle_request(payload):\n    # TODO: make the ${topicComment} path observable and bounded\n    result = await service.run(payload)\n    return result`,
    },
    {
      id: "prompt",
      label: "Prompt",
      language: "plaintext",
      content: `You are evaluating ${topic}.\n\nUse only supplied evidence.\nExplain the decision and name one trade-off.\nReturn a concise recommendation.`,
    },
    {
      id: "json",
      label: "JSON / schema",
      language: "json",
      content: `{
  "type": "object",
  "properties": {
    "decision": { "type": "string" },
    "evidence": { "type": "array", "items": { "type": "string" } }
  },
  "required": ["decision", "evidence"]
}`,
    },
    {
      id: "sql",
      label: "SQL",
      language: "sql",
      content: `SELECT source_id, score, latency_ms\nFROM evaluation_runs\nWHERE topic = '${topicComment.replace(/'/g, "''")}'\nORDER BY score DESC\nLIMIT 10;`,
    },
    {
      id: "config",
      label: "Config",
      language: "json",
      content: `{
  "timeout_ms": 1500,
  "max_retries": 2,
  "trace_enabled": true,
  "fallback": "fail_closed"
}`,
    },
  ];
}

function initialNodes(metadata: ChallengeMetadata): WorkspaceNode[] {
  return [
    {
      id: "input",
      position: { x: 48, y: 120 },
      data: {
        label: "Candidate input",
        kind: "source",
        detail: `Day ${metadata.curriculumDay} scenario`,
      },
    },
    {
      id: "decision",
      position: { x: 310, y: 120 },
      data: {
        label: "Decision point",
        kind: "compute",
        detail: metadata.topic,
      },
    },
    {
      id: "evidence",
      position: { x: 572, y: 120 },
      data: {
        label: "Evidence gate",
        kind: "guard",
        detail: "Validate before output",
      },
    },
  ];
}

const initialEdges: WorkspaceEdge[] = [
  { id: "input-decision", source: "input", target: "decision", type: "smoothstep" },
  { id: "decision-evidence", source: "decision", target: "evidence", type: "smoothstep" },
];

export function createChallengeDefinition(
  metadata: ChallengeMetadata,
): ChallengeDefinition {
  const id = `day-${metadata.curriculumDay}-${metadata.questionKind}-${slugify(metadata.topic)}`;
  const modes: ChallengeMode[] = metadata.interactionTypes.map((interactionType) => ({
    interactionType,
    renderer: RENDERER_BY_INTERACTION[interactionType] ?? "inspection",
    label: MODE_LABELS[interactionType] ?? "Evidence workspace",
  }));
  const editors = editorModes(metadata.topic);

  return {
    id,
    metadata,
    brief:
      metadata.challengeSummary ??
      `Use the workspace to make and defend a ${metadata.difficulty} decision about ${metadata.topic}.`,
    constraint: constraints[(metadata.curriculumDay - 1) % constraints.length],
    modes,
    editorModes: editors,
    configChoices: [
      { value: "local", label: "Local-first", detail: "Lowest data exposure; manage capacity." },
      { value: "managed", label: "Managed service", detail: "Faster operations; validate data boundaries." },
      { value: "hybrid", label: "Hybrid path", detail: "Flexible routing; more failure modes." },
    ],
    initialWorkspace: {
      nodes: initialNodes(metadata),
      edges: initialEdges,
      config: {
        architecture: "hybrid",
        timeout_ms: 1500,
        retry_enabled: true,
        top_k: 5,
      },
      editors: Object.fromEntries(editors.map((mode) => [`editor-${mode.id}`, mode.content])),
      submissions: [],
      events: [],
      workspaceActive: true,
      challengeId: id,
    },
  };
}
