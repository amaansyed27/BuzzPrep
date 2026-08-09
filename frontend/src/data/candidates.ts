import source from "./candidates.json";
import type { CandidateRecord } from "../apiTypes";

export const candidates = source.candidates as CandidateRecord[];
