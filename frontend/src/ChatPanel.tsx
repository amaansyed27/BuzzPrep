import { ArrowUp, Bot, CheckCircle2, X } from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import type { ErrorResponse } from "./apiTypes";
import { continueSession } from "./interviewApi";
import MessageItem from "./MessageItem";
import { useInterviewStore } from "./useInterviewStore";
import { useWorkspaceStore } from "./workspace/store";

export default function ChatPanel() {
  const [draft, setDraft] = useState("");
  const messages = useInterviewStore((state) => state.messages);
  const sessionId = useInterviewStore((state) => state.sessionId);
  const busy = useInterviewStore((state) => state.busy);
  const error = useInterviewStore((state) => state.lastError);
  const setBusy = useInterviewStore((state) => state.setBusy);
  const setError = useInterviewStore((state) => state.setError);
  const pushCandidateMessage = useInterviewStore((state) => state.pushCandidateMessage);
  const applyResponse = useInterviewStore((state) => state.applyResponse);
  const eventCount = useWorkspaceStore((state) => state.events.length);
  const workspaceActive = useWorkspaceStore((state) => state.workspaceActive);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  async function submitAnswer(event: FormEvent) {
    event.preventDefault();
    const answer = draft.trim();
    if (!answer || !sessionId || busy) return;
    setBusy(true);
    setError(null);
    try {
      const workspace = workspaceActive
        ? useWorkspaceStore.getState().serializeWorkspace()
        : undefined;
      const response = await continueSession({ sessionId, message: answer, workspace });
      pushCandidateMessage(answer);
      setDraft("");
      applyResponse(response);
    } catch (requestError) {
      setError(requestError as ErrorResponse);
    } finally {
      setBusy(false);
    }
  }

  return (
    <aside className="interviewer-panel">
      <header className="interviewer-heading">
        <span className="interviewer-icon"><Bot size={17} /></span>
        <div><small>Adaptive interviewer</small><strong>Evidence-aware conversation</strong></div>
        <span className="online-dot" title="Interview session active" />
      </header>

      <div className="messages" ref={scrollRef} aria-live="polite" aria-busy={busy}>
        {messages.map((message) => <MessageItem key={message.id} message={message} />)}
        {busy && (
          <div className="thinking-message">
            <span /><span /><span />
            <em>Evaluating your answer and workspace evidence</em>
          </div>
        )}
      </div>

      <div className="composer-shell">
        {error && (
          <div className="composer-error" role="alert">
            <div><strong>{error.error.code.replaceAll("_", " ")}</strong><span>{error.error.message}</span></div>
            <button onClick={() => setError(null)} aria-label="Dismiss error"><X size={14} /></button>
          </div>
        )}
        <form onSubmit={submitAnswer}>
          <label htmlFor="candidate-answer">Explain your decision</label>
          <textarea
            id="candidate-answer"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="Explain what you changed, why it works, and the trade-off you accepted…"
            disabled={busy}
            rows={4}
            onKeyDown={(event) => {
              if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <div className="composer-footer">
            <span className={eventCount > 0 ? "has-evidence" : ""}>
              <CheckCircle2 size={13} /> {eventCount} workspace action{eventCount === 1 ? "" : "s"}
            </span>
            <button type="submit" disabled={busy || !draft.trim()}>
              <ArrowUp size={17} aria-hidden="true" />
              <span className="sr-only">Send answer and workspace evidence</span>
            </button>
          </div>
        </form>
        <p className="composer-hint">Ctrl + Enter to send · selection is never counted as evidence</p>
      </div>
    </aside>
  );
}
