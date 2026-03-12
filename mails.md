---
description: Open email search interface
---

You are starting an email search session. Follow these steps exactly.

## Step 1 — Check tools
If `thunderbird-email` tools are not available, stop and say:
"Not available on mobile app. This command requires Claude Desktop with the Thunderbird MCP running."

## Step 2 — Output the link immediately (before any tool calls)

**Do this first, before making any tool calls.** Output the reply text now so the user sees the link right away while setup continues in the background:
- If the user provided **no arguments**: output only the link.
- If the user provided **arguments** (topic, date, keyword): output the link + one sentence summarising what will be pre-filled, based on what the user said (you can infer this without tool calls).

Link: `[Open Email Search](http://localhost:8080/mails_index.html)`

Then immediately branch based on whether the user included a task.

---

## Path A — No task (user typed only `/mails`)

### A1 — Read cache + start server (in parallel, same message)

**Account cache** (`~\.claude\data\mails_accounts.json`):
- If exists: read with the built-in Read tool. Use `accounts` + `lastChecked`. Skip `discoverOnly`.
- If missing: call `thunderbird-email:run_fetch_emails` with `discoverOnly: true`, then write result to cache via `mcp__Desktop_Commander__write_file`.

**Server start** (same parallel batch):
- command: `pythonw.exe "$env:USERPROFILE\.claude\skills\chrome-artifact\serve.py"`
- timeout_ms: `200`
- Silently exits if port already in use — always safe to call.

### A2 — Write config

Determine default params:
- **startDate**: today minus 10 days (YYYY-MM-DD)
- **endDate**: today
- **keyword**: empty
- **selected**: `true` if email contains `"s@o"` or `"s@h"`, else `false`
- **defaultCheckedFolders**: INBOX and Sent

Write `mails_config.js` via `mcp__Desktop_Commander__write_file`:
- path: `~\.claude\skills\chrome-artifact\mails_config.js`
- content: `window.EMAIL_CONFIG = <JSON.stringify(config)>;`

Config shape:
```json
{
  "_version": "email-YYYYMMDD-XXXX",
  "startDate": "<YYYY-MM-DD>",
  "endDate":   "<YYYY-MM-DD>",
  "keyword":   "<string>",
  "lastChecked": "<ISO timestamp from cache>",
  "accounts": [
    {
      "name": "<email>",
      "displayName": "<email>",
      "selected": true|false,
      "folders": ["INBOX", "Sent", ...],
      "defaultCheckedFolders": ["INBOX", "Sent"]
    }
  ]
}
```
Generate `_version` as `email-` + today (YYYYMMDD) + `-` + 4 random alphanumeric chars.

**Wait for the user's next message.** They will almost always send a task straight away — do not ask clarifying questions, just act on it.

---

## Path B — User included a task (search, summarise, date range, etc.)

The user wants results immediately. The artifact setup is secondary.

### B1 — Read cache

Read `~\.claude\data\mails_accounts.json` to get the account list.
- If missing: call `thunderbird-email:run_fetch_emails` with `discoverOnly: true` and write the cache.

### B2 — Determine search params and search

From the user's message + cache accounts, build:
- **accountFolders**: selected accounts → INBOX + Sent (or as implied by the user)
- **dateFrom / dateTo**: inferred from message, or default to today minus 10 days / today
- **keyword**: any obvious search term from the message

Call `thunderbird-email:run_fetch_emails` with those params. Present the results. Use stage 2 (full body) as needed to fulfil the task.

### B3 — Start server + write config (in parallel, after results are delivered)

Once results are presented, issue both in the same message:
- Start server: `mcp__Desktop_Commander__start_process` (same as Path A, timeout_ms: `200`)
- Write `mails_config.js` reflecting the date range / keyword used in the search, so the artifact opens pre-filled if the user clicks the link.

---

## When the user asks to search

1. Read `~\.claude\skills\chrome-artifact\mails_state.json` using `mcp__Desktop_Commander__start_process` with command `Get-Content "$env:USERPROFILE\.claude\skills\chrome-artifact\mails_state.json" -Raw` (timeout_ms: 5000). Parse the JSON from the output.
2. Build fetch parameters from the state object:
   - `accountFolders`: object mapping each account (where `state.accounts[name] === true`) to the list of its folders where `state.folders[name][folder] === true`. Only include checked accounts and folders.
   - `dateFrom`: `state.startDate`
   - `dateTo`: `state.endDate`
   - `keyword`: `state.keyword` (omit if empty or blank)

**Fallback** (if file missing or unreadable): use the config defaults — selected accounts, INBOX+Sent folders, date range from the last written config.

3. Call `thunderbird-email:run_fetch_emails` with those parameters.
4. Continue with the email search workflow (stage 1 headers, then stage 2 full body as needed).

---

## When the user specifies new filters from chat (dates, keyword, accounts)

1. Read `mails_state.json` using `Get-Content` (see "When the user asks to search") to get the current state and check `state.open`.
2. Build a pending object with only the changed fields (e.g. `{"startDate":"2026-03-01","endDate":"2026-03-05"}`).
3. **If `state.open` is `true`**: merge `_pending: <pending object>` into the current state and write the whole thing back to `~\.claude\skills\chrome-artifact\mails_state.json` via `mcp__Desktop_Commander__write_file`. The artifact will pick it up within ~3 seconds and merge it into its displayed state.
4. **If `state.open` is `false`** (or file missing): rewrite `mails_config.js` with the updated values and a new `_version`, so the next open shows the correct defaults.
5. Confirm to the user what was updated.
