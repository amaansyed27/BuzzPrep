import React, { FormEvent, useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { sendMessage as apiSend } from "./interviewApi";
import { useInterviewStore } from "./useInterviewStore";

export default function ChatInput() {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement | null>(null);
  const sessionId = useInterviewStore((s) => s.sessionId);
  const busy = useInterviewStore((s) => s.busy);
  const started = useInterviewStore((s) => s.started);
  const setBusy = useInterviewStore((s) => s.setBusy);
  const pushMessage = useInterviewStore((s) => s.pushMessage);
  const setError = useInterviewStore((s) => s.setError);

  useEffect(() => {
    if (!started) setValue("");
  }, [started]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const text = value.trim();
    if (!text || !sessionId || !started || busy) return;
    pushMessage({ role: "candidate", text });
    setValue("");
    setBusy(true);
    try {
      const resp = await apiSend(sessionId, text);
      pushMessage({ role: "interviewer", text: resp.reply });
    } catch (err) {
      setError((err as any) ?? { error: { code: "client_error", message: "Connection error", details: null } });
    } finally {
      setBusy(false);
      inputRef.current?.focus();
    }
  }

  return (
    <form className="chat-form" onSubmit={submit} aria-label="Send message">
      <input
        ref={inputRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={started ? "Explain your decision…" : "Start the demo first"}
        disabled={!started || busy}
        aria-label="Message"
      />
      <button type="submit" aria-label="Send message" disabled={!started || busy || !value.trim()}>
        <Send size={16} />
      </button>
    </form>
  );
}
