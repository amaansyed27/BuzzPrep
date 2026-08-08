import type { Node, Edge } from "@xyflow/react";

/**
 * Core workspace types for issue #4:
 * A curriculum-agnostic architecture tracking candidate actions
 */

export type WorkspaceNodeData = Record<string, unknown>;

export type WorkspaceNode = Node<WorkspaceNodeData>;
export type WorkspaceEdge = Edge;

export type WorkspaceSelection = {
  nodeIds: string[];
  edgeIds: string[];
};

export type WorkspaceConfig = Record<string, unknown>;

export type WorkspaceEditor = {
  [editorId: string]: string; // editorId -> content
};

export type WorkspaceSubmission = {
  taskId: string;
  timestamp: string;
  payload: Record<string, unknown>;
};

/**
 * Discriminated union for workspace events
 */
export type WorkspaceEventType = "add" | "remove" | "connect" | "configure" | "edit" | "run" | "submit" | "undo";

export type WorkspaceEventBase = {
  id: string;
  type: WorkspaceEventType;
  timestamp: string;
};

export type WorkspaceEventAdd = WorkspaceEventBase & {
  type: "add";
  payload: {
    nodeId: string;
    nodeData: WorkspaceNodeData;
  };
};

export type WorkspaceEventRemove = WorkspaceEventBase & {
  type: "remove";
  payload: {
    nodeId: string;
  };
};

export type WorkspaceEventConnect = WorkspaceEventBase & {
  type: "connect";
  payload: {
    edgeId: string;
    source: string;
    target: string;
  };
};

export type WorkspaceEventConfigure = WorkspaceEventBase & {
  type: "configure";
  payload: {
    configKey: string;
    value: unknown;
  };
};

export type WorkspaceEventEdit = WorkspaceEventBase & {
  type: "edit";
  payload: {
    editorId: string;
    content: string;
  };
};

export type WorkspaceEventRun = WorkspaceEventBase & {
  type: "run";
  payload: {
    target: string;
  };
};

export type WorkspaceEventSubmit = WorkspaceEventBase & {
  type: "submit";
  payload: {
    taskId: string;
    data: Record<string, unknown>;
  };
};

export type WorkspaceEventUndo = WorkspaceEventBase & {
  type: "undo";
  payload: {
    // Metadata about what was undone
    restoredToIndex?: number; // which point in history was restored
  };
};

export type WorkspaceEvent =
  | WorkspaceEventAdd
  | WorkspaceEventRemove
  | WorkspaceEventConnect
  | WorkspaceEventConfigure
  | WorkspaceEventEdit
  | WorkspaceEventRun
  | WorkspaceEventSubmit
  | WorkspaceEventUndo;

export type WorkspaceState = {
  nodes: WorkspaceNode[];
  edges: WorkspaceEdge[];
  selection: WorkspaceSelection;
  config: WorkspaceConfig;
  editors: WorkspaceEditor;
  submissions: WorkspaceSubmission[];
  events: WorkspaceEvent[];
  history: WorkspaceStateSnapshot[]; // for undo
  workspaceActive: boolean; // explicit flag: is a workspace currently active?
  challengeId?: string; // optional identifier for the current challenge/task
  initialSnapshot?: SerializedWorkspace; // stored initial snapshot for candidate resets
};

export type WorkspaceStateSnapshot = {
  nodes: WorkspaceNode[];
  edges: WorkspaceEdge[];
  config: WorkspaceConfig;
  editors: WorkspaceEditor;
  submissions: WorkspaceSubmission[];
};

export type SerializedWorkspace = {
  nodes: WorkspaceNode[];
  edges: WorkspaceEdge[];
  config: WorkspaceConfig;
  editors: WorkspaceEditor;
  submissions: WorkspaceSubmission[];
  events: WorkspaceEvent[];
  workspaceActive: boolean;
  challengeId?: string;
};
