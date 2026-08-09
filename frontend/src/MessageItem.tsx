import { Bot, UserRound } from "lucide-react";
import type { InterviewMessage } from "./useInterviewStore";

export default function MessageItem({ message }: { message: InterviewMessage }) {
  const interviewer = message.role === "interviewer";
  return (
    <article className={`message ${message.role}`}>
      <div className="message-author">
        <span>{interviewer ? <Bot size={14} /> : <UserRound size={14} />}</span>
        <strong>{interviewer ? "BuzzPrep interviewer" : "Your answer"}</strong>
      </div>
      <p>{message.text}</p>
    </article>
  );
}
