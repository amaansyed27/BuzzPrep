# BuzzPrep

BuzzPrep is Team **BuzzBees'** submission for **The Interview Agent** hackathon challenge.

## Challenge

Build an AI interview agent that conducts realistic, personalized technical interviews using a learner's AI Cohort journey. The interviewer should adapt to the candidate, ask meaningful follow-up questions, preserve context across turns, and provide actionable feedback at the end.

The supplied cohort covers 31 days across topics including RAG, vector databases, prompt engineering, agentic AI, MCP, deployment, security, observability, and production AI systems.

## Product Idea

**BuzzPrep turns the technical interview into an interactive simulation, not just a conversation.**

The inspiration is scenario-based learning experiences such as Duolingo's interactive language exercises: instead of only answering abstract questions, the learner must act inside a simulated environment.

During a BuzzPrep interview, the candidate talks with an AI interviewer while also working inside an interactive technical canvas. The interviewer can give a real engineering task, observe how the candidate approaches it, and ask follow-up questions about the decisions they make.

For example, a RAG challenge could ask the candidate to assemble a pipeline by dragging components onto a canvas and connecting them:

```text
Data Source → Chunking → Embeddings → Vector Store → Retrieval → LLM
```

Different compatible choices can be available at each stage, such as Sentence Transformers or an API embedding model, ChromaDB or Pinecone for vector storage, and structured or hybrid retrieval components. There should not be one hard-coded "correct" pipeline; the interview evaluates whether the candidate can make sensible choices and explain their trade-offs.

The AI can then adapt the interview from both channels:

- what the candidate **says**;
- what the candidate **builds or changes** on the canvas.

A weak or unusual design choice can trigger a follow-up. A strong answer can lead to a harder scenario. The interviewer can also introduce changing requirements or failure cases and ask the candidate to modify the system rather than merely describe the solution.

The same interaction model can later support other cohort topics such as agent orchestration, MCP, prompting, security, deployment, observability, and production-system design.

See [`docs/product-concept.md`](docs/product-concept.md) for the current concept in more detail.

## Team — BuzzBees

- **Ilma Khan** — Team Leader — [@ilmatech](https://github.com/ilmatech)
- **Amaan Syed** — [@amaansyed27](https://github.com/amaansyed27)

## Minimum Requirements

The solution must:

- Conduct a conversational, multi-turn technical interview.
- Ask at least **8 questions** covering at least **4 different curriculum days**.
- Generate follow-up questions based on previous answers.
- Maintain interview context throughout the session.
- Produce structured feedback at the end.
- Expose the required `POST /api/interview` HTTP endpoint.

BuzzPrep's interactive tasks complement these requirements rather than replacing them: actions on the canvas become additional interview context that can drive the required questions and follow-ups.

## API Contract

The interview API uses a supplied `sessionId` to maintain state.

- First request: `sessionId` + candidate profile.
- Later requests: `sessionId` + candidate response in `message`.
- Final response: `done: true` with `summary`, `strengths`, `gaps`, and `next` feedback fields.

See [`hackathon-resources/technical-spec.md`](hackathon-resources/technical-spec.md) for the complete contract.

## Resources

Hackathon-provided files are stored in [`hackathon-resources/`](hackathon-resources/):

- `curriculum.json` — 31-day AI Cohort curriculum.
- `candidates.json` — synthetic candidate profiles and learning signals.
- `technical-spec.md` — required API and feedback contract.

## Status

Product concept defined. Architecture and implementation are still to be decided.

## License

This project is licensed under the [MIT License](LICENSE).
