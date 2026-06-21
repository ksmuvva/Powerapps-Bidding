# 05 — Daily Excel → Dataverse Import (later phase)

> This pipeline is **not built yet**. This document captures the intended design
> so the data model and app are ready for it.

## Goal

Each day, an Excel export of opportunities is ingested into Dataverse,
creating new `bid_opportunity` records and updating existing ones — without
creating duplicates.

## Approach

Recommended: **Power Automate** scheduled cloud flow.

1. Trigger: scheduled (daily) — or "when a file is created/modified" if the
   Excel lands in a known SharePoint/OneDrive location.
2. List rows from the Excel table.
3. For each row, **upsert** into `bid_opportunity` keyed on
   `bid_external_ref` (the source/portal reference):
   - If a record with that key exists → update changed fields.
   - Else → create, with `bid_source = "Daily Excel Import"`.
4. Resolve lookups (company, domain, buyer type, buyer, framework) by name/code;
   if a referenced value doesn't exist, either create it or route to a review
   queue (decision per OQ-1).
5. Write an **Import Log** row (rows read / created / updated / skipped /
   errored) for the Admin "Import Log" view.

Alternatives if volume/transform needs grow: **Dataverse dataflows** (Power
Query) or **Azure Data Factory**.

## Expected column mapping (to confirm — OQ-1)

| Excel column (example) | Dataverse target |
| ---------------------- | ---------------- |
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

## Post-import handoff to AI

After a successful import, trigger the **Intake agent**
([04-ai-agents.md](04-ai-agents.md)) to enrich the new/changed records
(normalise lookups, generate `bid_ai_summary`, set `bid_ai_processed`).

## Data quality rules

- Reject/queue rows missing the key (`bid_external_ref`) or company.
- Normalise company to one of SMIT / ADI3 / MVRIT / ALPS.
- Map domain and buyer type to existing reference values; unknown values go to
  review rather than silently creating noise.

## To confirm (OQ-1)

- Exact source, filename/location, and column layout of the daily Excel.
- Whether unknown buyers/frameworks are auto-created or reviewed.
- Time of day / SLA for the daily run.
