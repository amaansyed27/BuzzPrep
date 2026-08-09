# BuzzPrep

BuzzPrep is Team **BuzzBees'** submission for **The Interview Agent** hackathon.
It is an adaptive technical interview workspace: the interviewer evaluates both what a
candidate says and what they do in a structured engineering challenge.

## What works

- Candidate selection uses all 20 supplied profiles from `candidates.json`.
- LangGraph owns the adaptive question, evaluation, follow-up, and feedback flow.
- Python enforces the completion gate: at least 8 questions across 4 curriculum days.
- SQLite persists local/test sessions; standard PostgreSQL persists deployed sessions.
- Gemini uses validated structured generation with bounded retries and secret-safe errors.
- Breeth stores only high-signal, session/candidate-scoped evidence and degrades safely.
- The workspace includes a React Flow system canvas, Monaco-based editor, configuration
  lab, and logs/metrics/trace inspection mode.
- Workspace mutations are serialized and sent with the candidate's answer; simple visual
  selection is not treated as evidence.
- The final view renders the required `summary`, `strengths`, `gaps`, and `next` fields.

## Architecture

- Frontend: React 19, Vite, TypeScript, Zustand, React Flow, Monaco, Lucide.
- Backend: Python 3.12, FastAPI, Pydantic, LangGraph, SQLAlchemy, psycopg 3.
- LLM: Gemini structured generation, or an explicitly selected deterministic fake provider.
- Memory: Breeth Python SDK behind a small `MemoryService` interface.
- Persistence: local SQLite or deployed PostgreSQL (Supabase is supported directly through
  its normal Postgres connection string; the Supabase Data API is not used).

The supplied curriculum is deterministic application data, not a vector database. Breeth
adds relevant evidence context but never overrides exact SQL session state.

## Environment

The canonical local configuration file is `repo-root/.env`. Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

Process environment variables take precedence over `.env`. Never commit `.env`.

```env
DATABASE_URL=sqlite:///./buzzprep.db

LLM_PROVIDER=gemini
LLM_API_KEY=
LLM_MODEL=gemini-3.6-flash

BREETH_API_KEY=
BREETH_ENABLED=true

VITE_API_BASE_URL=http://127.0.0.1:8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`LLM_PROVIDER=fake` is allowed for tests and explicit local demos. A normal run never falls
back to fake AI silently. If Breeth is enabled without a key, semantic memory logs a warning
and disables itself without failing the interview.

## Run locally on Windows

Use two PowerShell terminals from the repository root.

Backend:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` and `/health` to the local API.

For a deterministic demo without credentials, set these values in `.env` before starting
the backend:

```env
LLM_PROVIDER=fake
BREETH_ENABLED=false
```

Restore `LLM_PROVIDER=gemini` before a live-provider demo.

## Verification

Backend gates:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest
python -m ruff check .
python -m compileall -q app tests scripts
```

The deterministic end-to-end test is included in normal pytest and can also be isolated:

```powershell
python -m pytest tests\test_e2e_interview.py -q
```

Frontend gate:

```powershell
cd frontend
npm ci
npm run build
```

Live Gemini smoke (outside pytest):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\smoke_gemini.py
```

This starts a real session, submits one strong and one weak answer, and prints only a
secret-safe summary of the adaptive responses.

Live Breeth smoke (outside pytest):

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\smoke_breeth.py
```

This writes one temporary high-signal observation, retrieves it with the same
`group_id`/candidate scope, and checks that it is absent from another session scope.

## API contract

`POST /api/interview` is public and does not require authentication or workspace data.

Start:

```json
{
  "sessionId": "abc-123",
  "candidate": { "member": {}, "missions": [], "signals": {} }
}
```

Continue, optionally with additive workspace evidence:

```json
{
  "sessionId": "abc-123",
  "message": "My technical explanation...",
  "workspace": {
    "version": 1,
    "challengeId": "day-16-initial",
    "nodes": [],
    "edges": [],
    "config": {},
    "events": []
  }
}
```

Final:

```json
{
  "reply": "Interview completed.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
```

Non-final responses may add `challenge` and `progress`. They never expose hidden scores,
rubrics, answer keys, or future questions.

## PostgreSQL and Supabase

Set `DATABASE_URL` to a normal psycopg-compatible PostgreSQL URL. For Vercel or another
auto-scaling/serverless host with Supabase, use the dashboard's transaction-pooler URL on
port `6543`:

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@REGION.pooler.supabase.com:6543/postgres
```

BuzzPrep detects port `6543`, uses SQLAlchemy `NullPool`, and disables psycopg automatic
prepared statements for transaction-pooler compatibility. Use the direct/session URL for a
long-lived backend. Credentials remain server-side.

## Vercel deployment

Public hackathon demo:

- Frontend: <https://buzzprep-web.vercel.app>
- API: <https://buzzprep-api.vercel.app>
- Health: <https://buzzprep-api.vercel.app/health>

The currently published demo profile explicitly uses `LLM_PROVIDER=fake`,
`BREETH_ENABLED=false`, and SQLite under Vercel's writable `/tmp` directory. It proves the
public evaluator contract and browser integration, but it is not the live-provider,
durable-database submission profile. Before presenting it as the final hosted build, replace
those project settings with Gemini, Breeth, and a persistent Postgres `DATABASE_URL`, then
redeploy and repeat the live smoke tests.

The two application roots are independently deployable:

```powershell
cd backend
vercel

cd ..\frontend
vercel
```

Configure backend production variables:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `BREETH_API_KEY`
- `BREETH_ENABLED`
- `CORS_ORIGINS` (the deployed frontend origin)

Configure frontend production variables:

- `VITE_API_BASE_URL` (the deployed backend origin, without a trailing slash)

Verify the deployed backend before promotion:

```powershell
Invoke-RestMethod https://YOUR-API.vercel.app/health
```

Then verify a public `POST /api/interview` start request and the full browser journey before
promoting either preview deployment to production.

## Demo script

1. Select a supplied candidate and point out that their role and learning history shape the
   first curriculum area.
2. Start the interview and show the real `questions / 8+` and `days / 4+` progress counters.
3. Make one meaningful workspace change, attach or submit it, and explain that BuzzPrep sends
   the auditable event with the answer.
4. Give a strong explanation; show the interviewer escalating to a constraint/trade-off probe.
5. Give a deliberately weak explanation; show the targeted prerequisite diagnostic.
6. Continue across multiple renderer modes and at least four curriculum days.
7. Complete the eighth answer and show evidence-based strengths, gaps, and next steps.

The one-line differentiator: **BuzzPrep is not just a chatbot—it watches what the candidate
does in an interactive technical workspace and adapts.**

## Team BuzzBees

- **Ilma Khan**, Team Leader — [@ilmatech](https://github.com/ilmatech)
- **Amaan Syed** — [@amaansyed27](https://github.com/amaansyed27)

## License

[MIT](LICENSE)
