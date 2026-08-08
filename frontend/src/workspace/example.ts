/**
 * Example / demonstration of workspace state architecture
 * Shows how to use the workspace store for various candidate actions
 */

import { useWorkspaceStore } from "./store";
import type { WorkspaceEvent } from "./types";

/**
 * Example: Starting a simple workspace with some initial nodes
 */
export function exampleInitialize() {
  const store = useWorkspaceStore.getState();

  // Add some initial nodes
  store.addNode("node-1", { label: "Input", type: "input" });
  store.addNode("node-2", { label: "Process", type: "process" });
  store.addNode("node-3", { label: "Output", type: "output" });

  // Connect them
  store.connectNodes("edge-1-2", "node-1", "node-2");
  store.connectNodes("edge-2-3", "node-2", "node-3");

  console.log("Initialized workspace", store.serializeWorkspace());
}

/**
 * Example: Candidate configures a retrieval parameter
 */
export function exampleConfigure() {
  const store = useWorkspaceStore.getState();

  // Simulate candidate configuring a RAG retrieval model
  store.configure("retrieval_model", "bm25");
  store.configure("top_k", 5);

  console.log(
    "Configured workspace",
    store.events.filter((e: WorkspaceEvent) => e.type === "configure")
  );
}

/**
 * Example: Candidate edits code in an editor
 */
export function exampleEdit() {
  const store = useWorkspaceStore.getState();

  store.edit("solution-editor", "const result = await retrieveTopK(query, 5);");
  store.edit("solution-editor", "const result = await retrieveTopK(query, 5);\nreturn result.map(r => r.score);");

  console.log(
    "Edited solution",
    store.events.filter((e: WorkspaceEvent) => e.type === "edit")
  );
}

/**
 * Example: Candidate runs/executes something
 */
export function exampleRun() {
  const store = useWorkspaceStore.getState();

  store.run("solution-editor");

  console.log(
    "Ran solution",
    store.events.filter((e: WorkspaceEvent) => e.type === "run")
  );
}

/**
 * Example: Candidate submits a task
 */
export function exampleSubmit() {
  const store = useWorkspaceStore.getState();

  store.submit("task-1", {
    solution: "const result = await retrieveTopK(query, 5);",
  });

  console.log(
    "Submitted task",
    store.events.filter((e: WorkspaceEvent) => e.type === "submit")
  );
}

/**
 * Example: Serialize and restore workspace
 */
export function exampleSerializeRestore() {
  const store = useWorkspaceStore.getState();

  // Serialize current state
  const serialized = store.serializeWorkspace();
  console.log("Serialized:", serialized);

  // Reset workspace
  store.resetWorkspace();
  console.log("Reset workspace");

  // Restore from serialized
  store.restoreWorkspace(serialized);
  console.log("Restored workspace");

  // Verify it's the same
  const afterRestore = store.serializeWorkspace();
  console.log("After restore:", afterRestore);
}

/**
 * Example: Undo a recent action
 */
export function exampleUndo() {
  const store = useWorkspaceStore.getState();

  store.addNode("undo-test", { label: "Test" });
  console.log("Added node, events count:", store.events.length);

  store.undo();
  console.log("Undo, events count:", store.events.length);
}

/**
 * Example: Full workflow
 */
export function exampleFullWorkflow() {
  const store = useWorkspaceStore.getState();

  // Start fresh
  store.resetWorkspace();

  // Initialize
  store.addNode("retriever", { type: "retriever" });
  store.addNode("ranker", { type: "ranker" });
  store.connectNodes("edge-1", "retriever", "ranker");

  // Configure
  store.configure("retrieval_type", "bm25");
  store.configure("ranking_model", "cross-encoder");

  // Edit and run
  store.edit("query-editor", "What is machine learning?");
  store.run("retriever");

  // Submit
  store.submit("challenge-1", {
    architecture: "retriever -> ranker",
  });

  // Serialize for backend
  const serialized = store.serializeWorkspace();

  console.log("=== Full Workflow ===");
  console.log("Nodes:", serialized.nodes.length);
  console.log("Edges:", serialized.edges.length);
  console.log("Events:", serialized.events.length);
  console.log("Events by type:", {
    add: serialized.events.filter((e: WorkspaceEvent) => e.type === "add").length,
    connect: serialized.events.filter((e: WorkspaceEvent) => e.type === "connect").length,
    configure: serialized.events.filter((e: WorkspaceEvent) => e.type === "configure").length,
    edit: serialized.events.filter((e: WorkspaceEvent) => e.type === "edit").length,
    run: serialized.events.filter((e: WorkspaceEvent) => e.type === "run").length,
    submit: serialized.events.filter((e: WorkspaceEvent) => e.type === "submit").length,
  });
  console.log("Full serialization:", serialized);
}
