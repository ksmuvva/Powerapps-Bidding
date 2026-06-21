# 07 — App Build Runbook (model-driven app)

This finishes the **usable UI** on top of the tables. It assumes you have:

1. Run `solution/build/deploy_via_webapi.py` (tables, choices, relationships).
2. Loaded the seed CSVs (`solution/seed-data/`).
3. Run `solution/build/deploy_app.py` (custom Opportunity views).

What's automated vs done here:

| Layer | How |
| ----- | --- |
| Tables, choices, relationships | `deploy_via_webapi.py` (Web API) |
| Custom views (lenses, pipeline, at-risk, win/loss) | `deploy_app.py` (Web API) |
| App shell, site map, forms (subgrids), BPF, dashboards, security roles | **this runbook** (maker portal) |

> Why the portal for these: Microsoft recommends the modern app designer over
> code for app/sitemap/dashboards, and it auto-includes every table's forms,
> views and charts — so the custom views created above appear automatically.

All steps are at <https://make.powerapps.com> in your **dev environment**, inside
**Solutions → Bid Management** (so everything stays in the solution).

---

## 1. Customize the Opportunity main form (~5 min)

Tables → **Opportunity** → **Forms** → open the **Information** main form.

1. Organize the **General** tab into sections: *Summary* (title, reference,
   company, domain, buyer type, buyer, framework, stage, source), *Value &
   Dates* (estimated value, duration, published/clarification/submission/award/
   contract dates), *AI* (AI summary, AI processed).
2. Add **related-record subgrids** (the relationships already exist):
   - **Scorecard** (Bid Scorecards related to this Opportunity)
   - **Tasks** (Bid Tasks)
   - **Documents** (Bid Documents)
   - **Outcome** (Outcomes)
   Add each as a tab or section: *+ Component → Subgrid → Related → pick the
   table*.
3. **Save** → **Publish**.

(Reference tables — Company, Domain, Buyer, etc. — work fine with their
auto-generated forms.)

## 2. Business Process Flow — bid stages (~5 min)

Solutions → Bid Management → **+ New → Automation → Process → Business process
flow**.

- Table: **Opportunity**.
- Stages (each maps to the `Stage` choice): **Identified → Qualifying →
  Bid/No-Bid → In Progress → Internal Review → Submitted**.
- In each stage add 2–4 relevant data steps (e.g. Qualifying → buyer type,
  estimated value; Bid/No-Bid → link the scorecard decision).
- **Activate**.

## 3. Dashboards (~10 min)

Solutions → Bid Management → **+ New → Dashboard → 2 or 3 column overview**.

Create these charts (Opportunity → **Charts → + New chart**) and drop them on the
dashboard:

| Chart | Type | Category (X) | Value (Y) |
| ----- | ---- | ------------ | --------- |
| Pipeline Value by Stage | Column | Stage | Sum of Estimated Value |
| Open Bids by Company | Bar | Company | Count |
| Pipeline by Buyer Type | Pie | Buyer Type | Count |
| Win/Loss by Company | Stacked column | Company | Count (filter stage = Awarded/Lost) |

Add the **At-Risk - Due This Week** view as a list component for a deadline
watch-list. **Save → Publish**.

> For richer analytics later, connect **Power BI** to Dataverse and build the
> pipeline / win-rate reports described in [03-app-design.md](03-app-design.md).

## 4. Create the model-driven app + site map (~10 min)

Solutions → Bid Management → **+ New → App → Model-driven app** (modern
designer). Name it **Bid Manager**.

Add pages / navigation to match [03-app-design.md](03-app-design.md):

- **Pipeline** (area)
  - Opportunity — set default view to **All Open Bids**; also surface *My Open
    Bids*, *At-Risk - Due This Week*.
  - The Win/Loss dashboard.
- **Buyer Lenses** (group) — Opportunity pages defaulting to the **NHS Bids**,
  **MOD Bids**, **Council Bids** views (one subarea each, titled NHS / MOD /
  Councils).
- **Reference Data** (area) — Companies, Domains, Buyer Types, Buyers,
  Frameworks, Buyer Contacts.

For each table page, ensure the relevant forms/views/charts are ticked
(included by default). **Save → Publish**.

> Tip: to make a view the table's default, open **Views** for the table, select
> the view, and set it as default; the app then opens on it.

## 5. Security roles (~10 min)

Solutions → Bid Management → **+ New → Security → Security role**. Create the
four roles from [01-requirements.md](01-requirements.md) and grant table
privileges:

| Role | Opportunity & children | Reference data | Config |
| ---- | ---------------------- | -------------- | ------ |
| **Bid Manager** | Create/Read/Write/Append (Organization) | Read | none |
| **Contributor** | Create/Read/Write (User/owned) | Read | none |
| **Viewer** | Read (Organization) | Read | none |
| **AI Agent** | Create/Read/Write (Organization), **no Delete** | Read | none |

Assign the app + role to users (and the application user for AI — see
[04-ai-agents.md](04-ai-agents.md)).

## 6. Post-build configuration

- **Bid Reference autonumber**: Opportunity → column `bid_reference` → set data
  type to **Autonumber**, format e.g. `{COMPANY}-{DATETIME:yyyy}-{SEQNUM:0000}`
  (or per-company prefixes via a Power Automate flow).
- **Deadline reminders**: Power Automate scheduled flow on `Submission Deadline`
  (7/3/1 days) → notify the owner.
- **Stage checklist templates**: flow that creates standard Bid Tasks on stage
  entry.

## Done

Play the **Bid Manager** app. You now have: a stage-driven Opportunity form with
scorecard/tasks/documents/outcome, pipeline + buyer-lens + win/loss views,
dashboards, and role-based access — ready for the git feed
([05-data-import.md](05-data-import.md)) and AI agents
([04-ai-agents.md](04-ai-agents.md)).
