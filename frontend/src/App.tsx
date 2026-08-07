import { FormEvent, useMemo, useState } from "react";
import {
  Background,
  Controls,
  Edge,
  MiniMap,
  Node,
  ReactFlow,
} from "@xyflow/react";
import { Bot, Play, Send } from "lucide-react";

type ChatMessage = {
  role: "interviewer" | "candidate";
  text: string;
};

const starterNodes: Node[] = [
  { id: "scenario", position: { x: 80, y: 120 }, data: { label: "Scenario" } },
  { id: "workspace", position: { x: 310, y: 120 }, data: { label: "Interactive task" } },
  { id: "outcome", position: { x: 560, y: 120 }, data: { label: "Explain decision" } },
];

const starterEdges: Edge[] = [
  { id: "scenario-workspace", source: "scenario", target: "workspace" },
  { id: "workspace-outcome", source: "workspace", target: "outcome" },
];

export default function App() {
  const sessionId = useMemo(() => crypto.randomUUID(), []);
  const [started, setStarted] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "interviewer",
      text: "Scaffold ready. Start a demo session to verify the frontend-to-API flow.",
    },
  ]);

  async function callInterview(body: Record<string, unknown>) {
    setBusy(true);
    try {
      const response = await fetch("/api/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, ...body }),
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const data = (await response.json()) as { reply: string };
      setMessages((current) => [
        ...current,
        { role: "interviewer", text: data.reply },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown API error";
      setMessages((current) => [
        ...current,
        { role: "interviewer", text: `Connection error: ${message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function startDemo() {
    await callInterview({ candidate: { member: { name: "Demo Candidate" } } });
    setStarted(true);
  }

  async function submitMessage(event: FormEvent) {
    event.preventDefault();
    const value = input.trim();
    if (!value || !started || busy) return;

    setMessages((current) => [...current, { role: "candidate", text: value }]);
    setInput("");
    await callInterview({ message: value });
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">BuzzBees</p>
          <h1>BuzzPrep</h1>
        </div>
        <span className="status-pill">Scaffold</span>
      </header>

      <section className="workspace-grid">
        <aside className="panel candidate-panel">
          <p className="panel-kicker">Interview</p>
          <h2>Adaptive technical workspace</h2>
          <p>
            The final product will select curriculum tasks from the supplied candidate profile
            and evaluate both conversation and workspace actions.
          </p>
          <dl className="session-meta">
            <div>
              <dt>Session</dt>
              <dd>{sessionId.slice(0, 8)}</dd>
            </div>
            <div>
              <dt>State</dt>
              <dd>{started ? "Demo started" : "Not started"}</dd>
            </div>
          </dl>
          <button className="primary-button" onClick={startDemo} disabled={started || busy}>
            <Play size={16} />
            {started ? "Demo started" : "Start demo session"}
          </button>
        </aside>

        <section className="panel canvas-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Interactive task</p>
              <h2>Challenge canvas</h2>
            </div>
            <span>React Flow</span>
          </div>
          <div className="flow-wrap">
            <ReactFlow nodes={starterNodes} edges={starterEdges} fitView>
              <Background />
              <MiniMap pannable zoomable />
              <Controls />
            </ReactFlow>
          </div>
        </section>

        <aside className="panel chat-panel">
          <div className="panel-heading">
            <div>
              <p className="panel-kicker">Conversation</p>
              <h2>AI interviewer</h2>
            </div>
            <Bot size={20} />
          </div>

          <div className="messages" aria-live="polite">
            {messages.map((message, index) => (
              <div className={`message ${message.role}`} key={`${message.role}-${index}`}>
                <strong>{message.role === "interviewer" ? "Interviewer" : "You"}</strong>
                <p>{message.text}</p>
              </div>
            ))}
          </div>

          <form className="chat-form" onSubmit={submitMessage}>
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder={started ? "Explain your decision…" : "Start the demo first"}
              disabled={!started || busy}
            />
            <button type="submit" aria-label="Send message" disabled={!started || busy}>
              <Send size={17} />
            </button>
          </form>
        </aside>
      </section>
    </main>
  );
}
