# 08 — Export the Dataverse solution to GitHub (setup)

This wires up the [`export-solution.yml`](../.github/workflows/export-solution.yml)
GitHub Actions workflow so it can export the `bidmanagement` solution from your
Dataverse environment and commit the unpacked source into this repo.

You do this **once**. After that, you run the workflow whenever you want to
capture changes (a button click, or on a daily schedule).

---

## Can't create an app registration? Use one of these instead

If Step 1 fails with a permissions error, your tenant blocks non-admins from
registering apps. The app registration is **only needed for the automated GitHub
Actions route**. You can still get the solution into GitHub using your own
sign-in — pick one:

### Option B — Local export with your own login (no app reg, no secrets) ✅ easiest reliable

Uses the Power Platform CLI with an interactive browser sign-in (MFA works) and
your normal maker account.

1. Install the CLI once (needs .NET):
   ```bash
   dotnet tool install --global Microsoft.PowerApps.CLI.Tool
   # or the installer: https://aka.ms/PowerPlatformCLI
   ```
2. Run the helper script (signs in, exports, unpacks, commits, pushes):
   ```bash
   solution/build/export_to_git.sh bidmanagement https://orgXXXX.crm11.dynamics.com
   ```
   A browser opens for sign-in; then it commits `solutions/bidmanagement/`.

### Option C — Portal export, zero tooling (no app reg, no CLI)

1. <https://make.powerapps.com> → **Solutions** → tick **bidmanagement** →
   **Export solution** → **Next** → export as **Unmanaged** → download the
   `bidmanagement.zip`.
2. Put it in the repo: GitHub web UI → **Add file → Upload files** → drop the zip
   into a folder (e.g. `solutions/`) → commit. (Send it to me and I can unpack it
   into diffable files.)

### Option D — Ask an admin to create the app registration

If you want the hands-off **automated** workflow, send your IT/Entra admin
Step 1 below; once they give you the Client ID / Tenant ID / secret, you finish
Steps 2–4 yourself.

---

## Automated route (GitHub Actions + service principal)

The steps below set up the app registration for the
[`export-solution.yml`](../.github/workflows/export-solution.yml) workflow. Skip
this if you used Option B or C above.

Total time: ~15 minutes. You need: access to the **Microsoft Entra admin
center** (or Azure portal), the **Power Platform admin center**, and **admin on
this GitHub repo**.

---

## Step 1 — Register an app in Microsoft Entra (the service principal)

1. Go to <https://entra.microsoft.com> → **Identity → Applications → App
   registrations** → **New registration**.
2. Name it e.g. `powerplatform-github-export` → leave defaults → **Register**.
3. On the app's **Overview** page, copy these two values — you'll need them:
   - **Application (client) ID**  → this becomes `CLIENT_ID`
   - **Directory (tenant) ID**    → this becomes `TENANT_ID`
4. Go to **Certificates & secrets → Client secrets → New client secret**.
   - Description: `github`, Expiry: 12–24 months → **Add**.
   - **Copy the secret VALUE immediately** (not the Secret ID) — you can't see it
     again. → this becomes `CLIENT_SECRET`.

## Step 2 — Give the app access to your Dataverse environment

The app needs to be an **application user** in the environment with rights to
export solutions.

1. Go to <https://admin.powerplatform.microsoft.com> → **Environments** → open
   your environment (the one ending `…c501ae`).
2. Copy the **Environment URL** (e.g. `https://orgXXXX.crm11.dynamics.com`) →
   this becomes `POWERPLATFORM_URL`.
3. **Settings → Users + permissions → Application users → New app user**.
4. **Add an app** → search for `powerplatform-github-export` → select it.
5. Set the **Business unit** (the default/root one is fine).
6. Under **Security roles**, assign **System Administrator** (or **System
   Customizer**, which is enough to export) → **Create**.

## Step 3 — Add the four secrets to GitHub

1. In this repo: **Settings → Secrets and variables → Actions → New repository
   secret**.
2. Add each of these (names must match exactly):

   | Secret name | Value |
   | ----------- | ----- |
   | `POWERPLATFORM_URL` | Environment URL from Step 2 (e.g. `https://orgXXXX.crm11.dynamics.com`) |
   | `CLIENT_ID` | Application (client) ID from Step 1 |
   | `TENANT_ID` | Directory (tenant) ID from Step 1 |
   | `CLIENT_SECRET` | Client secret **value** from Step 1 |

## Step 4 — Run the workflow

1. Repo → **Actions** tab → **Export Dataverse solution to Git** (left list).
2. **Run workflow** → confirm the solution name (`bidmanagement`) → **Run
   workflow**.
3. Watch the run. On success it commits the unpacked solution to
   `solutions/bidmanagement/` on the branch you ran it from.

> First run on a protected/default branch: the workflow pushes a commit, so make
> sure branch protection allows the `github-actions[bot]` to push, or run it on a
> working branch.

---

## What you get

```
solutions/
└── bidmanagement/
    ├── Entities/            # each table as readable XML
    ├── OptionSets/          # global choices
    ├── Other/               # solution.xml, customizations.xml, relationships
    └── ...
```

This is the **source-controlled, diffable** representation of your live solution.
Re-running the workflow after you make changes in the maker portal commits just
the diffs — so Git becomes the history of your Dataverse customizations.

## Notes

- This is the **developer-tools** route to GitHub, which works today. The
  in-product **Connect to Git** button currently targets Azure DevOps (GitHub
  support is in preview, 2026 wave 1, and needs Managed Environments).
- To go the other way (build + deploy from source to another environment), add
  `pack-solution` + `import-solution` steps — see
  [Available GitHub Actions for Power Platform](https://learn.microsoft.com/power-platform/alm/devops-github-available-actions).
- Rotate the client secret before it expires and update the `CLIENT_SECRET`
  repo secret.
