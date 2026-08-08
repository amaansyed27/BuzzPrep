import React from "react";

export default function MessageItem({ role, text }: { role: "interviewer" | "candidate"; text: string }) {
  return (
    <div className={`message ${role}`}>
      <strong>{role === "interviewer" ? "Interviewer" : "You"}</strong>
      <p>{text}</p>
    </div>
  );
}
