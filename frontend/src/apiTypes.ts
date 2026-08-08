export type Feedback = {
  summary: string;
  strengths: string[];
  gaps: string[];
  next: string[];
};

export type InterviewResponse = {
  reply: string;
  done?: boolean;
  feedback?: Feedback | null;
};

export type ErrorDetail = {
  code: string;
  message: string;
  details?: Array<Record<string, unknown>> | null;
};

export type ErrorResponse = {
  error: ErrorDetail;
};
