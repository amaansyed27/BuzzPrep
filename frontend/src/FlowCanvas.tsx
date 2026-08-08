import React from "react";
import { ReactFlow, Background, Controls, MiniMap } from "@xyflow/react";
import { useInterviewStore } from "./useInterviewStore";

export default function FlowCanvas() {
  const nodes = useInterviewStore((s) => s.nodes);
  const edges = useInterviewStore((s) => s.edges);

  return (
    <section className="panel canvas-panel">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Interactive task</p>
          <h2>Challenge canvas</h2>
        </div>
        <span className="muted">React Flow</span>
      </div>

      <div className="flow-wrap">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="rgba(255,255,255,0.03)" gap={16} />
          <MiniMap pannable zoomable />
          <Controls />
        </ReactFlow>
      </div>
    </section>
  );
}
