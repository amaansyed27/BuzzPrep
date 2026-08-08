/**
 * Workspace serialization utilities
 */
import type { SerializedWorkspace, WorkspaceState, WorkspaceStateSnapshot } from "./types";

export function createSnapshot(state: WorkspaceState): WorkspaceStateSnapshot {
  return {
    nodes: JSON.parse(JSON.stringify(state.nodes)),
    edges: JSON.parse(JSON.stringify(state.edges)),
    config: JSON.parse(JSON.stringify(state.config)),
    editors: JSON.parse(JSON.stringify(state.editors)),
    submissions: JSON.parse(JSON.stringify(state.submissions)),
  };
}

export function serializeWorkspace(state: WorkspaceState): SerializedWorkspace {
  return {
    nodes: JSON.parse(JSON.stringify(state.nodes)),
    edges: JSON.parse(JSON.stringify(state.edges)),
    config: JSON.parse(JSON.stringify(state.config)),
    editors: JSON.parse(JSON.stringify(state.editors)),
    submissions: JSON.parse(JSON.stringify(state.submissions)),
    events: JSON.parse(JSON.stringify(state.events)),
    workspaceActive: state.workspaceActive,
    challengeId: state.challengeId,
  };
}

export function deserializeWorkspace(serialized: unknown): SerializedWorkspace {
  // Basic runtime validation
  if (typeof serialized !== "object" || serialized === null) {
    throw new Error("Invalid serialized workspace");
  }
  const data = serialized as Record<string, unknown>;
  if (
    !Array.isArray(data.nodes) ||
    !Array.isArray(data.edges) ||
    typeof data.config !== "object" ||
    typeof data.editors !== "object" ||
    !Array.isArray(data.submissions) ||
    !Array.isArray(data.events) ||
    typeof data.workspaceActive !== "boolean"
  ) {
    throw new Error("Invalid serialized workspace structure");
  }
  return {
    nodes: data.nodes,
    edges: data.edges,
    config: data.config,
    editors: data.editors,
    submissions: data.submissions,
    events: data.events,
    workspaceActive: data.workspaceActive,
    challengeId: data.challengeId as string | undefined,
  } as SerializedWorkspace;
}
