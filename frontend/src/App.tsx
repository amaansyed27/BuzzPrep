import InterviewShell from "./InterviewShell";
import ResultsScreen from "./ResultsScreen";
import SetupScreen from "./SetupScreen";
import { useInterviewStore } from "./useInterviewStore";

export default function App() {
  const phase = useInterviewStore((state) => state.phase);

  if (phase === "setup") return <SetupScreen />;
  if (phase === "results") return <ResultsScreen />;
  return <InterviewShell />;
}
