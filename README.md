# BuzzPrep

BuzzPrep is Team **BuzzBees'** submission for **The Interview Agent** hackathon.
It is an adaptive technical interview workspace: the interviewer evaluates both what a
candidate says and what they do in a structured engineering challenge.

## What works

- Candidate selection uses all 20 supplied profiles from `candidates.json`.
- LangGraph owns the adaptive question, evaluation, follow-up, and feedback flow.
- Python enforces the completion gate: at least 8 questions across 4 curriculum days.
- SQLite persists local/test sessions; standard PostgreSQL persists deployed sessions.
- Gemini, GroqCloud, and OpenRouter share one validated structured-generation interface.
  Runtime availability failures fail over in that order; invalid client requests do not.
- Breeth stores only high-signal, session/candidate-scoped evidence and degrades safely.
- The workspace includes a React Flow system canvas, Monaco-based editor, configuration
  lab, and logs/metrics/trace inspection mode.
- Workspace mutations are serialized and sent with the candidate's answer; simple visual
  selection is not treated as evidence.
- The final view renders the required `summary`, `strengths`, `gaps`, and `next` fields.
- The public product includes a landing page, Magic Link auth, a real SQL-backed dashboard,
  resumable interview history, readiness checks, and mobile-safe completed results.

## Architecture

- Frontend: React 19, Vite, TypeScript, Zustand, React Flow, Monaco, Lucide.
- Backend: Python 3.12, FastAPI, Pydantic, LangGraph, SQLAlchemy, psycopg 3.
- LLM: Gemini Interactions structured generation with GroqCloud and OpenRouter fallbacks,
  or an explicitly selected deterministic fake provider for offline development.
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

SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=

LLM_PROVIDER_CHAIN=gemini,groq,openrouter
LLM_PROVIDER=gemini
LLM_API_KEY=
LLM_MODEL=gemini-3.6-flash
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
OPENROUTER_API_KEY=
OPENROUTER_MODEL=openrouter/free

BREETH_API_KEY=
BREETH_ENABLED=true

VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_PUBLISHABLE_KEY=
VITE_ENABLE_AUTH=true
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://buzzprep-web.vercel.app
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

Landing, authentication, dashboard, history, and results are responsive. Starting or
resuming an active technical prep requires a viewport at least 960 CSS pixels wide and a
fine pointer; smaller/touch-only devices receive a desktop requirement with a copy-link
action instead of a cramped workspace.

For a deterministic demo without credentials, set these values in `.env` before starting
the backend:

```env
LLM_PROVIDER=fake
BREETH_ENABLED=false
```

Restore `LLM_PROVIDER=gemini` before a live-provider demo.

Magic Link authentication requires a Supabase project. Set the backend and `VITE_` public
URL/publishable-key pairs to the same project. In Supabase Auth URL Configuration use:

```text
Site URL: https://buzzprep-web.vercel.app
Redirect URLs:
  https://buzzprep-web.vercel.app/auth/callback
  http://localhost:5173/auth/callback
  http://127.0.0.1:5173/auth/callback
```

Only the publishable key belongs in Vite. Never expose a secret/service-role key.

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

Live structured smoke for the complete provider chain:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python scripts\smoke_structured_providers.py
```

This makes one bounded, schema-validated request to Gemini `gemini-3.6-flash`, GroqCloud
`openai/gpt-oss-120b`, and OpenRouter `openrouter/free`. It does not run during pytest.

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
  "candidate": {}
}
```

An empty object selects the neutral public-evaluator profile. The candidate product flow
sends the exact supplied candidate object from `candidates.json`.

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

When the browser sends a valid Supabase bearer token, the new session is associated with
the verified token subject. The browser never supplies a trusted raw user id. These routes
require that token and return only the current user's rows:

```text
GET /api/me/interviews
GET /api/me/interviews/{sessionId}
```

Public evaluator sessions remain ownerless. Integrity events such as tab visibility,
focus, fullscreen, and reconnect are stored separately from semantic workspace evidence.

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

The two application roots are independently deployable:

```powershell
cd backend
vercel

cd ..\frontend
vercel
```

Configure backend production variables:

- `DATABASE_URL`
- `LLM_PROVIDER_CHAIN`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `GROQ_API_KEY`
- `GROQ_MODEL`
- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL`
- `BREETH_API_KEY`
- `BREETH_ENABLED`
- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `CORS_ORIGINS` (the deployed frontend origin)

Configure frontend production variables:

- `VITE_API_BASE_URL` (the deployed backend origin, without a trailing slash)
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_PUBLISHABLE_KEY`
- `VITE_ENABLE_AUTH=true`

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
