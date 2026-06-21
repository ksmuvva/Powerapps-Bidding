# 03 — App Design

## App type

A **model-driven Power App** ("Bid Manager") on Dataverse. Model-driven is the
right fit because the solution is data-centric, needs role-based security,
business process flows, rich views/dashboards, and clean access for AI agents
via the Dataverse API. A canvas app or Power BI report can be layered on later
for a tailored leadership view.

## Site map / areas

```
Bid Manager
├── Pipeline
│   ├── My Open Bids
│   ├── All Open Bids
│   ├── Bids by Stage (Kanban-style views)
│   ├── Submission Calendar
│   └── At-Risk / Overdue
├── Opportunities (full register)
├── Buyer Lenses
│   ├── NHS
│   ├── MOD
│   ├── Councils
│   └── Central Government
├── Reference Data
│   ├── Companies
│   ├── Domains
│   ├── Buyer Types
│   ├── Buyers
│   ├── Frameworks
│   └── Contacts
├── Dashboards
└── Admin
    ├── Import Log (later phase)
    └── AI Agent Activity
```

## Key views (saved queries on bid_opportunity)

- **My Open Bids** — owner = current user, stage not terminal, sorted by
  submission deadline.
- **All Open Bids** — stage not terminal.
- **At-Risk** — submission deadline within N days and stage not Submitted.
- **Overdue** — submission deadline < today and not Submitted/terminal.
- **By Company** — grouped/filterable by SMIT / ADI3 / MVRIT / ALPS.
- **Buyer lens views** — filtered by `bid_buyertype` (NHS, MOD, Council, …).
- **Won this year / Lost this year**.

## Main form — bid_opportunity

Tabbed form:

1. **Summary** — title, reference, company, domain(s), buyer type, buyer,
   framework, value, key dates, owner, AI summary.
2. **Qualification** — embedded bid_scorecard subgrid + decision.
3. **Tasks** — bid_task subgrid (checklist + ad-hoc).
4. **Documents** — bid_document subgrid.
5. **Outcome** — bid_outcome (shown once Submitted/terminal).
6. **Activity / AI** — timeline (notes, posts), AI agent activity.

A **Business Process Flow** renders the active stage path across the top:
`Identified → Qualifying → Bid/No-Bid → In Progress → Internal Review →
Submitted`.

## Dashboards

- **Group Pipeline** — total open value, count by stage, by company, by domain,
  by buyer type.
- **Win/Loss** — win rate by company / domain / buyer type (count and value);
  lost-reason breakdown.
- **Deadlines** — calendar / upcoming submissions, at-risk count.
- **AI Activity** — records enriched, tasks created, drafts produced by agents.

Build interactive dashboards in the model-driven app; build richer analytics in
**Power BI** over Dataverse for leadership.

## Automation (Power Automate / business rules)

- Auto-set `bid_reference` per company/year.
- On stage entry, apply the relevant **task checklist template**.
- Deadline reminders (e.g. 7/3/1 days before submission) to the owner.
- Flag at-risk/overdue via business rules / view filters.
- Notify on outcome recorded.

## Security roles (Dataverse)

Map to the roles in [01-requirements.md](01-requirements.md):

- **System Administrator** — full.
- **Bid Manager** — create/read/write across opportunities, tasks, docs,
  scorecards, outcomes; read reference data.
- **Contributor** — read/write on records they own or are assigned; create
  tasks/docs.
- **Viewer** — read-only on transactional + reference data.
- **AI Agent (app user)** — scoped create/read/write per
  [04-ai-agents.md](04-ai-agents.md); no delete; no security-config access.

Ownership-based and (optionally) business-unit scoping by company can enforce
"each company sees its own bids" later if required.
