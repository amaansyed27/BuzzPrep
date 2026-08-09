import {
  ArrowUp,
  Bot,
  CheckCircle2,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  X,
} from "lucide-react";
import { type FormEvent, useEffect, useRef, useState } from "react";
import type { ErrorResponse } from "./apiTypes";
import { useAuth } from "./auth/AuthProvider";
import { continueSession } from "./interviewApi";
import MessageItem from "./MessageItem";
import { drainIntegrityEvents, restoreIntegrityEvents } from "./prep/integrityTelemetry";
import { useInterviewStore } from "./useInterviewStore";
import { useWorkspaceStore } from "./workspace/store";

type SpeechResultEvent = {
  resultIndex: number;
  results: ArrayLike<{ isFinal: boolean; 0: { transcript: string } }>;
};

type SpeechRecognitionLike = {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechResultEvent) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

function getSpeechRecognition(): SpeechRecognitionConstructor | null {
  const speechWindow = window as typeof window & {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  };
  return speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition ?? null;
}

function getNaturalVoice(): SpeechSynthesisVoice | undefined {
  const locale = navigator.language.toLowerCase();
  const language = locale.split("-")[0];
  const voices = window.speechSynthesis.getVoices();
  const qualityPattern = /natural|neural|online|google|aria|jenny|guy|samantha|serena|daniel/i;
  return voices
    .map((voice) => {
      const voiceLocale = voice.lang.toLowerCase();
      let score = qualityPattern.test(voice.name) ? 8 : 0;
      if (voiceLocale === locale) score += 5;
      else if (voiceLocale.startsWith(language)) score += 3;
      if (!voice.localService) score += 2;
      return { voice, score };
    })
    .sort((left, right) => right.score - left.score)[0]?.voice;
}

export default function ChatPanel() {
  const { session } = useAuth();
  const [draft, setDraft] = useState("");
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [listening, setListening] = useState(false);
  const [speechError, setSpeechError] = useState<string | null>(null);
  const [voiceCount, setVoiceCount] = useState(0);
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
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const dictationBaseRef = useRef("");
  const lastSpokenRef = useRef<string | null>(null);
  const speechAvailable = typeof window !== "undefined" && "speechSynthesis" in window;
  const recognitionAvailable = typeof window !== "undefined" && getSpeechRecognition() !== null;

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, busy]);

  useEffect(() => {
    if (!speechAvailable) return;
    const refreshVoices = () => setVoiceCount(window.speechSynthesis.getVoices().length);
    refreshVoices();
    window.speechSynthesis.addEventListener("voiceschanged", refreshVoices);
    return () => window.speechSynthesis.removeEventListener("voiceschanged", refreshVoices);
  }, [speechAvailable]);

  useEffect(() => {
    const latest = messages.at(-1);
    if (!autoSpeak || !speechAvailable || voiceCount === 0 || latest?.role !== "interviewer" || latest.id === lastSpokenRef.current) {
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(latest.text);
    utterance.voice = getNaturalVoice() ?? null;
    utterance.rate = 0.97;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
    lastSpokenRef.current = latest.id;
  }, [autoSpeak, messages, speechAvailable, voiceCount]);

  useEffect(() => () => {
    recognitionRef.current?.stop();
    window.speechSynthesis?.cancel();
  }, []);

  function toggleReadAloud() {
    if (!speechAvailable) return;
    if (autoSpeak) {
      window.speechSynthesis.cancel();
      setAutoSpeak(false);
      return;
    }
    lastSpokenRef.current = null;
    setAutoSpeak(true);
  }

  function toggleDictation() {
    if (listening) {
      recognitionRef.current?.stop();
      return;
    }
    const Recognition = getSpeechRecognition();
    if (!Recognition) {
      setSpeechError("Voice input is not supported in this browser. You can keep typing normally.");
      return;
    }
    setSpeechError(null);
    dictationBaseRef.current = draft.trimEnd();
    const recognition = new Recognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = navigator.language || "en-US";
    recognition.onresult = (event) => {
      let transcript = "";
      for (let index = 0; index < event.results.length; index += 1) {
        transcript += event.results[index][0].transcript;
      }
      const spacer = dictationBaseRef.current && transcript ? " " : "";
      setDraft(`${dictationBaseRef.current}${spacer}${transcript}`);
    };
    recognition.onerror = () => {
      setSpeechError("Voice input stopped. Check microphone permission or continue typing.");
      setListening(false);
    };
    recognition.onend = () => setListening(false);
    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }

  async function submitAnswer(event: FormEvent) {
    event.preventDefault();
    const answer = draft.trim();
    if (!answer || !sessionId || busy) return;
    recognitionRef.current?.stop();
    setBusy(true);
    setError(null);
    const integrityEvents = drainIntegrityEvents();
    try {
      const workspace = workspaceActive
        ? useWorkspaceStore.getState().serializeWorkspace()
        : undefined;
      const response = await continueSession(
        { sessionId, message: answer, workspace, integrityEvents },
        session?.access_token,
      );
      pushCandidateMessage(answer);
      setDraft("");
      applyResponse(response);
    } catch (requestError) {
      restoreIntegrityEvents(integrityEvents);
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
        <button
          className={`speech-toggle${autoSpeak ? " active" : ""}`}
          type="button"
          onClick={toggleReadAloud}
          disabled={!speechAvailable}
          aria-pressed={autoSpeak}
          title={speechAvailable ? `${autoSpeak ? "Turn off" : "Turn on"} interviewer read-aloud` : "Read-aloud is unavailable in this browser"}
        >
          {autoSpeak ? <Volume2 size={15} /> : <VolumeX size={15} />}
          <span className="sr-only">{autoSpeak ? "Disable" : "Enable"} interviewer read-aloud</span>
        </button>
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
        {speechError && (
          <div className="speech-error" role="status">
            <span>{speechError}</span>
            <button type="button" onClick={() => setSpeechError(null)} aria-label="Dismiss voice input message"><X size={13} /></button>
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
            <div className="composer-actions">
              <button
                className={`dictation-button${listening ? " listening" : ""}`}
                type="button"
                onClick={toggleDictation}
                disabled={busy || !recognitionAvailable}
                aria-pressed={listening}
                title={recognitionAvailable ? `${listening ? "Stop" : "Start"} voice input` : "Voice input is unavailable in this browser"}
              >
                {listening ? <MicOff size={15} /> : <Mic size={15} />}
                <span className="sr-only">{listening ? "Stop" : "Start"} voice input</span>
              </button>
              <button className="submit-answer" type="submit" disabled={busy || !draft.trim()}>
                <ArrowUp size={17} aria-hidden="true" />
                <span className="sr-only">Send answer and workspace evidence</span>
              </button>
            </div>
          </div>
        </form>
        <p className="composer-hint">{listening ? "Listening… speak naturally" : "Ctrl + Enter to send · microphone input stays in your browser"}</p>
      </div>
    </aside>
  );
}
