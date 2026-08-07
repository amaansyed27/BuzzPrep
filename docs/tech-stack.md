# BuzzPrep Tech Stack

## Decision

BuzzPrep will use a **React + FastAPI** architecture with a JSON-driven interactive challenge engine.

The frontend provides the adaptive technical workspace. The backend owns interview state, curriculum selection, AI orchestration, scoring, and the required `POST /api/interview` endpoint.

## Frontend

- **React + Vite + TypeScript** — fast development and a lightweight interactive frontend.
- **Tailwind CSS + shadcn/ui** — reusable interface primitives without building a design system from scratch.
- **@xyflow/react (React Flow)** — node-based system and architecture challenges such as RAG, agents, MCP, deployment, and data flows.
- **Monaco Editor** — code, prompt, JSON, schema, SQL, configuration, and debugging exercises.
- **Zustand** — local workspace state for canvas nodes, active challenge state, selections, and temporary UI state.

The workspace should use a renderer registry rather than one universal canvas. Challenge definitions can select an interaction type such as:

- `node_canvas`
- `code_editor`
- `prompt_editor`
- `config_lab`
- `data_workbench`
- `log_viewer`
- `incident_simulator`
- `architecture_review`

## Backend

- **Python 3.12**
- **FastAPI** — API server and required `POST /api/interview` endpoint.
- **Pydantic** — strict request, response, challenge, evaluator, and feedback schemas.
- **LangGraph** — explicit interview state machine and adaptive interview orchestration.
- **SQLModel / SQLAlchemy** — structured session-state persistence.
- **SQLite by default** for local development, with `DATABASE_URL` allowing PostgreSQL for deployment if required.

## LLM Layer

Use a small provider adapter rather than coupling the project to one model vendor.

The model is responsible for:

1. selecting an appropriate curriculum objective and scenario;
2. generating the next interviewer turn;
3. evaluating the candidate's explanation and workspace actions against a rubric;
4. adapting difficulty and follow-ups;
5. producing final structured feedback.

All machine-facing outputs should use validated Pydantic schemas. The LLM should not directly control the UI or mutate session state without validation.

## Breeth Memory

**Breeth will be used as the semantic memory layer, not as the sole session database.**

For each interview, BuzzPrep can use the `sessionId` as a Breeth memory group and the candidate ID as the end-user identifier.

High-signal observations can be stored after each turn, for example:

- concepts the candidate demonstrated correctly;
- misconceptions or gaps;
- technical choices made in the workspace;
- reasons given for those choices;
- trade-offs the candidate recognized;
- previous failures and corrections;
- communication and reasoning patterns.

Before generating a follow-up, the interviewer can retrieve the most relevant memories for the active topic. This gives the agent semantic recall across a long interview without repeatedly sending the complete transcript to the model.

Breeth should **not** be the canonical store for exact deterministic state such as:

- question number;
- required curriculum-day coverage;
- active scenario;
- current workspace graph;
- scoring totals;
- `done` status.

Those values remain in the structured session store.

The application should integrate Breeth through its Python SDK/REST API. Breeth's MCP server is additionally useful during development for coding assistants to remember project decisions, but the production interview runtime does not need to depend on MCP for basic memory operations.

## Interview State Machine

A session can maintain state similar to:

```text
Candidate Profile
      ↓
Curriculum Planner
      ↓
Scenario / Question Generator
      ↓
Candidate response + workspace action
      ↓
Evaluator
      ↓
Memory update (Breeth)
      ↓
Coverage + difficulty update
      ↓
Follow-up / new challenge
      ↓
Final feedback
```

Suggested LangGraph responsibilities:

- `plan_interview`
- `generate_turn`
- `evaluate_turn`
- `update_memory`
- `adapt_interview`
- `finalize_feedback`

## Challenge Schema

Interactive tasks should be generated as validated JSON rather than hard-coded screens.

Example shape:

```json
{
  "curriculumDays": [8, 10],
  "interactionType": "node_canvas",
  "scenario": "Design retrieval for structured and unstructured healthcare data.",
  "availableComponents": [],
  "initialWorkspace": {},
  "constraints": [],
  "rubric": [],
  "difficulty": 2
}
```

The frontend maps `interactionType` to the appropriate renderer. This is what allows BuzzPrep to cover the whole curriculum rather than making every exercise a node graph.

## Required API Compatibility

The public contract remains:

```text
POST /api/interview
```

The first request contains `sessionId` and `candidate`. Later requests contain `sessionId` and `message`.

For BuzzPrep's UI, workspace actions can be serialized into the `message` payload alongside the candidate's explanation so the required endpoint remains compatible with the hackathon specification. Plain-text messages from an evaluator must continue to work normally.

## Deployment

Preferred hackathon deployment:

- Build the Vite frontend to static assets.
- Serve the frontend and FastAPI application from the same deployment/container.
- Keep `/api/interview` on the same origin.
- Dockerize the complete application.
- Deploy the container to a simple container host.

This avoids unnecessary frontend/backend deployment coordination during the hackathon.

## Deliberate Non-Choices

- **No separate vector database for the curriculum.** The supplied curriculum has only 31 days and should be loaded directly from JSON.
- **No CrewAI unless a later requirement genuinely needs it.** LangGraph gives more predictable interview control.
- **No authentication.** Explicitly out of scope.
- **No long-term user account system.** Explicitly out of scope.
- **No voice pipeline for the MVP.** Voice is explicitly not required and would distract from the interactive interview differentiator.

## Final Stack Summary

| Layer | Choice |
|---|---|
| Frontend | React + Vite + TypeScript |
| Styling | Tailwind CSS + shadcn/ui |
| Interactive graphs | React Flow / `@xyflow/react` |
| Editors | Monaco Editor |
| Frontend state | Zustand |
| Backend | FastAPI + Python 3.12 |
| Validation | Pydantic |
| Agent orchestration | LangGraph |
| Structured state | SQLModel/SQLAlchemy + SQLite/PostgreSQL |
| Agent memory | Breeth |
| LLM | Provider adapter with structured outputs |
| Packaging | Docker |
