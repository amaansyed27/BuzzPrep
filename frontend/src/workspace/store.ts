/**
 * Workspace store using Zustand
 * Manages the curriculum-agnostic interview workspace state and event tracking
 */
import { create } from "zustand";
import type {
  WorkspaceState,
  WorkspaceNode,
  WorkspaceEdge,
  WorkspaceEvent,
  WorkspaceEventAdd,
  WorkspaceEventRemove,
  WorkspaceEventConnect,
  WorkspaceEventConfigure,
  WorkspaceEventEdit,
  WorkspaceEventRun,
  WorkspaceEventSubmit,
  WorkspaceEventUndo,
  SerializedWorkspace,
  WorkspaceStateSnapshot,
} from "./types";
import { createSnapshot, serializeWorkspace, deserializeWorkspace } from "./serialization";

/**
 * Store type definition
 */
type WorkspaceStoreState = WorkspaceState & {
  // Actions
  addNode: (nodeId: string, nodeData: Record<string, unknown>) => void;
  removeNode: (nodeId: string) => void;
  connectNodes: (edgeId: string, source: string, target: string) => void;
  configure: (key: string, value: unknown) => void;
  edit: (editorId: string, content: string) => void;
  run: (target: string) => void;
  submit: (taskId: string, data: Record<string, unknown>) => void;
  undo: () => void;
  resetWorkspace: () => void; // hard reset, clears events
  candidateReset: () => void; // resets workspace but preserves events
  initializeChallenge: (serialized?: SerializedWorkspace) => void; // hard initialize with optional snapshot
  setWorkspaceActive: (active: boolean, challengeId?: string, initialSnapshot?: SerializedWorkspace) => void;
  serializeWorkspace: () => SerializedWorkspace;
  restoreWorkspace: (serialized: unknown) => void;
  setNodes: (nodes: WorkspaceNode[]) => void;
  setEdges: (edges: WorkspaceEdge[]) => void;
  setSelection: (nodeIds: string[], edgeIds: string[]) => void;
};

const initialState: WorkspaceState = {
  nodes: [],
  edges: [],
  selection: { nodeIds: [], edgeIds: [] },
  config: {},
  editors: {},
  submissions: [],
  events: [],
  history: [],
  workspaceActive: false,
  challengeId: undefined,
};

function generateEventId(): string {
  return "evt_" + Math.random().toString(36).slice(2, 11);
}

function getCurrentTimestamp(): string {
  return new Date().toISOString();
}

