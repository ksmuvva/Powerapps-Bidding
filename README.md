# Bid Management Solution (Power Apps + Dataverse)

An internal bid-management platform for a group of four trading companies that
bid for UK public-sector and private contracts (NHS, MOD, councils, frameworks,
etc.). The solution tracks opportunities end-to-end, runs the bid/no-bid and
submission workflow, manages documents and tasks, and reports win/loss and
pipeline performance.

It is built on **Microsoft Power Platform** (Power Apps model-driven app +
Dataverse) and is designed from day one to be operated and assisted by
**AI agents (Claude Code SDK)**.

## Companies in scope

| Code   | Company           |
| ------ | ----------------- |
| SMIT   | Shreem Infotech   |
| ADI3   | adi3 Ltd          |
| MVRIT  | MVRIT             |
| ALPS   | ALPs Agility      |

Each bid belongs to exactly **one** company.

## Classification

Every opportunity is classified along two independent axes:

- **Domain / capability** — Construction & FM, Healthcare, NHS, IT, AI,
  Environment & Utilities.
- **Buyer type / sector** — NHS, MOD, Local Council, Central Government, Housing
  Association, Education, Private, Other.

This lets us report "all NHS bids" or "all bids in the AI domain" independently.

## Documentation

| Doc | Purpose |
| --- | ------- |
| [docs/01-requirements.md](docs/01-requirements.md) | Vision, scope, functional & non-functional requirements |
| [docs/02-data-model.md](docs/02-data-model.md) | Dataverse tables, columns, choices and relationships |
| [docs/03-app-design.md](docs/03-app-design.md) | App structure, screens, views, dashboards, security roles |
| [docs/04-ai-agents.md](docs/04-ai-agents.md) | How Claude Code SDK agents plug into the solution |
| [docs/05-data-import.md](docs/05-data-import.md) | Git feed → Dataverse ingestion via webhook (built later) |
| [docs/06-roadmap.md](docs/06-roadmap.md) | Phased delivery plan |
| [docs/07-app-build.md](docs/07-app-build.md) | Runbook to build the model-driven app (shell, forms, BPF, dashboards, roles) |
| [solution/](solution/) | **Importable Power Platform solution** — schema as code, zip, Web API deploy scripts, seed data |

## Deploy the solution

The Dataverse schema (11 tables, 10 global choices, 12 relationships) is built
and ready in [`solution/`](solution/). Two deployment paths are documented in
[solution/README.md](solution/README.md):

- **Path A** — import `solution/dist/BidManagement_1_0_0_0.zip` at
  make.powerapps.com (convenience).
- **Path B (recommended/supported)** — run `solution/build/deploy_via_webapi.py`
  against your environment.

Deploy into a **development environment first**.

## Status

Schema delivered as an importable solution (see [`solution/`](solution/)). The
git feed → Dataverse webhook ingestion and the model-driven app are upcoming work
described in the roadmap.
