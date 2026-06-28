# 09 — MCP Servers

The Bid Management AI agents (see [04-ai-agents.md](04-ai-agents.md)) are built
on the **Claude Code SDK**. This repo ships a project-scoped MCP configuration —
[`.mcp.json`](../.mcp.json) at the repo root — so every agent and contributor
gets the same catalogue of Model Context Protocol (MCP) servers.

## How it works

- Claude Code automatically discovers `.mcp.json` in the project root. On first
  run it asks you to **approve** the project's MCP servers (a security
  prompt) before any of them start.
- Credentials are **not** hard-coded. Each server reads `${VAR}` placeholders
  that resolve from your environment. Copy [`.env.example`](../.env.example) to
  `.env`, fill in only the servers you need, and load it before launching
  Claude Code (e.g. `set -a; source .env; set +a`).
- Every server is **optional**. If you do not want one, delete its entry from
  `.mcp.json` (or just leave its credentials blank and skip approving it).
- Transports used here:
  - **stdio** — launched locally via `npx` (Node) or `uvx` (Python/uv). Requires
    Node.js 18+ and/or [uv](https://docs.astral.sh/uv/) on the machine running
    the agent.
  - **http / sse** — hosted remote servers; Claude Code handles OAuth where a
    token is not supplied.

> Package/transport details below reflect each project's published guidance at
> time of writing. Pin or update versions to suit your environment, and verify
> the launch command against the upstream README before relying on it in
> production.

## Catalogue

### Core / docs

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `github` | github/github-mcp-server | http (hosted) | `GITHUB_MCP_PAT` |
| `context7` | upstash/context7 | http (hosted) | `CONTEXT7_API_KEY` (optional) |
| `deepwiki` | deepwiki.com | sse (hosted) | — |
| `huggingface` | huggingface.co/mcp | http (hosted) | `HF_TOKEN` |

### Vector DB / data

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `chroma` | chroma-core/chroma-mcp | stdio (uvx) | `CHROMA_DATA_DIR` |
| `qdrant` | qdrant/mcp-server-qdrant | stdio (uvx) | `QDRANT_URL`, `QDRANT_API_KEY` |
| `pinecone` | pinecone-io/pinecone-mcp | stdio (npx) | `PINECONE_API_KEY` |
| `mem0` | mem0ai/mem0-mcp | stdio (uvx/git) | `MEM0_API_KEY` |
| `supabase` | supabase-community/supabase-mcp | stdio (npx) | `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_REF` |
| `postgres` | crystaldba/postgres-mcp | stdio (uvx) | `DATABASE_URI` |

### Observability / web

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `langfuse` | langfuse/mcp-server-langfuse | stdio (npx) | `LANGFUSE_*` keys |
| `phoenix` | Arize-ai/phoenix | stdio (npx) | `PHOENIX_BASE_URL`, `PHOENIX_API_KEY` |
| `firecrawl` | firecrawl/firecrawl-mcp-server | stdio (npx) | `FIRECRAWL_API_KEY` |
| `exa` | exa-labs/exa-mcp-server | stdio (npx) | `EXA_API_KEY` |
| `apify` | apify/actors-mcp-server | stdio (npx) | `APIFY_TOKEN` |
| `sentry` | getsentry/sentry-mcp | http (hosted) | OAuth |
| `zapier` | mcp.zapier.com | http (hosted) | `ZAPIER_MCP_URL` |

### Sandboxes / browsers

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `e2b` | e2b-dev/mcp-server | stdio (npx) | `E2B_API_KEY` |
| `playwright` | microsoft/playwright-mcp | stdio (npx) | — |
| `chrome-devtools` | ChromeDevTools/chrome-devtools-mcp | stdio (npx) | — |

### Reasoning / thinking

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `sequential-thinking` | modelcontextprotocol/servers · sequentialthinking | stdio (npx) | — |
| `clear-thought` | waldzellai/clearthought-onepointfive | stdio (npx) | — |
| `mcp-reasoner` | Jacck/mcp-reasoner | stdio (npx) | — |
| `think-mcp` | Rai220/think-mcp | stdio (uvx) | — |
| `mas-sequential-thinking` | FradSer/mcp-server-mas-sequential-thinking | stdio (uvx/git) | `ANTHROPIC_API_KEY` |

### Memory / knowledge graph

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `memory` | modelcontextprotocol/servers · memory | stdio (npx) | `MEMORY_FILE_PATH` |
| `mem0` | mem0ai/mem0-mcp | _(see Vector DB)_ | `MEM0_API_KEY` |
| `graphiti` | getzep/graphiti | stdio (uvx/git) | Neo4j + `OPENAI_API_KEY` |
| `cognee` | topoteretes/cognee | stdio (uvx/git) | `OPENAI_API_KEY` |
| `letta` | letta-ai/letta | stdio (npx) | `LETTA_BASE_URL`, `LETTA_API_KEY` |
| `cipher` | campfirein/cipher | stdio (npx) | `ANTHROPIC_API_KEY` |

### Code / context

| Server | Source | Transport | Needs |
| ------ | ------ | --------- | ----- |
| `context7` | upstash/context7 | _(see Core)_ | `CONTEXT7_API_KEY` (optional) |
| `claude-context` | zilliztech/claude-context | stdio (npx) | `OPENAI_API_KEY`, `MILVUS_TOKEN` |
| `serena` | oraios/serena | stdio (uvx/git) | — |
| `repomix` | yamadashy/repomix | stdio (npx) | — |
| `deepwiki` | deepwiki.com | _(see Core)_ | — |

> `context7`, `mem0`, and `deepwiki` appear in more than one category in the
> source list; each is configured once in `.mcp.json` and reused.

## Recommended starting set

You do not need all of these at once. For the bid-management agents, a sensible
first cut is:

- **`github`**, **`context7`**, **`microsoft_docs`** equivalents — grounding in
  code and Power Platform docs.
- **`firecrawl`** / **`exa`** — tender and buyer research (Research agent).
- **`memory`** or **`mem0`** — durable agent memory across runs.
- **`serena`** / **`repomix`** — repo-aware code context.
- **`sequential-thinking`** — structured multi-step reasoning for qualification.

Add the vector-DB and observability servers as the platform matures.

## Security notes

- The hosted GitHub MCP server here is scoped by the PAT you supply — prefer a
  fine-grained token limited to this repo.
- `supabase` and `postgres` are configured **read-only / restricted** by
  default in `.mcp.json`; widen access deliberately, not by accident.
- MCP servers run with your local privileges. Only approve servers you trust,
  and review `.mcp.json` changes in PRs the same way you would any dependency.
