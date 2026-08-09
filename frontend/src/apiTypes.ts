import type { SerializedWorkspace } from "./workspace/types";

export type CandidateMember = {
  id: string;
  name: string;
  jobRole: string;
  yearsExperience: number;
  education?: string | null;
  status: string;
};

export type CandidateMission = {
  day: number;
  title: string;
  passed?: boolean;
  skipped?: boolean;
  attempts?: number;
};

export type CandidateRecord = {
  member: CandidateMember;
  missions: CandidateMission[];
  signals: {
    commitDays: number;
    missionsCompleted: number;
    missionsFirstTry: number;
  };
};

export type Feedback = {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
};

export type ChallengeMetadata = {
  curriculumDay: number;
  topic: string;
  intent: string;
  difficulty: string;
  interactionTypes: string[];
  questionKind: string;
  challengeSummary?: string | null;
};

export type InterviewProgress = {
  questionsAsked: number;
  minimumQuestions: number;
  daysCovered: number;
  minimumDays: number;
};

export type InterviewResponse = {
  reply: string;
  done: boolean;
  feedback?: Feedback | null;
  challenge?: ChallengeMetadata | null;
  progress?: InterviewProgress | null;
};

export type ContinueInterviewRequest = {
  sessionId: string;
  message: string;
  workspace?: SerializedWorkspace;
  integrityEvents?: IntegrityTelemetryEvent[];
};

export type IntegrityTelemetryEvent = {
  type:
    | "tab_hidden"
    | "tab_visible"
    | "window_blur"
    | "window_focus"
    | "fullscreen_enter"
    | "fullscreen_exit"
    | "reconnect";
  timestamp: string;
};

export type InterviewHistoryItem = {
  sessionId: string;
  status: "active" | "completed";
  candidateName: string;
  candidateRole: string;
  createdAt: string;
  lastActivity: string;
  completedAt?: string | null;
  questionsAsked: number;
  daysCovered: number;
  currentTopic?: string | null;
  resultAvailable: boolean;
};

export type InterviewHistoryList = {
  interviews: InterviewHistoryItem[];
};

export type InterviewTranscriptMessage = {
  sequence: number;
  role: "interviewer" | "candidate";
  text: string;
};

export type InterviewHistoryDetail = InterviewHistoryItem & {
  candidate: CandidateRecord;
  challenge?: ChallengeMetadata | null;
  progress: InterviewProgress;
  feedback?: Feedback | null;
  messages: InterviewTranscriptMessage[];
};

export type ErrorDetail = {
  code: string;
  message: string;
  details?: Array<Record<string, unknown>> | null;
};

export type ErrorResponse = {
  error: ErrorDetail;
};
