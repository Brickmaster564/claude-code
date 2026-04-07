# Tool Capability Map

Quick-reference for mapping tasks to tools. Check here before concluding any capability is unavailable.

## Local Scripts (tools/)

| Tool | Capabilities |
|---|---|
| `gdocs.py` | Google Docs: get, create-doc, duplicate, replace, batch-replace, write-at, share, upload-md. Drive: list-folder, search-folder, create-folder, move |
| `gmail.py` | Send email, read messages, search inbox |
| `gcal.py` | Google Calendar events and scheduling |
| `slack.py` | Send, reply, read-thread, list-channels, find-channel, find-user. Supports `--workspace cn` or `--workspace nalu` |
| `instantly.py` | List leads, add leads, campaign management |
| `lemlist.py` | Add leads, list campaigns |
| `apify.py` | Scrape LinkedIn profiles/comments, Instagram profiles/related, Twitter/X |
| `meta_ads.py` | Meta Ads campaign management |
| `meta_report.py` | Meta Ads performance reporting |
| `higgsfield.py` | Kie.ai image generation |
| `millionverifier.py` | Email verification (primary) |
| `bounceban.py` | Email verification (secondary/risky) |
| `quickbooks.py` | QuickBooks accounting |
| `revolut.py` | Revolut banking |
| `cashflow_sync.py` | Cashflow synchronization |

All support `--help`. Google tools support `--account cn` (default) or `--account nalu`.

## MCP Integrations (Deferred, load via ToolSearch)

| Integration | Key tools | Notes |
|---|---|---|
| Airtable | list_bases, list_tables, get_schema, list/create/update_records | Preferred over API key |
| Apollo | contacts search/create/update, companies, enrichment | Use MCP, not API key |
| Gmail MCP | search_messages, read_message, create_draft | Supplements local tool |
| Google Calendar MCP | authenticate + calendar operations | Supplements local tool |
| Slack MCP | send/read messages, search channels/users, canvases | Posts as Jasper (use bot for notifications) |
| Notion | search, create/update pages, databases, comments | |
| Asana | authenticate + task management | |

## Built-in Deferred Tools

| Tool | Purpose |
|---|---|
| WebSearch | Search the web |
| WebFetch | Fetch web page content |
| TodoWrite | Task tracking within conversations |
| CronCreate/Delete/List | Scheduled task management |
