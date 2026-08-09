# BuzzPrep Operations Guide

This guide covers local setup, environment configuration, provider modes, database/Supabase setup, verification, deployment, and common failure modes for the current BuzzPrep implementation.

## Prerequisites

Recommended local environment:

- Windows with PowerShell;
- Python 3.12+;
- Node.js/npm compatible with the checked-in frontend lockfile;
- Git;
- optional Vercel CLI for deployment.

Live-provider features additionally require the relevant API keys. Authenticated product flows require a Supabase project.

## 1. Clone and configure

From the repository root:

```powershell
git clone https://github.com/amaansyed27/BuzzPrep.git
cd BuzzPrep
Copy-Item .env.example .env
```

`.env` is intentionally ignored by Git. Do not commit secrets.

BuzzPrep loads `repo-root/.env` on backend startup with `override=False`, so real process environment variables take precedence.

## 2. Environment variables

The checked-in `.env.example` is the canonical variable inventory.

### Backend variables

| Variable | Purpose | Typical local/default value |
|---|---|---|
| `DATABASE_URL` | SQL interview state | `sqlite:///./buzzprep.db` |
| `SUPABASE_URL` | Supabase Auth project URL | empty unless auth enabled |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase public/publishable key used by backend token verification | empty unless auth enabled |
| `LLM_PROVIDER_CHAIN` | ordered structured-generation providers | `gemini,groq,openrouter` |
| `LLM_PROVIDER` | single provider when no chain is set | `gemini` |
| `LLM_API_KEY` | Gemini API key | secret |
| `LLM_MODEL` | Gemini model | `gemini-3.6-flash` |
| `GROQ_API_KEY` | GroqCloud API key | secret |
| `GROQ_MODEL` | GroqCloud model | `openai/gpt-oss-120b` |
| `OPENROUTER_API_KEY` | OpenRouter API key | secret |
| `OPENROUTER_MODEL` | OpenRouter model/router | `openrouter/free` |
| `BREETH_ENABLED` | enable semantic memory adapter | `true` |
| `BREETH_API_KEY` | Breeth API key | secret |
| `CORS_ORIGINS` | comma-separated browser origins | local + deployed frontend |

### Frontend variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | backend origin; empty is same-origin, local example uses `http://127.0.0.1:8000` |
| `VITE_SUPABASE_URL` | Supabase project URL exposed to browser |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | browser-safe Supabase publishable key |
| `VITE_ENABLE_AUTH` | enable the authenticated product flow |

Only public configuration belongs in `VITE_*`. Never expose a database password, service-role key, or LLM/Breeth secret through Vite variables.

## 3. Local backend

From the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --reload
```

The API should be available at:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "service": "buzzprep-api"
}
```

## 4. Local frontend

Open a second PowerShell terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

The Vite development server is explicitly configured around IPv4/local Windows behavior. `/api` and `/health` can be proxied to the backend during local development.

## 5. Local operating modes

### Deterministic/offline mode

Use this for development when no real LLM or Breeth credentials should be required:

```env
LLM_PROVIDER_CHAIN=
LLM_PROVIDER=fake
BREETH_ENABLED=false
```

The fake provider is deterministic and intended for tests/local demos only.

### Live single-provider Gemini mode

```env
LLM_PROVIDER_CHAIN=
LLM_PROVIDER=gemini
LLM_API_KEY=YOUR_KEY
LLM_MODEL=gemini-3.6-flash
```

### Live provider-chain mode

```env
LLM_PROVIDER_CHAIN=gemini,groq,openrouter
LLM_PROVIDER=gemini
LLM_API_KEY=YOUR_GEMINI_KEY
LLM_MODEL=gemini-3.6-flash
GROQ_API_KEY=YOUR_GROQ_KEY
GROQ_MODEL=openai/gpt-oss-120b
OPENROUTER_API_KEY=YOUR_OPENROUTER_KEY
OPENROUTER_MODEL=openrouter/free
```

When the chain is present, the backend constructs providers in that order. Provider/availability/structured-output failures can move to the next provider. A request rejected as invalid is surfaced rather than hidden behind fallback.

BuzzPrep does not silently fall back to the fake provider.

## 6. Breeth memory

Enable Breeth:

```env
BREETH_ENABLED=true
BREETH_API_KEY=YOUR_KEY
```

Disable it explicitly:

```env
BREETH_ENABLED=false
```

Breeth is optional for interview continuity. If retrieval/write fails, BuzzPrep logs the failure and continues using SQL state.

The adapter scopes memory with:

- candidate id as the Breeth end-user id;
- interview `sessionId` as the Breeth `group_id`.

