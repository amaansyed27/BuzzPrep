/**
 * Workspace module index
 * Exports all types and the Zustand store for interview workspace state
 */

export * from "./types";
export { useWorkspaceStore } from "./store";
export { serializeWorkspace, deserializeWorkspace, createSnapshot } from "./serialization";
