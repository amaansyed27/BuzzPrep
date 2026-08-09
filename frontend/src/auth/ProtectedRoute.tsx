import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthProvider";

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { configured, loading, user } = useAuth();
  const location = useLocation();
  if (loading) return <main className="route-loading"><span /><p>Restoring your BuzzPrep session…</p></main>;
  if (!configured || !user) {
    return <Navigate to="/auth?mode=signin" replace state={{ from: location.pathname }} />;
  }
  return children;
}
