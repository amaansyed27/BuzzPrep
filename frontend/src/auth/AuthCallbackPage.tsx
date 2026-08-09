import { CircleCheck, LoaderCircle, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { supabase } from "./supabase";

export default function AuthCallbackPage() {
  const [error, setError] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get("error_description") ?? params.get("error");
  });
  const navigate = useNavigate();

  useEffect(() => {
    if (!supabase || error) return;
    let active = true;
    void supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!active) return;
      if (sessionError) {
        setError(sessionError.message);
      } else if (data.session) {
        window.setTimeout(() => navigate("/dashboard", { replace: true }), 350);
      } else {
        setError("This Magic Link is invalid or has expired. Request a new link to continue.");
      }
    });
    return () => { active = false; };
  }, [error, navigate]);

  return (
    <main className="callback-page">
      <Link className="brand-lockup" to="/"><span>BuzzPrep</span></Link>
      {error ? (
        <section className="callback-status error" role="alert">
          <TriangleAlert size={30} />
          <span>LINK COULD NOT BE USED</span>
          <h1>Request a fresh Magic Link.</h1>
          <p>{error}</p>
          <Link to="/auth?mode=signin">Back to sign in</Link>
        </section>
      ) : (
        <section className="callback-status" role="status">
          <div className="callback-loader"><LoaderCircle className="spin" size={34} /><CircleCheck size={18} /></div>
          <span>ESTABLISHING SESSION</span>
          <h1>Opening your dashboard.</h1>
          <p>Verifying the one-time link and restoring your secure session.</p>
        </section>
      )}
    </main>
  );
}
