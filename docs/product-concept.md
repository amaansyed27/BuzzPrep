# BuzzPrep Product Concept

## Product statement

BuzzPrep is an **adaptive, evidence-aware technical interview simulator** for the supplied 31-day AI Cohort.

The product combines a conversational interviewer with a structured engineering workspace. A candidate is not evaluated only on the text of an answer: the interview can also use machine-readable evidence from actions such as changing configuration, editing code or prompts, connecting architecture components, running a task, or submitting a structured decision.

That distinction is the core product idea:

> **A technical interview should evaluate engineering decisions, not only interview prose.**

BuzzPrep is implemented as a full browser product and as the organizer-compatible public `POST /api/interview` API. The visual workspace is additive; the required conversational API remains usable independently.

## The two synchronized interview channels

Every full BuzzPrep interview can combine two evidence channels.

### 1. Conversation

The adaptive interviewer:

- asks curriculum-grounded questions;
- evaluates the candidate's latest answer;
- uses prior conversation context;
- decides whether to follow up, deepen, or move to another curriculum area;
- generates structured final feedback.

### 2. Interactive workspace

The candidate can perform practical actions in a reusable technical workspace. Workspace mutations are serialized into a stable schema and sent with the candidate's answer.

Examples include:

- add or remove a system component;
- connect or disconnect components;
- change a configuration value;
- edit code, prompts, JSON/schema, SQL, or configuration;
- run an inspection/test action;
- submit a structured decision;
- undo or reset work.

Pure visual selection is intentionally excluded from evidence. Selecting a node or edge does not prove technical understanding and therefore is not emitted as semantic candidate evidence.

## Product journey

BuzzPrep currently supports two browser journeys that use the same backend interview system.

### Public demo journey

The public demo does not require authentication.

```text
Landing page
    ↓
Public demo setup
    ↓
Choose supplied candidate
    ↓
Readiness check
    ↓
Adaptive interview + workspace
    ↓
Evidence-based results
```

The organizer can also call the public API directly without using the frontend or workspace.

### Authenticated journey

When Supabase Auth is configured, the product adds persistent user-owned history.

```text
Landing page
    ↓
Magic Link authentication
    ↓
Dashboard / history
    ↓
Candidate setup
    ↓
Readiness check
    ↓
Adaptive interview
    ↓
Persisted results
    ↓
Owned history / resume
```

The backend verifies the Supabase bearer token and uses the verified token subject as the owner. The frontend does not provide a trusted raw user id.

## Curriculum grounding

The supplied 31-day curriculum is deterministic application data, not a vector database and not model-generated content.

BuzzPrep loads the curriculum and uses it as the source of truth for:

- day and module coverage;
- topic names;
- objectives;
- tools;
- suitable interaction types.

The candidate profiler and planner normalize the supplied candidate record and use signals such as:

- job role;
- years of experience;
- education;
- passed missions;
- failed missions;
- skipped missions;
- attempt counts;
- first-try completion signals.

The planner then produces a deterministic interview plan before the LLM is responsible for conversational wording.

Failed and skipped material is not silently treated as completed knowledge. The planner can use it intentionally as diagnostic, gap-check, or exploratory material.

## Adaptive interview loop

The implemented high-level loop is:

```text
Candidate profile + curriculum
            ↓
Deterministic interview plan
            ↓
Retrieve relevant prior evidence (optional Breeth)
            ↓
Generate curriculum-grounded question
            ↓
Candidate answers + performs workspace actions
            ↓
Evaluate answer + workspace evidence
            ↓
Choose follow-up / deepen / transition
            ↓
Python checks hard completion invariant
            ↓
Continue OR generate structured final feedback
```

The adaptive loop is implemented with LangGraph. Model outputs are validated against Pydantic schemas rather than parsed from unrestricted prose.

## Hard completion rules

The LLM cannot decide that an interview is complete by itself.

Python owns the invariant:

```text
question_count >= 8
AND
number of distinct covered curriculum days >= 4
```

This guarantees the hackathon's minimum coverage even when the adaptive interviewer wants to stay longer on a strong or weak topic.

## Reusable interaction model

BuzzPrep uses nine logical interaction types from the deterministic planner:

- `system_canvas`
- `configuration_lab`
- `data_workbench`
- `prompt_schema_editor`
- `code_config_repair`
- `logs_metrics_explorer`
- `test_evaluation_runner`
- `incident_simulator`
- `architecture_critique`

The frontend maps these into four reusable renderer families instead of building 31 unrelated interfaces.

### System canvas

React Flow is used for component and architecture manipulation.

Typical uses:

- RAG/retrieval flow;
- agent/tool architecture;
- deployment/system design;
- production architecture critique.

### Configuration lab

The candidate chooses or changes tools, modes, parameters, policies, and settings.

Typical uses:

- model/provider choices;
- vector-store decisions;
- timeout/retry configuration;
- deployment and security settings.

### Editor challenge

Monaco-backed editor modes support code, prompt text, JSON/schema, SQL, and configuration.

Typical uses:

- prompt/schema design;
- code or config repair;
- structured output definitions;
- query fixes.

### Inspection challenge

A shared inspection family represents data, logs, metrics, tests, incidents, and architecture critique.

Typical uses:

- data/retrieval inspection;
- production debugging;
- evaluation results;
- failure/constraint analysis.

