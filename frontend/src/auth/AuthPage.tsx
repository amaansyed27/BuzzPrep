import { ArrowRight, Check, Inbox, LoaderCircle, Mail, ShieldCheck, TriangleAlert } from "lucide-react";
import { type FormEvent, useEffect, useState } from "react";
import { Link, Navigate, useSearchParams } from "react-router-dom";
import ProductSequence from "../marketing/ProductSequence";
import { useAuth } from "./AuthProvider";
import { supabase } from "./supabase";

type AuthMode = "signin" | "signup";
type SubmitState = "idle" | "sending" | "sent" | "error";

export default function AuthPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedMode = searchParams.get("mode") === "signup" ? "signup" : "signin";
  const [mode, setMode] = useState<AuthMode>(requestedMode);
  const [email, setEmail] = useState("");
  const [state, setState] = useState<SubmitState>("idle");
  const [message, setMessage] = useState("");
  const { configured, loading, user } = useAuth();

  useEffect(() => setMode(requestedMode), [requestedMode]);

  if (!loading && user) return <Navigate to="/dashboard" replace />;

  function changeMode(nextMode: AuthMode) {
    setMode(nextMode);
    setState("idle");
    setMessage("");
    setSearchParams({ mode: nextMode });
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!supabase || !email.trim()) return;
    setState("sending");
    setMessage("");
    const { error } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: {
        shouldCreateUser: mode === "signup",
        emailRedirectTo: `${window.location.origin}/auth/callback`,
      },
    });
    if (error) {
      setState("error");
      setMessage(error.message);
      return;
    }
    setState("sent");
  }

  return (
    <main className="auth-page">
      <section className="auth-visual">
        <Link className="brand-lockup" to="/" aria-label="BuzzPrep home">
          <span className="brand-mark">B</span><span>BUZZPREP</span>
        </Link>
        <div>
          <p className="eyebrow"><ShieldCheck size={14} /> Evidence-aware prep</p>
          <h1>Your technical decisions deserve a better follow-up.</h1>
          <p>Build in the workspace. Explain the trade-off. Let the next question respond.</p>
        </div>
        <ProductSequence compact />
        <ul>
          <li><Check size={14} /> Workspace actions become evidence</li>
          <li><Check size={14} /> Sessions cover multiple curriculum areas</li>
          <li><Check size={14} /> Results stay available across devices</li>
        </ul>
      </section>

      <section className="auth-form-side">
        <div className="auth-form-wrap">
          <Link className="auth-back" to="/">← Back to BuzzPrep</Link>
          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            <button type="button" role="tab" aria-selected={mode === "signin"} onClick={() => changeMode("signin")}>Sign in</button>
            <button type="button" role="tab" aria-selected={mode === "signup"} onClick={() => changeMode("signup")}>Create account</button>
          </div>
          <div className="auth-heading">
            <span>{mode === "signin" ? "WELCOME BACK" : "START YOUR FIRST PREP"}</span>
            <h2>{mode === "signin" ? "Continue where your evidence left off." : "Create your technical prep workspace."}</h2>
            <p>We’ll email a secure, one-time Magic Link. No password to remember.</p>
          </div>

          {!configured ? (
            <div className="auth-notice" role="alert">
              <TriangleAlert size={18} />
              <div><strong>Authentication is not configured in this build.</strong><p>Add the Supabase public environment variables, then rebuild the frontend.</p></div>
            </div>
          ) : state === "sent" ? (
            <div className="auth-sent" role="status">
              <span><Inbox size={24} /></span>
              <small>MAGIC LINK SENT</small>
              <h2>Check your inbox.</h2>
              <p>We sent a one-time {mode === "signup" ? "account" : "sign-in"} link to <strong>{email}</strong>.</p>
              <button type="button" onClick={() => setState("idle")}>Use a different email</button>
            </div>
          ) : (
            <form className="auth-form" onSubmit={submit}>
              <label htmlFor="auth-email">Work or personal email</label>
              <div className="auth-email-field">
                <Mail size={17} aria-hidden="true" />
                <input
                  id="auth-email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                  disabled={state === "sending"}
                />
              </div>
              {state === "error" ? <p className="auth-error" role="alert">{message}</p> : null}
              <button className="auth-submit" type="submit" disabled={state === "sending" || !email.trim()}>
                <span>{state === "sending" ? "Sending secure link…" : mode === "signin" ? "Email me a sign-in link" : "Create account with Magic Link"}</span>
                {state === "sending" ? <LoaderCircle className="spin" size={18} /> : <ArrowRight size={18} />}
              </button>
              <p className="auth-terms">By continuing, you agree to use BuzzPrep for transparent technical practice. Active prep records workspace and focus events—not camera, microphone, or screen video.</p>
            </form>
          )}
        </div>
      </section>
    </main>
  );
}
