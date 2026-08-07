# BuzzPrep Product Concept

## Core Idea

BuzzPrep is an **interactive AI technical interview simulator** for the complete 31-day AI Cohort.

A normal AI interviewer mainly asks questions in a chat or meeting-style interface. BuzzPrep adds a second layer: the candidate is placed inside an adaptive technical workspace where they must make decisions, manipulate systems, diagnose problems, and respond to changing scenarios while the interview is happening.

The experience is inspired by scenario-based learning such as Duolingo's interactive exercises, where the learner demonstrates knowledge by acting inside a simulated situation rather than only answering isolated questions.

RAG is only one example. The same product should be able to interview the candidate across every area represented in the supplied curriculum: environment setup, data processing, embeddings, vector search, RAG, prompting, fine-tuning, APIs, frontend integration, streaming, memory, agents, MCP, evaluation, optimization, security, deployment, observability, production readiness, and capstone system design.

## Two Synchronized Interview Channels

Every interview combines:

1. **Conversation** — the AI interviewer asks questions, listens to explanations, challenges assumptions, introduces constraints, and asks follow-ups.
2. **Interactive workspace** — the candidate performs technical actions appropriate to the current topic.

Both become part of the interview context.

The interviewer should therefore reason about:

- what the candidate said;
- what they selected, connected, configured, changed, or removed;
- whether their actions satisfy the scenario;
- whether their explanation matches what they actually built;
- how they react to failures or changing requirements;
- whether they can explain the trade-offs behind their decisions.

## The Workspace Is Adaptive, Not One Fixed Canvas

BuzzPrep should not force every curriculum topic into the same drag-and-drop graph.

Instead, interview challenges are rendered using a small set of reusable interaction primitives.

### 1. System Builder

Drag, connect, reorder, or remove technical components.

Useful for:

- full-stack architecture;
- knowledge-base pipelines;
- RAG;
- retrieval routing;
- agents;
- MCP;
- deployment;
- production architecture.

### 2. Configuration Lab

Choose tools, models, parameters, schemas, metadata, environment settings, or deployment options.

Useful for:

- local LLM setup;
- vector databases;
- embedding models;
- fine-tuning;
- function calling;
- API configuration;
- Docker/Kubernetes.

### 3. Data Workbench

Inspect, transform, classify, route, chunk, filter, or validate sample data.

Useful for:

- Pandas/SQL tasks;
- structured and unstructured data;
- chunking;
- metadata design;
- vector indexing;
- retrieval evaluation.

### 4. Prompt / Schema Builder

Construct or modify prompts, examples, constraints, tool schemas, Pydantic structures, or response formats and then test them.

Useful for:

- prompt engineering;
- structured outputs;
- function calling;
- grounded RAG prompting;
- response formatting.

### 5. Debugging Console

Show a partially broken system, logs, errors, traces, bad outputs, or incorrect routing and ask the candidate to diagnose and repair it.

Useful for:

- FastAPI/backend issues;
- streaming failures;
- conversation memory;
- agent tool selection;
- MCP failures;
- production testing.

### 6. Evaluation Bench

Present test cases, outputs, retrieval results, latency, token usage, or quality metrics. The candidate decides what is wrong and what to improve.

Useful for:

- embedding quality;
- retrieval evaluation;
- prompt comparisons;
- fine-tuning comparisons;
- chatbot evaluation;
- performance optimization.

### 7. Incident / Constraint Simulator

Change requirements during the interview and require the candidate to react.

Examples:

- a dataset doubles in size;
- a retrieval system starts returning irrelevant results;
- a tool fails intermittently;
- token usage becomes too expensive;
- sensitive data appears in the pipeline;
- latency increases;
- a deployment fails a health check;
- monitoring reveals a spike in errors.

This interaction style is useful across the whole curriculum and makes the interview behave more like an engineering conversation than a quiz.

## Example: RAG Is One Scenario

A RAG challenge might present:

```text
Data Sources
    ↓
Processing / Chunking
    ↓
Embedding Model
    ↓
Vector Store
    ↓
Retriever / Router
    ↓
LLM
    ↓
Answer
```

The candidate could choose among curriculum-aligned components such as Sentence Transformers, ChromaDB, Pinecone, SQLite, semantic retrieval, structured retrieval, hybrid retrieval, or an LLM provider.

There should not be one predetermined perfect graph. Multiple solutions may be valid depending on the scenario. The useful interview signal is whether the candidate makes a coherent decision and can defend it.

But this is only one challenge type. A Day 12 prompt interview should look different from a Day 27 security interview or a Day 29 observability interview.

## Curriculum-Wide Interview Examples

BuzzPrep should be able to generate interactive challenges for all eight curriculum modules:

### Module 1 — Environment & Tooling

Set up or repair a development environment, connect a local model, wire a simple React/FastAPI/Ollama application, or identify why a workflow does not run.

