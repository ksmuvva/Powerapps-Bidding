#!/usr/bin/env python3
"""
Generate an importable (unmanaged) Microsoft Dataverse / Power Apps solution
for the Bid Management application.

Output: solution/dist/BidManagement_1_0_0_0.zip  (import via make.powerapps.com)

The whole data model (tables, columns, choices, relationships) is declared in
the SPEC section below and rendered to classic solution XML
([Content_Types].xml, solution.xml, customizations.xml).

Run:  python3 solution/build/generate_solution.py
"""
import os
import uuid
import zipfile
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
PREFIX = "bid"                       # customization (schema) prefix -> bid_xxx
LCID = 1033                          # English (US)
VERSION = "1.0.1.0"
OPTVAL_PREFIX = 50732                # publisher option-value prefix (5 digits)
OPTVAL_BASE = OPTVAL_PREFIX * 10000  # global option base value

PUBLISHER_UNIQUE = "shreemgroup"
PUBLISHER_DISPLAY = "Shreem Group"
SOLUTION_UNIQUE = "BidManagement"
SOLUTION_DISPLAY = "Bid Management"

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "dist")
ZIP_NAME = f"{SOLUTION_UNIQUE}_{VERSION.replace('.', '_')}.zip"

# Control class ids (model-driven form controls)
CLASSID = {
    "text":     "{4273EDBD-AC1D-40d3-9FB2-095C621B552D}",
    "memo":     "{E0DECE4B-6FC8-4a8f-A065-082708572369}",
    "picklist": "{3EF39988-22BB-4f0b-BBBE-64B5A3748AEE}",
    "boolean":  "{B0C6723A-8503-4fd7-BB28-C8A06AC933C2}",
    "lookup":   "{270BD3DB-D9AF-4782-9025-509E298DEC0A}",
    "datetime": "{5B773807-9FB2-42db-97C3-7A91EFF8ADFF}",
    "int":      "{C6D124CA-7EDA-4a60-AAE0-8F0F6D293D9D}",
    "decimal":  "{C3EFE0C3-0EC6-42be-8349-CBD9079DFD8E}",
}

def guid():
    return "{" + str(uuid.uuid4()) + "}"

# --------------------------------------------------------------------------- #
# SPEC: global choice (option) sets
# --------------------------------------------------------------------------- #
GLOBAL_OPTIONSETS = {
    "bid_region": ["North East", "North West", "Yorkshire & Humber",
                   "East Midlands", "West Midlands", "East of England",
                   "London", "South East", "South West", "Scotland",
                   "Wales", "Northern Ireland", "National"],
    "bid_stage": ["Identified", "Qualifying", "Bid / No-Bid", "In Progress",
                  "Internal Review", "Submitted", "Awarded", "Lost",
                  "Withdrawn", "No-Bid"],
    "bid_source": ["Git Feed Import", "Manual Entry", "Portal", "AI Discovered"],
    "bid_score": ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High",
                  "5 - Very High"],
    "bid_recommendation": ["Bid", "No-Bid", "Review"],
    "bid_decision": ["Bid", "No-Bid"],
    "bid_taskstatus": ["Not Started", "In Progress", "Done", "Blocked"],
    "bid_doccategory": ["Tender Pack", "Clarification", "Draft Response",
                        "Final Submission", "Award Letter", "Other"],
    "bid_result": ["Won", "Lost", "Withdrawn", "No-Bid"],
    "bid_reasoncode": ["Price", "Quality", "Capability", "Late Submission",
                       "Strategic", "Other"],
}

# Assign stable option values (base + index) per global optionset.
_optionset_values = {}
for i, (osname, labels) in enumerate(GLOBAL_OPTIONSETS.items()):
    base = OPTVAL_BASE + i * 100
    _optionset_values[osname] = [(base + j, lbl) for j, lbl in enumerate(labels)]

