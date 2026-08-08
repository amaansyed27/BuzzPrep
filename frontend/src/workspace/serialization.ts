/**
 * Workspace serialization utilities
 */
import type {
  SerializedWorkspace,
  WorkspaceResetBaseline,
  WorkspaceState,
  WorkspaceStateSnapshot,
} from "./types";

function cloneJson<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isResetBaseline(value: unknown): value is WorkspaceResetBaseline {
  if (!isRecord(value)) return false;

  return (
    Array.isArray(value.nodes) &&
    Array.isArray(value.edges) &&
    isRecord(value.config) &&
    isRecord(value.editors) &&
    Array.isArray(value.submissions) &&
    (value.challengeId === undefined || typeof value.challengeId === "string")
  );
}

export function createResetBaseline(workspace: SerializedWorkspace): WorkspaceResetBaseline {
  return cloneJson({
    nodes: workspace.nodes,
    edges: workspace.edges,
    config: workspace.config,
    editors: workspace.editors,
    submissions: workspace.submissions,
    challengeId: workspace.challengeId,
  });
}

export function createSnapshot(state: WorkspaceState): WorkspaceStateSnapshot {
  return cloneJson({
    nodes: state.nodes,
    edges: state.edges,
    config: state.config,
    editors: state.editors,
    submissions: state.submissions,
  });
}

export function serializeWorkspace(state: WorkspaceState): SerializedWorkspace {
  return cloneJson({
    nodes: state.nodes,
    edges: state.edges,
    config: state.config,
    editors: state.editors,
    submissions: state.submissions,
    events: state.events,
    workspaceActive: state.workspaceActive,
    challengeId: state.challengeId,
    initialSnapshot: state.initialSnapshot,
  });
}

export function deserializeWorkspace(serialized: unknown): SerializedWorkspace {
  if (!isRecord(serialized)) {
    throw new Error("Invalid serialized workspace");
  }

  const data = serialized;
  if (
    !Array.isArray(data.nodes) ||
    !Array.isArray(data.edges) ||
    !isRecord(data.config) ||
    !isRecord(data.editors) ||
    !Array.isArray(data.submissions) ||
    !Array.isArray(data.events) ||
    typeof data.workspaceActive !== "boolean" ||
    (data.challengeId !== undefined && typeof data.challengeId !== "string") ||
    (data.initialSnapshot !== undefined && !isResetBaseline(data.initialSnapshot))
  ) {
    throw new Error("Invalid serialized workspace structure");
  }

  return cloneJson({
    nodes: data.nodes,
    edges: data.edges,
    config: data.config,
    editors: data.editors,
    submissions: data.submissions,
    events: data.events,
    workspaceActive: data.workspaceActive,
    challengeId: data.challengeId,
    initialSnapshot: data.initialSnapshot,
  }) as SerializedWorkspace;
}
