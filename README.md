# BuzzPrep

BuzzPrep is Team **BuzzBees'** submission for **The Interview Agent** hackathon challenge.

## Challenge

Build an AI interview agent that conducts realistic, personalized technical interviews using a learner's AI Cohort journey. The interviewer should adapt to the candidate, ask meaningful follow-up questions, preserve context across turns, and provide actionable feedback at the end.

The supplied cohort covers 31 days across topics including RAG, vector databases, prompt engineering, agentic AI, MCP, deployment, security, observability, and production AI systems.

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

Initial repository setup. Product concept, architecture, and implementation will be developed during the hackathon.

## License

This project is licensed under the [MIT License](LICENSE).
