# 06 — Delivery Roadmap

Phased plan. Each phase is shippable on its own.

## Phase 0 — Requirements & design (current)

- Capture vision, scope, roles, requirements.
- Design Dataverse data model, app structure, AI agent approach, import design.
- **Deliverable:** this `docs/` set. ✅

## Phase 1 — Foundation (Dataverse + reference data)

- Create the managed solution and publisher prefix.
- Build reference tables and seed them:
  - Companies: SMIT, ADI3, MVRIT, ALPS.
  - Domains: Construction & FM, Healthcare, NHS, IT, AI, Environment & Utilities.
  - Buyer types: NHS, MOD, Council, Central Gov, Housing, Education, Blue Light,
    Private, Other.
- Build the core `bid_opportunity` table + choices + autonumber.
- **Deliverable:** data model live in a Dev environment.

## Phase 2 — Core app & workflow

- Model-driven app, site map, main form, key views.
- Business Process Flow for stages.
- Scorecard, tasks, documents, outcome tables + subgrids.
- Security roles.
- **Deliverable:** Admins can manage bids end-to-end manually.

## Phase 3 — Reporting

- In-app dashboards + buyer lenses (NHS/MOD/Council).
- Power BI pipeline & win/loss reports.
- Deadline reminders via Power Automate.
- **Deliverable:** pipeline & win-rate visibility.

## Phase 4 — Daily Excel import

- Build the Power Automate upsert flow + Import Log
  ([05-data-import.md](05-data-import.md)).
- Confirm column mapping (OQ-1).
- **Deliverable:** opportunities flow in automatically each day.

## Phase 5 — AI agents (Claude Code SDK)

- Register Entra app + Dataverse application user with the AI Agent role.
- Build Intake and Qualification agents first; then Research, Task, Drafting,
  Reporting ([04-ai-agents.md](04-ai-agents.md)).
- Wire post-import handoff and human-in-the-loop guardrails.
- **Deliverable:** AI assists and progressively operates the pipeline.

## Phase 6 — Hardening & rollout

- ALM (Dev → Test → Prod), auditing, performance, onboarding of human users
  beyond Admins.
