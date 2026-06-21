# 04 — AI Agents (Claude Code SDK)

The solution is designed to be operated and assisted by AI agents built on the
**Claude Code SDK** (using the latest Claude models). Agents act on the same
Dataverse data the Power App uses, so humans and AI share one source of truth.

## How agents connect

- Agents authenticate to Dataverse via an **application user** backed by a
  registered Microsoft Entra app (service principal) — not a human licence.
- The app user is assigned the constrained **AI Agent** security role
  (see [03-app-design.md](03-app-design.md)): create/read/update on
  opportunities, tasks, notes, documents; **no delete**; **no** security or
  configuration access.
- Agents read/write through the Dataverse **Web API** (OData). Optionally,
  custom **Power Automate flows** or custom APIs expose higher-level actions
  (e.g. "qualify this bid") that agents call as tools.
- Every agent write is attributed to the app-user identity, so all AI activity
  is auditable (NFR-3) and visible on the "AI Agent Activity" view.

## Candidate agents

A multi-agent setup, each with a focused job:

| Agent | Job |
| ----- | --- |
| **Intake agent** | Read newly imported/created opportunities, normalise fields, fill `bid_buyer`/`bid_domain`/`bid_buyertype` where missing, generate `bid_ai_summary`, set `bid_ai_processed`. |
| **Qualification agent** | Draft a bid/no-bid scorecard from the tender + company track record; produce a recommendation and rationale for human sign-off. |
| **Research agent** | Enrich the buyer/framework, find incumbent/competitor and historical award info, surface risks. |
| **Task agent** | Generate the task checklist for the current stage; flag at-risk deadlines and nudge owners. |
| **Drafting agent** | Produce first-draft responses to tender questions from past winning bids and lessons learned. |
| **Reporting agent** | Answer natural-language questions over the pipeline ("NHS win rate this quarter by company") and summarise. |

## Human-in-the-loop guardrails

- Agents may freely create **drafts, notes, summaries, tasks, and
  recommendations**.
- Actions that **commit a decision or change stage** (e.g. setting the bid/no-bid
  decision, moving to Submitted, recording an outcome) require human
  confirmation by default — agents prepare, humans approve. (Configurable;
  see OQ-4.)
- A `bid_created_by_ai` / `bid_ai_processed` flag distinguishes AI-originated
  content for review.

## Why this shape

- Structured, choice-driven data ([02-data-model.md](02-data-model.md)) means
  agents read and write clean values, not ambiguous free text.
- One app user with least privilege keeps AI powerful but bounded.
- Auditing + the AI-activity surface keep AI actions transparent and reversible.

## Open items

- OQ-4: Exact list of auto-applied vs approval-required agent actions.
- Tooling: decide which higher-level actions become custom APIs/flows vs raw
  Web API calls.
- Orchestration: where the Claude Code SDK agents run and how they are scheduled
  / triggered (e.g. after the daily import).
