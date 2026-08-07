# Curriculum-Wide Interactive Interview Map

BuzzPrep should be capable of generating an interactive technical interview from any part of the supplied 31-day AI Cohort.

The examples below are not fixed questions or a single scripted interview. They show how each curriculum day can become an **action-based interview challenge** rather than only a verbal Q&A.

## Module 1 — Environment & Tooling

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 1 | VS Code & Python Environment Setup | Present a broken Python project setup. The candidate chooses the correct interpreter, creates/activates a `.venv`, fixes an environment mismatch, and demonstrates how they would verify/debug the program. |
| 2 | Local LLM & AI Coding Assistant Setup | Give the candidate Ollama, Qwen2.5-Coder, GitHub Copilot/Cline, and several connection/configuration choices. Ask them to assemble a working local coding workflow and diagnose a failed local-model connection. |
| 3 | First AI Project, React Frontend & GitHub | Give partially connected React, Vite, FastAPI, Ollama, Git, and GitHub components. The candidate wires the frontend to the backend, connects the model, identifies the health/API flow, and orders the Git publishing steps. |

## Module 2 — Data Foundations

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 4 | Reading & Processing Structured Data | Present messy CSV healthcare data and a target question. The candidate chooses Pandas cleaning operations, decides what belongs in SQLite, constructs/selects a SQL query, and explains where SQLAlchemy fits. |
| 5 | Reading & Processing Unstructured Data | Present PDF, Word, scanned-form, and web inputs. The candidate routes each source through tools such as pdfplumber/PyPDF, python-docx, Tesseract OCR, or BeautifulSoup/Requests, then chooses normalization steps. |
| 6 | Building the Knowledge Base | Give a set of processed documents. The candidate chooses chunk boundaries, attaches source/plan/section metadata, rejects poor chunks, and assembles the records that should be exported to `knowledge_base.jsonl`. |

## Module 3 — Embeddings & Vector Search

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 7 | Embeddings Explained | Show candidate text samples, embedding/model choices, and a similarity visualization. Ask the candidate to choose an embedding approach, predict which concepts should cluster, interpret a PCA plot, and diagnose clearly poor semantic grouping. |
| 8 | Vector Databases Overview | Present requirements such as local development, cloud scale, filtering, and operational overhead. The candidate compares ChromaDB and Pinecone, chooses one for the scenario, configures the basic store, and defends the trade-off. |
| 9 | Building & Populating the Vector Database | Give chunks, embeddings, IDs, and metadata with several mistakes. The candidate constructs the vector records, detects missing/unindexed chunks, configures metadata filtering, and tests semantic search results. |
| 10 | The Retrieval & Matching Engine | Present structured and semantic user queries. The candidate builds a router between SQLite, ChromaDB, and hybrid retrieval, then decides how to merge/deduplicate results and repairs poor routing decisions. |

## Module 4 — LLM Core, Prompting & Fine-Tuning

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 11 | RAG End-to-End & LLM API Basics | Assemble retrieval, context, a grounded prompt, and a local/hosted LLM provider into an end-to-end RAG flow. Then show an unsupported answer and ask the candidate to diagnose whether retrieval, context, or prompting caused it. |
| 12 | Prompt Engineering Fundamentals | Give a task, several system instructions, examples, constraints, and test questions. The candidate constructs zero/few-shot prompt variants, tests them against fixed cases, compares accuracy/compliance/tone, and chooses the production prompt. |
| 13 | Advanced Prompting: Function Calling & Structured Outputs | Present chatbot functions and user queries. The candidate defines/selects function schemas, maps queries to tools, constructs a Pydantic-style output shape, detects invalid structured output, and inspects tool-call logs. |
| 14 | Fine-Tuning: Concepts & When to Use It | Present several chatbot failures and candidate solutions: prompting, RAG, or fine-tuning. The candidate chooses the appropriate approach, identifies which examples belong in a fine-tuning dataset, and separates valid training/test data. |
| 15 | Fine-Tuning: Hands-On with LoRA & QLoRA | Give base/fine-tuned model outputs and configuration choices. The candidate configures a plausible LoRA/QLoRA-style run, compares unseen-test behavior, interprets quality changes, and decides whether fine-tuning produced measurable benefit. |

## Module 5 — Chatbot Application Build

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 16 | Chatbot Backend & API Integration | Present a FastAPI chatbot backend with missing or incorrectly connected retrieval, function-calling, session, and history pieces. The candidate repairs the request flow and tests example requests/responses. |
| 17 | Chatbot Frontend Development | Give a Streamlit-style chat UI and backend endpoints. The candidate connects the frontend request flow, keeps conversation history, adds the plan selector/new-conversation behavior, and diagnoses an end-to-end state bug. |
| 18 | Full-Stack Integration & Streaming Responses | Show a token-streaming pipeline using FastAPI/StreamingResponse/SSE. The candidate places the streaming pieces correctly, fixes an interrupted stream, and chooses how the frontend should represent loading and failure states. |
| 19 | Response Formatting & Rich Outputs | Give raw model responses, retrieved sources, claims, and structured data. The candidate builds a trustworthy final response using citations, Markdown, cards/tables, and validated structured output while catching malformed data. |
| 20 | Conversation Memory & Context Management | Present a long conversation that exceeds a token budget. The candidate decides what history to keep, what to summarize, how to preserve user preferences, and repairs a case where important context is lost. |