### Module 2 — Data Foundations

Choose the correct processing path for CSV, SQL, PDF, DOCX, scanned, or web data; clean it; build retrieval-friendly chunks; attach useful metadata; validate the resulting knowledge base.

### Module 3 — Embeddings & Vector Search

Compare embedding choices, interpret similarity behavior, configure a vector store, populate an index, test metadata filtering, and build structured/vector/hybrid retrieval flows.

### Module 4 — LLM Core, Prompting & Fine-Tuning

Build grounded RAG prompts, compare prompt strategies, construct function schemas, validate structured outputs, decide when fine-tuning is justified, and compare base vs fine-tuned behavior.

### Module 5 — Chatbot Application Build

Repair or assemble APIs, frontend/backend integration, streaming, rich outputs, citations, session history, summarization, and token-aware conversation memory.

### Module 6 — Agentic AI & MCP

Choose tools, inspect agent decisions, build routing between specialist agents, expose MCP tools, connect MCP clients, and recover from tool or orchestration failures.

### Module 7 — Evaluation, Security & Deployment

Create or interpret evaluation cases, improve latency/token cost, identify security weaknesses, add guardrails, containerize services, configure Kubernetes resources, and diagnose deployment problems.

### Module 8 — Production & Capstone

Interpret logs/metrics, design observability, perform production-readiness checks, diagnose end-to-end failures, and defend a complete production architecture.

See [`curriculum-interactions.md`](curriculum-interactions.md) for one concrete interactive interview example for every curriculum day.

## Adaptive Interviewing

Workspace actions should influence the interviewer immediately.

Examples:

- candidate chooses ChromaDB → ask why local storage fits the scenario;
- candidate configures a weak prompt → show a failure case and ask them to improve it;
- candidate gives an agent too many overlapping tools → present incorrect tool selection;
- candidate forgets retries around MCP calls → inject a transient failure;
- candidate ignores token limits → expand conversation history until context becomes a problem;
- candidate deploys without a health check → simulate an unhealthy container;
- candidate notices an error spike in metrics → ask what logs or traces they would inspect next.

A strong answer should not simply end the task. It can trigger a harder constraint or require the candidate to explain why an alternative would be worse.

## Personalization

The supplied candidate profile should determine which curriculum areas are selected and how difficult each challenge becomes.

Useful signals include:

- job role;
- years of experience;
- completed missions;
- failed missions;
- skipped missions;
- number of attempts;
- first-try completion signals.

The goal is not to punish skipped or failed topics automatically. These signals help the interviewer decide what knowledge is reasonable to test, what deserves reinforcement, and where a deeper probe may reveal genuine understanding.

An experienced DevOps engineer may receive deeper deployment, monitoring, and failure-recovery scenarios. A candidate who struggled with embeddings or vector databases may receive a more foundational retrieval challenge. An AI engineer who completed most missions on the first attempt may be pushed toward architecture trade-offs and failure cases.

## Interview Orchestration

A BuzzPrep interview can follow this loop:

```text
Candidate profile + curriculum
            ↓
Select interview areas and difficulty
            ↓
Present scenario
            ↓
Candidate talks + interacts
            ↓
Evaluate answer + workspace state
            ↓
Ask follow-up OR introduce constraint
            ↓
Candidate modifies/explains
            ↓
Track evidence and curriculum coverage
            ↓
Next challenge
            ↓
Structured final feedback
```

The challenge engine therefore needs to decide not only **what question to ask**, but also **what environment to show** and **what action the candidate should perform**.

## Assessment Model

BuzzPrep should assess more than keyword matching.

Useful dimensions include:

- conceptual understanding;
- technical correctness;
- architecture coherence;
- reasoning and trade-offs;
- ability to apply concepts;
- debugging ability;
- response to changing requirements;
- communication quality;
- consistency between explanation and workspace actions.

The final feedback can then summarize strengths, gaps, and next steps using evidence collected throughout the interview.

## Relationship to Hackathon Requirements

The interactive experience does not replace the required conversational interview.

BuzzPrep must still:

- conduct a multi-turn interview;
- ask at least 8 questions across at least 4 curriculum days;
- generate response-dependent follow-ups;
- preserve context using the provided `sessionId`;
- return the required structured feedback;
- expose `POST /api/interview`.

The interactive workspace is an additional source of interview evidence and differentiation.

The external API must remain usable even when no visual frontend is present. Interactive workspace actions should therefore be represented as machine-readable interview context without making the required conversational contract dependent on a particular UI.

## Current Direction

The product concept is intentionally architecture-neutral at this stage.

The next design step is to decide:

- the interview challenge schema;
- how each interaction primitive is represented in frontend state;
- how candidate actions are converted into machine-readable events;
- how the interviewer evaluates both conversation and workspace state;
- how the full curriculum maps into reusable challenge templates;
- how scoring and final feedback are derived;
- the frontend/backend architecture.
