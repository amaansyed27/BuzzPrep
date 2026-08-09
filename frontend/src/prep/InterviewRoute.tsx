import { LoaderCircle, RotateCcw, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import type { ErrorResponse } from "../apiTypes";
import { useAuth } from "../auth/AuthProvider";
import InterviewShell from "../InterviewShell";
import { getInterviewDetail } from "../interviewApi";
import { useInterviewStore } from "../useInterviewStore";
import DesktopRequirement from "./DesktopRequirement";
import { useIntegrityTelemetry } from "./integrityTelemetry";
import { useDesktopCapability } from "./useDesktopCapability";

export default function InterviewRoute() {
  const { sessionId = "" } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const demo = location.pathname.startsWith("/demo/");
  const desktop = useDesktopCapability();
  const { session } = useAuth();
  const storedSessionId = useInterviewStore((state) => state.sessionId);
  const phase = useInterviewStore((state) => state.phase);
  const resumeInterview = useInterviewStore((state) => state.resumeInterview);
  const [loading, setLoading] = useState(storedSessionId !== sessionId);
  const [error, setError] = useState<ErrorResponse | null>(null);
  const [retry, setRetry] = useState(0);
  useIntegrityTelemetry(desktop && storedSessionId === sessionId);

  useEffect(() => {
    if (storedSessionId === sessionId) {
      setLoading(false);
      return;
    }
    if (demo || !session?.access_token) {
      setLoading(false);
      return;
    }
    let active = true;
    setLoading(true);
    setError(null);
    void getInterviewDetail(sessionId, session.access_token)
      .then((detail) => { if (active) resumeInterview(detail); })
      .catch((requestError: ErrorResponse) => { if (active) setError(requestError); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [demo, resumeInterview, retry, session?.access_token, sessionId, storedSessionId]);

  useEffect(() => {
    if (phase === "results" && storedSessionId === sessionId) {
      navigate(demo ? `/demo/${sessionId}/results` : `/results/${sessionId}`, { replace: true });
    }
  }, [demo, navigate, phase, sessionId, storedSessionId]);

  if (!desktop) return <DesktopRequirement backTo={demo ? "/demo/setup" : "/dashboard"} />;
  if (loading) return <main className="route-loading"><LoaderCircle className="spin" size={24} /><p>Restoring your technical workspace…</p></main>;
  if (error) return <main className="route-error"><TriangleAlert size={28} /><h1>Couldn’t restore this prep.</h1><p>{error.error.message}</p><button type="button" onClick={() => setRetry((value) => value + 1)}><RotateCcw size={15} /> Retry</button><Link to="/dashboard">Back to dashboard</Link></main>;
  if (storedSessionId !== sessionId) return <main className="route-error"><TriangleAlert size={28} /><h1>This demo prep is not active in this tab.</h1><p>Start a new public demo to create a fresh workspace.</p><Link to="/demo/setup">Start demo</Link></main>;
  return <InterviewShell />;
}
