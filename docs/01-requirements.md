# 01 — Requirements

## 1. Vision

A single internal system where the group's four companies (Shreem Infotech,
adi3 Ltd, MVRIT, ALPs Agility) manage the full lifecycle of every bid they
pursue — from an opportunity landing in a daily feed, through bid/no-bid
qualification, drafting, internal review and submission, to win/loss outcome and
post-bid learning. The system is the single source of truth for pipeline value,
deadlines, and win rates, and is built so that AI agents can take on an
increasing share of the work over time.

## 2. Goals

- **Never miss a deadline.** Every live opportunity has an owner, a submission
  deadline, and a clear status.
- **Make fast, consistent bid/no-bid decisions** with a repeatable scoring model.
- **One pipeline, four companies.** Roll up the pipeline across the group while
  keeping each bid tagged to a single company.
- **Slice by domain and by buyer.** Report by capability (e.g. AI, Construction
  & FM) and by buyer type (e.g. NHS, MOD, Council) independently.
- **Keep all bid artefacts together** — tender docs, drafts, clarifications,
  submissions, and the final outcome.
- **Be AI-operable.** Data and processes are structured so Claude Code SDK
  agents can read, enrich, draft, summarise, and progress bids.

## 3. Scope

### In scope (this solution)

- Opportunity / bid register and lifecycle workflow.
- Reference data: companies, domains, buyer types, frameworks, contacts.
- Bid/no-bid qualification and scoring.
- Tasks, checklists and key dates per bid.
- Document management (tender pack + our responses).
- Win/loss capture and reporting dashboards.
- Role-based security and audit.
- Hooks/APIs that allow AI agents to operate on the data.

### Out of scope (for now)

- The daily Excel → Dataverse ingestion pipeline (designed in
  [05-data-import.md](05-data-import.md), built in a later phase).
- Full proposal authoring/word-processing (documents are attached/linked, not
  authored inside the app initially).
- Finance/invoicing and contract delivery after award.
- External / supplier-facing portal.

## 4. Users & roles

The day-to-day operators are **Admins**, supported increasingly by **AI agents**.
Roles are defined so they can be expanded as more human users join.

| Role | Description | Key permissions |
| ---- | ----------- | --------------- |
| **System Administrator** | Owns reference data, security, and import config. | Full control of all tables and configuration. |
| **Bid Manager** | Runs bids across one or more companies. | Create/edit bids, assign owners, move workflow stages, manage tasks & docs, record outcomes. |
| **Contributor** | Works on assigned bids. | Edit bids assigned to them, upload docs, complete tasks. |
| **Viewer / Leadership** | Oversight and reporting. | Read-only access to bids and dashboards. |
| **AI Agent (service principal)** | Claude Code SDK agents acting via an application user. | Scoped create/read/update on bids, tasks, notes and documents per [04-ai-agents.md](04-ai-agents.md). |

> Initial deployment is Admin-operated. The role model above is provisioned up
> front so adding humans later needs no rework.

## 5. Functional requirements

### 5.1 Opportunity & bid register

- FR-1: Capture an opportunity with title, reference, buyer/authority, buyer
  type, domain, owning company, estimated value, key dates and source.
- FR-2: Each bid is tagged to exactly one company (SMIT / ADI3 / MVRIT / ALPS).
- FR-3: Each bid has one primary domain and one buyer type; optional secondary
  domains may be tagged.
- FR-4: Bids can be linked to a **Framework / Lot** where the opportunity is a
  call-off under a framework agreement.
- FR-5: Auto-generated, human-readable bid reference (e.g. `SMIT-2026-0042`).

### 5.2 Workflow / lifecycle

- FR-6: Each bid moves through a defined stage pipeline:
  `Identified → Qualifying → Bid/No-Bid → In Progress → Internal Review →
   Submitted → Awarded / Lost / Withdrawn / No-Bid`.
- FR-7: Bid/No-Bid decision is recorded with a score, decision, decision-maker
  and rationale.
