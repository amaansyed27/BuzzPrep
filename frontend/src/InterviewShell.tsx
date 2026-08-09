import CandidatePanel from "./CandidatePanel";
import ChatPanel from "./ChatPanel";
import Topbar from "./Topbar";
import ChallengeWorkspace from "./challenges/ChallengeWorkspace";

export default function InterviewShell() {
  return (
    <main className="interview-app">
      <Topbar />
      <div className="interview-grid">
        <CandidatePanel />
        <ChallengeWorkspace />
        <ChatPanel />
      </div>
    </main>
  );
}
