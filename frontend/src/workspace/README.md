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
}
```

**IMPORTANT**: `workspaceActive` is the source of truth for whether a workspace is active.
Do NOT infer workspace state from `nodes.length === 0` or other indirect checks.
An empty-node workspace is still a valid active workspace.

## Event Types

All candidate actions generate structured, discriminated union events:

- **add** — node created
- **remove** — node deleted
- **connect** — edge created between nodes
- **configure** — configuration key set
- **edit** — editor content changed
- **run** — execution/run action triggered
- **submit** — task submission
- **undo** — undo action performed (explicit event, not recursive)

**Selection changes (selectNode, selectNodes, selectEdges) do NOT generate events.** Selection is UI-only state.

Each event contains:
- `id` — unique event identifier (prefixed evt_)
- `type` — machine-readable event type
- `timestamp` — ISO 8601 timestamp
- `payload` — structured event data (no prose)

## Store API

### Actions That Generate Events

```typescript
addNode(nodeId: string, nodeData: Record<string, unknown>) → void
removeNode(nodeId: string) → void
connectNodes(edgeId: string, source: string, target: string) → void
configure(key: string, value: unknown) → void
edit(editorId: string, content: string) → void
run(target: string) → void
submit(taskId: string, data: Record<string, unknown>) → void
undo() → void
```

Each action generates exactly one corresponding WorkspaceEvent. The `undo` action generates a `WorkspaceEventUndo` that records the undo occurred (not recursive).

### UI-Only Actions (No Events)

```typescript
selectNode(nodeId: string) → void
selectNodes(nodeIds: string[]) → void
selectEdges(edgeIds: string[]) → void
clearSelection() → void
setSelection(nodeIds: string[], edgeIds: string[]) → void
```

Selection changes are transient UI state and do not generate workspace events.

### Other Actions

```typescript
resetWorkspace() → void
setWorkspaceActive(active: boolean, challengeId?: string) → void
serializeWorkspace() → SerializedWorkspace
restoreWorkspace(serialized: unknown) → void
setNodes(nodes: WorkspaceNode[]) → void
setEdges(edges: WorkspaceEdge[]) → void
```
useWorkspaceStore.getState().addNode("node-1", { label: "Input" });

// Connect
useWorkspaceStore.getState().connectNodes("edge-1", "node-1", "node-2");

// Configure
useWorkspaceStore.getState().configure("model", "bm25");

// Edit
useWorkspaceStore.getState().edit("solution", "const x = 42;");

// Run
useWorkspaceStore.getState().run("solution");

// Submit
useWorkspaceStore.getState().submit("task-1", { score: 0.9 });

// Undo
useWorkspaceStore.getState().undo();

// Serialize
const data = useWorkspaceStore.getState().serializeWorkspace();
```

## React Flow Integration

FlowCanvas automatically wires React Flow mutations into workspace actions:

- Node addition calls `addNode()`
- Node deletion calls `removeNode()`
- Edge creation calls `connectNodes()`
- Selection changes update workspace selection state

All mutations generate corresponding WorkspaceEvents.

## Serialization

The workspace state is fully serializable to JSON:

```typescript
const serialized = useWorkspaceStore.getState().serializeWorkspace();
// Returns SerializedWorkspace with all state but no functions or React components

// Later:
store.restoreWorkspace(serialized);
```

Deserialization includes lightweight runtime validation.

## Non-Canvas State

Configuration and editor state are first-class workspace state, independent of React Flow:

```typescript
// Configure a RAG retrieval setting
store.configure("retrieval_model", "bm25");

// Edit code without React Flow nodes
store.edit("solution-editor", "const result = await search(query);");

// Run/execute
store.run("solution-editor");

// Submit
store.submit("challenge-1", { code: "...", time: 45 });
```

## History/Undo

Simple undo support reverts the most recent mutation by restoring the previous state snapshot:

```typescript
store.undo();
```

Undo does not itself generate events (avoids recursive event history).

## Activity Display

WorkspaceToolbar shows recent events (action type + timestamp) for debugging/demonstration.

## Design Principles

- **Curriculum-agnostic** — no hardcoding of RAG, coding tasks, etc.
- **Extensible** — new action types can be added by extending WorkspaceEventType union
- **No duplicated state** — React Flow nodes/edges are the source of truth; workspace store maintains them
- **Machine-readable events** — structured payloads, no prose; suitable for backend consumption
- **Serializable** — full state snapshot can be sent to backend for evaluation/logging
- **Typed** — strict TypeScript, discriminated unions, no `any`

## Backend Integration (Future)

The serialized workspace can be sent to the backend:

```typescript
const workspace = store.serializeWorkspace();
// POST to backend with workspace.events, workspace.nodes, etc.
// Backend evaluates candidate actions against rubric
```

Currently, POST /api/interview is unchanged. Workspace state is frontend-only until the backend contract is updated to accept it.

## Testing / Examples

See `example.ts` for usage demonstrations:

```typescript
import { exampleFullWorkflow } from "./workspace/example";
exampleFullWorkflow(); // Logs full event sequence and serialized state
```

These are development references, not part of the production UI.
