#!/usr/bin/env python3
"""
Create the Bid Management application views (saved queries) in Dataverse via the
supported Web API. Run this AFTER deploy_via_webapi.py (the tables must exist)
and after loading the buyer-type seed data (for the buyer-lens views).

Creates public views on the Opportunity table:
  - All Open Bids / My Open Bids / At-Risk (Due This Week)
  - Submitted Bids / Won Bids / Lost Bids
  - Buyer lenses: NHS Bids / MOD Bids / Council Bids

Then publishes customizations. The model-driven app shell, site map, business
process flow and dashboards are assembled in the maker portal — see
docs/07-app-build.md (a 10-minute runbook).

Usage (same auth options as deploy_via_webapi.py):
  pip install msal
  python3 solution/build/deploy_app.py --url https://YOURORG.crm11.dynamics.com
  python3 solution/build/deploy_app.py --url <url> --dry-run
"""
import argparse
import os
import sys

from deploy_via_webapi import Client, get_token
from generate_solution import _optionset_values

ENTITY = "bid_opportunity"
PRIMARY = "bid_title"
PK = "bid_opportunityid"

# stage label -> option value
STAGE = {lbl: val for val, lbl in _optionset_values["bid_stage"]}
OPEN_STAGES = ["Identified", "Qualifying", "Bid / No-Bid",
               "In Progress", "Internal Review"]
OPEN_VALUES = [STAGE[s] for s in OPEN_STAGES]

# Columns shown in every view (logical name, width)
COLUMNS = [
    (PRIMARY, 300), ("bid_reference", 120), ("bid_companyid", 150),
    ("bid_buyertypeid", 150), ("bid_stage", 140), ("bid_estvalue", 120),
    ("bid_submissiondeadline", 170),
]


def open_condition():
    vals = "".join(f"<value>{v}</value>" for v in OPEN_VALUES)
    return f'<condition attribute="bid_stage" operator="in">{vals}</condition>'


def fetchxml(filter_inner="", link=""):
    attrs = "".join(f'<attribute name="{c}" />' for c, _ in COLUMNS)
    flt = f'<filter type="and">{filter_inner}</filter>' if filter_inner else ""
    return (f'<fetch version="1.0" mapping="logical" returntotalrecordcount="true">'
            f'<entity name="{ENTITY}">{attrs}<attribute name="{PK}" />'
            f'<order attribute="bid_submissiondeadline" descending="false" />'
            f'{flt}{link}</entity></fetch>')


def lens_link(buyertype_name):
    return (f'<link-entity name="bid_buyertype" from="bid_buyertypeid" '
            f'to="bid_buyertypeid" alias="bt" link-type="inner">'
            f'<filter><condition attribute="bid_name" operator="eq" '
            f'value="{buyertype_name}" /></filter></link-entity>')


def layoutxml(otc):
    cells = "".join(f'<cell name="{c}" width="{w}" />' for c, w in COLUMNS)
    return (f'<grid name="resultset" object="{otc}" jump="{PRIMARY}" select="1" '
            f'icon="1" preview="1"><row name="result" id="{PK}">{cells}'
            f'</row></grid>')


def views():
    return [
        ("All Open Bids", fetchxml(open_condition())),
        ("My Open Bids",
         fetchxml(open_condition() +
                  '<condition attribute="ownerid" operator="eq-userid" />')),
        ("At-Risk - Due This Week",
         fetchxml(open_condition() +
                  '<condition attribute="bid_submissiondeadline" '
                  'operator="next-seven-days" />')),
        ("Submitted Bids",
         fetchxml(f'<condition attribute="bid_stage" operator="eq" '
                  f'value="{STAGE["Submitted"]}" />')),
        ("Won Bids",
         fetchxml(f'<condition attribute="bid_stage" operator="eq" '
                  f'value="{STAGE["Awarded"]}" />')),
        ("Lost Bids",
         fetchxml(f'<condition attribute="bid_stage" operator="eq" '
                  f'value="{STAGE["Lost"]}" />')),
        ("NHS Bids", fetchxml(link=lens_link("NHS"))),
        ("MOD Bids", fetchxml(link=lens_link("MOD"))),
        ("Council Bids", fetchxml(link=lens_link("Local Council"))),
    ]


def get_otc(c):
    if c.dry_run:
        return 10000
    s, r = c.req("GET",
                 f"EntityDefinitions(LogicalName='{ENTITY}')?$select=ObjectTypeCode")
    if s != 200:
        sys.exit(f"Could not read ObjectTypeCode for {ENTITY}: {s} {r}")
    return r["ObjectTypeCode"]


def main():
    ap = argparse.ArgumentParser(description="Create Bid Management views.")
    ap.add_argument("--url", default=os.environ.get("DATAVERSE_URL", ""))
    ap.add_argument("--auth", choices=["device", "az", "token"], default="device")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.url:
        sys.exit("Provide --url or set DATAVERSE_URL.")

    token = "" if args.dry_run else get_token(args.auth, args.url.rstrip("/"))
    c = Client(args.url, token, dry_run=args.dry_run)

    print(f"\nTarget: {args.url}\n")
    if not args.dry_run:
        s, r = c.req("GET", "WhoAmI")
        if s != 200:
            sys.exit(f"WhoAmI failed: {s} {r}")
        print(f"Connected. UserId: {r.get('UserId')}\n")
    else:
        print("DRY RUN — no changes will be made.\n")

    otc = get_otc(c)
    layout = layoutxml(otc)

    print("Views (Opportunity)")
    for name, fx in views():
        c.write(name, "savedqueries", {
            "name": name,
            "description": f"{name} - Bid Management",
            "returnedtypecode": ENTITY,
            "fetchxml": fx,
            "layoutxml": layout,
            "querytype": 0,
            "isdefault": False,
        })

    if not args.dry_run:
        print("\nPublishing customizations...")
        s, r = c.req("POST", "PublishAllXml")
        print("  ✓ published" if s in (200, 204) else f"  ✗ publish: {s} {r}")

    print(f"\nSummary: {c.created} created/ok, {c.skipped} skipped, {c.failed} failed")
    print("Next: build the app shell + dashboards per docs/07-app-build.md")
    sys.exit(1 if c.failed else 0)


if __name__ == "__main__":
    main()
