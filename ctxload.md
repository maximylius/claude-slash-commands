---
description: Restore a saved conversation context from Notion into the current session
---

## Step 1: Fetch contexts

`notion-fetch` id = "https://www.notion.so/31fcdf456c4180fe869ee69ed80761f4". Collect all child pages (title + URL/ID). If none: "No saved contexts found." Stop.

## Step 2: Resolve argument

| Argument | Action |
|---|---|
| `?` or no argument | count = 5 → Step 3 |
| plain integer N | Load entry #N from prior list → Step 4. If no prior list, show list first. |
| `:last` | Load last child page from Step 1 → Step 4 |
| `:all` | count = total pages → Step 3 |
| `:N` (colon + digits) | count = N → Step 3 |
| name text | Find case-insensitive title match → Step 4. Not found: say so, count = 5 → Step 3 |

## Step 3: Display list

Do NOT call `notion-fetch` on any child page. Take the last `count` entries from Step 1 (pages are in creation order; last = newest). Reverse so #1 = newest.

```
Available contexts:

1. Title A
2. Title B

Reply with a number to load that context.
```

Wait. Number reply → load that entry (Step 4).

## Step 4: Load context

`notion-fetch` the selected page. Present content under its original headings. Output "Context restored. Ready to continue." State the most important open item.
