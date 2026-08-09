import { ArrowLeft, Check, Copy, MonitorUp, Share2 } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

export default function DesktopRequirement({ backTo = "/dashboard" }: { backTo?: string }) {
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    await navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return (
    <main className="desktop-gate">
      <Link className="brand-lockup" to="/"><span className="brand-mark">B</span><span>BUZZPREP</span></Link>
      <section>
        <span className="desktop-gate-icon"><MonitorUp size={34} /></span>
        <small>ACTIVE PREP REQUIREMENT</small>
        <h1>This prep is designed for a desktop or laptop.</h1>
        <p>BuzzPrep uses an interactive technical workspace and transparent focus checks that need a larger screen and precise pointer.</p>
        <ul>
          <li><Check size={15} /> Landing, dashboard, history, and results work here</li>
          <li><Check size={15} /> Your active prep remains saved</li>
          <li><Check size={15} /> Open this URL on a computer to continue</li>
        </ul>
        <div>
          <Link to={backTo}><ArrowLeft size={16} /> Back to dashboard</Link>
          <button type="button" onClick={copyLink}>{copied ? <Check size={16} /> : <Copy size={16} />}{copied ? "Copied" : "Copy prep URL"}</button>
          {typeof navigator.share === "function" ? <button type="button" onClick={() => void navigator.share({ title: "BuzzPrep", url: window.location.href })}><Share2 size={16} /> Share</button> : null}
        </div>
      </section>
    </main>
  );
}
