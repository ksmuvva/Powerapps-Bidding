#!/usr/bin/env bash
#
# Export the Dataverse solution to this repo using YOUR OWN sign-in
# (interactive browser, MFA supported) — no app registration / service
# principal / secrets required.
#
# Prereq: Power Platform CLI (pac). Install once with .NET:
#   dotnet tool install --global Microsoft.PowerApps.CLI.Tool
# (or the standalone/MSI: https://aka.ms/PowerPlatformCLI )
#
# Usage:
#   solution/build/export_to_git.sh <solution-name> <environment-url>
#   e.g. solution/build/export_to_git.sh bidmanagement https://orgXXXX.crm11.dynamics.com
#
set -euo pipefail

SOLUTION="${1:-bidmanagement}"
ENV_URL="${2:-${DATAVERSE_URL:-}}"

if [ -z "$ENV_URL" ]; then
  echo "Usage: $0 <solution-name> <environment-url>"
  echo "   or: DATAVERSE_URL=<url> $0 <solution-name>"
  exit 1
fi

if ! command -v pac >/dev/null 2>&1; then
  echo "Power Platform CLI (pac) not found. Install it with:"
  echo "  dotnet tool install --global Microsoft.PowerApps.CLI.Tool"
  echo "  (or the MSI: https://aka.ms/PowerPlatformCLI )"
  exit 1
fi

echo ">> Signing in to $ENV_URL (a browser window will open)..."
pac auth create --environment "$ENV_URL"

echo ">> Exporting solution '$SOLUTION' (unmanaged)..."
mkdir -p out
pac solution export --name "$SOLUTION" --path out --managed false --overwrite

echo ">> Unpacking into solutions/$SOLUTION ..."
pac solution unpack \
  --zipfile "out/${SOLUTION}.zip" \
  --folder "solutions/${SOLUTION}" \
  --packagetype Unmanaged

rm -rf out

echo ">> Committing to git..."
git add "solutions/${SOLUTION}"
if git diff --staged --quiet; then
  echo "No solution changes to commit."
else
  git commit -m "Export ${SOLUTION} solution from Dataverse"
  git push
  echo "Done. Pushed solutions/${SOLUTION}."
fi
