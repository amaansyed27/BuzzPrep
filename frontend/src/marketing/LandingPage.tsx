import {
  Activity,
  ArrowDown,
  ArrowRight,
  Bot,
  Braces,
  ChartNoAxesCombined,
  Check,
  CircleGauge,
  Code2,
  Eye,
  Focus,
  GitBranch,
  Layers3,
  MemoryStick,
  MonitorUp,
  Network,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  TerminalSquare,
  Workflow,
} from "lucide-react";
import { type CSSProperties, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import ProductNav from "../components/ProductNav";
import ProductSequence from "./ProductSequence";
import "./landing-cinematic.css";
import { useLandingCinematics } from "./useLandingCinematics";

const narrative = [
  { number: "01", title: "Scenario", copy: "A real technical constraint sets the problem.", event: "challenge.open(day_08)" },
  { number: "02", title: "Act", copy: "Build, connect, configure, inspect, or debug in the workspace.", event: "workspace.connect(retriever, ranker)" },
  { number: "03", title: "Explain", copy: "Defend the decision and name the trade-off you accepted.", event: "answer.attach(workspace_evidence)" },
  { number: "04", title: "Evaluate evidence", copy: "Your explanation and meaningful workspace actions are evaluated together.", event: "evaluate(answer + actions)" },
  { number: "05", title: "Constraint", copy: "BuzzPrep changes one operating condition instead of moving on blindly.", event: "constraint.inject(p95_latency=150ms)" },
  { number: "06", title: "Adapt", copy: "The next question responds to what you actually demonstrated.", event: "follow_up.generate(evidence)" },
];

const rendererModes = [
  { id: "canvas", label: "System Canvas", icon: Network, copy: "Connect services and make system boundaries visible.", event: "connect(node_a, node_b)" },
  { id: "editor", label: "Editor", icon: Code2, copy: "Work in code, prompt, SQL, JSON, and config modes.", event: "edit(prompt.system)" },
  { id: "config", label: "Config Lab", icon: SlidersHorizontal, copy: "Tune model, retrieval, retry, and runtime settings.", event: "configure(timeout_ms)" },
  { id: "inspect", label: "Logs + Metrics", icon: Activity, copy: "Diagnose traces, tests, incidents, and performance shifts.", event: "submit(trace_diagnosis)" },
];

const curriculumAreas = [
  ["07", "Embeddings"],
  ["08", "Vector DBs"],
  ["10", "Retrieval"],
  ["12", "Prompt systems"],
  ["16", "API reliability"],
  ["22", "Agent tools"],
];

function RevealWords({ text }: { text: string }) {
  return (
    <span className="cinematic-word-line" aria-label={text}>
      {text.split(" ").map((word, index) => (
        <span
          aria-hidden="true"
          className="cinematic-word"
          key={`${word}-${index}`}
          style={{ "--word-delay": `${Math.min(index * 34, 620)}ms` } as CSSProperties}
        >
          {word}&nbsp;
        </span>
      ))}
    </span>
  );
}

export default function LandingPage() {
  const [renderer, setRenderer] = useState(0);
  const rootRef = useRef<HTMLElement>(null);
  const heroRef = useRef<HTMLElement>(null);
  const loopRef = useRef<HTMLElement>(null);
  const proofVideoRef = useRef<HTMLVideoElement>(null);
  const activeStep = useLandingCinematics(rootRef, heroRef, loopRef, narrative.length);
  const RendererIcon = rendererModes[renderer].icon;
  const activeNarrative = narrative[activeStep];

  useEffect(() => {
    const video = proofVideoRef.current;
    if (!video || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) void video.play().catch(() => undefined);
      else video.pause();
    }, { threshold: 0.2 });
    observer.observe(video);
    return () => observer.disconnect();
  }, []);

  return (
    <main className="landing-page cinematic-landing" ref={rootRef}>
      <ProductNav transparent />
      <div className="cinematic-atmosphere" aria-hidden="true" />
      <div className="cinematic-grid" aria-hidden="true" />

      <section className="cinematic-hero" ref={heroRef}>
        <div className="cinematic-hero-sticky">
          <div className="cinematic-hero-copy" data-hero-meta>
            <p className="eyebrow"><Focus size={14} /> Adaptive technical prep</p>
            <div className="cinematic-live-note"><span /> EVIDENCE-AWARE INTERVIEW ENGINE</div>
          </div>

          <h1 className="cinematic-hero-title" aria-label="Technical interviews should react to what you do">
            <span data-hero-line>Technical interviews</span>
            <span data-hero-line>should react to</span>
            <span data-hero-line><em>what you do.</em></span>
          </h1>

          <div className="cinematic-hero-support" data-hero-meta>
            <p>Explain. Build. Debug. Adapt. BuzzPrep evaluates the answer and the engineering actions behind it.</p>
            <div className="hero-actions">
              <Link className="primary-cta" to="/auth?mode=signup">Start a prep <ArrowRight size={17} /></Link>
              <Link className="text-cta" to="/demo/setup">Open the hackathon demo</Link>
            </div>
            <div className="hero-proof">
              <span><Check size={14} /> 8+ evidence-backed questions</span>
              <span><Check size={14} /> 4+ curriculum days</span>
              <span><Check size={14} /> 31-day curriculum grounded</span>
            </div>
          </div>

          <div className="cinematic-hero-product" data-hero-product>
            <div className="cinematic-product-label"><span>LIVE PRODUCT PREVIEW</span><em>Actions become evidence</em></div>
            <ProductSequence compact />
          </div>

          <div className="cinematic-scroll-cue" data-hero-cue aria-hidden="true">
            <span>SCROLL TO ENTER THE INTERVIEW</span>
            <ArrowDown size={15} />
          </div>
        </div>
      </section>

      <section className="cinematic-statement">
        <div className="cinematic-section-index" data-reveal>01 / THE DIFFERENCE</div>
        <h2 data-reveal>
          <RevealWords text="A chatbot hears your answer." />
          <span className="statement-dim"><RevealWords text="BuzzPrep watches the engineering decision unfold." /></span>
        </h2>
        <div className="cinematic-statement-proof" data-reveal>
          <span><Workflow size={15} /> workspace actions</span>
          <ArrowRight size={14} />
          <span><Bot size={15} /> adaptive follow-up</span>
          <ArrowRight size={14} />
          <span><MemoryStick size={15} /> evidence-backed feedback</span>
        </div>
      </section>

      <section className="cinematic-loop" id="how-it-works" ref={loopRef}>
        <div className="cinematic-loop-sticky">
          <div className="cinematic-loop-heading">
            <p className="eyebrow"><GitBranch size={14} /> One continuous loop</p>
            <h2>Every next question has a reason.</h2>
            <p>No random question bank. No fake completion score. The interview keeps pressure on the evidence.</p>
          </div>

          <div className="cinematic-loop-stage" aria-live="polite">
            <header>
              <span><i /> LIVE INTERVIEW GRAPH</span>
              <strong>STEP {activeNarrative.number} / 06</strong>
            </header>
            <div className="loop-stage-grid" aria-hidden="true" />
            <div className="loop-stage-rail" aria-hidden="true">
              {narrative.map((item, index) => (
                <span className={index <= activeStep ? "passed" : ""} key={item.number}><i /></span>
              ))}
            </div>
            <div className="loop-stage-card" key={activeNarrative.number}>
              <span>{activeNarrative.number} / {activeNarrative.title}</span>
              <h3>{activeNarrative.copy}</h3>
              <code>{activeNarrative.event}</code>
            </div>
            <footer>
              <span>candidate + workspace</span>
              <ArrowRight size={14} />
              <span>next interview state</span>
            </footer>
          </div>

          <div className="cinematic-loop-steps">
            {narrative.map((item, index) => (
              <article className={index === activeStep ? "active" : index < activeStep ? "passed" : ""} key={item.number}>
                <span>{item.number}</span>
                <div><h3>{item.title}</h3><p>{item.copy}</p></div>
                <ArrowRight size={15} />
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="cinematic-workspace" id="workspace">
        <div className="workspace-intro" data-reveal>
          <div>
            <p className="eyebrow"><Layers3 size={14} /> A workspace, not a textbox</p>
            <h2><RevealWords text="Four interaction families. One evidence model." /></h2>
          </div>
          <p>BuzzPrep changes the environment to fit the engineering skill being tested instead of forcing every topic into the same UI.</p>
        </div>

        <div className="cinematic-renderer" data-reveal data-parallax="0.04">
          <div className="cinematic-renderer-tabs" role="tablist" aria-label="Workspace renderer modes">
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
                  <span>0{index + 1}</span><Icon size={16} /><strong>{mode.label}</strong>
                </button>
              );
            })}
          </div>

          <div className="cinematic-renderer-stage">
            <header><RendererIcon size={16} /><strong>{rendererModes[renderer].label}</strong><span>STRUCTURED ACTION STREAM</span></header>
            <div className={`cinematic-renderer-demo mode-${rendererModes[renderer].id}`}>
              <div className="renderer-main-panel">
                <span><TerminalSquare size={15} /> challenge.workspace</span>
                <strong>{rendererModes[renderer].copy}</strong>
                <div className="renderer-visual-lines"><i /><i /><i /><i /><i /></div>
                <div className="renderer-nodes" aria-hidden="true"><b /><b /><b /></div>
              </div>
              <aside>
                <span>Evidence emitted</span>
                <code>{rendererModes[renderer].event}</code>
                <small>Selection alone is UI state. Only meaningful mutations become semantic evidence.</small>
              </aside>
            </div>
          </div>
        </div>
      </section>

      <section className="cinematic-adaptive">
        <div className="adaptive-giant" data-reveal>
          <span>02 / PRESSURE TEST</span>
          <h2><RevealWords text="Strong answers do not end the conversation." /></h2>
          <p>They earn a harder constraint.</p>
        </div>
        <div className="adaptive-conversation" data-reveal data-parallax="0.03">
          <article><span><Bot size={14} /> Interviewer</span><p>Why use a hybrid retrieval path here?</p></article>
          <article className="candidate"><span>Candidate + 3 workspace actions</span><p>Dense recall catches semantic matches; lexical fallback protects exact identifiers.</p></article>
          <div className="constraint-insert"><ShieldCheck size={15} /> New constraint: p95 latency is now 150 ms.</div>
          <article><span><Bot size={14} /> Adaptive follow-up</span><p>Which branch do you budget first, and what recall loss will you accept?</p></article>
        </div>
      </section>

      <section className="cinematic-proof">
        <header data-reveal>
          <div>
            <p className="eyebrow"><MonitorUp size={14} /> Real product, in motion</p>
            <h2>Not a concept render.</h2>
          </div>
          <p>These captures come from the working BuzzPrep product flow.</p>
        </header>
        <div className="cinematic-proof-grid" data-reveal>
          <figure className="cinematic-proof-loop">
            <video
              ref={proofVideoRef}
              autoPlay
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
          <div className="cinematic-proof-stills">
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

      <section className="cinematic-evidence" id="evidence">
        <div className="evidence-heading" data-reveal>
          <span>03 / FEEDBACK WITH RECEIPTS</span>
          <h2><RevealWords text="Feedback should remember what you demonstrated." /></h2>
          <p>Concise evidence follows the interview without replacing canonical session state.</p>
        </div>

        <div className="cinematic-evidence-grid">
          <div className="evidence-ledger" data-reveal>
            <div className="ledger-head"><span>SESSION EVIDENCE</span><span>Day / turn / source</span><span>Signal</span></div>
            <div><span>D08 · T04</span><p>Explained cosine similarity; missed index recall and latency interaction.</p><em>Gap</em></div>
            <div><span>D16 · T06</span><p>Configured timeout handling and justified bounded retry behavior.</p><em className="positive">Strength</em></div>
            <div><span>D22 · T07</span><p>Trace diagnosis matched the workspace change and verbal explanation.</p><em className="positive">Evidence</em></div>
          </div>
          <div className="evidence-stats" data-reveal>
            <article><strong>8+</strong><span>questions before completion</span></article>
            <article><strong>4+</strong><span>distinct curriculum days</span></article>
            <article><strong>31</strong><span>curriculum days available</span></article>
          </div>
        </div>

        <div className="curriculum-marquee" data-reveal aria-label="Example curriculum areas">
          <div>
            {[...curriculumAreas, ...curriculumAreas].map(([day, area], index) => (
              <span key={`${day}-${area}-${index}`}><i>DAY {day}</i>{area}<em>{index % 3 === 0 ? "evidence" : "adaptive"}</em></span>
            ))}
          </div>
        </div>
      </section>

      <section className="cinematic-focus">
        <div className="focus-visual" data-reveal>
          <MonitorUp size={36} />
          <span>DESKTOP FOCUS MODE</span>
          <div><Eye size={15} /> Transparent tab and fullscreen telemetry only</div>
          <div><CircleGauge size={15} /> Stable workspace and fixed composer</div>
          <div><ChartNoAxesCombined size={15} /> Results remain available on mobile</div>
        </div>
        <div className="focus-copy" data-reveal>
          <p className="eyebrow"><ShieldCheck size={14} /> Focused, not invasive</p>
          <h2>Practice under pressure without surveillance theater.</h2>
          <p>BuzzPrep records the workspace actions you intentionally make and transparent focus-state changes—never webcam, screen recording, or biometrics. Voice input is opt-in and browser-controlled.</p>
        </div>
      </section>

      <section className="cinematic-final">
        <div className="final-orbit" aria-hidden="true"><span /><span /><span /></div>
        <div data-reveal>
          <span><Sparkles size={17} /> THE NEXT ANSWER SHOULD CHANGE THE ROOM.</span>
          <h2><RevealWords text="Practice how you think while you build." /></h2>
          <p>Eight or more questions. Four or more curriculum days. One interview that actually reacts.</p>
          <div className="hero-actions">
            <Link className="primary-cta" to="/auth?mode=signup">Create your BuzzPrep account <ArrowRight size={17} /></Link>
            <Link className="text-cta" to="/demo/setup">Run the public demo</Link>
          </div>
        </div>
      </section>

      <footer className="landing-footer cinematic-footer">
        <Link className="brand-lockup compact" to="/"><span>BuzzPrep</span></Link>
        <p>Adaptive technical preparation grounded in real workspace evidence.</p>
        <div><Link to="/auth?mode=signin">Sign in</Link><Link to="/demo/setup">Demo</Link><a href="https://github.com/amaansyed27/BuzzPrep">GitHub</a></div>
      </footer>
    </main>
  );
}
