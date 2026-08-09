import type { ChallengeMetadata } from "../apiTypes";
import type { SerializedWorkspace } from "../workspace/types";

export type RendererKind = "canvas" | "editor" | "configuration" | "inspection";

export type ChallengeMode = {
  interactionType: string;
  renderer: RendererKind;
  label: string;
};

export type EditorMode = {
  id: "code" | "prompt" | "json" | "sql" | "config";
  label: string;
  language: string;
  content: string;
};

export type ConfigChoice = {
  value: string;
  label: string;
  detail: string;
};

export type ChallengeDefinition = {
  id: string;
  metadata: ChallengeMetadata;
  brief: string;
  constraint: string;
  modes: ChallengeMode[];
  editorModes: EditorMode[];
  configChoices: ConfigChoice[];
  initialWorkspace: SerializedWorkspace;
};

export type ChallengeRendererProps = {
  definition: ChallengeDefinition;
  interactionType: string;
};
