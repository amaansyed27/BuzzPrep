import { useCallback } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type EdgeChange,
  type NodeChange,
} from "@xyflow/react";
import { Network, Plus, Trash2 } from "lucide-react";
import { useWorkspaceStore } from "../../workspace/store";
import type { WorkspaceEdge, WorkspaceNode } from "../../workspace/types";
import type { ChallengeRendererProps } from "../types";

const nodePalette = [
  { kind: "service", label: "Service" },
  { kind: "store", label: "Data store" },
  { kind: "guard", label: "Guardrail" },
];

export default function SystemCanvas({ definition }: ChallengeRendererProps) {
  const nodes = useWorkspaceStore((state) => state.nodes);
  const edges = useWorkspaceStore((state) => state.edges);
  const selection = useWorkspaceStore((state) => state.selection);
  const addNode = useWorkspaceStore((state) => state.addNode);
  const removeNode = useWorkspaceStore((state) => state.removeNode);
  const removeEdge = useWorkspaceStore((state) => state.removeEdge);
  const connectNodes = useWorkspaceStore((state) => state.connectNodes);
  const configure = useWorkspaceStore((state) => state.configure);
  const setNodes = useWorkspaceStore((state) => state.setNodes);
  const setEdges = useWorkspaceStore((state) => state.setEdges);
  const setSelection = useWorkspaceStore((state) => state.setSelection);

  const selectedNode = nodes.find((node) => selection.nodeIds.includes(node.id));
  const selectedEdge = edges.find((edge) => selection.edgeIds.includes(edge.id));

  const onNodesChange = useCallback(
    (changes: NodeChange<WorkspaceNode>[]) => {
      const layoutChanges = changes.filter((change) => change.type !== "remove");
      setNodes(applyNodeChanges(layoutChanges, nodes));
    },
    [nodes, setNodes],
  );

  const onEdgesChange = useCallback(
    (changes: EdgeChange<WorkspaceEdge>[]) => {
      const uiChanges = changes.filter((change) => change.type !== "remove");
      setEdges(applyEdgeChanges(uiChanges, edges));
    },
    [edges, setEdges],
  );

  const onConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) return;
      connectNodes(
        `edge-${connection.source}-${connection.target}-${Date.now()}`,
        connection.source,
        connection.target,
      );
    },
    [connectNodes],
  );

  const onSelectionChange = useCallback(
    ({
      nodes: selectedNodes,
      edges: selectedEdges,
    }: {
      nodes: WorkspaceNode[];
      edges: WorkspaceEdge[];
    }) => {
      const nodeIds = selectedNodes.map((node) => node.id);
      const edgeIds = selectedEdges.map((edge) => edge.id);
      const unchanged =
        selection.nodeIds.length === nodeIds.length &&
        selection.edgeIds.length === edgeIds.length &&
        selection.nodeIds.every((id) => nodeIds.includes(id)) &&
        selection.edgeIds.every((id) => edgeIds.includes(id));
      if (!unchanged) setSelection(nodeIds, edgeIds);
    },
    [selection, setSelection],
  );

  function addPaletteNode(kind: string, label: string) {
    const nodeId = `${kind}-${Date.now()}`;
    addNode(nodeId, {
      label,
      kind,
      detail: `Candidate-added ${label.toLowerCase()}`,
    });
  }

  function configureSelected(role: string) {
    if (!selectedNode) return;
    setNodes(
      nodes.map((node) =>
        node.id === selectedNode.id
          ? { ...node, data: { ...node.data, role } }
          : node,
      ),
    );
    configure(`node.${selectedNode.id}.role`, role);
  }

  return (
    <div className="canvas-renderer">
      <aside className="canvas-palette" aria-label="Canvas component palette">
        <div className="tool-section-heading">
          <Network size={15} aria-hidden="true" />
          Components
        </div>
        {nodePalette.map((item) => (
          <button
            className="palette-button"
            key={item.kind}
            onClick={() => addPaletteNode(item.kind, item.label)}
          >
            <Plus size={14} aria-hidden="true" />
            {item.label}
          </button>
        ))}
        <p className="tool-hint">Connect handles to show the request path.</p>
      </aside>

      <div className="flow-surface" aria-label={`${definition.metadata.topic} system canvas`}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodesDelete={(deleted) => deleted.forEach((node) => removeNode(node.id))}
          onEdgesDelete={(deleted) => deleted.forEach((edge) => removeEdge(edge.id))}
          onSelectionChange={onSelectionChange}
          fitView
          minZoom={0.55}
          maxZoom={1.6}
          deleteKeyCode={["Backspace", "Delete"]}
        >
          <Background color="rgba(138, 155, 171, 0.14)" gap={20} size={1} />
          <MiniMap
            pannable
            zoomable
            nodeStrokeWidth={2}
            nodeColor="#2a3945"
            nodeStrokeColor="#667785"
            maskColor="rgba(7, 10, 13, 0.8)"
            style={{ width: 148, height: 82 }}
          />
          <Controls showInteractive={false} />
        </ReactFlow>
      </div>

      <aside className="canvas-inspector" aria-label="Selection inspector">
        <span className="inspector-label">Selection</span>
        {selectedNode ? (
          <>
            <strong>{String(selectedNode.data.label ?? selectedNode.id)}</strong>
            <label className="field-label" htmlFor="node-role">
              Runtime role
            </label>
            <select
              id="node-role"
              value={String(selectedNode.data.role ?? "primary")}
              onChange={(event) => configureSelected(event.target.value)}
            >
              <option value="primary">Primary</option>
              <option value="fallback">Fallback</option>
              <option value="validation">Validation</option>
            </select>
            <button className="danger-quiet-button" onClick={() => removeNode(selectedNode.id)}>
              <Trash2 size={14} aria-hidden="true" /> Remove node
            </button>
          </>
        ) : selectedEdge ? (
          <>
            <strong>Connection</strong>
            <span className="muted compact-copy">
              {selectedEdge.source} → {selectedEdge.target}
            </span>
            <button className="danger-quiet-button" onClick={() => removeEdge(selectedEdge.id)}>
              <Trash2 size={14} aria-hidden="true" /> Disconnect
            </button>
          </>
        ) : (
          <p className="muted compact-copy">
            Select a node to configure it or an edge to disconnect it.
          </p>
        )}
      </aside>
    </div>
  );
}
