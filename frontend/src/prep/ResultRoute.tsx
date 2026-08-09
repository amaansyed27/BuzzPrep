import { LoaderCircle, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import type { ErrorResponse } from "../apiTypes";
import { useAuth } from "../auth/AuthProvider";
import { getInterviewDetail } from "../interviewApi";
import ResultsScreen from "../ResultsScreen";
import { useInterviewStore } from "../useInterviewStore";

export default function ResultRoute() {
  const { sessionId = "" } = useParams();
  const location = useLocation();
  const demo = location.pathname.startsWith("/demo/");
  const { session } = useAuth();
  const storedSessionId = useInterviewStore((state) => state.sessionId);
  const feedback = useInterviewStore((state) => state.feedback);
  const resumeInterview = useInterviewStore((state) => state.resumeInterview);
  const [loading, setLoading] = useState(!feedback || storedSessionId !== sessionId);
  const [error, setError] = useState<ErrorResponse | null>(null);

  useEffect(() => {
    if (feedback && storedSessionId === sessionId) {
      setLoading(false);
      return;
    }
    if (demo || !session?.access_token) {
      setLoading(false);
      return;
    }
    let active = true;
    void getInterviewDetail(sessionId, session.access_token)
      .then((detail) => { if (active) resumeInterview(detail); })
      .catch((requestError: ErrorResponse) => { if (active) setError(requestError); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [demo, feedback, resumeInterview, session?.access_token, sessionId, storedSessionId]);

  if (loading) return <main className="route-loading"><LoaderCircle className="spin" size={24} /><p>Loading evidence-based feedback…</p></main>;
  if (error || !feedback || storedSessionId !== sessionId) return <main className="route-error"><TriangleAlert size={28} /><h1>Feedback is not available.</h1><p>{error?.error.message ?? "Complete the interview before opening this result."}</p><Link to={demo ? "/demo/setup" : "/dashboard"}>Back</Link></main>;
  return <ResultsScreen />;
}
