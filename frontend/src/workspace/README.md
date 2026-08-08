# Workspace State Module (Issue #4, PR #16)

## Overview

The workspace module provides a curriculum-agnostic, structured state layer for tracking candidate actions during interview challenges. It uses Zustand for state management and implements machine-readable event tracking.

## Architecture

### Core Files

- `types.ts` — TypeScript type definitions for workspace state, events, and serialization
- `store.ts` — Zustand store with state and actions
- `serialization.ts` — JSON serialization/deserialization utilities
- `index.ts` — Module exports
- `example.ts` — Usage examples (development reference only)

### State Structure

```typescript
WorkspaceState {
  nodes: WorkspaceNode[];              // React Flow nodes
  edges: WorkspaceEdge[];              // React Flow edges
  selection: WorkspaceSelection;       // Selected node/edge IDs (UI-only, no events)
  config: WorkspaceConfig;             // Key-value configuration state
  editors: WorkspaceEditor;            // Editor ID -> content mappings
  submissions: WorkspaceSubmission[];  // Task submissions
  events: WorkspaceEvent[];            // Structured event history
  history: WorkspaceStateSnapshot[];   // Snapshots for undo
  workspaceActive: boolean;            // Explicit flag: is workspace active?
  challengeId?: string;                // Optional challenge/task identifier
  initialSnapshot?: WorkspaceResetBaseline; // Candidate-reset baseline
}
```

**IMPORTANT**: `workspaceActive` is the source of truth for whether a workspace is active.
Do NOT infer workspace state from `nodes.length === 0` or other indirect checks.
An empty-node workspace is still a valid active workspace.

## Event Types

Candidate actions generate structured, discriminated union events:

- **add** — node created
- **remove** — node deleted
- **connect** — edge created between nodes
- **disconnect** — edge deleted
- **configure** — configuration key set
- **edit** — editor content changed
- **run** — execution/run action triggered
- **submit** — task submission
- **undo** — undo action performed
- **reset** — candidate reset performed

**Selection changes do NOT generate events.** Selection is UI-only state.

Each event contains:

- `id` — unique event identifier (prefixed `evt_`)
- `type` — machine-readable event type
- `timestamp` — ISO 8601 timestamp
- `payload` — structured event data

## Reset and Disconnect

- `candidateReset()` restores the workspace to its initial challenge baseline when available, or clears candidate-editable state when no baseline exists. It preserves the full `events[]` history and appends exactly one `reset` event.
- `initializeChallenge(serialized?)` and `resetWorkspace()` are hard lifecycle resets. They clear `events[]` and `history[]` for a fresh challenge/workspace.
- `initializeChallenge()` explicitly sets or clears `challengeId` so identifiers cannot leak across challenges.
- `connectNodes(...)` emits `connect`.
- `removeEdge(edgeId)` emits `disconnect`.

## Undo

`undo()` restores the previous mutation snapshot and emits an explicit `undo` event with `payload.restoredToIndex` metadata. Undo events remain part of evidence but are not themselves added to the undo snapshot stack.

## Store API

### Actions That Generate Events

```typescript
addNode(nodeId: string, nodeData: Record<string, unknown>) → void
removeNode(nodeId: string) → void
connectNodes(edgeId: string, source: string, target: string) → void
removeEdge(edgeId: string) → void
configure(key: string, value: unknown) → void
edit(editorId: string, content: string) → void
run(target: string) → void
submit(taskId: string, data: Record<string, unknown>) → void
undo() → void
candidateReset() → void
```

### UI-Only Actions (No Events)

```typescript
selectNode(nodeId: string) → void
selectNodes(nodeIds: string[]) → void
selectEdges(edgeIds: string[]) → void
clearSelection() → void
setSelection(nodeIds: string[], edgeIds: string[]) → void
```

### Lifecycle and State Actions

```typescript
resetWorkspace() → void
initializeChallenge(serialized?: SerializedWorkspace) → void
setWorkspaceActive(active: boolean, challengeId?: string, initialSnapshot?: SerializedWorkspace) → void
serializeWorkspace() → SerializedWorkspace
restoreWorkspace(serialized: unknown) → void
setNodes(nodes: WorkspaceNode[]) → void
setEdges(edges: WorkspaceEdge[]) → void
```

## React Flow Integration

FlowCanvas wires React Flow mutations into the common workspace model:

- node deletion calls `removeNode()`;
- edge creation calls `connectNodes()`;
- edge deletion calls `removeEdge()`;
- node/edge selection synchronizes to `WorkspaceSelection` without creating evidence events;
- position changes update serializable workspace nodes.

Challenge renderers can call the same store actions for node creation and non-canvas interactions.

## Serialization

The workspace is serializable to JSON and can be restored later:

```typescript
const serialized = useWorkspaceStore.getState().serializeWorkspace();
store.restoreWorkspace(serialized);
```

`SerializedWorkspace` includes the `initialSnapshot` reset baseline. Therefore this sequence is stable:

```text
initialize challenge
→ candidate changes workspace
→ serialize
→ restore
→ candidateReset()
→ original challenge baseline
```

For backward compatibility, restoring a payload without `initialSnapshot` reconstructs a baseline from the restored workspace instead of retaining a stale baseline from another challenge.

Deserialization performs lightweight runtime shape validation.

## Non-Canvas State

Configuration and editor state are first-class workspace state, independent of React Flow:

```typescript
store.configure("retrieval_model", "bm25");
store.edit("solution-editor", "const result = await search(query);");
store.run("solution-editor");
store.submit("challenge-1", { code: "...", time: 45 });
```

These operations are curriculum-agnostic; the examples are illustrative only.

## Activity Display

`WorkspaceToolbar` exposes candidate-facing Undo and Reset controls plus a lightweight recent-action view for debugging/demonstration.

## Design Principles

- **Curriculum-agnostic** — no hardcoding of one curriculum topic or challenge type
- **Extensible** — event types are discriminated unions
- **Machine-readable events** — structured payloads suitable for backend consumption
- **Serializable** — workspace state and candidate-reset baseline survive JSON round trips
- **Evidence-preserving** — candidate reset/undo actions remain auditable
- **Typed** — TypeScript types define the workspace contract

## Backend Integration (Future)

The serialized workspace can later be attached to the interview backend without changing the organizer's required plain-message contract:

```typescript
const workspace = useWorkspaceStore.getState().serializeWorkspace();
```

Backend evaluation/persistence is intentionally outside Issue #4.

## Testing / Examples

See `example.ts` for development usage examples. Production challenge renderers should consume the workspace module rather than duplicating workspace state or scoring logic.