## Module 6 — Agentic AI & MCP

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 21 | Agentic Frameworks: LangChain Agents & Tool Use | Give an agent a set of reusable tools and several queries. The candidate decides which tools the agent should expose, inspects a ReAct/tool-selection trace, identifies an incorrect decision, and modifies the tool setup or instructions. |
| 22 | Multi-Agent Orchestration | Give specialist agents and a router. The candidate constructs the delegation flow, routes sample healthcare requests, repairs an incorrect hand-off, and decides whether a single-agent or multi-agent design is justified for the scenario. |
| 23 | Model Context Protocol (MCP) | Present an MCP server, candidate tools, and compatible clients. The candidate decides what should be exposed as tools, connects the client/server flow, executes a sample interaction, and identifies a broken MCP tool contract. |
| 24 | Agentic Chatbot Integration | Give retrieval, memory, agents, MCP tools, retries, and timeouts as system components. The candidate assembles the production-style flow and then handles injected failures such as an unavailable MCP tool or timed-out agent action. |

## Module 7 — Evaluation, Security & Deployment

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 25 | Chatbot Evaluation & Testing | Present chatbot outputs and a candidate benchmark set. The candidate classifies test cases, chooses measures for accuracy/grounding/retrieval/consistency, identifies failure clusters, and decides what should be fixed first. |
| 26 | Performance Optimization & Cost Management | Show baseline latency, token usage, prompt size, retrieval count, and repeated-query behavior. The candidate changes retrieval/prompt/cache choices, runs a simulated benchmark, and balances cost against response quality. |
| 27 | Security, Privacy & Guardrails | Present an API and agent pipeline containing unsafe inputs, sensitive information, prompt injection, and missing protections. The candidate identifies vulnerable points and adds authentication/input validation/privacy/guardrail controls where appropriate. |
| 28 | Docker & Kubernetes Deployment | Give backend/frontend services and deployment components. The candidate creates the correct container/service relationships, configures environment variables and health checks, and diagnoses an unhealthy or incorrectly exposed deployment. |

## Module 8 — Production & Capstone

| Day | Curriculum topic | Example interactive interview task |
|---|---|---|
| 29 | Monitoring, Logging & Observability | Present logs, latency/error metrics, tool-execution data, and a dashboard. The candidate decides what should be logged/monitored, links Prometheus/Grafana-style signals to the application, and diagnoses a production regression from the evidence. |
| 30 | Production Readiness & Final Testing | Give a nearly finished application with several hidden integration failures. The candidate runs through an end-to-end readiness board, selects tests for retrieval/agents/frontend/deployment, finds failures, and prioritizes fixes/documentation. |
| 31 | Capstone Project & Final Demo | Give a complete enterprise-chatbot requirement. The candidate constructs or critiques the end-to-end architecture across retrieval, RAG, agents, MCP, memory, API/frontend, deployment, evaluation, and observability, then defends the key trade-offs as a final system-design interview. |

## How These Become Interviews

These tasks should not be presented as 31 fixed levels that every candidate must complete.

The interview agent should use the candidate profile and curriculum history to select a subset of relevant days, then combine interaction and conversation.

For example:

```text
Interviewer gives scenario
        ↓
Candidate performs an action
        ↓
Interviewer asks why
        ↓
Candidate explains
        ↓
System evaluates action + answer
        ↓
Interviewer introduces failure/constraint
        ↓
Candidate modifies solution
        ↓
Evidence recorded for feedback
```

The required interview still needs at least 8 questions spanning at least 4 curriculum days. Interactive challenges provide the practical context in which those questions and follow-ups happen.

## Reusable Interaction Primitives

The 31 curriculum examples can be covered by a relatively small frontend toolkit rather than 31 completely separate interfaces:

- **node/system canvas** — build pipelines and architectures;
- **drag/drop ordering** — arrange processing or deployment steps;
- **choice/config panels** — select tools, models, parameters, metadata, or policies;
- **data/table workbench** — inspect and manipulate records or retrieval results;
- **prompt/schema editor** — construct prompts, schemas, or structured responses;
- **code/config editor** — repair small snippets or configuration without requiring a full IDE;
- **log/trace/metric viewer** — diagnose agent and production behavior;
- **test runner/output panel** — compare expected and actual behavior;
- **incident cards** — introduce changing requirements and failures;
- **architecture critique mode** — identify, explain, and repair problems in an existing system.

The challenge definition should choose and combine these primitives based on the curriculum objective being assessed.
