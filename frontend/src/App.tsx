import { useMemo, useEffect } from "react";
import Topbar from "./Topbar";
import CandidatePanel from "./CandidatePanel";
import FlowCanvas from "./FlowCanvas";
import ChatPanel from "./ChatPanel";
import { useInterviewStore } from "./useInterviewStore";

const AppShell = () => {
  const setSessionId = useInterviewStore((s) => s.setSessionId);

  useEffect(() => {
    const id = crypto.randomUUID();
    setSessionId(id);
  }, [setSessionId]);

  return (
    <main className="app-shell premium-bg">
      <Topbar />
      <section className="workspace-grid">
        <CandidatePanel />
        <FlowCanvas />
        <ChatPanel />
      </section>
    </main>
  );
};

export default AppShell;