- FR-8: Stage changes are timestamped and attributed (business process flow +
  audit).
- FR-9: Overdue and at-risk (deadline within N days) bids are visually flagged
  and surfaced in views/dashboards.

### 5.3 Qualification & scoring

- FR-10: A configurable bid/no-bid scorecard (strategic fit, capability,
  competitiveness, commercial value, deliverability, win probability).
- FR-11: Weighted total score and a recommended decision.

### 5.4 Tasks, checklists & dates

- FR-12: Create tasks against a bid with owner, due date and status.
- FR-13: Standard task templates/checklists applied on stage entry.
- FR-14: Track key dates: published, clarification deadline, submission
  deadline, award date, contract start.

### 5.5 Documents

- FR-15: Attach/link tender documents and our response artefacts to a bid.
- FR-16: Categorise documents (Tender Pack, Clarification, Draft Response, Final
  Submission, Award Letter, Other).

### 5.6 Outcome & learning

- FR-17: Record outcome (Won/Lost/Withdrawn/No-Bid), awarded value, winner (if
  lost), and reason codes.
- FR-18: Capture post-bid lessons / feedback for future reuse by people and AI.

### 5.7 Reporting & dashboards

- FR-19: Pipeline by company, domain, buyer type and stage.
- FR-20: Win rate (count and value) by company, domain and buyer type.
- FR-21: Deadline calendar / upcoming submissions.
- FR-22: Separate "buyer lenses" — e.g. NHS view, MOD view, Council view.

### 5.8 AI agent operations

- FR-23: AI agents can create and update bids, tasks and notes via an
  application (service principal) user.
- FR-24: All AI-created/modified records are attributable and auditable
  (created/modified by the agent identity).
- FR-25: AI actions that change stage or commit a decision require an audit
  trail and (configurably) human confirmation. See [04-ai-agents.md](04-ai-agents.md).

## 6. Non-functional requirements

- NFR-1 **Platform**: Microsoft Power Platform — model-driven Power App on
  Dataverse, managed solution for ALM.
- NFR-2 **Security**: Role-based access via Dataverse security roles; least
  privilege; AI agent runs as a constrained application user.
- NFR-3 **Auditability**: Dataverse auditing enabled on bid, stage, decision and
  outcome changes.
- NFR-4 **Data quality**: Required fields and choice fields (not free text) for
  company, domain, buyer type and stage to keep reporting clean.
- NFR-5 **Performance**: Standard views load < 3s for typical data volumes
  (thousands of bids/year).
- NFR-6 **Extensibility**: Choices (domains, buyer types, frameworks) are
  data-driven so new ones are added without code changes.
- NFR-7 **ALM**: Dev → Test → Prod via solutions; source-controlled.
- NFR-8 **Compliance**: UK data residency; handle bid data as commercially
  confidential.

## 7. Assumptions

- A1: Microsoft 365 / Power Platform tenant with Dataverse is available.
- A2: The daily feed of opportunities (and supporting documents) is delivered
  from a **git repository** and ingested via a **webhook** on push — see
  [05-data-import.md](05-data-import.md).
- A3: Initial users are Admins; broader rollout follows.
- A4: AI agents authenticate via a registered app / application user in Dataverse.

## 8. Decisions & open questions

**Decided**

- D-1: Feed source is a **git repository**, ingested via **webhook** on push
  (data + documents). (Resolves former OQ-1 source.)
- D-2: Documents are delivered through the **same git feed/webhook** and stored
  in Dataverse file columns with the git path/commit retained for traceability.
  (Resolves former OQ-3.)
- D-3: **No consortium / joint bids** — each bid belongs to exactly one company.
  (Resolves former OQ-2.)

**Open**

- OQ-1: Exact feed details — repo URL, branch, file format and column headers
  (see [05-data-import.md](05-data-import.md)).
- OQ-4: Which AI agent actions are auto-applied vs require human approval —
  **not yet decided**.
- OQ-5: Definition of "at-risk" deadline window (N days).
