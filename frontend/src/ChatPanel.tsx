import React from "react";
import MessageItem from "./MessageItem";
import ChatInput from "./ChatInput";
import { useInterviewStore } from "./useInterviewStore";

export default function ChatPanel() {
  const messages = useInterviewStore((s) => s.messages);
  const lastError = useInterviewStore((s) => s.lastError);
  const busy = useInterviewStore((s) => s.busy);

  return (
    <aside className="panel chat-panel">
      <div className="panel-heading">
        <div>
          <p className="panel-kicker">Conversation</p>
          <h2>AI interviewer</h2>
        </div>
      </div>

      <div className="messages" aria-live="polite">
        {messages.length === 0 && <p className="muted">No messages yet. Start the demo to begin.</p>}
        {messages.map((m, i) => (
          <MessageItem key={`${m.role}-${i}`} role={m.role} text={m.text} />
        ))}
      </div>

      <div className="chat-form-wrap">
        {lastError && <div className="error-banner">Error: {lastError.error.message}</div>}
        <ChatInput />
        {busy && <div className="busy-overlay">Working…</div>}
      </div>
    </aside>
  );
}