## 7. Local database

The default is SQLite:

```env
DATABASE_URL=sqlite:///./buzzprep.db
```

The database stores interview sessions and turns. Local SQLite database files are ignored by Git.

BuzzPrep creates metadata-defined tables on application startup and applies compatible additive upgrades for fields introduced after the earliest session schema.

## 8. PostgreSQL / Supabase Postgres

BuzzPrep accepts ordinary PostgreSQL connection URLs and normalizes them to psycopg 3.

Example form:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DATABASE
```

### Supabase serverless transaction pooler

For Vercel/serverless production, use the Supabase transaction-pooler URL from the project dashboard, typically on port `6543`:

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@REGION.pooler.supabase.com:6543/postgres
```

When BuzzPrep detects port `6543`, it configures SQLAlchemy/psycopg for transaction-pooler compatibility:

- `prepare_threshold=None` disables psycopg automatic prepared statements;
- `NullPool` prevents per-function SQLAlchemy pools from competing with Supavisor;
- `pool_pre_ping` remains enabled for non-SQLite connections.

For a long-lived backend, a direct/session PostgreSQL connection can be used instead.

## 9. Supabase Auth

Authentication is optional for the public evaluator endpoint but required for user-owned dashboard/history routes.

Set matching backend variables:

```env
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
```

And frontend variables:

```env
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_KEY
VITE_ENABLE_AUTH=true
```

The frontend and backend must reference the same Supabase project.

### Auth redirect configuration

For the current production frontend, configure Supabase Auth URL settings similar to:

```text
Site URL:
  https://buzzprep-web.vercel.app

Redirect URLs:
  https://buzzprep-web.vercel.app/auth/callback
  http://localhost:5173/auth/callback
  http://127.0.0.1:5173/auth/callback
```

The backend validates access tokens against Supabase Auth's user endpoint. It does not trust a browser-provided owner id.

### Magic Link email limits

Supabase-hosted email delivery can be rate-limited. If the application reports an email-send rate limit, the public demo/evaluator remains available because `POST /api/interview` is intentionally unauthenticated.

For reliable repeated production auth testing, configure an appropriate SMTP setup or respect the hosted sender quota.

## 10. Backend verification

Activate the backend venv:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

Run the standard gates:

```powershell
python -m pytest
python -m ruff check .
python -m compileall -q app tests scripts
```

Run the deterministic E2E case directly:

```powershell
python -m pytest tests\test_e2e_interview.py -q
```

The production-finish release in PR #19 recorded 71 passing backend tests with Ruff and compile checks passing.

## 11. Frontend verification

```powershell
cd frontend
npm ci
npm run build
```

`npm run build` runs TypeScript checking before the Vite production build.

The voice-controls change after PR #19 is frontend-only and does not change the backend API/state contract.

## 12. Live smoke tests

These scripts make real external calls and therefore do not run inside normal pytest.

Activate the backend venv first:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

### Gemini adaptive smoke

```powershell
python scripts\smoke_gemini.py
```

This creates a real interview session and exercises strong/weak adaptive behavior with secret-safe output.

### Complete structured provider-chain smoke

```powershell
python scripts\smoke_structured_providers.py
```

This makes one bounded schema-validated structured request to each configured production provider path.

### Breeth smoke

```powershell
python scripts\smoke_breeth.py
```

This writes and retrieves a temporary scoped observation and checks cross-session isolation.

## 13. Public API smoke

Start a neutral evaluator session:

```powershell
$body = @{
  sessionId = "docs-smoke-001"
  candidate = @{}
} | ConvertTo-Json -Depth 20

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/interview" `
  -ContentType "application/json" `
  -Body $body
```

Continue the same session:

```powershell
$body = @{
  sessionId = "docs-smoke-001"
  message = "I would first define the failure boundary and validate the evidence before choosing an implementation."
} | ConvertTo-Json -Depth 20

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/interview" `
  -ContentType "application/json" `
  -Body $body
```

Use a new `sessionId` for each fresh start. Reusing a started session id with another `candidate` start request returns a session conflict.

## 14. Vercel deployment

BuzzPrep uses two independently deployable application roots.

### Backend

```powershell
cd backend
vercel
```

Configure production backend variables:

```text
DATABASE_URL
LLM_PROVIDER_CHAIN
LLM_PROVIDER
LLM_API_KEY
LLM_MODEL
GROQ_API_KEY
GROQ_MODEL
OPENROUTER_API_KEY
OPENROUTER_MODEL
BREETH_API_KEY
BREETH_ENABLED
SUPABASE_URL
SUPABASE_PUBLISHABLE_KEY
CORS_ORIGINS
```

