import { create } from "zustand";
import type {
  CandidateRecord,
  ChallengeMetadata,
  ErrorResponse,
  Feedback,
  InterviewProgress,
  InterviewResponse,
  InterviewHistoryDetail,
} from "./apiTypes";

export type InterviewMessage = {
  id: string;
  role: "interviewer" | "candidate";
  text: string;
};

export type CoveredArea = {
  day: number;
  topic: string;
};

type InterviewPhase = "setup" | "interview" | "results";

type InterviewState = {
  phase: InterviewPhase;
  sessionId: string | null;
  candidate: CandidateRecord | null;
  busy: boolean;
  lastError: ErrorResponse | null;
  messages: InterviewMessage[];
  challenge: ChallengeMetadata | null;
  progress: InterviewProgress | null;
  coveredAreas: CoveredArea[];
  feedback: Feedback | null;
  prepareInterview: (candidate: CandidateRecord, sessionId: string) => void;
  startInterview: (
    candidate: CandidateRecord,
    sessionId: string,
    response: InterviewResponse,
  ) => void;
  pushCandidateMessage: (text: string) => void;
  applyResponse: (response: InterviewResponse) => void;
  setBusy: (busy: boolean) => void;
  setError: (error: ErrorResponse | null) => void;
  restart: () => void;
  resumeInterview: (detail: InterviewHistoryDetail) => void;
};

const asMessage = (
  role: InterviewMessage["role"],
  text: string,
): InterviewMessage => ({ id: crypto.randomUUID(), role, text });

function appendCoveredArea(
  coveredAreas: CoveredArea[],
  challenge?: ChallengeMetadata | null,
): CoveredArea[] {
  if (!challenge || coveredAreas.some((area) => area.day === challenge.curriculumDay)) {
    return coveredAreas;
  }
  return [
    ...coveredAreas,
    { day: challenge.curriculumDay, topic: challenge.topic },
  ];
}

export const useInterviewStore = create<InterviewState>((set) => ({
  phase: "setup",
  sessionId: null,
  candidate: null,
  busy: false,
  lastError: null,
  messages: [],
  challenge: null,
  progress: null,
  coveredAreas: [],
  feedback: null,

  prepareInterview: (candidate, sessionId) =>
    set({
      phase: "setup",
      candidate,
      sessionId,
      busy: false,
      lastError: null,
      messages: [],
      challenge: null,
      progress: null,
      coveredAreas: [],
      feedback: null,
    }),

  startInterview: (candidate, sessionId, response) =>
    set({
      phase: response.done ? "results" : "interview",
      sessionId,
      candidate,
      messages: [asMessage("interviewer", response.reply)],
      challenge: response.challenge ?? null,
      progress: response.progress ?? null,
      coveredAreas: appendCoveredArea([], response.challenge),
      feedback: response.feedback ?? null,
      lastError: null,
    }),

  pushCandidateMessage: (text) =>
    set((state) => ({ messages: [...state.messages, asMessage("candidate", text)] })),

  applyResponse: (response) =>
    set((state) => ({
      phase: response.done ? "results" : state.phase,
      messages: [...state.messages, asMessage("interviewer", response.reply)],
      challenge: response.challenge ?? state.challenge,
      progress: response.progress ?? state.progress,
      coveredAreas: appendCoveredArea(state.coveredAreas, response.challenge),
      feedback: response.feedback ?? state.feedback,
      lastError: null,
    })),

  setBusy: (busy) => set({ busy }),
  setError: (lastError) => set({ lastError }),
  resumeInterview: (detail) =>
    set({
      phase: detail.status === "completed" ? "results" : "interview",
      sessionId: detail.sessionId,
      candidate: detail.candidate,
      busy: false,
      lastError: null,
      messages: detail.messages.map((message) => asMessage(message.role, message.text)),
      challenge: detail.challenge ?? null,
      progress: detail.progress,
      coveredAreas: detail.challenge
        ? [{ day: detail.challenge.curriculumDay, topic: detail.challenge.topic }]
        : [],
      feedback: detail.feedback ?? null,
    }),
  restart: () =>
    set({
      phase: "setup",
      sessionId: null,
      candidate: null,
      busy: false,
      lastError: null,
      messages: [],
      challenge: null,
      progress: null,
      coveredAreas: [],
      feedback: null,
    }),
}));