# --------------------------------------------------------------------------- #
# SPEC: tables (entities)
# t = text, memo, int, decimal, money, date, datetime, url, email,
#     boolean, picklist (global), lookup
# --------------------------------------------------------------------------- #
ENTITIES = [
    {
        "schema": "bid_company", "display": "Company", "plural": "Companies",
        "primary": ("bid_name", "Company Name", 200),
        "attributes": [
            {"schema": "bid_code", "display": "Code", "type": "text", "len": 10},
            {"schema": "bid_active", "display": "Active", "type": "boolean", "default": 1},
        ],
    },
    {
        "schema": "bid_domain", "display": "Domain", "plural": "Domains",
        "primary": ("bid_name", "Domain Name", 200),
        "attributes": [
            {"schema": "bid_active", "display": "Active", "type": "boolean", "default": 1},
        ],
    },
    {
        "schema": "bid_buyertype", "display": "Buyer Type", "plural": "Buyer Types",
        "primary": ("bid_name", "Buyer Type", 200),
        "attributes": [
            {"schema": "bid_active", "display": "Active", "type": "boolean", "default": 1},
        ],
    },
    {
        "schema": "bid_buyer", "display": "Buyer", "plural": "Buyers",
        "primary": ("bid_name", "Buyer Name", 200),
        "attributes": [
            {"schema": "bid_buyertypeid", "display": "Buyer Type", "type": "lookup",
             "target": "bid_buyertype"},
            {"schema": "bid_region", "display": "Region", "type": "picklist",
             "optionset": "bid_region"},
            {"schema": "bid_website", "display": "Website", "type": "url"},
        ],
    },
    {
        "schema": "bid_framework", "display": "Framework", "plural": "Frameworks",
        "primary": ("bid_name", "Framework Name", 200),
        "attributes": [
            {"schema": "bid_lot", "display": "Lot", "type": "text", "len": 100},
            {"schema": "bid_ownerauthorityid", "display": "Owning Authority",
             "type": "lookup", "target": "bid_buyer"},
            {"schema": "bid_expiry", "display": "Expiry Date", "type": "date"},
        ],
    },
    {
        "schema": "bid_opportunity", "display": "Opportunity", "plural": "Opportunities",
        "primary": ("bid_title", "Opportunity Title", 300),
        "attributes": [
            {"schema": "bid_reference", "display": "Bid Reference", "type": "text", "len": 50},
            {"schema": "bid_companyid", "display": "Company", "type": "lookup",
             "target": "bid_company"},
            {"schema": "bid_domainid", "display": "Domain", "type": "lookup",
             "target": "bid_domain"},
            {"schema": "bid_buyertypeid", "display": "Buyer Type", "type": "lookup",
             "target": "bid_buyertype"},
            {"schema": "bid_buyerid", "display": "Buyer", "type": "lookup",
             "target": "bid_buyer"},
            {"schema": "bid_frameworkid", "display": "Framework", "type": "lookup",
             "target": "bid_framework"},
            {"schema": "bid_stage", "display": "Stage", "type": "picklist",
             "optionset": "bid_stage"},
            {"schema": "bid_source", "display": "Source", "type": "picklist",
             "optionset": "bid_source"},
            {"schema": "bid_estvalue", "display": "Estimated Value", "type": "decimal",
             "precision": 2},
            {"schema": "bid_durationmonths", "display": "Duration (Months)", "type": "int"},
            {"schema": "bid_externalref", "display": "External Reference", "type": "text", "len": 100},
            {"schema": "bid_publisheddate", "display": "Published Date", "type": "date"},
            {"schema": "bid_clarificationdeadline", "display": "Clarification Deadline", "type": "datetime"},
            {"schema": "bid_submissiondeadline", "display": "Submission Deadline", "type": "datetime"},
            {"schema": "bid_awarddate", "display": "Award Date", "type": "date"},
            {"schema": "bid_contractstart", "display": "Contract Start", "type": "date"},
            {"schema": "bid_summary", "display": "Summary", "type": "memo", "len": 4000},
            {"schema": "bid_aisummary", "display": "AI Summary", "type": "memo", "len": 4000},
            {"schema": "bid_aiprocessed", "display": "AI Processed", "type": "boolean", "default": 0},
        ],
    },
    {
        "schema": "bid_scorecard", "display": "Scorecard", "plural": "Scorecards",
        "primary": ("bid_name", "Scorecard Name", 200),
        "attributes": [
            {"schema": "bid_opportunityid", "display": "Opportunity", "type": "lookup",
             "target": "bid_opportunity"},
            {"schema": "bid_strategicfit", "display": "Strategic Fit", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_capability", "display": "Capability", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_competitiveness", "display": "Competitiveness", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_commercialvalue", "display": "Commercial Value", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_deliverability", "display": "Deliverability", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_winprobability", "display": "Win Probability", "type": "picklist", "optionset": "bid_score"},
            {"schema": "bid_totalscore", "display": "Total Score", "type": "int"},
            {"schema": "bid_recommendation", "display": "Recommendation", "type": "picklist", "optionset": "bid_recommendation"},
            {"schema": "bid_decision", "display": "Decision", "type": "picklist", "optionset": "bid_decision"},
            {"schema": "bid_decisiondate", "display": "Decision Date", "type": "datetime"},
            {"schema": "bid_rationale", "display": "Rationale", "type": "memo", "len": 4000},
        ],
    },
    {
        "schema": "bid_task", "display": "Bid Task", "plural": "Bid Tasks",
        "primary": ("bid_name", "Task", 300),
        "attributes": [
            {"schema": "bid_opportunityid", "display": "Opportunity", "type": "lookup", "target": "bid_opportunity"},
            {"schema": "bid_duedate", "display": "Due Date", "type": "datetime"},
            {"schema": "bid_status", "display": "Status", "type": "picklist", "optionset": "bid_taskstatus"},
            {"schema": "bid_ischecklistitem", "display": "Checklist Item", "type": "boolean", "default": 0},
            {"schema": "bid_createdbyai", "display": "Created by AI", "type": "boolean", "default": 0},
        ],
    },
    {
        "schema": "bid_document", "display": "Bid Document", "plural": "Bid Documents",
        "primary": ("bid_name", "Document Name", 300),
        "attributes": [
            {"schema": "bid_opportunityid", "display": "Opportunity", "type": "lookup", "target": "bid_opportunity"},
            {"schema": "bid_category", "display": "Category", "type": "picklist", "optionset": "bid_doccategory"},
            {"schema": "bid_url", "display": "Source / Git Path", "type": "url"},
            {"schema": "bid_version", "display": "Version", "type": "text", "len": 50},
        ],
    },
    {
        "schema": "bid_outcome", "display": "Outcome", "plural": "Outcomes",
        "primary": ("bid_name", "Outcome Name", 200),
        "attributes": [
            {"schema": "bid_opportunityid", "display": "Opportunity", "type": "lookup", "target": "bid_opportunity"},
            {"schema": "bid_result", "display": "Result", "type": "picklist", "optionset": "bid_result"},
            {"schema": "bid_awardedvalue", "display": "Awarded Value", "type": "decimal", "precision": 2},
            {"schema": "bid_winningsupplier", "display": "Winning Supplier", "type": "text", "len": 200},
            {"schema": "bid_reasoncode", "display": "Reason Code", "type": "picklist", "optionset": "bid_reasoncode"},
            {"schema": "bid_lessonslearned", "display": "Lessons Learned", "type": "memo", "len": 4000},
            {"schema": "bid_debriefreceived", "display": "Debrief Received", "type": "boolean", "default": 0},
        ],
    },
    {
        "schema": "bid_contact", "display": "Buyer Contact", "plural": "Buyer Contacts",
        "primary": ("bid_name", "Contact Name", 200),
        "attributes": [
            {"schema": "bid_buyerid", "display": "Buyer", "type": "lookup", "target": "bid_buyer"},
            {"schema": "bid_email", "display": "Email", "type": "email"},
            {"schema": "bid_phone", "display": "Phone", "type": "text", "len": 50},
            {"schema": "bid_role", "display": "Role", "type": "text", "len": 100},
        ],
    },
]

# --------------------------------------------------------------------------- #
# Derive relationships from lookup attributes
# --------------------------------------------------------------------------- #
RELATIONSHIPS = []  # (referenced_entity, referencing_entity, referencing_attr)
for ent in ENTITIES:
    for a in ent["attributes"]:
        if a["type"] == "lookup":
            RELATIONSHIPS.append((a["target"], ent["schema"], a["schema"]))

# --------------------------------------------------------------------------- #
# XML rendering helpers
# --------------------------------------------------------------------------- #
def labels(text):
    return (f'<labels><label description="{escape(text)}" languagecode="{LCID}" /></labels>')

def displaynames(text):
    return (f'<displaynames><displayname description="{escape(text)}" '
            f'languagecode="{LCID}" /></displaynames>')

def descriptions(text=""):
    return (f'<Descriptions><Description description="{escape(text)}" '
            f'languagecode="{LCID}" /></Descriptions>')

def localized_names(text):
    return (f'<LocalizedNames><LocalizedName description="{escape(text)}" '
            f'languagecode="{LCID}" /></LocalizedNames>')

def common_attr_flags(required="none", valid_create=1, valid_update=1):
    return f"""<RequiredLevel>{required}</RequiredLevel>
      <ValidForUpdateApi>{valid_update}</ValidForUpdateApi>
      <ValidForReadApi>1</ValidForReadApi>
      <ValidForCreateApi>{valid_create}</ValidForCreateApi>
      <IsCustomField>1</IsCustomField>
      <IsAuditEnabled>1</IsAuditEnabled>
      <IsSecured>0</IsSecured>
      <IntroducedVersion>{VERSION}</IntroducedVersion>
      <IsCustomizable>1</IsCustomizable>
      <IsRenameable>1</IsRenameable>
      <CanModifySearchSettings>1</CanModifySearchSettings>
      <CanModifyRequirementLevelSettings>1</CanModifyRequirementLevelSettings>
      <CanModifyAdditionalSettings>1</CanModifyAdditionalSettings>
      <SourceType>0</SourceType>
      <IsGlobalFilterEnabled>0</IsGlobalFilterEnabled>
      <IsSortableEnabled>0</IsSortableEnabled>"""

def render_primarykey(entity):
    pk = entity["schema"] + "id"
    return f"""<attribute PhysicalName="{pk}">
      <Type>primarykey</Type>
      <Name>{pk}</Name>
      <LogicalName>{pk}</LogicalName>
      <RequiredLevel>systemrequired</RequiredLevel>
      <ValidForUpdateApi>0</ValidForUpdateApi>
      <ValidForReadApi>1</ValidForReadApi>
      <ValidForCreateApi>0</ValidForCreateApi>
      <IsCustomField>1</IsCustomField>
      <IsAuditEnabled>0</IsAuditEnabled>
      <IsSecured>0</IsSecured>
      <IntroducedVersion>{VERSION}</IntroducedVersion>
      <IsCustomizable>0</IsCustomizable>
      <IsRenameable>0</IsRenameable>
      <IsValidForAdvancedFind>0</IsValidForAdvancedFind>
      <IsPrimaryId>1</IsPrimaryId>
      {displaynames(entity['display'])}
      {descriptions('Unique identifier for ' + entity['display'])}
    </attribute>"""

def render_primaryname(entity):
    schema, display, length = entity["primary"]
    return f"""<attribute PhysicalName="{schema}">
      <Type>nvarchar</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {common_attr_flags(required='none')}
      <MaxLength>{length}</MaxLength>
      <Format>text</Format>
      <IsBaseCurrency>0</IsBaseCurrency>
      <IsPrimaryName>1</IsPrimaryName>
      <ImeMode>auto</ImeMode>
      {displaynames(display)}
      {descriptions()}
    </attribute>"""

def render_attribute(entity, a):
    t = a["type"]
    schema = a["schema"]
    display = a["display"]
    flags = common_attr_flags()

    if t == "text":
        body = f"""<Type>nvarchar</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MaxLength>{a.get('len', 100)}</MaxLength>
      <Format>text</Format>
      <ImeMode>auto</ImeMode>"""
    elif t == "url":
        body = f"""<Type>nvarchar</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MaxLength>500</MaxLength>
      <Format>url</Format>
      <ImeMode>auto</ImeMode>"""
    elif t == "email":
        body = f"""<Type>nvarchar</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MaxLength>200</MaxLength>
      <Format>email</Format>
      <ImeMode>auto</ImeMode>"""
    elif t == "memo":
        body = f"""<Type>ntext</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MaxLength>{a.get('len', 2000)}</MaxLength>
      <Format>text</Format>
      <ImeMode>auto</ImeMode>"""
    elif t == "int":
        body = f"""<Type>int</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MinValue>-2147483648</MinValue>
      <MaxValue>2147483647</MaxValue>
      <Format>none</Format>
      <ImeMode>auto</ImeMode>"""
    elif t == "decimal":
        body = f"""<Type>decimal</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <MinValue>-100000000000</MinValue>
      <MaxValue>100000000000</MaxValue>
      <Precision>{a.get('precision', 2)}</Precision>
      <ImeMode>auto</ImeMode>"""
    elif t == "date":
        body = f"""<Type>datetime</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <Format>date</Format>
      <Behavior>1</Behavior>
      <CanChangeDateTimeBehavior>1</CanChangeDateTimeBehavior>
      <ImeMode>auto</ImeMode>"""
    elif t == "datetime":
        body = f"""<Type>datetime</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <Format>datetime</Format>
      <Behavior>1</Behavior>
      <CanChangeDateTimeBehavior>1</CanChangeDateTimeBehavior>
      <ImeMode>auto</ImeMode>"""
    elif t == "boolean":
        default = a.get("default", 0)
        true_val = OPTVAL_BASE + 9000
        false_val = OPTVAL_BASE + 9001
        body = f"""<Type>bit</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <DefaultValue>{default}</DefaultValue>
      <Format>none</Format>
      <optionset Name="{entity['schema']}_{schema}">
        <OptionSetType>bit</OptionSetType>
        <IsGlobal>0</IsGlobal>
        <IsCustomizable>1</IsCustomizable>
        <introducedversion>{VERSION}</introducedversion>
        {displaynames(display)}
        {descriptions()}
        <options>
          <option value="1"><labels><label description="Yes" languagecode="{LCID}" /></labels></option>
          <option value="0"><labels><label description="No" languagecode="{LCID}" /></labels></option>
        </options>
        <falseoption>0</falseoption>
        <trueoption>1</trueoption>
      </optionset>"""
    elif t == "picklist":
        osname = a["optionset"]
        body = f"""<Type>picklist</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <Format>none</Format>
      <optionset Name="{osname}">
        <OptionSetType>picklist</OptionSetType>
        <IsGlobal>1</IsGlobal>
      </optionset>"""
    elif t == "lookup":
        body = f"""<Type>lookup</Type>
      <Name>{schema}</Name>
      <LogicalName>{schema}</LogicalName>
      {flags}
      <LookupStyle>single</LookupStyle>
      <LookupTypes />
      <Format>none</Format>"""
    else:
        raise ValueError(f"unknown type {t}")

    return f"""<attribute PhysicalName="{schema}">
      {body}
      {displaynames(display)}
      {descriptions()}
    </attribute>"""


def render_global_optionset(name, values):
    opts = "\n".join(
        f'        <option value="{v}">{labels(lbl)}</option>'
        for v, lbl in values
    )
    return f"""  <optionset Name="{name}" localizedName="{name}">
    <OptionSetType>picklist</OptionSetType>
    <IsGlobal>1</IsGlobal>
    <IsCustomizable>1</IsCustomizable>
    <introducedversion>{VERSION}</introducedversion>
    {displaynames(name.replace('bid_', '').replace('_', ' ').title())}
    {descriptions()}
    <options>
{opts}
    </options>
  </optionset>"""


def render_form(entity):
    """Minimal but valid main form with all custom fields in one section."""
    formid = guid()
    schema = entity["schema"]
    pname = entity["primary"][0]

    def control(field, classid):
        cid = guid()
        return (f'<cell id="{guid()}"><control id="{field}" '
                f'classid="{classid}" datafieldname="{field}" /></cell>')

    rows = [f'<row><cell id="{guid()}"><labels>'
            f'<label description="{escape(entity["primary"][1])}" languagecode="{LCID}" />'
            f'</labels><control id="{pname}" classid="{CLASSID["text"]}" '
            f'datafieldname="{pname}" /></cell></row>']
    for a in entity["attributes"]:
        cls = CLASSID.get(a["type"], CLASSID["text"])
        rows.append(
            f'<row><cell id="{guid()}"><labels>'
            f'<label description="{escape(a["display"])}" languagecode="{LCID}" />'
            f'</labels><control id="{a["schema"]}" classid="{cls}" '
            f'datafieldname="{a["schema"]}" /></cell></row>')
    rows_xml = "\n".join(rows)

    return f"""<FormXml>
      <forms type="main">
        <systemform>
          <formid>{formid}</formid>
          <IsCustomizable>1</IsCustomizable>
          <form>
            <tabs>
              <tab name="general" id="{guid()}" IsUserDefined="0" associatedentitytypecode="">
                <labels><label description="General" languagecode="{LCID}" /></labels>
                <columns>
                  <column width="100%">
                    <sections>
                      <section name="details" id="{guid()}" IsUserDefined="0" showlabel="true" showbar="false" columns="1" labelwidth="115" celllabelalignment="Left" celllabelposition="Left">
                        <labels><label description="Details" languagecode="{LCID}" /></labels>
                        <rows>
{rows_xml}
                        </rows>
                      </section>
                    </sections>
                  </column>
                </columns>
              </tab>
            </tabs>
          </form>
          <LocalizedNames><LocalizedName description="Information" languagecode="{LCID}" /></LocalizedNames>
        </systemform>
      </forms>
    </FormXml>"""


def render_savedquery(entity):
    sqid = guid()
    schema = entity["schema"]
    pname = entity["primary"][0]
    pk = schema + "id"
    # build a few columns: primary name + first 3 simple fields
    extra = [a for a in entity["attributes"] if a["type"] in
             ("text", "picklist", "lookup", "date", "datetime", "boolean")][:4]
    cols = [f'<cell name="{pname}" width="300" />']
    cols += [f'<cell name="{a["schema"]}" width="150" />' for a in extra]
    cells = "\n            ".join(cols)
    fetch_attrs = f'<attribute name="{pname}" />\n          ' + "\n          ".join(
        f'<attribute name="{a["schema"]}" />' for a in extra)
    return f"""<SavedQueries>
      <savedqueries>
        <savedquery>
          <IsCustomizable>1</IsCustomizable>
          <CanBeDeleted>0</CanBeDeleted>
          <isquickfindquery>0</isquickfindquery>
          <isprivate>0</isprivate>
          <isdefault>1</isdefault>
          <returnedtypecode>{schema}</returnedtypecode>
          <savedqueryid>{sqid}</savedqueryid>
          <layoutxml>
            <grid name="resultset" object="1" jump="{pname}" select="1" icon="1" preview="1">
              <row name="result" id="{pk}">
            {cells}
              </row>
            </grid>
          </layoutxml>
          <fetchxml>
            <fetch version="1.0" mapping="logical" returntotalrecordcount="true" no-lock="false">
              <entity name="{schema}">
                {fetch_attrs}
                <order attribute="{pname}" descending="false" />
              </entity>
            </fetch>
          </fetchxml>
          <LocalizedNames><LocalizedName description="Active {escape(entity['plural'])}" languagecode="{LCID}" /></LocalizedNames>
          <querytype>0</querytype>
        </savedquery>
      </savedqueries>
    </SavedQueries>"""


def render_entity(entity):
    schema = entity["schema"]
    attrs = [render_primarykey(entity), render_primaryname(entity)]
    attrs += [render_attribute(entity, a) for a in entity["attributes"]]
    attrs_xml = "\n    ".join(attrs)
    entity_set = schema + "es" if entity["plural"].lower().endswith("s") else schema + "s"

    return f"""<Entity>
    <Name LocalizedName="{escape(entity['display'])}" OriginalName="{escape(entity['display'])}">{schema}</Name>
    <EntityInfo>
      <entity Name="{schema}">
        {localized_names(entity['display'])}
        <LocalizedCollectionNames><LocalizedCollectionName description="{escape(entity['plural'])}" languagecode="{LCID}" /></LocalizedCollectionNames>
        {descriptions(entity['display'] + ' record')}
        <attributes>
    {attrs_xml}
        </attributes>
        <EntitySetName>{entity_set}</EntitySetName>
        <IsDuplicateCheckSupported>1</IsDuplicateCheckSupported>
        <IsBusinessProcessEnabled>0</IsBusinessProcessEnabled>
        <IsRenameable>1</IsRenameable>
        <IsCustomizable>1</IsCustomizable>
        <IsActivity>0</IsActivity>
        <IsAvailableOffline>1</IsAvailableOffline>
        <IsAuditEnabled>1</IsAuditEnabled>
        <IsValidForQueue>0</IsValidForQueue>
        <IsConnectionsEnabled>0</IsConnectionsEnabled>
        <IsDocumentManagementEnabled>0</IsDocumentManagementEnabled>
        <IsMailMergeEnabled>0</IsMailMergeEnabled>
        <IsVisibleInMobile>1</IsVisibleInMobile>
        <IsVisibleInMobileClient>1</IsVisibleInMobileClient>
        <OwnershipTypeMask>UserOwned</OwnershipTypeMask>
        <IsMapiGridEnabled>1</IsMapiGridEnabled>
        <PrimaryNameAttribute>{entity['primary'][0]}</PrimaryNameAttribute>
        <PrimaryIdAttribute>{schema}id</PrimaryIdAttribute>
      </entity>
    </EntityInfo>
    {render_form(entity)}
    {render_savedquery(entity)}
  </Entity>"""


def render_relationship(referenced, referencing, attr):
    name = f"{referenced}_{referencing}_{attr}"
    if len(name) > 100:
        name = name[:100]
    ref_disp = next(e["display"] for e in ENTITIES if e["schema"] == referenced)
    return f"""  <EntityRelationship Name="{name}">
    <EntityRelationshipType>OneToMany</EntityRelationshipType>
    <IsCustomizable>1</IsCustomizable>
    <IntroducedVersion>{VERSION}</IntroducedVersion>
    <IsHierarchical>0</IsHierarchical>
    <ReferencingEntityName>{referencing}</ReferencingEntityName>
    <ReferencedEntityName>{referenced}</ReferencedEntityName>
    <CascadeAssign>NoCascade</CascadeAssign>
    <CascadeDelete>RemoveLink</CascadeDelete>
    <CascadeReparent>NoCascade</CascadeReparent>
    <CascadeShare>NoCascade</CascadeShare>
    <CascadeUnshare>NoCascade</CascadeUnshare>
    <CascadeMerge>NoCascade</CascadeMerge>
    <CascadeRollupView>NoCascade</CascadeRollupView>
    <IsValidForAdvancedFind>1</IsValidForAdvancedFind>
    <ReferencingAttributeName>{attr}</ReferencingAttributeName>
    <RelationshipDescription>{localized_names(ref_disp)}</RelationshipDescription>
    <EntityRelationshipRoles>
      <EntityRelationshipRole>
        <NavPaneDisplayOption>UseCollectionName</NavPaneDisplayOption>
        <NavPaneArea>Details</NavPaneArea>
        <NavPaneOrder>10000</NavPaneOrder>
        <NavigationPropertyName>{name}</NavigationPropertyName>
        <RelationshipRoleType>1</RelationshipRoleType>
      </EntityRelationshipRole>
      <EntityRelationshipRole>
        <NavigationPropertyName>{name}</NavigationPropertyName>
        <RelationshipRoleType>0</RelationshipRoleType>
      </EntityRelationshipRole>
    </EntityRelationshipRoles>
  </EntityRelationship>"""


# --------------------------------------------------------------------------- #
# Assemble files
# --------------------------------------------------------------------------- #
def build_customizations():
    entities_xml = "\n  ".join(render_entity(e) for e in ENTITIES)
    rels_xml = "\n".join(
        render_relationship(ref, ing, attr) for ref, ing, attr in RELATIONSHIPS)
    optionsets_xml = "\n".join(
        render_global_optionset(n, v) for n, v in _optionset_values.items())

    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2.0.0" SolutionPackageVersion="9.2" languagecode="{LCID}" generatedBy="ClaudeCode" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Entities>
  {entities_xml}
  </Entities>
  <Roles />
  <Workflows />
  <FieldSecurityProfiles />
  <Templates />
  <EntityMaps />
  <EntityRelationships>
{rels_xml}
  </EntityRelationships>
  <OrganizationSettings />
  <optionsets>
{optionsets_xml}
  </optionsets>
  <CustomControls />
  <SolutionPluginAssemblies />
  <EntityDataProviders />
  <Languages>
    <Language>{LCID}</Language>
  </Languages>
</ImportExportXml>"""


def build_solution_xml():
    # Root components: entities (type 1) + global optionsets (type 9)
    ent_components = "\n      ".join(
        f'<RootComponent type="1" schemaName="{e["schema"]}" behavior="0" />'
        for e in ENTITIES)
    os_components = "\n      ".join(
        f'<RootComponent type="9" schemaName="{n}" behavior="0" />'
        for n in _optionset_values.keys())

    return f"""<?xml version="1.0" encoding="utf-8"?>
<ImportExportXml version="9.2.0.0" SolutionPackageVersion="9.2" languagecode="{LCID}" generatedBy="ClaudeCode" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <SolutionManifest>
    <UniqueName>{SOLUTION_UNIQUE}</UniqueName>
    <LocalizedNames>
      <LocalizedName description="{SOLUTION_DISPLAY}" languagecode="{LCID}" />
    </LocalizedNames>
    <Descriptions>
      <Description description="Bid management solution for the Shreem Group companies (Shreem Infotech, adi3 Ltd, MVRIT, ALPs Agility)." languagecode="{LCID}" />
    </Descriptions>
    <Version>{VERSION}</Version>
    <Managed>0</Managed>
    <Publisher>
      <UniqueName>{PUBLISHER_UNIQUE}</UniqueName>
      <LocalizedNames>
        <LocalizedName description="{PUBLISHER_DISPLAY}" languagecode="{LCID}" />
      </LocalizedNames>
      <Descriptions>
        <Description description="{PUBLISHER_DISPLAY}" languagecode="{LCID}" />
      </Descriptions>
      <EMailAddress xsi:nil="true"></EMailAddress>
      <SupportingWebsiteUrl xsi:nil="true"></SupportingWebsiteUrl>
      <CustomizationPrefix>{PREFIX}</CustomizationPrefix>
      <CustomizationOptionValuePrefix>{OPTVAL_PREFIX}</CustomizationOptionValuePrefix>
      <Addresses>
        <Address>
          <AddressNumber>1</AddressNumber>
          <AddressTypeCode>1</AddressTypeCode>
          <City xsi:nil="true"></City>
          <County xsi:nil="true"></County>
          <Country xsi:nil="true"></Country>
          <Fax xsi:nil="true"></Fax>
          <FreightTermsCode xsi:nil="true"></FreightTermsCode>
          <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
          <Latitude xsi:nil="true"></Latitude>
          <Line1 xsi:nil="true"></Line1>
          <Line2 xsi:nil="true"></Line2>
          <Line3 xsi:nil="true"></Line3>
          <Longitude xsi:nil="true"></Longitude>
          <Name xsi:nil="true"></Name>
          <PostalCode xsi:nil="true"></PostalCode>
          <PostOfficeBox xsi:nil="true"></PostOfficeBox>
          <PrimaryContactName xsi:nil="true"></PrimaryContactName>
          <ShippingMethodCode xsi:nil="true"></ShippingMethodCode>
          <StateOrProvince xsi:nil="true"></StateOrProvince>
          <Telephone1 xsi:nil="true"></Telephone1>
          <Telephone2 xsi:nil="true"></Telephone2>
          <Telephone3 xsi:nil="true"></Telephone3>
          <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
          <UPSZone xsi:nil="true"></UPSZone>
          <UTCOffset xsi:nil="true"></UTCOffset>
          <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
        </Address>
        <Address>
          <AddressNumber>2</AddressNumber>
          <AddressTypeCode>1</AddressTypeCode>
          <City xsi:nil="true"></City>
          <County xsi:nil="true"></County>
          <Country xsi:nil="true"></Country>
          <Fax xsi:nil="true"></Fax>
          <FreightTermsCode xsi:nil="true"></FreightTermsCode>
          <ImportSequenceNumber xsi:nil="true"></ImportSequenceNumber>
          <Latitude xsi:nil="true"></Latitude>
          <Line1 xsi:nil="true"></Line1>
          <Line2 xsi:nil="true"></Line2>
          <Line3 xsi:nil="true"></Line3>
          <Longitude xsi:nil="true"></Longitude>
          <Name xsi:nil="true"></Name>
          <PostalCode xsi:nil="true"></PostalCode>
          <PostOfficeBox xsi:nil="true"></PostOfficeBox>
          <PrimaryContactName xsi:nil="true"></PrimaryContactName>
          <ShippingMethodCode xsi:nil="true"></ShippingMethodCode>
          <StateOrProvince xsi:nil="true"></StateOrProvince>
          <Telephone1 xsi:nil="true"></Telephone1>
          <Telephone2 xsi:nil="true"></Telephone2>
          <Telephone3 xsi:nil="true"></Telephone3>
          <TimeZoneRuleVersionNumber xsi:nil="true"></TimeZoneRuleVersionNumber>
          <UPSZone xsi:nil="true"></UPSZone>
          <UTCOffset xsi:nil="true"></UTCOffset>
          <UTCConversionTimeZoneCode xsi:nil="true"></UTCConversionTimeZoneCode>
        </Address>
      </Addresses>
    </Publisher>
    <RootComponents>
      {ent_components}
      {os_components}
    </RootComponents>
    <MissingDependencies />
  </SolutionManifest>
</ImportExportXml>"""


CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="text/xml" /></Types>"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = {
        "solution.xml": build_solution_xml(),
        "customizations.xml": build_customizations(),
        "[Content_Types].xml": CONTENT_TYPES,
    }
    # write raw files for inspection
    src_dir = os.path.join(OUT_DIR, "src")
    os.makedirs(src_dir, exist_ok=True)
    for name, content in files.items():
        with open(os.path.join(src_dir, name), "w", encoding="utf-8") as f:
            f.write(content)

    zip_path = os.path.join(OUT_DIR, ZIP_NAME)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)

    print(f"Entities:        {len(ENTITIES)}")
    print(f"Global choices:  {len(GLOBAL_OPTIONSETS)}")
    print(f"Relationships:   {len(RELATIONSHIPS)}")
    print(f"Solution zip:    {zip_path}")


if __name__ == "__main__":
    main()
