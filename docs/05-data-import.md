# 05 — Git Feed → Dataverse Ingestion (later phase)

> This pipeline is **not built yet**. This document captures the intended design
> so the data model and app are ready for it.

## Decision

The daily feed is **sourced from a git repository** and ingested into Dataverse
via a **webhook** (push-triggered), not a scheduled poll or a SharePoint drop.
Both the opportunity data **and** supporting documents arrive through this git
feed.

## Goal

Whenever the feed repo is updated (a push), the changed files are ingested into
Dataverse — creating new `bid_opportunity` records and updating existing ones —
without creating duplicates. Documents committed alongside the data are synced
to the related bid.

## Architecture

```
Feed git repo  ──push──►  Git webhook  ──►  Ingestion endpoint  ──►  Dataverse
(Excel/CSV +                (HTTP POST)      (Azure Function /        (upsert
 documents)                                   Power Automate HTTP /    opportunities,
                                              custom connector)        sync docs)
                                                     │
                                                     └──► Intake AI agent (enrich)
```

1. **Trigger** — a push to the feed repo fires a git webhook (HTTP POST) to the
   ingestion endpoint. The webhook payload identifies the commit and changed
   files.
2. **Endpoint** — an ingestion service receives the webhook. Recommended:
   - **Azure Function** (most control over parsing/secret-verification), or
   - **Power Automate** cloud flow with an **HTTP request trigger**, or
   - a **custom connector** fronting either.
3. **Verify** — validate the webhook signature/secret and the source repo/branch
   before processing (see Security below).
4. **Fetch & parse** — read the changed data file(s) from the repo (Excel/CSV)
   and parse rows. Read any changed document files.
5. **Upsert** opportunities into `bid_opportunity`, keyed on `bid_external_ref`
   (the source/portal reference):
   - Exists → update changed fields.
   - New → create, with `bid_source = "Git Feed Import"`.
6. **Resolve lookups** (company, domain, buyer type, buyer, framework) by
   name/code; unknown values go to a review queue rather than silently creating
   noise.
7. **Sync documents** — for document files in the push, create/update
   `bid_document` rows on the matching bid; store the binary in the Dataverse
   file column and retain the **git path/commit** in `bid_url` for traceability.
8. **Log** — write an **Import Log** row (commit SHA, files processed, created /
   updated / skipped / errored) for the Admin "Import Log" view.
9. **Handoff** — trigger the **Intake agent**
   ([04-ai-agents.md](04-ai-agents.md)) to enrich new/changed records.

## Why git + webhook

- **Versioned & auditable** — every feed change is a commit; the commit SHA is
  recorded on imported records and in the Import Log, so we can trace any record
  back to its source.
- **Event-driven** — updates flow in as soon as they're pushed; no polling lag,
  though pushes will typically happen on the daily cadence.
- **Single channel for data + docs** — opportunities and their documents travel
  together in the same repo.

## Expected feed layout (to confirm — OQ-1)

A suggested convention in the feed repo (final layout TBD with the feed owner):

```
/data/opportunities.xlsx        (or dated/CSV files)
/documents/<external_ref>/...   tender docs grouped by opportunity reference
```

### Column mapping (data file → Dataverse)

| Feed column (example) | Dataverse target |
| --------------------- | ---------------- |
| Reference / ID | `bid_external_ref` (key) |
| Title | `bid_title` |
| Company | `bid_company` (by code/name) |
| Domain / Category | `bid_domain` |
| Buyer Type / Sector | `bid_buyertype` |
| Buying Authority | `bid_buyer` |
| Framework / Lot | `bid_framework` |
| Estimated Value | `bid_est_value` |
| Published Date | `bid_published_date` |
| Clarification Deadline | `bid_clarification_deadline` |
| Submission Deadline | `bid_submission_deadline` |
| Source/Portal | `bid_source` / notes |
| Description | `bid_summary` |

## Document storage (resolves OQ-3)

- Documents are **fed from the git repo via the same webhook**.
- Store the file binary in the **Dataverse file column** on `bid_document`, and
  keep the originating **git path + commit SHA** in `bid_url` so each document is
  traceable to its source commit.
- Match a document to its bid by the `external_ref` folder convention above.

## Security

- Verify the webhook **secret/signature** on every call; reject unverified
  payloads.
- Restrict to the expected **repo and branch**.
- The ingestion service authenticates to Dataverse as the constrained
  application user (least privilege; no delete).
- Treat feed contents as commercially confidential (NFR-8).

## Data quality rules

- Reject/queue rows missing the key (`bid_external_ref`) or company.
- Normalise company to one of SMIT / ADI3 / MVRIT / ALPS.
- Map domain and buyer type to existing reference values; unknown values → review.

## To confirm (OQ-1)

- The feed **repo URL, branch**, and exact file layout / column headers.
- File format(s): Excel vs CSV; one rolling file vs dated files.
- Webhook provider (e.g. GitHub) and secret-management approach.
- Whether unknown buyers/frameworks are auto-created or routed to review.
