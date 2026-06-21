# 02 — Dataverse Data Model

This is the proposed Dataverse schema. Publisher prefix shown as `bid_`
(finalise during solution setup). Choice (option set) values are listed so
reporting and the daily import map cleanly onto them.

## Table overview

| Table | Purpose | Type |
| ----- | ------- | ---- |
| `bid_company` | The four trading companies | Reference |
| `bid_domain` | Capability domains | Reference |
| `bid_buyertype` | Buyer / sector categories | Reference |
| `bid_buyer` | Specific buying authorities (e.g. "NHS England", "MOD DE&S") | Reference |
| `bid_framework` | Framework agreements & lots | Reference |
| `bid_opportunity` | **Core** — an opportunity / bid | Transactional |
| `bid_scorecard` | Bid/no-bid qualification score | Transactional |
| `bid_task` | Tasks / checklist items per bid | Transactional |
| `bid_document` | Document metadata + file/link | Transactional |
| `bid_outcome` | Outcome & lessons learned | Transactional |
| `bid_contact` | People (buyer contacts, partners) | Reference |

Several "reference" tables could be modelled as global choices instead. They are
tables here so they are **data-driven** (Admins/AI add new domains, buyer types
and frameworks without changing the solution — satisfies NFR-6).

---

## bid_company

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | e.g. "Shreem Infotech" |
| `bid_code` | Text | SMIT / ADI3 / MVRIT / ALPS |
| `bid_active` | Yes/No | |

Seed rows: SMIT, ADI3, MVRIT, ALPS.

## bid_domain

Capability / delivery domain.

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | |
| `bid_active` | Yes/No | |

Seed rows: **Construction & FM, Healthcare, NHS, IT, AI, Environment &
Utilities**.

## bid_buyertype

Sector / type of buying organisation — drives the "buyer lenses".

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | |
| `bid_active` | Yes/No | |

Seed rows: **NHS, MOD, Local Council, Central Government, Housing Association,
Education, Blue Light (Police/Fire/Ambulance), Private, Other**.

## bid_buyer

The specific authority running the procurement.

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | e.g. "Birmingham City Council" |
| `bid_buyertype` | Lookup → bid_buyertype | |
| `bid_region` | Choice | UK region |
| `bid_website` | URL | |

## bid_framework

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | e.g. "G-Cloud 14", "NHS SBS" |
| `bid_lot` | Text | Lot reference |
| `bid_owner_authority` | Lookup → bid_buyer | |
| `bid_expiry` | Date | |

---

## bid_opportunity (core table)

