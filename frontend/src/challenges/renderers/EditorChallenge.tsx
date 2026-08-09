import Editor from "@monaco-editor/react";
import { CheckCircle2, FlaskConical, Send } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useWorkspaceStore } from "../../workspace/store";
import type { ChallengeRendererProps, EditorMode } from "../types";

function preferredMode(interactionType: string, modes: EditorMode[]) {
  if (interactionType === "prompt_schema_editor") {
    return modes.find((mode) => mode.id === "json") ?? modes[0];
  }
  return modes.find((mode) => mode.id === "code") ?? modes[0];
}

export default function EditorChallenge({
  definition,
  interactionType,
}: ChallengeRendererProps) {
  const editors = useWorkspaceStore((state) => state.editors);
  const edit = useWorkspaceStore((state) => state.edit);
  const run = useWorkspaceStore((state) => state.run);
  const submit = useWorkspaceStore((state) => state.submit);
  const initialMode = useMemo(
    () => preferredMode(interactionType, definition.editorModes),
    [definition.editorModes, interactionType],
  );
  const [activeId, setActiveId] = useState(initialMode.id);
  const [drafts, setDrafts] = useState<Record<string, string>>(() =>
    Object.fromEntries(
      definition.editorModes.map((mode) => [`editor-${mode.id}`, mode.content]),
    ),
  );
  const [checkMessage, setCheckMessage] = useState<string | null>(null);
  const activeMode =
    definition.editorModes.find((mode) => mode.id === activeId) ?? initialMode;
  const editorId = `editor-${activeMode.id}`;

  useEffect(() => {
    setActiveId(initialMode.id);
    setDrafts(
      Object.fromEntries(
        definition.editorModes.map((mode) => [`editor-${mode.id}`, mode.content]),
      ),
    );
    setCheckMessage(null);
  }, [definition.editorModes, definition.id, initialMode.id]);

  function commitDraft() {
    const content = drafts[editorId] ?? activeMode.content;
    if (content !== editors[editorId]) edit(editorId, content);
    return content;
  }

  function checkDraft() {
    commitDraft();
    run(editorId);
    setCheckMessage(
      "Static review recorded. BuzzPrep did not execute arbitrary code; discuss the expected runtime behavior in your answer.",
    );
  }

  function submitDraft() {
    const content = commitDraft();
    submit(`${definition.id}-${activeMode.id}`, {
      editorMode: activeMode.id,
      content,
      reviewType: "candidate_draft",
    });
    setCheckMessage("Draft attached as workspace evidence. Explain the important decision before sending.");
  }

  return (
    <div className="editor-renderer">
      <div className="editor-tabs" role="tablist" aria-label="Editor modes">
        {definition.editorModes.map((mode) => (
          <button
            key={mode.id}
            role="tab"
            aria-selected={activeId === mode.id}
            className={activeId === mode.id ? "active" : ""}
            onClick={() => {
              commitDraft();
              setActiveId(mode.id);
              setCheckMessage(null);
            }}
          >
            {mode.label}
          </button>
        ))}
      </div>
      <div className="editor-toolbar">
        <span className="editor-language">{activeMode.language}</span>
        <div>
          <button className="quiet-button" onClick={checkDraft}>
            <FlaskConical size={14} aria-hidden="true" /> Check
          </button>
          <button className="workspace-primary-button" onClick={submitDraft}>
            <Send size={14} aria-hidden="true" /> Attach draft
          </button>
        </div>
      </div>
      <div className="monaco-shell">
        <Editor
          height="100%"
          language={activeMode.language}
          theme="vs-dark"
          value={drafts[editorId] ?? activeMode.content}
          onChange={(value) =>
            setDrafts((current) => ({ ...current, [editorId]: value ?? "" }))
          }
          onMount={(_, monaco) => {
            monaco.editor.defineTheme("buzzprep-dark", {
              base: "vs-dark",
              inherit: true,
              rules: [],
              colors: {
                "editor.background": "#0d1217",
                "editorLineNumber.foreground": "#4d5b68",
                "editorCursor.foreground": "#f4b942",
              },
            });
            monaco.editor.setTheme("buzzprep-dark");
          }}
          options={{
            minimap: { enabled: false },
            fontSize: 13,
            lineHeight: 21,
            padding: { top: 16 },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            wordWrap: "on",
            tabSize: 2,
          }}
        />
      </div>
      <div className="editor-output" aria-live="polite">
        <CheckCircle2 size={15} aria-hidden="true" />
        {checkMessage ?? "Make a focused repair, then attach the draft as evidence."}
      </div>
    </div>
  );
}
