/**
 * Workspace store using Zustand
 * Manages the curriculum-agnostic interview workspace state and event tracking
 */
import { create } from "zustand";
import type {
  WorkspaceState,
  WorkspaceNode,
  WorkspaceEdge,
  WorkspaceEventAdd,
  WorkspaceEventRemove,
  WorkspaceEventConnect,
  WorkspaceEventDisconnect,
  WorkspaceEventConfigure,
  WorkspaceEventEdit,
  WorkspaceEventRun,
  WorkspaceEventSubmit,
  WorkspaceEventUndo,
  WorkspaceEventReset,
  SerializedWorkspace,
} from "./types";
import {
  createResetBaseline,
  createSnapshot,
  serializeWorkspace,
  deserializeWorkspace,
} from "./serialization";

/**
 * Store type definition
 */
type WorkspaceStoreState = WorkspaceState & {
  // Candidate actions
  addNode: (nodeId: string, nodeData: Record<string, unknown>) => void;
  removeNode: (nodeId: string) => void;
  connectNodes: (edgeId: string, source: string, target: string) => void;
  removeEdge: (edgeId: string) => void;
  configure: (key: string, value: unknown) => void;
  edit: (editorId: string, content: string) => void;
  run: (target: string) => void;
  submit: (taskId: string, data: Record<string, unknown>) => void;
  undo: () => void;
  candidateReset: () => void;

  // UI-only selection actions
  selectNode: (nodeId: string) => void;
  selectNodes: (nodeIds: string[]) => void;
  selectEdges: (edgeIds: string[]) => void;
  clearSelection: () => void;
  setSelection: (nodeIds: string[], edgeIds: string[]) => void;

  // Lifecycle/state actions
  resetWorkspace: () => void; // hard reset, clears events
  initializeChallenge: (serialized?: SerializedWorkspace) => void;
  setWorkspaceActive: (
    active: boolean,
    challengeId?: string,
    initialSnapshot?: SerializedWorkspace
  ) => void;
  serializeWorkspace: () => SerializedWorkspace;
  restoreWorkspace: (serialized: unknown) => void;
  setNodes: (nodes: WorkspaceNode[]) => void;
  setEdges: (edges: WorkspaceEdge[]) => void;
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
  initialSnapshot: undefined,
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
      const snapshot = createSnapshot(state);
      return {
        edges: [...state.edges, newEdge],
        events: [...state.events, event],
        history: [...state.history, snapshot],
      };
    }),

  removeEdge: (edgeId: string) =>
    set((state) => {
      const edge = state.edges.find((candidate) => candidate.id === edgeId);
      const event: WorkspaceEventDisconnect = {
        id: generateEventId(),
        type: "disconnect",
        timestamp: getCurrentTimestamp(),
        payload: {
          edgeId,
          source: edge?.source,
          target: edge?.target,
        },
      };
      const snapshot = createSnapshot(state);
      return {
        edges: state.edges.filter((candidate) => candidate.id !== edgeId),
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
      return {
        nodes: prev.nodes,
        edges: prev.edges,
        config: prev.config,
        editors: prev.editors,
        submissions: prev.submissions,
        events: [...state.events, event],
        history: state.history.slice(0, -1),
        selection: { nodeIds: [], edgeIds: [] },
      };
    }),

  resetWorkspace: () =>
    set(() => ({ ...initialState })),

  candidateReset: () =>
    set((state) => {
      const initial = state.initialSnapshot;
      const resetEvent: WorkspaceEventReset = {
        id: generateEventId(),
        type: "reset",
        timestamp: getCurrentTimestamp(),
        payload: {
          reason: "candidate_reset",
          initialSnapshotPresent: initial !== undefined,
        },
      };

      if (initial) {
        return {
          nodes: initial.nodes,
          edges: initial.edges,
          config: initial.config,
          editors: initial.editors,
          submissions: initial.submissions,
          events: [...state.events, resetEvent],
          history: [],
          selection: { nodeIds: [], edgeIds: [] },
          challengeId: initial.challengeId,
        };
      }

      return {
        nodes: [],
        edges: [],
        config: {},
        editors: {},
        submissions: [],
        events: [...state.events, resetEvent],
        history: [],
        selection: { nodeIds: [], edgeIds: [] },
      };
    }),

  initializeChallenge: (serialized?: SerializedWorkspace) =>
    set(() => {
      if (serialized) {
        const baseline = serialized.initialSnapshot ?? createResetBaseline(serialized);
        return {
          nodes: serialized.nodes,
          edges: serialized.edges,
          config: serialized.config,
          editors: serialized.editors,
          submissions: serialized.submissions,
          events: [],
          history: [],
          selection: { nodeIds: [], edgeIds: [] },
          initialSnapshot: baseline,
          workspaceActive: true,
          challengeId: serialized.challengeId,
        };
      }

      return {
        nodes: [],
        edges: [],
        config: {},
        editors: {},
        submissions: [],
        events: [],
        history: [],
        selection: { nodeIds: [], edgeIds: [] },
        initialSnapshot: undefined,
        workspaceActive: true,
        challengeId: undefined,
      };
    }),

  setWorkspaceActive: (
    active: boolean,
    challengeId?: string,
    initialSnapshot?: SerializedWorkspace
  ) =>
    set(() => ({
      workspaceActive: active,
      challengeId: active ? challengeId : undefined,
      initialSnapshot:
        active && initialSnapshot
          ? initialSnapshot.initialSnapshot ?? createResetBaseline(initialSnapshot)
          : undefined,
    })),

  serializeWorkspace: () => {
    const state = get();
    return serializeWorkspace(state);
  },

  restoreWorkspace: (serialized: unknown) => {
    const data = deserializeWorkspace(serialized);
    const baseline = data.initialSnapshot ?? createResetBaseline(data);
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
      initialSnapshot: baseline,
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