### Frontend

```powershell
cd frontend
vercel
```

Configure production frontend variables:

```text
VITE_API_BASE_URL
VITE_SUPABASE_URL
VITE_SUPABASE_PUBLISHABLE_KEY
VITE_ENABLE_AUTH
```

`VITE_API_BASE_URL` should be the deployed backend origin without a trailing slash.

### Current production endpoints

```text
Frontend: https://buzzprep-web.vercel.app
API:      https://buzzprep-api.vercel.app
Health:   https://buzzprep-api.vercel.app/health
```

## 15. Production validation checklist

Before promoting a deployment:

1. call `GET /health`;
2. start a public interview with `POST /api/interview` and no auth;
3. continue the same session from a separate request;
4. verify the same database state is visible across deployment instances;
5. verify a full deterministic or live interview reaches exactly the required completion schema;
6. confirm coverage cannot finish below 8 questions / 4 distinct curriculum days;
7. exercise at least one workspace mutation and confirm the next answer request includes serialized workspace events;
8. verify LLM provider fallback using safe test conditions when credentials permit;
9. verify Breeth failure is non-fatal;
10. verify CORS from the deployed frontend origin;
11. verify authenticated history returns only the signed-in user's sessions;
12. verify public sessions remain ownerless;
13. verify landing/auth/dashboard/results on mobile widths;
14. verify active interview shows the desktop requirement on unsupported small/touch-only layouts;
15. verify the production frontend build contains no secret keys.

## 16. Browser voice behavior

Voice controls are optional enhancements in the active interviewer panel.

### Dictation requirements

The microphone button is enabled only if the browser exposes:

```text
SpeechRecognition
or
webkitSpeechRecognition
```

If unsupported, candidates can type normally.

The browser may require explicit microphone permission. Recognition implementation and whether processing occurs locally or through a browser/vendor service depend on that browser/OS. BuzzPrep itself sends only the resulting text to its backend and does not define an audio-upload endpoint.

### Read-aloud requirements

Read-aloud uses browser `speechSynthesis`. When voices are available, BuzzPrep prefers a locale-compatible natural/neural-style voice by name/locale scoring and otherwise uses an available voice.

## 17. Common troubleshooting

### Frontend reports API/network errors

Check the backend first:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Confirm:

- backend is bound to `127.0.0.1:8000`;
- frontend is opened at the configured local origin;
- `VITE_API_BASE_URL` is correct if bypassing the Vite proxy;
- `CORS_ORIGINS` includes the exact browser origin.

### `localhost` works inconsistently on Windows

BuzzPrep's Vite configuration was changed to use explicit IPv4 behavior because `localhost` can resolve to IPv6 `::1` while Uvicorn is listening on IPv4. Prefer:

```text
http://127.0.0.1:5173
http://127.0.0.1:8000
```

### Backend fails at startup with LLM configuration error

A normal runtime requires a configured provider or provider chain. For deterministic local work, explicitly set:

```env
LLM_PROVIDER_CHAIN=
LLM_PROVIDER=fake
```

Do not expect an implicit fake fallback.

### Gemini/Groq/OpenRouter request fails

Check:

- correct key variable;
- model variable;
- quota/rate limit;
- provider-chain order;
- outbound network access.

The structured adapters validate outputs against Pydantic models. A provider can fail even after HTTP success if it returns invalid structured data.

### Breeth key is missing

Either configure `BREETH_API_KEY` or set:

```env
BREETH_ENABLED=false
```

Memory is optional and should not prevent interview startup when intentionally disabled.

### Authenticated history returns 401/403

Check:

- frontend and backend point to the same Supabase project;
- access token is current;
- publishable key is correct;
- auth callback URL is allowed in Supabase;
- browser session actually completed the Magic Link callback.

### Magic Link email is not delivered

Check Supabase Auth logs and email rate limits. The public demo does not depend on email auth.

### Voice input button is disabled

The browser does not expose a supported Speech Recognition API. Use typing or test in a browser/OS combination that implements the API.

### Voice input starts then stops

Check microphone permission and browser speech-service availability. BuzzPrep displays a non-fatal voice message and keeps the text composer usable.

### Active interview is blocked on mobile

This is intentional. The technical workspace requires at least 960 CSS pixels and a fine pointer. Results/history/landing remain responsive.

## 18. Secret handling

Never commit:

- `.env`;
- database passwords;
- LLM provider API keys;
- Breeth API keys;
- Supabase service-role/secret keys.

Repository-safe public values include a Supabase project URL and publishable key where needed by browser auth, but they still belong in environment configuration rather than being hard-coded into source.
