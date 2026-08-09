import { lazy, Suspense } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import LandingPage from "./marketing/LandingPage";

const AuthCallbackPage = lazy(() => import("./auth/AuthCallbackPage"));
const AuthPage = lazy(() => import("./auth/AuthPage"));
const DashboardPage = lazy(() => import("./dashboard/DashboardPage"));
const InterviewRoute = lazy(() => import("./prep/InterviewRoute"));
const ReadinessPage = lazy(() => import("./prep/ReadinessPage"));
const ResultRoute = lazy(() => import("./prep/ResultRoute"));
const SetupScreen = lazy(() => import("./SetupScreen"));

function RouteFallback() {
  return <main className="route-loading"><span /><p>Opening BuzzPrep…</p></main>;
}

export default function App() {
  return (
    <Suspense fallback={<RouteFallback />}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/history" element={<ProtectedRoute><DashboardPage fullHistory /></ProtectedRoute>} />
        <Route path="/prep/new" element={<ProtectedRoute><SetupScreen /></ProtectedRoute>} />
        <Route path="/prep/:sessionId/readiness" element={<ProtectedRoute><ReadinessPage /></ProtectedRoute>} />
        <Route path="/prep/:sessionId" element={<ProtectedRoute><InterviewRoute /></ProtectedRoute>} />
        <Route path="/results/:sessionId" element={<ProtectedRoute><ResultRoute /></ProtectedRoute>} />
        <Route path="/demo/setup" element={<SetupScreen />} />
        <Route path="/demo/:sessionId/readiness" element={<ReadinessPage />} />
        <Route path="/demo/:sessionId" element={<InterviewRoute />} />
        <Route path="/demo/:sessionId/results" element={<ResultRoute />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}
