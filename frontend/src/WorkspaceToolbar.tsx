import { History, RotateCcw, Undo2, X } from "lucide-react";
import { useState } from "react";
import { useWorkspaceStore } from "./workspace/store";

export default function WorkspaceToolbar() {
  const [showActivity, setShowActivity] = useState(false);
  const events = useWorkspaceStore((state) => state.events);
  const history = useWorkspaceStore((state) => state.history);
  const undo = useWorkspaceStore((state) => state.undo);
  const candidateReset = useWorkspaceStore((state) => state.candidateReset);

  return (
    <div className="workspace-toolbar-wrap">
      <div className="workspace-toolbar" role="toolbar" aria-label="Workspace history tools">
        <button onClick={undo} disabled={history.length === 0} title="Undo last mutation">
          <Undo2 size={14} aria-hidden="true" /> Undo
        </button>
        <button onClick={candidateReset} title="Reset to the initial challenge state">
          <RotateCcw size={14} aria-hidden="true" /> Reset
        </button>
        <button
          className={showActivity ? "active" : ""}
          onClick={() => setShowActivity((visible) => !visible)}
          aria-expanded={showActivity}
        >
          <History size={14} aria-hidden="true" /> Evidence log <b>{events.length}</b>
        </button>
      </div>
      {showActivity && (
        <aside className="activity-drawer" aria-label="Workspace evidence log">
          <div className="activity-drawer-heading">
            <span>Candidate actions</span>
            <button onClick={() => setShowActivity(false)} aria-label="Close evidence log"><X size={15} /></button>
          </div>
          {events.length === 0 ? (
            <p>No semantic workspace actions yet. Selection and panning are not evidence.</p>
          ) : (
            <ol>
              {events.slice().reverse().map((event) => (
                <li key={event.id}>
                  <span>{event.type}</span>
                  <time>{new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</time>
                </li>
              ))}
            </ol>
          )}
        </aside>
      )}
    </div>
  );
}
