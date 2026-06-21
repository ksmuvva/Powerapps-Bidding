#!/usr/bin/env python3
"""
Deploy the Bid Management schema to a Dataverse environment using the
**supported** Dataverse Web API (metadata operations).

This is the recommended, fully-supported alternative to importing the
hand-authored solution zip. It creates: a publisher, a solution, 10 global
choices, 11 tables (with columns), and 12 one-to-many relationships — all from
the single spec declared in generate_solution.py.

Usage
-----
  export DATAVERSE_URL="https://yourorg.crm11.dynamics.com"
  export DATAVERSE_TOKEN="<bearer access token>"
  python3 solution/build/deploy_via_webapi.py

Getting a token (any one of):
  * Azure CLI:   az account get-access-token --resource https://yourorg.crm11.dynamics.com --query accessToken -o tsv
  * pac:         pac auth create --url https://yourorg.crm11.dynamics.com   (then reuse its token)
  * a registered app / service principal with the Dataverse "system customizer" role.

The script is idempotent-ish: components that already exist are skipped.
No third-party packages required (uses urllib).
"""
import json
import os
import sys
import urllib.request
import urllib.error

# Reuse the single source of truth.
from generate_solution import (
    ENTITIES, RELATIONSHIPS, _optionset_values, LCID, VERSION,
    PREFIX, OPTVAL_PREFIX, PUBLISHER_UNIQUE, PUBLISHER_DISPLAY,
    SOLUTION_UNIQUE, SOLUTION_DISPLAY,
)

URL = os.environ.get("DATAVERSE_URL", "").rstrip("/")
TOKEN = os.environ.get("DATAVERSE_TOKEN", "")
API = f"{URL}/api/data/v9.2"

if not URL or not TOKEN:
    sys.exit("Set DATAVERSE_URL and DATAVERSE_TOKEN environment variables.")


def label(text):
    return {
        "@odata.type": "Microsoft.Dynamics.CRM.Label",
        "LocalizedLabels": [{
            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
            "Label": text, "LanguageCode": LCID,
        }],
    }


def req(method, path, body=None, headers=None):
    url = path if path.startswith("http") else f"{API}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    h = {
        "Authorization": f"Bearer {TOKEN}",
        "OData-MaxVersion": "4.0", "OData-Version": "4.0",
        "Accept": "application/json", "Content-Type": "application/json",
        "MSCRM.SolutionUniqueName": SOLUTION_UNIQUE,
    }
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            txt = resp.read().decode()
            return resp.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def ok(status):
    return status in (200, 201, 204)