One row per opportunity / bid. Auto-numbered reference per company/year.

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_reference` | Autonumber | e.g. `SMIT-2026-0042` |
| `bid_title` | Text (Primary) | Opportunity title |
| `bid_company` | Lookup → bid_company | **Owning company (exactly one)** |
| `bid_domain` | Lookup → bid_domain | Primary domain |
| `bid_secondary_domains` | Multi-select choice | Optional extra domains |
| `bid_buyertype` | Lookup → bid_buyertype | Sector lens |
| `bid_buyer` | Lookup → bid_buyer | Buying authority |
| `bid_framework` | Lookup → bid_framework | If call-off under a framework |
| `bid_stage` | Choice | See stage values below |
| `bid_status_reason` | Status reason | Active / Won / Lost / etc. |
| `bid_est_value` | Currency | Estimated contract value |
| `bid_duration_months` | Whole number | Contract term |
| `bid_win_probability` | Choice / % | Optional |
| `bid_source` | Choice | Daily Excel, Manual, Portal, AI-found |
| `bid_external_ref` | Text | Source/portal reference (import key) |
| `bid_published_date` | Date | |
| `bid_clarification_deadline` | DateTime | |
| `bid_submission_deadline` | DateTime | Key driver of alerts |
| `bid_award_date` | Date | |
| `bid_contract_start` | Date | |
| `bid_owner` (ownerid) | Owner | Bid manager/contributor |
| `bid_summary` | Multiline text | |
| `bid_ai_summary` | Multiline text | AI-generated précis |
| `bid_ai_processed` | Yes/No | Has an agent enriched this record |

### Stage choice (`bid_stage`)

`Identified` → `Qualifying` → `Bid/No-Bid` → `In Progress` →
`Internal Review` → `Submitted` → `Awarded` / `Lost` / `Withdrawn` / `No-Bid`

(Implement the active path as a **Business Process Flow**; terminal states via
status reasons.)

### Source choice (`bid_source`)

`Daily Excel Import`, `Manual Entry`, `Portal`, `AI Discovered`.

---

## bid_scorecard

Bid/no-bid qualification (1 active per bid; history allowed).

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_opportunity` | Lookup → bid_opportunity | |
| `bid_strategic_fit` | Choice 1–5 | |
| `bid_capability` | Choice 1–5 | Do we have the capability/track record |
| `bid_competitiveness` | Choice 1–5 | |
| `bid_commercial_value` | Choice 1–5 | |
| `bid_deliverability` | Choice 1–5 | |
| `bid_win_probability` | Choice 1–5 | |
| `bid_total_score` | Calculated | Weighted sum |
| `bid_recommendation` | Choice | Bid / No-Bid / Review |
| `bid_decision` | Choice | Bid / No-Bid |
| `bid_decision_by` | Lookup → systemuser | |
| `bid_decision_date` | DateTime | |
| `bid_rationale` | Multiline text | |

## bid_task

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | Task title |
| `bid_opportunity` | Lookup → bid_opportunity | |
| `bid_assigned_to` | Lookup → systemuser | |
| `bid_due_date` | DateTime | |
| `bid_status` | Choice | Not Started / In Progress / Done / Blocked |
| `bid_is_checklist_item` | Yes/No | From a stage template |
| `bid_created_by_ai` | Yes/No | |

## bid_document

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | |
| `bid_opportunity` | Lookup → bid_opportunity | |
| `bid_category` | Choice | Tender Pack / Clarification / Draft Response / Final Submission / Award Letter / Other |
| `bid_file` | File | Or SharePoint link (see OQ-3) |
| `bid_url` | URL | External link alternative |
| `bid_version` | Text | |

## bid_outcome

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_opportunity` | Lookup → bid_opportunity | 1:1 |
| `bid_result` | Choice | Won / Lost / Withdrawn / No-Bid |
| `bid_awarded_value` | Currency | |
| `bid_winning_supplier` | Text | If lost |
| `bid_reason_code` | Choice | Price / Quality / Capability / Late / Strategic / Other |
| `bid_lessons_learned` | Multiline text | Reusable by people + AI |
| `bid_debrief_received` | Yes/No | |

## bid_contact

| Column | Type | Notes |
| ------ | ---- | ----- |
| `bid_name` | Text (Primary) | |
| `bid_buyer` | Lookup → bid_buyer | |
| `bid_email` | Email | |
| `bid_phone` | Phone | |
| `bid_role` | Text | |

---

## Relationship summary

```
bid_company    1 ──< bid_opportunity
bid_domain     1 ──< bid_opportunity (primary)
bid_buyertype  1 ──< bid_opportunity
bid_buyer      1 ──< bid_opportunity
bid_framework  1 ──< bid_opportunity
bid_buyertype  1 ──< bid_buyer
bid_buyer      1 ──< bid_contact

bid_opportunity 1 ──< bid_scorecard
bid_opportunity 1 ──< bid_task
bid_opportunity 1 ──< bid_document
bid_opportunity 1 ──1 bid_outcome
```

## Import key

The daily Excel feed maps to `bid_opportunity`, keyed on `bid_external_ref`
(source/portal reference) so re-imports **upsert** rather than duplicate. See
[05-data-import.md](05-data-import.md).
