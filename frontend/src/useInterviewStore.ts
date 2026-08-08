import { create } from "zustand";
import type { Node, Edge } from "@xyflow/react";
import type { InterviewResponse, ErrorResponse } from "./apiTypes";

type Message = { role: "interviewer" | "candidate"; text: string; kind?: string };

type SessionMeta = { status?: string; turnCount?: number };

type InterviewState = {
  sessionId: string | null;
  started: boolean;
  busy: boolean;
  lastError: ErrorResponse | null;
  messages: Message[];
  nodes: Node[];
  edges: Edge[];
  sessionMeta: SessionMeta;
  setSessionId: (id: string) => void;
  setStarted: (v: boolean) => void;
  setBusy: (v: boolean) => void;
  setError: (e: ErrorResponse | null) => void;
  pushMessage: (m: Message) => void;
  setNodes: (ns: Node[]) => void;
  setEdges: (es: Edge[]) => void;
  setSessionMeta: (m: SessionMeta) => void;
  clearMessages: () => void;
};

export const useInterviewStore = create<InterviewState>((set, get) => ({
  sessionId: null,
  started: false,
  busy: false,
  lastError: null,
  messages: [
    {
      role: "interviewer",
      text: "Scaffold ready. Start a demo session to verify the frontend-to-API flow.",
    },
  ],
  nodes: [
    { id: "scenario", position: { x: 80, y: 120 }, data: { label: "Scenario" } },
    { id: "workspace", position: { x: 310, y: 120 }, data: { label: "Interactive task" } },
    { id: "outcome", position: { x: 560, y: 120 }, data: { label: "Explain decision" } },
  ],
  edges: [
    { id: "scenario-workspace", source: "scenario", target: "workspace" },
    { id: "workspace-outcome", source: "workspace", target: "outcome" },
  ],
  sessionMeta: {},
  setSessionId: (id) => set({ sessionId: id }),
  setStarted: (v) => set({ started: v }),
  setBusy: (v) => set({ busy: v }),
  setError: (e) => set({ lastError: e }),
  pushMessage: (m) => set((s) => ({ messages: [...s.messages, m] })),
  setNodes: (ns) => set({ nodes: ns }),
  setEdges: (es) => set({ edges: es }),
  setSessionMeta: (m) => set({ sessionMeta: m }),
  clearMessages: () => set({ messages: [] }),
}));
