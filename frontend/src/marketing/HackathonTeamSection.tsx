import { ArrowUpRight, Github, Trophy, Users } from "lucide-react";
import "./hackathon-team.css";

const team = [
  {
    name: "Ilma Khan",
    handle: "ilmatech",
    role: "Team Leader",
    href: "https://github.com/ilmatech",
    avatar: "https://github.com/ilmatech.png?size=240",
  },
  {
    name: "Amaan Syed",
    handle: "amaansyed27",
    role: "Team Member",
    href: "https://github.com/amaansyed27",
    avatar: "https://avatars.githubusercontent.com/u/96974001?v=4",
  },
];

export default function HackathonTeamSection() {
  return (
    <section className="hackathon-team-section" data-reveal>
      <div className="hackathon-track-panel">
        <div className="hackathon-track-mark" aria-hidden="true">
          <Trophy size={26} />
          <span>TRACK 01</span>
        </div>
        <div className="hackathon-track-copy">
          <p className="eyebrow"><Trophy size={14} /> Built for the ABTalks Hackathon</p>
          <h2>The Interview Agent</h2>
          <p className="hackathon-track-line">Build the interviewer, not the interview.</p>
          <p className="hackathon-track-description">
            BuzzPrep was created for this track as an adaptive technical interviewer that reacts
            to both the candidate&apos;s explanation and the engineering actions they take in the workspace.
          </p>
          <a
            className="hackathon-track-link"
            href="https://www.abtalks.in/hackathon"
            target="_blank"
            rel="noreferrer"
          >
            View the hackathon <ArrowUpRight size={15} />
          </a>
        </div>
      </div>

      <div className="hackathon-team-panel">
        <header>
          <div>
            <p className="eyebrow"><Users size={14} /> The team behind BuzzPrep</p>
            <h3>Team BuzzBees</h3>
          </div>
          <span>02 BUILDERS</span>
        </header>

        <div className="hackathon-member-grid">
          {team.map((member) => (
            <a
              className="hackathon-member"
              href={member.href}
              target="_blank"
              rel="noreferrer"
              key={member.handle}
            >
              <img src={member.avatar} alt={`${member.name} GitHub profile`} loading="lazy" />
              <div>
                <span>{member.role}</span>
                <strong>{member.name}</strong>
                <code><Github size={13} /> @{member.handle}</code>
              </div>
              <ArrowUpRight className="hackathon-member-arrow" size={17} />
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}