The curriculum-wide examples in [`curriculum-interactions.md`](curriculum-interactions.md) show how all 31 days can map into these reusable primitives.

## Workspace evidence model

The workspace is curriculum-agnostic and serializable.

Important state includes:

- nodes and edges;
- configuration values;
- editor content;
- submissions;
- structured mutation events;
- active challenge id;
- reset baseline.

Candidate mutation events include:

```text
add
remove
connect
disconnect
configure
edit
run
submit
undo
reset
```

The backend receives both a snapshot and recent events. The interview engine can summarize those actions into compact facts and include them in answer evaluation and question generation.

The system protects against invented workspace references: generated questions may only claim to use a workspace fact that was actually supplied.

## Evidence-based evaluation

BuzzPrep is designed to evaluate more than keyword overlap.

The interview engine can reason about:

- conceptual correctness;
- technical reasoning;
- trade-offs;
- application of curriculum concepts;
- whether the explanation matches the candidate's workspace actions;
- debugging and failure-handling decisions;
- demonstrated strengths or misconceptions over multiple turns.

Final feedback uses the required shape:

```json
{
  "summary": "...",
  "strengths": [],
  "gaps": [],
  "next": []
}
```

The browser progress UI shows safe operational progress such as questions asked and curriculum days covered. Hidden scores, rubrics, future questions, and answer keys are not exposed.

## State, memory, and ownership

BuzzPrep uses different storage mechanisms for different responsibilities.

### SQL is canonical state

SQLAlchemy persists:

- candidate data;
- interview ownership;
- ordered conversation turns;
- question and turn counts;
- covered curriculum days;
- current day/topic/challenge;
- workspace snapshot;
- structured evaluation state;
- completion state;
- integrity telemetry;
- timestamps and final status.

SQLite is used for local development by default. Production can use PostgreSQL, including Supabase Postgres.

### Breeth is optional semantic memory

Breeth sits behind a small `MemoryService` interface. BuzzPrep writes concise, high-signal observations rather than treating the memory service as the source of truth.

Memory is scoped by:

- candidate id; and
- interview session id.

Retrieval failure, timeout, or unavailability does not terminate the interview. The deterministic SQL session state remains sufficient to continue.

### Authenticated history is additive

A valid Supabase bearer token lets the backend associate a session with the verified user and expose owned history through:

```text
GET /api/me/interviews
GET /api/me/interviews/{sessionId}
```

The required public interview endpoint remains unauthenticated.

## LLM boundary and provider fallback

The interview graph calls one provider-neutral structured generation interface.

The configured production chain can use:

1. Gemini;
2. GroqCloud;
3. OpenRouter.

Fallback is intended for provider availability, transient failure, or invalid structured generation. Rejected/invalid client requests are not hidden by trying another provider.

A deterministic fake provider exists for tests and explicit offline/local demos. Normal runtime never silently chooses fake AI.

## Voice interaction

The active interview UI now supports optional browser voice controls.

### Dictation

If the browser exposes `SpeechRecognition` or `webkitSpeechRecognition`, the candidate can dictate into the normal answer composer. Dictation is always optional; the candidate can edit the resulting text before submission.

BuzzPrep does not upload or persist microphone audio in its backend. Recognition behavior, processing location, permissions, and browser support depend on the browser/OS implementation.

### Interviewer read-aloud

The candidate can enable browser Speech Synthesis for interviewer messages. BuzzPrep prefers a locale-compatible natural/neural voice when one is exposed by the browser and falls back to an available voice.

No audio recording is required for either feature.

## Integrity telemetry and privacy boundary

BuzzPrep records a small set of transparent browser-state events during active prep:

- tab hidden / visible;
- window blur / focus;
- fullscreen enter / exit;
- reconnect.

These events are kept separate from answer and workspace evidence. They are not treated as proof that an answer is right or wrong.

The product does **not** add passive microphone recording, camera recording, or screen-video capture.

## Desktop workspace requirement

The full technical workspace is intentionally desktop-oriented.

An active interview requires:

```text
(min-width: 960px) and (pointer: fine)
```

This avoids presenting a broken compressed engineering canvas on phones or touch-only devices. Landing, auth, dashboard, history, and results remain available in responsive layouts.

## Relationship to the hackathon requirements

BuzzPrep preserves the organizer's required behavior:

- public `POST /api/interview`;
- state maintained by supplied `sessionId`;
- conversational multi-turn interview;
- at least 8 questions;
- at least 4 curriculum days;
- response-dependent follow-ups;
- structured final feedback with `summary`, `strengths`, `gaps`, and `next`.

The following are product extensions, not evaluator requirements:

- interactive workspace evidence;
- Supabase Magic Link authentication;
- owned interview history;
- readiness flow;
- integrity telemetry;
- browser voice input and read-aloud.

## Current product boundaries

BuzzPrep is a hackathon product, not a remote-proctoring platform or a general-purpose IDE.

Important boundaries:

- the workspace is a structured simulation, not arbitrary code execution;
- browser speech support varies and typing is always the fallback;
- Breeth is optional and non-authoritative;
- the active workspace is desktop-oriented;
- the public evaluator does not need authentication or workspace payloads;
- deterministic curriculum/session rules remain outside the LLM.

These boundaries keep the product focused on the interview objective: **turning a candidate's learning history, reasoning, and technical actions into an adaptive interview with defensible evidence.**
