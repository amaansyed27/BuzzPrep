# BuzzPrep

BuzzPrep is Team **BuzzBees'** submission for **The Interview Agent** hackathon challenge.

## Challenge

Build an AI interview agent that conducts realistic, personalized technical interviews using a learner's AI Cohort journey. The interviewer should adapt to the candidate, ask meaningful follow-up questions, preserve context across turns, and provide actionable feedback at the end.

The supplied cohort covers 31 days across environment setup, data foundations, embeddings and vector search, RAG, prompting, fine-tuning, full-stack chatbot development, memory, agents, MCP, evaluation, optimization, security, deployment, observability, and production AI systems.

## Product Idea

**BuzzPrep turns the technical interview into an interactive simulation, not just a conversation.**

The inspiration is scenario-based learning experiences such as Duolingo's interactive exercises: instead of only answering abstract questions, the learner must act inside a simulated environment.

During a BuzzPrep interview, the candidate talks with an AI interviewer while also working inside an adaptive technical workspace. The interviewer can give a real engineering task, observe how the candidate approaches it, and ask follow-up questions about the decisions they make.

The workspace is **not limited to RAG or to a drag-and-drop node graph**. BuzzPrep changes the interaction style to fit the curriculum topic. Depending on the challenge, a candidate might:

- connect components in a system or data-flow canvas;
- choose and configure tools or models;
- process or route data;
- repair a broken architecture;
- inspect logs, traces, metrics, or agent decisions;
- compare model, prompt, retrieval, or deployment choices;
- respond to a security or production incident;
- modify code/configuration snippets or structured schemas;
- test a system and interpret its output;
- explain the trade-offs behind each action.

For example, a RAG task may use a node canvas, while a prompt-engineering task may ask the candidate to construct and test a prompt, an MCP task may require wiring a client to exposed tools, and an observability task may present logs and metrics that must be diagnosed.

The AI adapts from both channels:

- what the candidate **says**;
- what the candidate **does** in the interactive workspace.

A weak or unusual decision can trigger a follow-up. A strong solution can lead to a harder constraint. The interviewer can also change the scenario mid-interview and ask the candidate to modify the system instead of merely describing what they would do.

The goal is to support interactive challenges across **all 31 curriculum days**, while selecting the most relevant tasks for each candidate based on their profile and learning history.

See [`docs/product-concept.md`](docs/product-concept.md) for the product model and [`docs/curriculum-interactions.md`](docs/curriculum-interactions.md) for example interactive challenges covering the complete curriculum.

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

BuzzPrep's interactive tasks complement these requirements rather than replacing them: workspace actions become additional interview context that can drive the required questions and follow-ups.

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

Curriculum-wide interactive interview concept defined. Architecture and implementation are still to be decided.

## License

This project is licensed under the [MIT License](LICENSE).
