# BuzzPrep Product Concept

## Core Idea

BuzzPrep is an **interactive AI technical interview simulator**.

A normal AI interviewer mainly asks questions in a chat or meeting-style interface. BuzzPrep adds a second layer: the candidate is given a technical environment in which they must make decisions, assemble systems, and respond to changing scenarios while the interview is happening.

The experience is inspired by scenario-based learning such as Duolingo's interactive exercises, where the learner demonstrates knowledge by acting inside a simulated situation rather than only answering isolated questions.

## Interview Experience

The interview has two synchronized channels:

1. **Conversation** — the AI interviewer asks questions, listens to explanations, challenges assumptions, and asks follow-ups.
2. **Interactive workspace** — the candidate performs technical tasks using visual components, configuration choices, and system-building actions.

Both become part of the interview context.

The interviewer should therefore be able to reason about:

- what the candidate said;
- what components they selected;
- how they connected or configured them;
- whether they changed their approach after feedback;
- whether their architecture satisfies the scenario;
- how well they can explain the trade-offs behind their choices.

## Example: RAG Challenge

The interviewer could present a scenario such as:

> Build a retrieval system for a knowledge base that contains both structured and unstructured information. Explain your decisions as you build it.

Instead of asking the candidate to only describe a RAG architecture, BuzzPrep provides a Scratch-like technical canvas.

Possible component groups could include:

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

The candidate might be offered several valid choices drawn from the cohort, for example:

- embedding models such as Sentence Transformers or an API-based embedding model;
- ChromaDB or Pinecone for vector storage;
- SQLite for structured information;
- semantic, structured, or hybrid retrieval;
- different prompting or generation components.

There should not be one predetermined perfect graph. Multiple solutions may be valid depending on the scenario. The important signal is whether the candidate selects a coherent solution and can defend it.

## Adaptive Interviewing

Canvas actions should influence the interview immediately.

Examples:

- The candidate chooses ChromaDB → ask why a local vector database is appropriate here.
- The candidate combines SQLite and vector search → ask how query routing or result merging should work.
- The candidate omits metadata → introduce a filtering requirement.
- The candidate builds a strong baseline quickly → add latency, cost, security, or scale constraints.
- The candidate makes a questionable choice → ask them to diagnose the consequences rather than simply marking it wrong.

This keeps the interview conversational while making it practical.

## Scenario Changes

The interviewer can introduce new constraints during the exercise, similar to a real system-design interview.

Examples:

- "The dataset has doubled in size."
- "Users are receiving irrelevant retrieval results."
- "The system now contains private healthcare information."
- "The application must run locally."
- "Latency has become a production problem."
- "One of your agent tools is failing intermittently."

The candidate then modifies the canvas and explains the change.

## Beyond RAG

The same interaction model can be reused across the supplied 31-day curriculum.

Potential interactive interview modes include:

### Prompt Engineering

Choose or modify prompt components, examples, constraints, and structured-output requirements, then explain why one approach is preferable.

### Agentic AI

Connect agents, tools, routers, and decision paths. Diagnose incorrect delegation or tool selection.

### MCP

Select tools/resources exposed by an MCP server, connect a client, and reason about the interface between them.

### Security

Identify vulnerable parts of a pipeline and add validation, access control, or prompt-injection protections.

### Deployment

Arrange application services, containers, health checks, environment configuration, and deployment components.

### Observability

Add logs, metrics, monitoring, and failure signals to an existing architecture.

### Production Debugging

Given an existing visual system with a problem, locate the likely failure and modify the design.

## Personalization

The supplied candidate profile should determine what kind of interview is generated.

Signals include:

- job role;
- years of experience;
- completed missions;
- failed missions;
- skipped missions;
- number of attempts;
- first-try completion signals.

The interview can use these signals to select appropriate curriculum areas and difficulty.

For example, an experienced DevOps engineer may receive deeper deployment and observability challenges, while a candidate who struggled with vector databases may receive a more foundational retrieval scenario with targeted follow-ups.

The goal is not to punish skipped or failed topics automatically. These signals help the interviewer decide what knowledge is reasonable to test and where probing could reveal genuine understanding.

## Assessment Model

BuzzPrep should eventually assess more than whether an answer contains certain keywords.

Useful dimensions include:

- conceptual understanding;
- architecture correctness;
- reasoning and trade-offs;
- ability to apply concepts;
- debugging ability;
- response to changing requirements;
- communication quality;
- consistency between spoken explanation and canvas actions.

The final required feedback can then summarize strengths, gaps, and next steps using evidence collected throughout the interview.

## Relationship to Hackathon Requirements

The interactive experience does not replace the required conversational interview.

BuzzPrep must still:

- conduct a multi-turn interview;
- ask at least 8 questions across at least 4 curriculum days;
- generate response-dependent follow-ups;
- preserve context using the provided `sessionId`;
- return the required structured feedback;
- expose `POST /api/interview`.

The visual workspace is an additional source of interview context and differentiation.

## Current Direction

The product concept is intentionally architecture-neutral at this stage.

The next design step is to decide:

- the exact interview flow;
- how canvas actions are represented as machine-readable state;
- which interactive challenge types are feasible for the hackathon;
- how the AI interviewer receives and evaluates workspace state;
- how scoring and feedback are derived;
- the frontend and backend architecture.
