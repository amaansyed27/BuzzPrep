# BuzzPrep Demo Guide

This guide is the shortest reliable path for demonstrating BuzzPrep's differentiation and the organizer contract without turning the presentation into an infrastructure walkthrough.

## Live endpoints

```text
Frontend: https://buzzprep-web.vercel.app
API:      https://buzzprep-api.vercel.app
Health:   https://buzzprep-api.vercel.app/health
```

## The 20-second explanation

**BuzzPrep is an adaptive technical interviewer that combines conversation with a structured engineering workspace.** It personalizes the interview from the candidate's cohort history, records meaningful technical actions as evidence, adapts follow-ups using both the answer and workspace changes, and produces evidence-based final feedback.

The shortest differentiator:

> **It does not only ask what you know; it watches what you build, change, and defend.**

## Recommended browser demo

Use a laptop/desktop browser with a viewport wider than 960 CSS pixels and a fine pointer. The full workspace intentionally does not compress into a phone-sized interview view.

### 1. Start from the landing page

Open:

```text
https://buzzprep-web.vercel.app
```

Point out that the product has two paths:

- public demo/evaluator-compatible interview;
- optional Magic Link account for persistent owned history.

For a hackathon presentation, the public demo is the lowest-risk path because it does not depend on email delivery.

### 2. Select a supplied candidate

Open the demo setup and choose one of the supplied candidate profiles.

Explain that the backend does not simply paste the profile into a prompt. It deterministically profiles:

- role;
- years of experience;
- passed/failed/skipped days;
- attempt counts;
- strong and weaker learning signals.

The planner then chooses curriculum areas before the LLM generates interview wording.

### 3. Show readiness and the interview workspace

The active interview is composed of:

- candidate/progress context;
- reusable technical workspace;
- adaptive interviewer conversation.

Point out the real progress counters:

```text
questions / 8+
days / 4+
```

These are not fake UI counters. Python enforces the underlying minimum completion rule.

### 4. Perform one meaningful workspace action

Use whichever challenge renderer is active.

Good demonstration actions include:

- connect two components in the system canvas;
- change a timeout/retry/config choice;
- edit a prompt/schema/code/config block;
- run or submit an inspection/evaluation action.

Then show the workspace action count near the answer composer.

Important talking point:

> BuzzPrep records mutations as structured events. Simply clicking/selecting a node is not counted as evidence.

### 5. Explain the decision in chat

Answer the interviewer and explicitly reference the workspace decision.

A useful strong-answer pattern is:

```text
I changed X because the scenario requires Y. The trade-off is Z, and I would validate it using ...
```

The backend receives:

- the text answer;
- serialized workspace state;
- structured workspace events;
- separate integrity telemetry.

### 6. Show an adaptive follow-up

After a strong answer, point out a follow-up that deepens a trade-off, adds a constraint, or asks the candidate to defend a design decision.

Then give one intentionally weak or incomplete answer later in the interview and show the interviewer becoming more diagnostic.

This demonstrates that the sequence is not a fixed questionnaire.

### 7. Show more than one renderer mode

If the interview transitions across curriculum areas, highlight that BuzzPrep is not a single RAG canvas.

The backend planner exposes nine logical interaction types that map into four renderer families:

```text
System canvas
Configuration lab
Editor challenge
Inspection challenge
```

This architecture allows the same product to cover data, embeddings, RAG, prompting, APIs, agents, MCP, evaluation, security, deployment, observability, and capstone design.

### 8. Optional voice demonstration

If the browser exposes Speech Recognition, click the microphone and dictate part of an answer.

Then optionally enable interviewer read-aloud.

Explain accurately:

- voice is opt-in;
- candidates can always type;
- BuzzPrep's backend receives text, not an audio upload;
- speech recognition/synthesis support and processing behavior depend on the browser/OS implementation.

Do not make voice the core demo dependency. It is an enhancement, not the interview architecture.

### 9. Finish and show results

Continue until the backend completion gate is satisfied:

```text
at least 8 questions
AND
at least 4 distinct curriculum days
```

The LLM cannot bypass this gate.

The final response and UI must show exactly these feedback fields:

```text
summary
strengths
gaps
next
```

Point out that feedback is generated from the accumulated interview evidence rather than from one final answer.

## Best presentation sequence

A concise 4-6 minute product demo can follow this structure:

1. **Problem — 20 seconds**
   - learners completed the AI cohort but need realistic interview practice;
   - normal AI interviewers are mostly chat-based.

2. **BuzzPrep difference — 20 seconds**
   - adaptive conversation + practical workspace evidence.

3. **Candidate personalization — 30 seconds**
   - choose a supplied candidate;
   - explain deterministic profiling/planning.

4. **Interview/workspace — 2 minutes**
   - make a real workspace mutation;
   - explain it;
   - show adaptive follow-up.

5. **Coverage and reliability — 30 seconds**
   - Python-owned 8-question/4-day gate;
   - persistent SQL state;
   - real provider fallback;
   - Breeth is non-fatal.