export const useWorkspaceStore = create<WorkspaceStoreState>((set, get) => ({
  ...initialState,

  addNode: (nodeId: string, nodeData: Record<string, unknown>) =>
    set((state) => {
      const newNode: WorkspaceNode = {
        id: nodeId,
        data: nodeData,
        position: { x: Math.random() * 200, y: Math.random() * 200 },
      };
      const event: WorkspaceEventAdd = {
        id: generateEventId(),
        type: "add",
        timestamp: getCurrentTimestamp(),
        payload: { nodeId, nodeData },
      };
      // Save snapshot before mutation for undo
      const snapshot = createSnapshot(state);
      return {
        nodes: [...state.nodes, newNode],
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  removeNode: (nodeId: string) =>
    set((state) => {
      const event: WorkspaceEventRemove = {
        id: generateEventId(),
        type: "remove",
        timestamp: getCurrentTimestamp(),
        payload: { nodeId },
      };
      // Save snapshot before mutation for undo
      const snapshot = createSnapshot(state);
      return {
        nodes: state.nodes.filter((n) => n.id !== nodeId),
        edges: state.edges.filter((e) => e.source !== nodeId && e.target !== nodeId),
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  connectNodes: (edgeId: string, source: string, target: string) =>
    set((state) => {
      const newEdge: WorkspaceEdge = { id: edgeId, source, target };
      const event: WorkspaceEventConnect = {
        id: generateEventId(),
        type: "connect",
        timestamp: getCurrentTimestamp(),
        payload: { edgeId, source, target },
      };
      // Save snapshot before mutation for undo
      const snapshot = createSnapshot(state);
      return {
        edges: [...state.edges, newEdge],
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  selectNode: (nodeId: string) =>
    set(() => ({
      selection: { nodeIds: [nodeId], edgeIds: [] },
    })),

  selectNodes: (nodeIds: string[]) =>
    set(() => ({
      selection: { nodeIds, edgeIds: [] },
    })),

  selectEdges: (edgeIds: string[]) =>
    set(() => ({
      selection: { nodeIds: [], edgeIds },
    })),

  clearSelection: () =>
    set(() => ({
      selection: { nodeIds: [], edgeIds: [] },
    })),

  setSelection: (nodeIds: string[], edgeIds: string[]) =>
    set(() => ({
      selection: { nodeIds, edgeIds },
    })),

  configure: (key: string, value: unknown) =>
    set((state) => {
      const event: WorkspaceEventConfigure = {
        id: generateEventId(),
        type: "configure",
        timestamp: getCurrentTimestamp(),
        payload: { configKey: key, value },
      };
      // Save snapshot before mutation for undo
      const snapshot = createSnapshot(state);
      return {
        config: { ...state.config, [key]: value },
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  edit: (editorId: string, content: string) =>
    set((state) => {
      const event: WorkspaceEventEdit = {
        id: generateEventId(),
        type: "edit",
        timestamp: getCurrentTimestamp(),
        payload: { editorId, content },
      };
      // Save snapshot before mutation for undo
      const snapshot = createSnapshot(state);
      return {
        editors: { ...state.editors, [editorId]: content },
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  run: (target: string) =>
    set((state) => {
      const event: WorkspaceEventRun = {
        id: generateEventId(),
        type: "run",
        timestamp: getCurrentTimestamp(),
        payload: { target },
      };
      return {
        events: [...state.events, event],
      };
    }),

  submit: (taskId: string, data: Record<string, unknown>) =>
    set((state) => {
      const submission = {
        taskId,
        timestamp: getCurrentTimestamp(),
        payload: data,
      };
      const event: WorkspaceEventSubmit = {
        id: generateEventId(),
        type: "submit",
        timestamp: getCurrentTimestamp(),
        payload: { taskId, data },
      };
      return {
        submissions: [...state.submissions, submission],
        events: [...state.events, event],
      };
    }),

  undo: () =>
    set((state) => {
      if (state.history.length === 0) return state;
      const prev = state.history[state.history.length - 1];
      const restoredToIndex = state.history.length - 1;
      const event: WorkspaceEventUndo = {
        id: generateEventId(),
        type: "undo",
        timestamp: getCurrentTimestamp(),
        payload: { restoredToIndex },
      };
      // Undo restores state and records the undo event
      return {
        nodes: prev.nodes,
        edges: prev.edges,
        config: prev.config,
        editors: prev.editors,
        submissions: prev.submissions,
        events: [...state.events, event],
        history: state.history.slice(0, -1),
      };
    }),

  resetWorkspace: () =>
    set(() => initialState),

  candidateReset: () =>
    set((state) => {
      // Preserve events (evidence), reset nodes/edges/editors/submissions to initialSnapshot if present
      const initial = state.initialSnapshot;
      if (initial) {
        return {
          nodes: initial.nodes,
          edges: initial.edges,
          config: initial.config,
          editors: initial.editors,
          submissions: initial.submissions,
          // preserve events and history cleared to avoid mismatched snapshots
          events: state.events,
          history: [],
        };
      }
      // No initial snapshot available - clear state but preserve events
      return {
        nodes: [],
        edges: [],
        config: {},
        editors: {},
        submissions: [],
        events: state.events,
        history: [],
      };
    }),

  initializeChallenge: (serialized?: SerializedWorkspace) =>
    set((state) => {
      // Hard initialize: set provided snapshot (if any) and clear events/history
      if (serialized) {
        return {
          nodes: serialized.nodes,
          edges: serialized.edges,
          config: serialized.config,
          editors: serialized.editors,
          submissions: serialized.submissions,
          events: [],
          history: [],
          initialSnapshot: serialized,
          workspaceActive: true,
        };
      }
      // No snapshot - start empty
      return {
        nodes: [],
        edges: [],
        config: {},
        editors: {},
        submissions: [],
        events: [],
        history: [],
        initialSnapshot: undefined,
        workspaceActive: true,
      };
    }),

  setWorkspaceActive: (active: boolean, challengeId?: string, initialSnapshot?: SerializedWorkspace) =>
    set(() => ({
      workspaceActive: active,
      challengeId: active ? challengeId : undefined,
      initialSnapshot: initialSnapshot ?? undefined,
    })),

  serializeWorkspace: () => {
    const state = get();
    return serializeWorkspace(state);
  },

  restoreWorkspace: (serialized: unknown) => {
    const data = deserializeWorkspace(serialized);
    set(() => ({
      nodes: data.nodes,
      edges: data.edges,
      config: data.config,
      editors: data.editors,
      submissions: data.submissions,
      events: data.events,
      history: [],
      selection: { nodeIds: [], edgeIds: [] },
      workspaceActive: data.workspaceActive,
      challengeId: data.challengeId,
    }));
  },

  setNodes: (nodes: WorkspaceNode[]) =>
    set(() => ({
      nodes,
    })),

  setEdges: (edges: WorkspaceEdge[]) =>
    set(() => ({
      edges,
    })),
}));
