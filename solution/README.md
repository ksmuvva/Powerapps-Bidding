# Bid Management — Power Platform Solution

This folder contains the **Bid Management** Dataverse schema as code, plus two
ways to deploy it into a Power Platform environment.

What gets created:

- **11 tables** — Company, Domain, Buyer Type, Buyer, Framework, Opportunity
  (core), Scorecard, Bid Task, Bid Document, Outcome, Buyer Contact.
- **10 global choices** — Stage, Source, Region, Score, Recommendation,
  Decision, Task Status, Document Category, Result, Reason Code.
- **12 one-to-many relationships** wiring everything to the core Opportunity
  table and the reference tables.
- A **publisher** (`Shreem Group`, prefix `bid`) and an unmanaged **solution**
  (`Bid Management`).

The entire model is declared once in
[`build/generate_solution.py`](build/generate_solution.py) (the `SPEC` section)
and both deployment paths read from it.

---

## Important: which deployment path to use

> **Recommended (supported): Path B — Web API deployment script.**
> Microsoft documents creating tables/columns/relationships/choices by
> hand-editing `customizations.xml` as an **unsupported** operation. The
> generated solution zip (Path A) is provided for convenience and often works,
> but if it errors on import, use Path B, which uses the fully supported
> Dataverse metadata Web API.

These docs were generated without access to a live Dataverse tenant, so deploy
into a **development environment first**.

---

## Path A — Import the solution zip (convenience)

1. Build the zip (already committed under `dist/`, or regenerate):
   ```bash
   python3 build/generate_solution.py
   # -> dist/BidManagement_1_0_0_0.zip
   ```
2. Go to <https://make.powerapps.com> → pick your **dev environment**.
3. **Solutions** → **Import solution** → upload
   `dist/BidManagement_1_0_0_0.zip` → **Next** → **Import**.
4. If the import reports an error, note the message and switch to Path B (or
   send me the error and I'll correct the generator).

`dist/src/` contains the unzipped `solution.xml`, `customizations.xml`, and
`[Content_Types].xml` for inspection.

## Path B — Deploy via the supported Web API (recommended)

Creates the publisher, solution, choices, tables, columns and relationships
through documented metadata operations.

```bash
export DATAVERSE_URL="https://yourorg.crm11.dynamics.com"
# Get a bearer token, e.g. with Azure CLI:
export DATAVERSE_TOKEN="$(az account get-access-token \
  --resource https://yourorg.crm11.dynamics.com \
  --query accessToken -o tsv)"

python3 build/deploy_via_webapi.py
```

The script prints the result of each create call and is idempotent-ish
(already-existing components are skipped). You need a user/service principal
with the **System Customizer** (or System Administrator) role.

---

## After deployment — load reference data

Seed CSVs are in [`seed-data/`](seed-data/):

| File | Table | Rows |
| ---- | ----- | ---- |
| `companies.csv` | Company | SMIT, ADI3, MVRIT, ALPS |
| `domains.csv` | Domain | Construction & FM, Healthcare, NHS, IT, AI, Environment & Utilities |
| `buyer-types.csv` | Buyer Type | NHS, MOD, Council, Central Gov, Housing, Education, Blue Light, Private, Other |

Load them via **make.powerapps.com → Tables → (table) → Import → Import from
Excel/CSV**, or with `pac data import`.

---

## Notes & deviations from the design docs

- **Estimated/Awarded value** are modelled as **decimal** (not currency) to
  avoid pulling in the currency/exchange-rate columns on first deploy. Switch to
  a currency column later in the maker portal if multi-currency is needed.
- **Bid Reference** is a plain text column. Configure it as an **autonumber**
  (`SMIT-{SEQNUM:0000}` etc.) in the maker portal after deploy.
- **Documents** use a URL column for the git path/source. Add a Dataverse
  **File** column or SharePoint document management later (see
  [../docs/05-data-import.md](../docs/05-data-import.md)).
- Forms/views: the zip ships a basic main form + default view per table; the Web
  API path relies on Dataverse auto-generated forms/views. Build the model-driven
  app and richer views per [../docs/03-app-design.md](../docs/03-app-design.md).

## Regenerating

Edit the `SPEC` in `build/generate_solution.py`, then:

```bash
python3 build/generate_solution.py     # rebuild the zip
# and/or
python3 build/deploy_via_webapi.py     # re-deploy via Web API
```
