# Curriculum-Wide Interactive Interview Map

BuzzPrep can ground interview challenges in any part of the supplied **31-day AI Cohort** without building 31 unrelated interfaces.

This document is a curriculum-to-interaction reference. The examples are **not fixed questions** and are not a required sequence for every candidate. The deterministic planner selects a subset of curriculum days from the candidate profile, and the adaptive interviewer decides how deeply to probe each selected area.

## Current implementation model

The backend planner exposes nine logical interaction types:

```text
system_canvas
configuration_lab
data_workbench
prompt_schema_editor
code_config_repair
logs_metrics_explorer
test_evaluation_runner
incident_simulator
architecture_critique
```

The frontend maps them into four reusable renderer families:

| Logical interaction type | Current renderer family |
|---|---|
| `system_canvas` | System canvas |
| `configuration_lab` | Configuration lab |
| `prompt_schema_editor` | Editor challenge |
| `code_config_repair` | Editor challenge |
| `data_workbench` | Inspection challenge |
| `logs_metrics_explorer` | Inspection challenge |
| `test_evaluation_runner` | Inspection challenge |
| `incident_simulator` | Inspection challenge |
| `architecture_critique` | Inspection challenge |

The editor family supports code, prompt, JSON/schema, SQL, and configuration modes. The inspection family is reused for data, logs, metrics, tests, incidents, and architecture critique.

Candidate mutations are serialized through the common workspace event model. Visual selection alone is UI state and is not treated as evidence.

## Module 1 — Environment & Tooling

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 1 | VS Code & Python Environment Setup | `code_config_repair`, `incident_simulator` | Diagnose a broken Python environment, interpreter mismatch, or `.venv` setup and explain how to verify the fix. |
| 2 | Local LLM & AI Coding Assistant Setup | `configuration_lab`, `incident_simulator` | Configure a local model/coding workflow and recover from a failed local-model connection. |
| 3 | First AI Project, React Frontend & GitHub | `system_canvas`, `code_config_repair` | Connect React/Vite, FastAPI, a model service, and the Git workflow; repair a broken frontend/backend path. |

## Module 2 — Data Foundations

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 4 | Reading & Processing Structured Data | `data_workbench`, `code_config_repair` | Clean messy tabular data, decide what belongs in SQLite, and repair or choose a query/transformation path. |
| 5 | Reading & Processing Unstructured Data | `system_canvas`, `data_workbench` | Route PDF, DOCX, scanned, and web sources through appropriate extraction and normalization steps. |
| 6 | Building the Knowledge Base | `data_workbench`, `configuration_lab` | Choose chunk boundaries and metadata, reject poor records, and construct retrieval-ready knowledge-base entries. |

## Module 3 — Embeddings & Vector Search

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 7 | Embeddings Explained | `data_workbench`, `test_evaluation_runner` | Compare semantic relationships, inspect similarity behavior, and diagnose poor grouping or embedding choices. |
| 8 | Vector Databases Overview | `configuration_lab`, `architecture_critique` | Choose between local/managed vector-store options for a scenario and defend scale, filtering, and operational trade-offs. |
| 9 | Building & Populating the Vector Database | `data_workbench`, `code_config_repair` | Detect missing IDs/metadata/indexing mistakes, configure filtering, and validate search results. |
| 10 | The Retrieval & Matching Engine | `system_canvas`, `test_evaluation_runner` | Build structured/vector/hybrid routing, merge results, and repair poor retrieval decisions. |

## Module 4 — LLM Core, Prompting & Fine-Tuning

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 11 | RAG End-to-End & LLM API Basics | `system_canvas`, `incident_simulator` | Assemble retrieval, context, prompt, and LLM components, then diagnose an unsupported or ungrounded answer. |
| 12 | Prompt Engineering Fundamentals | `prompt_schema_editor`, `test_evaluation_runner` | Build and compare prompt variants against fixed cases and justify the production choice. |
| 13 | Advanced Prompting: Function Calling & Structured Outputs | `prompt_schema_editor`, `logs_metrics_explorer` | Define tool/output schemas, inspect invalid structured output, and repair tool-call behavior. |
| 14 | Fine-Tuning: Concepts & When to Use It | `configuration_lab`, `architecture_critique` | Decide whether a failure needs prompting, RAG, or fine-tuning and separate valid training/test data. |
| 15 | Fine-Tuning: Hands-On with LoRA & QLoRA | `configuration_lab`, `test_evaluation_runner` | Configure a plausible LoRA/QLoRA run, compare unseen-test behavior, and decide whether the result is meaningful. |

## Module 5 — Chatbot Application Build

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 16 | Chatbot Backend & API Integration | `code_config_repair`, `system_canvas` | Repair a FastAPI request flow containing retrieval, tool-calling, session, or history mistakes and verify example requests. |
| 17 | Chatbot Frontend Development | `code_config_repair`, `incident_simulator` | Fix frontend/backend state flow and diagnose conversation-history or new-session bugs. |
| 18 | Full-Stack Integration & Streaming Responses | `system_canvas`, `logs_metrics_explorer` | Place streaming components correctly, inspect an interrupted stream, and choose loading/failure handling. |
| 19 | Response Formatting & Rich Outputs | `prompt_schema_editor`, `test_evaluation_runner` | Turn raw model/retrieval output into validated rich output with citations/structure while catching malformed data. |
| 20 | Conversation Memory & Context Management | `configuration_lab`, `architecture_critique` | Manage a conversation that exceeds its token budget and defend what to retain, summarize, or externalize. |