6. **Results — 30-60 seconds**
   - show summary, strengths, gaps, next steps.

7. **Close — 15 seconds**
   - "BuzzPrep evaluates the engineering decisions behind the answer, not only the answer itself."

## What to emphasize technically

### Deterministic vs generative responsibilities

A useful architecture explanation is:

```text
Curriculum + candidate profile -> deterministic plan
LLM -> wording/evaluation/adaptation
Python -> state, rules, completion, validation
SQL -> canonical session state
Breeth -> optional semantic recall
Frontend -> renderer + structured action capture
```

This is stronger than saying "we used LangGraph" without explaining what the graph controls.

### Provider resilience

The production structured-generation chain can be:

```text
Gemini -> GroqCloud -> OpenRouter
```

Availability/provider failures can move through the chain. Invalid client requests are not masked by fallback. Fake AI is never selected silently.

### Persistence

A session is not stored only in browser state or an LLM conversation object. SQL persists the exact session, turns, curriculum coverage, challenge, workspace snapshot, evaluation state, and final result.

### Memory

Breeth stores concise high-signal evidence scoped to candidate/session. If memory is unavailable, the interview continues because SQL is authoritative.

### Auth

Authentication is a product extension, not an organizer requirement. Supabase bearer tokens are verified server-side and owned history is isolated by the verified user subject.

## Public evaluator demonstration

The organizer can use only the required endpoint.

### Start

```http
POST https://buzzprep-api.vercel.app/api/interview
Content-Type: application/json
```

```json
{
  "sessionId": "evaluator-demo-001",
  "candidate": {}
}
```

An empty candidate object selects the neutral evaluator-compatible profile.

### Continue

```json
{
  "sessionId": "evaluator-demo-001",
  "message": "I would separate deterministic routing from model reasoning and add bounded failure handling."
}
```

Workspace data is optional. The evaluator does not need to reproduce the browser product.

### Final response

After the interview completes:

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

## PowerShell evaluator smoke

Use a unique session id:

```powershell
$sessionId = "evaluator-$([Guid]::NewGuid().ToString('N').Substring(0, 8))"
$body = @{
  sessionId = $sessionId
  candidate = @{}
} | ConvertTo-Json -Depth 20

$response = Invoke-RestMethod `
  -Method Post `
  -Uri "https://buzzprep-api.vercel.app/api/interview" `
  -ContentType "application/json" `
  -Body $body

$response
```

Continue:

```powershell
$body = @{
  sessionId = $sessionId
  message = "I would first define the failure boundary, then validate the observable evidence before changing the architecture."
} | ConvertTo-Json -Depth 20

Invoke-RestMethod `
  -Method Post `
  -Uri "https://buzzprep-api.vercel.app/api/interview" `
  -ContentType "application/json" `
  -Body $body
```

## Low-risk demo fallback

If live provider credentials or external provider quotas are unreliable during a local presentation, use deterministic mode locally:

```env
LLM_PROVIDER_CHAIN=
LLM_PROVIDER=fake
BREETH_ENABLED=false
```

Restart the backend after changing `.env`.

This mode is useful to demonstrate the complete UI/state/evidence path without depending on external services. It should be described as deterministic demo/test mode rather than a live model run.

For the deployed hackathon product, prefer the configured live provider chain.

## What not to claim

Avoid claims that are stronger than the implementation.

Do not say:

- BuzzPrep records the candidate's screen — it does not;
- BuzzPrep records camera video — it does not;
- BuzzPrep continuously records microphone audio — it does not;
- voice recognition is guaranteed in every browser — it is not;
- Breeth is required for session memory — SQL is canonical and Breeth is optional semantic memory;
- every curriculum day has a unique custom UI — nine interaction types reuse four renderer families;
- the LLM decides the minimum interview length — Python enforces it;
- the public evaluator requires login — it does not.

## Useful one-line answers to likely judge questions

**How is it personalized?**  
The candidate profile is normalized deterministically and used to build a curriculum-grounded plan before the LLM generates questions.

**How do you know the interview is adaptive?**  
Each answer is evaluated, the graph makes a structured follow-up/deepen/transition decision, and the next question can include supplied workspace evidence.

**What makes the workspace real evidence?**  
Candidate mutations emit structured events and serialized state; simple visual selection is not treated as evidence.

**How do you guarantee the minimum requirements?**  
A Python completion gate requires at least eight questions and four distinct curriculum days.

**What happens if the primary model fails?**  
Configured real providers can fall back in order; BuzzPrep never silently switches to fake AI.

**What happens if Breeth fails?**  
The interview continues from canonical SQL state; semantic memory is non-fatal.

**Why SQL and Breeth?**  
SQL stores exact state and transcript; Breeth retrieves relevant high-signal observations for adaptive context.

**Does auth break the organizer endpoint?**  
No. The organizer endpoint is public. Auth only adds owned dashboard/history behavior.

**Is the voice feature server-side?**  
No audio endpoint is required; the browser converts speech to text and the normal text answer is submitted.