# --------------------------------------------------------------------------- #
# Column metadata builders
# --------------------------------------------------------------------------- #
def attr_meta(a):
    t = a["type"]
    common = {
        "SchemaName": PREFIX + "_" + a["schema"].split("_", 1)[1],
        "DisplayName": label(a["display"]),
        "Description": label(""),
        "RequiredLevel": {"Value": "None"},
    }
    common["SchemaName"] = a["schema"]  # already prefixed in spec
    if t in ("text", "url", "email"):
        fmt = {"text": "Text", "url": "Url", "email": "Email"}[t]
        ml = {"text": a.get("len", 100), "url": 500, "email": 200}[t]
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
                "FormatName": {"Value": fmt}, "MaxLength": ml}
    if t == "memo":
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
                "Format": "Text", "MaxLength": a.get("len", 2000)}
    if t == "int":
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
                "Format": "None", "MinValue": -2147483648, "MaxValue": 2147483647}
    if t == "decimal":
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
                "Precision": a.get("precision", 2),
                "MinValue": -100000000000, "MaxValue": 100000000000}
    if t in ("date", "datetime"):
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
                "Format": "DateOnly" if t == "date" else "DateAndTime",
                "DateTimeBehavior": {"Value": "UserLocal"}}
    if t == "boolean":
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
                "DefaultValue": bool(a.get("default", 0)),
                "OptionSet": {
                    "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
                    "TrueOption": {"Value": 1, "Label": label("Yes")},
                    "FalseOption": {"Value": 0, "Label": label("No")},
                }}
    if t == "picklist":
        return {**common, "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
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
# Deployment steps
# --------------------------------------------------------------------------- #
def ensure_publisher():
    s, _ = req("POST", "publishers", {
        "uniquename": PUBLISHER_UNIQUE,
        "friendlyname": PUBLISHER_DISPLAY,
        "customizationprefix": PREFIX,
        "customizationoptionvalueprefix": OPTVAL_PREFIX,
    })
    print(f"[publisher] {PUBLISHER_UNIQUE}: {'ok' if ok(s) else s}")


def ensure_solution():
    # need publisher id
    s, data = req("GET", f"publishers?$select=publisherid&$filter=uniquename eq '{PUBLISHER_UNIQUE}'")
    pid = data["value"][0]["publisherid"] if ok(s) and data.get("value") else None
    if not pid:
        print("[solution] cannot find publisher id; create publisher first")
        return
    s, _ = req("POST", "solutions", {
        "uniquename": SOLUTION_UNIQUE,
        "friendlyname": SOLUTION_DISPLAY,
        "version": VERSION,
        "publisherid@odata.bind": f"/publishers({pid})",
    })
    print(f"[solution] {SOLUTION_UNIQUE}: {'ok' if ok(s) else s}")


def deploy_optionsets():
    for name, values in _optionset_values.items():
        body = {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "Name": name, "OptionSetType": "Picklist", "IsGlobal": True,
            "DisplayName": label(name.replace("bid_", "").replace("_", " ").title()),
            "Description": label(""),
            "Options": [{"Value": v, "Label": label(lbl)} for v, lbl in values],
        }
        s, r = req("POST", "GlobalOptionSetDefinitions", body)
        print(f"[choice] {name}: {'ok' if ok(s) else r}")


def deploy_entities():
    for e in ENTITIES:
        body = {
            "@odata.type": "Microsoft.Dynamics.CRM.EntityMetadata",
            "SchemaName": e["schema"],
            "DisplayName": label(e["display"]),
            "DisplayCollectionName": label(e["plural"]),
            "Description": label(e["display"] + " record"),
            "OwnershipType": "UserOwned",
            "HasActivities": False, "HasNotes": False,
            "Attributes": [primary_name_meta(e)],
        }
        s, r = req("POST", "EntityDefinitions", body)
        print(f"[table] {e['schema']}: {'ok' if ok(s) else r}")


def deploy_columns():
    for e in ENTITIES:
        for a in e["attributes"]:
            if a["type"] == "lookup":
                continue  # created via relationship
            s, r = req("POST",
                       f"EntityDefinitions(LogicalName='{e['schema']}')/Attributes",
                       attr_meta(a))
            print(f"[column] {e['schema']}.{a['schema']}: {'ok' if ok(s) else r}")


def deploy_relationships():
    for referenced, referencing, attr in RELATIONSHIPS:
        name = f"{referenced}_{referencing}_{attr}"[:100]
        ref_disp = next(e["display"] for e in ENTITIES if e["schema"] == referenced)
        body = {
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
                "SchemaName": attr,
                "DisplayName": label(ref_disp),
                "Description": label(""),
                "RequiredLevel": {"Value": "None"},
            },
            "AssociatedMenuConfiguration": {
                "Behavior": "UseCollectionName", "Group": "Details", "Order": 10000,
            },
        }
        s, r = req("POST", "RelationshipDefinitions", body)
        print(f"[relationship] {name}: {'ok' if ok(s) else r}")


def main():
    print(f"Target: {URL}\n")
    ensure_publisher()
    ensure_solution()
    deploy_optionsets()
    deploy_entities()
    deploy_columns()
    deploy_relationships()
    print("\nDone. Open make.powerapps.com > Solutions > "
          f"{SOLUTION_DISPLAY} to verify.")


if __name__ == "__main__":
    main()