## Module 6 — Agentic AI & MCP

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 21 | Agentic Frameworks: LangChain Agents & Tool Use | `system_canvas`, `logs_metrics_explorer` | Choose agent tools, inspect a tool-selection trace, and correct a bad decision or overlapping tool set. |
| 22 | Multi-Agent Orchestration | `system_canvas`, `architecture_critique` | Construct a router/delegation flow, repair a bad hand-off, and justify single-agent vs multi-agent architecture. |
| 23 | Model Context Protocol (MCP) | `system_canvas`, `code_config_repair` | Connect MCP client/server/tools and diagnose a broken tool contract. |
| 24 | Agentic Chatbot Integration | `system_canvas`, `incident_simulator` | Assemble retrieval, memory, agents, MCP, retries, and timeouts, then react to tool or orchestration failures. |

## Module 7 — Evaluation, Security & Deployment

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 25 | Chatbot Evaluation & Testing | `test_evaluation_runner`, `data_workbench` | Classify evaluation cases, inspect grounding/retrieval/consistency failures, and prioritize fixes. |
| 26 | Performance Optimization & Cost Management | `logs_metrics_explorer`, `configuration_lab` | Change prompt/retrieval/cache choices against latency/token/cost signals and explain the quality trade-off. |
| 27 | Security, Privacy & Guardrails | `architecture_critique`, `incident_simulator` | Find unsafe inputs, data exposure, prompt injection, or missing controls and make the smallest justified correction. |
| 28 | Docker & Kubernetes Deployment | `system_canvas`, `code_config_repair` | Configure service/container relationships, environment, exposure, and health checks; diagnose an unhealthy deployment. |

## Module 8 — Production & Capstone

| Day | Curriculum topic | Suitable interaction | Example interview challenge |
|---|---|---|---|
| 29 | Monitoring, Logging & Observability | `logs_metrics_explorer`, `incident_simulator` | Correlate logs, latency/error metrics, and traces to diagnose a production regression. |
| 30 | Production Readiness & Final Testing | `test_evaluation_runner`, `architecture_critique` | Use an end-to-end readiness board to find integration failures and prioritize fixes/documentation. |
| 31 | Capstone Project & Final Demo | `system_canvas`, `architecture_critique` | Build or critique an end-to-end production AI architecture and defend retrieval, agent, memory, API, deployment, evaluation, and observability trade-offs. |

## How the map becomes an interview

The candidate does **not** progress through the 31 rows in order.

The runtime pattern is closer to:

```text
Candidate profile
      ↓
Deterministic curriculum plan
      ↓
Interviewer presents selected day/scenario
      ↓
Frontend renders suitable interaction mode(s)
      ↓
Candidate performs action(s) + explains decision
      ↓
Backend evaluates answer + supplied workspace evidence
      ↓
Adaptive decision: follow up / deepen / transition
      ↓
Python checks 8-question / 4-day completion invariant
      ↓
Continue or finish with structured feedback
```

The deterministic planner decides **what is reasonable to assess**. The LLM decides **how to phrase and adapt the conversation** within validated structured outputs. The frontend decides **how to render the practical interaction**. These responsibilities remain separate.

## Personalization examples

The same curriculum day can be presented differently depending on the candidate.

### Strong first-try signal

A candidate with strong demonstrated progress may receive:

- a harder constraint;
- an architecture trade-off;
- a failure case;
- a comparison between plausible solutions.

### Repeated-attempt/weaker signal

A candidate who needed several attempts may receive:

- a more foundational configuration or diagnosis;
- a smaller repair task;
- a prerequisite probe before moving deeper.

### Failed or skipped material

Failed/skipped topics are not represented as completed learning. If selected, they are intentionally framed as diagnostic, gap-check, or exploratory areas according to the planner.

## Evidence examples

### System canvas

Useful evidence:

```text
add node
remove node
connect nodes
disconnect edge
reset / undo
```

Possible follow-up:

> You inserted a validation gate before the model call. What failure are you containing there, and what would change under higher throughput?

### Configuration lab

Useful evidence:

```text
change provider/mode
change timeout
change retry behavior
change top-k or policy
submit configuration decision
```

Possible follow-up:

> You enabled retries and reduced the timeout. Which failures are safe to retry, and how do you prevent duplicate side effects?

### Editor challenge

Useful evidence:

```text
edit code
edit prompt
edit JSON/schema
edit SQL
edit config
run / submit
```

Possible follow-up:

> Your schema now makes `evidence` required. What happens when the upstream model cannot produce valid evidence, and where should that failure be handled?

### Inspection challenge

Useful evidence:

```text
inspect/choose evidence
run evaluation
submit diagnosis
react to incident constraint
```

Possible follow-up:

> You prioritized the latency spike over the small quality regression. Which metric or trace would you inspect next to confirm that decision?

## Constraint injection

The current challenge registry can attach reusable scenario constraints such as:

- tighter latency budget;
- stale dependency results;
- 10× traffic increase;
- intermittent downstream timeout;
- sensitive data appearing in a request.

A constraint is useful only when it changes the reasoning expected from the candidate. It should not be added merely as visual decoration.

## Relationship to final feedback

Workspace actions do not automatically become strengths or gaps. They are evidence supplied to structured per-turn evaluation.

Final feedback should reflect patterns across the interview, for example:

- repeated sound trade-off reasoning;
- consistent grounding in observable evidence;
- a recurring misconception;
- weak failure handling;
- improved reasoning after targeted follow-up.

The required final schema remains:

```text
summary
strengths[]
gaps[]
next[]
```

## Important product boundary

The interactive map extends the conversational interview; it does not replace it.

The organizer can use BuzzPrep with only:

```text
POST /api/interview
sessionId + candidate/message
```

Workspace state is optional additive context. This keeps the external contract simple while allowing the browser product to demonstrate technical reasoning through actions.
