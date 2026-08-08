import React, { useState } from "react";
import { useWorkspaceStore } from "./workspace/store";
import { IconButton } from "./IconButton";

export default function WorkspaceToolbar() {
  const [showActivity, setShowActivity] = useState(false);
  const events = useWorkspaceStore((s) => s.events);
  const undo = useWorkspaceStore((s) => s.undo);
  const resetWorkspace = useWorkspaceStore((s) => s.resetWorkspace);

  return (
    <div className="workspace-toolbar-wrap">
      <div className="workspace-toolbar" role="toolbar" aria-label="Workspace toolbar">
        <button
          onClick={() => undo()}
          className="toolbar-action-button"
          title="Undo last action"
          aria-label="Undo"
        >
          ↶ Undo
        </button>
        <button
          onClick={() => resetWorkspace()}
          className="toolbar-action-button"
          title="Reset workspace"
          aria-label="Reset"
        >
          ↻ Reset
        </button>
        <button
          onClick={() => setShowActivity(!showActivity)}
          className="toolbar-action-button"
          title={showActivity ? "Hide activity" : "Show activity"}
          aria-label="Toggle activity"
        >
          📋 Activity ({events.length})
        </button>
      </div>

      {showActivity && (
        <div className="workspace-activity">
          <div className="activity-header">Recent actions</div>
          <div className="activity-list">
            {events.length === 0 ? (
              <p className="muted">No actions yet</p>
            ) : (
              events.slice(-10).map((evt) => (
                <div key={evt.id} className="activity-item">
                  <span className="activity-type">{evt.type}</span>
                  <span className="activity-time">{new Date(evt.timestamp).toLocaleTimeString()}</span>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
