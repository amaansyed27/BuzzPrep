import {
  Activity,
  ArrowRight,
  Bot,
  Braces,
  ChartNoAxesCombined,
  Check,
  CircleGauge,
  Code2,
  DatabaseZap,
  Eye,
  Focus,
  GitBranch,
  Layers3,
  MemoryStick,
  MonitorUp,
  Network,
  ShieldCheck,
  SlidersHorizontal,
  TerminalSquare,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import ProductNav from "../components/ProductNav";
import ProductSequence from "./ProductSequence";

const narrative = [
  ["01", "Scenario", "A real technical constraint sets the problem."],
  ["02", "Act", "Build, connect, configure, inspect, or debug."],
  ["03", "Explain", "Defend the choice and name the trade-off."],
  ["04", "Evaluate evidence", "Your answer and workspace actions are evaluated together."],
  ["05", "Constraint", "The system changes one operating condition."],
  ["06", "Adapt", "The next question responds to what you demonstrated."],
];

const rendererModes = [
  { id: "canvas", label: "System Canvas", icon: Network, copy: "Connect services and make system boundaries visible." },
  { id: "editor", label: "Editor", icon: Code2, copy: "Work in code, prompt, SQL, JSON, and config modes." },
  { id: "config", label: "Config Lab", icon: SlidersHorizontal, copy: "Tune model, retrieval, retry, and runtime settings." },
  { id: "inspect", label: "Logs + Metrics", icon: Activity, copy: "Diagnose traces, tests, incidents, and performance shifts." },
];

function useScrollReveal() {
  useEffect(() => {
    const nodes = Array.from(document.querySelectorAll<HTMLElement>("[data-reveal]"));
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      nodes.forEach((node) => node.classList.add("revealed"));
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => entries.forEach((entry) => {
        if (entry.isIntersecting) entry.target.classList.add("revealed");
      }),
      { threshold: 0.16 },
    );
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);
}

export default function LandingPage() {
  const [renderer, setRenderer] = useState(0);
  const [reducedMotion] = useState(() => window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  const proofVideoRef = useRef<HTMLVideoElement>(null);
  useScrollReveal();
  const RendererIcon = rendererModes[renderer].icon;

  useEffect(() => {
    const video = proofVideoRef.current;
    if (!video || reducedMotion) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) void video.play().catch(() => undefined);
      else video.pause();
    }, { threshold: 0.2 });
    observer.observe(video);
    return () => observer.disconnect();
  }, [reducedMotion]);

  return (
    <main className="landing-page">
      <ProductNav transparent />
      <section className="landing-hero">
        <div className="hero-copy" data-reveal>
          <p className="eyebrow"><Focus size={14} /> Adaptive technical prep</p>
          <h1>Technical interviews should react to <em>what you do.</em></h1>
          <p>
            BuzzPrep turns prep into an adaptive technical workspace.
            Explain. Build. Debug. Adapt.
          </p>
          <div className="hero-actions">
            <Link className="primary-cta" to="/auth?mode=signup">Start a prep <ArrowRight size={17} /></Link>
            <Link className="text-cta" to="/demo/setup">Open the hackathon demo</Link>
          </div>
          <div className="hero-proof">
            <span><Check size={14} /> 8+ evidence-backed questions</span>
            <span><Check size={14} /> 4+ curriculum areas</span>
            <span><Check size={14} /> No fake completion score</span>
          </div>
        </div>
        <div className="hero-product" data-reveal>
          <div className="hero-product-label"><span>PRODUCT PREVIEW</span><em>Actions become evidence</em></div>
          <ProductSequence />
        </div>
      </section>

      <section className="statement-band" data-reveal>
        <span>NOT A CHATBOT SIMULATION</span>
        <h2>
          The interviewer adapts not only to what you say, but to what you actually
          <em> build, configure, connect, inspect, and debug.</em>
        </h2>
      </section>

      <section className="product-proof-section" data-reveal>
        <header>
          <div>
            <p className="eyebrow"><MonitorUp size={14} /> Real product, in motion</p>
            <h2>See the prep react before you start one.</h2>
          </div>
          <p>Short captures from the live product—not a concept render.</p>
        </header>
        <div className="product-proof-grid">
          <figure className="product-proof-loop">
            <video
              ref={proofVideoRef}
              autoPlay={!reducedMotion}
              muted
              loop
              playsInline
              poster="/media/adaptive-workspace-poster.jpg"
              aria-label="Short recording of the BuzzPrep workspace adapting to a candidate action"
            >
              <source src="/media/adaptive-workspace.mp4" type="video/mp4" />
            </video>
            <figcaption><span>01 / ADAPTIVE LOOP</span><strong>Constraint → workspace action → follow-up</strong></figcaption>
          </figure>
          <div className="product-proof-stills">
            <figure>
              <img src="/media/candidate-setup.jpg" alt="BuzzPrep candidate profile selection screen" loading="lazy" />
              <figcaption><span>02 / SETUP</span><strong>Start from a real candidate profile</strong></figcaption>
            </figure>
            <figure>
              <img src="/media/desktop-readiness.jpg" alt="BuzzPrep focused session readiness screen" loading="lazy" />
              <figcaption><span>03 / READINESS</span><strong>Enter a transparent focused session</strong></figcaption>
            </figure>
          </div>
        </div>
      </section>

      <section className="narrative-section" id="how-it-works">
        <div className="section-heading sticky-heading" data-reveal>
          <p className="eyebrow"><GitBranch size={14} /> One continuous loop</p>
          <h2>Every turn leaves evidence. Every next turn has a reason.</h2>
          <p>No random question bank. No completion percentage pretending to be insight.</p>
        </div>
        <div className="narrative-list">
          {narrative.map(([number, title, copy]) => (
            <article key={number} data-reveal>
              <span>{number}</span><h3>{title}</h3><p>{copy}</p><ArrowRight size={16} />
            </article>
          ))}
        </div>
      </section>

      <section className="renderer-section" id="workspace">
        <div className="section-heading" data-reveal>
          <p className="eyebrow"><Layers3 size={14} /> A workspace, not a textbox</p>
          <h2>Four interaction families. One evidence model.</h2>
        </div>
        <div className="renderer-showcase" data-reveal>
          <div className="renderer-tabs" role="tablist" aria-label="Workspace renderer modes">
            {rendererModes.map((mode, index) => {
              const Icon = mode.icon;
              return (
                <button
                  type="button"
                  role="tab"
                  aria-selected={renderer === index}
                  onClick={() => setRenderer(index)}
                  key={mode.id}
                >
                  <Icon size={16} /><span>{mode.label}</span><em>0{index + 1}</em>
                </button>
              );
            })}
          </div>
          <div className="renderer-stage">
            <header><RendererIcon size={16} /><strong>{rendererModes[renderer].label}</strong><span>Structured action stream</span></header>
            <div className={`renderer-demo mode-${rendererModes[renderer].id}`}>
              <div className="renderer-demo-primary">
                <span><TerminalSquare size={15} /> challenge.workspace</span>
                <strong>{rendererModes[renderer].copy}</strong>
                <div className="demo-lines"><i /><i /><i /><i /></div>
              </div>
              <aside>
                <span>Evidence emitted</span>
                <code>{rendererModes[renderer].id === "canvas" ? "connect(node_a, node_b)" : rendererModes[renderer].id === "editor" ? "edit(prompt.system)" : rendererModes[renderer].id === "config" ? "configure(timeout_ms)" : "submit(trace_diagnosis)"}</code>
                <small>Selection alone is never treated as semantic evidence.</small>
              </aside>
            </div>
          </div>
        </div>
      </section>

      <section className="adaptive-section">
        <div className="adaptive-copy" data-reveal>
          <p className="eyebrow"><Bot size={14} /> Adaptive interviewer</p>
          <h2>Your answer changes the next question.</h2>
          <p>
            A strong answer earns a deeper constraint. A weak answer triggers a focused
            prerequisite probe. Python keeps the coverage gate fixed; the model cannot end early.
          </p>
          <dl>
            <div><dt>Strong signal</dt><dd>Pressure-test the trade-off</dd></div>
            <div><dt>Unclear signal</dt><dd>Probe the missing prerequisite</dd></div>
            <div><dt>Workspace conflict</dt><dd>Ask about what the candidate actually changed</dd></div>
          </dl>
        </div>
        <div className="adaptive-thread" data-reveal>
          <article><span><Bot size={14} /> Interviewer</span><p>Why use a hybrid retrieval path here?</p></article>
          <article className="candidate"><span>Candidate + 3 actions</span><p>Dense recall catches semantic matches; lexical fallback protects exact identifiers.</p></article>
          <div className="constraint-insert"><ShieldCheck size={15} /> New constraint: p95 latency is now 150 ms.</div>
          <article><span><Bot size={14} /> Adaptive follow-up</span><p>Which branch do you budget first, and what recall loss will you accept?</p></article>
        </div>
      </section>

      <section className="evidence-section" id="evidence">
        <div className="section-heading" data-reveal>
          <p className="eyebrow"><MemoryStick size={14} /> Scoped evidence memory</p>
          <h2>Feedback reflects what you demonstrated.</h2>
        </div>
        <div className="evidence-ledger" data-reveal>
          <div className="ledger-head"><span>SESSION EVIDENCE</span><span>Day / turn / source</span><span>Signal</span></div>
          <div><span>D08 · T04</span><p>Explained cosine similarity; missed index recall and latency interaction.</p><em>Gap</em></div>
          <div><span>D16 · T06</span><p>Configured timeout handling and justified bounded retry behavior.</p><em className="positive">Strength</em></div>
          <div><span>D22 · T07</span><p>Trace diagnosis matched the workspace change and verbal explanation.</p><em className="positive">Evidence</em></div>
        </div>
      </section>

      <section className="curriculum-section">
        <div className="curriculum-copy" data-reveal>
          <p className="eyebrow"><DatabaseZap size={14} /> Multi-area coverage</p>
          <h2>Prep across the system, not inside one favorite topic.</h2>
          <p>Every session spans at least four curriculum days before final feedback can unlock.</p>
        </div>
        <div className="curriculum-track" data-reveal>
          {["Embeddings", "Vector DBs", "Retrieval", "Prompt systems", "Agent tools", "API reliability"].map((area, index) => (
            <span key={area}><i>DAY {String([7, 8, 10, 12, 16, 22][index]).padStart(2, "0")}</i>{area}<em>{index < 4 ? "covered" : "next"}</em></span>
          ))}
        </div>
      </section>

      <section className="focus-section">
        <div className="focus-visual" data-reveal>
          <MonitorUp size={36} />
          <span>DESKTOP FOCUS MODE</span>
          <div><Eye size={15} /> Transparent tab and fullscreen telemetry only</div>
          <div><CircleGauge size={15} /> Stable workspace and fixed composer</div>
          <div><ChartNoAxesCombined size={15} /> Results remain available on mobile</div>
        </div>
        <div className="focus-copy" data-reveal>
          <p className="eyebrow"><MonitorUp size={14} /> Proctor-ready by design</p>
          <h2>Built for focused desktop practice. No invasive surveillance.</h2>
          <p>
            Active prep uses a larger technical workspace. BuzzPrep records only transparent
            focus changes and the actions you intentionally make in the workspace—never webcam,
            screen recording, or biometrics. Optional voice input is browser-controlled and user-triggered.
          </p>
        </div>
      </section>

      <section className="final-cta" data-reveal>
        <span><Braces size={18} /> YOUR NEXT ANSWER SHOULD CHANGE THE ROOM.</span>
        <h2>Practice the part interviews usually miss: how you think while you build.</h2>
        <Link className="primary-cta" to="/auth?mode=signup">Create your BuzzPrep account <ArrowRight size={17} /></Link>
      </section>

      <footer className="landing-footer">
        <Link className="brand-lockup compact" to="/"><span>BuzzPrep</span></Link>
        <p>Adaptive technical preparation grounded in real workspace evidence.</p>
        <div><Link to="/auth?mode=signin">Sign in</Link><Link to="/demo/setup">Demo</Link><a href="https://github.com/amaansyed27/BuzzPrep">GitHub</a></div>
      </footer>
    </main>
  );
}
