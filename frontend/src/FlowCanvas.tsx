import React, { useCallback } from "react";
import { ReactFlow, Background, Controls, MiniMap, Connection } from "@xyflow/react";
import { useInterviewStore } from "./useInterviewStore";
import { useWorkspaceStore } from "./workspace/store";
import WorkspaceToolbar from "./WorkspaceToolbar";

export default function FlowCanvas() {
  const interviewNodes = useInterviewStore((s) => s.nodes);
  const interviewEdges = useInterviewStore((s) => s.edges);

  // Workspace store - explicit flag determines if workspace is active
  const workspaceNodes = useWorkspaceStore((s) => s.nodes);
  const workspaceEdges = useWorkspaceStore((s) => s.edges);
  const workspaceActive = useWorkspaceStore((s) => s.workspaceActive);
  const removeNode = useWorkspaceStore((s) => s.removeNode);
  const connectNodes = useWorkspaceStore((s) => s.connectNodes);
  const setNodes = useWorkspaceStore((s) => s.setNodes);
  const setEdges = useWorkspaceStore((s) => s.setEdges);

  // Use workspace nodes/edges if workspace is active, otherwise fall back to interview store (demo mode)
  const nodes = workspaceActive ? workspaceNodes : interviewNodes;
  const edges = workspaceActive ? workspaceEdges : interviewEdges;

  // Handle node position/selection changes from React Flow
  // These don't create workspace events, just update local positions
  const onNodesChange = useCallback(
    (changes: any) => {
      const updated = nodes.map((node) => {
        const change = changes.find((c: any) => c.id === node.id);
        if (!change) return node;
        // Only sync position and selected state, not creation/deletion
        return { ...node, position: change.position ?? node.position, selected: change.selected ?? node.selected };
      });
      if (workspaceActive) {
        setNodes(updated);
      }
    },
    [nodes, workspaceActive, setNodes]
  );

  const onEdgesChange = useCallback(
    (changes: any) => {
      const updated = edges.map((edge) => {
        const change = changes.find((c: any) => c.id === edge.id);
        if (!change) return edge;
        return { ...edge, selected: change.selected ?? edge.selected };
      });
      if (workspaceActive) {
        setEdges(updated);
      }
    },
    [edges, workspaceActive, setEdges]
  );

  // Handle new connections - single mutation path through workspace store
  const onConnect = useCallback(
    (connection: Connection) => {
      if (!workspaceActive) {
        // Demo mode: don't create workspace events
        return;
      }
      // Workspace mode: create event
      const edgeId = `edge_${connection.source}_${connection.target}_${Date.now()}`;
      connectNodes(edgeId, connection.source || "", connection.target || "");
    },
    [workspaceActive, connectNodes]
  );

  // Handle node deletion - single mutation path through workspace store
  const onNodesDelete = useCallback(
    (nodesToDelete: typeof nodes) => {
      if (!workspaceActive) {
        // Demo mode: don't create workspace events
        return;
      }
      // Workspace mode: create event for each deletion
      nodesToDelete.forEach((node) => {
        removeNode(node.id);
      });
    },
    [workspaceActive, removeNode]
  );

  return (
    <section className="panel canvas-panel">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Interactive task</p>
          <h2>Challenge canvas</h2>
        </div>
        <span className="muted">React Flow + Workspace</span>
      </div>

      <WorkspaceToolbar />

      <div className="flow-wrap">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodesDelete={onNodesDelete}
          fitView
        >
          <Background color="rgba(255,255,255,0.03)" gap={16} />
          <MiniMap pannable zoomable />
          <Controls />
        </ReactFlow>
      </div>
    </section>
  );
}
