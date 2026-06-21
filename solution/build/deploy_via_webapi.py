#!/usr/bin/env python3
"""
Deploy the Bid Management schema to a Dataverse environment using the
**supported** Dataverse Web API (metadata operations).

This creates a publisher, a solution, 10 global choices, 11 tables (with
columns), and 12 one-to-many relationships, all from the single spec declared
in generate_solution.py.

Quick start (interactive device-code sign-in)
---------------------------------------------
  pip install msal
  python3 solution/build/deploy_via_webapi.py \
      --url https://YOURORG.crm11.dynamics.com

  -> the script prints a code + URL; sign in with your maker/admin account.

Other auth options
------------------
  --auth az        use an Azure CLI token (run `az login` first)
  --auth token     read a bearer token from the DATAVERSE_TOKEN env var

Useful flags
------------
  --dry-run        show what would be created, call nothing
  --url <url>      environment URL (or set DATAVERSE_URL)

Needs a user/service principal with the System Customizer (or System
Administrator) role. No third-party packages required unless using --auth device
(which needs `msal`).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

from generate_solution import (
    ENTITIES, RELATIONSHIPS, _optionset_values, LCID, VERSION,
    PREFIX, OPTVAL_PREFIX, PUBLISHER_UNIQUE, PUBLISHER_DISPLAY,
    SOLUTION_UNIQUE, SOLUTION_DISPLAY,
)

# Public client id used by the Power Platform CLI for interactive sign-in.
DEFAULT_CLIENT_ID = os.environ.get(
    "AZURE_CLIENT_ID", "51f81489-12ee-4a9e-aaae-a2591f45987d")
AUTHORITY = "https://login.microsoftonline.com/organizations"


# --------------------------------------------------------------------------- #
# Auth
# --------------------------------------------------------------------------- #
def get_token(method, url):
    if method == "token":
        tok = os.environ.get("DATAVERSE_TOKEN", "")
        if not tok:
            sys.exit("--auth token requires the DATAVERSE_TOKEN env var.")
        return tok
    if method == "az":
        try:
            out = subprocess.check_output(
                ["az", "account", "get-access-token", "--resource", url,
                 "--query", "accessToken", "-o", "tsv"], text=True)
            return out.strip()
        except Exception as e:  # noqa
            sys.exit(f"Azure CLI token failed ({e}). Run `az login` first.")
    if method == "device":
        try:
            import msal
        except ImportError:
            sys.exit("Device-code sign-in needs MSAL. Run:  pip install msal")
        app = msal.PublicClientApplication(DEFAULT_CLIENT_ID, authority=AUTHORITY)
        flow = app.initiate_device_flow(scopes=[f"{url}/.default"])
        if "user_code" not in flow:
            sys.exit(f"Could not start device flow: {flow}")
        print("\n" + flow["message"] + "\n")  # contains URL + code
        result = app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            sys.exit(f"Sign-in failed: {result.get('error_description', result)}")
        return result["access_token"]
    sys.exit(f"Unknown auth method: {method}")


# --------------------------------------------------------------------------- #
# Web API client
# --------------------------------------------------------------------------- #
class Client:
    def __init__(self, url, token, dry_run=False):
        self.api = f"{url.rstrip('/')}/api/data/v9.2"
        self.token = token
        self.dry_run = dry_run
        self.created = self.skipped = self.failed = 0

    def req(self, method, path, body=None):
        url = path if path.startswith("http") else f"{self.api}/{path}"
        if self.dry_run and method != "GET":
            return 0, "(dry-run)"
        data = json.dumps(body).encode() if body is not None else None
        headers = {
            "Authorization": f"Bearer {self.token}",
            "OData-MaxVersion": "4.0", "OData-Version": "4.0",
            "Accept": "application/json", "Content-Type": "application/json",
            "MSCRM.SolutionUniqueName": SOLUTION_UNIQUE,
        }
        for attempt in range(5):
            r = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(r) as resp:
                    txt = resp.read().decode()
                    return resp.status, (json.loads(txt) if txt else {})
            except urllib.error.HTTPError as e:
                body_txt = e.read().decode()
                if e.code in (429, 503) and attempt < 4:
                    wait = int(e.headers.get("Retry-After", 2 ** (attempt + 1)))
                    time.sleep(wait)
                    continue
                return e.code, body_txt
            except urllib.error.URLError as e:
                return -1, f"network error: {e}"
        return -1, "exhausted retries"

    def write(self, what, path, body):
        status, resp = self.req("POST", path, body)
        if self.dry_run:
            print(f"  would create {what}")
            self.created += 1
            return
        if status in (200, 201, 204):
            print(f"  ✓ {what}")
            self.created += 1
        elif _already_exists(resp):
            print(f"  • {what} (already exists, skipped)")
            self.skipped += 1
        else:
            print(f"  ✗ {what}\n      {status}: {_short(resp)}")
            self.failed += 1


def _already_exists(resp):
    t = json.dumps(resp).lower() if isinstance(resp, dict) else str(resp).lower()
    return any(s in t for s in (
        "already exists", "duplicate", "with the same name",
        "with the specified name", "isvalidforcreate"))


def _short(resp):
    if isinstance(resp, str):
        try:
            resp = json.loads(resp)
        except Exception:  # noqa
            return resp[:300]
    if isinstance(resp, dict) and "error" in resp:
        return resp["error"].get("message", str(resp))[:300]
    return str(resp)[:300]


# --------------------------------------------------------------------------- #
# Metadata builders
# --------------------------------------------------------------------------- #
def label(text):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [{
            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
            "Label": text, "LanguageCode": LCID,
        }],
    }


def attr_meta(a):
    t = a["type"]
    m = {
        "SchemaName": a["schema"],
        "DisplayName": label(a["display"]),
        "Description": label(""),
        "RequiredLevel": {"Value": "None"},
    }
    if t in ("text", "url", "email"):
        fmt = {"text": "Text", "url": "Url", "email": "Email"}[t]
        ml = {"text": a.get("len", 100), "url": 500, "email": 200}[t]
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                "FormatName": {"Value": fmt}, "MaxLength": ml}
    if t == "memo":
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
                "Format": "Text", "MaxLength": a.get("len", 2000)}
    if t == "int":
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
                "Format": "None", "MinValue": -2147483648, "MaxValue": 2147483647}
    if t == "decimal":
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
                "Precision": a.get("precision", 2),
                "MinValue": -100000000000, "MaxValue": 100000000000}
    if t in ("date", "datetime"):
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
                "Format": "DateOnly" if t == "date" else "DateAndTime",
                "DateTimeBehavior": {"Value": "UserLocal"}}
    if t == "boolean":
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
                "DefaultValue": bool(a.get("default", 0)),
                "OptionSet": {
                    "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
                    "TrueOption": {"Value": 1, "Label": label("Yes")},
                    "FalseOption": {"Value": 0, "Label": label("No")},
                }}
    if t == "picklist":
        return {**m, "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
                "GlobalOptionSet@odata.bind":
                    f"/GlobalOptionSetDefinitions(Name='{a['optionset']}')"}
    raise ValueError(t)


def primary_name_meta(entity):
    schema, display, length = entity["primary"]
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
        "SchemaName": schema, "DisplayName": label(display),
        "Description": label(""), "RequiredLevel": {"Value": "None"},
        "MaxLength": length, "FormatName": {"Value": "Text"},
        "IsPrimaryName": True,
    }


# --------------------------------------------------------------------------- #
# Steps
# --------------------------------------------------------------------------- #
def preflight(c):
    if c.dry_run:
        print("DRY RUN — no changes will be made.\n")
        return
    status, resp = c.req("GET", "WhoAmI")
    if status != 200:
        sys.exit(f"Connectivity/auth check (WhoAmI) failed: {status} {_short(resp)}")
    print(f"Connected. UserId: {resp.get('UserId')}\n")


def ensure_publisher(c):
    print("Publisher")
    c.write(f"publisher {PUBLISHER_UNIQUE}", "publishers", {
        "uniquename": PUBLISHER_UNIQUE,
        "friendlyname": PUBLISHER_DISPLAY,
        "customizationprefix": PREFIX,
        "customizationoptionvalueprefix": OPTVAL_PREFIX,
    })


def ensure_solution(c):
    print("Solution")
    if c.dry_run:
        c.write(f"solution {SOLUTION_UNIQUE}", "solutions", {})
        return
    s, data = c.req(
        "GET",
        f"publishers?$select=publisherid&$filter=uniquename eq '{PUBLISHER_UNIQUE}'")
    if s != 200 or not data.get("value"):
        print("  ✗ cannot resolve publisher id; aborting solution create")
        c.failed += 1
        return
    pid = data["value"][0]["publisherid"]
    c.write(f"solution {SOLUTION_UNIQUE}", "solutions", {
        "uniquename": SOLUTION_UNIQUE, "friendlyname": SOLUTION_DISPLAY,
        "version": VERSION, "publisherid@odata.bind": f"/publishers({pid})",
    })


def deploy_optionsets(c):
    print("Global choices")
    for name, values in _optionset_values.items():
        c.write(name, "GlobalOptionSetDefinitions", {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "Name": name, "OptionSetType": "Picklist", "IsGlobal": True,
            "DisplayName": label(name.replace("bid_", "").replace("_", " ").title()),
            "Description": label(""),
            "Options": [{"Value": v, "Label": label(lbl)} for v, lbl in values],
        })


def deploy_entities(c):
    print("Tables")
    for e in ENTITIES:
        c.write(e["schema"], "EntityDefinitions", {
            "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
            "SchemaName": e["schema"],
            "DisplayName": label(e["display"]),
            "DisplayCollectionName": label(e["plural"]),
            "Description": label(e["display"] + " record"),
            "OwnershipType": "UserOwned",
            "HasActivities": False, "HasNotes": False,
            "Attributes": [primary_name_meta(e)],
        })


def deploy_columns(c):
    print("Columns")
    for e in ENTITIES:
        for a in e["attributes"]:
            if a["type"] == "lookup":
                continue
            c.write(f"{e['schema']}.{a['schema']}",
                    f"EntityDefinitions(LogicalName='{e['schema']}')/Attributes",
                    attr_meta(a))


def deploy_relationships(c):
    print("Relationships")
    for referenced, referencing, attr in RELATIONSHIPS:
        name = f"{referenced}_{referencing}_{attr}"[:100]
        ref_disp = next(e["display"] for e in ENTITIES if e["schema"] == referenced)
        c.write(name, "RelationshipDefinitions", {
            "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
            "SchemaName": name,
            "ReferencedEntity": referenced,
            "ReferencingEntity": referencing,
            "CascadeConfiguration": {
                "Assign": "NoCascade", "Delete": "RemoveLink", "Merge": "NoCascade",
                "Reparent": "NoCascade", "Share": "NoCascade", "Unshare": "NoCascade",
            },
            "Lookup": {
                "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
                "SchemaName": attr, "DisplayName": label(ref_disp),
                "Description": label(""), "RequiredLevel": {"Value": "None"},
            },
            "AssociatedMenuConfiguration": {
                "Behavior": "UseCollectionName", "Group": "Details", "Order": 10000,
            },
        })


def main():
    ap = argparse.ArgumentParser(description="Deploy Bid Management to Dataverse.")
    ap.add_argument("--url", default=os.environ.get("DATAVERSE_URL", ""),
                    help="Environment URL, e.g. https://org.crm11.dynamics.com")
    ap.add_argument("--auth", choices=["device", "az", "token"], default="device")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.url:
        sys.exit("Provide --url or set DATAVERSE_URL.")

    token = "" if args.dry_run else get_token(args.auth, args.url.rstrip("/"))
    c = Client(args.url, token, dry_run=args.dry_run)

    print(f"\nTarget: {args.url}\n")
    preflight(c)
    ensure_publisher(c)
    ensure_solution(c)
    deploy_optionsets(c)
    deploy_entities(c)
    deploy_columns(c)
    deploy_relationships(c)

    print(f"\nSummary: {c.created} created/ok, {c.skipped} skipped, {c.failed} failed")
    if not args.dry_run:
        print(f"Open https://make.powerapps.com → Solutions → {SOLUTION_DISPLAY} to verify.")
    sys.exit(1 if c.failed else 0)


if __name__ == "__main__":
    main()
